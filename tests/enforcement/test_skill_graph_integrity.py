"""Curated-graph integrity tests (#3214 Part A): 8 stale nodes removed, empty
allowlist, edge-integrity check (allowlist pre-existing, fail new dangling)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
MOD = REPO_ROOT / "scripts" / "enforcement" / "check-skill-index-coherence.py"
spec = importlib.util.spec_from_file_location("check_skill_index_coherence", MOD)
mod = importlib.util.module_from_spec(spec)
sys.modules["check_skill_index_coherence"] = mod
spec.loader.exec_module(mod)

STALE8 = {
    "workspace-hub/agent-orchestration", "workspace-hub/compliance-check",
    "workspace-hub/sparc-workflow", "workspace-hub/workspace-cli",
    "digitalmodel/orcaflex-modeling", "digitalmodel/orcaflex-post-processing",
    "digitalmodel/aqwa-analysis", "assetutilities/pdf-utilities",
}


def test_known_stale_curated_emptied():
    assert mod.KNOWN_STALE_CURATED == set()


def test_eight_stale_nodes_gone_from_graph_and_index():
    kg = yaml.safe_load(open(mod.KNOWLEDGE_GRAPH))
    node_ids = {n["id"] for n in kg["nodes"]}
    assert STALE8.isdisjoint(node_ids)
    # no edge references any of the 8
    for e in kg.get("edges", []):
        assert e["from"] not in STALE8 and e["to"] not in STALE8
    gi_text = mod.GRAPH_INDEX.read_text()
    for sid in STALE8:
        assert sid not in gi_text


def test_coherence_a_passes_with_empty_allowlist():
    fails: list[str] = []
    mod.check_a_coherence(fails)
    assert fails == [], fails


def test_graph_integrity_passes_on_current_graph():
    # the 5 pre-existing dangling edges are allowlisted; no NEW dangling.
    fails: list[str] = []
    mod.check_d_graph_integrity(fails)
    assert fails == [], fails


def test_graph_integrity_fails_on_new_dangling(tmp_path, monkeypatch):
    g = tmp_path / "kg.yaml"
    g.write_text(yaml.safe_dump({
        "nodes": [{"id": "a/x"}, {"id": "a/y"}],
        "edges": [{"from": "a/x", "to": "a/y"},
                  {"from": "a/x", "to": "a/ghost"}],  # ghost not a node, not allowlisted
    }))
    monkeypatch.setattr(mod, "KNOWLEDGE_GRAPH", g)
    fails: list[str] = []
    mod.check_d_graph_integrity(fails)
    assert any("a/ghost" in f for f in fails)


FOUR_ADDED = {
    "engineering/marine-offshore/diffraction-analysis",
    "engineering/marine-offshore/cathodic-protection",
    "engineering/marine-offshore/risk-assessment",
    "engineering/asset-integrity/fitness-for-service",
}


def test_dangling_allowlist_emptied_3220():
    assert mod.KNOWN_DANGLING_EDGE_REFS == set()


def test_four_skills_now_nodes_3220():
    kg = yaml.safe_load(open(mod.KNOWLEDGE_GRAPH))
    node_ids = {n["id"] for n in kg["nodes"]}
    assert FOUR_ADDED <= node_ids


def test_integrity_green_with_empty_allowlist_3220():
    # the whole point of #3220: no dangling edges remain, allowlist empty.
    fails: list[str] = []
    mod.check_d_graph_integrity(fails)
    assert fails == [], fails


def test_absent_converter_edge_removed_3220():
    kg = yaml.safe_load(open(mod.KNOWLEDGE_GRAPH))
    for e in kg.get("edges", []):
        assert "eng/diffraction-spec-converter" not in (e["from"], e["to"])


def test_index_reflects_added_nodes_3220():
    # the regenerated graph-index must surface the 4 nodes + the new bucket (F2/F3).
    gi = mod.GRAPH_INDEX.read_text()
    for sid in FOUR_ADDED:
        assert sid in gi, sid
    assert "asset_integrity" in gi


def test_added_nodes_basename_in_tree_3220():
    fails: list[str] = []
    mod.check_a_coherence(fails)  # the 4 new ids must still satisfy (a)
    assert fails == [], fails


def test_graph_integrity_allowlist_suppresses(tmp_path, monkeypatch):
    g = tmp_path / "kg.yaml"
    g.write_text(yaml.safe_dump({
        "nodes": [{"id": "a/x"}],
        "edges": [{"from": "a/x", "to": "a/allowed"}],
    }))
    monkeypatch.setattr(mod, "KNOWLEDGE_GRAPH", g)
    monkeypatch.setattr(mod, "KNOWN_DANGLING_EDGE_REFS", {"a/allowed"})
    fails: list[str] = []
    mod.check_d_graph_integrity(fails)
    assert fails == []
