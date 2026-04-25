# Plan for #2103: Extend llm-wiki ingestion to AQWA and BEMRosetta documentation

> **Status:** draft (v4 — addresses r3 Claude P2s; Gemini r3 APPROVED v3)
> **Complexity:** T2
> **Date:** 2026-04-24
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2103
> **Base commit:** `12b4be834954505ca1e7fc8ad8b20bda34e92baf` (HEAD at v3 plan-drafting time; cite line numbers relative to this SHA)
> **Review artifacts (r1, r2):** see v2/v3 plan history — closed in v3.
> **Review artifacts (r3):**
> - Claude — `scripts/review/results/20260425T031815Z-plan-2103-v3.md-plan-claude.md` (MAJOR — 3 P2s + 6 P3s)
> - Gemini — `scripts/review/results/20260425T032034Z-plan-2103-v3.md-plan-gemini.md` (APPROVE — 1 suggestion + 1 question)
> **Review artifacts (r4, pending):** `scripts/review/results/2026-04-24-plan-2103-v4-{claude,gemini}.md`

---

## Hyphen-Path Recurrence Notice (5TH RECURRENCE — DO NOT SKIM)

This v4 plan introduces the file `update_master_index.py` (UNDERSCORE — not hyphen).

The v3 plan specified `update-master-index.py` (hyphen). That filename re-introduced the very anti-pattern v3 was supposed to close out — **the 5th time** the hyphen pattern slipped through plan drafting on or after 2026-04-24:
1. #2124 v1 — `from ingest_orcina import …` paired with `ingest-orcina.py`
2. #2124 v2 — created `ingest-orcina-extended.py`
3. #2126 v4 — `pytest -p scripts.data.llm-wiki.tests.markdown_qa.conftest`
4. #2103 v2 — kept `ingest-bemrosetta.py` / `ingest-aqwa.py` hyphenated for "parallelism"
5. #2103 v3 — fixed the two ingesters but introduced a brand-new hyphenated `update-master-index.py`

