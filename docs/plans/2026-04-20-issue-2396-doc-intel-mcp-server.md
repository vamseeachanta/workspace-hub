# Plan for #2396: MCP server exposing doc_key lookup, wiki search, registry query

> **Status:** plan-review
> **Complexity:** T3
> **Date:** 2026-04-20
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2396
> **Review artifacts:** scripts/review/results/2026-04-20-plan-2396-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `.claude/mcp-servers/` — existing MCP server registrations; pattern to follow.
- Found: `scripts/orchestrator/hermes/` — Hermes' custom intel helpers that this replaces with a unified surface.
- Found: `scripts/data/document-index/` — registry I/O we'll wrap.
- Gap: no internal MCP server for doc-intel; each agent reimplements lookup logic.

### Standards
Not applicable.

### LLM Wiki pages consulted
- Not applicable (tooling).

### Documents consulted
- Operating model §7 (cross-machine tier rules — MCP server surfaces tier semantics in responses).
- `docs/document-intelligence/intelligence-accessibility-map.md` — inventory of intel surfaces the MCP server exposes.
- MCP spec ([Model Context Protocol](https://modelcontextprotocol.io)) — stdio transport + JSON-RPC tool calls.
- Related issue #1804 (MCP server evaluation) — this informs / is informed by that evaluation.
- Related issue #2393 (embeddings index — parallel) — backs `wiki_search`.
- Related issue #2395 (CFR ingestion — parallel) — backs `cfr_lookup`.
- Memory `feedback_codex_needs_pushed_artifact.md` + `feedback_codex_sandbox_write_blocked.md` — Codex can't read local FS; MCP tool call is the path in.
- Memory `data_format_guidelines.md` — default YAML for agent-facing structured data; MCP tool responses should follow.

### Gaps identified
- No internal MCP server.
- No path allowlist standard for read-only intelligence servers.
- No audit log standard for MCP queries.

**Distinct sources consulted: 10** — exceeds ≥3 minimum.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-20-issue-2396-doc-intel-mcp-server.md` |
| Server package | `scripts/mcp/doc_intel_server/` |
| Server entry | `scripts/mcp/doc_intel_server/server.py` |
| Tools module | `scripts/mcp/doc_intel_server/tools/` (one file per tool) |
| pyproject | `scripts/mcp/doc_intel_server/pyproject.toml` |
| Claude Code registration | `.claude/mcp-servers/doc-intel.json` |
| Gemini registration | `.gemini/mcp-servers.yaml` (or equivalent config file) |
| Hermes bridge | `scripts/orchestrator/hermes/mcp_doc_intel_client.py` |
| Query log | `logs/mcp/doc-intel/queries-YYYY-MM-DD.jsonl` |
| Tests | `tests/mcp/doc_intel_server/test_*.py` |
| Docs | `docs/document-intelligence/mcp-server.md` |
| Plan review — Claude | `scripts/review/results/2026-04-20-plan-2396-claude.md` |

---

## Deliverable

An MCP server (stdio transport, Python `mcp` SDK) exposing 5 read-only tools for doc-intel access, registered for Claude Code / Codex / Gemini / Hermes, with audit logging and a path allowlist.

---

## Pseudocode

```
class DocIntelServer(MCPServer):
    tools = [
        doc_key_lookup,   # inputs: {doc_key: str}
        wiki_search,      # inputs: {query: str, domain?: str, top_k: int=10}
        registry_query,   # inputs: {registry: enum, filter: dict}
        coverage_status,  # inputs: {discipline: str}
        cfr_lookup,       # inputs: {title: int, part?: int, section?: str}
    ]

    def on_tool_call(name, args):
        log_query(name, args, caller)  # JSONL audit log
        validate args against JSON schema
        assert no disallowed paths in response (allowlist check)
        dispatch to handler
        return YAML-formatted response (per data_format_guidelines memory)

def doc_key_lookup(doc_key):
    entry = registry.find(doc_key)
    return {doc_key, layer, paths, provenance, status, tier} or {error: "not-found"}

def wiki_search(query, domain, top_k):
    if embeddings_index_available():
        results = query_embeddings(query, top_k, layer="L3", domain_filter=domain)
    else:
        results = grep_fallback(query, top_k, domain)
    return [{doc_key, path, excerpt, similarity}]

# ... etc
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/mcp/doc_intel_server/__init__.py` | Package init |
| Create | `scripts/mcp/doc_intel_server/server.py` | MCP server entry |
| Create | `scripts/mcp/doc_intel_server/tools/doc_key_lookup.py` | Tool 1 |
| Create | `scripts/mcp/doc_intel_server/tools/wiki_search.py` | Tool 2 |
| Create | `scripts/mcp/doc_intel_server/tools/registry_query.py` | Tool 3 |
| Create | `scripts/mcp/doc_intel_server/tools/coverage_status.py` | Tool 4 |
| Create | `scripts/mcp/doc_intel_server/tools/cfr_lookup.py` | Tool 5 (stub if #2395 not yet shipped) |
| Create | `scripts/mcp/doc_intel_server/allowlist.py` | Path allowlist (deny secrets/, .env, .claude/state/) |
| Create | `scripts/mcp/doc_intel_server/pyproject.toml` | Package metadata, dep on `mcp` |
| Create | `.claude/mcp-servers/doc-intel.json` | Claude Code registration |
| Create | `.gemini/mcp-servers.yaml` or equivalent | Gemini registration |
| Create | `scripts/orchestrator/hermes/mcp_doc_intel_client.py` | Hermes bridge |
| Create | `tests/mcp/doc_intel_server/test_server.py` | Integration tests |
| Create | `tests/mcp/doc_intel_server/test_tools.py` | Per-tool tests |
| Create | `tests/mcp/doc_intel_server/test_allowlist.py` | Security tests |
| Create | `docs/document-intelligence/mcp-server.md` | Usage + tool reference |
| Update | `docs/plans/README.md` | Add this plan |

---

## TDD Test List

| Test | Verifies | Input | Expected |
|---|---|---|---|
| test_server_boots | Server starts, advertises 5 tools | stdio handshake | tools list contains 5 names |
| test_doc_key_lookup_found | Known `doc_key` returns entry | fixture registry | YAML entry with required fields |
| test_doc_key_lookup_missing | Unknown returns error, not exception | bogus key | `{error: "not-found"}`, exit 0 |
| test_wiki_search_with_index | Query returns top-K with similarity | fixture index + 1 query | 3 results ordered |
| test_wiki_search_fallback_grep | No index → falls back to grep | fixture without embeddings | grep results returned |
| test_registry_query_filter | Filter by field matches | registry + filter dict | matching rows |
| test_coverage_status_domain | Discipline → coverage metrics | fixture gap report | %covered + counts |
| test_cfr_lookup_stubs_if_no_registry | No CFR registry → "feature-not-available" | absent registry | friendly stub response |
| test_allowlist_blocks_env | Request for `.env` path refused | path=.env | error + log entry |
| test_allowlist_blocks_secrets | Request for `config/secrets/` refused | path=secrets/foo | error + log entry |
| test_query_log_written | Every tool call logged JSONL | 3 calls | 3 log lines with caller/tool/args |
| test_read_only_no_writes | Server exposes no mutation tools | static check | grep for write methods = 0 |
| test_perf_doc_key_lookup_p95 | p95 lookup < 500ms | 100 calls benchmark | p95 under threshold |

---

## Acceptance Criteria

- [ ] All tests pass
- [ ] Server boots and registers in Claude Code (`claude mcp list` shows `doc-intel`)
- [ ] Server invocable from Gemini CLI (smoke test manually)
- [ ] Server invocable from Hermes bridge (integration test)
- [ ] Audit log entries land in `logs/mcp/doc-intel/queries-YYYY-MM-DD.jsonl`
- [ ] Allowlist enforced — red-team test (request `.env`) returns error
- [ ] Documentation at `docs/document-intelligence/mcp-server.md`
- [ ] Review artifacts posted

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (self) | MINOR | See findings below |
| Codex | PENDING | **Recommended** — MCP surface affects Codex directly via FS-bridge path |
| Gemini | PENDING | Recommended — Gemini registration needs provider-specific config validation |

Revisions made inline:
- **A:** Added explicit path-allowlist module + red-team tests (orig draft had it in prose only).
- **B:** Added fallback-grep path for `wiki_search` when embeddings index not yet built — prevents hard-dep deadlock with #2393.
- **C:** Added `test_read_only_no_writes` static check — enforces design invariant at test level, not just convention.
- **D:** Added p95 perf test — matches issue-body performance budget commitment.
- **E:** CFR tool stubs gracefully if #2395 not yet shipped — removes hard dependency.

---

## Risks and Open Questions

- **Risk:** `mcp` Python SDK version drift breaks server. Mitigation: pin version in pyproject; integration test on install-hooks.
- **Risk:** Codex may not consume stdio MCP natively; HTTP bridge may be required. Mitigation: Hermes bridge included; Codex-specific adapter deferred if native support lands.
- **Risk:** Query log growth. Mitigation: daily-rotated JSONL + weekly compress step in cron.
- **Open:** Should `wiki_search` also surface L2 summaries (not just L3 pages)? Plan: L3 only initially; expand if user workflow justifies.
- **Open:** Authentication? MCP stdio is per-process trust; not adding auth. If HTTP bridge opens, bearer-token required.

---

## Complexity: T3

Multi-tool server, multi-agent registration surface, security-sensitive (path allowlist + audit log), dependency on #2393 and #2395.
