# Resume From: April 1, 2026

## Starter Prompt
> I'm continuing work on Project_01 (Lichen Ledger) from the Hamza Cohort 01 Claude Code Course. Last session we built the full app. Read the PRD at `Product Requirements Document Consulting.md` and the run instructions at `Run_Project_01.txt` to get oriented.

## What Was Accomplished
- Built complete Lichen Ledger expense tracker from scratch in one session
- **Frontend:** React 19 + Vite + Tailwind CSS with all 7 components matching the Stitch HTML mockups (Sidebar, Header, UploadZone, TransactionList, CategoryAlert, ProcessedLog, SuccessBanner)
- **Backend:** Python 3.13 FastAPI with 5 API endpoints (upload, categories, sync, log, summary)
- **MCP Integration:** Python `mcp` SDK connecting to `@piotr-agier/google-drive-mcp` via stdio — tested live against 2025 Google Sheet, successfully pulled 14 categories
- **Claude Vision Parser:** PDF-to-image pipeline via PyMuPDF, then Claude Sonnet for structured transaction extraction
- **Sync & Logging:** Writes approved transactions to correct monthly Google Sheet tab, logs to `processed_statements.md`, duplicate detection
- **Inline Editing:** Users can edit vendor, amount, category, notes (and Client for 2026) before syncing
- **Statement Preview:** First PDF page rendered as base64 PNG in the left panel

## What's Next
- **End-to-end test:** Upload a real PDF statement, verify parsed transactions look correct, sync to Google Sheets, confirm data landed in the right tab
- **Visual QA:** Compare running app side-by-side with the PNG screenshots to catch any styling gaps
- **Edge cases:** Test receipt images (JPG/PNG), test 2026 year with Client column, test duplicate file rejection
- **Potential improvements:** Category autocomplete in the new-category mapping input, better error messages for MCP connection failures, dark mode support

## Key File Paths
- PRD: `Product Requirements Document Consulting.md`
- Run instructions: `Run_Project_01.txt`
- Backend entry: `backend/main.py`
- MCP Sheets service: `backend/services/mcp_sheets.py`
- LLM parser: `backend/services/llm_parser.py`
- Log service: `backend/services/log_service.py`
- Pydantic models: `backend/models.py`
- Frontend entry: `frontend/src/App.jsx`
- API layer: `frontend/src/api.js`
- Tailwind theme: `frontend/tailwind.config.js`
- Environment config: `.env`
