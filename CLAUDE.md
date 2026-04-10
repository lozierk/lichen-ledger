# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Lichen Ledger** — a full-stack consulting expense tracker for a solo consultant. Parses financial statements (PDF/image) via Claude Vision, lets the user review/edit/categorize transactions, then syncs approved data to Google Sheets via MCP.

PRD: `PRD_Lichen_Ledger_v2.md` (restructured v2 with user stories, P0/P1/P2 prioritization, success metrics)
Original PRD: `Product Requirements Document Consulting.md`

## Running the App

```bash
# Prerequisite: uncomment ANTHROPIC_API_KEY in ~/.zshrc, then `source ~/.zshrc`

# Terminal 1 — Backend (localhost:8000)
cd backend && source .venv/bin/activate && python main.py

# Terminal 2 — Frontend (localhost:5173)
cd frontend && npm run dev
```

Open http://localhost:5173. The Vite dev server proxies `/api` requests to the backend.

## Architecture

**Frontend:** React 19 + Vite + Tailwind CSS 3. Local state only (no Redux/Zustand). Seven components in `frontend/src/components/`.

**Backend:** Python 3.13 FastAPI with async endpoints. Three service modules in `backend/services/`:
- `llm_parser.py` — PDF→PNG conversion (PyMuPDF at 200 DPI), sends to Claude Sonnet for structured transaction extraction
- `mcp_sheets.py` — Google Sheets read/write via `@piotr-agier/google-drive-mcp` stdio. Spawns MCP subprocess at startup via FastAPI lifespan
- `log_service.py` — manages `processed_statements.md` for duplicate detection

**Data flow:** Upload → duplicate check → PDF→image → Claude Vision parse → user review/edit → sync approved rows to Google Sheets → log entry

## Key Design Decisions

- **Year-based column schemas:** 2025 has 7 columns (no Client); 2026+ has 8 columns (adds Client). Branching logic in both `mcp_sheets.py` and `TransactionList.jsx`
- **MCP for Sheets access** rather than direct Google API — avoids separate OAuth setup, leverages the Claude Code harness connection named `google-drive-personal`
- **Base64 preview images** inline (no file hosting) — first PDF page rendered and sent as data URI
- **`processed_statements.md`** is the single source of truth for what's been synced (prevents double-processing)

## Google Sheets

| Year | Sheet ID | Columns |
|------|----------|---------|
| 2025 | `1LPu8pOIuPIf6CaHY4D5gnH9yfSYMl01UgRVuPBx6bjQ` | Date, Vendor, Description, Amount, Category, Source Account, Notes |
| 2026 | `1MW2qq5L2ITGOQSgZR3KbzSBYlY3bOboXl1Ro_mBmSLc` | Date, Vendor, Description, Amount, Category, Client, Source Account, Notes |

Each sheet has monthly tabs (January–December) plus a Summary tab.

## Environment Variables (`.env`)

- `ANTHROPIC_API_KEY` — Claude API key (also needs to be in shell env)
- `GOOGLE_DRIVE_OAUTH_CREDENTIALS` — path to GCP OAuth keys JSON
- `GOOGLE_DRIVE_MCP_TOKEN_PATH` — path to MCP token JSON
- `SHEETS_2025_ID`, `SHEETS_2026_ID` — Google Sheet document IDs

## Frontend Theme

"Lichen Ledger" — forest greens + slate blues, defined in `frontend/tailwind.config.js`. Primary color `#154212`, secondary `#496173`. Font: Inter. Icons: Google Material Symbols Outlined.

## Reference Mockups

HTML mockups from Stitch and their PNG screenshots are in the project root:
- `Consulting_Expense_Tracker_Main_Screen_01.html` / `.png`
- `Consulting_Expense_Tracker_Success_Screen_02.html` / `.png`
