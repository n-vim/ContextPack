from __future__ import annotations

from contextpack.tree import build_tree


def test_build_tree(sample_repo):
    output = build_tree(sample_repo)
    assert "sample/" in output
    assert "README.md" in output
    assert "dist" not in output
