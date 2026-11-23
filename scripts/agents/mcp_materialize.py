#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Materialize first-party MCP servers into per-harness registrations (G3 #3118).

One source of truth (config/agents/mcp-servers.yaml) → the three registration forms
empirically verified in #3118 Phase 0:
  - Claude:  a `.mcp.json` stdio entry
  - Codex:   `codex mcp add <name> -- uv run --no-project <script>`
  - Gemini:  `gemini mcp add <name> uv run --no-project <script>`

So adding a provider-portable tool is a ONE-line edit to mcp-servers.yaml that lands
correctly on every harness — the "define once, materialize per harness" pattern
(mirrors scripts/agents/build-soul-runtime.sh), applied to MCP tools.

  emit:   python scripts/agents/mcp_materialize.py            # print all forms (dry-run)
  apply:  python scripts/agents/mcp_materialize.py --apply    # write .mcp.json + run codex/gemini mcp add
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = REPO_ROOT / "config" / "agents" / "mcp-servers.yaml"
MCP_JSON = REPO_ROOT / ".mcp.json"

# Common launch form for a PEP-723 first-party server script.
_LAUNCH = ["uv", "run", "--no-project"]


def load_servers(path: Path | str = DEFAULT_SOURCE) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return data.get("servers", {})


def claude_mcp_entry(name: str, server: dict) -> dict:
    """The `.mcp.json` stdio entry for a server."""
    return {"type": "stdio", "command": _LAUNCH[0], "args": _LAUNCH[1:] + [server["script"]], "env": {}}


def codex_add_cmd(name: str, server: dict) -> list[str]:
    """`codex mcp add <name> -- uv run --no-project <script>` (verified Phase-0 form)."""
    return ["codex", "mcp", "add", name, "--", *_LAUNCH, server["script"]]


def gemini_add_cmd(name: str, server: dict) -> list[str]:
    """`gemini mcp add <name> uv run --no-project <script>` (verified Phase-0 form; no `--`)."""
    return ["gemini", "mcp", "add", name, *_LAUNCH, server["script"]]


def render_mcp_json(servers: dict) -> dict:
    existing = {}
    if MCP_JSON.exists():
        existing = json.loads(MCP_JSON.read_text(encoding="utf-8"))
    existing.setdefault("mcpServers", {})
    for name, server in servers.items():
        existing["mcpServers"][name] = claude_mcp_entry(name, server)
    return existing


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Materialize MCP servers per harness.")
    ap.add_argument("--apply", action="store_true", help="write .mcp.json + run codex/gemini mcp add")
    ap.add_argument("--source", default=str(DEFAULT_SOURCE))
    args = ap.parse_args(argv)
    servers = load_servers(args.source)
    if not servers:
        print("no servers in source", file=sys.stderr)
        return 1
    for name, server in servers.items():
        print(f"# {name}: {server.get('description', '')}")
        print(f"#   claude(.mcp.json): {json.dumps(claude_mcp_entry(name, server))}")
        print(f"#   codex : {' '.join(codex_add_cmd(name, server))}")
        print(f"#   gemini: {' '.join(gemini_add_cmd(name, server))}")
        if args.apply:
            for cmd in (codex_add_cmd(name, server), gemini_add_cmd(name, server)):
                subprocess.run(cmd, check=False)
    if args.apply:
        MCP_JSON.write_text(json.dumps(render_mcp_json(servers), indent=2) + "\n", encoding="utf-8")
        print(f"# wrote {MCP_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
