from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
ROUTING_INDEX = ROOT / "docs/ROUTING_INDEX.md"
CONTENT_INDEX = ROOT / "docs/CONTENT_INDEX.md"
DOCS_README = ROOT / "docs/README.md"
REGISTRY = ROOT / "data/document-index/intelligence-accessibility-registry.yaml"
GENERATOR = ROOT / "scripts/search/build_content_index.py"

RAW_SENTINEL = "<!-- tier1-raw-inventory-banner: preserve; see docs/plans/2026-04-22-issue-2464 -->"
README_SENTINEL_START = "<!-- tier1-routing-block: begin; see docs/plans/2026-04-22-issue-2464 -->"
README_SENTINEL_END = "<!-- tier1-routing-block: end -->"
TIER1_REPOS = {"workspace-hub", "digitalmodel", "assetutilities", "aceengineer-website"}
BANNED_ROOT_FILES = {
    "-",
    "**Complexity:**",
    "**Date:**",
    "**Issue:**",
    "**Review",
    "**Source",
    "**Status:**",
    "Compatibility",
    "Comprehensive",
    "This",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _tracked_root_files() -> set[str]:
    result = subprocess.run(
        ["git", "ls-files", "--", ":!:*/*"],
        cwd=ROOT,
        text=True,
        check=True,
        capture_output=True,
    )
    return set(result.stdout.splitlines())


def _readme_tier1_block() -> str:
    text = _read(DOCS_README)
    pattern = re.compile(
        re.escape(README_SENTINEL_START)
        + r"(?P<body>.*?)"
        + re.escape(README_SENTINEL_END),
        flags=re.DOTALL,
    )
    match = pattern.search(text)
    assert match, "docs/README.md is missing the sentinel-guarded Tier-1 Routing block"
    return match.group("body")


def _registry_assets() -> list[dict[str, object]]:
    data = yaml.safe_load(_read(REGISTRY))
    assert isinstance(data, dict)
    assets = data.get("assets")
    assert isinstance(assets, list)
    return assets


def test_routing_index_exists_and_has_required_sections() -> None:
    assert ROUTING_INDEX.exists()
    text = _read(ROUTING_INDEX)

    for heading in ("## Portfolio Matrix", "## Per-Repo Routing", "## Curated vs Raw Inventory"):
        assert heading in text


def test_routing_index_mentions_all_tier1_repos_and_core_contracts() -> None:
    text = _read(ROUTING_INDEX)

    for repo in TIER1_REPOS:
        assert repo in text

    for required in (
        "docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md",
        "data/document-index/intelligence-accessibility-registry.yaml",
        "docs/reports/2026-04-22-tier-1-indexing-scorecard.md",
        "docs/CONTENT_INDEX.md",
    ):
        assert required in text


def test_routing_index_contains_issue_type_to_repo_to_path_matrix() -> None:
    text = _read(ROUTING_INDEX)
    matrix_lines = [
        line
        for line in text.splitlines()
        if line.startswith("|") and not re.match(r"^\|\s*-", line)
    ]

    assert any("Issue type" in line and "Repo" in line and "Canonical path" in line for line in matrix_lines)
    issue_rows = [line for line in matrix_lines if re.match(r"^\|\s*`?cat:|^\|\s*[A-Za-z]", line)]
    assert len(issue_rows) >= 9

    for repo in TIER1_REPOS:
        assert any(repo in line for line in issue_rows), f"routing matrix does not include {repo}"


def test_content_index_has_sentinel_banner() -> None:
    head = "\n".join(_read(CONTENT_INDEX).splitlines()[:12])

    assert RAW_SENTINEL in head
    assert "machine-generated" in head.lower()
    assert "not a curated routing index" in head.lower()
    assert "docs/ROUTING_INDEX.md" in head


def test_content_index_generator_preserves_sentinel(tmp_path: Path) -> None:
    repo = tmp_path / "sample-repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    (repo / "README.md").write_text("# Sample\n", encoding="utf-8")

    output_md = tmp_path / "CONTENT_INDEX.md"
    output_json = tmp_path / "content_index.json"
    output_md.write_text(
        "\n".join(
            [
                RAW_SENTINEL,
                "> **Raw inventory:** This file is machine-generated and not a curated routing index.",
                "",
                "# Old Content Index",
                "",
            ]
        ),
        encoding="utf-8",
    )

    subprocess.run(
        [
            sys.executable,
            str(GENERATOR),
            "--root",
            str(tmp_path),
            "--output-json",
            str(output_json),
            "--output-md",
            str(output_md),
        ],
        cwd=ROOT,
        text=True,
        check=True,
        capture_output=True,
    )

    generated_head = "\n".join(output_md.read_text(encoding="utf-8").splitlines()[:6])
    assert RAW_SENTINEL in generated_head
    assert "not a curated routing index" in generated_head.lower()


def test_root_has_no_routing_noise_exact_set() -> None:
    assert _tracked_root_files().isdisjoint(BANNED_ROOT_FILES)


def test_root_no_markdown_fragment_filenames() -> None:
    offenders = sorted(path for path in _tracked_root_files() if re.match(r"^\*{2,}", path))
    assert offenders == []


def test_readme_links_discoverability_surfaces() -> None:
    block = _readme_tier1_block()

    for required in (
        "ROUTING_INDEX.md",
        "intelligence-accessibility-registry.yaml",
        "2026-04-22-tier-1-indexing-scorecard.md",
        "docs/CONTENT_INDEX.md",
    ):
        assert required in block

    assert "raw inventory" in block.lower()
    assert "not a curated routing" in block.lower()


def test_routing_index_registered_in_accessibility_registry() -> None:
    matches = [asset for asset in _registry_assets() if asset.get("canonical_path") == "docs/ROUTING_INDEX.md"]
    assert len(matches) == 1

    asset = matches[0]
    assert asset.get("asset_type") == "map"
    assert asset.get("layer") == "L2"
    assert asset.get("freshness_cadence")
    assert asset.get("owner_issue") == 2464
    assert asset.get("discoverability") == "discoverable"
    assert asset.get("gaps") is None


def test_accessibility_gaps_flipped_for_linked_assets() -> None:
    block = _readme_tier1_block()

    linked_assets = [
        asset
        for asset in _registry_assets()
        if asset.get("human_entry_point") and str(asset["human_entry_point"]) in block
    ]
    assert linked_assets, "Tier-1 Routing block should link registered intelligence assets"

    for asset in linked_assets:
        assert asset.get("gaps") != "Not linked from docs/README.md", asset.get("asset_key")
