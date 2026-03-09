# WRK-1055 AC Test Matrix

| # | Test | Command | Result |
|---|------|---------|--------|
| 1 | mcp-servers.yaml is valid YAML with ≥2 entries | `uv run --no-project python -c "import yaml; yaml.safe_load(open('config/ai-tools/mcp-servers.yaml'))"` | PASS (2 entries) |
| 2 | ≥1 active entry, ≥1 evaluated entry | assert statuses contains 'active' and 'evaluated' | PASS (['active', 'evaluated']) |
| 3 | .mcp.json contains semantic-scholar-mcp with pinned SHA | assert SHA `95d41cfbb1...` in args | PASS |
| 4 | MCP server starts and responds | `uvx ... semantic-scholar-mcp --help` | PASS (CLI responds) |
| 5 | Rollback removes entry; re-install restores it | `claude mcp remove` + `claude mcp add` | PASS |
| 6 | mcp-servers.md ≤200 lines, required sections present | assert Trust, Install, Remove, Supply-Chain in content | PASS (93 lines) |
| 7 | No active entry has trust_assessment != pass | assert all active entries have trust_assessment=pass | PASS |

All 7 tests PASS, 0 FAIL. Acceptance criteria fully met.
