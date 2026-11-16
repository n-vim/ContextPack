"""Lightweight source outline extraction for context bundles."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .models import FileRecord, ScanResult


@dataclass(frozen=True)
class OutlineSymbol:
    """A function, class, command, or heading discovered in source files."""

    file: str
    line: int
    kind: str
    name: str


PY_PATTERNS = [
    ("class", re.compile(r"^\s*class\s+([A-Za-z_][A-Za-z0-9_]*)")),
    ("function", re.compile(r"^\s*(?:async\s+def|def)\s+([A-Za-z_][A-Za-z0-9_]*)")),
]
JS_PATTERNS = [
    ("function", re.compile(r"^\s*(?:export\s+)?function\s+([A-Za-z_$][\w$]*)")),
    ("function", re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\(")),
    ("class", re.compile(r"^\s*(?:export\s+)?class\s+([A-Za-z_$][\w$]*)")),
]
GO_PATTERNS = [("function", re.compile(r"^\s*func\s+(?:\([^)]*\)\s*)?([A-Za-z_][A-Za-z0-9_]*)"))]
RUST_PATTERNS = [
    ("function", re.compile(r"^\s*(?:pub\s+)?fn\s+([A-Za-z_][A-Za-z0-9_]*)")),
    ("struct", re.compile(r"^\s*(?:pub\s+)?struct\s+([A-Za-z_][A-Za-z0-9_]*)")),
    ("enum", re.compile(r"^\s*(?:pub\s+)?enum\s+([A-Za-z_][A-Za-z0-9_]*)")),
]
MD_PATTERN = re.compile(r"^(#{1,3})\s+(.+)$")


def _patterns_for(file: FileRecord):
    if file.extension == ".py":
        return PY_PATTERNS
    if file.extension in {".js", ".jsx", ".ts", ".tsx"}:
        return JS_PATTERNS
    if file.extension == ".go":
        return GO_PATTERNS
    if file.extension == ".rs":
        return RUST_PATTERNS
    return []


def extract_outline_for_file(file: FileRecord, limit: int = 40) -> tuple[OutlineSymbol, ...]:
    """Extract a lightweight outline from a single file."""

    symbols: list[OutlineSymbol] = []
    if file.extension in {".md", ".mdx"}:
        for line_number, line in enumerate(file.content.splitlines(), start=1):
            match = MD_PATTERN.match(line)
            if match:
                symbols.append(OutlineSymbol(file.relative_path, line_number, "heading", match.group(2).strip()))
            if len(symbols) >= limit:
                break
        return tuple(symbols)

    patterns = _patterns_for(file)
    for line_number, line in enumerate(file.content.splitlines(), start=1):
        for kind, pattern in patterns:
            match = pattern.match(line)
            if match:
                symbols.append(OutlineSymbol(file.relative_path, line_number, kind, match.group(1)))
                break
        if len(symbols) >= limit:
            break
    return tuple(symbols)


def build_outline(scan: ScanResult, per_file_limit: int = 25, total_limit: int = 300) -> tuple[OutlineSymbol, ...]:
    """Build an outline for selected context files."""

    symbols: list[OutlineSymbol] = []
    for file in scan.files:
        symbols.extend(extract_outline_for_file(file, limit=per_file_limit))
        if len(symbols) >= total_limit:
            break
    return tuple(symbols[:total_limit])


def render_outline_markdown(scan: ScanResult) -> str:
    """Render a Markdown outline for source and documentation files."""

    symbols = build_outline(scan)
    lines = [f"# Context Outline: {scan.root.name}", ""]
    if not symbols:
        lines.append("No outline symbols were detected in the selected context.")
        return "\n".join(lines).rstrip() + "\n"

    current_file = ""
    for symbol in symbols:
        if symbol.file != current_file:
            current_file = symbol.file
            lines.extend(["", f"## `{current_file}`", ""])
        lines.append(f"- Line {symbol.line}: **{symbol.kind}** `{symbol.name}`")
    return "\n".join(lines).rstrip() + "\n"
