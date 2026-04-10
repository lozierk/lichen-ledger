from pydantic import BaseModel


class Transaction(BaseModel):
    date: str
    vendor: str
    description: str
    amount: str
    category: str
    is_new_category: bool = False
    source_account: str = ""
    client: str = ""
    notes: str = ""
    approved: bool = False


class ParseResult(BaseModel):
    transactions: list[Transaction]
    source_document_type: str
    statement_period: str | None
    new_categories: list[str]
    filename: str
    preview_image: str | None = None  # Base64 PNG of first page


class SyncRequest(BaseModel):
    year: int
    month: str  # "January", "February", etc.
    transactions: list[Transaction]
    filename: str


class SyncResponse(BaseModel):
    transaction_count: int
    filename: str
    total_amount: str
    sheet_total: str
    synced_at: str


class LogEntry(BaseModel):
    date_processed: str
    filename: str
    transaction_count: int
    status: str
