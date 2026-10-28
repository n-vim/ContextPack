from __future__ import annotations

from contextpack.detector import detect_project_type, detect_tools


def test_detect_python_project(sample_repo):
    assert detect_project_type(sample_repo) == "python"


def test_detect_tools(sample_repo):
    tools = detect_tools(sample_repo)
    assert "pytest" in tools
