# LogParser Documentation

## What This Code Does

This code analyzes log files from WMS (Warehouse Management System) XDock Pegging operations to find problems with database record locking and Oracle database errors.

In simple terms, it:

- Scans through large log files looking for WDD (Warehouse Delivery Detail) lock attempts
- Tracks whether locks succeeded or failed and how long they took
- Finds Oracle database errors (like ORA-00054, ORA-01422, etc.)
- Creates reports in multiple formats (CSV, Excel, HTML) for easy analysis

Think of it like a detective searching through thousands of pages of system logs to find and highlight all the important problems, then organizing them into easy-to-read reports.

---

## How It Works

### 1. **First, it reads your log files**

   - You point it to a folder containing `.log` files
   - It processes each file one by one, reading through every line
   - Large files (hundreds of MB) are handled efficiently

### 2. **Then, it hunts for WDD lock patterns**

- It looks for lines containing `WMS_XDock_Pegging_Pub:`
- It finds the Delivery ID (`Del Id`) being processed
- It tracks when a lock wait started (`wdd update wait time`)
- It records whether the lock succeeded (`RM - Got WDD lock`) or failed (`Could not lock the WDD demand line record`)
- It calculates how long each lock attempt took

### 3. **Next, it searches for Oracle errors**

   - It finds all `ORA-XXXXX` error codes in the logs
   - It skips `ORA-01403` (no data found) since this is often expected behavior
   - It captures the error message, timestamp, line number, and context

### 4. **Finally, it creates reports**

   - **CSV file**: Simple spreadsheet with WDD lock results
   - **Excel file**: Professional workbook with multiple sheets (WDD locks, Oracle errors, Error summary)
   - **Console output**: Color-coded summary displayed in your terminal

---

## What You Need Before Running

### Software Requirements

- **Python version**: 3.9 or higher
- **Required packages**:

  ```
  pip install openpyxl
  ```
  (openpyxl is needed for Excel report generation)

### Input Requirements

- **Log files**: One or more `.log` files from WMS XDock Pegging operations
- **Log format**: Files must contain timestamps in format `[DD-MON-YY HH:MM:SS]`

### File/Data Requirements

- Log files should be in a single folder
- Files can be any size (the tool handles large files efficiently)

---

## How to Run This Code

### Quick Start

```bash
python logparser.py /path/to/your/logs
```

### Detailed Steps

**Step 1: Install Required Packages**

```bash
pip install openpyxl
```

**Step 2: Prepare Your Log Files**

- Place all log files you want to analyze in a single folder
- Ensure files have `.log` extension (or specify your pattern)

**Step 3: Run the Code**

Basic usage (analyzes all .log files):
```bash
python logparser.py /path/to/logs
```

With custom output filename:
```bash
python logparser.py /path/to/logs my_results.csv
```

With custom file pattern:
```bash
python logparser.py /path/to/logs results.csv "*.txt"
```

**Step 4: Find Your Output**
After running, you'll find these files in your current directory:

- `wdd_lock_results.csv` - CSV with WDD lock data
- `wdd_lock_results.xlsx` - Excel workbook with all reports

### ID Trace Mode

To extract all log lines for a specific ID:

```bash
python logparser.py /path/to/logs --id 12345678
```

This creates a folder `id_traces_12345678` containing extracted traces from each log file where the ID was found.

### Common Ways to Run

| Scenario | Command | What It Does |
|----------|---------|--------------|
| Basic analysis | `python logparser.py ./logs` | Analyzes all .log files in ./logs folder |
| Custom output | `python logparser.py ./logs output.csv` | Saves results to output.csv/xlsx |
| Different file type | `python logparser.py ./logs results.csv "*.txt"` | Analyzes .txt files instead |
| Trace specific ID | `python logparser.py ./logs --id 98765` | Extracts all lines mentioning ID 98765 |

---

## Use Cases

### Use Case 1: Daily Lock Issue Analysis

**Scenario:** You need to check overnight batch processing logs for lock failures.
**How to use:**
```bash
python logparser.py /app/logs/overnight results_$(date +%Y%m%d).csv
```
**Example:** Running this on Monday morning gives you `results_20241211.csv` with all weekend lock issues summarized.

### Use Case 2: Investigating a Specific Delivery

**Scenario:** A user reports that delivery ID 45678901 had problems. You need to find all related log entries.
**How to use:**
```bash
python logparser.py /app/logs --id 45678901
```
**Example:** This creates `id_traces_45678901/` folder with all log lines mentioning this delivery, making it easy to trace the issue.

### Use Case 3: Oracle Error Audit

**Scenario:** DBA needs a summary of all Oracle errors for the past week.
**How to use:**
```bash
python logparser.py /app/logs/week results.csv
```
**Example:** Open `results.xlsx` and check the "Oracle Errors" and "Error Summary" sheets for a complete breakdown of all database errors.

### Use Case 4: Performance Investigation

