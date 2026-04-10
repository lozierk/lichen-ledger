import os
import re

from models import LogEntry

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
LOG_PATH = os.path.join(PROJECT_ROOT, "processed_statements.md")

HEADER = """# Processed Statements Log

| Date Processed | Filename | Transactions | Status |
|---|---|---|---|
"""


class LogService:
    """Manages the processed_statements.md log file."""

    def _ensure_file(self):
        if not os.path.exists(LOG_PATH):
            with open(LOG_PATH, "w") as f:
                f.write(HEADER)

    def read_log(self) -> list[LogEntry]:
        self._ensure_file()
        entries = []
        with open(LOG_PATH) as f:
            for line in f:
                line = line.strip()
                if line.startswith("|") and not line.startswith("| Date") and not line.startswith("|---"):
                    parts = [p.strip() for p in line.split("|") if p.strip()]
                    if len(parts) >= 4:
                        entries.append(LogEntry(
                            date_processed=parts[0],
                            filename=parts[1],
                            transaction_count=int(parts[2]) if parts[2].isdigit() else 0,
                            status=parts[3],
                        ))
        return entries

    def append_entry(self, entry: LogEntry):
        self._ensure_file()
        with open(LOG_PATH, "a") as f:
            f.write(f"| {entry.date_processed} | {entry.filename} | {entry.transaction_count} | {entry.status} |\n")

    def is_duplicate(self, filename: str) -> bool:
        entries = self.read_log()
        return any(e.filename == filename and e.status == "Synced" for e in entries)
