"""G3 #3118 — anti-drift contract test for the doc_key_lookup MCP pilot.

The adversarial review's key requirement: "wrap the same function" is NOT
drift-proof on its own — the MCP tool, the CLI, and the core must be proven to
agree. This test asserts:  core (lookup_data) == MCP-tool == CLI `--json`
for a deterministic (empty-result) query, so the three surfaces cannot silently
diverge.

The MCP *logic* function is importable WITHOUT the `mcp` package (the package is
only needed to actually run the stdio server), so this test stays offline/fast.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DKL_PATH = REPO_ROOT / "scripts" / "knowledge" / "doc-key-lookup.py"
MCP_PATH = REPO_ROOT / "scripts" / "knowledge" / "doc_key_lookup_mcp.py"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

dkl = _load("doc_key_lookup_cli", DKL_PATH)
mcp_mod = _load("doc_key_lookup_mcp", MCP_PATH)

lookup_data = dkl.lookup_data          # pure core extracted from run_lookup
doc_key_lookup = mcp_mod.doc_key_lookup  # MCP tool logic (no mcp pkg needed to import)

# A query guaranteed to match nothing -> deterministic empty result, no volatile index dependency.
NONE_Q = "zzz-nonexistent-doc-key-9f9f9f"


def _strip_volatile(d: dict) -> dict:
    d = dict(d)
    d.pop("timestamp", None)  # run_lookup adds a wall-clock timestamp; not part of the contract
    return d


def test_lookup_data_is_pure_and_timestamp_free():
    r = lookup_data(NONE_Q, "key")
    assert r["query"] == NONE_Q and r["lookup_type"] == "key"
    assert r["index_records"] == [] and r["standards_ledger"] == [] and r["wiki_pages"] == []
    assert "timestamp" not in r  # the pure core must be deterministic


def test_mcp_tool_equals_core():
    assert doc_key_lookup(NONE_Q, "key") == lookup_data(NONE_Q, "key")


def test_cli_json_equals_core():
    out = subprocess.run(
        [sys.executable, str(DKL_PATH), NONE_Q, "--by", "key", "--json"],
        capture_output=True, text=True,
    )
    cli = json.loads(out.stdout)
    assert _strip_volatile(cli) == lookup_data(NONE_Q, "key")
