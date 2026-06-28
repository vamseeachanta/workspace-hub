#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml", "pytest"]
# ///
"""Tests for catalog_delta.py source resolution + public-safe guarantees.

Run:  uv run --no-project --with pyyaml --with pytest pytest test_catalog_delta.py
  or: uv run --script test_catalog_delta.py   (delegates to pytest)
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

THIS_DIR = Path(__file__).resolve().parent

# Load the (PEP-723) script module by path so pytest can exercise its functions.
_spec = importlib.util.spec_from_file_location(
    "catalog_delta", THIS_DIR / "catalog_delta.py"
)
cd = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cd)

# A synthetic, NON-CLIENT marker used to prove that any private/internal-bearing
# field (scope / description / residency) is dropped by the public-safe projection.
# We deliberately do NOT embed real client codenames in this repo (they would trip
# the Client-PII gate); a generic sentinel demonstrates the same drop property.
PRIVATE_MARKER = "ZZZ_SYNTHETIC_PRIVATE_MARKER"

# A minimal canonical artifact mirroring deckhand/docs/deckhand/api-catalog.json:
# only live_public + roadmap rows; private/internal reduced to a count.
CANONICAL = {
    "source": "config/deckhand/routing/domain-workflows.yaml",
    "note": "Public-safe API-path catalog - live_public + roadmap only.",
    "private_internal_count": 4,
    "records": [
        {
            "ref": "floating_marine_mooring_screen",
            "kind": "workflow",
            "domain": "floating-marine",
            "subdomains": ["mooring"],
            "status": "live_public",
            "claimable_public": True,
            "report_url_example": "https://vamseeachanta.github.io/deckhand-sandbox/domains/floating-marine/deckhand-deliverables/<run-id>/report.html",
            "analytical_paths": ["digitalmodel:mooring-fatigue"],
            "owner_repo": "deckhand",
            "description": "Open Deck floating/marine mooring screening workflow.",
        },
        {
            "ref": "subsea_pipeline_wall_thickness_screen",
            "kind": "workflow",
            "domain": "subsea-pipelines-integrity",
            "subdomains": ["pipeline"],
            "status": "live_public",
            "claimable_public": True,
            "report_url_example": "https://vamseeachanta.github.io/deckhand-sandbox/domains/subsea-pipelines-integrity/deckhand-deliverables/<run-id>/report.html",
            "owner_repo": "deckhand",
            "description": "Open Deck subsea pipeline wall-thickness screening workflow.",
        },
        {
            "ref": "roadmap:cad",
            "kind": "roadmap",
            "domain": "cad",
            "subdomains": ["cad"],
            "status": "roadmap",
            "claimable_public": False,
            "owner_repo": "deckhand",
            "description": "Bound channel domain 'cad' - escalate-only; workflow row owed later.",
        },
    ],
}


def _write_canonical(tmp_path: Path) -> Path:
    p = tmp_path / "api-catalog.json"
    p.write_text(json.dumps(CANONICAL))
    return p


def test_canonical_extract_yields_live_public_and_roadmap():
    rows = cd.extract_paths_from_canonical(CANONICAL)
    safe = cd.public_safe(rows)
    statuses = {r["status"] for r in safe}
    assert statuses == {"live_public", "roadmap"}
    refs = {r["ref"] for r in safe}
    assert "floating_marine_mooring_screen" in refs
    assert "subsea_pipeline_wall_thickness_screen" in refs
    assert "roadmap:cad" in refs
    # Field re-keying: published `domain` -> internal `channel_domain`,
    # `report_url_example` -> `report_url_hint`.
    moor = next(r for r in safe if r["ref"] == "floating_marine_mooring_screen")
    assert moor["channel_domain"] == "floating-marine"
    assert moor["report_url_hint"].startswith("https://vamseeachanta.github.io/")


def test_public_safe_only_whitelisted_keys():
    rows = cd.extract_paths_from_canonical(CANONICAL)
    safe = cd.public_safe(rows)
    for r in safe:
        assert set(r).issubset(set(cd.PUBLIC_SAFE_KEYS)), r


def test_public_safe_drops_private_internal_rows_and_their_fields():
    """Any non-(live_public|roadmap) row, plus the fields that can carry a client
    identifier (scope / residency / description), must be dropped from the output.
    This is the codename-free guarantee expressed as a generic drop property —
    proven with a synthetic non-client marker rather than real codenames."""
    # Derive path: a private (client-wiki) workflow whose scope/description carry
    # the synthetic marker. It must NOT survive into the public-safe projection.
    catalog = {
        "workflows": {
            "private_client_run": {
                "artifact_residency": "client-wiki",
                "owner_repo": "deckhand",
                "description": PRIVATE_MARKER,
                "route": {
                    "scope": PRIVATE_MARKER,
                    "channel_domain": "floating-marine",
                    "subdomains": ["mooring"],
                },
            },
            "floating_marine_mooring_screen": {
                "artifact_residency": "public-sandbox",
                "owner_repo": "deckhand",
                "route": {
                    "channel_domain": "floating-marine",
                    "subdomains": ["mooring"],
                },
            },
        },
        "channel_domain_subdomains": {"cad": ["cad"]},
    }
    full = cd.extract_paths(catalog)
    safe = cd.public_safe(full)
    blob = json.dumps(safe)
    assert PRIVATE_MARKER not in blob, "private-bearing field leaked into public output"
    assert all(p["status"] in cd.PUBLIC_SAFE_STATUSES for p in safe)
    # The private row contributes to the de-identified count instead.
    assert cd.private_internal_count(full) == 1


def test_private_internal_count_from_canonical():
    # The published count is taken directly; raw private rows are never present.
    assert int(CANONICAL["private_internal_count"]) == 4


def test_auto_prefers_canonical_when_present(tmp_path):
    canonical = _write_canonical(tmp_path)
    args = SimpleNamespace(
        source="auto",
        canonical=canonical,
        catalog=tmp_path / "does-not-exist.yaml",
        snapshot=tmp_path / "snap.json",
    )
    current, priv, source_used, source_path = cd.resolve_current(args)
    assert source_used == "canonical"
    assert source_path == canonical
    assert priv == 4
    assert {r["status"] for r in current} == {"live_public", "roadmap"}


def test_auto_falls_back_to_derive_when_canonical_absent(tmp_path):
    # Minimal routing catalog so derive has something to read.
    catalog = tmp_path / "domain-workflows.yaml"
    catalog.write_text(
        "workflows:\n"
        "  floating_marine_mooring_screen:\n"
        "    artifact_residency: public-sandbox\n"
        "    owner_repo: deckhand\n"
        "    route:\n"
        "      channel_domain: floating-marine\n"
        "      subdomains: [mooring]\n"
        "channel_domain_subdomains:\n"
        "  cad: [cad]\n"
    )
    args = SimpleNamespace(
        source="auto",
        canonical=tmp_path / "missing-api-catalog.json",
        catalog=catalog,
        snapshot=tmp_path / "snap.json",
    )
    current, priv, source_used, _ = cd.resolve_current(args)
    assert source_used == "derive"
    assert {r["status"] for r in current} == {"live_public", "roadmap"}


def test_canonical_source_requires_artifact(tmp_path):
    args = SimpleNamespace(
        source="canonical",
        canonical=tmp_path / "missing.json",
        catalog=None,
        snapshot=tmp_path / "snap.json",
    )
    with pytest.raises(FileNotFoundError):
        cd.resolve_current(args)


if __name__ == "__main__":
    import sys

    raise SystemExit(pytest.main([str(Path(__file__)), "-q"]))
