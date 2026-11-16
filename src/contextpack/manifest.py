"""Manifest generation for ContextPack outputs."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .bundler import summarize_scan
from .models import BundleManifest, ScanResult


def _content_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def build_manifest(scan: ScanResult, output_name: str = "CONTEXT.md") -> BundleManifest:
    """Build a machine-readable manifest for a scan result."""

    summary = summarize_scan(scan)
    files = tuple(
        {
            "path": item.relative_path,
            "language": item.language,
            "size_bytes": item.size_bytes,
            "tokens": item.token_estimate,
            "sha256": _content_hash(item.content),
            "reason": item.reason,
        }
        for item in scan.files
    )
    skipped = tuple({"path": item.relative_path, "reason": item.reason} for item in scan.skipped)
    return BundleManifest(
        project=summary.name,
        project_type=summary.project_type,
        generated_at=datetime.now(timezone.utc).isoformat(),
        output_file=output_name,
        file_count=len(scan.files),
        skipped_count=len(scan.skipped),
        total_tokens=scan.total_tokens,
        total_bytes=scan.total_bytes,
        detected_tools=summary.detected_tools,
        files=files,
        skipped=skipped,
    )


def manifest_to_dict(manifest: BundleManifest) -> dict[str, object]:
    """Convert manifest dataclass to a JSON-friendly dictionary."""

    return {
        "project": manifest.project,
        "project_type": manifest.project_type,
        "generated_at": manifest.generated_at,
        "output_file": manifest.output_file,
        "file_count": manifest.file_count,
        "skipped_count": manifest.skipped_count,
        "total_tokens": manifest.total_tokens,
        "total_bytes": manifest.total_bytes,
        "detected_tools": list(manifest.detected_tools),
        "files": list(manifest.files),
        "skipped": list(manifest.skipped),
    }


def render_manifest_json(manifest: BundleManifest) -> str:
    """Render manifest as JSON."""

    return json.dumps(manifest_to_dict(manifest), indent=2, sort_keys=True) + "\n"


def render_manifest_markdown(manifest: BundleManifest) -> str:
    """Render manifest as Markdown."""

    lines = [
        f"# ContextPack Manifest: {manifest.project}",
        "",
        "## Summary",
        "",
        f"- Project type: `{manifest.project_type}`",
        f"- Generated at: `{manifest.generated_at}`",
        f"- Output file: `{manifest.output_file}`",
        f"- Files included: `{manifest.file_count}`",
        f"- Files skipped: `{manifest.skipped_count}`",
        f"- Estimated tokens: `{manifest.total_tokens}`",
        f"- Total bytes: `{manifest.total_bytes}`",
        "",
        "## Included Files",
        "",
    ]
    for item in manifest.files:
        lines.append(f"- `{item['path']}` - {item['tokens']} tokens - `{item['sha256'][:12]}`")
    if manifest.skipped:
        lines.extend(["", "## Skipped Files", ""])
        for item in manifest.skipped[:50]:
            lines.append(f"- `{item['path']}` - {item['reason']}")
    return "\n".join(lines).rstrip() + "\n"


def write_manifest(path: Path, content: str, force: bool = False) -> Path:
    """Write a manifest file safely."""

    if path.exists() and not force:
        raise FileExistsError(f"Manifest already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path
