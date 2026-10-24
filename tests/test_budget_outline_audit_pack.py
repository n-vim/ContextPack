from pathlib import Path

from contextpack.audit import run_context_audit
from contextpack.budget import build_budget_report, render_budget_markdown
from contextpack.config import BundleConfig
from contextpack.outline import build_outline, render_outline_markdown
from contextpack.packager import create_artifact_folder, create_artifact_zip
from contextpack.scanner import scan_repository


def test_budget_report_groups_by_top_level(tmp_path: Path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("def main():\n    return 'ok'\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    scan = scan_repository(tmp_path)

    report = build_budget_report(scan, budget=1000)
    names = {group.name for group in report.groups}

    assert "src" in names
    assert "root" in names
    assert "within budget" in render_budget_markdown(report)


def test_outline_extracts_python_symbols(tmp_path: Path):
    (tmp_path / "tool.py").write_text("class Runner:\n    pass\n\ndef run():\n    pass\n", encoding="utf-8")
    scan = scan_repository(tmp_path)

    symbols = build_outline(scan)
    rendered = render_outline_markdown(scan)

    assert any(symbol.name == "Runner" for symbol in symbols)
    assert any(symbol.name == "run" for symbol in symbols)
    assert "Context Outline" in rendered


def test_audit_reports_disabled_redaction(tmp_path: Path):
    (tmp_path / "settings.py").write_text("API_KEY='abc123456789'\n", encoding="utf-8")
    config = BundleConfig(redact_secrets=False)
    scan = scan_repository(tmp_path, config=config)

    findings = run_context_audit(scan, config)

    assert any("redaction" in finding.title.lower() for finding in findings)


def test_packager_creates_artifact_folder_and_zip(tmp_path: Path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("def main():\n    return 1\n", encoding="utf-8")
    artifact_dir = tmp_path / "artifacts"

    created = create_artifact_folder(tmp_path, artifact_dir, force=True)
    zip_path = create_artifact_zip(artifact_dir, tmp_path / "artifacts.zip", force=True)

    created_names = {path.name for path in created}
    assert "CONTEXT.md" in created_names
    assert "context-audit.md" in created_names
    assert zip_path.exists()
