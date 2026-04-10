import os
from contextlib import asynccontextmanager
from datetime import datetime

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

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
