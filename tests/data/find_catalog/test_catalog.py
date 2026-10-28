"""Synthetic acceptance cases for the private find layer."""

import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

SCRIPTS = Path(__file__).resolve().parents[3] / "scripts/data/find_catalog"
sys.path.insert(0, str(SCRIPTS))
import catalog_store as store
from catalog_sources import load_config, records


@pytest.fixture
def fixture(tmp_path):
    inputs = tmp_path / "inputs"
    inputs.mkdir()

    def save(name, value):
        path = inputs / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(value), encoding="utf-8")
        return path

    energy = save("energy.yaml", {"generated_at": "2026-01-01", "modules": {
        "ocean": {"datasets": [{"id": "waves-01", "name": "Wave climate",
            "path": "data/waves.csv", "columns": [{"name": "height", "unit": "m"}]}]}}})
    atlas = save("atlases/response/run/manifest.yaml", {"atlas_id": "response-01",
        "basename": "Semisubmersible RAO", "response": "heave",
        "axes": [{"name": "frequency", "unit": "rad/s"}],
        "provenance": {"code_version": "synthetic-v1"}})
    riser = save("riser/manifest.yaml", {"tables": {
        "riser-01": {"file": "stackup.csv", "rows": 2, "sha256": "a" * 64}}})
    standards = inputs / "standards.json"
    standards.write_text(json.dumps({"standards": [{"id": "STD-001",
        "title": "Synthetic RAO guidance", "domain": "marine"}]}))
    page = inputs / "wikis/marine/wiki/concepts/motions.md"
    page.parent.mkdir(parents=True)
    page.write_text("---\ntitle: Semisubmersible motions\n---\nRAO heave response at depth.")
    manifest = inputs / "store/owner/MANIFEST.tsv"
    manifest.parent.mkdir(parents=True)
    manifest.write_text("# synthetic manifest\npath\tbytes\tsha256\tblob\n"
                        "data/rao.csv\t12\t" + "b" * 64 + "\tblobs/rao.csv\n")
    sources = [
        ("energy", "energy_catalog", energy, "energy", "public"),
        ("model", "atlas_manifests", atlas.parents[2], "marine", "internal"),
        ("riser", "riser_manifest", riser, "riser", "internal"),
        ("standards", "standards_registry", standards, "standards", "internal"),
        ("wiki", "wiki_pages", inputs / "wikis", "wiki", "restricted"),
        ("store", "ace_manifest", manifest.parent.parent, "marine", "restricted"),
    ]
    config = tmp_path / "config.yaml"
    config.write_text(yaml.safe_dump({"version": 1, "database": str(tmp_path / "private/catalog.db"),
        "sources": [{"id": sid, "kind": kind, "path": str(path), "domain": domain,
                     "exposure": exposure, "revision": "synthetic-v1"}
                    for sid, kind, path, domain, exposure in sources]}))
    return config


def test_all_adapters_preserve_identity_units_and_provenance(fixture):
    config = load_config(fixture)
    rows = list(records(config))
    assert len(rows) == 6
    assert {r["source"] for r in rows} == {s["id"] for s in config["sources"]}
    energy = next(r for r in rows if r["source"] == "energy")
    assert energy["id"] == "waves-01"
    assert "m" in json.dumps(energy["units"])
    assert all(r["provenance"]["observed_sha256"] for r in rows)
    assert all(r["readiness"] == "unverified" for r in rows)
    archive = next(r for r in rows if r["source"] == "store")
    assert archive["digest"] == "sha256:" + "b" * 64
    assert archive["locator"] == "owner/data/rao.csv"


def test_fts_filters_and_rebuild_remove_stale_entries(fixture):
    config = load_config(fixture)
    counts = store.build(config)
    assert counts == {s["id"]: 1 for s in config["sources"]}
    db = config["database"]
    hits = store.find(db, "RAO")
    assert len(hits) == 4
    assert len(store.find(db, "RAO", domain="marine")) == 4
    assert store.find(db, "RAO", domain="energy") == []
    assert [r["id"] for r in store.find(db, "RAO", source="standards")] == ["STD-001"]
    assert len(store.find(db, "RAO", exposure="restricted")) == 2
    assert store.find(db, "RAO", exposure="public") == []
    assert store.find(db, '" OR *') == []
    assert store.find(db, "") == []
    assert store.find(db, "RAO", limit=0) == []
    page = next(Path(config["sources"][4]["path"]).rglob("*.md"))
    page.write_text("No matching terms remain")
    store.build(config)
    assert store.find(db, "RAO", source="wiki") == []
    assert len(store.find(db, "RAO")) == 3
    with sqlite3.connect(db) as conn:
        assert conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"


