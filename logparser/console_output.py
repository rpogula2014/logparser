"""
Console output formatting and display functions.
"""

from collections import Counter


class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[91m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


def print_row(r: dict, use_color: bool = True):
    """Print a result row with optional color highlighting."""
    is_failed = r['result'] == 'LOCK FAILED'
    has_time_diff = r['time_diff_seconds'] > 0

    row = f"{r['file']:<30} {r['del_id']:<15} {r['wait_start']:<20} {r['result_time']:<20} {r['time_diff_seconds']:<15.2f} {r['result']}"

    if use_color:
        if is_failed:
            print(f"{Colors.RED}{Colors.BOLD}{row}{Colors.RESET}")
        elif has_time_diff:
            print(f"{Colors.RED}{row}{Colors.RESET}")
        else:
            print(f"{Colors.GREEN}{row}{Colors.RESET}")
    else:
        print(row)


def print_summary(all_results: list[dict], stats: dict, files_processed: int):
    """Print the WDD lock analysis summary to console."""
    print(f"\n{'='*120}")
    print(f"SUMMARY: Processed {files_processed} file(s), found {len(all_results)} WDD lock attempt(s)")
    print(f"{'='*120}")
    print(f"{Colors.RED}# RED = LOCK FAILED{Colors.RESET}  |  {Colors.RED}# RED = Time Diff > 0{Colors.RESET}  |  {Colors.GREEN}# GREEN = Success (no delay){Colors.RESET}")
    print(f"{'='*120}\n")

    if all_results:
        # Print header
        header = f"{'File':<30} {'Del ID':<15} {'Wait Start':<20} {'Result Time':<20} {'Time Diff (s)':<15} {'Result'}"
        print(f"{Colors.BOLD}{header}{Colors.RESET}")
        print(f"{'-'*30} {'-'*15} {'-'*20} {'-'*20} {'-'*15} {'-'*15}")

        for r in all_results:
            print_row(r)

        print(f"\n{'='*120}")
        print(f"{Colors.BOLD}STATS:{Colors.RESET}")
        print(f"  Total lock attempts:    {stats['total']}")
        print(f"  {Colors.GREEN}Successful locks:       {stats['success']}{Colors.RESET}")
        print(f"  {Colors.RED}Failed locks:           {stats['failed']}{Colors.RESET}")
        print(f"  {Colors.RED}Entries with delay > 0: {stats['with_delay']}{Colors.RESET}")

        failed = [r for r in all_results if r['result'] == 'LOCK FAILED']
        success = [r for r in all_results if r['result'] == 'LOCK SUCCESS']

        if failed:
            avg_fail_time = sum(r['time_diff_seconds'] for r in failed) / len(failed)
            max_fail_time = max(r['time_diff_seconds'] for r in failed)
            print(f"  {Colors.RED}Avg time for failed:    {avg_fail_time:.2f} seconds{Colors.RESET}")
            print(f"  {Colors.RED}Max time for failed:    {max_fail_time:.2f} seconds{Colors.RESET}")

        if success:
            avg_success_time = sum(r['time_diff_seconds'] for r in success) / len(success)
            print(f"  {Colors.GREEN}Avg time for success:   {avg_success_time:.2f} seconds{Colors.RESET}")


def print_oracle_errors(oracle_errors: list[dict]):
    """Print Oracle errors summary to console."""
    print(f"\n{'='*120}")
    print(f"{Colors.BOLD}ORACLE ERRORS (excluding ORA-01403):{Colors.RESET}")
    print(f"{'='*120}")

    if oracle_errors:
        error_counts = Counter(e['error_code'] for e in oracle_errors)

        print(f"  {Colors.RED}Total Oracle errors found: {len(oracle_errors)}{Colors.RESET}")
        print(f"\n  Error breakdown:")
        for code, count in error_counts.most_common():
            print(f"    {Colors.RED}{code}: {count} occurrence(s){Colors.RESET}")

        print(f"\n  {Colors.BOLD}Error Details:{Colors.RESET}")
        print(f"  {'-'*116}")
        for err in oracle_errors[:20]:  # Show first 20 errors in console
            print(f"  {Colors.RED}{err['error_code']}{Colors.RESET} | {err['file']} | Line {err['line_number']} | {err['timestamp']}")
            print(f"    {err['message'][:100]}{'...' if len(err['message']) > 100 else ''}")

        if len(oracle_errors) > 20:
            print(f"\n  ... and {len(oracle_errors) - 20} more errors (see HTML/Excel report for full list)")
    else:
        print(f"  {Colors.GREEN}No Oracle errors found (excluding ORA-01403){Colors.RESET}")
