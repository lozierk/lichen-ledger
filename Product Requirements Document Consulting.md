# Product Requirements Document: Consulting Expense Tracker (Lichen Ledger)

## 1. Overview
A high-utility, low-friction web application designed for a solo consultant to track tax-deductible business expenses. The application automates the parsing of monthly financial statements (PDFs) and individual receipts (Images), categorizes the expenses, and synchronizes the data with a master Google Sheets spreadsheet.

## 2. Core User Workflow
1.  **Select Tax Year/Month:** User navigates to the relevant period using the sidebar.
2.  **Upload:** User drags and drops a monthly statement (PDF) or a single receipt (Image) into the central upload zone.
3.  **Parsing:** An LLM-powered backend parses the file to extract transaction date, vendor, description, amount, and suggested category.
4.  **Review & Categorize:** User reviews parsed data. If a new category is detected, the user confirms or maps it to an existing one.
5.  **Sync:** Validated data is appended to the corresponding month's tab in the Google Sheets workbook.
6.  **Logging:** Every successful sync is recorded in a local `processed_statements.md` file and a "Processed Statements Log" in the UI to ensure no duplicates or missed months.

## 3. Functional Requirements
### 3.1 Data Acquisition & Parsing
- Support for PDF (bank/credit card statements) and Image (JPG/PNG receipts) formats.
- Integration with an LLM (e.g., Gemini or Claude) to extract structured data from unstructured financial documents.
- Intelligent category suggestion based on the user's existing Google Sheet categories.
- Intelligent new category suggestions when new vendor expenses encountered, to include insertint new categories in the Google Sheet Document.

### 3.2 Google Sheets Integration
- OAuth2 authentication for secure access to the user's Google Drive/Sheets.
- Ability to identify and append data to specific tabs (e.g., "January", "February").
- Real-time calculation of totals within the sheet to reflect in the UI summary cards.
- Connection to Google Sheets is via MCP and the connection name is "google-drive-personal"
- Prototype Google Sheet Tax Year 2025 can be found at: https://docs.google.com/spreadsheets/d/1LPu8pOIuPIf6CaHY4D5gnH9yfSYMl01UgRVuPBx6bjQ/edit?gid=0#gid=0
- Prototype Google Sheet Tax Year 2026 can be found at: https://docs.google.com/spreadsheets/d/1MW2qq5L2ITGOQSgZR3KbzSBYlY3bOboXl1Ro_mBmSLc/edit?gid=0#gid=0


### 3.3 State Management & Logging
- **Local Log (`processed_statements.md`):** A markdown file that tracks `Date Processed`, `File Name`, `Transaction Count`, and `Status`.
- **Duplicate Prevention:** The system should check the log before processing a file to avoid double-counting.

### 3.4 UI/UX Specifications
- **Theme:** "Lichen Ledger" (Clean, Minimal, Forest Greens, Slate Blues).
- **Navigation:** Sidebar with Year Selector and Monthly tabs.
- **Dashboard:**
    - Summary Cards: "Total Expenses Found", "Auto-Categorized".
    - Upload Zone: Centrally located, supporting drag-and-drop.
    - Processed Statements Log: A table view of the markdown log contents for the selected period.
- **Feedback:** Clear "Sync Success" state with transaction counts and visual confirmation.

## 4. Technical Constraints
- **Environment:** Local machine or cloud personal server.
- **Frontend:** HTML/CSS (provided by Stitch), likely paired with a lightweight framework (React/Vue/Svelte).
- **Backend:** Node.js or Python to handle file system operations, API calls (Google Sheets), and LLM integration.

## 5. Success Metrics
- Minimal manual data entry (only for category confirmation).
- 100% accuracy in syncing validated data to Google Sheets.
- At-a-glance visibility of "Tax Season" completion status across multiple years.
- Intelligent new expense category recognition and Google Sheet Category updating

## 6. Reference Files
- The following files are in your working folder
- "Product Requirements Document Consulting.md" | This document is your PRD Reference file
- "Consulting_Expense_Tracker_Main_Screen_01.html" | your main working screen frontend layout reference (Provided by Stitch)
- "Consulting_Expense_Tracker_Success_Screen_02.html" | your upload success working screen frontend layout reference (Provided by Stitch)
- "Consulting_Expense_Tracker_Main_Screen_01.png" | Main working screen comparison image for your success evaluation when building
- "Consulting_Expense_Tracker_Success_Screen_02.png" | Upload success screen comparison image for your success evaluation when building
