"""Small gitignore-style matching helpers."""

from __future__ import annotations

from fnmatch import fnmatch


def matches_any_pattern(path: str, patterns: tuple[str, ...]) -> bool:
    """Return true if a path matches any simple glob pattern."""

    normalized = path.replace("\\", "/")
    for pattern in patterns:
        cleaned = pattern.strip().replace("\\", "/")
        if not cleaned or cleaned.startswith("#"):
            continue
        if fnmatch(normalized, cleaned) or fnmatch(normalized.split("/")[-1], cleaned):
            return True
    return False