def test_failed_import_leaves_previous_database_unchanged(fixture):
    config = load_config(fixture)
    store.build(config)
    before = Path(config["database"]).read_bytes()
    Path(config["sources"][3]["path"]).write_text("{bad JSON")
    with pytest.raises((ValueError, store.CatalogError)):
        store.build(config)
    assert Path(config["database"]).read_bytes() == before


def test_output_in_any_git_tree_or_symlink_rejected(fixture, tmp_path):
    config = load_config(fixture)
    repo = tmp_path / "public"
    repo.mkdir()
    (repo / ".git").write_text("gitdir: elsewhere")
    link = tmp_path / "alias"
    link.symlink_to(repo, target_is_directory=True)
    for parent in (repo, link):
        config["database"] = parent / "generated/catalog.db"
        with pytest.raises(store.CatalogError, match="outside"):
            store.build(config)
        assert not (parent / "generated").exists()


def test_readonly_search_never_creates_database(tmp_path):
    path = tmp_path / "missing.db"
    with pytest.raises(store.CatalogError):
        store.find(path, "RAO")
    assert not path.exists()


def test_config_rejects_missing_sources_unknown_exposure_and_digest_mismatch(fixture):
    raw = yaml.safe_load(fixture.read_text())
    raw["sources"][0]["exposure"] = "unknown"
    fixture.write_text(yaml.safe_dump(raw))
    with pytest.raises(ValueError, match="exposure"):
        load_config(fixture)
    raw["sources"][0]["exposure"] = "public"
    raw["sources"][0]["sha256"] = "0" * 64
    fixture.write_text(yaml.safe_dump(raw))
    with pytest.raises(ValueError, match="digest"):
        list(records(load_config(fixture)))


def test_cli_worked_lookup_and_private_permissions(fixture):
    env = {k: v for k, v in os.environ.items()
           if k not in {"GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"}}
    command = [sys.executable, str(SCRIPTS / "cli.py"), "--config", str(fixture)]
    for args in (["inventory"], ["build"], ["find", "RAO", "--source", "model"]):
        result = subprocess.run(command + args, env=env, text=True, capture_output=True, check=False)
        assert result.returncode == 0, result.stderr
        payload = json.loads(result.stdout)
    assert payload[0]["id"] == "response-01"
    assert payload[0]["locator"] == "response/run/manifest.yaml"
    db = load_config(fixture)["database"]
    if os.name == "posix":
        assert Path(db).stat().st_mode & 0o777 == 0o600


def test_pages_symlink_cannot_import_content_outside_root(fixture):
    config = load_config(fixture)
    source = config["sources"][4]
    page = next(Path(source["path"]).rglob("*.md"))
    outside = page.parents[4] / "outside.md"
    outside.write_text("secret outside root")
    page.unlink()
    page.symlink_to(outside)
    with pytest.raises(ValueError, match="symlink|outside"):
        list(records(config))


def test_duplicate_source_ids_and_empty_source_sets_rejected(fixture):
    raw = yaml.safe_load(fixture.read_text())
    raw["sources"].append(raw["sources"][0])
    fixture.write_text(yaml.safe_dump(raw))
    with pytest.raises(ValueError, match="duplicate"):
        load_config(fixture)
    raw["sources"] = []
    fixture.write_text(yaml.safe_dump(raw))
    with pytest.raises(ValueError, match="sources"):
        load_config(fixture)


def test_page_search_survives_stale_graph_gate_and_bad_frontmatter(fixture):
    config = load_config(fixture)
    root = Path(config["sources"][4]["path"])
    (root / "query_sources.json").write_text(json.dumps({"gated_commands": {
        "pages search": {"reason": "requires a graph artifact"}}}))
    page = next(root.rglob("*.md"))
    page.write_text("---\ntitle: broken: header\n---\nRAO synthetic page body")
    store.build(config)
    hits = store.find(config["database"], "RAO", source="wiki")
    assert len(hits) == 1
    assert hits[0]["warnings"] == ["invalid page frontmatter; metadata unverified"]
    assert hits[0]["readiness"] == "unverified"


def test_git_directory_marker_rejected_before_creating_output(fixture, tmp_path):
    config = load_config(fixture)
    repo = tmp_path / "checkout"
    metadata = repo / ".git"
    metadata.mkdir(parents=True)
    (metadata / "HEAD").write_text("ref: refs/heads/synthetic\n")
    config["database"] = repo / "output/catalog.db"
    with pytest.raises(store.CatalogError):
        store.build(config)
    assert not (repo / "output").exists()
    assert (metadata / "HEAD").read_text() == "ref: refs/heads/synthetic\n"


def test_archive_traversal_is_not_an_owner_relative_locator(fixture):
    config = load_config(fixture)
    manifest = next(Path(config["sources"][5]["path"]).rglob("MANIFEST.tsv"))
    manifest.write_text("path\tsha256\n../escape.csv\t" + "c" * 64 + "\n")
    with pytest.raises(ValueError, match="relative"):
        list(records(config))
