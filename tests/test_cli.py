from __future__ import annotations

from typer.testing import CliRunner

from contextpack.cli import app

runner = CliRunner()


def test_cli_summarize(sample_repo):
    result = runner.invoke(app, ["summarize", str(sample_repo)])
    assert result.exit_code == 0
    assert "sample" in result.output


def test_cli_build_output(sample_repo):
    output = sample_repo / "CONTEXT.md"
    result = runner.invoke(app, ["build", str(sample_repo), "--output", str(output)])
    assert result.exit_code == 0
    assert output.exists()


def test_cli_export_json(sample_repo):
    output = sample_repo / "report.json"
    result = runner.invoke(app, ["export", str(sample_repo), "--format", "json", "--output", str(output)])
    assert result.exit_code == 0
    assert output.exists()
