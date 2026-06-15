# Wikis moved to llm-wiki repo

As of **2026-05-05** the engineering domain wikis live at:

> **https://github.com/vamseeachanta/llm-wiki**

Only `personal/` remains under this directory — and only as a scaffold (`index.md` + `CLAUDE.md`); its entity pages were relocated per [#2835](https://github.com/vamseeachanta/workspace-hub/issues/2835). Wiki-health lint telemetry is now generated to `docs/reports/wiki-health/`, not under `knowledge/wikis/`.

## What moved

The 8 domain wikis previously under `knowledge/wikis/`:

- `mkt-a/`
- `asset-management/`
- `engineering/`
- `engineering-standards/`
- `lng-projects/`
- `marine-engineering/` (largest — 19k+ files)
- `maritime-law/`
- `naval-architecture/`
- `cross-links.md` (cross-domain link manifest)

…now live at `wikis/<domain>/` in the llm-wiki repo (link above). `tests/fixtures/llm-wiki/` and `knowledge/seeds/` also moved there.

## What stayed

- The corpus extraction **pipeline** stays in workspace-hub: `scripts/data/llm-wiki/`, `scripts/knowledge/llm_wiki.py`, `scripts/knowledge/` helpers, `.claude/skills/research/llm-wiki/`, `.claude/skills/coordination/llm-wiki-roadmap-integration/`, `.claude/state/llm-wiki-completeness-loop/`, `data/document-index/`.
- `personal/` remains here as a scaffold (entity pages relocated per #2835). Wiki-health reports are generated to `docs/reports/wiki-health/` (no longer under `knowledge/wikis/`).

## Why

Per the user-approved [llm-wiki spinout migration plan](../../worldenergydata/docs/plans/2026-05-05-llm-wiki-spinout-migration-plan.md) (in `vamseeachanta/worldenergydata`), and the override of [#2398](https://github.com/vamseeachanta/workspace-hub/issues/2398). The new repo is the canonical content storehouse; workspace-hub remains the orchestration hub that feeds it.

Vendor-derivative PDFs (DNV, API, ABS standards) were stripped to `/mnt/ace/llm-wiki-archive/` per workspace-hub PR [#2648](https://github.com/vamseeachanta/workspace-hub/pull/2648) BEFORE the public llm-wiki repo was initialized — never republished.

## Migration follow-ups (workspace-hub side)

- Update Python files in `scripts/`, `tests/` that still reference removed `knowledge/wikis/<domain>/` paths (tracked in a follow-up workspace-hub issue)
- Decide consumer pattern: clone-adjacent vs. git-submodule for the pipeline's wiki content access
