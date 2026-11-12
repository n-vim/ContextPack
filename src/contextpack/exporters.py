"""Export helpers."""

from __future__ import annotations

from pathlib import Path

from .exceptions import OutputError


def write_output(path: Path, content: str, force: bool = False) -> Path:
    """Write content to an output path safely."""

    if path.exists() and not force:
        raise OutputError(f"Output already exists: {path}. Use --force to overwrite.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path
