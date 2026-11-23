#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp", "pyyaml"]
# ///
"""MCP server exposing `doc_key_lookup` — G3 #3118 pilot (cross-harness tool seam).

Wraps the EXISTING, tested core `lookup_data()` in scripts/knowledge/doc-key-lookup.py
(one of #2400's tools) so Claude / Codex / Gemini can call it identically over MCP
instead of via bespoke per-harness shell invocation.

Anti-drift: the tool logic calls the same `lookup_data()` the CLI uses — no
reimplementation. The `core == CLI == MCP` contract is enforced by
tests/test_doc_key_lookup_mcp.py.

The tool LOGIC (`doc_key_lookup`) imports WITHOUT the `mcp` package, so it is unit-
testable offline; the `mcp` dependency is only needed to actually run the stdio server.

Run as an MCP server (stdio):
    uv run scripts/knowledge/doc_key_lookup_mcp.py
Register per harness:
    Claude  — add to .mcp.json
    Codex   — codex mcp add doc-key-lookup -- uv run .../doc_key_lookup_mcp.py
    Gemini  — gemini mcp add doc-key-lookup uv run .../doc_key_lookup_mcp.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

# Load the existing CLI module (hyphenated filename) and reuse its pure core.
_DKL_PATH = Path(__file__).resolve().parent / "doc-key-lookup.py"
_spec = importlib.util.spec_from_file_location("doc_key_lookup_core", _DKL_PATH)
_core = importlib.util.module_from_spec(_spec)
sys.modules["doc_key_lookup_core"] = _core
_spec.loader.exec_module(_core)


def doc_key_lookup(query: str, by: str = "key") -> dict[str, Any]:
    """Look up artifacts across the intelligence pyramid by doc_key / path / standard.

    Returns registry index records, standards-ledger matches, and wiki pages related
    to `query`. `by` is one of "key" | "path" | "standard". Read-only.
    """
    if by not in ("key", "path", "standard"):
        raise ValueError("by must be one of: key, path, standard")
    return _core.lookup_data(query, by)


def _build_server():
    """Construct the FastMCP server. Imported lazily so the logic above stays mcp-free."""
    from mcp.server.fastmcp import FastMCP

    server = FastMCP("doc-key-lookup")
    server.tool()(doc_key_lookup)
    return server


if __name__ == "__main__":
    _build_server().run()
