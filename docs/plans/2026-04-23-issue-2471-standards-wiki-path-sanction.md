# Plan for #2471: sanction `wiki/standards/` as first-class wiki page type

> **Status:** draft (v2 — addresses r1 findings)
> **Complexity:** T1 (schema + tooling surface, no content generation)
> **Date:** 2026-04-23
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2471
> **Decision reference:** issue #2471 comment 2026-04-23 — "Add sanctioned wiki/standards/"

---

## Resource Intelligence Summary

### Existing repo code (ls-verified 2026-04-23)
- `knowledge/wikis/marine-engineering/CLAUDE.md` — current sanctioned page types: `entities/`, `concepts/`, `sources/`, `comparisons/`, `visualizations/`. Will be amended to add `standards/`.
- `knowledge/wikis/engineering/CLAUDE.md` — **already declares** `wiki/{concepts,entities,sources,standards,workflows}/` on line 7 (verified by `sed -n '7p' knowledge/wikis/engineering/CLAUDE.md`). No amendment required — this wiki is already conformant.
- `knowledge/wikis/naval-architecture/CLAUDE.md` — present (verified via `ls knowledge/wikis/naval-architecture/`); will be amended.
- `knowledge/wikis/maritime-law/CLAUDE.md` and `knowledge/wikis/personal/CLAUDE.md` and `knowledge/wikis/health-reports/CLAUDE.md` — out of scope for #2471 (non-standards wikis); will not be amended but will be left consistent.
- `scripts/knowledge/pyramid-conformance-check.py` — **frontmatter completeness checker (verified: lines 5, 120, 166 all concern frontmatter; no path allow-list)**. NOT the right surface for path sanctioning. Removed from Files-to-Change.
- `scripts/knowledge/llm_wiki.py` — `INIT_DIRS` constant at lines 42-52 enumerates created directories; currently missing `wiki/standards/` and `wiki/workflows/`. `cmd_status` loop at line 279 iterates `["entities", "concepts", "sources", "comparisons", "visualizations"]` — missing `standards` and `workflows`. This is the correct surface for the sanction.
- `scripts/knowledge/wiki-ingest-cron.sh` — ingest driver; expected path-agnostic but will be reviewed (no change expected).
- `scripts/data/llm-wiki/resolve_wiki_path.py` — path resolver; will be checked for allow-list.
- `.gitignore` — **verified lines 490-494**: `/knowledge/wikis/*` broadly ignores all wikis; only `!/knowledge/wikis/engineering/` and `!/knowledge/wikis/cross-links.md` are re-included. Therefore `knowledge/wikis/marine-engineering/` and `knowledge/wikis/naval-architecture/` are currently UNTRACKED by git. Any stub placed under these paths would not commit. **Decision: place the proof stub under `knowledge/wikis/engineering/wiki/standards/` (already tracked) rather than modify `.gitignore`**, since the stub's purpose is schema validation only. Domain-specific content relocation is deferred to #2227.

### Standards (meta — this plan is itself about standards governance)
| Standard / contract | Status | Source |
|---|---|---|
| Workspace issue-planning retrieval contract | active | `docs/plans/README.md` |
| llm-wiki frontmatter/index/log contract | active | `knowledge/wikis/*/CLAUDE.md` |
| Pyramid conformance contract | active | `scripts/knowledge/pyramid-conformance-check.py` |

### Documents consulted
- Issue #2471 body — acceptance criteria sanctioning a durable CSA destination.
- #2471 comment 2026-04-23 — user routing decision "Add sanctioned `wiki/standards/`".
- Issue #2227 — blocked CSA portion; will cite this plan as unblocking artifact.
- Issue #2216 — ACMA-codes umbrella; same.

---

## Scope

