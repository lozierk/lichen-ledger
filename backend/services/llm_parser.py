import base64
import json
import os

import anthropic
import fitz  # PyMuPDF

from models import ParseResult, Transaction


class LLMParser:
    """Parses financial documents using Claude's vision API."""

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    async def parse_document(
        self,
        file_bytes: bytes,
        file_type: str,
        existing_categories: list[str],
        existing_accounts: list[str],
        year: int,
    ) -> ParseResult:
        """Parse a financial document and return structured transactions."""

        if file_type == "pdf":
            images = self._pdf_to_images(file_bytes)
            preview_image = images[0] if images else None
        else:
            images = [base64.b64encode(file_bytes).decode("utf-8")]
            preview_image = images[0]

        prompt = self._build_prompt(existing_categories, existing_accounts, year)
        media_type = "image/png" if file_type == "pdf" else self._guess_media_type(file_bytes)

        # Build message content with all page images
        content = []
        for img_b64 in images:
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": img_b64,
                },
            })
        content.append({"type": "text", "text": prompt})

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": content}],
        )

        # Extract JSON from response
        raw_text = response.content[0].text
        parsed = self._extract_json(raw_text)

        transactions = []
        for tx_data in parsed.get("transactions", []):
            transactions.append(Transaction(
                date=tx_data.get("date", ""),
                vendor=tx_data.get("vendor", ""),
                description=tx_data.get("description", ""),
                amount=tx_data.get("amount", ""),
                category=tx_data.get("category", ""),
                is_new_category=tx_data.get("is_new_category", False),
                source_account=tx_data.get("source_account", ""),
                client=tx_data.get("client", ""),
                notes=tx_data.get("notes", ""),
                approved=False,
            ))

        return ParseResult(
            transactions=transactions,
            source_document_type=parsed.get("source_document_type", "unknown"),
            statement_period=parsed.get("statement_period"),
            new_categories=parsed.get("new_categories", []),
            filename="",  # Set by caller
            preview_image=preview_image,
        )

    def _pdf_to_images(self, pdf_bytes: bytes) -> list[str]:
        """Convert PDF pages to base64-encoded PNG images."""
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        images = []
        for page in doc:
            pixmap = page.get_pixmap(dpi=200)
            png_bytes = pixmap.tobytes("png")
            images.append(base64.b64encode(png_bytes).decode("utf-8"))
        doc.close()
        return images

    def _build_prompt(
        self, categories: list[str], accounts: list[str], year: int
    ) -> str:
        cats_str = ", ".join(categories) if categories else "No existing categories yet"
        accts_str = ", ".join(accounts) if accounts else "Unknown"

        client_field = ""
        if year >= 2026:
            client_field = '- "client": The client this expense relates to, if identifiable. Otherwise empty string.\n'

        return f"""You are a financial document parser for a consulting business. Extract every transaction from this bank/credit card statement or receipt image.

For each transaction, return a JSON object with these fields:
- "date": The transaction date in MM/DD/{year} format
- "vendor": A clean, human-readable vendor name (not the raw bank description)
- "description": The original raw description from the statement
- "amount": The dollar amount as a string with $ prefix (e.g., "$142.30"). Use positive numbers.
- "category": Suggest from this list of existing categories: [{cats_str}]
  If no existing category fits well, suggest a new descriptive category and set is_new_category to true.
- "is_new_category": boolean, true only if the category is not in the existing list above
- "source_account": If identifiable from the document, suggest from: [{accts_str}]. Otherwise empty string.
{client_field}- "notes": Any relevant notes (empty string if none)

Return a JSON object with this exact structure (no markdown fences, just raw JSON):
{{
  "transactions": [... array of transaction objects ...],
  "source_document_type": "bank_statement" or "credit_card_statement" or "receipt",
  "statement_period": "Month YYYY" if identifiable from the document, otherwise null,
  "new_categories": ["list of any category strings not in the existing list"]
}}

Important:
- Extract ALL transactions visible in the document
- Dates must be in MM/DD/{year} format
- Amounts should be positive dollar values with $ prefix
- Return ONLY valid JSON, no explanation or markdown"""

    def _guess_media_type(self, file_bytes: bytes) -> str:
        if file_bytes[:3] == b"\xff\xd8\xff":
            return "image/jpeg"
        if file_bytes[:8] == b"\x89PNG\r\n\x1a\n":
            return "image/png"
        return "image/jpeg"

    def _extract_json(self, text: str) -> dict:
        """Extract JSON from LLM response, handling markdown fences."""
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            lines = lines[1:]  # Remove opening fence
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines)

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON object in the text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                try:
                    return json.loads(text[start:end])
                except json.JSONDecodeError:
                    pass
            return {"transactions": [], "source_document_type": "unknown", "statement_period": None, "new_categories": []}
