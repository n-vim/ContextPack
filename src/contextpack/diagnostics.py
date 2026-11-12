"""Diagnostic checks for ContextPack."""

from __future__ import annotations

from pathlib import Path

from .config import CONFIG_FILE_NAME, load_config
from .models import DiagnosticResult
from .scanner import scan_repository
from .validators import validate_config


def run_diagnostics(root: Path) -> tuple[DiagnosticResult, ...]:
    """Run simple checks for a repository and ContextPack setup."""

    results: list[DiagnosticResult] = []
    config = load_config(root)
    scan = scan_repository(root, config=config)

    for message in validate_config(config):
        results.append(DiagnosticResult(message.level, "config", message.message))

    if not (root / CONFIG_FILE_NAME).exists():
        results.append(DiagnosticResult("warning", "config", f"{CONFIG_FILE_NAME} is missing"))
    if not scan.files:
        results.append(DiagnosticResult("error", "scan", "No files were selected for context"))
    if scan.total_tokens > config.token_budget:
        results.append(DiagnosticResult("warning", "tokens", "Selected files exceed the configured token budget"))
    if any(item.reason == "risky secret-like filename" for item in scan.skipped):
        results.append(DiagnosticResult("warning", "safety", "Secret-like filenames were skipped"))
    if not results:
        results.append(DiagnosticResult("info", "diagnostics", "ContextPack setup looks ready"))
    return tuple(results)