This plan will:
1. Add `standards/` to the sanctioned page-type list for the two wikis that do not yet declare it (marine-engineering, naval-architecture). The engineering wiki already declares `standards/` and will not be amended.
2. Define the frontmatter contract for `wiki/standards/*.md` pages (neutral across publishers — no per-code routing).
3. Extend `llm_wiki.py` so `INIT_DIRS` includes `wiki/standards/` and `wiki/workflows/`, and `cmd_status`'s counting loop includes `standards` and `workflows`.
4. Produce one sanctioned neutral stub at `knowledge/wikis/engineering/wiki/standards/TEMPLATE.md` (template-only, publisher-agnostic) to prove the schema end-to-end. This wiki is already git-tracked.
5. Not promote any publisher-specific content (CSA, OCIMF, API, DNV) into `wiki/standards/` — that is #2227's job, unblocked by this sanction. **Per decision #2471 ("sanctions path shape, not per-code routing"), this plan will not carry a CSA-specific stub.**

## Non-goals

- Will NOT promote CSA/OCIMF/DNV/API content into `wiki/standards/` at scale — that is deferred to #2227 and future content plans.
- Will NOT hardcode any per-publisher code (e.g., CSA) into the sanction artifacts — the decision explicitly scopes this plan to path shape only.
- Will NOT add `standards/` to non-standards wikis (maritime-law, personal, health-reports) — they can opt in later if relevant.
- Will NOT modify `.gitignore` to re-include `marine-engineering/` or `naval-architecture/` — their tracking status is orthogonal to path sanctioning and belongs to a separate decision.
- Will NOT restructure `raw/standards/` — that directory already exists and is unaffected.
- Will NOT change cross-wiki link syntax or frontmatter for existing page types.
- Will NOT modify `scripts/knowledge/pyramid-conformance-check.py` — it is a frontmatter checker, not a path allow-list, and is the wrong surface for this change.

---

## Files to Change

| File | Change type | Why |
|---|---|---|
| `knowledge/wikis/marine-engineering/CLAUDE.md` | modify | Add `standards/` (and, if missing, `workflows/`) to sanctioned list + frontmatter schema |
| `knowledge/wikis/naval-architecture/CLAUDE.md` | modify | Same |
| `knowledge/wikis/engineering/CLAUDE.md` | no change | Already declares `wiki/{concepts,entities,sources,standards,workflows}/` at line 7 (verified) |
| `scripts/knowledge/llm_wiki.py` | modify | Add `wiki/standards` and `wiki/workflows` to `INIT_DIRS` (lines 42-52); extend `cmd_status` counting loop (line 279) to include `standards` and `workflows` |
| `scripts/data/llm-wiki/resolve_wiki_path.py` | modify (conditional) | Add `standards/` to path allow-list if enumerated |
| `knowledge/wikis/engineering/wiki/standards/TEMPLATE.md` | create | Neutral (publisher-agnostic) schema-validation stub; path already git-tracked |
| `scripts/knowledge/tests/test_llm_wiki.py` | modify or create | Add test asserting `cmd_init` creates `wiki/standards/` and `wiki/workflows/` directories and `cmd_status` counts files under each |
| `docs/plans/README.md` | modify | Add row citing this plan |

## Frontmatter Contract for `wiki/standards/*.md`

Required fields (in addition to base schema):

| Field | Required | Type | Description |
|---|---|---|---|
| `title` | required | string | Standard name + short-form (e.g., "CSA Z276: LNG — production, storage, and handling") |
| `code_id` | required | string | Canonical code identifier (e.g., `csa-z276`, `api-17j`, `ocimf-mooring-equipment-guidelines-4e`) |
| `publisher` | required | string | Publishing body (e.g., `CSA Group`, `API`, `OCIMF`) |
| `revision` | required | string | Revision/edition/year (e.g., `2023`, `4e`, `1.2`) |
| `jurisdiction` | optional | string | Geographic or regulatory scope (e.g., `Canada`, `international`, `US-federal`) |
| `supersedes` | optional | list | Prior revisions or codes replaced |
| `added` | required | date | Per existing schema |
| `last_updated` | required | date | Per existing schema |
| `tags` | required | list | Per existing schema |
| `sources` | optional | list | Links to `raw/standards/*` source PDFs (canonical form) |

