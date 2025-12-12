"""
HTML report generation for WDD Lock Analysis.
"""

from datetime import datetime
from collections import Counter


def generate_html(results: list[dict], output_html: str, stats: dict, files_processed: int, oracle_errors: list[dict] = None):
    """Generate an HTML file with the results table and Oracle errors."""
    if not results and not oracle_errors:
        print("No results to generate HTML.")
        return

    oracle_errors = oracle_errors or []

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WDD Lock Analysis Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            padding: 30px 40px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.2em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .header .subtitle {{
            color: #a0a0a0;
            font-size: 1.1em;
        }}
        .stats-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px 40px;
            background: #f8f9fa;
        }}
        .stat-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        .stat-card.total {{ border-left: 5px solid #4472C4; }}
        .stat-card.success {{ border-left: 5px solid #28a745; }}
        .stat-card.failed {{ border-left: 5px solid #dc3545; }}
        .stat-card.delay {{ border-left: 5px solid #ffc107; }}
        .stat-card.errors {{ border-left: 5px solid #6f42c1; }}
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .stat-card.total .stat-value {{ color: #4472C4; }}
        .stat-card.success .stat-value {{ color: #28a745; }}
        .stat-card.failed .stat-value {{ color: #dc3545; }}
        .stat-card.delay .stat-value {{ color: #ffc107; }}
        .stat-card.errors .stat-value {{ color: #6f42c1; }}
        .stat-label {{
            color: #666;
            font-size: 0.95em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .legend {{
            display: flex;
            justify-content: center;
            gap: 30px;
            padding: 20px;
            background: #f8f9fa;
            flex-wrap: wrap;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.9em;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
        }}
        .legend-color.red {{ background: #ffcccc; border: 1px solid #dc3545; }}
        .legend-color.yellow {{ background: #ffffcc; border: 1px solid #ffc107; }}
        .legend-color.green {{ background: #ccffcc; border: 1px solid #28a745; }}
        .table-container {{
            padding: 20px 40px 40px;
            overflow-x: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.95em;
        }}
        th {{
            background: linear-gradient(135deg, #4472C4 0%, #2c5aa0 100%);
            color: white;
            padding: 15px 12px;
            text-align: center;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 0.85em;
        }}
        td {{
            padding: 12px;
            text-align: center;
            border-bottom: 1px solid #e0e0e0;
        }}
        tr:hover td {{
            background: rgba(0,0,0,0.02);
        }}
        tr.failed td {{
            background: #ffcccc;
        }}
        tr.failed:hover td {{
            background: #ffb3b3;
        }}
        tr.delay td {{
            background: #ffffcc;
        }}
        tr.delay:hover td {{
            background: #ffff99;
        }}
        tr.success td {{
            background: #ccffcc;
        }}
        tr.success:hover td {{
            background: #b3ffb3;
        }}
        .result-badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.85em;
        }}
        .result-badge.failed {{
            background: #dc3545;
            color: white;
        }}
        .result-badge.success {{
            background: #28a745;
            color: white;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            color: #666;
            font-size: 0.9em;
        }}
        .additional-stats {{
            padding: 20px 40px;
            background: white;
        }}
        .additional-stats h3 {{
            margin-bottom: 15px;
            color: #333;
        }}
        .additional-stats p {{
            margin: 5px 0;
            color: #555;
        }}
        .section-header {{
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
            color: white;
            padding: 20px 40px;
            margin-top: 30px;
        }}
        .section-header h2 {{
            margin: 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .section-header .count {{
            background: rgba(255,255,255,0.2);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8em;
        }}
        .oracle-error-card {{
            background: #fff5f5;
            border-left: 4px solid #dc3545;
            margin: 15px 40px;
            padding: 15px 20px;
            border-radius: 0 8px 8px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .oracle-error-card:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .error-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .error-code {{
            background: #dc3545;
            color: white;
            padding: 5px 12px;
            border-radius: 4px;
            font-weight: bold;
            font-family: monospace;
        }}
        .error-meta {{
            display: flex;
            gap: 20px;
            color: #666;
            font-size: 0.9em;
        }}
        .error-meta span {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        .error-message {{
            background: #f8f9fa;
            padding: 10px 15px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 0.9em;
            color: #333;
            word-break: break-word;
            margin-top: 10px;
        }}
        .no-errors {{
            text-align: center;
            padding: 40px;
            color: #28a745;
            font-size: 1.2em;
        }}
        .no-errors .icon {{
            font-size: 3em;
            margin-bottom: 10px;
        }}
        .error-summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            padding: 20px 40px;
            background: #fff5f5;
        }}
        .error-summary-item {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .error-summary-item .code {{
            font-family: monospace;
            font-weight: bold;
            color: #dc3545;
        }}
        .error-summary-item .count {{
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>WDD Lock Analysis Report</h1>
            <p class="subtitle">Processed {files_processed} file(s) - Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <div class="stats-container">
            <div class="stat-card total">
                <div class="stat-value">{stats['total']}</div>
                <div class="stat-label">Total Attempts</div>
            </div>
            <div class="stat-card success">
                <div class="stat-value">{stats['success']}</div>
                <div class="stat-label">Successful Locks</div>
            </div>
            <div class="stat-card failed">
                <div class="stat-value">{stats['failed']}</div>
                <div class="stat-label">Failed Locks</div>
            </div>
            <div class="stat-card delay">
                <div class="stat-value">{stats['with_delay']}</div>
                <div class="stat-label">With Delay > 0</div>
            </div>
            <div class="stat-card errors">
                <div class="stat-value">{len(oracle_errors)}</div>
                <div class="stat-label">Oracle Errors</div>
            </div>
        </div>

        <div class="legend">
            <div class="legend-item">
                <div class="legend-color red"></div>
                <span>LOCK FAILED</span>
            </div>
            <div class="legend-item">
                <div class="legend-color yellow"></div>
                <span>Time Diff > 0</span>
            </div>
            <div class="legend-item">
                <div class="legend-color green"></div>
                <span>Success (no delay)</span>
            </div>
        </div>

        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>File</th>
                        <th>Del ID</th>
                        <th>Wait Start</th>
                        <th>Result Time</th>
                        <th>Time Diff (s)</th>
                        <th>Result</th>
                    </tr>
                </thead>
                <tbody>
"""

    for r in results:
        if r['result'] == 'LOCK FAILED':
            row_class = 'failed'
            badge_class = 'failed'
        elif r['time_diff_seconds'] > 0:
            row_class = 'delay'
            badge_class = 'success'
        else:
            row_class = 'success'
            badge_class = 'success'

        html_content += f"""                    <tr class="{row_class}">
                        <td>{r['file']}</td>
                        <td>{r['del_id']}</td>
                        <td>{r['wait_start']}</td>
                        <td>{r['result_time']}</td>
                        <td>{r['time_diff_seconds']:.2f}</td>
                        <td><span class="result-badge {badge_class}">{r['result']}</span></td>
                    </tr>
"""

    # Calculate additional stats
    failed = [r for r in results if r['result'] == 'LOCK FAILED']
    success = [r for r in results if r['result'] == 'LOCK SUCCESS']

    additional_stats_html = ""
    if failed:
        avg_fail_time = sum(r['time_diff_seconds'] for r in failed) / len(failed)
        max_fail_time = max(r['time_diff_seconds'] for r in failed)
        additional_stats_html += f"<p><strong>Avg time for failed:</strong> {avg_fail_time:.2f} seconds</p>"
        additional_stats_html += f"<p><strong>Max time for failed:</strong> {max_fail_time:.2f} seconds</p>"

    if success:
        avg_success_time = sum(r['time_diff_seconds'] for r in success) / len(success)
        additional_stats_html += f"<p><strong>Avg time for success:</strong> {avg_success_time:.2f} seconds</p>"

    html_content += f"""                </tbody>
            </table>
        </div>

        <div class="additional-stats">
            <h3>Additional Statistics</h3>
            {additional_stats_html}
        </div>
"""

    # Oracle Errors Section
    html_content += f"""
        <div class="section-header">
            <h2>Oracle Database Errors <span class="count">{len(oracle_errors)} found (excluding ORA-01403)</span></h2>
        </div>
"""

    if oracle_errors:
        # Error summary by code
        error_counts = Counter(e['error_code'] for e in oracle_errors)

        html_content += """        <div class="error-summary">
"""
        for code, count in error_counts.most_common(10):
            html_content += f"""            <div class="error-summary-item">
                <div class="code">{code}</div>
                <div class="count">{count}</div>
            </div>
"""
        html_content += """        </div>
"""

        # Individual error cards
        for err in oracle_errors:
            html_content += f"""        <div class="oracle-error-card">
            <div class="error-header">
                <span class="error-code">{err['error_code']}</span>
                <div class="error-meta">
                    <span>File: {err['file']}</span>
                    <span>Line: {err['line_number']}</span>
                    <span>Time: {err['timestamp']}</span>
                    <span>Context: {err['context']}</span>
                </div>
            </div>
            <div class="error-message">{err['message']}</div>
        </div>
"""
    else:
        html_content += """        <div class="no-errors">
            <div class="icon">&#10004;</div>
            <div>No Oracle errors found (excluding ORA-01403)</div>
        </div>
"""

    html_content += """
        <div class="footer">
            WDD Lock Analysis Report - Generated by logparser.py
        </div>
    </div>
</body>
</html>
"""

    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"HTML report saved to: {output_html}")
