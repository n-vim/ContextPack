from __future__ import annotations

import json

from contextpack.config import load_config
from contextpack.manifest import build_manifest, render_manifest_json
from contextpack.profiles import apply_profile, get_profile
from contextpack.scanner import scan_repository
from contextpack.splitter import split_files_into_chunks
from contextpack.indexer import language_breakdown, render_context_index
from contextpack.insights import build_insights
from contextpack.validators import validate_config


def test_profile_lookup_and_apply(sample_repo):
    profile = get_profile("compact")
    assert profile.name == "compact"
    config, prompt = apply_profile(load_config(sample_repo), "compact")
    assert prompt == "default"
    assert config.token_budget == 18000
    assert config.include_tests is False


def test_manifest_json_contains_hashes(sample_repo):
    scan = scan_repository(sample_repo)
    manifest = build_manifest(scan, output_name="CONTEXT.md")
    data = json.loads(render_manifest_json(manifest))
    assert data["project"] == "sample"
    assert data["file_count"] >= 1
    assert "sha256" in data["files"][0]


def test_split_files_into_chunks(sample_repo):
    scan = scan_repository(sample_repo)
    chunks = split_files_into_chunks(scan.files, max_tokens=20)
    assert len(chunks) >= 1
    assert chunks[0].index == 1


def test_context_index_and_breakdown(sample_repo):
    scan = scan_repository(sample_repo)
    breakdown = language_breakdown(scan)
    assert "python" in breakdown
    rendered = render_context_index(scan)
    assert "Context Index" in rendered
    assert "README.md" in rendered


def test_insights_and_validation(sample_repo):
    scan = scan_repository(sample_repo)
    insights = build_insights(scan)
    assert insights
    messages = validate_config(load_config(sample_repo))
    assert messages
