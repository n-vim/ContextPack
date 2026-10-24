from __future__ import annotations

from contextpack.bundler import build_bundle


def test_build_bundle(sample_repo):
    bundle = build_bundle(sample_repo)
    assert "# Context Pack: sample" in bundle.output
    assert "src/sample/app.py" in bundle.output
    assert bundle.total_tokens > 0
