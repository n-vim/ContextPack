"""Configuration loading for ContextPack."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .constants import DEFAULT_MAX_FILE_SIZE_KB, DEFAULT_TOKEN_BUDGET
from .exceptions import ConfigError
from .models import BundleConfig

CONFIG_FILE_NAME = ".contextpack.yaml"

DEFAULT_CONFIG_TEXT = """# ContextPack configuration
max_file_size_kb: 128
token_budget: 50000
include_hidden_files: false
include_tests: true
include_docs: true
include_config: true
include_gitignored: false
redact_secrets: true
output_file: CONTEXT.md

ignore_dirs:
  - .git
  - .venv
  - node_modules
  - dist
  - build
  - __pycache__
  - .pytest_cache

ignore_files:
  - package-lock.json
  - yarn.lock
  - pnpm-lock.yaml
  - poetry.lock

include_extensions: []
exclude_extensions: []
"""


def _as_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, list):
        return tuple(str(item) for item in value)
    raise ConfigError("Expected a string or list in configuration")


def load_config(root: Path, config_path: Path | None = None) -> BundleConfig:
    """Load .contextpack.yaml from a repository if it exists."""

    path = config_path or root / CONFIG_FILE_NAME
    if not path.exists():
        return BundleConfig(
            max_file_size_kb=DEFAULT_MAX_FILE_SIZE_KB,
            token_budget=DEFAULT_TOKEN_BUDGET,
        )
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"Could not parse config file: {path}") from exc

    if not isinstance(raw, dict):
        raise ConfigError("Configuration file must contain a YAML object")

    return BundleConfig(
        max_file_size_kb=int(raw.get("max_file_size_kb", DEFAULT_MAX_FILE_SIZE_KB)),
        token_budget=int(raw.get("token_budget", DEFAULT_TOKEN_BUDGET)),
        include_hidden_files=bool(raw.get("include_hidden_files", False)),
        include_tests=bool(raw.get("include_tests", True)),
        include_docs=bool(raw.get("include_docs", True)),
        include_config=bool(raw.get("include_config", True)),
        include_gitignored=bool(raw.get("include_gitignored", False)),
        ignore_dirs=_as_tuple(raw.get("ignore_dirs", ())),
        ignore_files=_as_tuple(raw.get("ignore_files", ())),
        include_extensions=tuple(ext.lower() for ext in _as_tuple(raw.get("include_extensions", ()))),
        exclude_extensions=tuple(ext.lower() for ext in _as_tuple(raw.get("exclude_extensions", ()))),
        redact_secrets=bool(raw.get("redact_secrets", True)),
        output_file=str(raw.get("output_file", "CONTEXT.md")),
    )


def write_default_config(root: Path, force: bool = False) -> Path:
    """Write a default .contextpack.yaml file."""

    path = root / CONFIG_FILE_NAME
    if path.exists() and not force:
        raise FileExistsError(f"Config already exists: {path}")
    path.write_text(DEFAULT_CONFIG_TEXT, encoding="utf-8")
    return path