Memory: `feedback_llm_wiki_hyphen_module_path_pattern.md`. Per Claude r3 (P2 #1) the merger rename is a non-negotiable in v4. v4 also promotes the regression-prevention from imports to file naming (see TDD `test_no_new_hyphen_named_python_files_under_llm_wiki`). All implementers must grep the plan body for `llm-wiki\.` and `\b[a-z]+-[a-z]+\.py\b` BEFORE landing — both must be 0 matches.

---

## Review History (closure summary)

### r1, r2 (resolved in v2/v3)

See v2/v3 plan history.

### r3 (resolved in v4)

| Finding | Class | Resolution in v4 |
|---|---|---|
| **`update-master-index.py` is a newly-created hyphen-named Python file** — directly recurring the very anti-pattern v3 cites and supposedly closes for the two ingesters. Either rename to `update_master_index.py` or justify CLI-only-never-imported. | **P2** | **Resolved.** v4 renames the merger to `update_master_index.py` (underscore). All references in Pseudocode, Files-to-Change, Acceptance Criteria, and Build Sequence updated. Additionally, v4 promotes the regression guard from import-only to file-naming: a new TDD row `test_no_new_hyphen_named_python_files_under_llm_wiki` will grep `find scripts/data/llm-wiki -maxdepth 1 -name '*-*.py'` and assert the only match is the grandfathered `ingest-orcina.py`. |
| **`_atomic_write_json` location unspecified** — v3 references it from `ingest_bemrosetta.py`, `ingest_aqwa.py`, AND inline in the merger; three implementations will drift. If it lives in `orcina_common.py`, that adds a dependency on #2124 v3 beyond the 4 currently-attested helpers. | **P2** | **Resolved — option (c): new dedicated local module.** v4 introduces `scripts/data/llm-wiki/atomic_io.py` as the single source of truth for `_atomic_write_json`. Both new ingesters AND the renamed merger import from it: `from atomic_io import atomic_write_json`. Rationale for choosing this over option (a) (extend `orcina_common.py`): adding helpers to `orcina_common.py` requires re-coordination with #2124 v3 beyond the 4 attested helpers — that re-opens cross-plan negotiation that v3 explicitly closed. Rationale for choosing this over option (b) (duplicate per ingester): three drifting implementations is exactly the DRY violation Claude r3 P2 #2 flagged. The new `atomic_io.py` is small, scoped, and reachable via the same `tests/conftest.py` `sys.path.insert` that the ingesters use — no new import gymnastics. Pseudocode now defines `atomic_write_json` once, with the try/finally tempfile-unlink path spelled out (closes r3 P3 atomic-write tempfile cleanup). |
| **Master-index merger read-modify-write is NOT concurrency-safe** despite v3's "single-shell serial model" claim. Two concurrent merger runs will silently last-writer-wins on the `products` dict — atomic write of the final file does not protect the read-modify-write window. | **P2** | **Resolved — option (i): file lock via `fcntl.flock` on a sidecar lockfile.** v4 wraps the entire `merge_master_index` read-modify-write window in an exclusive advisory `fcntl.flock(LOCK_EX)` on `<output_root>/.index-lock` (a separate sentinel file, NOT the master `index.json` itself — locking the in-place file would race against the `os.replace` swap). Justification for option (i) over (ii) per-source append-then-merge: the merger's job IS reconciliation across sources; pushing reconciliation downstream just relocates the same race. Justification over (iii) serial-only with runtime assertion: the v3 Risks section already noted "future automation may chain ingest→merge" — a runtime assertion converts a silent data loss into a hard crash, but the user-visible failure is still the same operational blocker. `fcntl.flock` is POSIX, available in stdlib, and converts the race into a cooperative serialization with no operator-visible impact. The lockfile is created on first run if missing; held for the duration of the read-modify-write; released on context-manager exit. The Risk section documents the `fcntl` POSIX-only constraint (Linux + macOS — no Windows support; matches existing repo posture per `pyproject.toml` runtime targets). |

### r3 P3s (acknowledged in v4)

| Finding | v4 disposition |
|---|---|
| Tempfile cleanup on mid-write failure not shown in pseudocode but asserted by 3 tests | Resolved — `atomic_write_json` pseudocode now spells out the try/except/finally + `os.unlink(tmp_path)` cleanup explicitly. The three atomic-write tests now have a clear implementation target. |
| `parse_wiki_sidebar` and `fetch_github_tree_for_repo_markdown` ownership unclear | Resolved — declared LOCAL to `ingest_bemrosetta.py` in pseudocode comments. NOT expected from `orcina_common.py`. |
| `test_search_wiki_surfaces_bemrosetta` fixture wiring mechanism unspecified | Resolved — v4 specifies the wiring: tests will set `WIKI_OUTPUT_ROOT` env var (already honored by `resolve_wiki_path.py` per #2140) to point at the fixture dir, then `subprocess.run([sys.executable, ".../search-wiki.py", ...], env={**os.environ, "WIKI_OUTPUT_ROOT": str(fixture_dir)})`. Added to TDD Test List description column. |
| Codex coverage gap (r2 + r3 both skip Codex due to upstream regression #2479) | Acknowledged in Adversarial Review Summary; not a blocker since Claude+Gemini r3 cycle reached MAJOR + APPROVE convergence on actionable defects. Will retry Codex on r4 if upstream regression is resolved by then. |
| Registry/priority-queue follow-up SLA missing | v4 commits to filing the follow-up issue at PLAN-APPROVAL time (not PR-open) and links the issue number in the acceptance-criterion checkbox. Tightens the ingested-but-unconsumed window. |
| Hyphen-import regression guard scope | Promoted in v4 — see r3 P2 #1 resolution above; new TDD row covers file-naming as well as imports. |

### r3 Gemini suggestion + question (acknowledged in v4)

- Suggestion: centralize `_atomic_write_json` in `orcina_common.py` in a future PR — v4 places it in the new `atomic_io.py` for now (rationale in r3 P2 #2 row above). A future PR can promote `atomic_io.py` into `orcina_common.py` once #2124 has stabilized; non-blocking follow-up.
- Question: timeline/threshold to trigger the `orcina_common.py` shim fallback for #2124 dependency slip — v4 sets a concrete SLA: **if `#2124 v3` has not landed within 5 working days of `#2103` plan-approval, escalate to extracting the 4-helper shim as a micro-PR** (and `atomic_io.py` ships from this plan independently regardless). Documented in Risks.

---

## Attested Evidence

Independently-verifiable claims this v4 plan relies on. Each was checked against HEAD `12b4be834954505ca1e7fc8ad8b20bda34e92baf` on 2026-04-24.

| Claim | Verification method | Result |
|---|---|---|
| Issue #2103 OPEN | `gh issue view 2103` | OPEN — "feat(llm-wiki): extend ingestion to AQWA and BEMRosetta documentation" |
| Issue #2088 CLOSED (parent — Orcina prior-art) | carry-forward from v2/v3 evidence | CLOSED |
| Issue #2140 CLOSED (portable path resolver) | carry-forward; `resolve_wiki_path.py` honors `WIKI_OUTPUT_ROOT` env var | CLOSED |
| Issue #2124 OPEN (sibling — extended Orcina ingestion + `orcina_common.py` extraction) | carry-forward; r3 in flight | OPEN |
| `scripts/data/llm-wiki/ingest-orcina.py` exists (filename hyphenated, not importable as `ingest_orcina`) | `ls scripts/data/llm-wiki/ingest*.py` | EXISTS — only hyphenated match (grandfathered legacy) |
| `scripts/data/llm-wiki/search-wiki.py` hardcodes `PRODUCTS = ["orcaflex", "orcawave", "orcfxapi", "papers"]` at line 15 | `grep -n "PRODUCTS" scripts/data/llm-wiki/search-wiki.py` | line 15, also referenced at lines 37, 40, 166 — CONFIRMED |
| `search-wiki.py:_load_topics` (lines 25-30) is generic per-product loader; reads `<WIKI_DIR>/<product>/index.json`; honors `topics` key (or `papers` for the papers product) | Read of `search-wiki.py:_load_topics` | CONFIRMED — extending PRODUCTS plus emitting `topics: [...]` keyed indexes is sufficient |
| `docs/plans/README.md:53` requires `cat:data-pipeline` class to **consult** `registry.yaml`, pipeline config, and `resource-intelligence-maturity.yaml` (verb is "consult", not "update") | `grep -n "data-pipeline" docs/plans/README.md` | line 53 row — CONFIRMED. Verb is "consult" |
| `data/document-index/registry.yaml` has NO pre-existing BEMRosetta / AQWA entries | `grep -n "bemrosetta\|aqwa" data/document-index/registry.yaml` | no match — CONFIRMED |
| `data/document-index/resource-intelligence-maturity.yaml` has NO pre-existing BEMRosetta / AQWA maturity rows | `grep -n "bemrosetta\|aqwa" data/document-index/resource-intelligence-maturity.yaml` | no match — CONFIRMED |
| `data/document-index/online-resource-registry.yaml` lists ANSYS AQWA reference/theory/training/product entries + BEMRosetta GitHub repo | `grep -n "aqwa\|bemrosetta" data/document-index/online-resource-registry.yaml` | lines 1031, 1217, 1228, 1238, 1533 — CONFIRMED |
| `data/document-index/llm-wiki-external-source-priority-queue.yaml` exists and governs llm-wiki ingestion pipeline config | `ls data/document-index/llm-wiki-external-source-priority-queue.yaml` | EXISTS |
| `#2124 v3` proposes `orcina_common.py` (underscore-named) covering helpers `html_to_markdown`, `_convert_element`, `_convert_table`, `fetch_page` (verbatim move from `ingest-orcina.py` lines 98/135/261/286) | read of `/tmp/plan-drafts/plan-2124-v3.md` Files-to-Change + Pseudocode | CONFIRMED — `orcina_common.py` is the canonical name to reuse from #2103. **v4 note:** the 4 attested helpers do NOT include any atomic-write helper — that's why v4 places `atomic_write_json` in a new local `atomic_io.py` rather than extending `orcina_common.py`. |
| `scripts/data/llm-wiki/tests/` contains `__init__.py`, `test_e2e_smoke.py`, `test_resolve_wiki_path.py` at HEAD; **no conftest.py exists** | `ls scripts/data/llm-wiki/tests/` | conftest.py NOT FOUND — v4 will create it (carried from v3) |
| `resolve_wiki_path.py` resolves output root by env var `WIKI_OUTPUT_ROOT` first, then config, then `data/llm-wiki/`, then `knowledge/wikis/` | read of `scripts/data/llm-wiki/resolve_wiki_path.py` | CONFIRMED — `WIKI_OUTPUT_ROOT` is the env var name; v4 search-integration tests use it to point `search-wiki.py` at the fixture dir |
| `fcntl.flock` is in Python stdlib on Linux + macOS, not Windows | Python stdlib docs (`fcntl` module is POSIX-only) | CONFIRMED — matches workspace-hub Linux-first runtime posture |

Claims the plan does NOT attest (require live verification during implementation, not plan-approval):
- Exact pagination / sidebar HTML structure of `https://github.com/BEMRosetta/BEMRosetta/wiki` (fixtures will be captured during implementation).
- Exact public-reachability of ANSYS AQWA help URLs from unauthenticated CI — the ingester is designed to degrade gracefully to zero-topic + populated `errors[]` if gated.
- BEMRosetta repo `doc/` directory exact Markdown file count.

---

## Resource Intelligence Summary

### Existing repo code (anchored to base SHA `12b4be83`)
- Found: `scripts/data/llm-wiki/ingest-orcina.py` — canonical prior-art ingester (#2088). Provides `parse_toc_xml()`, `html_to_markdown()`, `_convert_element()`, `_convert_table()`, `fetch_page()`, `ingest_product()`, `ingest_supplementary()`, `ingest_papers()`. Writes to `<output_root>/<product>/topics/*.md` plus `<product>/index.json` and master `index.json`.
- Found: `scripts/data/llm-wiki/resolve_wiki_path.py` — portable output-root resolver (#2140); honors env var `WIKI_OUTPUT_ROOT` first, then config, then `data/llm-wiki/`, then `knowledge/wikis/`.
- Found: `scripts/data/llm-wiki/search-wiki.py` — search CLI. **Critical:** hardcodes `PRODUCTS = ["orcaflex", "orcawave", "orcfxapi", "papers"]` at line 15. The `_load_topics()` loader (line 25-30) is generic.
- Found: `scripts/data/llm-wiki/tests/test_resolve_wiki_path.py`, `tests/test_e2e_smoke.py` — existing pytest scaffold.
- **Will-exist after #2124 v3 lands (gating dependency)**: `scripts/data/llm-wiki/orcina_common.py` — shared helpers extracted from `ingest-orcina.py`. v4 reuses it directly; does NOT create a second helpers module.
- Gap: no `ingest_bemrosetta.py` or `ingest_aqwa.py` exists.
- Gap: no `scripts/data/llm-wiki/atomic_io.py` exists (created by this plan; closes r3 P2 #2).
- Gap: no `scripts/data/llm-wiki/tests/conftest.py` exists (created by this plan; closes r2 P2 #1).
- Gap: no `update_master_index.py` exists (created by this plan; underscore name closes r3 P2 #1).
- Gap: no curated AQWA/BEMRosetta cross-reference under `knowledge/wikis/marine-engineering/wiki/tools/` — out of scope, future issue.

### cat:data-pipeline retrieval contract (carried from v3)

Per `docs/plans/README.md:53`, `cat:data-pipeline` issues must **consult** `registry.yaml`, pipeline config, and `resource-intelligence-maturity.yaml`. v4 follows the v3 disposition: consultation satisfied; only `resource-intelligence-maturity.yaml` is updated by this plan; `registry.yaml` and `llm-wiki-external-source-priority-queue.yaml` updates land as the plan-approval-time follow-up sibling issue (per r3 P3 SLA tightening).

### Master-index and per-product-index contract (locks the `search-wiki.py` integration)

v4 carries v3's contract verbatim. The relevant `search-wiki.py:_load_topics` excerpt:

```python
def _load_topics(wiki_dir, product):
    idx = wiki_dir / product / "index.json"
    if not idx.exists():
        return []
    data = json.loads(idx.read_text())
    return data.get("topics" if product != "papers" else "papers", [])
```

Each new ingester writes:

```
<output_root>/bemrosetta/index.json  →  {"topics": [{"file": "...", "title": "...", "sections": [...], "section_path": [...]}, ...], "errors": [...]}
<output_root>/aqwa/index.json        →  {"topics": [...], "errors": [...]}
```

Per-product index writes use the canonical `atomic_write_json` from `atomic_io.py` (closes r3 P2 #2 — single source of truth).

The renamed master-index merger (`update_master_index.py`) merges per-product indexes into `<output_root>/index.json`, wrapping the read-modify-write window in `fcntl.flock(LOCK_EX)` on `<output_root>/.index-lock` (closes r3 P2 #3 — concurrency-safe):

```
{
  "generated": "<iso timestamp>",
  "products": {"orcaflex": {...}, "orcawave": {...}, "orcfxapi": {...}, "bemrosetta": {...}, "aqwa": {...}},
  "supplementary": {...}, "papers": {...}
}
```

### Standards
Not applicable — documentation-pipeline issue, not an engineering-standards deliverable.

### LLM Wiki pages consulted
- `knowledge/wikis/marine-engineering/wiki/` — existing marine-engineering wiki tree; new AQWA/BEMRosetta output lands under `data/llm-wiki/`, not in the curated wiki.
- `knowledge/wikis/marine-engineering/CLAUDE.md` — governance guardrails for durable-curated vs transient-ingested content (#2209).

### Documents consulted
- Issue body #2103 — deliverables: `ingest_bemrosetta.py`, `ingest_aqwa.py` (underscore), outputs at `data/llm-wiki/bemrosetta/` and `data/llm-wiki/aqwa/`, master index update.
- Parent issue #2088 — CLOSED; defined the MadCap-Flare TOC + `html_to_markdown` pattern.
- Sibling plan `/tmp/plan-drafts/plan-2124-v3.md` — gating dependency; introduces `orcina_common.py` that this plan reuses.
- `docs/plans/2026-04-12-llm-wiki-ecosystem-strengthening-gh-stories.md` — ecosystem roadmap.
- `docs/plans/2026-04-11-issue-2205-multi-machine-llm-wiki-resource-doc-intelligence-operating-model.md` — operating model.
- `docs/plans/README.md` — issue-class retrieval contract (line 53 — `cat:data-pipeline`).
- Memory: `feedback_llm_wiki_hyphen_module_path_pattern.md` — drives the underscore-rename + conftest pattern; **5th-recurrence trigger** for the `update_master_index.py` rename in v4.
- Memory: `feedback_merge_race_silent_revert.md`, `feedback_multi_agent_commit_serialization.md` — drive the block-on-#2124-v3 coordination decision.
- Upstream: `https://github.com/BEMRosetta/BEMRosetta` — open-source repo with `doc/` + GitHub wiki.
- Upstream: ANSYS AQWA help — public help URLs gated behind login; degrade gracefully.

### Gaps identified
- No BEMRosetta ingester (built by this plan).
- No AQWA ingester (built by this plan).
- No `atomic_io.py` for shared atomic-write helper (built by this plan; r3 P2 #2 fix).
- No conftest.py for tests (built by this plan; r2 P2 #1 fix).
- No master-index merger (built by this plan; renamed underscore in v4 — r3 P2 #1 fix).
- No `search-wiki.py` coverage for new products (extended by this plan).
- No registry / maturity rows (maturity rows added by this plan; registry follow-up filed at plan-approval time per r3 P3 SLA tightening).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-24):
- `#2103` — OPEN
- `#2088` — CLOSED
- `#2140` — CLOSED
- `#2124` — OPEN (gating dependency for this plan)

**File existence** (`ls` 2026-04-24 against HEAD `12b4be83`):
- EXISTS: `scripts/data/llm-wiki/ingest-orcina.py`
- EXISTS: `scripts/data/llm-wiki/resolve_wiki_path.py`
- EXISTS: `scripts/data/llm-wiki/search-wiki.py`
- EXISTS: `scripts/data/llm-wiki/tests/test_resolve_wiki_path.py`, `tests/test_e2e_smoke.py`, `tests/__init__.py`
- EXISTS: `data/document-index/{registry,resource-intelligence-maturity,llm-wiki-external-source-priority-queue,online-resource-registry}.yaml`
- WILL-EXIST AFTER #2124 v3 LANDS (gating dependency): `scripts/data/llm-wiki/orcina_common.py`
- MISSING (this plan creates): `scripts/data/llm-wiki/ingest_bemrosetta.py`
- MISSING (this plan creates): `scripts/data/llm-wiki/ingest_aqwa.py`
- MISSING (this plan creates): `scripts/data/llm-wiki/atomic_io.py` (r3 P2 #2 fix — single source of truth for atomic write)
- MISSING (this plan creates): `scripts/data/llm-wiki/update_master_index.py` (UNDERSCORE — r3 P2 #1 fix)
- MISSING (this plan creates): `scripts/data/llm-wiki/tests/conftest.py`
- MISSING (this plan creates): `scripts/data/llm-wiki/tests/test_ingest_bemrosetta.py`
- MISSING (this plan creates): `scripts/data/llm-wiki/tests/test_ingest_aqwa.py`
- MISSING (this plan creates): `scripts/data/llm-wiki/tests/test_search_wiki_surfaces_new_products.py`
- MISSING (this plan creates): `scripts/data/llm-wiki/tests/test_atomic_io.py`

Distinct sources consulted: 13 (issue body, #2088, #2140, #2124 v3 sibling plan, `ingest-orcina.py`, `resolve_wiki_path.py`, `search-wiki.py`, marine-engineering wiki, ecosystem-strengthening plan, docs/plans/README.md, operating-model plan #2205 + registry/maturity/queue yaml trio, hyphen-path memory, merge-race memory).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan (v4) | `docs/plans/2026-04-24-issue-2103-aqwa-bemrosetta-ingestion.md` |
| Shared helpers module (reused, NOT created) | `scripts/data/llm-wiki/orcina_common.py` (created by #2124 v3 — this plan blocks on its landing) |
| Shared atomic-write helper (NEW — r3 P2 #2 fix) | `scripts/data/llm-wiki/atomic_io.py` (single source of truth for `atomic_write_json`) |
| BEMRosetta ingester | `scripts/data/llm-wiki/ingest_bemrosetta.py` (underscore — closes r2 P2 #3) |
| AQWA ingester | `scripts/data/llm-wiki/ingest_aqwa.py` (underscore — closes r2 P2 #3) |
| Master-index updater (RENAMED — r3 P2 #1 fix) | `scripts/data/llm-wiki/update_master_index.py` (underscore; was hyphen in v3) |
| Search-wiki CLI (PRODUCTS extended) | `scripts/data/llm-wiki/search-wiki.py` |
| Tests conftest (NEW — closes r2 P2 #1) | `scripts/data/llm-wiki/tests/conftest.py` |
| Atomic-io tests (NEW — supports r3 P2 #2 fix) | `scripts/data/llm-wiki/tests/test_atomic_io.py` |
| BEMRosetta tests | `scripts/data/llm-wiki/tests/test_ingest_bemrosetta.py` |
| AQWA tests | `scripts/data/llm-wiki/tests/test_ingest_aqwa.py` |
| search-wiki integration test | `scripts/data/llm-wiki/tests/test_search_wiki_surfaces_new_products.py` |
| Fixtures | `scripts/data/llm-wiki/tests/fixtures/bemrosetta_wiki_page.html`, `bemrosetta_raw_readme.md`, `aqwa_login_wall.html`, `aqwa_public_help.html`, `search_fixture_wiki/bemrosetta/index.json` + sample topic md, `search_fixture_wiki/aqwa/index.json` |
| Ingested output (runtime) | `data/llm-wiki/bemrosetta/topics/*.md`, `data/llm-wiki/aqwa/topics/*.md`, `data/llm-wiki/bemrosetta/index.json`, `data/llm-wiki/aqwa/index.json` |
| Master index | `data/llm-wiki/index.json` |
| Master-index lockfile (NEW — r3 P2 #3 fix) | `data/llm-wiki/.index-lock` (sentinel only; never read for content) |
| Plan reviews (r4) | `scripts/review/results/2026-04-24-plan-2103-v4-{claude,gemini}.md` |

---

## Deliverable

After #2124 v3 will land `orcina_common.py` on `main`, this plan will add: a tests `conftest.py` that puts the llm-wiki package directory on `sys.path` (closes r2 P2 #1); a new `atomic_io.py` providing the canonical `atomic_write_json` used by both new ingesters and the master-index merger (closes r3 P2 #2); two new underscore-named ingesters — `ingest_bemrosetta.py` (GitHub wiki + repo `doc/` Markdown + raw README) and `ingest_aqwa.py` (ANSYS help with login-wall detection + graceful zero-topic degradation), both reusing `orcina_common.py` helpers (closes r2 P2 #2 + #3); a master-index merger `update_master_index.py` (UNDERSCORE filename — closes r3 P2 #1; concurrency-safe via `fcntl.flock` on a sidecar lockfile — closes r3 P2 #3); and an extension of `search-wiki.py`'s `PRODUCTS` list, so that BEMRosetta and AQWA corpora will surface through the existing search CLI alongside the Orcina family.

---

## Pseudocode

```
# ── scripts/data/llm-wiki/tests/conftest.py (NEW — closes r2 P2 #1) ──
# Put the package directory on sys.path so tests under tests/ can import
# `from ingest_bemrosetta import ...`, `from ingest_aqwa import ...`,
# `from orcina_common import ...`, `from atomic_io import ...` directly
# without importlib gymnastics. SINGLE declarative mechanism.
import sys
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent.parent  # scripts/data/llm-wiki/
if str(PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGE_DIR))


# ── scripts/data/llm-wiki/atomic_io.py (NEW — closes r3 P2 #2: SINGLE SOURCE OF TRUTH) ──
# Canonical atomic JSON write. Used by both ingesters AND the master-index merger.
# Pseudocode spells out the try/except/finally tempfile cleanup explicitly so the
# three atomic-write tests (test_bemrosetta_index_atomic_write,
# test_aqwa_index_atomic_write, test_update_master_index_atomic_write) have a
# clear implementation target (closes r3 P3 tempfile-cleanup gap).
import json
import os
import tempfile
from pathlib import Path

def atomic_write_json(path: Path, payload, *, indent: int = 2, sort_keys: bool = True) -> None:
    """Write payload to path atomically: write-temp + os.replace.

    Tempfile is created in the same directory as `path` (so os.replace stays
    on the same filesystem and is truly atomic). On any error during json.dump,
    the partial tempfile is unlinked so the destination is never half-written
    AND no .tmp orphans are left behind.
    """
    path = Path(path)
    tmp_fd, tmp_path = tempfile.mkstemp(
        prefix=path.name + ".",
        suffix=f".{os.getpid()}.json.tmp",
        dir=str(path.parent),
    )
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=indent, sort_keys=sort_keys)
        os.replace(tmp_path, path)
    except Exception:
        # Cleanup partial tempfile so the directory does not collect .tmp orphans.
        try:
            os.unlink(tmp_path)
        except FileNotFoundError:
            pass
        raise


# ── scripts/data/llm-wiki/ingest_bemrosetta.py (NEW — underscore name; closes r2 P2 #3) ──
# Reuses orcina_common.py (closes r2 P2 #2 — no second helpers module).
# Reuses atomic_io.atomic_write_json (closes r3 P2 #2 — no duplicated helper).
# Local helpers (parse_wiki_sidebar, fetch_github_tree_for_repo_markdown,
# fetch_raw_markdown, extract_title_from_markdown, extract_md_headings) are
# DEFINED IN THIS FILE — NOT expected from orcina_common.py (closes r3 P3
# helper-ownership ambiguity).
from orcina_common import fetch_page, html_to_markdown, _convert_element, _convert_table
from atomic_io import atomic_write_json

SOURCES = {
    "github_wiki":  "https://github.com/BEMRosetta/BEMRosetta/wiki",
    "repo_docs":    "https://raw.githubusercontent.com/BEMRosetta/BEMRosetta/master/doc",
    "readme_raw":   "https://raw.githubusercontent.com/BEMRosetta/BEMRosetta/master/README.md",
    "tree_api":     "https://api.github.com/repos/BEMRosetta/BEMRosetta/git/trees/master?recursive=1",
}

def slugify(url_or_title) -> str:
    """Stable slug from URL or title; mirrors the existing ingester's convention. Local helper."""
    ...

def parse_wiki_sidebar(html) -> list[tuple[str, str]]:
    """LOCAL helper. Parses the GitHub wiki sidebar HTML and returns [(page_url, title), ...]."""
    ...

def fetch_github_tree_for_repo_markdown(api_url, *, subdir: str) -> list[dict]:
    """LOCAL helper. Returns markdown-file entries from the GitHub git-tree API; falls back on 403 rate-limit."""
    ...

def fetch_raw_markdown(url) -> bytes | None:
    """LOCAL helper. Fetches raw markdown bytes; returns None on failure."""
    ...

def extract_title_from_markdown(md_bytes, *, fallback) -> str:
    """LOCAL helper."""
    ...

def extract_md_headings(md_body) -> list[str]:
    """LOCAL helper."""
    ...

def ingest_bemrosetta(output_root):
    product_dir = output_root / "bemrosetta"
    topics_dir  = product_dir / "topics"
    topics_dir.mkdir(parents=True, exist_ok=True)
    topics, errors = [], []

    # 1. GitHub wiki: fetch sidebar, enumerate pages, convert each via html_to_markdown
    wiki_index_html = fetch_page(SOURCES["github_wiki"])
    for page_url, title in parse_wiki_sidebar(wiki_index_html):
        page_html = fetch_page(page_url)
        if page_html is None:
            errors.append({"url": page_url, "reason": "fetch_failed"}); continue
        md, headings = html_to_markdown(page_html, page_url)
        filename = f"{slugify(title)}.md"
        (topics_dir / filename).write_text(md, encoding="utf-8")
        topics.append({"file": filename, "title": title, "sections": headings, "section_path": ["wiki"]})

    # 2. Repo doc tree via raw.githubusercontent (with 403 fallback)
    tree = fetch_github_tree_for_repo_markdown(SOURCES["tree_api"], subdir="doc")
    for entry in tree:
        raw_url = f"https://raw.githubusercontent.com/BEMRosetta/BEMRosetta/master/{entry['path']}"
        md_bytes = fetch_raw_markdown(raw_url)
        if md_bytes is None:
            errors.append({"url": raw_url, "reason": "fetch_failed"}); continue
        title = extract_title_from_markdown(md_bytes, fallback=Path(entry["path"]).stem)
        filename = f"{slugify(entry['path'])}.md"
        md_body = f"<!-- source: {raw_url} -->\n\n{md_bytes.decode('utf-8', errors='replace')}"
        (topics_dir / filename).write_text(md_body, encoding="utf-8")
        topics.append({"file": filename, "title": title, "sections": extract_md_headings(md_body), "section_path": ["doc"]})

    # 3. README
    readme_bytes = fetch_raw_markdown(SOURCES["readme_raw"])
    if readme_bytes is not None:
        md_body = f"<!-- source: {SOURCES['readme_raw']} -->\n\n{readme_bytes.decode('utf-8','replace')}"
        (topics_dir / "README.md").write_text(md_body, encoding="utf-8")
        topics.append({"file": "README.md", "title": "BEMRosetta README", "sections": extract_md_headings(md_body), "section_path": ["readme"]})

    # 4. Per-product index — atomic write via single source of truth (r3 P2 #2 fix)
    index = {"generated": iso_now(), "topic_count": len(topics), "topics": topics, "errors": errors}
    atomic_write_json(product_dir / "index.json", index)


# ── scripts/data/llm-wiki/ingest_aqwa.py (NEW — underscore name; closes r2 P2 #3) ──
from orcina_common import fetch_page, html_to_markdown
from atomic_io import atomic_write_json

AQWA_SEEDS = [
    "https://www.ansys.com/products/structures/ansys-aqwa",
    # ANSYS help URLs; login-gated — will record to errors[] if unreachable
    "https://ansyshelp.ansys.com/Views/Secured/corp/v242/en/aqwa_ref/aqwa_ref.html",
    "https://ansyshelp.ansys.com/Views/Secured/corp/v242/en/aqwa_theory/aqwa_theory.html",
]

def is_login_wall(html: str) -> bool:
    """LOCAL helper. Returns True if HTML is an ANSYS SSO redirect or generic sign-in page
       (indicators: 'returnurl=/Views/Secured', 'Sign In', 'login')."""
    ...

def ingest_aqwa(output_root):
    product_dir = output_root / "aqwa"
    topics_dir  = product_dir / "topics"
    topics_dir.mkdir(parents=True, exist_ok=True)
    topics, errors = [], []
    for url in AQWA_SEEDS:
        html = fetch_page(url)
        if html is None:
            errors.append({"url": url, "reason": "fetch_failed"}); continue
        if is_login_wall(html):
            errors.append({"url": url, "reason": "gated_login_wall"}); continue
        md, headings = html_to_markdown(html, url)
        title = extract_title(md, fallback=url)
        filename = f"{slugify(url)}.md"
        (topics_dir / filename).write_text(md, encoding="utf-8")
        topics.append({"file": filename, "title": title, "sections": headings, "section_path": ["help"]})
    # Zero-topic case is permitted; index always valid JSON. Atomic write (r3 P2 #2 fix).
    index = {"generated": iso_now(), "topic_count": len(topics), "topics": topics, "errors": errors}
    atomic_write_json(product_dir / "index.json", index)


# ── scripts/data/llm-wiki/update_master_index.py (NEW — UNDERSCORE; closes r3 P2 #1) ──
# 5TH RECURRENCE OF THE HYPHEN PATTERN — v3 had `update-master-index.py`; v4 renames.
# Grep this plan for `\b[a-z]+-[a-z]+\.py\b` BEFORE landing — must be 0 matches
# (modulo grandfathered `ingest-orcina.py` which is mentioned only as legacy context).
import fcntl
import json
from atomic_io import atomic_write_json

PRODUCT_KEYS = ["orcaflex", "orcawave", "orcfxapi", "bemrosetta", "aqwa"]

def merge_master_index(output_root):
    """Read-modify-write the master index.json under an exclusive flock on a sidecar
    lockfile (closes r3 P2 #3 — concurrency safety).

    Lockfile is `<output_root>/.index-lock` — a separate sentinel, NOT the master
    index.json itself, because locking the in-place file would race against the
    os.replace swap inside atomic_write_json. fcntl.flock(LOCK_EX) is POSIX-only
    (Linux + macOS); see Risks for the Windows-not-supported note.
    """
    master_path = output_root / "index.json"
    lock_path   = output_root / ".index-lock"
    output_root.mkdir(parents=True, exist_ok=True)
    # Create lockfile if missing; open for the duration of the read-modify-write.
    with open(lock_path, "a+") as lock_fh:
        fcntl.flock(lock_fh.fileno(), fcntl.LOCK_EX)
        try:
            existing = json.loads(master_path.read_text()) if master_path.exists() else {}
            existing.setdefault("products", {})
            for product in PRODUCT_KEYS:
                p = output_root / product / "index.json"
                if p.exists():
                    existing["products"][product] = {"topic_count": json.loads(p.read_text()).get("topic_count", 0)}
            existing["generated"] = iso_now()
            atomic_write_json(master_path, existing)
        finally:
            fcntl.flock(lock_fh.fileno(), fcntl.LOCK_UN)


# ── scripts/data/llm-wiki/search-wiki.py (MODIFIED — extends PRODUCTS) ──
# BEFORE (line 15): PRODUCTS = ["orcaflex", "orcawave", "orcfxapi", "papers"]
# AFTER  (line 15): PRODUCTS = ["orcaflex", "orcawave", "orcfxapi", "bemrosetta", "aqwa", "papers"]
# No other logic change: _load_topics (lines 25-30) is generic; argparse choices read PRODUCTS.
```

**Implementation rule (v4):** the new ingesters import shared helpers from `orcina_common.py` (created by #2124 v3 — gating dependency) AND `atomic_write_json` from the new local `atomic_io.py` (single source of truth). The renamed merger `update_master_index.py` (UNDERSCORE) imports `atomic_write_json` from the same `atomic_io.py` and wraps its read-modify-write in `fcntl.flock`. All ingester filenames are underscore-named; tests use plain `from <name> import ...` resolved through `tests/conftest.py` `sys.path.insert`. No `importlib.util.spec_from_file_location` workaround is used.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| **(Reuse, NOT create)** | `scripts/data/llm-wiki/orcina_common.py` | Created by #2124 v3 (gating dependency). This plan reuses `html_to_markdown`, `fetch_page`, `_convert_element`, `_convert_table`. Closes r2 P2 #2 by avoiding a second helpers module. |
| **Create** | **`scripts/data/llm-wiki/atomic_io.py`** | **(r3 P2 #2 fix)** single source of truth for `atomic_write_json`. Imported by both ingesters and the merger. Includes try/except/finally tempfile cleanup (closes r3 P3 tempfile orphan gap). |
| **Create** | **`scripts/data/llm-wiki/tests/conftest.py`** | **(r2 P2 #1 fix)** insert `scripts/data/llm-wiki/` on `sys.path` so tests can import underscore-named ingesters, `orcina_common`, and `atomic_io` directly. |
| Create | `scripts/data/llm-wiki/ingest_bemrosetta.py` | **(r2 P2 #3 fix — underscore filename)** BEMRosetta GitHub wiki + repo `/doc` + README ingester. Imports helpers via `from orcina_common import ...` and `from atomic_io import atomic_write_json`. Local helpers (parse_wiki_sidebar, fetch_github_tree_for_repo_markdown, fetch_raw_markdown, extract_title_from_markdown, extract_md_headings) defined inline (closes r3 P3 helper ownership gap). |
| Create | `scripts/data/llm-wiki/ingest_aqwa.py` | **(r2 P2 #3 fix — underscore filename)** AQWA ingester with login-wall detection + graceful zero-topic degradation. Atomic per-product index write via `atomic_io.atomic_write_json`. |
| **Create** | **`scripts/data/llm-wiki/update_master_index.py`** | **(r3 P2 #1 fix — UNDERSCORE filename, was hyphen in v3)** Merges per-product indexes into `data/llm-wiki/index.json`. Wraps read-modify-write in `fcntl.flock(LOCK_EX)` on `<output_root>/.index-lock` (r3 P2 #3 fix). Uses `atomic_io.atomic_write_json` for the final swap. |
| **Modify** | **`scripts/data/llm-wiki/search-wiki.py`** | extend `PRODUCTS` from `["orcaflex", "orcawave", "orcfxapi", "papers"]` to `["orcaflex", "orcawave", "orcfxapi", "bemrosetta", "aqwa", "papers"]` at line 15. |
| Create | `scripts/data/llm-wiki/tests/test_atomic_io.py` | unit tests for `atomic_write_json`: success path, mid-write failure leaves destination untouched + cleans up tempfile, concurrent writes from same process. |
| Create | `scripts/data/llm-wiki/tests/test_ingest_bemrosetta.py` | unit tests using fixture HTML + raw MD; uses plain `from ingest_bemrosetta import ingest_bemrosetta` (works through conftest sys.path). Patches `ingest_bemrosetta.fetch_page` (consuming module's bound name), not `orcina_common.fetch_page`. |
| Create | `scripts/data/llm-wiki/tests/test_ingest_aqwa.py` | unit tests for login-wall detection + zero-topic index. Plain import via conftest. |
| Create | `scripts/data/llm-wiki/tests/test_search_wiki_surfaces_new_products.py` | integration test: invokes `search-wiki.py` via subprocess with `WIKI_OUTPUT_ROOT` env var pointing at the fixture wiki dir (mechanism per `resolve_wiki_path.py` #2140). `--product=bemrosetta` returns ≥1 hit; `--product=aqwa` accepts argparse and returns 0 hits cleanly. |
| Create | `scripts/data/llm-wiki/tests/fixtures/bemrosetta_wiki_page.html` | offline fixture |
| Create | `scripts/data/llm-wiki/tests/fixtures/bemrosetta_raw_readme.md` | offline fixture for raw-MD path |
| Create | `scripts/data/llm-wiki/tests/fixtures/aqwa_login_wall.html` | offline fixture (ANSYS SSO redirect page) |
| Create | `scripts/data/llm-wiki/tests/fixtures/aqwa_public_help.html` | offline fixture for the happy-path case |
| Create | `scripts/data/llm-wiki/tests/fixtures/search_fixture_wiki/` | search-integration fixture: minimal `bemrosetta/index.json` + topic md + `aqwa/index.json` |
| Update | `data/document-index/resource-intelligence-maturity.yaml` | add draft-level maturity rows for `bemrosetta` and `aqwa` (cat:data-pipeline contract — consultation + this single update). |
| Update | `docs/plans/README.md` | add this plan to index |

**Dependency status (attested):** `beautifulsoup4>=4.14.3` already in root `pyproject.toml:12`. No manifest change. **Gating dependency**: #2124 v3's `orcina_common.py` must land on `main` before this plan executes (with 5-working-day SLA fallback to a 4-helper shim micro-PR — see Risks).

---

## TDD Test List

All tests use plain `from ingest_bemrosetta import ...` / `from ingest_aqwa import ...` / `from orcina_common import ...` / `from atomic_io import ...` resolved through `tests/conftest.py` `sys.path.insert`. Tests patching `fetch_page` patch the bound name in the consuming ingester module (e.g., `ingest_bemrosetta.fetch_page`), not `orcina_common.fetch_page`.

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_conftest_puts_llm_wiki_on_syspath` (r2 P2 #1 gate) | conftest mechanism is in place | run after collection: assert `str(Path(__file__).resolve().parent.parent) in sys.path` | True |
| `test_orcina_common_importable_from_tests` (r2 P2 #1 + #2 gate) | reused helpers module imports cleanly via conftest sys.path | `from orcina_common import html_to_markdown, fetch_page` inside a test | no ImportError |
| `test_atomic_io_importable_from_tests` (r3 P2 #2 gate) | new atomic_io module importable via conftest sys.path | `from atomic_io import atomic_write_json` | no ImportError |
| `test_atomic_io_success_path` | `atomic_write_json` writes valid JSON to destination | small dict, fresh tmp_path | file exists, json.load returns same dict, no `.tmp` orphans in dir |
| `test_atomic_io_failure_cleans_tempfile` (r3 P3 fix) | mid-write failure leaves destination untouched AND removes tempfile | monkeypatched `json.dump` raises | original destination unchanged; `glob('*.tmp')` returns empty list |
| `test_bemrosetta_wiki_page_converts` | GitHub-wiki HTML fixture renders to markdown with `<!-- source: ... -->` comment and H1 | fixture HTML | markdown string containing `# <title>` + source comment |
| `test_bemrosetta_raw_md_passthrough` | a `.md` from raw.githubusercontent passes through with source header added | raw md bytes + URL | md begins with `<!-- source: ... -->` |
| `test_bemrosetta_writes_product_index_shape` | index.json emitted at `<out>/bemrosetta/index.json` with `topics: [...]` matching `search-wiki.py:_load_topics` | mocked fetcher yields 3 topics | index.json has `topics` list length 3; each entry has `file`, `title`, `sections` |
| `test_bemrosetta_index_atomic_write` (r2 P3 fix) | per-product index write is atomic — no half-written file under simulated mid-write failure; uses `atomic_io.atomic_write_json` | monkeypatched `json.dump` raises mid-write | original index.json unchanged; no leftover `.tmp` file in dir |
| `test_bemrosetta_api_rate_limit_fallback` | when GitHub API tree endpoint returns 403, ingester falls back to README-only + WARN | mocked 403 response | exit 0 with README-only topics + `errors[]` populated with `rate_limited` reason |
| `test_aqwa_login_wall_recorded_not_crashed` | login-wall HTML is flagged + added to `errors[]`; run completes exit 0 | fixture login HTML | index.json `errors[]` length ≥ 1; `topic_count == 0`; process exit 0 |
| `test_aqwa_zero_topic_index_valid_json` | zero-topic run still writes a valid JSON index | all seeds return login walls | `json.load(index.json)` succeeds; shape has `topics: []` not missing key |
| `test_aqwa_public_happy_path_converts` | when a seed URL is publicly reachable, its HTML is converted and a topic entry is appended | fixture `aqwa_public_help.html` | `topics` has ≥1 entry |
| `test_aqwa_index_atomic_write` (r2 P3 fix) | per-product index write is atomic | monkeypatched `json.dump` raises mid-write | original index.json unchanged; no leftover `.tmp` file |
| `test_update_master_index_merges_all_products` | merger combines orcaflex/orcawave/orcfxapi/bemrosetta/aqwa if each per-product index exists | 5 fake per-product indexes | master `index.json` `products` dict has all 5 keys |
| `test_update_master_index_partial_ok` | merger runs when only a subset of per-product indexes exist | only bemrosetta index present | master has only `bemrosetta`; no KeyError |
| `test_update_master_index_atomic_write` | atomic write uses `os.replace` via `atomic_io.atomic_write_json`; no half-written file observable | monkeypatched `json.dump` raises mid-write | original master unchanged; no leftover `.tmp` |
| `test_update_master_index_flock_serializes_concurrent_runs` (r3 P2 #3 fix) | concurrent merger invocations serialize correctly via `fcntl.flock` — no `products` dict last-writer-wins | spawn two subprocess merger runs in parallel, each adding a different product index | both products present in final master; lockfile exists; no products silently dropped |
| `test_search_wiki_products_list_extended` (carry-forward) | `search-wiki.PRODUCTS` includes `bemrosetta` and `aqwa` | import `search-wiki` module; read `PRODUCTS` | `"bemrosetta" in PRODUCTS and "aqwa" in PRODUCTS` |
| `test_search_wiki_surfaces_bemrosetta` (r3 P3 wiring spec) | `search-wiki.py --product=bemrosetta "hydrodynamic"` returns ≥1 hit against fixture; wiring uses `WIKI_OUTPUT_ROOT` env var per #2140 | fixture `search_fixture_wiki/bemrosetta/index.json` + topic md; `subprocess.run([sys.executable, ".../search-wiki.py", "hydrodynamic", "--product=bemrosetta"], env={**os.environ, "WIKI_OUTPUT_ROOT": str(fixture_dir)})` | subprocess exit 0; JSON output list length ≥ 1; first hit's `product == "bemrosetta"` |
| `test_search_wiki_surfaces_aqwa` (r3 P3 wiring spec) | `search-wiki.py --product=aqwa` is accepted; if fixture aqwa index empty, returns 0 hits cleanly | fixture `search_fixture_wiki/aqwa/index.json` with `topics: []`; same `WIKI_OUTPUT_ROOT` env wiring | subprocess exit 0; JSON output is empty list; no traceback |
| `test_no_hyphen_in_python_import_paths` | grep — no Python `from`/`import` statements naming the hyphenated package directory or any hyphenated ingester filename | shell grep across `scripts/` and `docs/` for the hyphen-import patterns | zero matches |
| `test_no_new_hyphen_named_python_files_under_llm_wiki` (r3 P2 #1 promotion) | grep — no NEW hyphenated `.py` file under `scripts/data/llm-wiki/` (modulo grandfathered `ingest-orcina.py`) | `find scripts/data/llm-wiki -maxdepth 1 -name '*-*.py'` | only result is `ingest-orcina.py` (legacy); zero new matches |

Fixtures: saved HTML snapshots captured once from upstream; tests never hit the network.

---

## Acceptance Criteria

- [ ] `#2124 v3` will have landed `scripts/data/llm-wiki/orcina_common.py` on `main` (gating dependency check before any work begins; 5-working-day SLA fallback per Risks).
- [ ] `uv run pytest scripts/data/llm-wiki/tests/test_atomic_io.py -v` passes.
- [ ] `uv run pytest scripts/data/llm-wiki/tests/test_ingest_bemrosetta.py -v` passes.
- [ ] `uv run pytest scripts/data/llm-wiki/tests/test_ingest_aqwa.py -v` passes.
- [ ] `uv run pytest scripts/data/llm-wiki/tests/test_search_wiki_surfaces_new_products.py -v` passes.
- [ ] `uv run pytest scripts/data/llm-wiki/tests/ -v` (full suite including conftest-loaded discovery) passes — no regression on existing tests.
- [ ] `uv run python scripts/data/llm-wiki/ingest_bemrosetta.py --output-dir /tmp/wiki-smoke` exits 0 and produces `/tmp/wiki-smoke/bemrosetta/index.json` with `topic_count >= 1` (live-dependent floor; informational `>= 5` smoke target documented in Build Sequence step 11).
- [ ] `uv run python scripts/data/llm-wiki/ingest_aqwa.py --output-dir /tmp/wiki-smoke` exits 0 (even if all seeds gated); `/tmp/wiki-smoke/aqwa/index.json` is valid JSON with `topics` key present.
- [ ] `uv run python scripts/data/llm-wiki/update_master_index.py --output-dir /tmp/wiki-smoke` emits `/tmp/wiki-smoke/index.json` with `products.bemrosetta` and `products.aqwa` present, AND creates `/tmp/wiki-smoke/.index-lock` (sentinel).
- [ ] `uv run python scripts/data/llm-wiki/search-wiki.py "hydrodynamic" --product=bemrosetta` (with `WIKI_OUTPUT_ROOT=/tmp/wiki-smoke`) returns at least one hit.
- [ ] `uv run python scripts/data/llm-wiki/search-wiki.py "aqwa" --product=aqwa` is accepted by argparse and returns 0 hits cleanly when corpus empty.
- [ ] `grep -rn "from llm-wiki\|from ingest-orcina\|from ingest-bemrosetta\|from ingest-aqwa\|from update-master-index" scripts/ docs/` returns zero matches (hyphen-import regression guard).
- [ ] `find scripts/data/llm-wiki -maxdepth 1 -name '*-*.py'` returns ONLY `ingest-orcina.py` (file-naming regression guard — closes r3 P2 #1 promotion).
- [ ] `data/document-index/resource-intelligence-maturity.yaml` will gain draft-level rows for `bemrosetta` and `aqwa`.
- [ ] Follow-up sibling issue filed at PLAN-APPROVAL TIME (per r3 P3 SLA tightening) for: (a) `data/document-index/registry.yaml` entries, (b) `data/document-index/llm-wiki-external-source-priority-queue.yaml` entries. Issue number recorded in this checklist before plan-approval status flip.
- [ ] Plan review artifacts (r4) present at `scripts/review/results/2026-04-24-plan-2103-v4-{claude,gemini}.md`.

---

## Adversarial Review Summary

| Provider | Verdict (r1) | Verdict (r2) | Verdict (r3) | Verdict (r4) | Key findings |
|---|---|---|---|---|---|
| Claude | MAJOR (inline-content dispatch bug — UNUSABLE) | MAJOR (3 P2s + 4 P3s) | MAJOR (3 P2s + 6 P3s) | TBD after r4 | r3 P2s all resolved in v4: (P2 #1) merger renamed `update-master-index.py` → `update_master_index.py` AND grep guard promoted to file-naming; (P2 #2) `_atomic_write_json` consolidated into new `atomic_io.py` single-source-of-truth; (P2 #3) merger wraps read-modify-write in `fcntl.flock` on sidecar lockfile. r3 P3s addressed: tempfile cleanup spelled out, local helpers declared, search-wiki test wiring specified via `WIKI_OUTPUT_ROOT` env var. |
| Codex | MAJOR (2 P1s + 1 P2, all real) | not-run (codex-cli upstream regression #2479) | not-run (#2479 still open) | TBD (will retry r4 if #2479 resolves) | r1 closed in v2; r2/r3 not run due to upstream tooling block. |
| Gemini | NO_OUTPUT (silent failure) | APPROVE (2 non-blocking suggestions) | APPROVE (1 suggestion + 1 question) | TBD after r4 | Suggestion (centralize atomic write) — partially folded: lives in new `atomic_io.py` per r3 P2 #2 resolution; promotion to `orcina_common.py` deferred to follow-up PR. Question (#2124 slip SLA) — answered: 5-working-day threshold triggers minimal 4-helper shim micro-PR. |

**Overall result (r3):** MAJOR — resolved in v4.
**r4 pending.**

---

## Build Sequence (explicit — maps r3 P2 fixes to order)

1. **Verify gating dependency** (carry-forward). Confirm `#2124 v3` will have landed on `main` and `scripts/data/llm-wiki/orcina_common.py` exists with the four required helpers (`html_to_markdown`, `fetch_page`, `_convert_element`, `_convert_table`). If not landed within 5 working days of plan-approval, BLOCK and trigger the shim-micro-PR fallback (see Risks).
2. **Create `scripts/data/llm-wiki/tests/conftest.py`** (carry-forward). Insert package dir on `sys.path`. Run `uv run pytest scripts/data/llm-wiki/tests/test_resolve_wiki_path.py -v` to confirm conftest doesn't regress existing tests.
3. **Create `scripts/data/llm-wiki/atomic_io.py`** (r3 P2 #2 fix). Implements `atomic_write_json` with try/except/finally tempfile cleanup. Write `test_atomic_io.py` first (TDD), then implement.
4. **Write `test_conftest_puts_llm_wiki_on_syspath`, `test_orcina_common_importable_from_tests`, `test_atomic_io_importable_from_tests`** — gate the conftest + atomic_io modules. Run green.
5. **Modify `search-wiki.py` PRODUCTS** — one-line literal change at line 15 from 4 elements to 6.
6. **Write `test_search_wiki_surfaces_new_products.py`** (TDD-first) using `WIKI_OUTPUT_ROOT` env var wiring.
7. **Create `ingest_bemrosetta.py`** with three source flows. Imports `from atomic_io import atomic_write_json`. Local helpers (`parse_wiki_sidebar`, `fetch_github_tree_for_repo_markdown`, etc.) defined inline.
8. **Create `ingest_aqwa.py`** with login-wall detection + graceful zero-topic. Imports `from atomic_io import atomic_write_json`.
9. **Create `update_master_index.py`** (UNDERSCORE — r3 P2 #1 fix) with `fcntl.flock` wrapper around read-modify-write (r3 P2 #3 fix) and `atomic_io.atomic_write_json` for the final swap.
10. **Run `test_no_hyphen_in_python_import_paths` AND `test_no_new_hyphen_named_python_files_under_llm_wiki`** — repo-wide grep + filename grep must both return zero new hyphen matches.
11. **Add draft-level maturity rows** to `data/document-index/resource-intelligence-maturity.yaml` for `bemrosetta` + `aqwa`.
12. **Live smoke** — run BEMRosetta ingester once against upstream; informational target ≥5 topics (gating floor is ≥1); run AQWA ingester (zero-topic + populated errors[] still exit 0); run merger (verify `.index-lock` sentinel created); run `search-wiki.py --product=bemrosetta "hydrodynamic"` — ≥1 hit.
13. **File follow-up sibling issue** for registry.yaml + priority-queue.yaml entries at PLAN-APPROVAL time (per r3 P3 SLA tightening); record issue number in Acceptance Criteria checklist.
14. **Dispatch r4 cross-review** (Claude / Gemini; Codex retry if #2479 resolves). Address findings or iterate; do NOT self-approve.

---

## Risks and Open Questions

- **Risk — gating dependency on #2124 v3 may slip; SLA fallback (r3 Gemini question answered):** if #2124 v3 will not land within **5 working days of #2103 plan-approval**, escalate to extracting a minimal `orcina_common.py` shim (just the four helpers — `html_to_markdown`, `fetch_page`, `_convert_element`, `_convert_table`) into its own micro-PR that both #2103 and #2124 v3 will consume. Note that `atomic_io.py` ships from this plan independently regardless — it does not block on #2124. Decision tree captured here so a future operator does not need to re-derive it.
- **Risk — `fcntl.flock` is POSIX-only (r3 P2 #3 caveat):** the master-index merger's concurrency safety relies on `fcntl.flock`, which is Linux + macOS stdlib but not present on Windows. This matches the workspace-hub Linux-first runtime posture (per repo memory `context.md`). If a Windows runtime is ever introduced, swap to `portalocker` (cross-platform). Not a blocker for current execution.
- **Risk — helper-extraction regression already absorbed by #2124 v3:** since #2124 v3 owns the `ingest-orcina.py` mutation that creates `orcina_common.py`, this plan inherits that risk transitively but does not create it.
- **Risk — conftest scope leakage to other test directories:** the new `tests/conftest.py` only affects pytest collection rooted at `scripts/data/llm-wiki/tests/`. It does not pollute repo-wide `sys.path`.
- **Risk — AQWA public accessibility unknown at plan time:** ANSYS help is largely gated. Ingester succeeds with zero topics + populated `errors[]` rather than fail.
- **Risk — BEMRosetta GitHub API rate limits:** unauthenticated GitHub API may hit 60 req/hr. Mitigation: use `raw.githubusercontent.com` for content; use API only once per run for tree enumeration; on 403 fall back to README-only + WARN.
- **Risk — per-product index.json schema drift from `search-wiki.py:_load_topics` expectations:** v4 carries v3's lock on `topics: [{file, title, sections, section_path}, ...]`. Any future schema change must update `search-wiki.py` in the same commit.
- **Risk — atomic_io.py future migration to orcina_common.py (Gemini r3 suggestion):** v4 places `atomic_write_json` in a dedicated local `atomic_io.py` to avoid re-coordinating with #2124 v3 beyond the 4 attested helpers. Once #2124 stabilizes, a follow-up PR can promote `atomic_io.py` content into `orcina_common.py` and update the 5 import sites (2 ingesters + 1 merger + 1 test + 1 conftest reference). Non-blocking.
- **Open — automatic vs standalone master-index trigger** (carry-forward Gemini r2 question): v4 keeps standalone-only. With `fcntl.flock` now in place (r3 P2 #3 fix), future automation chaining ingest→merge is concurrency-safe. Confirm during approval whether to auto-trigger.
- **Open — when to file registry.yaml follow-up** (resolved r3 P3 — was: PR-open time; now: PLAN-APPROVAL time): v4 commits to filing at plan-approval time so the follow-up issue number can be recorded in the acceptance checklist before status flip.

---

## Complexity: T2

**T2** — gated reuse of an existing helper module (`orcina_common.py` from #2124 v3) + a new local `atomic_io.py` (single source of truth for atomic JSON write) + two new underscore-named ingesters + one new merger script (also underscore-named per r3 P2 #1 fix; concurrency-safe via `fcntl.flock` per r3 P2 #3 fix) + one surgical extension of `search-wiki.py`'s PRODUCTS list + a new `tests/conftest.py` + offline-fixture test suite + a single YAML maturity-row addition. Single domain, bounded surface. Multi-source + graceful-degrade AQWA path + search-integration gate + file-locking concurrency model keep it above T1; gating dependency on #2124 v3 with explicit SLA fallback is the most distinctive coordination element.
