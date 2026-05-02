# Plan for #2480: llm-wiki end-to-end pipeline smoke test

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-24
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2480
> **Review artifacts:** (pending — not yet submitted to cross-review)

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/data/llm-wiki/ingest-orcina.py` — primary ingest implementation for Orcina HTML → wiki markdown
- Found: `scripts/data/llm-wiki/search-wiki.py` — combined-index build + fast/deep search
- Found: `scripts/data/llm-wiki/resolve_wiki_path.py` — resolves `WIKI_DIR` from env / default (`/mnt/ace/wiki-data/llm-wiki` or similar)
- Found: `scripts/data/llm-wiki/tests/` — existing test directory (content per #2141)
- Gap: no test exercises the full ingest → index → search → (MCP) chain with a fixture raw source

### Standards
Not applicable (harness/integration test work, not engineering calculation).

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/index.md` — canonical wiki entry point (target shape)
- `knowledge/wikis/marine-engineering/wiki/` — shows scale (19K+ pages) that E2E test must not touch in CI

### Documents consulted
- `#2141` — existing fixture-backed ingest/search unit tests (complementary, narrower scope)
- `#2293` — ingest idempotency (addresses stage-1 reliability but not end-to-end)
- `#2400` — MCP server exposing `wiki_search` (future retrieval endpoint; this plan gates MCP verification behind capability flag)
- `#2402` — embeddings L2+L3 index (separate retrieval modality; future extension of smoke coverage)
- `#2390` epic roadmap — classifies moving parts; confirms no existing E2E test owner

### Gaps identified
- No single test asserts "raw input → agent-reachable result" contract
- No guard against silent regressions when #2400 and #2402 land alongside promotion waves
- No fixture-break harness that simulates corruption at each pipeline stage

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-24 via `gh issue list`):
- `#2141` — OPEN — "Add fixture-backed tests for llm-wiki ingest and search scripts"
- `#2293` — OPEN — "fix(wiki-ingest): make nightly ingest idempotent and push-status truthful"
- `#2400` — OPEN — MCP server with `wiki_search`
- `#2402` — OPEN — embeddings index L2+L3
- `#2390` — OPEN — epic roadmap

**File existence** (`ls` 2026-04-24):
- EXISTS: `scripts/data/llm-wiki/ingest-orcina.py`
- EXISTS: `scripts/data/llm-wiki/search-wiki.py`
- EXISTS: `scripts/data/llm-wiki/resolve_wiki_path.py`
- EXISTS: `scripts/data/llm-wiki/tests/`
- MISSING (this plan creates): `scripts/data/llm-wiki/tests/fixtures/e2e/`
- MISSING (this plan creates): `scripts/data/llm-wiki/tests/test_e2e_smoke.py`

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-24-issue-2480-llm-wiki-e2e-smoke-test.md |
| Fixture tree | scripts/data/llm-wiki/tests/fixtures/e2e/ |
| Test implementation | scripts/data/llm-wiki/tests/test_e2e_smoke.py |
| CI workflow update | .github/workflows/nightly-*.yml (existing nightly harness — identify during impl) |
| Developer doc | scripts/data/llm-wiki/README.md (new section) |
| Plan review — Claude | scripts/review/results/2026-04-24-plan-2480-claude.md |
| Plan review — Codex | scripts/review/results/2026-04-24-plan-2480-codex.md |
| Plan review — Gemini | scripts/review/results/2026-04-24-plan-2480-gemini.md |

---

## Deliverable

A nightly-runnable pytest smoke test under `scripts/data/llm-wiki/tests/test_e2e_smoke.py` that ingests a fixture raw source, verifies wiki-page creation, index rebuild, and `search-wiki.py` retrieval — with a capability-gated assertion for MCP `wiki_search` once #2400 lands.

---

## Pseudocode

