# Product Requirements Document: Lichen Ledger

## Consulting Expense Tracker — Tax-Deductible Expense Extraction & Sync

---

## 1. Product Description

Lichen Ledger is a high-utility expense tracker for a solo consultant who needs to extract tax-deductible business expenses from monthly credit card and bank statement PDFs. Every month, the consultant downloads statements, manually scans them for business expenses, and types them into a Google Sheet — tedious, error-prone, and easy to procrastinate. Lichen Ledger automates the painful part: upload a PDF, let Claude Vision parse every transaction into structured data, review and categorize in a clean UI, then sync approved rows directly to the consultant's existing Google Sheets workbook. The goal is zero manual data entry beyond category confirmation.

---

## 2. Problem Statement

A solo consultant tracks tax-deductible business expenses across multiple credit cards and bank accounts. Each month, they download PDF statements, visually scan pages of transactions to find the business-related ones, then manually key them into a Google Sheet organized by month and year. This process takes 30-60 minutes per statement, is error-prone (missed transactions, typos, wrong categories), and creates enough friction that it gets postponed — leading to a painful tax-season scramble.

The cost of not solving this: missed deductions at tax time (real money lost), stress during tax season, and hours of low-value manual work each month that could be spent on billable consulting.

---

## 3. Target Users

**Primary user:** Solo consultant (the builder — this is a personal tool)

- Operates as a 1099 independent contractor
- Has 2-4 credit cards and bank accounts with mixed personal/business transactions
- Already tracks expenses in Google Sheets with monthly tabs (January-December) per tax year
- Comfortable with basic web apps but not a developer
- Needs to extract, categorize, and reconcile expenses monthly for quarterly estimated taxes and annual filing

**This is NOT for:** Teams, accountants managing multiple clients, or users who want a full bookkeeping system. It solves one problem for one person.

---

## 4. Core Features

### Must-Have (P0) — The feature cannot ship without these

| Feature | Description | Why P0 |
|---------|-------------|--------|
| PDF Statement Upload | Drag-and-drop upload of credit card/bank statement PDFs | Core input — everything starts here |
| Claude Vision Parsing | LLM extracts date, vendor, description, amount, and suggested category from each transaction | This IS the product — replaces manual scanning |
| Transaction Review & Editing | Table view of parsed transactions with inline editing for vendor, amount, category, notes | Human-in-the-loop — user must verify before sync |
| Transaction Approval | Per-row approve/reject with bulk "Approve All" option | Controls what gets synced — prevents bad data |
| Google Sheets Sync | Writes approved transactions to the correct monthly tab in the user's Google Sheet | The destination — where tax data lives |
| Duplicate Detection | Checks if a statement file has already been processed before parsing | Prevents double-counting expenses |
| Statement Preview | Shows first page of uploaded PDF as image alongside parsed transactions | Visual confirmation that the right file was parsed |

### Nice-to-Have (P1) — Improves experience but core works without them

| Feature | Description | Why P1 |
|---------|-------------|--------|
| Intelligent Category Suggestions | LLM uses existing categories from Google Sheet to suggest matches for new transactions | Reduces manual categorization work |
| New Category Detection | Alerts user when a new vendor/expense type doesn't match existing categories | Keeps category taxonomy clean |
| Category Mapping | UI to map a new category to an existing one or confirm the new category | Prevents category sprawl |
| Receipt Image Upload | Support for JPG/PNG receipt images (not just PDFs) | Handles one-off purchases without statements |
| Processed Statements Log | UI table showing all previously synced statements with date, filename, transaction count | Audit trail — "did I already do March?" |

### Future Considerations (P2) — Out of scope for v1 but design should not block them

| Feature | Description | Why Deferred |
|---------|-------------|-------------|
| Year/Month Navigation Sidebar | Browse by tax year and month, see completion status | Useful but not needed for core upload-parse-sync loop |
| Summary Dashboard | Total expenses, auto-categorized count, monthly/yearly totals | Reporting belongs in Google Sheets for now |
| Multi-page PDF Optimization | Smarter page-by-page parsing for 20+ page statements | Current approach works; optimize when needed |
| Dark Mode | Alternative color theme | Cosmetic, not functional |

---

## 5. Non-Goals (What This Product Is NOT)

| Non-Goal | Why Out of Scope |
|----------|-----------------|
| Full bookkeeping system | Lichen Ledger handles extraction and categorization only — the Google Sheet IS the ledger |
| Personal expense tracking | Only business/tax-deductible expenses matter; personal transactions are ignored during review |
| Receipt OCR for handwritten receipts | Claude Vision handles printed/digital receipts; handwritten is a different problem |
| Tax calculation or filing | This feeds data into a Sheet; the accountant or tax software handles the rest |
| Bank account aggregation (Plaid, etc.) | User downloads PDFs manually; auto-fetching adds auth complexity and security risk for v1 |
| Multi-user or shared access | Single user, single Google account — this is a personal tool |
| Mobile app | Desktop-only web app; statements are downloaded on a computer anyway |

---

## 6. User Stories

### Core Workflow

- **As a solo consultant**, I want to upload a credit card statement PDF so that I don't have to manually scan pages for business expenses
- **As a solo consultant**, I want Claude to extract and categorize every transaction from my statement so that I can review them in seconds instead of minutes
- **As a solo consultant**, I want to see my uploaded statement alongside the parsed transactions so that I can visually confirm the extraction is correct
- **As a solo consultant**, I want to edit any transaction's vendor, amount, category, or notes before syncing so that I can fix parsing errors
- **As a solo consultant**, I want to approve transactions individually or in bulk so that I control exactly what gets written to my Google Sheet
- **As a solo consultant**, I want approved transactions synced to the correct monthly tab in my Google Sheet so that my expense tracking stays organized without copy-pasting
- **As a solo consultant**, I want to be warned if I try to upload a statement I've already processed so that I don't accidentally double-count expenses

