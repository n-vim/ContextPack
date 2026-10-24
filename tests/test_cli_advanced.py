from __future__ import annotations

from typer.testing import CliRunner

from contextpack.cli import app

runner = CliRunner()


def test_cli_profiles():
    result = runner.invoke(app, ["profiles"])
    assert result.exit_code == 0
    assert "compact" in result.output


def test_cli_manifest(sample_repo):
    output = sample_repo / "manifest.json"
    result = runner.invoke(app, ["manifest", str(sample_repo), "--output", str(output)])
    assert result.exit_code == 0
    assert output.exists()


def test_cli_split(sample_repo):
    output_dir = sample_repo / "chunks"
    result = runner.invoke(app, ["split", str(sample_repo), "--output-dir", str(output_dir), "--max-tokens", "40"])
    assert result.exit_code == 0
    assert (output_dir / "README.md").exists()


def test_cli_index_and_insights(sample_repo):
    index = sample_repo / "index.md"
    result = runner.invoke(app, ["index", str(sample_repo), "--output", str(index)])
    assert result.exit_code == 0
    assert index.exists()
    result = runner.invoke(app, ["insights", str(sample_repo)])
    assert result.exit_code == 0
    assert "ContextPack Insights" in result.output


def test_cli_doctor_and_workspace(sample_repo):
    result = runner.invoke(app, ["doctor", str(sample_repo)])
    assert result.exit_code == 0
    result = runner.invoke(app, ["workspace", str(sample_repo)])
    assert result.exit_code == 0
    assert (sample_repo / ".contextpack" / "README.md").exists()
