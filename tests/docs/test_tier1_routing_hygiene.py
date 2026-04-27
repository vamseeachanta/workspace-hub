from __future__ import annotations

import re
import subprocess
from importlib import util as importlib_util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

ROUTING_INDEX = REPO_ROOT / "docs" / "ROUTING_INDEX.md"
CONTENT_INDEX = REPO_ROOT / "docs" / "CONTENT_INDEX.md"
README = REPO_ROOT / "docs" / "README.md"
REGISTRY = REPO_ROOT / "data" / "document-index" / "intelligence-accessibility-registry.yaml"
GENERATOR = REPO_ROOT / "scripts" / "search" / "build_content_index.py"

SENTINEL = "<!-- tier1-raw-inventory-banner: preserve; see docs/plans/2026-04-22-issue-2464 -->"

ROUTING_BLOCK_OPEN = "<!-- tier1-routing-block:open; see docs/plans/2026-04-22-issue-2464 -->"
ROUTING_BLOCK_CLOSE = "<!-- tier1-routing-block:close; see docs/plans/2026-04-22-issue-2464 -->"

TIER1_REPOS = ["workspace-hub", "digitalmodel", "assetutilities", "aceengineer-website"]

BANNED_ROOT_NOISE = [
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
]

REQUIRED_ROUTING_INDEX_SECTIONS = [
    "Portfolio matrix",
    "Per-repo routing",
    "Curated vs raw inventory",
]


def _git_root_files() -> set[str]:
    out = subprocess.check_output(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        text=True,
    )
    return {line for line in out.splitlines() if "/" not in line}


def test_routing_index_exists_and_has_required_sections() -> None:
    assert ROUTING_INDEX.exists(), f"missing curated routing index at {ROUTING_INDEX}"
    body = ROUTING_INDEX.read_text(encoding="utf-8")
    for heading in REQUIRED_ROUTING_INDEX_SECTIONS:
        assert heading in body, f"required heading not found in routing index: {heading!r}"


def test_content_index_has_sentinel_banner() -> None:
    assert CONTENT_INDEX.exists(), f"missing CONTENT_INDEX at {CONTENT_INDEX}"
    text = CONTENT_INDEX.read_text(encoding="utf-8")
    assert SENTINEL in text, "sentinel comment missing from CONTENT_INDEX.md"
    lines = text.splitlines()
    sentinel_idx = next(i for i, ln in enumerate(lines) if SENTINEL in ln)
    window = "\n".join(lines[sentinel_idx + 1 : sentinel_idx + 1 + 12])
    assert "> **⚠ Raw inventory" in window, (
        "callout `> **⚠ Raw inventory` not found within 12 lines after sentinel"
    )
    assert "machine-generated" in window.lower(), "callout must declare 'machine-generated'"
    assert "not a curated routing index" in window.lower(), (
        "callout must state 'not a curated routing index'"
    )
    assert "docs/ROUTING_INDEX.md" in window or "ROUTING_INDEX.md" in window, (
        "callout must name docs/ROUTING_INDEX.md as the curated alternative"
    )


def test_content_index_generator_preserves_sentinel(tmp_path: Path) -> None:
    spec = importlib_util.spec_from_file_location("build_content_index", GENERATOR)
    assert spec is not None and spec.loader is not None
    module = importlib_util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert hasattr(module, "write_markdown"), (
        "build_content_index.py must expose write_markdown(output_path, index_data) "
        "for sentinel preservation tests"
    )

    target = tmp_path / "CONTENT_INDEX.md"
    banner = (
        SENTINEL
        + "\n\n"
        + "> **⚠ Raw inventory.** This file is machine-generated and is **not a curated routing index**. "
        "See [`docs/ROUTING_INDEX.md`](ROUTING_INDEX.md).\n\n"
    )
    target.write_text(banner + "# Content Index\n\nGenerated on stub\n\nstale body line\n", encoding="utf-8")

    fake_index_data = {
        "/tmp/fake-repo": {
            "disciplines": [],
            "project_files": ["pyproject.toml"],
            "key_docs": ["docs/README.md"],
        }
    }
    module.write_markdown(target, fake_index_data)

    rebuilt = target.read_text(encoding="utf-8")
    assert SENTINEL in rebuilt, "sentinel not preserved across generator round-trip"
    assert "> **⚠ Raw inventory" in rebuilt, "callout not preserved across generator round-trip"
    assert rebuilt.startswith(banner.split("\n", 1)[0]), (
        "preserved leading region must remain at the very top of the regenerated file"
    )


def test_root_has_no_routing_noise_exact_set() -> None:
    tracked_root = _git_root_files()
    leftover = sorted(set(BANNED_ROOT_NOISE) & tracked_root)
    assert not leftover, f"banned root-noise filenames still tracked: {leftover}"


