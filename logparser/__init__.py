"""
LogParser - WDD Lock Analysis and Oracle Error Detection Tool

A comprehensive log analysis tool for parsing WMS XDock Pegging logs,
detecting WDD lock issues, and identifying Oracle database errors.
"""

from .parsers import extract_wdd_lock_info, extract_oracle_errors, parse_timestamp
from .html_report import generate_html
from .excel_report import generate_excel
from .console_output import print_summary, print_oracle_errors, Colors

__version__ = "1.0.0"
__all__ = [
    'extract_wdd_lock_info',
    'extract_oracle_errors',
    'parse_timestamp',
    'generate_html',
    'generate_excel',
    'print_summary',
    'print_oracle_errors',
    'Colors',
]
