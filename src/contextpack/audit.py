"""Context safety and quality audit helpers."""

from __future__ import annotations

from dataclasses import dataclass

from .models import BundleConfig, ScanResult
from .safety import is_risky_filename
from .tokenizer import format_tokens


@dataclass(frozen=True)
class AuditFinding:
    """A safety or quality finding for generated context."""

    level: str
    title: str
    detail: str
    suggestion: str


MASK_HINTS = ("****", "AKIA", "ghp_", "sk_live", "sk_test", "PRIVATE KEY")


def run_context_audit(scan: ScanResult, config: BundleConfig) -> tuple[AuditFinding, ...]:
    """Return audit findings for the selected context."""

    findings: list[AuditFinding] = []
    risky_files = [item for item in scan.files if is_risky_filename(item.path.name)]
    if risky_files:
        findings.append(
            AuditFinding(
                "high",
                "Risky filenames are included",
                ", ".join(item.relative_path for item in risky_files[:5]),
                "Exclude secret-like files or keep redact_secrets enabled before sharing context.",
            )
        )

    if not config.redact_secrets:
        findings.append(
            AuditFinding(
                "high",
                "Secret redaction is disabled",
                "The current config allows raw file content to be bundled without masking.",
                "Set redact_secrets: true in .contextpack.yaml.",
            )
        )

    very_large = [item for item in scan.files if item.token_estimate > 10000]
    if very_large:
        findings.append(
            AuditFinding(
                "medium",
                "Very large files are included",
                f"{len(very_large)} file(s) exceed 10k estimated tokens.",
                "Use split, compact profile, or ignore large generated files.",
            )
        )

    if scan.total_tokens > config.token_budget:
        findings.append(
            AuditFinding(
                "medium",
                "Selected context exceeds token budget",
                f"Selected: {format_tokens(scan.total_tokens)} / budget: {format_tokens(config.token_budget)}.",
                "Use --profile compact, --max-files, or the split command.",
            )
        )

    included_hidden = [item.relative_path for item in scan.files if item.relative_path.startswith(".")]
    if included_hidden and config.include_hidden_files:
        findings.append(
            AuditFinding(
                "low",
                "Hidden files are included",
                f"{len(included_hidden)} hidden file(s) are part of the context.",
                "Review hidden files before sharing the generated bundle.",
            )
        )

    if len(scan.files) == 0:
        findings.append(
            AuditFinding(
                "high",
                "No files selected",
                "The current filters did not include any files.",
                "Check include_extensions, ignore_dirs, and max_file_size_kb.",
            )
        )

    if not findings:
        findings.append(
            AuditFinding(
                "info",
                "Context selection looks safe",
                "No major sharing risks were detected from the selected context.",
                "Review generated output before sending it to any external tool.",
            )
        )
    return tuple(findings)


def render_audit_markdown(findings: tuple[AuditFinding, ...]) -> str:
    """Render audit findings as Markdown."""

    lines = ["# ContextPack Audit", "", "| Level | Finding | Detail | Suggestion |", "| --- | --- | --- | --- |"]
    for item in findings:
        lines.append(f"| `{item.level}` | {item.title} | {item.detail} | {item.suggestion} |")
    return "\n".join(lines).rstrip() + "\n"
