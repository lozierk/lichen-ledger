import base64
import os
from contextlib import asynccontextmanager
from datetime import datetime

import asyncio
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from models import LogEntry, ParseResult, SyncRequest, SyncResponse, Transaction
from services.mcp_sheets import SheetsService
from services.log_service import LogService

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

sheets = SheetsService()
log_service = LogService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await sheets.connect()
    yield
    await sheets.disconnect()


app = FastAPI(title="Lichen Ledger API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/demo")
async def demo_data():
    """Return sample parsed transactions for demo/review without API keys or Sheets."""
    sample_transactions = [
        Transaction(date="03/02/2025", vendor="Amazon Web Services", description="AWS SERVICES 03/02", amount="$247.93", category="Software & Cloud", is_new_category=False, source_account="Chase Ink Business", notes="Monthly hosting"),
        Transaction(date="03/04/2025", vendor="Zoom", description="ZOOM.US 888-799-9666", amount="$14.99", category="Software & Cloud", is_new_category=False, source_account="Chase Ink Business", notes=""),
        Transaction(date="03/05/2025", vendor="United Airlines", description="UNITED 016-2198374625", amount="$387.40", category="Travel", is_new_category=False, source_account="Chase Ink Business", notes="Client site visit - Denver"),
        Transaction(date="03/05/2025", vendor="Marriott Denver", description="MARRIOTT DENVER TECH CTR", amount="$189.00", category="Travel", is_new_category=False, source_account="Chase Ink Business", notes="1 night - client meeting"),
        Transaction(date="03/07/2025", vendor="Staples", description="STAPLES #1284", amount="$63.47", category="Office Supplies", is_new_category=False, source_account="Chase Ink Business", notes="Printer paper, toner"),
        Transaction(date="03/10/2025", vendor="LinkedIn", description="LINKEDIN PREMIUM", amount="$59.99", category="Marketing", is_new_category=False, source_account="Chase Ink Business", notes=""),
        Transaction(date="03/12/2025", vendor="WeWork", description="WEWORK MEMBERSHIP MAR", amount="$350.00", category="Office Rent", is_new_category=True, source_account="Chase Ink Business", notes="Hot desk membership"),
        Transaction(date="03/14/2025", vendor="Uber", description="UBER TRIP DEN-DIA", amount="$42.15", category="Travel", is_new_category=False, source_account="Chase Ink Business", notes="Airport return"),
        Transaction(date="03/18/2025", vendor="Anthropic", description="ANTHROPIC API USAGE", amount="$86.20", category="Software & Cloud", is_new_category=False, source_account="Chase Ink Business", notes="Claude API"),
        Transaction(date="03/19/2025", vendor="FedEx", description="FEDEX OFFICE #4821", amount="$28.50", category="Office Supplies", is_new_category=False, source_account="Chase Ink Business", notes="Client proposal printing"),
        Transaction(date="03/22/2025", vendor="Loom", description="LOOM.COM SUBSCRIPTION", amount="$12.50", category="Software & Cloud", is_new_category=False, source_account="Chase Ink Business", notes=""),
        Transaction(date="03/25/2025", vendor="Client Dinner - Acme Corp", description="THE CAPITAL GRILLE", amount="$215.80", category="Meals & Entertainment", is_new_category=True, source_account="Chase Ink Business", notes="Q1 review dinner with CEO"),
        Transaction(date="03/27/2025", vendor="Adobe", description="ADOBE CREATIVE CLOUD", amount="$54.99", category="Software & Cloud", is_new_category=False, source_account="Chase Ink Business", notes=""),
        Transaction(date="03/29/2025", vendor="Verizon Business", description="VERIZON WRLS 03/29", amount="$85.00", category="Telecommunications", is_new_category=True, source_account="Chase Ink Business", notes="Business phone line"),
        Transaction(date="03/31/2025", vendor="QuickBooks", description="INTUIT QUICKBOOKS", amount="$30.00", category="Software & Cloud", is_new_category=False, source_account="Chase Ink Business", notes=""),
    ]
    return ParseResult(
        transactions=sample_transactions,
        source_document_type="credit_card_statement",
        statement_period="March 2025",
        new_categories=["Office Rent", "Meals & Entertainment", "Telecommunications"],
        filename="demo_chase_ink_march_2025.pdf",
        preview_image=None,
    )


@app.get("/api/categories")
async def get_categories(year: int = 2025):
    categories = await sheets.get_categories(year)
    return {"categories": categories}


@app.get("/api/accounts")
async def get_accounts(year: int = 2025):
    accounts = await sheets.get_source_accounts(year)
    return {"accounts": accounts}


@app.get("/api/summary/{year}/{month}")
async def get_summary(year: int, month: str):
    summary = await sheets.get_summary(year, month)
    return summary