### Category Management

- **As a solo consultant**, I want Claude to suggest categories based on what's already in my Google Sheet so that my categorization stays consistent
- **As a solo consultant**, I want to be alerted when a new category is detected so that I can decide whether to keep it or map it to an existing one

### Edge Cases

- **As a solo consultant**, I want to see a clear error message if the PDF can't be parsed so that I know to try a different format or re-download
- **As a solo consultant**, I want to upload a single receipt image (not just a full statement) so that I can capture one-off purchases

---

## 7. Agent Workflow (Step-by-Step)

1. **Upload** — User drags a PDF statement into the upload zone
2. **Duplicate Check** — System checks `processed_statements.md` log; rejects if already synced
3. **PDF-to-Image Conversion** — PyMuPDF renders each page at 200 DPI as PNG
4. **Context Pull** — System fetches existing categories and source accounts from Google Sheet
5. **Claude Vision Parse** — All page images + existing categories sent to Claude Sonnet; returns structured JSON with date, vendor, description, amount, category, source account, notes
6. **User Review** — Parsed transactions displayed in editable table alongside statement preview image
7. **Category Resolution** — If new categories detected, user maps them to existing or confirms new ones
8. **Approval** — User approves/rejects individual transactions or approves all
9. **Sync to Sheets** — Approved transactions appended to correct monthly tab via MCP
10. **Log Entry** — Filename, date, transaction count, and status written to `processed_statements.md`
11. **Success Confirmation** — Summary screen shows what was synced, total amount, and link to Google Sheet

---

## 8. Success Metrics

### Leading Indicators (measurable within days)

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Parse accuracy | 90%+ of transactions correctly extracted on first pass | Count edits made before approval vs. total transactions |
| Category match rate | 70%+ of transactions auto-matched to existing categories | Count transactions where suggested category was kept vs. changed |
| Time to process one statement | Under 5 minutes (upload to sync) | Timestamp between upload and sync API calls |
| Approval rate without edits | 60%+ of transactions approved without modification | Count approved-as-is vs. edited-then-approved |

### Lagging Indicators (measurable over weeks/months)

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Monthly completion rate | All statements processed within 7 days of availability | Check processed_statements.md log dates vs. statement dates |
| Missed deductions | Zero missed deductions reported at tax time | Compare Sheet totals against manual spot-check of 2-3 statements |
| Time saved per month | 2+ hours saved vs. manual process | User estimate (no formal tracking needed for personal tool) |

---

## 9. Tech Stack (v1)

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | React 19 + Vite + Tailwind CSS 3 | Fast setup, utility styling, hot reload |
| Backend | Python 3.13 + FastAPI | Async endpoints, good PDF library support |
| PDF Processing | PyMuPDF (fitz) | Converts PDF pages to images at 200 DPI for Claude Vision |
| AI Parsing | Claude Sonnet via Anthropic SDK | Vision capability for reading statement images; structured extraction |
| Google Sheets | MCP (`@piotr-agier/google-drive-mcp`) | Avoids separate Google OAuth setup; leverages existing MCP connection |
| Logging | Local markdown file (`processed_statements.md`) | Simple, no database needed for single-user tool |
| Theme | "Lichen Ledger" — forest greens + slate blues, Inter font | Distinct visual identity; calming palette for financial work |

---

## 10. Open Questions

| Question | Who Answers | Blocking? |
|----------|------------|-----------|
| Should the app auto-detect which month a statement covers from the parsed data, or rely on user selection? | Product (me) | No — user selection works for v1 |
| How to handle statements that span two months (e.g., billing cycle March 15 - April 14)? | Product (me) | No — edge case, handle manually for now |
| Should new categories be auto-added to a master list in the Google Sheet? | Product (me) | No — v1 just syncs transactions; category management is manual |
| What happens when MCP connection to Google Sheets fails mid-sync? | Engineering | Yes — need retry or clear error state |
| Should the app support re-processing a statement (overwrite previous sync)? | Product (me) | No — v1 rejects duplicates; user can rename file if needed |

---

## 11. Prototype Scope

**Core feature for prototype:** PDF Upload + Claude Vision Parse + Transaction Review + Google Sheets Sync (Steps 1-10 of the agent workflow)

This is the complete core loop. A user should be able to:
1. Upload a real credit card statement PDF
2. See it parsed into structured transactions
3. Review and edit any row
4. Approve and sync to their Google Sheet
5. See confirmation that data landed correctly

**Mocked or deferred for prototype:**
- Year/month sidebar navigation (hardcode to current month)
- Summary dashboard cards
- Receipt image upload (PDFs only for v1)

---

## 12. Reference Files

| File | Purpose |
|------|---------|
| `Product Requirements Document Consulting.md` | Original PRD (v1) |
| `PRD_Lichen_Ledger_v2.md` | This document — restructured PRD (v2) |
| `Consulting_Expense_Tracker_Main_Screen_01.html` | Stitch HTML mockup — main screen |
| `Consulting_Expense_Tracker_Main_Screen_01.png` | Screenshot of main screen mockup |
| `Consulting_Expense_Tracker_Success_Screen_02.html` | Stitch HTML mockup — success screen |
| `Consulting_Expense_Tracker_Success_Screen_02.png` | Screenshot of success screen mockup |
| `RESUME_FROM_20260401.md` | Session notes from initial build on April 1 |
