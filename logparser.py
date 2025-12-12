#!/usr/bin/env python3
"""
LogParser - WDD Lock Analysis and Oracle Error Detection Tool

Main entry point for the log parser application.
Analyzes WMS XDock Pegging logs for WDD lock issues and Oracle database errors.

Usage:
    python logparser.py <folder_path> [output_file] [file_pattern]
    python logparser.py <folder_path> --id <search_id> [file_pattern]

Example:
    python logparser.py /path/to/logs results.csv *.log
    python logparser.py /path/to/logs --id 12345678 *.log

Outputs:
    - CSV file with WDD lock results
    - HTML report with styled tables and Oracle errors
    - Excel file with multiple sheets (WDD locks, Oracle errors, Error summary)
    - ID trace files (when using --id option)
"""

import sys
from pathlib import Path

# Import from the logparser package
from logparser.parsers import extract_wdd_lock_info, extract_oracle_errors, extract_id_traces
# from logparser.html_report import generate_html
from logparser.excel_report import generate_excel
from logparser.console_output import print_summary, print_oracle_errors


def process_folder(folder_path: str, output_path: str = None, file_pattern: str = "*.log", generate_reports: bool = True):
    """
    Process all log files in a folder.

    Args:
        folder_path: Path to the folder containing log files
        output_path: Base path for output files (optional)
        file_pattern: Glob pattern for matching log files
        generate_reports: Whether to generate HTML and Excel reports

    Returns:
        Tuple of (wdd_results, oracle_errors)
    """
    folder = Path(folder_path)

    if not folder.exists():
        print(f"Error: Folder '{folder_path}' not found")
        sys.exit(1)

    all_results = []
    all_oracle_errors = []
    files_processed = 0

    log_files = list(folder.glob(file_pattern))

    if not log_files:
        print(f"No files matching '{file_pattern}' found in {folder_path}")
        sys.exit(1)

    print(f"Found {len(log_files)} file(s) to process...")

    for log_file in log_files:
        file_size_mb = log_file.stat().st_size / (1024 * 1024)
        print(f"Processing {log_file.name} ({file_size_mb:.2f} MB)...")

        # Extract WDD lock info
        results = extract_wdd_lock_info(str(log_file))
        all_results.extend(results)

        # Extract Oracle errors
        oracle_errors = extract_oracle_errors(str(log_file))
        all_oracle_errors.extend(oracle_errors)

        files_processed += 1

    # Calculate stats
    failed = [r for r in all_results if r['result'] == 'LOCK FAILED']
    success = [r for r in all_results if r['result'] == 'LOCK SUCCESS']
    with_delay = [r for r in all_results if r['time_diff_seconds'] > 0]

    stats = {
        'total': len(all_results),
        'success': len(success),
        'failed': len(failed),
        'with_delay': len(with_delay)
    }

    # Print to console
    print_summary(all_results, stats, files_processed)
    print_oracle_errors(all_oracle_errors)

    # Generate reports
    if generate_reports:
        base_path = output_path.rsplit('.', 1)[0] if output_path else 'wdd_lock_results'

        # # Generate HTML
        # html_path = base_path + '.html'
        # generate_html(all_results, html_path, stats, files_processed, all_oracle_errors)

        # Generate Excel (now includes Oracle errors)
        excel_path = base_path + '.xlsx'
        generate_excel(all_results, excel_path, stats, all_oracle_errors)

    # Write to CSV (WDD locks only - Oracle errors are in Excel)
    if output_path and all_results:
        with open(output_path, 'w', encoding='utf-8') as out:
            out.write("File,Del_ID,Wait_Start,Result_Time,Time_Diff_Seconds,Result\n")
            for r in all_results:
                out.write(f"{r['file']},{r['del_id']},{r['wait_start']},{r['result_time']},{r['time_diff_seconds']},{r['result']}\n")
        print(f"CSV saved to: {output_path}")

    return all_results, all_oracle_errors


def extract_id_from_folder(folder_path: str, search_id: str, file_pattern: str = "*.log"):
    """
    Extract all traces for a specific ID from log files and save to separate files.

    Args:
        folder_path: Path to the folder containing log files
        search_id: The ID to search for
        file_pattern: Glob pattern for matching log files
    """
    folder = Path(folder_path)

    if not folder.exists():
        print(f"Error: Folder '{folder_path}' not found")
        sys.exit(1)

    log_files = list(folder.glob(file_pattern))

    if not log_files:
        print(f"No files matching '{file_pattern}' found in {folder_path}")
        sys.exit(1)

    print(f"Searching for ID '{search_id}' in {len(log_files)} file(s)...")

    output_dir = folder / f"id_traces_{search_id}"
    files_with_id = 0

    for log_file in log_files:
        file_size_mb = log_file.stat().st_size / (1024 * 1024)
        print(f"Scanning {log_file.name} ({file_size_mb:.2f} MB)...", end=" ")

        trace_lines, first_line, last_line = extract_id_traces(str(log_file), search_id)

        if trace_lines:
            # Create output directory if needed
            output_dir.mkdir(exist_ok=True)

            # Generate output filename
            output_file = output_dir / f"{log_file.stem}_id_{search_id}.log"

            # Write the trace lines
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# Extracted traces for ID: {search_id}\n")
                f.write(f"# Source file: {log_file.name}\n")
                f.write(f"# Lines {first_line} to {last_line} ({last_line - first_line + 1} lines)\n")
                f.write("#" + "=" * 79 + "\n\n")
                f.writelines(trace_lines)

            print(f"FOUND (lines {first_line}-{last_line}) -> {output_file.name}")
            files_with_id += 1
        else:
            print("NOT FOUND")

    print(f"\n{'=' * 60}")
    if files_with_id > 0:
        print(f"ID '{search_id}' found in {files_with_id} file(s)")
        print(f"Trace files saved to: {output_dir}")
    else:
        print(f"ID '{search_id}' was not found in any files")


def main():
    """Main entry point for the log parser."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    folder_path = sys.argv[1]

    # Check for --id flag for trace extraction mode
    if len(sys.argv) > 2 and sys.argv[2] == "--id":
        if len(sys.argv) < 4:
            print("Error: --id requires a search ID value")
            print("Usage: python logparser.py <folder_path> --id <search_id> [file_pattern]")
            sys.exit(1)
        search_id = sys.argv[3]
        file_pattern = sys.argv[4] if len(sys.argv) > 4 else "*.log"
        extract_id_from_folder(folder_path, search_id, file_pattern)
    else:
        # Normal mode - WDD lock analysis
        output_file = sys.argv[2] if len(sys.argv) > 2 else "wdd_lock_results.csv"
        file_pattern = sys.argv[3] if len(sys.argv) > 3 else "*.log"
        process_folder(folder_path, output_file, file_pattern)


if __name__ == "__main__":
    main()