@app.post("/api/upload")
async def upload_document(
    file: UploadFile = File(...),
    year: int = Form(2025),
    month: str = Form("January"),
):
    # Check for duplicates
    if log_service.is_duplicate(file.filename):
        raise HTTPException(
            status_code=409,
            detail=f"'{file.filename}' has already been processed. Upload with a different name to reprocess.",
        )

    file_bytes = await file.read()
    file_ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""

    if file_ext == "pdf":
        file_type = "pdf"
    elif file_ext in ("jpg", "jpeg", "png"):
        file_type = "image"
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF, JPG, or PNG.")

    # Get existing categories for the prompt
    categories = await sheets.get_categories(year)
    accounts = await sheets.get_source_accounts(year)

    # Parse with LLM (Phase 4)
    from services.llm_parser import LLMParser
    parser = LLMParser(os.getenv("ANTHROPIC_API_KEY", ""))
    result = await parser.parse_document(
        file_bytes=file_bytes,
        file_type=file_type,
        existing_categories=categories,
        existing_accounts=accounts,
        year=year,
    )
    result.filename = file.filename

    return result


@app.post("/api/upload-stream")
async def upload_document_stream(
    file: UploadFile = File(...),
    year: int = Form(2025),
    month: str = Form("January"),
):
    """Upload with SSE progress updates."""
    # Check for duplicates
    if log_service.is_duplicate(file.filename):
        raise HTTPException(
            status_code=409,
            detail=f"'{file.filename}' has already been processed.",
        )

    file_bytes = await file.read()
    file_ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""

    if file_ext == "pdf":
        file_type = "pdf"
    elif file_ext in ("jpg", "jpeg", "png"):
        file_type = "image"
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    filename = file.filename

    async def event_stream():
        import json as _json

        def send_event(data):
            return f"data: {_json.dumps(data)}\n\n"

        yield send_event({"stage": "start", "message": "Preparing document..."})

        # Convert PDF to images
        from services.llm_parser import LLMParser
        parser = LLMParser(os.getenv("ANTHROPIC_API_KEY", ""))

        if file_type == "pdf":
            yield send_event({"stage": "converting", "message": "Converting PDF pages to images..."})
            images = parser._pdf_to_images(file_bytes)
            page_count = len(images)
            yield send_event({"stage": "converted", "message": f"Converted {page_count} page{'s' if page_count != 1 else ''}", "pages": page_count})
            preview_image = images[0] if images else None
        else:
            images = [base64.b64encode(file_bytes).decode("utf-8")]
            preview_image = images[0]
            page_count = 1
            yield send_event({"stage": "converted", "message": "Image loaded", "pages": 1})

        # Get categories
        yield send_event({"stage": "context", "message": "Fetching existing categories from Google Sheets..."})
        try:
            categories = await sheets.get_categories(year)
            accounts = await sheets.get_source_accounts(year)
            yield send_event({"stage": "context_done", "message": f"Found {len(categories)} categories"})
        except Exception:
            categories = []
            accounts = []
            yield send_event({"stage": "context_done", "message": "Using default categories (Sheets unavailable)"})

        # Call Claude
        yield send_event({"stage": "parsing", "message": f"Sending {page_count} page{'s' if page_count != 1 else ''} to Claude for analysis..."})

        result = await parser.parse_document(
            file_bytes=file_bytes,
            file_type=file_type,
            existing_categories=categories,
            existing_accounts=accounts,
            year=year,
        )
        result.filename = filename

        tx_count = len(result.transactions)
        new_cat_count = len(result.new_categories)
        yield send_event({
            "stage": "complete",
            "message": f"Found {tx_count} transaction{'s' if tx_count != 1 else ''}" +
                       (f" ({new_cat_count} new categor{'ies' if new_cat_count != 1 else 'y'})" if new_cat_count else ""),
            "result": result.model_dump(),
        })

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/api/sync", response_model=SyncResponse)
async def sync_transactions(req: SyncRequest):
    # Check for duplicates
    if log_service.is_duplicate(req.filename):
        raise HTTPException(status_code=409, detail=f"'{req.filename}' has already been processed.")

    # Build rows matching the sheet schema
    rows = []
    total_amount = 0.0
    for tx in req.transactions:
        if not tx.approved:
            continue
        # Parse amount for summing
        amt_str = tx.amount.replace("$", "").replace(",", "")
        try:
            total_amount += float(amt_str)
        except ValueError:
            pass

        if req.year >= 2026:
            rows.append([tx.date, tx.vendor, tx.description, tx.amount, tx.category, tx.client, tx.source_account, tx.notes])
        else:
            rows.append([tx.date, tx.vendor, tx.description, tx.amount, tx.category, tx.source_account, tx.notes])

    if not rows:
        raise HTTPException(status_code=400, detail="No approved transactions to sync.")

    # Append to Google Sheets
    count = await sheets.append_transactions(req.year, req.month, rows)

    # Get updated summary
    summary = await sheets.get_summary(req.year, req.month)

    # Log the sync
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    log_service.append_entry(LogEntry(
        date_processed=now,
        filename=req.filename,
        transaction_count=count,
        status="Synced",
    ))

    return SyncResponse(
        transaction_count=count,
        filename=req.filename,
        total_amount=f"${total_amount:,.2f}",
        sheet_total=f"{summary['count']} Total" if summary["count"] != "N/A" else "Updated",
        synced_at=now,
    )


@app.get("/api/log")
async def get_log():
    entries = log_service.read_log()
    return {"entries": entries}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