**Scenario:** System is slow and you suspect lock contention.
**How to use:**
```bash
python logparser.py /app/logs perf_analysis.csv
```
**Example:** Check the "Time Diff (s)" column in results - entries with high values indicate lock wait times that may be causing slowdowns.

---

## Understanding the Output

### Console Output Colors

| Color | Meaning |
|-------|---------|
| **RED BOLD** | Lock FAILED - the system could not obtain the lock |
| **RED** | Lock succeeded but with delay > 0 seconds |
| **GREEN** | Lock succeeded immediately (no delay) |

### CSV File Columns

| Column | Description |
|--------|-------------|
| File | Source log file name |
| Del_ID | Delivery ID being processed |
| Wait_Start | When the lock wait began |
| Result_Time | When the lock attempt completed |
| Time_Diff_Seconds | How long the lock took (in seconds) |
| Result | "LOCK SUCCESS" or "LOCK FAILED" |

### Excel Workbook Sheets

**Sheet 1: WDD Lock Results**

- Same data as CSV but with color-coded rows
- Legend included at top
- Statistics summary

**Sheet 2: Oracle Errors**

- Error code (ORA-XXXXX)
- Source file and line number
- Timestamp and context
- Full error message

**Sheet 3: Error Summary**

- Count of each error code
- Percentage breakdown
- Reference table of common Oracle error descriptions

---

## Module Reference

### Main Script: `logparser.py`

**`process_folder(folder_path, output_path, file_pattern, generate_reports)`**

- Main function that orchestrates the log analysis
- Processes all matching files in a folder
- Generates all output files

**`extract_id_from_folder(folder_path, search_id, file_pattern)`**

- Extracts all traces for a specific ID
- Creates output files in a dedicated folder

### Package: `logparser/`

**`parsers.py`** - Core parsing functions

- `parse_timestamp(line)` - Extracts timestamp from log line
- `extract_wdd_lock_info(file_path)` - Finds WDD lock attempts
- `extract_oracle_errors(file_path)` - Finds Oracle errors
- `extract_id_traces(file_path, search_id)` - Extracts lines for specific ID

**`console_output.py`** - Terminal display

- `print_summary(results, stats, files_processed)` - Prints WDD summary
- `print_oracle_errors(oracle_errors)` - Prints Oracle error summary
- `Colors` class - ANSI color codes for terminal

**`excel_report.py`** - Excel generation

- `generate_excel(results, output_excel, stats, oracle_errors)` - Creates Excel workbook

**`html_report.py`** - HTML generation (currently disabled in main)

- `generate_html(results, output_html, stats, files_processed, oracle_errors)` - Creates HTML report

---

## Troubleshooting

### Problem: "No files matching '*.log' found"

**Why it happens:** The folder path is wrong or files have different extension.
**How to fix:**

1. Check the folder path exists: `ls /your/path`
2. Check file extensions: `ls /your/path/*.log`
3. Try a different pattern: `python logparser.py /path results.csv "*.txt"`

### Problem: "openpyxl not installed"

**Why it happens:** The Excel library is missing.
**How to fix:**
```bash
pip install openpyxl
```

### Problem: Output files are empty

**Why it happens:** Log files don't contain WMS_XDock_Pegging patterns.
**How to fix:**

1. Verify logs are from the right system
2. Check a log file manually for `WMS_XDock_Pegging_Pub:` text
3. The tool still captures Oracle errors even if no WDD locks found

### Problem: UnicodeDecodeError

**Why it happens:** Log file contains unusual characters.
**How to fix:** The tool handles this automatically with `errors='replace'`, but if issues persist, check if logs are in a non-standard encoding.

### Problem: Memory issues with very large files

**Why it happens:** Files are extremely large (multiple GB).
**How to fix:**

1. Split large log files into smaller chunks
2. Process logs day-by-day instead of all at once

---

## Quick Reference

| What | Details |
|------|---------|
| Purpose | Analyze WMS logs for WDD lock issues and Oracle errors |
| Main Input | Folder containing .log files |
| Main Output | CSV, Excel workbook with analysis results |
| Run Command | `python logparser.py /path/to/logs` |
| ID Trace Mode | `python logparser.py /path/to/logs --id <ID>` |
| Required Package | `openpyxl` (for Excel output) |
| Python Version | 3.9+ |

---

## Architecture Overview

```
logparser/
├── logparser.py          # Main entry point
└── logparser/            # Package directory
    ├── __init__.py       # Package exports
    ├── parsers.py        # Log parsing logic
    ├── console_output.py # Terminal display
    ├── excel_report.py   # Excel generation
    └── html_report.py    # HTML generation
```

### Data Flow

1. **Input**: Log files in specified folder
2. **Parsing**: `parsers.py` extracts WDD locks and Oracle errors
3. **Processing**: Main script aggregates results and calculates statistics
4. **Output**: Console display + CSV + Excel (+ HTML if enabled)

---

*Documentation generated for LogParser v1.0.0*
