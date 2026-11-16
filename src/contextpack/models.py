"""Data models used by ContextPack."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class BundleConfig:
    """Runtime configuration for scanning and bundling a repository."""

    max_file_size_kb: int = 128
    token_budget: int = 50000
    include_hidden_files: bool = False
    include_tests: bool = True
    include_docs: bool = True
    include_config: bool = True
    include_gitignored: bool = False
    ignore_dirs: tuple[str, ...] = ()
    ignore_files: tuple[str, ...] = ()
    include_extensions: tuple[str, ...] = ()
    exclude_extensions: tuple[str, ...] = ()
    redact_secrets: bool = True
    output_file: str = "CONTEXT.md"


@dataclass(frozen=True)
class FileRecord:
    """A scanned file that can be included in a context bundle."""

    path: Path
    relative_path: str
    size_bytes: int
    extension: str
    language: str
    content: str
    token_estimate: int
    importance: int = 0
    reason: str = "included"


@dataclass(frozen=True)
class SkippedFile:
    """A file skipped during scanning."""

    relative_path: str
    reason: str


@dataclass(frozen=True)
class ScanResult:
    """Result of scanning a repository."""

    root: Path
    project_type: str
    files: tuple[FileRecord, ...]
    skipped: tuple[SkippedFile, ...]
    total_bytes: int
    total_tokens: int


@dataclass(frozen=True)
class BundleResult:
    """Rendered context bundle."""

    root: Path
    project_name: str
    project_type: str
    output: str
    files: tuple[FileRecord, ...]
    skipped: tuple[SkippedFile, ...]
    total_tokens: int
    total_bytes: int


@dataclass(frozen=True)
class ProjectSummary:
    """Small generated summary for a project."""

    name: str
    project_type: str
    file_count: int
    token_estimate: int
    notable_files: tuple[str, ...] = field(default_factory=tuple)
    detected_tools: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class BundleProfile:
    """A named set of bundle settings."""

    name: str
    description: str
    token_budget: int
    max_file_size_kb: int
    include_tests: bool
    include_docs: bool
    include_config: bool
    prompt_style: str = "default"


@dataclass(frozen=True)
class BundleChunk:
    """A token-limited group of files."""

    index: int
    files: tuple[FileRecord, ...]
    token_estimate: int


@dataclass(frozen=True)
class BundleManifest:
    """Machine-readable metadata for generated context."""

    project: str
    project_type: str
    generated_at: str
    output_file: str
    file_count: int
    skipped_count: int
    total_tokens: int
    total_bytes: int
    detected_tools: tuple[str, ...]
    files: tuple[dict[str, Any], ...]
    skipped: tuple[dict[str, str], ...]


@dataclass(frozen=True)
class RepoInsight:
    """A practical insight about the selected context."""

    title: str
    severity: str
    detail: str
    suggestion: str


@dataclass(frozen=True)
class ValidationMessage:
    """Config validation message."""

    level: str
    message: str


@dataclass(frozen=True)
class DiagnosticResult:
    """Diagnostic result displayed by the doctor command."""

    level: str
    area: str
    message: str


JsonDict = dict[str, Any]
