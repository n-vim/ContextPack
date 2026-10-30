from __future__ import annotations

from contextpack.tokenizer import estimate_tokens, format_tokens


def test_estimate_tokens():
    assert estimate_tokens("hello world") > 0


def test_format_tokens():
    assert format_tokens(1200) == "1.2K"
