import asyncio
import json
import os
import re

from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

# Default sheet IDs — overridden by .env values at runtime
_DEFAULT_SHEET_IDS = {
    2025: "1LPu8pOIuPIf6CaHY4D5gnH9yfSYMl01UgRVuPBx6bjQ",
    2026: "1MW2qq5L2ITGOQSgZR3KbzSBYlY3bOboXl1Ro_mBmSLc",
}

# Populated at runtime by load_sheet_ids()
SHEET_IDS: dict[int, str] = {}


def _env_path() -> str:
    """Path to the project .env file."""
    return os.path.join(os.path.dirname(__file__), "..", "..", ".env")


def load_sheet_ids():
    """Load sheet IDs from environment variables and .env file.

    Call this AFTER dotenv has loaded the .env file.
    Picks up any SHEETS_YYYY_ID variables (e.g., SHEETS_2025_ID, SHEETS_2027_ID).
    """
    SHEET_IDS.clear()

    # Load defaults first
    for year, sid in _DEFAULT_SHEET_IDS.items():
        SHEET_IDS[year] = sid

    # Override with env vars (supports any year)
    for key, val in os.environ.items():
        if key.startswith("SHEETS_") and key.endswith("_ID") and val:
            try:
                year = int(key.replace("SHEETS_", "").replace("_ID", ""))
                SHEET_IDS[year] = val
            except ValueError:
                continue

    # Ensure defaults are persisted to .env so they survive restarts
    env_file = _env_path()
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            env_content = f.read()
    else:
        env_content = ""

    for year, sid in SHEET_IDS.items():
        var_name = f"SHEETS_{year}_ID"
        if var_name not in env_content:
            with open(env_file, "a") as f:
                f.write(f"{var_name}={sid}\n")
            print(f"[Config] Added {var_name} to .env")

    print(f"[Config] Loaded sheet IDs: { {y: sid[:12] + '...' for y, sid in SHEET_IDS.items()} }")


def save_sheet_id(year: int, sheet_id: str):
    """Persist a sheet ID to the .env file and the runtime dict."""
    SHEET_IDS[year] = sheet_id

    env_file = _env_path()
    var_name = f"SHEETS_{year}_ID"

    # Read existing .env content
    lines = []
    replaced = False
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            for line in f:
                if line.startswith(f"{var_name}="):
                    lines.append(f"{var_name}={sheet_id}\n")
                    replaced = True
                else:
                    lines.append(line)

    # Append if not already present
    if not replaced:
        lines.append(f"{var_name}={sheet_id}\n")

    with open(env_file, "w") as f:
        f.writelines(lines)

    # Also set in the current process environment
    os.environ[var_name] = sheet_id
    print(f"[Config] Saved {var_name}={sheet_id[:12]}... to .env")

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

    async def create_expense_sheet(self, year: int) -> dict:
        """Create a new expense tracking Google Sheet for the given year.

        Returns dict with spreadsheet_id, title, and url.
        """
        title = f"Consulting Expenses {year}"
        columns = self._get_columns(year)

        # Create the spreadsheet with column headers as initial data
        result = await self._call_tool("createGoogleSheet", {
            "name": title,
            "data": [columns],
        })
        print(f"[MCP] createGoogleSheet result: {result}")

        # Extract spreadsheet ID from result text
        # Result typically contains the spreadsheet URL or ID
        sheet_id = self._extract_sheet_id(result)
        if not sheet_id:
            raise ValueError(f"Could not extract spreadsheet ID from creation result: {result}")

        # The default first tab is "Sheet1" — rename it to January
        try:
            await self._call_tool("renameSheet", {
                "spreadsheetId": sheet_id,
                "sheetId": 0,
                "newTitle": "January",
            })
            print("[MCP] Renamed Sheet1 to January")
        except Exception as e:
            print(f"[MCP] Warning: could not rename Sheet1: {e}")

        # Add remaining monthly tabs (February through December) + Summary
        for tab_name in MONTHS[1:] + ["Summary"]:
            try:
                await self._call_tool("addSpreadsheetSheet", {
                    "spreadsheetId": sheet_id,
                    "sheetTitle": tab_name,
                })
                print(f"[MCP] Added tab: {tab_name}")
            except Exception as e:
                print(f"[MCP] Warning: could not add tab {tab_name}: {e}")

        # Write column headers to February-December tabs
        # (January already has headers from creation, Summary doesn't need them)
        for month in MONTHS[1:]:
            try:
                await self._call_tool("appendSpreadsheetRows", {
                    "spreadsheetId": sheet_id,
                    "range": f"{month}!A1:A1",
                    "values": [columns],
                })
            except Exception as e:
                print(f"[MCP] Warning: could not write headers to {month}: {e}")

        # Persist the new sheet ID to .env and runtime dict
        save_sheet_id(year, sheet_id)

        return {
            "spreadsheet_id": sheet_id,
            "title": title,
            "url": f"https://docs.google.com/spreadsheets/d/{sheet_id}",
            "year": year,
        }

    def _extract_sheet_id(self, result_text: str) -> str | None:
        """Extract a Google Spreadsheet ID from MCP tool result text."""
        # Try to find spreadsheet ID in a URL pattern
        url_match = re.search(r"/spreadsheets/d/([a-zA-Z0-9_-]+)", result_text)
        if url_match:
            return url_match.group(1)
        # Try to find a standalone ID-like string (44 chars, alphanumeric + hyphens/underscores)
        id_match = re.search(r"[a-zA-Z0-9_-]{30,}", result_text)
        if id_match:
            return id_match.group(0)
        return None

    def has_sheet(self, year: int) -> bool:
        """Check if a sheet ID is configured for the given year."""
        return bool(SHEET_IDS.get(year))

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
