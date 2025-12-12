"""
Log parsing functions for extracting WDD lock info and Oracle errors.
"""

import re
import os
from datetime import datetime


def parse_timestamp(line: str) -> datetime:
    """Extract timestamp from log line."""
    match = re.search(r'\[(\d{2}-[A-Z]{3}-\d{2}\s+\d{2}:\d{2}:\d{2})\]', line)
    if match:
        return datetime.strptime(match.group(1), '%d-%b-%y %H:%M:%S')
    return None


def extract_oracle_errors(file_path: str) -> list[dict]:
    """
    Extract Oracle database errors from log file (excluding ORA-01403 no data found).
    Returns list of dicts with error code, message, timestamp, and context.
    """
    errors = []
    # Pattern to match ORA-XXXXX errors
    ora_pattern = re.compile(r'(ORA-(\d{5})[:\s].*?)(?:\n|$)', re.IGNORECASE)
    # Context pattern to get surrounding info (skip past timestamp bracket)
    context_pattern = re.compile(r'\]\s*(\w+(?:\.\w+)*(?:_\w+)*):')

    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        line_num = 0
        for line in f:
            line_num += 1
            line = line.rstrip('\n')

            ora_match = ora_pattern.search(line)
            if ora_match:
                error_code = ora_match.group(2)
                # Skip ORA-01403 (no data found) as it's often expected
                if error_code == '01403':
                    continue

                full_error = ora_match.group(1).strip()
                timestamp = parse_timestamp(line)

                # Try to extract context (module/procedure name)
                context_match = context_pattern.search(line)
                context = context_match.group(1) if context_match else 'Unknown'

                errors.append({
                    'error_code': f'ORA-{error_code}',
                    'message': full_error,
                    'timestamp': timestamp.strftime('%d-%b-%y %H:%M:%S') if timestamp else 'N/A',
                    'line_number': line_num,
                    'context': context,
                    'file': os.path.basename(file_path),
                    'full_line': line[:200] + '...' if len(line) > 200 else line
                })

    return errors


def extract_wdd_lock_info(file_path: str) -> list[dict]:
    """
    Extract WDD lock information from log file.
    Returns list of dicts with Del Id, timestamps, time diff, and result.
    """
    results = []
    current_del_id = None
    wait_time_line = None
    wait_timestamp = None

    xdock_pattern = re.compile(r'WMS_XDock_Pegging_Pub:')
    del_id_pattern = re.compile(r'WMS_XDock_Pegging_Pub:\s*Del Id:(\d+)')
    wait_time_pattern = re.compile(r'WMS_XDock_Pegging_Pub:.*wdd update wait time:(\d+)')
    lock_fail_pattern = re.compile(r'WMS_XDock_Pegging_Pub:.*Could not lock the WDD demand line record')
    lock_success_pattern = re.compile(r'WMS_XDock_Pegging_Pub:.*RM - Got WDD lock')

    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.rstrip('\n')

            if not xdock_pattern.search(line):
                continue

            del_match = del_id_pattern.search(line)
            if del_match:
                current_del_id = del_match.group(1)
                wait_time_line = None
                wait_timestamp = None
                continue

            wait_match = wait_time_pattern.search(line)
            if wait_match and current_del_id:
                wait_time_line = line
                wait_timestamp = parse_timestamp(line)
                continue

            if lock_fail_pattern.search(line) and current_del_id and wait_timestamp:
                result_timestamp = parse_timestamp(line)
                if result_timestamp:
                    time_diff = (result_timestamp - wait_timestamp).total_seconds()
                    results.append({
                        'del_id': current_del_id,
                        'wait_start': wait_timestamp.strftime('%d-%b-%y %H:%M:%S'),
                        'result_time': result_timestamp.strftime('%d-%b-%y %H:%M:%S'),
                        'time_diff_seconds': time_diff,
                        'result': 'LOCK FAILED',
                        'file': os.path.basename(file_path)
                    })
                current_del_id = None
                wait_time_line = None
                wait_timestamp = None
                continue

            if lock_success_pattern.search(line) and current_del_id and wait_timestamp:
                result_timestamp = parse_timestamp(line)
                if result_timestamp:
                    time_diff = (result_timestamp - wait_timestamp).total_seconds()
                    results.append({
                        'del_id': current_del_id,
                        'wait_start': wait_timestamp.strftime('%d-%b-%y %H:%M:%S'),
                        'result_time': result_timestamp.strftime('%d-%b-%y %H:%M:%S'),
                        'time_diff_seconds': time_diff,
                        'result': 'LOCK SUCCESS',
                        'file': os.path.basename(file_path)
                    })
                current_del_id = None
                wait_time_line = None
                wait_timestamp = None
                continue

    return results


def extract_id_traces(file_path: str, search_id: str) -> tuple[list[str], int, int]:
    """
    Extract all trace lines from the first occurrence to the last occurrence of a specific ID.

    Args:
        file_path: Path to the log file
        search_id: The ID to search for (e.g., Del Id, or any identifier)

    Returns:
        Tuple of (list of trace lines, first_line_number, last_line_number)
        Returns empty list and 0,0 if ID not found
    """
    first_occurrence = None
    last_occurrence = None
    all_lines = []

    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        for line_num, line in enumerate(f, 1):
            all_lines.append(line)
            if search_id in line:
                if first_occurrence is None:
                    first_occurrence = line_num
                last_occurrence = line_num

    if first_occurrence is None or last_occurrence is None:
        return [], 0, 0

    # Extract lines from first to last occurrence (convert to 0-based index)
    trace_lines = all_lines[first_occurrence - 1:last_occurrence]

    return trace_lines, first_occurrence, last_occurrence
