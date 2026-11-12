"""Project type detection."""

from __future__ import annotations

from pathlib import Path


def detect_project_type(root: Path) -> str:
    """Detect a repository's primary project type."""

    markers = {
        "python": ["pyproject.toml", "requirements.txt", "setup.py", "setup.cfg"],
        "node": ["package.json", "vite.config.js", "next.config.js", "next.config.ts"],
        "rust": ["Cargo.toml"],
        "go": ["go.mod"],
        "php": ["composer.json"],
        "java": ["pom.xml", "build.gradle", "settings.gradle"],
        "docker": ["Dockerfile", "docker-compose.yml", "compose.yaml"],
    }
    for project_type, names in markers.items():
        if any((root / name).exists() for name in names):
            return project_type
    if (root / "src").exists():
        return "source"
    if (root / "README.md").exists():
        return "documentation"
    return "general"


def detect_tools(root: Path) -> tuple[str, ...]:
    """Detect common project tools from repository files."""

    tools: list[str] = []
    checks = {
        "pytest": ["pytest.ini", "pyproject.toml"],
        "ruff": ["ruff.toml", "pyproject.toml"],
        "mypy": ["mypy.ini", "pyproject.toml"],
        "docker": ["Dockerfile", ".dockerignore"],
        "github-actions": [".github/workflows"],
        "pre-commit": [".pre-commit-config.yaml"],
        "npm": ["package.json"],
    }
    for tool, paths in checks.items():
        if any((root / item).exists() for item in paths):
            tools.append(tool)
    return tuple(sorted(tools))
