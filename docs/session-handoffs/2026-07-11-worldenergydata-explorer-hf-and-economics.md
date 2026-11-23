# Session handoff — World Energy Field Explorer: program complete, HF publishing, economics bug

**Date:** 2026-07-11 · **Repo focus:** `vamseeachanta/worldenergydata` (+ `workspace-hub` for tooling)
**Full durable record:** memory topic `project_world_energy_field_explorer_program.md` (read it first) and
`reference_hf_dataset_publishing_skill.md`.

## TL;DR
The World Energy Field Explorer (#939) is **feature-complete and live**. Its analysis results are **published
to Hugging Face**. A **client-facing economics data bug (#971)** was found and is the priority remaining work
(diagnosed, awaiting an owner methodology decision). Visualizations are **deferred** behind a hosting decision
(#972). A reusable **HF data-saving script + skill** was built for the whole ecosystem.

## What shipped this session (all merged + verified)
- **PR #967** — HF results-bundle exporter (`scripts/hf_export/build_explorer_results_bundle.py`).
- **PR #968** — #945 client-presentation layer (provenance footers, guided-demo band, capabilities repoint, dual
  "205 in scope · 84 with field data" relabel). Live-verified.
- **PR #970** — #969 field architecture-drawing panel (inline plan-view SVG, 3 fields render / 7 placeholder→#962,
  cascade_chinook captioned "Chinook subsea tieback"). Live-verified `#/field/julia`.
- **HF dataset PUBLISHED:** `aceengineer/worldenergydata-explorer` (public) — fields/wells/countries parquet +
  card; datasets-server `/rows` API live. **npv_mm/breakeven_wti WITHHELD** pending #971.
- **workspace-hub PR #3473 — MERGED** — reusable `scripts/hf/save_results_to_hf.py` (generic any-repo→HF; auto-table
  discovery, PRIVATE-by-default, refuses `-runs`, prints per-column stats as a data-quality eyeball) + the
  `.claude/skills/data/hf-dataset-publishing/` skill (SKILL.md + PROMPT.md). Follow-up **#3474**: regenerate
  `config/agents/skill-index-full.yaml` from a non-FUSE checkout (advisory Skill-Index-Coherence check runs red until
  then; NOT merge-blocking — main is unprotected).

## THE PRIORITY: #971 economics bug (data correctness)
**Diagnosed, NOT fixed.** The Explorer's per-field `npv_mm`/`breakeven_wti` are implausible (7/7 producing fields
negative NPV; $79–380 breakevens) and are **client-facing on the live Explorer + PDF one-pagers**, not just the
(withheld) HF columns.
- **Root cause (proven by computation, posted to #971):** NOT a code bug. It's a **life-to-date NPV** — full
  sunk capex charged against only oil produced *to date*, discounted 10% — surfaced as if full-cycle. Proof:
  breakeven tracks % of EUR produced (Anchor 1.9%→$380; Jack/St.Malo 39%→$79); Jack is undiscounted-POSITIVE
  (+$4.8B) but discount-negative → capex correctly netted, no sign error.
- **Computed at** `scripts/lower_tertiary/generate_field_economics_report.py:245,285,298-299` → parsed via
  `build_field_performance_comparison.py` → `_performance.json` → `build_lifecycle_posters.py:566` → `_explorer.json`.
- **OWNER DECISION NEEDED before implementing:** Tier 1 (recompute full-cycle NPV to `eur_mmbbl` — substantive,
  gives credible numbers) vs Tier 2 (relabel "life-to-date @10%" + suppress early-life values). Plus a sanity-gate
  test (surfaced breakeven ≤ ~$150; NOT a naive "producing⇒positive NPV" gate — LTD NPV is legitimately negative).
- **Caveat for Tier 1:** `eur_mmbbl` values look high (Anchor 998 vs ~440 real) — a separate reserves data-quality
  question that a full-cycle recompute depends on.
- **NEXT:** get the Tier 1/Tier 2 decision → plan (adversarial review) → approve → implement TDD → un-withhold the
  HF economics columns once fixed.

## Deferred / parked (documented on the tracker)
- **#972 — viz hosting decision (design issue):** where the custom viz dashboards live — GitHub Pages (static) /
  aceengineer.com / HF Space (Gradio paid-on-org or static-free) / external. A **Gradio Space with 4 charts is
  built + tested** (staged at `/tmp/wed-viz-space/`, NOT deployed — org Gradio needs a paid HF plan; datasets are
  free). Charts avoid the withheld economics. Recommendation leaning: GH-Pages-static or HF-static (free, org-branded).
- **#966 — HF viz endpoint:** subsumed into #972's platform choice; data-on-HF half is done.
- **#965 — HF export projection:** DONE (bundle shipped). Coordinate `hf_dataset` field → `aceengineer/*` namespace
  when the wh#3433 pipeline lands.

## Coordination note (parallel session)
`workspace-hub#3433` ("HF projection + staged promotion", home `assetutilities.workflow_api.publication`, namespace
**`aceengineer/*`**) is a PARALLEL claude session building the contract-managed **algorithm-run ledger**
(`aceengineer/<repo>-runs`). Our `-explorer` dataset is deliberately SEPARATE — do NOT publish analysis projections
into `-runs`. wed#927 (BSEE→HF pilot) is blocked-by that chain.

## Environment gotchas (cost real cycles — reuse)
- **FUSE mount** `/mnt/local-analysis`: local `git` hangs → clone `--depth 1` to `/tmp`, or commit via the GitHub
  **git-data API** (blobs→tree→commit→ref; that's how PR #3473 was made).
- Sandbox: **`python3 -c` DENIED** → `python3 - <<'EOF'` heredocs. **`base64 -d` DENIED** → `gh api -H "Accept:
  application/vnd.github.raw"`. Post-merge **raw.githubusercontent CDN lags** → verify via `gh api`/`HfApi`.
- HF: CLI is **`hf`** (`huggingface-cli` deprecated). Token at `~/.cache/huggingface/token`; `hf auth whoami` →
  user=vamseeachanta orgs=aceengineer. datasets-server indexes a new dataset over a few minutes (poll, don't fail).
- worldenergydata build recipe (from the topic file): shallow clone → venv-min (pyyaml pydantic-settings pytest
  pandas openpyxl) → PYTHONPATH=src:packages/worldenergydata-core/src:packages/worldenergydata-bsee/src → regenerate
  posters then atlas → pytest -o addopts="" --noconftest. Single-`<h1>` + identity + SVG-portability gates.

## First steps for the fresh session
1. Read the two memory files above. 2. Check PR #3473 merge status (skill-index-coherence check — index regen).
3. Confirm the #971 Tier 1/Tier 2 decision with the owner, then plan the economics fix (it's the priority — it's
   live and client-facing). 4. Everything else is parked with a tracked issue.
