"""Command-line interface for ContextPack."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import __version__
from .audit import render_audit_markdown, run_context_audit
from .budget import build_budget_report, render_budget_markdown
from .bundler import build_bundle, summarize_scan
from .config import load_config, write_default_config
from .detector import detect_project_type, detect_tools
from .diagnostics import run_diagnostics
from .exporters import write_output
from .html import render_html_report
from .indexer import render_context_index
from .insights import build_insights, render_insights_markdown
from .manifest import build_manifest, render_manifest_json, render_manifest_markdown
from .outline import render_outline_markdown
from .packager import create_artifact_folder, create_artifact_zip
from .profiles import apply_profile, available_profiles, get_profile
from .reports import render_json_report, render_markdown_report, render_text_summary
from .scanner import scan_repository
from .splitter import render_chunk_markdown, render_chunks_index, split_files_into_chunks
from .tokenizer import format_tokens
from .tree import build_tree
from .utils import ensure_repository
from .workspace import init_workspace

app = typer.Typer(
    name="contextpack",
    help="Create clean AI-ready context bundles from repositories.",
    no_args_is_help=True,
)
console = Console()


def version_callback(value: bool) -> None:
    if value:
        console.print(f"ContextPack {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        help="Show ContextPack version.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """ContextPack command group."""


@app.command()
def build(
    path: Path = typer.Argument(Path("."), help="Repository path to bundle."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output Markdown file."),
    prompt: Optional[str] = typer.Option(None, "--prompt", help="Prompt style: default, review, bugfix, docs, or security."),
    profile: Optional[str] = typer.Option(None, "--profile", help="Bundle profile: balanced, compact, deep, bugfix, docs, security."),
    max_files: Optional[int] = typer.Option(None, "--max-files", help="Limit included files."),
    manifest: bool = typer.Option(False, "--manifest", help="Also write a JSON manifest."),
    index: bool = typer.Option(False, "--index", help="Also write a Markdown context index."),
    force: bool = typer.Option(False, "--force", help="Overwrite output if it already exists."),
    print_output: bool = typer.Option(False, "--print", help="Print bundle instead of writing it."),
) -> None:
    """Build an AI-ready Markdown context bundle."""

    root = ensure_repository(path)
    config, profile_prompt = apply_profile(load_config(root), profile)
    selected_prompt = prompt or profile_prompt
    bundle = build_bundle(root, config=config, prompt_style=selected_prompt, max_files=max_files)
    if print_output:
        console.print(bundle.output)
        return
    output_path = output or root / config.output_file
    write_output(output_path, bundle.output, force=force)

    scan = scan_repository(root, config=config)
    extra_lines: list[str] = []
    if manifest:
        manifest_path = output_path.with_suffix(".manifest.json")
        manifest_content = render_manifest_json(build_manifest(scan, output_path.name))
        write_output(manifest_path, manifest_content, force=force)
        extra_lines.append(f"Manifest: {manifest_path}")
    if index:
        index_path = output_path.with_name("context-index.md")
        write_output(index_path, render_context_index(scan), force=force)
        extra_lines.append(f"Index: {index_path}")

    extras = "\n" + "\n".join(extra_lines) if extra_lines else ""
    console.print(
        Panel.fit(
            f"Created [bold]{output_path}[/bold]\n"
            f"Files: {len(bundle.files)} | Tokens: {format_tokens(bundle.total_tokens)}{extras}",
            title="ContextPack",
            border_style="green",
        )
    )


@app.command("tree")
def tree_command(
    path: Path = typer.Argument(Path("."), help="Repository path."),
    depth: int = typer.Option(4, "--depth", help="Maximum tree depth."),
    profile: Optional[str] = typer.Option(None, "--profile", help="Apply a bundle profile."),
) -> None:
    """Show the filtered repository tree that ContextPack would use."""

    root = ensure_repository(path)
    config, _ = apply_profile(load_config(root), profile)
    console.print(build_tree(root, config=config, max_depth=depth))


@app.command()
def summarize(
    path: Path = typer.Argument(Path("."), help="Repository path."),
    profile: Optional[str] = typer.Option(None, "--profile", help="Apply a bundle profile."),
) -> None:
    """Show a repository context summary."""

    root = ensure_repository(path)
    config, _ = apply_profile(load_config(root), profile)
    scan = scan_repository(root, config=config)
    summary = summarize_scan(scan)
    table = Table(title="ContextPack Summary")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")
    table.add_row("Project", summary.name)
    table.add_row("Type", summary.project_type)
    table.add_row("Files included", str(summary.file_count))
    table.add_row("Files skipped", str(len(scan.skipped)))
    table.add_row("Estimated tokens", format_tokens(summary.token_estimate))
    table.add_row("Tools", ", ".join(summary.detected_tools) or "none detected")
    console.print(table)


@app.command()
def tokens(
    path: Path = typer.Argument(Path("."), help="Repository path."),
    profile: Optional[str] = typer.Option(None, "--profile", help="Apply a bundle profile."),
) -> None:
    """Estimate how many tokens the selected repository context will use."""

    root = ensure_repository(path)
    config, _ = apply_profile(load_config(root), profile)
    scan = scan_repository(root, config=config)
    console.print(f"Estimated tokens: [bold]{format_tokens(scan.total_tokens)}[/bold]")
    console.print(f"Included files: [bold]{len(scan.files)}[/bold]")


@app.command()
def export(
    path: Path = typer.Argument(Path("."), help="Repository path."),
    format: str = typer.Option("markdown", "--format", "-f", help="Output format: markdown, json, text, html, or insights."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path."),
    profile: Optional[str] = typer.Option(None, "--profile", help="Apply a bundle profile."),
    force: bool = typer.Option(False, "--force", help="Overwrite output if it exists."),
) -> None:
    """Export a repository context report."""

    root = ensure_repository(path)
    config, _ = apply_profile(load_config(root), profile)
    scan = scan_repository(root, config=config)
    selected = format.lower()
    if selected == "json":
        content = render_json_report(scan)
        default_name = "context-report.json"
    elif selected == "text":
        content = render_text_summary(scan)
        default_name = "context-summary.txt"
    elif selected == "html":
        content = render_html_report(scan)
        default_name = "context-report.html"
    elif selected == "insights":
        content = render_insights_markdown(scan)
        default_name = "context-insights.md"
    else:
        content = render_markdown_report(scan)
        default_name = "context-report.md"
    if output is None:
        output = root / default_name
    write_output(output, content, force=force)
    console.print(f"Created [bold green]{output}[/bold green]")


@app.command()
def manifest(
    path: Path = typer.Argument(Path("."), help="Repository path."),
    format: str = typer.Option("json", "--format", "-f", help="Output format: json or markdown."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path."),
    profile: Optional[str] = typer.Option(None, "--profile", help="Apply a bundle profile."),
    force: bool = typer.Option(False, "--force", help="Overwrite output if it exists."),
) -> None:
    """Generate a context manifest with file hashes and metadata."""

    root = ensure_repository(path)
    config, _ = apply_profile(load_config(root), profile)
    scan = scan_repository(root, config=config)
    data = build_manifest(scan)
    if format.lower() == "markdown":
        content = render_manifest_markdown(data)
        default = "context-manifest.md"
    else:
        content = render_manifest_json(data)
        default = "context-manifest.json"
    output_path = output or root / default
    write_output(output_path, content, force=force)
    console.print(f"Created [bold green]{output_path}[/bold green]")


@app.command()
def split(
    path: Path = typer.Argument(Path("."), help="Repository path."),
    output_dir: Path = typer.Option(Path("context-chunks"), "--output-dir", "-o", help="Directory for chunk files."),
    max_tokens: int = typer.Option(12000, "--max-tokens", help="Maximum tokens per chunk."),
    profile: Optional[str] = typer.Option(None, "--profile", help="Apply a bundle profile."),
    force: bool = typer.Option(False, "--force", help="Overwrite existing chunk files."),
) -> None:
    """Split repository context into multiple AI-friendly chunk files."""

    root = ensure_repository(path)
    config, _ = apply_profile(load_config(root), profile)
    scan = scan_repository(root, config=config)
    chunks = split_files_into_chunks(scan.files, max_tokens=max_tokens)
    target = output_dir if output_dir.is_absolute() else root / output_dir
    target.mkdir(parents=True, exist_ok=True)
    write_output(target / "README.md", render_chunks_index(chunks, root.name), force=force)
    for chunk in chunks:
        name = f"context-chunk-{chunk.index:02d}.md"
        write_output(target / name, render_chunk_markdown(chunk, root.name), force=force)
    console.print(f"Created [bold green]{len(chunks)} chunks[/bold green] in {target}")


@app.command()
def profiles() -> None:
    """List built-in bundle profiles."""

    table = Table(title="ContextPack Profiles")
    table.add_column("Name", style="cyan")
    table.add_column("Tokens", justify="right")
    table.add_column("Prompt")
    table.add_column("Description")
    for profile in available_profiles():
        table.add_row(profile.name, str(profile.token_budget), profile.prompt_style, profile.description)
    console.print(table)


@app.command("profile")
def profile_info(name: str = typer.Argument(..., help="Profile name.")) -> None:
    """Show details about one profile."""

    profile = get_profile(name)
    table = Table(title=f"Profile: {profile.name}")
    table.add_column("Field", style="cyan")
    table.add_column("Value")
    for key, value in profile.__dict__.items():
        table.add_row(key, str(value))
    console.print(table)


@app.command()
def insights(
    path: Path = typer.Argument(Path("."), help="Repository path."),
    profile: Optional[str] = typer.Option(None, "--profile", help="Apply a bundle profile."),
) -> None:
    """Show practical insights about the selected context."""

    root = ensure_repository(path)
    config, _ = apply_profile(load_config(root), profile)
    scan = scan_repository(root, config=config)
    table = Table(title="ContextPack Insights")
    table.add_column("Severity", style="cyan")
    table.add_column("Title")
    table.add_column("Suggestion")
    for item in build_insights(scan):
        table.add_row(item.severity, item.title, item.suggestion)
    console.print(table)


@app.command()
def index(
    path: Path = typer.Argument(Path("."), help="Repository path."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output Markdown file."),
    profile: Optional[str] = typer.Option(None, "--profile", help="Apply a bundle profile."),
    force: bool = typer.Option(False, "--force", help="Overwrite output if it exists."),
) -> None:
    """Generate a file and language index for selected context."""

    root = ensure_repository(path)
    config, _ = apply_profile(load_config(root), profile)
    scan = scan_repository(root, config=config)
    output_path = output or root / "context-index.md"
    write_output(output_path, render_context_index(scan), force=force)
    console.print(f"Created [bold green]{output_path}[/bold green]")


@app.command()
def doctor(path: Path = typer.Argument(Path("."), help="Repository path.")) -> None:
    """Check ContextPack configuration and scan readiness."""

    root = ensure_repository(path)
    table = Table(title="ContextPack Doctor")
    table.add_column("Level", style="cyan")
    table.add_column("Area")
    table.add_column("Message")
    for item in run_diagnostics(root):
        table.add_row(item.level, item.area, item.message)
    console.print(table)


@app.command()
def workspace(
    path: Path = typer.Argument(Path("."), help="Repository path."),
    force: bool = typer.Option(False, "--force", help="Overwrite existing workspace files."),
) -> None:
    """Create a .contextpack workspace with prompts and profile examples."""

    root = ensure_repository(path)
    created = init_workspace(root, force=force)
    table = Table(title="Created Workspace Files")
    table.add_column("Path", style="green")
    for item in created:
        table.add_row(item.relative_to(root).as_posix())
    console.print(table)


@app.command()
def budget(
    path: Path = typer.Argument(Path("."), help="Repository path."),
    token_budget: Optional[int] = typer.Option(None, "--token-budget", help="Override token budget."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write Markdown budget report."),
    profile: Optional[str] = typer.Option(None, "--profile", help="Apply a bundle profile."),
    force: bool = typer.Option(False, "--force", help="Overwrite output if it exists."),
) -> None:
    """Analyze token usage by folder and highlight heavy files."""

    root = ensure_repository(path)
    config, _ = apply_profile(load_config(root), profile)
    scan = scan_repository(root, config=config)
    report = build_budget_report(scan, budget=token_budget or config.token_budget)

    table = Table(title="ContextPack Token Budget")
    table.add_column("Area", style="cyan")
    table.add_column("Files", justify="right")
    table.add_column("Tokens", justify="right")
    table.add_column("Bytes", justify="right")
    for group in report.groups[:12]:
        table.add_row(group.name, str(group.files), str(group.tokens), str(group.bytes))
    console.print(table)
    status = "over budget" if report.over_budget else "within budget"
    console.print(Panel.fit(f"Selected: {format_tokens(report.total_tokens)}\nBudget: {format_tokens(report.budget)}\nStatus: {status}", title="Budget Status"))

    if output:
        write_output(output, render_budget_markdown(report), force=force)
        console.print(f"Created [bold green]{output}[/bold green]")


@app.command()
def outline(
    path: Path = typer.Argument(Path("."), help="Repository path."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write Markdown outline."),
    profile: Optional[str] = typer.Option(None, "--profile", help="Apply a bundle profile."),
    force: bool = typer.Option(False, "--force", help="Overwrite output if it exists."),
) -> None:
    """Generate a lightweight source and documentation outline."""

    root = ensure_repository(path)
    config, _ = apply_profile(load_config(root), profile)
    scan = scan_repository(root, config=config)
    content = render_outline_markdown(scan)
    if output:
        write_output(output, content, force=force)
        console.print(f"Created [bold green]{output}[/bold green]")
    else:
        console.print(content)


@app.command()
def audit(
    path: Path = typer.Argument(Path("."), help="Repository path."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write Markdown audit report."),
    profile: Optional[str] = typer.Option(None, "--profile", help="Apply a bundle profile."),
    force: bool = typer.Option(False, "--force", help="Overwrite output if it exists."),
) -> None:
    """Audit selected context for sharing risks and quality issues."""

    root = ensure_repository(path)
    config, _ = apply_profile(load_config(root), profile)
    scan = scan_repository(root, config=config)
    findings = run_context_audit(scan, config)
    table = Table(title="ContextPack Audit")
    table.add_column("Level", style="cyan")
    table.add_column("Finding")
    table.add_column("Suggestion")
    for item in findings:
        table.add_row(item.level, item.title, item.suggestion)
    console.print(table)
    if output:
        write_output(output, render_audit_markdown(findings), force=force)
        console.print(f"Created [bold green]{output}[/bold green]")


@app.command()
def pack(
    path: Path = typer.Argument(Path("."), help="Repository path."),
    output_dir: Path = typer.Option(Path("contextpack-artifacts"), "--output-dir", "-o", help="Artifact folder."),
    zip_output: Optional[Path] = typer.Option(None, "--zip", help="Optional zip output path."),
    prompt: str = typer.Option("default", "--prompt", help="Prompt style."),
    profile: Optional[str] = typer.Option(None, "--profile", help="Apply a bundle profile."),
    force: bool = typer.Option(False, "--force", help="Overwrite existing files."),
) -> None:
    """Create a complete context artifact folder, optionally zipped."""

    root = ensure_repository(path)
    config, profile_prompt = apply_profile(load_config(root), profile)
    selected_prompt = prompt or profile_prompt
    target = output_dir if output_dir.is_absolute() else root / output_dir
    created = create_artifact_folder(root, target, config=config, prompt_style=selected_prompt, force=force)
    zip_path = None
    if zip_output:
        zip_path = create_artifact_zip(target, zip_output if zip_output.is_absolute() else root / zip_output, force=force)

    table = Table(title="ContextPack Artifacts")
    table.add_column("File", style="green")
    for item in created:
        table.add_row(item.relative_to(root).as_posix() if item.is_relative_to(root) else item.as_posix())
    if zip_path:
        table.add_row(zip_path.relative_to(root).as_posix() if zip_path.is_relative_to(root) else zip_path.as_posix())
    console.print(table)


@app.command()
def detect(path: Path = typer.Argument(Path("."), help="Repository path.")) -> None:
    """Detect project type and common tools."""

    root = ensure_repository(path)
    project_type = detect_project_type(root)
    tools = detect_tools(root)
    console.print(Panel.fit(f"Type: [bold]{project_type}[/bold]\nTools: {', '.join(tools) or 'none'}", title="Detection"))


@app.command()
def inspect(
    path: Path = typer.Argument(Path("."), help="Repository path."),
    limit: int = typer.Option(20, "--limit", help="Maximum files to show."),
    profile: Optional[str] = typer.Option(None, "--profile", help="Apply a bundle profile."),
) -> None:
    """Inspect which files are included in the context selection."""

    root = ensure_repository(path)
    config, _ = apply_profile(load_config(root), profile)
    scan = scan_repository(root, config=config)
    table = Table(title="Included Files")
    table.add_column("Path", style="cyan")
    table.add_column("Language")
    table.add_column("Tokens", justify="right")
    table.add_column("Size", justify="right")
    for item in scan.files[:limit]:
        table.add_row(item.relative_path, item.language, str(item.token_estimate), str(item.size_bytes))
    console.print(table)
    if len(scan.files) > limit:
        console.print(f"Showing {limit} of {len(scan.files)} files")


@app.command()
def init(
    path: Path = typer.Argument(Path("."), help="Repository path."),
    force: bool = typer.Option(False, "--force", help="Overwrite existing config."),
) -> None:
    """Create a default .contextpack.yaml config file."""

    root = ensure_repository(path)
    config_path = write_default_config(root, force=force)
    console.print(f"Created [bold green]{config_path}[/bold green]")


@app.command()
def config(path: Path = typer.Argument(Path("."), help="Repository path.")) -> None:
    """Show loaded ContextPack configuration."""

    root = ensure_repository(path)
    loaded = load_config(root)
    table = Table(title="ContextPack Config")
    table.add_column("Key", style="cyan")
    table.add_column("Value")
    for key, value in loaded.__dict__.items():
        table.add_row(key, repr(value))
    console.print(table)


if __name__ == "__main__":
    app()
