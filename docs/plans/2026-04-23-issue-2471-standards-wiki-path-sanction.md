# Plan for #2471: sanction `wiki/standards/` as first-class wiki page type

> **Status:** draft (v1 — awaiting cross-review)
> **Complexity:** T1 (schema + tooling surface, no content generation)
> **Date:** 2026-04-23
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2471
> **Decision reference:** issue #2471 comment 2026-04-23 — "Add sanctioned wiki/standards/"

---

## Resource Intelligence Summary

### Existing repo code (ls-verified 2026-04-23)
- `knowledge/wikis/marine-engineering/CLAUDE.md` — current sanctioned page types: `entities/`, `concepts/`, `sources/`, `comparisons/`, `visualizations/`. Will be amended to add `standards/`.
- `knowledge/wikis/engineering/CLAUDE.md` — parallel structure; needs same amendment.
- `knowledge/wikis/naval-architecture/CLAUDE.md` — present (verified via `ls knowledge/wikis/naval-architecture/`); needs same amendment.
- `knowledge/wikis/maritime-law/CLAUDE.md` and `knowledge/wikis/personal/CLAUDE.md` and `knowledge/wikis/health-reports/CLAUDE.md` — out of scope for #2471 (non-standards wikis); will not be amended but will be left consistent.
- `scripts/knowledge/pyramid-conformance-check.py` — enumerates sanctioned paths; will be extended.
- `scripts/knowledge/llm_wiki.py` — lint + init CLI; will be checked for path enumeration.
- `scripts/knowledge/wiki-ingest-cron.sh` — ingest driver; expected path-agnostic but will be reviewed.
- `scripts/data/llm-wiki/resolve_wiki_path.py` — path resolver; will be checked for allow-list.
- `.gitignore` — will not change (standards pages are git-tracked by default via the positive rule already covering `knowledge/wikis/**/wiki/**`).

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
1. Add `standards/` to the sanctioned page-type list across the three standards-touching wikis.
2. Define the frontmatter contract for `wiki/standards/*.md` pages.
3. Extend `pyramid-conformance-check.py` to accept the new path.
4. Extend `llm_wiki.py` lint to recognize the new page type.
5. Produce one sanctioned stub at `knowledge/wikis/marine-engineering/wiki/standards/csa-z276.md` to prove the schema end-to-end.
6. Not promote any other standards content — that is #2227's job, unblocked by this.

## Non-goals

- Will NOT promote CSA/OCIMF/DNV/API content into `wiki/standards/` at scale — that is deferred to #2227 and future content plans.
- Will NOT add `standards/` to non-standards wikis (maritime-law, personal, health-reports) — they can opt in later if relevant.
- Will NOT restructure `raw/standards/` — that directory already exists and is unaffected.
- Will NOT change cross-wiki link syntax or frontmatter for existing page types.

---

## Files to Change

| File | Change type | Why |
|---|---|---|
| `knowledge/wikis/marine-engineering/CLAUDE.md` | modify | Add `standards/` to sanctioned list + frontmatter schema |
| `knowledge/wikis/engineering/CLAUDE.md` | modify | Same |
| `knowledge/wikis/naval-architecture/CLAUDE.md` | modify | Same |
| `scripts/knowledge/pyramid-conformance-check.py` | modify | Add `standards/` to path allow-list |
| `scripts/knowledge/llm_wiki.py` | modify (conditional) | Add `standards/` to lint page-type enumeration if enumerated |
| `scripts/data/llm-wiki/resolve_wiki_path.py` | modify (conditional) | Add `standards/` to path allow-list if enumerated |
| `knowledge/wikis/marine-engineering/wiki/standards/csa-z276.md` | create | First sanctioned stub (frontmatter only + placeholder content) |
| `scripts/knowledge/tests/test_pyramid_conformance.py` | modify or create | Add test case covering `wiki/standards/<code>.md` accept path |
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

1. Read current `pyramid-conformance-check.py` to find the sanctioned-paths enumeration; verify exactly which constant/list to amend.
2. Amend `pyramid-conformance-check.py` first; add a unit test (`test_pyramid_conformance.py`) that asserts `wiki/standards/csa-z276.md` passes and `wiki/standards/` (empty) fails.
3. Amend the three wiki `CLAUDE.md` files in parallel with identical standards/ section insertions (preserve existing ordering).
4. Create the CSA Z276 stub page with full frontmatter and a minimal body ("This page will be populated by #2227. Placeholder exists to validate the schema contract.").
5. Run `uv run scripts/knowledge/pyramid-conformance-check.py` against the three wikis; expect clean exit.
6. Run `uv run scripts/knowledge/llm_wiki.py lint --wiki marine-engineering` (if such invocation exists) to confirm the new page type is recognized without warnings.
7. Update `docs/plans/README.md` to add the row.
8. Atomic commit per the standard plan-execution convention; push to a feature branch.

## TDD / Validation List

| Test | Passes when | Failure signal |
|---|---|---|
| Pyramid conformance accepts `wiki/standards/csa-z276.md` | exit 0 | exit non-zero with standards-path rejection |
| Pyramid conformance rejects empty `wiki/standards/` dir on other wikis that didn't opt in | unchanged behavior for non-amended wikis | inadvertent universal opt-in |
| Wiki lint accepts the CSA Z276 stub | clean lint summary | lint warns on frontmatter fields added by schema |
| Frontmatter schema applied to stub contains all required fields | YAML parse + required-field check passes | missing code_id / publisher / revision |
| `docs/plans/README.md` row exists | grep match on `2471` | row missing |

## Acceptance Criteria Alignment

- [x] sanctioned CSA durable destination is documented — via CLAUDE.md amendments
- [x] relevant wiki CLAUDE/schema guidance allows or rejects the destination explicitly — three CLAUDE.md files amended
- [x] gitignore/durability expectations are documented for the chosen path — via the frontmatter contract + existing positive .gitignore rule; no new ignore needed
- [x] #2227 can split OCIMF and CSA without unresolved routing ambiguity — CSA target path sanctioned; #2227 plan v2 will cite this plan

## Risk & Rollback

- Risk: amending three CLAUDE.md files in isolation could introduce drift if one amendment is phrased differently. Mitigation: same paragraph inserted in all three, verified by diff.
- Risk: pyramid-conformance-check edit could break existing CI. Mitigation: preserve existing passing tests; new test is additive.
- Rollback: single revert per atomic commit; stub page deletion is isolated.

## Downstream unblocks

- #2227 CSA portion can proceed against `knowledge/wikis/marine-engineering/wiki/standards/csa-z276.md`.
- Future standards coverage (API, OCIMF, DNV, ISO) has a sanctioned home.
