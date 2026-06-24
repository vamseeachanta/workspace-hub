# Session Handoff — Naval-Architecture Citation Flywheel (2026-06-22 → 2026-06-23)

## What this session did

Started from "add lessons: \<LinkedIn URL\>" and built it out, step by step, into a complete
calc-citation flywheel spanning three repos. Chain delivered end to end:

> external source (LinkedIn/blog) → `docs/lessons/` capture → wiki concept page →
> EN400 standards citation-target → cited `digitalmodel` calc output (provenance sidecar)

## Shipped & MERGED

### workspace-hub
- **PR #3228** — new `docs/lessons/` folder: 3 source-attributed practitioner captures
  (Campillo geomodeling, Schlömilch marine-analysis-timing, naval-architecture interview
  fundamentals) + README index + `YYYY-MM-DD-<slug>.md` convention.

### llm-wiki (private; `wikis/marine-engineering/`)
- **PR #781** — `concepts/naval-architecture-fundamentals.md` (coverage map, 5 clusters).
- **PR #782** — 4 deepen concept pages (ship-stability-gz-curve, ship-resistance-and-powering,
  hull-girder-strength, ship-seakeeping-and-motions) + index/log + fixed #781 orphan.
- **PR #786** — `standards/en400.md` citation-resolver target (code_id EN400 / USNA / Summer 2020).
- **PR #788** — EN400 Ch8 (Seakeeping) row + seakeeping cross_link.

### digitalmodel (`src/digitalmodel/naval_architecture/`, `citations/`)
- **PR #999** — `citations/registry.py: get_en400_reference()` + `fundamentals.py: mass_to_weight_cited()`
  (TDD pilot, opt-in by name, fail-closed, graceful standalone). 4 tests + vendored EN400 fixture.
- **PR #1003** — 4 more `*_cited` variants (buoyant_force, gz_from_cross_curves, ittc_1957_cf,
  natural_heave_period). 16 tests. Built via **4 parallel agents** over disjoint module+test pairs.
  Full citation+naval_architecture suite: **157 passed, 1 xfailed**.

**Net:** 5 foundational naval_architecture calcs now emit EN400 provenance sidecars resolving to the
wiki standards page, cross-linked to 6 concept pages.

## Repo states at exit
- **workspace-hub**: on `main`, no session files dirty. (Local `main` carries unrelated pre-existing
  noise from other processes — not from this session.)
- **llm-wiki**: on `main`, all 4 PRs merged; no session files dirty. NOTE: an unrelated parallel
  session has in-flight #762/#763 DNV-extraction work dirty in this checkout — **left untouched**.
- **digitalmodel**: on `main`, both PRs merged; no session files dirty. Pre-existing benchmark/chart
  `.png/.json` + `skills-catalog.json` are dirty from other sessions / test regen — **not committed**
  (all session commits were pathspec-scoped to exactly the intended files).
- All session feature branches deleted locally and on remote. No session worktrees remain.

## Open / follow-up (none blocking)
- **digitalmodel #1002** (filed this session) — Quality Gates is RED on `main` due to a **pre-existing**
  hardcoded `/mnt/local-analysis/worldenergydata` path in `marine_ops/vessel_db/wed_adapter.py`
  (L14 docstring, L52 functional). Not caused by this session's diffs. Fix = env/home-relative
  discovery (mirror `citations/resolver.py` precedence). Until fixed, every PR's Quality Gates shows
  this standing red — do not mistake it for a regression.
- **DRY follow-up** — the 5 near-identical citation try/except blocks across the `*_cited` functions
  could collapse into one `_emit_en400_citation` helper. Deferred to keep the parallel batch's files
  disjoint; safe to consolidate now in a single sequential PR.
- **Remaining deepen pages** — the 4 `(deepen)` concept pages exist; further per-concept worked-example
  pages (sourced from SNAME PNA Vols I–III at `/mnt/ace/docs/_standards/SNAME/`) are open.

## No external actions pending
No emails, Telegram, or external posts. All outputs are git PRs (merged) + GitHub issue #1002.

## Environment notes for the next agent
- **digitalmodel worktrees get clobbered/starved** on this box (8+ concurrent worktrees + autorun).
  Reliable fallback used here: work in the **primary checkout** on a feature branch, commit with
  **pathspec** (`git commit -- <files>`) to avoid sweeping other sessions' dirty files, push
  immediately (remote branch is immune to autorun `reset --hard`), then `git checkout main`.
- **llm-wiki worktrees were reliable** — used for all wiki PRs.
- Citation contract: `validate_citation` matches `code_id`/`publisher`/`revision` frontmatter
  EXACTLY; the cited page must be a **standards page** (concept pages carry no `code_id`). The
  `section` field is free-text (not validated). Test fixtures live under
  `tests/citations/fixtures/knowledge/wikis/<domain>/wiki/standards/`.
- Runner: `.venv/bin/python -m pytest` (not `uv run`).
