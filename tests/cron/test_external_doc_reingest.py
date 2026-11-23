"""Tests for scripts/cron/external-doc-reingest.sh — TDD per #2318 plan."""

import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "cron" / "external-doc-reingest.sh"


def _mk_registry(path: Path, generated: str, vendors: list[dict]):
    lines = [f"generated: '{generated}'", f"total_entries: {len(vendors)}", "entries:"]
    for v in vendors:
        lines.append(f"  - name: {v['name']}")
        lines.append(f"    url: {v['url']}")
        lines.append(f"    type: {v.get('type', 'tool')}")
        lines.append(f"    domain: {v.get('domain', 'general')}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def _mk_manifest(path: Path, rows: dict[str, str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["ingests:"]
    for name, ts in rows.items():
        lines.append(f"  - name: {name}")
        lines.append(f"    last_ingested: '{ts}'")
    path.write_text("\n".join(lines) + "\n")


def _baseline(quarter: str, vendors: list[str]) -> str:
    lines = [
        f"# external-doc-reingest — {quarter}",
        "",
        "**Status:** GREEN — seed baseline.",
        "",
        "## Per-vendor change log",
        "",
        "| Vendor | Source URL | Last modified | Δ since last ingest | Re-ingested |",
        "|--------|-----------|---------------|---------------------|-------------|",
    ]
    for v in vendors:
        lines.append(f"| {v} | https://example.com/{v} | 2026-01-15 | n/a | initial ingest |")
    lines.append("")
    return "\n".join(lines)


def _run(tmp_path: Path, registry_vendors: list[dict], baseline: str | None = None,
         manifest: dict | None = None):
    out_dir = tmp_path / "out"
    registry = tmp_path / "data" / "online-resource-registry.yaml"
    _mk_registry(registry, "2026-04-17T00:00:00", registry_vendors)

    if baseline is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "external-doc-reingest-2026-Q1.md").write_text(baseline)

    env = os.environ.copy()
    env["EXTDOC_OUT_DIR"] = str(out_dir)
    env["EXTDOC_QUARTER"] = "2026-Q2"
    env["EXTDOC_PREV_QUARTER"] = "2026-Q1"
    env["EXTDOC_REGISTRY"] = str(registry)
    env["REPO_ROOT"] = str(tmp_path)
    if manifest is not None:
        manifest_path = tmp_path / "ingest-manifest.yaml"
        _mk_manifest(manifest_path, manifest)
        env["EXTDOC_MANIFEST"] = str(manifest_path)

    r = subprocess.run(["bash", str(SCRIPT)],
                       env=env, capture_output=True, text=True, timeout=15)
    return r, out_dir / "external-doc-reingest-2026-Q2.md"


def test_reingest_green_when_no_manifest(tmp_path):
    """No dm#503 manifest → placeholder mode, GREEN, reports vendor inventory."""
    r, report = _run(tmp_path, [{"name": "orcina", "url": "https://orcina.com/help"}])
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    assert "Status:** GREEN" in body
    assert "placeholder" in body.lower() or "no ingest manifest" in body.lower()
    assert "orcina" in body


def test_reingest_counts_registry_entries(tmp_path):
    vendors = [
        {"name": "orcina", "url": "https://orcina.com", "domain": "orcaflex"},
        {"name": "openfoam", "url": "https://openfoam.org", "domain": "cfd"},
        {"name": "dnv", "url": "https://dnv.com", "domain": "naval_architecture"},
    ]
    r, report = _run(tmp_path, vendors)
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    for v in ("orcina", "openfoam", "dnv"):
        assert v in body


def test_reingest_yellow_on_change(tmp_path):
    """With a manifest + a vendor whose last-ingested timestamp is stale, flag YELLOW."""
    vendors = [{"name": "orcina", "url": "https://orcina.com"}]
    # Manifest says orcina was ingested long ago — registry 'generated' is newer
    # so the script sees orcina as "changed since last ingest".
    manifest = {"orcina": "2025-01-01T00:00:00"}
    r, report = _run(tmp_path, vendors, manifest=manifest)
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    assert "Status:** YELLOW" in body
    assert "orcina" in body


def test_reingest_handles_vendor_without_url(tmp_path):
    """Registry entry without url → row flagged."""
    vendors = [{"name": "ghost_vendor", "url": ""}]
    r, report = _run(tmp_path, vendors)
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    assert "ghost_vendor" in body


def test_reingest_handles_missing_registry(tmp_path):
    out_dir = tmp_path / "out"
    env = os.environ.copy()
    env["EXTDOC_OUT_DIR"] = str(out_dir)
    env["EXTDOC_QUARTER"] = "2026-Q2"
    env["EXTDOC_REGISTRY"] = str(tmp_path / "does_not_exist.yaml")
    env["REPO_ROOT"] = str(tmp_path)
    r = subprocess.run(["bash", str(SCRIPT)],
                       env=env, capture_output=True, text=True, timeout=15)
    assert r.returncode == 0, r.stderr
    body = (out_dir / "external-doc-reingest-2026-Q2.md").read_text()
    assert "registry not found" in body.lower() or "no registry" in body.lower()


def test_reingest_lists_consumer_impact(tmp_path):
    """Orcina vendor in registry → consumer-impact section mentions dm#503."""
    vendors = [{"name": "orcina", "url": "https://orcina.com", "domain": "orcaflex"}]
    r, report = _run(tmp_path, vendors)
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    assert "dm#503" in body or "digitalmodel#503" in body
