from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture()
def sample_repo(tmp_path: Path) -> Path:
    root = tmp_path / "sample"
    root.mkdir()
    (root / "src" / "sample").mkdir(parents=True)
    (root / "tests").mkdir()
    (root / "README.md").write_text("# Sample\n", encoding="utf-8")
    (root / "pyproject.toml").write_text("[project]\nname='sample'\n", encoding="utf-8")
    (root / "src" / "sample" / "app.py").write_text("def hello():\n    return 'hi'\n", encoding="utf-8")
    (root / "tests" / "test_app.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    (root / ".env").write_text("SECRET_KEY=real_secret_value\n", encoding="utf-8")
    (root / "dist").mkdir()
    (root / "dist" / "bundle.js").write_text("large build output", encoding="utf-8")
    return root