## Build Sequence

1. Amend `scripts/knowledge/llm_wiki.py`: extend `INIT_DIRS` with `"wiki/standards"` and `"wiki/workflows"`; extend `cmd_status`'s subdir loop to include `standards` and `workflows` in the count dictionary.
2. Add/extend tests under `scripts/knowledge/tests/` that exercise `cmd_init` and `cmd_status` to assert both new page types are created and counted.
3. Amend the two wiki `CLAUDE.md` files (marine-engineering, naval-architecture) with identical standards/ section insertions (preserve existing ordering). Do NOT touch engineering/CLAUDE.md — already conformant.
4. Create the neutral TEMPLATE.md stub at `knowledge/wikis/engineering/wiki/standards/TEMPLATE.md` with placeholder frontmatter fields and body "Template for publisher-specific standards pages. Populate per frontmatter contract. #2227 will add concrete pages under domain wikis once their git-tracking status is resolved."
5. Run `uv run python scripts/knowledge/pyramid-conformance-check.py`; expect clean exit (frontmatter complete on TEMPLATE.md).
6. Run `uv run python scripts/knowledge/llm_wiki.py status --wiki engineering` to confirm the new page types appear in the count report.
7. Update `docs/plans/README.md` to add the row.
8. Atomic commit per the standard plan-execution convention; push to a feature branch.

## TDD / Validation List

| Test | Passes when | Failure signal |
|---|---|---|
| `cmd_init` creates `wiki/standards/` and `wiki/workflows/` | directories exist after init | missing dir → schema not sanctioned |
| `cmd_status` reports non-zero file counts for `standards` and `workflows` keys after files are placed | counts dict has the keys with correct integers | KeyError or zero-count regression |
| Pyramid conformance accepts `knowledge/wikis/engineering/wiki/standards/TEMPLATE.md` | exit 0, no missing-frontmatter failures | frontmatter incomplete → exit non-zero |
| Frontmatter schema applied to TEMPLATE.md contains all required fields | YAML parse + required-field check passes | missing code_id / publisher / revision placeholders |
| `docs/plans/README.md` row exists | grep match on `2471` | row missing |

## Acceptance Criteria Alignment

- [x] sanctioned `wiki/standards/` durable destination is documented (publisher-neutral) — via `INIT_DIRS`, `cmd_status`, and CLAUDE.md amendments
- [x] relevant wiki CLAUDE/schema guidance allows the destination explicitly — two CLAUDE.md files amended (engineering already conformant)
- [x] gitignore/durability expectations are documented — verified `knowledge/wikis/engineering/` is re-included; TEMPLATE stub lands there; domain-wiki tracking is out of scope
- [x] #2227 can split OCIMF and CSA without unresolved routing ambiguity — `wiki/standards/` path sanctioned generically; #2227 plan v2 will choose publishers and cite this plan

## Risk & Rollback

- Risk: amending two CLAUDE.md files in isolation could introduce drift if one amendment is phrased differently. Mitigation: same paragraph inserted in both, verified by diff.
- Risk: `llm_wiki.py` `INIT_DIRS`/`cmd_status` edit could affect existing wikis that ran `cmd_init` before the change. Mitigation: `cmd_init` uses `mkdir -p` semantics (idempotent); `cmd_status` edit is additive (new keys, no removal).
- Rollback: single revert per atomic commit; TEMPLATE stub deletion is isolated.

## Downstream unblocks

- #2227 CSA/OCIMF portions can proceed against `knowledge/wikis/<domain>/wiki/standards/<code>.md` once domain tracking is resolved; #2227 plan v2 will cite this plan.
- Future standards coverage (API, OCIMF, DNV, ISO) has a sanctioned path shape.
