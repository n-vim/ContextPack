from __future__ import annotations

from contextpack.safety import is_risky_filename, redact_secrets


def test_redact_secret_assignment():
    text = "API_KEY=sk_test_1234567890abcdefghijklmnop"
    redacted = redact_secrets(text)
    assert "abcdefghijklmnop" not in redacted
    assert "****" in redacted


def test_risky_filename():
    assert is_risky_filename(".env") is True
    assert is_risky_filename("README.md") is False
