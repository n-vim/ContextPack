"""Token budget analysis for selected repository context."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from .models import FileRecord, ScanResult
from .tokenizer import format_tokens


@dataclass(frozen=True)
class BudgetGroup:
    """Token usage grouped by a repository area."""

    name: str
    files: int
    tokens: int
    bytes: int


@dataclass(frozen=True)
class BudgetReport:
    """Token budget report for a repository scan."""

    budget: int
    total_tokens: int
    total_files: int
    groups: tuple[BudgetGroup, ...]
    heavy_files: tuple[FileRecord, ...]
    recommendations: tuple[str, ...]

    @property
    def over_budget(self) -> bool:
        """Return true if selected context exceeds the configured budget."""

        return self.total_tokens > self.budget

    @property
    def remaining_tokens(self) -> int:
        """Return remaining budget, never below zero."""

        return max(0, self.budget - self.total_tokens)


def _top_level_area(path: str) -> str:
    parts = path.split("/")
    if len(parts) == 1:
        return "root"
    return parts[0]


def build_budget_report(scan: ScanResult, budget: int | None = None) -> BudgetReport:
    """Build a report showing how selected files consume the token budget."""

    selected_budget = budget or 50000
    grouped: dict[str, dict[str, int]] = defaultdict(lambda: {"files": 0, "tokens": 0, "bytes": 0})
    for file in scan.files:
        area = _top_level_area(file.relative_path)
        grouped[area]["files"] += 1
        grouped[area]["tokens"] += file.token_estimate
        grouped[area]["bytes"] += file.size_bytes

    groups = tuple(
        BudgetGroup(name=name, files=data["files"], tokens=data["tokens"], bytes=data["bytes"])
        for name, data in sorted(grouped.items(), key=lambda item: (-item[1]["tokens"], item[0]))
    )
    heavy_files = tuple(sorted(scan.files, key=lambda item: item.token_estimate, reverse=True)[:10])

    recommendations: list[str] = []
    if scan.total_tokens > selected_budget:
        recommendations.append("Use the compact profile or lower --max-files before sending context to an AI tool.")
        recommendations.append("Split the context into chunks with the split command.")
    if heavy_files and heavy_files[0].token_estimate > selected_budget * 0.25:
        recommendations.append(f"Review `{heavy_files[0].relative_path}` because it uses a large share of the token budget.")
    if len(scan.files) > 80:
        recommendations.append("Use a focused profile or include_extensions to keep the bundle smaller.")
    if not recommendations:
        recommendations.append("The selected context is within budget and looks manageable.")

    return BudgetReport(
        budget=selected_budget,
        total_tokens=scan.total_tokens,
        total_files=len(scan.files),
        groups=groups,
        heavy_files=heavy_files,
        recommendations=tuple(recommendations),
    )


def render_budget_markdown(report: BudgetReport) -> str:
    """Render a Markdown budget report."""

    lines = [
        "# ContextPack Token Budget",
        "",
        f"- Budget: `{format_tokens(report.budget)}`",
        f"- Selected tokens: `{format_tokens(report.total_tokens)}`",
        f"- Remaining tokens: `{format_tokens(report.remaining_tokens)}`",
        f"- Files selected: `{report.total_files}`",
        f"- Status: `{'over budget' if report.over_budget else 'within budget'}`",
        "",
        "## Token Usage by Area",
        "",
        "| Area | Files | Tokens | Bytes |",
        "| --- | ---: | ---: | ---: |",
    ]
    for group in report.groups:
        lines.append(f"| `{group.name}` | {group.files} | {group.tokens} | {group.bytes} |")

    lines.extend(["", "## Heaviest Files", "", "| File | Tokens | Bytes |", "| --- | ---: | ---: |"])
    for file in report.heavy_files:
        lines.append(f"| `{file.relative_path}` | {file.token_estimate} | {file.size_bytes} |")

    lines.extend(["", "## Recommendations", ""])
    for item in report.recommendations:
        lines.append(f"- {item}")
    return "\n".join(lines).rstrip() + "\n"
