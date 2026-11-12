"""File filtering logic."""

from __future__ import annotations

from pathlib import Path

from .constants import DEFAULT_IGNORE_DIRS, DEFAULT_IGNORE_FILES, IMPORTANT_FILENAMES
from .models import BundleConfig
from .safety import is_risky_filename
from .utils import is_hidden_path, is_probably_binary, is_supported_text_file, relative_to_root


def should_skip_directory(relative_path: str, config: BundleConfig) -> str | None:
    """Return a skip reason for a directory, or None if it can be scanned."""

    parts = [] if relative_path in {"", "."} else relative_path.split("/")
    ignore_dirs = set(DEFAULT_IGNORE_DIRS) | set(config.ignore_dirs)
    for part in parts:
        if part in ignore_dirs:
            return f"ignored directory: {part}"
    if not config.include_hidden_files and any(part.startswith(".") for part in parts):
        allowed = {".github"}
        if not any(part in allowed for part in parts):
            return "hidden directory"
    return None


def should_include_file(path: Path, root: Path, config: BundleConfig) -> tuple[bool, str]:
    """Return whether a file should be included and the reason."""

    relative = relative_to_root(path, root)
    name = path.name
    suffix = path.suffix.lower()

    if name in set(DEFAULT_IGNORE_FILES) | set(config.ignore_files):
        return False, "ignored file"
    if is_risky_filename(name):
        return False, "risky secret-like filename"
    if not config.include_hidden_files and is_hidden_path(relative):
        if not relative.startswith(".github/") and name not in IMPORTANT_FILENAMES:
            return False, "hidden file"
    if config.exclude_extensions and suffix in config.exclude_extensions:
        return False, "excluded extension"
    if config.include_extensions and suffix not in config.include_extensions and name not in IMPORTANT_FILENAMES:
        return False, "not in include_extensions"
    if path.stat().st_size > config.max_file_size_kb * 1024:
        return False, "file too large"
    if is_probably_binary(path):
        return False, "binary file"
    if not is_supported_text_file(path) and name not in IMPORTANT_FILENAMES:
        return False, "unsupported file type"
    if not config.include_tests and any(part in {"tests", "test"} for part in relative.split("/")):
        return False, "tests disabled"
    if not config.include_docs and any(part in {"docs", "doc"} for part in relative.split("/")):
        return False, "docs disabled"
    return True, "included"


def importance_score(path: Path, relative_path: str) -> int:
    """Score a file by importance so bundle output has a sensible order."""

    name = path.name
    score = 10
    if name in IMPORTANT_FILENAMES:
        score += 100
    if relative_path.startswith("src/"):
        score += 60
    if relative_path.startswith("tests/"):
        score += 35
    if relative_path.startswith("docs/"):
        score += 25
    if name.endswith((".py", ".ts", ".js", ".go", ".rs")):
        score += 20
    if "config" in name.lower():
        score += 10
    return score


def language_from_extension(path: Path) -> str:
    """Return a Markdown fence language for a file path."""

    name = path.name
    suffix = path.suffix.lower()
    mapping = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "jsx",
        ".ts": "typescript",
        ".tsx": "tsx",
        ".go": "go",
        ".rs": "rust",
        ".java": "java",
        ".php": "php",
        ".rb": "ruby",
        ".sh": "bash",
        ".html": "html",
        ".css": "css",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".toml": "toml",
        ".md": "markdown",
        ".txt": "text",
        ".env": "dotenv",
    }
    if name == "Dockerfile":
        return "dockerfile"
    return mapping.get(suffix, "text")
