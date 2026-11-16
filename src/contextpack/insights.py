"""Repository insight generation."""

from __future__ import annotations

from .models import RepoInsight, ScanResult


def build_insights(scan: ScanResult) -> tuple[RepoInsight, ...]:
    """Generate practical insights from a scan."""

    insights: list[RepoInsight] = []
    names = {item.relative_path for item in scan.files}
    skipped_reasons = [item.reason for item in scan.skipped]

    if scan.total_tokens > 80000:
        insights.append(
            RepoInsight(
                title="Large context bundle",
                severity="medium",
                detail="The selected context is large and may be difficult to paste into one AI chat.",
                suggestion="Use the compact profile or split command before sharing the context.",
            )
        )
    if "README.md" not in names and "readme.md" not in names:
        insights.append(
            RepoInsight(
                title="README not included",
                severity="medium",
                detail="No README file was selected for the context bundle.",
                suggestion="Add a README or adjust filters so the AI receives project overview information.",
            )
        )
    if not any(path.startswith("tests/") for path in names) and scan.project_type in {"python", "node", "go", "rust"}:
        insights.append(
            RepoInsight(
                title="Tests not included",
                severity="low",
                detail="The bundle does not include test files.",
                suggestion="Include tests when asking for bug fixes or refactoring suggestions.",
            )
        )
    if any("risky secret-like filename" in reason for reason in skipped_reasons):
        insights.append(
            RepoInsight(
                title="Secret-like files skipped",
                severity="high",
                detail="Some files were skipped because their names look sensitive.",
                suggestion="Keep those files out of AI prompts and commit history unless they are safe examples.",
            )
        )
    if len(scan.files) == 0:
        insights.append(
            RepoInsight(
                title="No files selected",
                severity="high",
                detail="ContextPack did not select any files from this repository.",
                suggestion="Check ignore rules, max file size, and include extension settings.",
            )
        )
    if not insights:
        insights.append(
            RepoInsight(
                title="Context looks ready",
                severity="info",
                detail="The selected files look suitable for an AI-ready repository bundle.",
                suggestion="Generate CONTEXT.md or export a Markdown report.",
            )
        )
    return tuple(insights)


def render_insights_markdown(scan: ScanResult) -> str:
    """Render insights as Markdown."""

    lines = [f"# ContextPack Insights: {scan.root.name}", ""]
    for insight in build_insights(scan):
        lines.append(f"## {insight.title}")
        lines.append("")
        lines.append(f"- Severity: `{insight.severity}`")
        lines.append(f"- Detail: {insight.detail}")
        lines.append(f"- Suggestion: {insight.suggestion}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
