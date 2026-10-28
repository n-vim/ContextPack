from __future__ import annotations

import json

from contextpack.reports import render_json_report, render_markdown_report
from contextpack.scanner import scan_repository


def test_json_report(sample_repo):
    scan = scan_repository(sample_repo)
    data = json.loads(render_json_report(scan))
    assert data["project"] == "sample"
    assert data["files_included"] >= 1


def test_markdown_report(sample_repo):
    scan = scan_repository(sample_repo)
    report = render_markdown_report(scan)
    assert "# ContextPack Report" in report
