"""Context index generation."""

from __future__ import annotations

from collections import Counter, defaultdict

from .models import ScanResult
from .tokenizer import format_tokens


def language_breakdown(scan: ScanResult) -> dict[str, int]:
    """Count included files by language."""

    counter = Counter(item.language or "text" for item in scan.files)
    return dict(sorted(counter.items(), key=lambda item: (-item[1], item[0])))


def directory_breakdown(scan: ScanResult) -> dict[str, int]:
    """Count included files by top-level directory."""

    counter: Counter[str] = Counter()
    for item in scan.files:
        top = item.relative_path.split("/", 1)[0]
        counter[top] += 1
    return dict(sorted(counter.items(), key=lambda item: (-item[1], item[0])))


def render_context_index(scan: ScanResult) -> str:
    """Render a readable index of the selected repository context."""

    by_dir: dict[str, list[str]] = defaultdict(list)
    for item in scan.files:
        top = item.relative_path.split("/", 1)[0]
        by_dir[top].append(item.relative_path)

    lines = [
        f"# Context Index: {scan.root.name}",
        "",
        "## Overview",
        "",
        f"- Project type: `{scan.project_type}`",
        f"- Included files: `{len(scan.files)}`",
        f"- Skipped files: `{len(scan.skipped)}`",
        f"- Estimated tokens: `{format_tokens(scan.total_tokens)}`",
        "",
        "## Language Breakdown",
        "",
    ]
    for language, count in language_breakdown(scan).items():
        lines.append(f"- `{language}`: {count}")

    lines.extend(["", "## Directory Breakdown", ""])
    for directory, count in directory_breakdown(scan).items():
        lines.append(f"- `{directory}`: {count}")

    lines.extend(["", "## Files by Directory", ""])
    for directory in sorted(by_dir):
        lines.append(f"### `{directory}`")
        lines.append("")
        for path in sorted(by_dir[directory]):
            lines.append(f"- `{path}`")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