```
fixture setup:
    tmp_wiki_dir = pytest tmp_path / "llm-wiki"
    copy fixture raw HTML (2 pages) into tmp source tree
    set WIKI_DIR env var to tmp_wiki_dir for subprocess calls

test_ingest_produces_wiki_pages():
    run ingest against fixture source
    assert tmp_wiki_dir / "<product>" / "topics" / "<fixture>.md" exists
    assert tmp_wiki_dir / "<product>" / "index.json" contains fixture topic

test_search_index_rebuilds():
    run search-wiki.py build_index(force=True)
    assert tmp_wiki_dir / "search-index.json" contains fixture entry
    assert entry has expected title_tokens derived from fixture

test_search_wiki_retrieval():
    query search-wiki.py with unique fixture keyword
    assert fixture page is in top 3 results

test_mcp_wiki_search_retrieval():  # capability-gated
    if MCP server tooling not present: skip with reason
    invoke wiki_search MCP tool against tmp wiki
    assert fixture page returned

test_ingest_break_detection():
    corrupt one stage (delete index.json between ingest and search)
    assert smoke test FAILS loudly at correct stage with diagnostic
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | scripts/data/llm-wiki/tests/fixtures/e2e/source.html | minimal fixture raw input |
| Create | scripts/data/llm-wiki/tests/fixtures/e2e/expected_topic.md | golden expected output for diff |
| Create | scripts/data/llm-wiki/tests/test_e2e_smoke.py | the E2E test module |
| Modify | scripts/data/llm-wiki/README.md | add section explaining smoke test scope and how to regenerate fixtures |
| Modify | .github/workflows/nightly-*.yml (identified during impl) | register the new test in nightly CI |
| Update | docs/plans/README.md | add index row for this plan |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_ingest_produces_wiki_pages | ingest writes expected markdown and updates product index | fixture HTML source | wiki file exists, index entry present |
| test_search_index_rebuilds | build_index writes combined search-index.json | populated product indexes | combined index contains fixture tokens |
| test_search_wiki_retrieval | search-wiki.py returns fixture for keyword query | unique keyword from fixture | fixture page in top-3 results |
| test_mcp_wiki_search_retrieval | MCP tool (once #2400 lands) returns fixture | unique keyword | fixture page returned |
| test_ingest_break_detects_missing_wiki_file | smoke fails loudly if wiki page missing | fixture + deleted wiki file | assertion error naming stage |
| test_ingest_break_detects_stale_index | smoke fails if search-index.json stale | fixture + unmutated index | assertion error naming stage |

---

## Acceptance Criteria

- [ ] All new tests pass: `uv run pytest scripts/data/llm-wiki/tests/test_e2e_smoke.py -v`
- [ ] No regression in existing suite: `uv run pytest scripts/data/llm-wiki/` passes
- [ ] Synthetic break at each stage fails the smoke with a stage-named diagnostic
- [ ] CI wiring runs nightly with visible pass/fail signal
- [ ] Developer section in `scripts/data/llm-wiki/README.md` documents the fixture-regeneration command
- [ ] MCP assertion is capability-gated (skipped cleanly when #2400 not yet merged)

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | not yet dispatched |
| Codex | PENDING | not yet dispatched — codex-cli 0.124.0 regression (#2479) currently blocks `codex exec` |
| Gemini | PENDING | not yet dispatched |

**Overall result:** PENDING — plan is surfaced for user-first review per explicit request; cross-provider adversarial review will run after user tightens scope if needed.

---

## Risks and Open Questions

- **Risk:** fixture drift if OrcaFlex source HTML schema changes upstream. Mitigation: fixture is minimal synthetic HTML, not a real Orcina sample.
- **Risk:** nightly CI target workflow not yet identified — impl must locate the canonical nightly job.
- **Risk:** MCP capability flag may require test-time introspection rather than static skip; decide approach during impl.
- **Open:** should the smoke test also assert embedding-index update (#2402)? Current proposal excludes — review during planning.

---

## Complexity: T2

New test module with fixture tree plus a CI wiring change; no cross-repo churn; narrow blast radius.
