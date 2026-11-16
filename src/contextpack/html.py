"""HTML report rendering."""

from __future__ import annotations

import html

from .insights import build_insights
from .models import ScanResult
from .tokenizer import format_tokens


def render_html_report(scan: ScanResult) -> str:
    """Render a simple standalone HTML report."""

    file_rows = "\n".join(
        f"<tr><td>{html.escape(item.relative_path)}</td><td>{html.escape(item.language)}</td>"
        f"<td>{item.token_estimate}</td><td>{item.size_bytes}</td></tr>"
        for item in scan.files[:200]
    )
    insight_rows = "\n".join(
        f"<li><strong>{html.escape(item.title)}</strong> "
        f"<code>{html.escape(item.severity)}</code><br>{html.escape(item.detail)}<br>"
        f"<em>{html.escape(item.suggestion)}</em></li>"
        for item in build_insights(scan)
    )
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>ContextPack Report - {html.escape(scan.root.name)}</title>
  <style>
    body {{ font-family: system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif; margin: 40px; color: #17202a; }}
    h1, h2 {{ color: #0f172a; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; }}
    .card {{ border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; background: #f8fafc; }}
    .value {{ font-size: 24px; font-weight: 700; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 16px; }}
    th, td {{ border-bottom: 1px solid #e5e7eb; padding: 10px; text-align: left; }}
    code {{ background: #eef2ff; padding: 2px 6px; border-radius: 6px; }}
  </style>
</head>
<body>
  <h1>ContextPack Report</h1>
  <p>Project: <strong>{html.escape(scan.root.name)}</strong></p>
  <div class=\"cards\">
    <div class=\"card\"><div>Project Type</div><div class=\"value\">{html.escape(scan.project_type)}</div></div>
    <div class=\"card\"><div>Files</div><div class=\"value\">{len(scan.files)}</div></div>
    <div class=\"card\"><div>Skipped</div><div class=\"value\">{len(scan.skipped)}</div></div>
    <div class=\"card\"><div>Tokens</div><div class=\"value\">{format_tokens(scan.total_tokens)}</div></div>
  </div>
  <h2>Insights</h2>
  <ul>{insight_rows}</ul>
  <h2>Included Files</h2>
  <table>
    <thead><tr><th>Path</th><th>Language</th><th>Tokens</th><th>Bytes</th></tr></thead>
    <tbody>{file_rows}</tbody>
  </table>
</body>
</html>
"""
