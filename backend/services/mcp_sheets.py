import asyncio
import json
import os

from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

SHEET_IDS = {
    2025: os.getenv("SHEETS_2025_ID", "1LPu8pOIuPIf6CaHY4D5gnH9yfSYMl01UgRVuPBx6bjQ"),
    2026: os.getenv("SHEETS_2026_ID", "1MW2qq5L2ITGOQSgZR3KbzSBYlY3bOboXl1Ro_mBmSLc"),
}

# 2025: Date, Vendor, Description, Amount, Category, Source Account, Notes (7 cols)
# 2026: Date, Vendor, Description, Amount, Category, Client, Source Account, Notes (8 cols)
COLUMNS_2025 = ["Date", "Vendor", "Description", "Amount", "Category", "Source Account", "Notes"]
COLUMNS_2026 = ["Date", "Vendor", "Description", "Amount", "Category", "Client", "Source Account", "Notes"]

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


class SheetsService:
    """Manages MCP connection to Google Drive MCP server for Sheets operations."""

    def __init__(self):
        self._session: ClientSession | None = None
        self._cm_stdio = None
        self._cm_session = None

    async def connect(self):
        """Spawn the MCP server and initialize the client session."""
        server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@piotr-agier/google-drive-mcp"],
            env={
                "GOOGLE_DRIVE_OAUTH_CREDENTIALS": os.getenv("GOOGLE_DRIVE_OAUTH_CREDENTIALS"),
                "GOOGLE_DRIVE_MCP_TOKEN_PATH": os.getenv("GOOGLE_DRIVE_MCP_TOKEN_PATH"),
                "PATH": os.environ.get("PATH", ""),
                "HOME": os.environ.get("HOME", ""),
                "NODE_PATH": os.environ.get("NODE_PATH", ""),
            },
        )
        self._cm_stdio = stdio_client(server_params)
        read_stream, write_stream = await self._cm_stdio.__aenter__()
        self._cm_session = ClientSession(read_stream, write_stream)
        self._session = await self._cm_session.__aenter__()
        await self._session.initialize()
        print("[MCP] Connected to Google Drive MCP server")

    async def disconnect(self):
        """Clean shutdown of MCP session."""
        if self._cm_session:
            await self._cm_session.__aexit__(None, None, None)
        if self._cm_stdio:
            await self._cm_stdio.__aexit__(None, None, None)
        print("[MCP] Disconnected from Google Drive MCP server")

    async def _call_tool(self, tool_name: str, arguments: dict) -> str:
        """Call an MCP tool and return the text result."""
        result = await self._session.call_tool(tool_name, arguments)
        # MCP returns a list of content blocks; extract text
        texts = []
        for block in result.content:
            if hasattr(block, "text"):
                texts.append(block.text)
        return "\n".join(texts)

    def _get_sheet_id(self, year: int) -> str:
        sheet_id = SHEET_IDS.get(year)
        if not sheet_id:
            raise ValueError(f"No spreadsheet configured for year {year}")
        return sheet_id

    def _get_columns(self, year: int) -> list[str]:
        return COLUMNS_2026 if year >= 2026 else COLUMNS_2025

    async def get_categories(self, year: int) -> list[str]:
        """Scan Category column across all months, return unique sorted list."""
        sheet_id = self._get_sheet_id(year)
        categories = set()

        # Category is column E for both 2025 and 2026
        for month in MONTHS:
            try:
                raw = await self._call_tool("getGoogleSheetContent", {
                    "spreadsheetId": sheet_id,
                    "range": f"{month}!E2:E500",
                })
                for line in raw.strip().split("\n"):
                    line = line.strip()
                    # Skip header-like lines and empty lines
                    if line and not line.startswith("Content for") and not line.startswith("Row 1:"):
                        # Parse "Row N: value" format
                        if ": " in line:
                            val = line.split(": ", 1)[1].strip()
                            if val and val.upper() != "CATEGORY" and val.upper() != "MONTHLY TOTAL":
                                categories.add(val)
                        elif line.upper() != "CATEGORY":
                            categories.add(line)
            except Exception:
                # Month tab might be empty or not exist
                continue

        return sorted(categories)

    async def get_source_accounts(self, year: int) -> list[str]:
        """Scan Source Account column, return unique sorted list."""
        sheet_id = self._get_sheet_id(year)
        accounts = set()

        # Source Account: col F for 2025, col G for 2026
        col = "G" if year >= 2026 else "F"
        for month in MONTHS:
            try:
                raw = await self._call_tool("getGoogleSheetContent", {
                    "spreadsheetId": sheet_id,
                    "range": f"{month}!{col}2:{col}500",
                })
                for line in raw.strip().split("\n"):
                    line = line.strip()
                    if line and not line.startswith("Content for") and not line.startswith("Row 1:"):
                        if ": " in line:
                            val = line.split(": ", 1)[1].strip()
                            if val and val.upper() not in ("SOURCE ACCOUNT", "MONTHLY TOTAL", ""):
                                accounts.add(val)
            except Exception:
                continue

        return sorted(accounts)

    async def get_month_data(self, year: int, month: str) -> list[dict]:
        """Read all transactions from a specific month tab."""
        sheet_id = self._get_sheet_id(year)
        cols = self._get_columns(year)
        last_col = chr(ord("A") + len(cols) - 1)

        raw = await self._call_tool("getGoogleSheetContent", {
            "spreadsheetId": sheet_id,
            "range": f"{month}!A2:{last_col}500",
        })

        transactions = []
        for line in raw.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith("Content for"):
                continue
            if ": " in line:
                row_data = line.split(": ", 1)[1]
                values = [v.strip() for v in row_data.split(", ")]
                if len(values) >= 4 and values[0] and "/" in values[0]:
                    row_dict = {}
                    for j, col_name in enumerate(cols):
                        row_dict[col_name.lower().replace(" ", "_")] = values[j] if j < len(values) else ""
                    transactions.append(row_dict)

        return transactions

    async def append_transactions(self, year: int, month: str, rows: list[list]) -> int:
        """Append rows to the specified month tab. Returns count appended."""
        sheet_id = self._get_sheet_id(year)

        result = await self._call_tool("appendSpreadsheetRows", {
            "spreadsheetId": sheet_id,
            "range": f"{month}!A:A",
            "values": rows,
        })
        print(f"[MCP] Appended {len(rows)} rows to {month}: {result}")
        return len(rows)

    async def get_summary(self, year: int, month: str) -> dict:
        """Get transaction count and total for a specific month."""
        sheet_id = self._get_sheet_id(year)

        try:
            raw = await self._call_tool("getGoogleSheetContent", {
                "spreadsheetId": sheet_id,
                "range": "Summary!A1:C20",
            })
            # Parse summary to find the month's row
            for line in raw.strip().split("\n"):
                if month in line:
                    parts = line.split(", ")
                    total = parts[1] if len(parts) > 1 else "N/A"
                    count = parts[2] if len(parts) > 2 else "N/A"
                    return {"total": total, "count": count}
        except Exception:
            pass

        return {"total": "N/A", "count": "N/A"}
