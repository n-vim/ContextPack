from __future__ import annotations

from contextpack.scanner import scan_repository


def test_scan_repository_includes_source(sample_repo):
    scan = scan_repository(sample_repo)
    paths = {item.relative_path for item in scan.files}
    assert "README.md" in paths
    assert "src/sample/app.py" in paths
    assert ".env" not in paths


def test_scan_repository_skips_dist(sample_repo):
    scan = scan_repository(sample_repo)
    skipped = {item.relative_path for item in scan.skipped}
    assert "dist/bundle.js" in skipped
