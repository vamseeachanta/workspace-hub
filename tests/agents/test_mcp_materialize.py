"""G3 #3118 Phase 2 — single-source MCP registration materializer.

One source-of-truth entry (config/agents/mcp-servers.yaml) → the three per-harness
registration forms that were empirically verified in Phase 0:
  - Claude:  a `.mcp.json` stdio entry
  - Codex:   `codex mcp add <name> -- uv run --no-project <script>`
  - Gemini:  `gemini mcp add <name> uv run --no-project <script>`

This is the "materialize per harness" seam (mirrors scripts/agents/build-soul-runtime.sh).
Pure functions, tested offline.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "agents" / "mcp_materialize.py"
spec = importlib.util.spec_from_file_location("mcp_materialize", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules["mcp_materialize"] = mod
spec.loader.exec_module(mod)

SERVER = {"script": "scripts/knowledge/doc_key_lookup_mcp.py", "description": "doc key lookup"}
NAME = "doc-key-lookup"


def test_claude_entry_matches_mcp_json_shape():
    e = mod.claude_mcp_entry(NAME, SERVER)
    assert e == {
        "type": "stdio",
        "command": "uv",
        "args": ["run", "--no-project", "scripts/knowledge/doc_key_lookup_mcp.py"],
        "env": {},
    }


def test_codex_add_cmd_uses_double_dash():
    # verified Phase-0 form: codex mcp add <name> -- uv run --no-project <script>
    assert mod.codex_add_cmd(NAME, SERVER) == [
        "codex", "mcp", "add", NAME, "--",
        "uv", "run", "--no-project", "scripts/knowledge/doc_key_lookup_mcp.py",
    ]


def test_gemini_add_cmd_has_no_double_dash():
    # verified Phase-0 form: gemini mcp add <name> uv run --no-project <script>
    assert mod.gemini_add_cmd(NAME, SERVER) == [
        "gemini", "mcp", "add", NAME,
        "uv", "run", "--no-project", "scripts/knowledge/doc_key_lookup_mcp.py",
    ]


def test_source_config_loads_and_lists_pilot():
    servers = mod.load_servers()
    assert "doc-key-lookup" in servers
    assert servers["doc-key-lookup"]["script"].endswith("doc_key_lookup_mcp.py")