def test_root_no_markdown_fragment_filenames() -> None:
    pattern = re.compile(r"^\*{2,}")
    offenders = sorted(p for p in _git_root_files() if pattern.match(p))
    assert not offenders, f"tracked root-level filenames matching markdown-fragment pattern: {offenders}"


def test_readme_links_discoverability_surfaces() -> None:
    body = README.read_text(encoding="utf-8")
    assert ROUTING_BLOCK_OPEN in body and ROUTING_BLOCK_CLOSE in body, (
        "docs/README.md must contain the sentinel-guarded Tier-1 Routing block"
    )
    open_idx = body.index(ROUTING_BLOCK_OPEN)
    close_idx = body.index(ROUTING_BLOCK_CLOSE)
    assert close_idx > open_idx
    block = body[open_idx:close_idx]
    assert "ROUTING_INDEX.md" in block, "Tier-1 Routing block must link ROUTING_INDEX.md"
    assert "intelligence-accessibility-registry.yaml" in block, (
        "Tier-1 Routing block must link intelligence-accessibility-registry.yaml"
    )
    assert "2026-04-22-tier-1-indexing-scorecard.md" in block, (
        "Tier-1 Routing block must link the tier-1 indexing scorecard"
    )


def test_routing_index_mentions_all_tier1_repos() -> None:
    body = ROUTING_INDEX.read_text(encoding="utf-8")
    missing = [name for name in TIER1_REPOS if name not in body]
    assert not missing, f"routing index missing tier-1 repos: {missing}"


def _parse_registry_assets() -> list[dict]:
    """Light yaml-free parser scoped to this registry's flat schema. Avoids adding a runtime dep."""
    text = REGISTRY.read_text(encoding="utf-8")
    assets: list[dict] = []
    current: dict | None = None
    in_assets_list = False
    for raw_line in text.splitlines():
        stripped = raw_line.rstrip()
        if stripped.startswith("assets:"):
            in_assets_list = True
            continue
        if not in_assets_list:
            continue
        if stripped.startswith("  - asset_key:"):
            if current is not None:
                assets.append(current)
            current = {"asset_key": stripped.split(":", 1)[1].strip()}
            continue
        if current is None:
            continue
        m = re.match(r"^    ([a-zA-Z_][\w-]*):\s*(.*)$", stripped)
        if m:
            key, value = m.group(1), m.group(2).strip()
            current[key] = value
    if current is not None:
        assets.append(current)
    return assets


def test_routing_index_registered_in_accessibility_registry() -> None:
    assets = _parse_registry_assets()
    matches = [
        a for a in assets if a.get("canonical_path", "").strip().strip("'\"") == "docs/ROUTING_INDEX.md"
    ]
    assert matches, "intelligence-accessibility-registry.yaml has no entry for docs/ROUTING_INDEX.md"
    entry = matches[0]
    assert entry.get("asset_type", "").strip() == "map", (
        f"asset_type for ROUTING_INDEX must be 'map'; got {entry.get('asset_type')!r}"
    )
    discoverability = entry.get("discoverability", "").strip()
    assert discoverability == "discoverable", (
        f"discoverability for ROUTING_INDEX must be 'discoverable'; got {discoverability!r}"
    )
    cadence = entry.get("freshness_cadence", "").strip()
    assert cadence and cadence.lower() != "null", (
        f"freshness_cadence for ROUTING_INDEX must be non-null; got {cadence!r}"
    )
    owner = entry.get("owner_issue", "").strip().strip("'\"")
    assert owner.lstrip("#") == "2464", (
        f"owner_issue for ROUTING_INDEX must reference #2464; got {owner!r}"
    )


def test_accessibility_gaps_flipped_for_linked_assets() -> None:
    body = README.read_text(encoding="utf-8")
    assert ROUTING_BLOCK_OPEN in body and ROUTING_BLOCK_CLOSE in body
    block = body[body.index(ROUTING_BLOCK_OPEN) : body.index(ROUTING_BLOCK_CLOSE)]
    assets = _parse_registry_assets()
    bad_gap = '"Not linked from docs/README.md"'
    violations: list[str] = []
    for asset in assets:
        entry = asset.get("human_entry_point", "").strip().strip("'\"")
        if not entry:
            continue
        if entry in block:
            gap_value = asset.get("gaps", "").strip()
            if gap_value == bad_gap:
                violations.append(asset.get("asset_key", "<unknown>"))
    assert not violations, (
        "registry assets newly linked from docs/README.md still claim "
        "'Not linked from docs/README.md': " + ", ".join(violations)
    )
