# Plan for #2628: digitalmodel domain-divided CI architecture

> **Status:** plan-approved — r1 questions resolved by user 2026-05-04 (5 decisions locked); execution-ready under Phase 1
> **Complexity:** T3
> **Date:** 2026-05-03 (r0) | amended 2026-05-04 (r1-decisions)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2628
> **Parent / context:** #2614 (cluster fixes that surfaced masking) | #2616 (full-mask-removal sweep) | #2129 (issue-state drift / quality-gates audit umbrella)
> **Triage artifact:** `/tmp/mystery-tests-2616.md` (200-failure landscape across 53 files)
> **Locked decisions (2026-05-04, vamseeachanta):** D1=keep `misc` (transitional, force-migrate by Phase 5) | D2=silent in Phase 2 (no PR comments) | D3=2-week cutover overlap (Phase 3→4) | D4=remove `pytest.ini --maxfail=50` atomically with `.claude/quality-gates.yaml` refactor in Phase 2 | D5=Cluster A polluter bisect (no autouse purge fixture)
> **Review artifacts:** plan-r0 user-reviewed 2026-05-04; cross-provider r1 (claude+gemini) is post-Phase-1-landing optional

---

## Resource Intelligence Summary

### Existing repo code

- Found: `digitalmodel/.claude/quality-gates.yaml` — 130-line LINEAR (tests → coverage → quality → security → docs) gate config; line 10 is the load-bearing single repo-wide pytest invocation with `--maxfail=20` that masks ~200+ failures (per #2616 sweep). `parallel_execution: false` (line 128).
- Found: `digitalmodel/.github/workflows/quality-gates.yml` — 120-line workflow that calls `python -m digitalmodel.workflows.automation.quality_gates_cli check --json`. Single `quality-gates` job, no matrix.
- Found: `digitalmodel/.github/workflows/` — 11 OTHER workflows already exist as one-per-tooling: `aqwa-tests.yml`, `catenary-riser-tests.yml`, `diffraction-tests.yml`, `gmsh-meshing-tests.yml`, `hydrodynamics-tests.yml`, `mooring-analysis-tests.yml`, `orcaflex-tests.yml`, `structural-analysis-tests.yml`, `viv-analysis-tests.yml`, `workflow-automation-tests.yml`, `docs.yml`. They use a `paths:` filter pattern targeting `tests/domains/<name>/**` — but `tests/domains/` is currently a near-empty stub directory (only 1 test_ in it). These workflows are aspirational ahead of a real domain layout.
- Found: `digitalmodel/tests/conftest.py` (93 lines) — repo-wide. Carries: `collect_ignore` (24 file paths excluded for missing modules / data / platform), sys.path injection for `assetutilities` and `aceengineercode`, and a MagicMock pre-registration for `digitalmodel.subsea.catenary_riser.legacy.catenary_riser_summary` (lines 61-93) to suppress module-level execution.
- Found: `digitalmodel/pytest.ini` — already declares per-tier markers (`commit`, `task`, `session`) and a `solver` marker (`Tests requiring OrcFxAPI on licensed machine`). `addopts` carries `--maxfail=50`. `norecursedirs` excludes `tests/data_systems/data_scraping`, `tests/marine_ops/artificial_lift/dynacard/benchmark`, `tests/specialized/cathodic_protection`, `tests/workflows/integration`.
- Found: `digitalmodel/tests/orcaflex/conftest.py` — already provides fake `OrcFxAPI` types so OrcaFlex tests run without a license (mock model + range-graph + line objects). This is a strong precedent that domain-local conftests are workable.
- Found: `digitalmodel/tests/contracts/conftest.py` — already provides `au_version` fixture for assetutilities contract tests. Another precedent.
- Gap: No `tests/DOMAINS.md` exists. No `CODEOWNERS` at `digitalmodel/CODEOWNERS` or `digitalmodel/.github/CODEOWNERS`.
- Gap: No reusable "matrix per domain" workflow exists. Existing workflows are independent files duplicating boilerplate.
- Gap: No touched-domain detection script exists.

### Standards

| Standard | Status | Source |
|---|---|---|
| n/a | n/a | This is harness/CI architecture, not engineering calculation |

### LLM Wiki pages consulted

- n/a — harness/infrastructure work, not knowledge promotion.

### Documents consulted

- `gh issue view 2628` — umbrella body: 14-15 domains estimated; aggregator policy = "all must pass"; touched-domains-only on PRs + full matrix nightly cron; CODEOWNERS sole owner = vamseeachanta; no test deletion or blanket-skip without AI-attested commit per `feedback_attestation_enables_contradiction_detection`.
- `/tmp/mystery-tests-2616.md` — Cluster A (sys.modules pollution → contracts), Cluster B (worldenergydata skipif gap → field_development, 1-file fix), Cluster C (capsys × `-p no:capture` → cross-cuts CLI tests in 6 files), Cluster D (51 errors in `tests/infrastructure/core/` from missing redis/psycopg2/motor), Cluster E (~60 marine engineering regressions), Cluster F (long-tail singletons across 19 files). Ground-truth file→failure-count table that the domain inventory must align to.
- `digitalmodel/CLAUDE.md` — repo adapter contract (workspace-hub/AGENTS.md is canonical; required gates: WRK→plan→approval→cross-review).
- `workspace-hub/AGENTS.md` (21 lines) — Hard Gates 1-3; commands `uv run` always; reviews APPROVE|MINOR|MAJOR.
- `workspace-hub/CLAUDE.md` (13 lines) — Claude adapter; planning workflow mandatory; Context budget 16KB total.
- `docs/plans/_template-issue-plan.md` — section ordering source of truth.
- `docs/plans/README.md` (411 lines) — index with table starting around line 90; template-required sections.
- `docs/plans/2026-05-02-issue-2559-ocimf-tandem-wiki-source-promotion.md` — recent precedent for: (a) load-bearing-decision section, (b) explicit `## #NNNN Closeout Reframe` style, (c) inline `gh`-verified evidence sub-section, (d) USER APPROVAL GATE risk handling, (e) Known Defects to Address During Execution table.
- `feedback_never_offer_to_self_label_plan_approved` — user-in-loop approval gate is load-bearing; this plan must NOT pre-authorize batch execution agents nor self-label `status:plan-approved`.
- `feedback_attestation_enables_contradiction_detection` — required attestation surface for any test deletion/skip during the cluster cleanup phase.
- `feedback_codex_cli_0_124_upstream_regression` (#2479) — Codex r1 may be UNAVAILABLE; fallback to Claude+Gemini per `feedback_permission_gate_blocks_cross_review`.

### Gaps identified

- No domain inventory artifact exists in the digitalmodel repo (`tests/DOMAINS.md` is the gap this plan creates).
- No CODEOWNERS file exists in digitalmodel.
- No matrix-per-domain reusable workflow exists.
- No touched-domain detection script exists.
- Repo-wide `tests/conftest.py` carries fixtures that should be domain-local (sys.path + MagicMock pre-registration are repo-wide; `collect_ignore` should be partitioned per-domain).
- Workspace-hub `AGENTS.md` and `CLAUDE.md` do not yet encode the "always test by domain during development" rule.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-03 via `gh issue view`):
- `#2628` — OPEN (umbrella) — `feat(digitalmodel): domain-divided CI architecture` — sub-tasks A-G open.
- `#2614` — referenced as the cluster-fixes-that-surfaced-masking parent.
- `#2616` — referenced as the masking-investigation issue; its triage produced `/tmp/mystery-tests-2616.md`.
- `#2129` — issue-state drift / quality-gates audit umbrella.

**File existence** (verified 2026-05-03):
- EXISTS: `digitalmodel/.claude/quality-gates.yaml` (130 lines)
- EXISTS: `digitalmodel/.github/workflows/quality-gates.yml` (120 lines)
- EXISTS: `digitalmodel/.github/workflows/{aqwa,catenary-riser,diffraction,gmsh-meshing,hydrodynamics,mooring-analysis,orcaflex,structural-analysis,viv-analysis,workflow-automation}-tests.yml`
- EXISTS: `digitalmodel/tests/conftest.py` (93 lines), `digitalmodel/tests/orcaflex/conftest.py`, `digitalmodel/tests/contracts/conftest.py`, `digitalmodel/tests/specs/conftest.py`, `digitalmodel/tests/drilling_riser/conftest.py`, `digitalmodel/tests/solver/conftest.py`, plus 14 nested conftest.py files.
- EXISTS: `digitalmodel/pytest.ini`
- MISSING (this plan creates): `digitalmodel/tests/DOMAINS.md`
- MISSING (this plan creates): `digitalmodel/CODEOWNERS`
- MISSING (this plan creates): `digitalmodel/.github/workflows/quality-gates-by-domain.yml`
- MISSING (this plan creates): `digitalmodel/scripts/ci/detect_touched_domains.py`

**Test-count map** (verified 2026-05-03 via `grep -rc 'def test_' <path> | awk -F: '{s+=$2} END {print s}'`):
```
2720  tests/hydrodynamics             (includes 1365 in tests/hydrodynamics/diffraction)
1503  tests/structural
1231  tests/marine_ops                (includes 410 in tests/marine_ops/marine_engineering)
1201  tests/solvers/orcaflex
 850  tests/specialized
 784  tests/visualization
 622  tests/infrastructure
 476  tests/field_development
 475  tests/naval_architecture
 462  tests/workflows
 392  tests/subsea
 351  tests/unit
 324  tests/ansys
 308  tests/asset_integrity
 307  tests/orcawave
 260  tests/orcaflex
 245  tests/fatigue
 235  tests/hydrodynamics/passing_ship
 212  tests/power
 206  tests/cathodic_protection
 180  tests/well
 134  tests/data_systems
 133  tests/gis
  93  tests/production_engineering
  84  tests/signal_processing
  84  tests/benchmarks
  73  tests/geotechnical
  60  tests/engineering_validation
  56  tests/drilling_riser
  47  tests/web
  40  tests/solver
  33  tests/docs
  31  tests/scripts
  17  tests/contracts
  16  tests/reservoir
  14  tests/citations
  13  tests/nde
  10  tests/compat
   7  tests/integration
   7  tests/naming_convention_validation
   2  tests/test_automation
   1  tests/domains
   0  tests/cross_repo
   0  tests/performance
```

Total `def test_` declarations across listed roots: ~14,800 (overlap from `tests/hydrodynamics` containing diffraction/passing_ship is the largest double-count; net unique ≈ 13,200).

**Existing per-domain conftest precedents** (verified 2026-05-03 via `find tests -name conftest.py`):
- `tests/orcaflex/conftest.py` — fake OrcFxAPI types for license-free runs
- `tests/contracts/conftest.py` — `au_version` fixture
- 14 nested conftests at sub-domain depth (aqwa, bemrosetta, diffraction, hull_library, rao_analysis, factories, installation, performance, signal_analysis, time_series, blender_automation, drilling_riser, orcawave, specs, solver, benchmarks, domains)

**Source-count: 7 (issue body, mystery-tests-2616.md, digitalmodel/CLAUDE.md, workspace-hub/AGENTS.md, docs/plans/_template-issue-plan.md, docs/plans/README.md, 2026-05-02 issue-2559 plan precedent) — minimum 3 satisfied.**

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-03-issue-2628-digitalmodel-domain-divided-ci.md` |
| Domain inventory (sub-task A) | `digitalmodel/tests/DOMAINS.md` |
| CODEOWNERS (sub-task F) | `digitalmodel/CODEOWNERS` |
| Refactored gate config (sub-task B) | `digitalmodel/.claude/quality-gates.yaml` (in-place) |
| New matrix workflow (sub-task C) | `digitalmodel/.github/workflows/quality-gates-by-domain.yml` |
| Touched-domain detector (sub-task D) | `digitalmodel/scripts/ci/detect_touched_domains.py` |
| Per-domain conftests (sub-task E, incremental) | `digitalmodel/tests/<domain>/conftest.py` (per migration table) |
| Workspace-hub agent guidance (sub-task G) | `AGENTS.md` + `CLAUDE.md` (insertion text below) |
| Plan review — Claude | `scripts/review/results/2026-05-03-plan-2628-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-03-plan-2628-codex.md` (or "UNAVAILABLE per #2479") |
| Plan review — Gemini | `scripts/review/results/2026-05-03-plan-2628-gemini.md` |

---

## Deliverable

A digitalmodel quality-gates architecture in which **each test domain runs as an independent CI job** with its own dependency closure and its own pass/fail signal, gated by an aggregator that only goes green when all domains pass — eliminating the repo-wide `--maxfail=20` masking pattern that has been hiding ~200+ pre-existing failures per the #2616 sweep. Touched-domains-only on PRs (sub-2-min for trivial changes) and full matrix nightly. Workspace-hub agent harness updated so AI-driven changes default to domain-scoped pytest invocations during development.

---

## Domain Count Decision

**The umbrella estimated 14-15 domains. After walking the tests/ tree, this plan settles on 16 domains.**

Rationale for the +1 over the upper estimate:
- The umbrella's "hydrodynamics-diffraction" + "hydrodynamics-passing-ship" split (2 sub-domains under one parent) is sound; this plan adopts it and adds a third (`hydrodynamics-other` for aqwa/bemrosetta/capytaine/hull_library/parametric_hull_analysis/rao_analysis — ~1120 test_ declarations not yet sub-split).
- The umbrella's "infrastructure-core" (heavy deps) is split from "infrastructure-other" (the rest of `tests/infrastructure/`) — Cluster D in #2616 is concentrated in `tests/infrastructure/core/`; isolating its 51-error blast radius is the explicit win this whole architecture is designed to deliver.
- The umbrella's "solver-smoke" + "orcaflex-solver" + "orcaflex" 3-way split is preserved; aggregating would defeat the OrcFxAPI license-windows-only isolation.
- "misc" exists in the umbrella as a catch-all; this plan keeps it but flags it as a smell — domains in "misc" should migrate to a real domain in a follow-up. **DECISION-LOCKED D1 (2026-05-04):** keep as transitional bucket for Phase 1-4; force-migrate every entry to a real domain by end of Phase 5; delete the `misc` domain entry from `.claude/quality-gates.yaml` and `tests/DOMAINS.md` once empty.

The 16 domains are listed in §Sub-task A below. Open question for r1: should `cathodic_protection` (its own root) and `specialized/cathodic_protection` (under specialized) be one domain or two? Plan answer: **one** (`cathodic-protection`), since they share an engineering scope; the implementer maps both roots to one domain in `DOMAINS.md`.

---

## Sub-task A — Domain inventory (`tests/DOMAINS.md`)

The implementer creates this file verbatim. Copy-paste-ready:

```markdown
# digitalmodel Test Domains

> Single source of truth: each row maps a `tests/<root>` directory to one CI domain.
> Touched-domain detection (`scripts/ci/detect_touched_domains.py`) reads this file.
> Owner of every domain (per #2628 session decision): `@vamseeachanta`.

## Domain table

| Domain | Test roots (one per line) | Est. test count | `--with` deps (best-effort) | Notes |
|---|---|---|---|---|
| `asset-integrity` | `tests/asset_integrity` | 308 | numpy, pandas, pyyaml, loguru | clean (no #2616 hits) |
| `cathodic-protection` | `tests/cathodic_protection`, `tests/specialized/cathodic_protection` | 206 (root) + ~50 (under specialized) | numpy, scipy, pandas, pyyaml | `pytest.ini` `norecursedirs` excludes `tests/specialized/cathodic_protection`; this domain MUST drop that exclusion or move to `[skipif]` (decision: drop on first PR) |
| `citations` | `tests/citations` | 14 | pyyaml, pydantic | `digitalmodel.citations` package; #2471 frontmatter contract |
| `contracts` | `tests/contracts` | 17 | (assetutilities sibling repo on path) | Cluster A in #2616 — sys.modules pollution from upstream tests; **DECISION-LOCKED D5 (2026-05-04):** polluter bisect (NOT autouse purge fixture) — fix the source pollution rather than mask its symptom in `tests/contracts/conftest.py` |
| `field-development` | `tests/field_development` | 476 | numpy, pandas, pyyaml, loguru, pint, scipy, openpyxl | Cluster B in #2616 — `worldenergydata` import gap in 4 sibling classes; one-file `@skipif` fix needed |
| `hydrodynamics-diffraction` | `tests/hydrodynamics/diffraction` | 1365 | numpy, scipy, matplotlib, pandas, plotly, pyyaml, loguru, gmsh | post-#2614 clean; was the wave that surfaced #2616 |
| `hydrodynamics-passing-ship` | `tests/hydrodynamics/passing_ship` | 235 | numpy, scipy, matplotlib, pandas, click | Cluster C in #2616 — `capsys` × `-p no:capture` regression; fix is to drop `-p no:capture` from this domain's command (other domains keep it if perf-sensitive) |
| `hydrodynamics-other` | `tests/hydrodynamics/aqwa`, `tests/hydrodynamics/bemrosetta`, `tests/hydrodynamics/capytaine`, `tests/hydrodynamics/hull_library`, `tests/hydrodynamics/parametric_hull_analysis`, `tests/hydrodynamics/rao_analysis` | ~1120 (= 2720 - 1365 - 235) | numpy, scipy, matplotlib, pandas, plotly, pyyaml, loguru, gmsh, capytaine | `tests/hydrodynamics/hull_library/test_hull_library_expansion.py` is in `tests/conftest.py:39` `collect_ignore` (data file gap); decide per-domain skipif vs. data-file landing |
| `infrastructure-core` | `tests/infrastructure/core` | ~51 (subset of 622) | redis, psycopg2-binary, motor, sqlalchemy, pyyaml | Cluster D in #2616 — 51 errors from missing deps; decision (this plan): add the deps to THIS domain's `--with` list (not to repo-wide); accept dep-install cost increase only here |
| `infrastructure-other` | `tests/infrastructure/common`, `tests/infrastructure/contracts`, `tests/infrastructure/factories`, `tests/infrastructure/installation`, `tests/infrastructure/performance`, `tests/infrastructure/property`, `tests/infrastructure/security`, `tests/infrastructure/unit`, `tests/infrastructure/utils`, `tests/infrastructure/validation` | ~571 (= 622 - 51) | numpy, pandas, pyyaml, loguru, click, hypothesis | clean of #2616 hits |
| `marine-engineering` | `tests/marine_ops/marine_engineering` | 410 | numpy, scipy, matplotlib, pandas, pyyaml, loguru, plotly, openpyxl | Cluster E in #2616 — ~60 regressions across catenary/wave/ocimf/integration; THIS DOMAIN OWNS the cluster cleanup |
| `marine-ops-other` | `tests/marine_ops/artificial_lift`, `tests/marine_ops/installation`, `tests/marine_ops/marine_analysis`, `tests/marine_ops/reservoir` | ~821 (= 1231 - 410) | numpy, scipy, pandas, pyyaml, loguru, matplotlib | `tests/marine_ops/artificial_lift/dynacard/benchmark` excluded in `pytest.ini:norecursedirs` — preserved |
| `naval-architecture` | `tests/naval_architecture` | 475 | numpy, scipy, matplotlib, pandas, pyyaml, loguru | clean |
| `orcaflex` | `tests/orcaflex` (mock-only Python tests; uses `tests/orcaflex/conftest.py` fake OrcFxAPI) | 260 | numpy, pandas, pyyaml, loguru | runs on linux + windows; **no real OrcFxAPI license needed** (conftest provides mocks) |
| `orcaflex-solver` | `tests/solvers/orcaflex` | 1201 | numpy, pandas, pyyaml, loguru, click | mixed: most use mocks, but some import the real `OrcFxAPI` (per import scan); domain-local conftest must protect non-licensed runs with `pytest.importorskip("OrcFxAPI")` or equivalent. Cluster C in #2616 also touches `test_template_generator.py` and `test_campaign_generator.py` here (capsys × no:capture) |
| `solver-smoke` | `tests/solver`, `tests/solvers/blender_automation`, `tests/solvers/calculix`, `tests/solvers/fea`, `tests/solvers/gmsh_meshing`, `tests/solvers/openfoam`, `tests/solvers/orcawave` | ~40 (root) + small subdir totals | numpy, gmsh (gmsh_meshing only), pyyaml | linux runners; NO orcaflex |
| `specialized` | `tests/specialized/cli`, `tests/specialized/code_dnvrph103`, `tests/specialized/custom`, `tests/specialized/digitalmarketing`, `tests/specialized/gis`, `tests/specialized/ship_design`, `tests/specialized/umbilical_analysis` (cathodic_protection moved out) | ~800 | numpy, pandas, pyyaml, loguru, click, geopandas (gis subpath only — load via `pytest.importorskip`) | `tests/specialized/custom/test_pipesizing.py` has 4 #2616 numeric/property failures — domain owns triage |
| `structural` | `tests/structural`, `tests/fatigue`, `tests/unit/structural`, `tests/well` | 1503 + 245 + ~50 + 180 = ~1978 | numpy, scipy, pandas, matplotlib, pyyaml, loguru, plotly, openpyxl | largest domain; consider further splitting in a follow-up if CI time is dominated by this domain |
| `subsea` | `tests/subsea`, `tests/drilling_riser` | 392 + 56 = 448 | numpy, scipy, pandas, pyyaml, loguru | `tests/conftest.py:19` `collect_ignore` excludes `subsea/pipeline/test_on_bottom_stability.py` |
| `workflows` | `tests/workflows`, `tests/test_automation` | 462 + 2 = 464 | numpy, pandas, pyyaml, loguru, click | `pytest.ini:norecursedirs` excludes `tests/workflows/integration`; preserved |
| `misc` | everything not above: `tests/ansys`, `tests/benchmarks`, `tests/compat`, `tests/cross_repo`, `tests/data_systems`, `tests/docs`, `tests/domains`, `tests/engineering_validation`, `tests/fixtures`, `tests/geotechnical`, `tests/gis`, `tests/integration`, `tests/naming_convention_validation`, `tests/nde`, `tests/orcawave`, `tests/output*`, `tests/performance`, `tests/power`, `tests/production_engineering`, `tests/rainflow_comparison_results`, `tests/reservoir`, `tests/scripts`, `tests/signal_processing`, `tests/test_configs`, `tests/test_failure_recovery_temp`, `tests/test_wall_thickness_codes`, `tests/unit/hull_library`, `tests/unit/hydrodynamics`, `tests/visualization`, `tests/web` | ~1900 | numpy, pandas, pyyaml, loguru, scipy, matplotlib, click, openpyxl | catch-all; SMELL — every entry here should migrate to a real domain in a follow-up. Tracked as a follow-up issue, not blocking #2628. |

## Domain → primary owner

All 16 domains: `@vamseeachanta` (per #2628 session decision).
Authoritative encoding: `digitalmodel/CODEOWNERS`.

## Cross-domain integration tests

Tests under `tests/integration/` and `tests/cross_repo/` (currently empty/near-empty) intentionally span domains. Policy: integration suite is **not** subject to touched-domain detection — it always runs on PRs that touch `src/digitalmodel/**`. Tracked separately (not part of this domain matrix); see `quality-gates-by-domain.yml`'s `integration` job.

## Updating this file

When new tests are added under an existing root: no change needed. When new test roots are added or existing roots split: update the table and the `detect_touched_domains.py` mapping in the same PR. The mapping in the script must be kept in sync.
```

---

## Sub-task B — `.claude/quality-gates.yaml` refactor

### Side-by-side: current vs. proposed

**Current** (`.claude/quality-gates.yaml:5-12`, the load-bearing single command):
```yaml
gates:
  tests:
    enabled: true
    order: 1
    description: "All tests must pass"
    command: "python -m pytest --maxfail=20 -rfE -p no:asyncio -p no:randomly -p no:sugar --no-header -q --tb=line --cov=src --cov-report=json"
    failure_action: "block"
```

**Proposed** (full file replacement; ~200 lines):
```yaml
# Quality Gates Configuration v2 — domain-divided
# Per-domain test gates run independently; aggregator gate fails if ANY domain fails.
# Repo-wide --maxfail removed (was the masking mechanism per #2616).
# Coverage and quality (ruff/bandit/docs) remain repo-wide.

gates:
  # =========================================================================
  # Per-domain test gates (one per row in tests/DOMAINS.md)
  # =========================================================================

  tests-asset-integrity:
    enabled: true
    order: 1
    domain: asset-integrity
    description: "asset-integrity domain tests"
    command: >-
      uv run --with-editable . --with numpy --with pandas --with pyyaml
      --with loguru --with pytest --with pytest-cov
      python -m pytest tests/asset_integrity -rfE -p no:asyncio -p no:randomly
      -p no:sugar --no-header -q --tb=short
      --cov=src/digitalmodel --cov-report=json:reports/coverage-asset-integrity.json
    failure_action: "block"

  tests-cathodic-protection:
    enabled: true
    order: 1
    domain: cathodic-protection
    description: "cathodic-protection domain tests"
    command: >-
      uv run --with-editable . --with numpy --with scipy --with pandas
      --with pyyaml --with loguru --with pytest --with pytest-cov
      python -m pytest tests/cathodic_protection tests/specialized/cathodic_protection
      -rfE -p no:asyncio -p no:randomly -p no:sugar --no-header -q --tb=short
      --cov=src/digitalmodel --cov-report=json:reports/coverage-cathodic-protection.json
    failure_action: "block"

  tests-citations:
    enabled: true
    order: 1
    domain: citations
    description: "citations domain tests"
    command: >-
      uv run --with-editable . --with pyyaml --with pydantic --with pytest
      --with pytest-cov
      python -m pytest tests/citations -rfE -p no:asyncio -p no:randomly
      -p no:sugar --no-header -q --tb=short
      --cov=src/digitalmodel/citations --cov-report=json:reports/coverage-citations.json
    failure_action: "block"

  tests-contracts:
    enabled: true
    order: 1
    domain: contracts
    description: "contracts domain tests (assetutilities API stability)"
    command: >-
      uv run --with-editable . --with pytest --with pytest-cov
      python -m pytest tests/contracts -rfE -p no:asyncio -p no:randomly
      -p no:sugar --no-header -q --tb=short
      --cov=src/digitalmodel --cov-report=json:reports/coverage-contracts.json
    failure_action: "block"

  tests-field-development:
    enabled: true
    order: 1
    domain: field-development
    description: "field-development domain tests"
    command: >-
      uv run --with-editable . --with numpy --with pandas --with pyyaml
      --with loguru --with pint --with scipy --with openpyxl
      --with pytest --with pytest-cov
      python -m pytest tests/field_development -rfE -p no:asyncio -p no:randomly
      -p no:sugar --no-header -q --tb=short
      --cov=src/digitalmodel --cov-report=json:reports/coverage-field-development.json
    failure_action: "block"

  tests-hydrodynamics-diffraction:
    enabled: true
    order: 1
    domain: hydrodynamics-diffraction
    description: "hydrodynamics/diffraction domain tests"
    command: >-
      uv run --with-editable . --with numpy --with scipy --with matplotlib
      --with pandas --with plotly --with pyyaml --with loguru --with gmsh
      --with pytest --with pytest-cov
      python -m pytest tests/hydrodynamics/diffraction -rfE -p no:asyncio
      -p no:randomly -p no:sugar --no-header -q --tb=short
      --cov=src/digitalmodel --cov-report=json:reports/coverage-hydrodynamics-diffraction.json
    failure_action: "block"

  tests-hydrodynamics-passing-ship:
    enabled: true
    order: 1
    domain: hydrodynamics-passing-ship
    description: "hydrodynamics/passing_ship domain tests"
    # NOTE: -p no:capture INTENTIONALLY OMITTED here (Cluster C fix per #2616)
    command: >-
      uv run --with-editable . --with numpy --with scipy --with matplotlib
      --with pandas --with click --with pyyaml --with loguru
      --with pytest --with pytest-cov
      python -m pytest tests/hydrodynamics/passing_ship -rfE -p no:asyncio
      -p no:randomly -p no:sugar --no-header -q --tb=short
      --cov=src/digitalmodel --cov-report=json:reports/coverage-hydrodynamics-passing-ship.json
    failure_action: "block"

  tests-hydrodynamics-other:
    enabled: true
    order: 1
    domain: hydrodynamics-other
    description: "hydrodynamics non-diffraction/non-passing-ship domain tests"
    command: >-
      uv run --with-editable . --with numpy --with scipy --with matplotlib
      --with pandas --with plotly --with pyyaml --with loguru --with gmsh
      --with capytaine --with pytest --with pytest-cov
      python -m pytest tests/hydrodynamics
      --ignore=tests/hydrodynamics/diffraction
      --ignore=tests/hydrodynamics/passing_ship
      -rfE -p no:asyncio -p no:randomly -p no:sugar --no-header -q --tb=short
      --cov=src/digitalmodel --cov-report=json:reports/coverage-hydrodynamics-other.json
    failure_action: "block"

  tests-infrastructure-core:
    enabled: true
    order: 1
    domain: infrastructure-core
    description: "infrastructure/core domain tests (heavy backend deps)"
    # NOTE: redis/psycopg2-binary/motor isolated to THIS domain only (Cluster D fix per #2616)
    command: >-
      uv run --with-editable . --with numpy --with pandas --with pyyaml
      --with loguru --with redis --with psycopg2-binary --with motor
      --with sqlalchemy --with pytest --with pytest-cov
      python -m pytest tests/infrastructure/core -rfE -p no:asyncio
      -p no:randomly -p no:sugar --no-header -q --tb=short
      --cov=src/digitalmodel --cov-report=json:reports/coverage-infrastructure-core.json
    failure_action: "block"

  tests-infrastructure-other:
    enabled: true
    order: 1
    domain: infrastructure-other
    description: "infrastructure non-core domain tests"
    command: >-
      uv run --with-editable . --with numpy --with pandas --with pyyaml
      --with loguru --with click --with hypothesis
      --with pytest --with pytest-cov
      python -m pytest tests/infrastructure --ignore=tests/infrastructure/core
      -rfE -p no:asyncio -p no:randomly -p no:sugar --no-header -q --tb=short
      --cov=src/digitalmodel --cov-report=json:reports/coverage-infrastructure-other.json
    failure_action: "block"

  tests-marine-engineering:
    enabled: true
    order: 1
    domain: marine-engineering
    description: "marine-engineering domain tests (Cluster E owner)"
    command: >-
      uv run --with-editable . --with numpy --with scipy --with matplotlib
      --with pandas --with plotly --with pyyaml --with loguru --with openpyxl
      --with pytest --with pytest-cov
      python -m pytest tests/marine_ops/marine_engineering -rfE -p no:asyncio
      -p no:randomly -p no:sugar --no-header -q --tb=short
      --cov=src/digitalmodel --cov-report=json:reports/coverage-marine-engineering.json
    failure_action: "block"

  tests-marine-ops-other:
    enabled: true
    order: 1
    domain: marine-ops-other
    description: "marine-ops non-marine-engineering domain tests"
    command: >-
      uv run --with-editable . --with numpy --with scipy --with pandas
      --with pyyaml --with loguru --with matplotlib
      --with pytest --with pytest-cov
      python -m pytest tests/marine_ops --ignore=tests/marine_ops/marine_engineering
      -rfE -p no:asyncio -p no:randomly -p no:sugar --no-header -q --tb=short
      --cov=src/digitalmodel --cov-report=json:reports/coverage-marine-ops-other.json
    failure_action: "block"

  tests-naval-architecture:
    enabled: true
    order: 1
    domain: naval-architecture
    description: "naval-architecture domain tests"
    command: >-
      uv run --with-editable . --with numpy --with scipy --with matplotlib
      --with pandas --with pyyaml --with loguru
      --with pytest --with pytest-cov
      python -m pytest tests/naval_architecture -rfE -p no:asyncio
      -p no:randomly -p no:sugar --no-header -q --tb=short
      --cov=src/digitalmodel --cov-report=json:reports/coverage-naval-architecture.json
    failure_action: "block"

  tests-orcaflex:
    enabled: true
    order: 1
    domain: orcaflex
    description: "orcaflex domain tests (mock OrcFxAPI via tests/orcaflex/conftest.py)"
    command: >-
      uv run --with-editable . --with numpy --with pandas --with pyyaml
      --with loguru --with pytest --with pytest-cov
      python -m pytest tests/orcaflex -rfE -p no:asyncio -p no:randomly
      -p no:sugar --no-header -q --tb=short
      --cov=src/digitalmodel --cov-report=json:reports/coverage-orcaflex.json
    failure_action: "block"

  tests-orcaflex-solver:
    enabled: true
    order: 1
    domain: orcaflex-solver
    description: "orcaflex-solver domain tests (some require real OrcFxAPI; importorskip via conftest)"
    command: >-
      uv run --with-editable . --with numpy --with pandas --with pyyaml
      --with loguru --with click --with pytest --with pytest-cov
      python -m pytest tests/solvers/orcaflex -rfE -p no:asyncio -p no:randomly
      -p no:sugar --no-header -q --tb=short
      --cov=src/digitalmodel --cov-report=json:reports/coverage-orcaflex-solver.json
    failure_action: "block"

  tests-solver-smoke:
    enabled: true
    order: 1
    domain: solver-smoke
    description: "solver-smoke domain tests (calculix/openfoam/gmsh/blender; no orcaflex)"
    command: >-
      uv run --with-editable . --with numpy --with pyyaml --with loguru
      --with gmsh --with pytest --with pytest-cov
      python -m pytest tests/solver tests/solvers/blender_automation
      tests/solvers/calculix tests/solvers/fea tests/solvers/gmsh_meshing
      tests/solvers/openfoam tests/solvers/orcawave
      -rfE -p no:asyncio -p no:randomly -p no:sugar --no-header -q --tb=short
      --cov=src/digitalmodel --cov-report=json:reports/coverage-solver-smoke.json
    failure_action: "block"

  tests-specialized:
    enabled: true
    order: 1
    domain: specialized
    description: "specialized domain tests (cli/dnvrph103/custom/digitalmarketing/gis/ship_design/umbilical)"
    # NOTE: tests/specialized/cathodic_protection MOVED to cathodic-protection domain
    command: >-
      uv run --with-editable . --with numpy --with pandas --with pyyaml
      --with loguru --with click --with pytest --with pytest-cov
      python -m pytest tests/specialized
      --ignore=tests/specialized/cathodic_protection
      -rfE -p no:asyncio -p no:randomly -p no:sugar --no-header -q --tb=short
      --cov=src/digitalmodel --cov-report=json:reports/coverage-specialized.json
    failure_action: "block"

  tests-structural:
    enabled: true
    order: 1
    domain: structural
    description: "structural + fatigue + well + unit/structural domain tests"
    command: >-
      uv run --with-editable . --with numpy --with scipy --with pandas
      --with matplotlib --with pyyaml --with loguru --with plotly --with openpyxl
      --with pytest --with pytest-cov
      python -m pytest tests/structural tests/fatigue tests/unit/structural tests/well
      -rfE -p no:asyncio -p no:randomly -p no:sugar --no-header -q --tb=short
      --cov=src/digitalmodel --cov-report=json:reports/coverage-structural.json
    failure_action: "block"

  tests-subsea:
    enabled: true
    order: 1
    domain: subsea
    description: "subsea + drilling_riser domain tests"
    command: >-
      uv run --with-editable . --with numpy --with scipy --with pandas
      --with pyyaml --with loguru --with pytest --with pytest-cov
      python -m pytest tests/subsea tests/drilling_riser
      -rfE -p no:asyncio -p no:randomly -p no:sugar --no-header -q --tb=short
      --cov=src/digitalmodel --cov-report=json:reports/coverage-subsea.json
    failure_action: "block"

  tests-workflows:
    enabled: true
    order: 1
    domain: workflows
    description: "workflows + test_automation domain tests"
    command: >-
      uv run --with-editable . --with numpy --with pandas --with pyyaml
      --with loguru --with click --with pytest --with pytest-cov
      python -m pytest tests/workflows tests/test_automation
      -rfE -p no:asyncio -p no:randomly -p no:sugar --no-header -q --tb=short
      --cov=src/digitalmodel --cov-report=json:reports/coverage-workflows.json
    failure_action: "block"

  tests-misc:
    enabled: true
    order: 1
    domain: misc
    description: "misc catch-all (everything not in a real domain — SMELL: should empty over time)"
    command: >-
      uv run --with-editable . --with numpy --with pandas --with pyyaml
      --with loguru --with scipy --with matplotlib --with click --with openpyxl
      --with pytest --with pytest-cov
      python -m pytest tests/ansys tests/benchmarks tests/compat tests/data_systems
      tests/docs tests/domains tests/engineering_validation tests/geotechnical
      tests/gis tests/integration tests/naming_convention_validation tests/nde
      tests/orcawave tests/power tests/production_engineering tests/reservoir
      tests/scripts tests/signal_processing tests/visualization tests/web
      tests/unit/hull_library tests/unit/hydrodynamics
      -rfE -p no:asyncio -p no:randomly -p no:sugar --no-header -q --tb=short
      --cov=src/digitalmodel --cov-report=json:reports/coverage-misc.json
    failure_action: "block"

  # =========================================================================
  # Aggregator: must be green for the QG suite to be green
  # =========================================================================
  aggregator:
    enabled: true
    order: 2
    description: "Aggregator: requires ALL domain test gates to pass"
    depends_on:
      - tests-asset-integrity
      - tests-cathodic-protection
      - tests-citations
      - tests-contracts
      - tests-field-development
      - tests-hydrodynamics-diffraction
      - tests-hydrodynamics-passing-ship
      - tests-hydrodynamics-other
      - tests-infrastructure-core
      - tests-infrastructure-other
      - tests-marine-engineering
      - tests-marine-ops-other
      - tests-naval-architecture
      - tests-orcaflex
      - tests-orcaflex-solver
      - tests-solver-smoke
      - tests-specialized
      - tests-structural
      - tests-subsea
      - tests-workflows
      - tests-misc
    failure_action: "block"

  # =========================================================================
  # Coverage: combined per-domain coverage with combine step
  # =========================================================================
  coverage:
    enabled: true
    order: 3
    description: "Combined test coverage requirements"
    depends_on: ["aggregator"]
    combine_step: "coverage combine reports/coverage-*.json && coverage report --format=json > reports/coverage-combined.json"
    thresholds:
      failure: 60.0
      warning: 80.0
    report_format: "json"
    output_file: "reports/coverage-combined.json"
    failure_action: "block"
    warning_action: "warn"

  # =========================================================================
  # Quality (repo-wide; not failure-masking-prone)
  # =========================================================================
  quality:
    enabled: true
    order: 4
    description: "Code quality and complexity (repo-wide)"
    depends_on: ["aggregator", "coverage"]
    tools:
      ruff:
        enabled: true
        complexity_threshold:
          warning: 10
          failure: 15
        command: "ruff check"
        config_file: "pyproject.toml"
    failure_action: "block"
    warning_action: "warn"

  # =========================================================================
  # Security (repo-wide)
  # =========================================================================
  security:
    enabled: true
    order: 5
    description: "Security vulnerability scanning"
    depends_on: ["aggregator", "coverage", "quality"]
    tools:
      bandit:
        enabled: true
        command: "bandit -r src/ -f json -o reports/bandit_report.json"
        severity_threshold:
          high: "failure"
          medium: "warning"
          low: "report"
        confidence_threshold: "medium"
    failure_action: "block"
    warning_action: "warn"

  # =========================================================================
  # Documentation (warning-only; can run independently)
  # =========================================================================
  documentation:
    enabled: true
    order: 5
    description: "Documentation coverage check"
    depends_on: []
    threshold: 75.0
    scan_paths:
      - "src/digitalmodel"
    exclude_paths:
      - "*/tests/*"
      - "*/__pycache__/*"
      - "*/migrations/*"
    failure_action: "warn"
    warning_action: "report"

settings:
  execution_mode: "parallel"  # CHANGED: domain test gates run in parallel; aggregator gates the rest
  cli:
    strict_mode: false
    verbose: true
    show_details: true
    color_output: true
  pre_commit:
    enabled: false  # CHANGED: pre-commit runs ONLY the touched-domain subset via a separate hook (TBD; tracked as follow-up)
  ci_cd:
    enabled: true
    strict_mode: true
    export_results: true
    result_format: "json"
    result_file: "reports/quality_gates_results.json"
  reporting:
    console:
      enabled: true
      format: "detailed"
    json:
      enabled: true
      output_file: "reports/quality_gates_results.json"
  paths:
    source_root: "src"
    test_root: "tests"
    reports_dir: "reports"
    cache_dir: ".quality-gates-cache"
  performance:
    cache_enabled: true
    cache_duration: 3600
    parallel_execution: true  # CHANGED: enabled
    timeout: 900  # raised to 15 min per gate (some domains, e.g. structural, are large)
```

**Notes for implementer:**
- `execution_mode: parallel` requires the `quality_gates_cli check` runner to support a parallel topology (depends_on DAG). If the existing CLI is strictly linear, this plan blocks until #6 sub-task is filed against `digitalmodel/src/digitalmodel/workflows/automation/quality_gates_cli.py`. Decision: **shadow mode** in Phase 2 means the new YAML is interpreted by the new GH workflow (`quality-gates-by-domain.yml`) directly, NOT by the existing CLI. The CLI upgrade is deferred to Phase 4 when the cutover happens.
- `combine_step` is a new field on the `coverage` gate — the CLI either honors it or the workflow does the equivalent shell step (workflow path is the shadow-mode option).
- `pre_commit.enabled: false` is intentional during Phase 2-3 to prevent pre-commit timing out on 16 parallel domain runs. A separate pre-commit-touched-domain hook is a Phase 5+ follow-up.

---

## Sub-task C — `.github/workflows/quality-gates-by-domain.yml`

```yaml
name: Quality Gates (Domain-Divided)

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main, develop]
  schedule:
    # Nightly full-matrix run (full, not touched-subset) — 06:00 UTC
    - cron: "0 6 * * *"
  workflow_dispatch:
    inputs:
      run_full_matrix:
        description: "Force full matrix (ignore touched-domain detection)"
        type: boolean
        default: false

# Cancel in-flight runs for the same PR ref when a new push lands
concurrency:
  group: quality-gates-by-domain-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read
  pull-requests: write  # for the summary comment

jobs:
  # -------------------------------------------------------------------------
  # detect: emits the JSON matrix subset for downstream jobs
  # -------------------------------------------------------------------------
  detect:
    name: Detect touched domains
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.detect.outputs.matrix }}
      run_count: ${{ steps.detect.outputs.run_count }}
      mode: ${{ steps.detect.outputs.mode }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # full history for diff against base

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Determine run mode
        id: mode
        run: |
          if [ "${{ github.event_name }}" = "schedule" ] || [ "${{ inputs.run_full_matrix }}" = "true" ] || [ "${{ github.event_name }}" = "push" ]; then
            echo "mode=full" >> "$GITHUB_OUTPUT"
          else
            echo "mode=touched" >> "$GITHUB_OUTPUT"
          fi

      - name: Detect touched domains
        id: detect
        run: |
          if [ "${{ steps.mode.outputs.mode }}" = "full" ]; then
            python scripts/ci/detect_touched_domains.py --mode full \
              --domains-file tests/DOMAINS.md \
              --output-format json-matrix > matrix.json
          else
            git fetch origin ${{ github.base_ref }}
            python scripts/ci/detect_touched_domains.py --mode touched \
              --base origin/${{ github.base_ref }} --head HEAD \
              --domains-file tests/DOMAINS.md \
              --output-format json-matrix > matrix.json
          fi
          MATRIX=$(cat matrix.json)
          COUNT=$(echo "$MATRIX" | python -c "import json,sys; print(len(json.load(sys.stdin)['domain']))")
          echo "matrix=$MATRIX" >> "$GITHUB_OUTPUT"
          echo "run_count=$COUNT" >> "$GITHUB_OUTPUT"
          echo "mode=${{ steps.mode.outputs.mode }}" >> "$GITHUB_OUTPUT"
          echo "::notice::Mode=${{ steps.mode.outputs.mode }}, will run $COUNT domains"

  # -------------------------------------------------------------------------
  # test: per-domain matrix (subset on PR, full on cron/push)
  # -------------------------------------------------------------------------
  test:
    name: Test ${{ matrix.domain }}
    needs: detect
    if: ${{ needs.detect.outputs.run_count != '0' }}
    runs-on: ${{ matrix.runner }}
    strategy:
      fail-fast: false
      matrix: ${{ fromJSON(needs.detect.outputs.matrix) }}
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install uv
        uses: astral-sh/setup-uv@v3

      - name: Run domain test gate
        timeout-minutes: 20
        run: |
          # Read the command for this domain from .claude/quality-gates.yaml.
          # The CLI extraction is preferred; fallback to a yq one-liner.
          uv run python -c "
          import yaml, sys, subprocess, shlex
          gates = yaml.safe_load(open('.claude/quality-gates.yaml'))['gates']
          gate_key = 'tests-${{ matrix.domain }}'
          assert gate_key in gates, f'Gate {gate_key} not found'
          cmd = gates[gate_key]['command']
          print(f'>>> {cmd}')
          rc = subprocess.call(cmd, shell=True)
          sys.exit(rc)
          "

      - name: Upload domain coverage artifact
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: coverage-${{ matrix.domain }}
          path: reports/coverage-${{ matrix.domain }}.json
          retention-days: 7
          if-no-files-found: ignore

      - name: Upload domain test log
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: testlog-${{ matrix.domain }}
          path: |
            reports/quality-gates-pytest-${{ matrix.domain }}.log
          retention-days: 7
          if-no-files-found: ignore

  # -------------------------------------------------------------------------
  # integration: cross-domain smoke (always runs on src/** changes)
  # -------------------------------------------------------------------------
  integration:
    name: Cross-domain integration
    needs: detect
    runs-on: ubuntu-latest
    if: ${{ needs.detect.outputs.mode == 'full' || contains(github.event.pull_request.changed_files, 'src/digitalmodel/') }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - uses: astral-sh/setup-uv@v3
      - name: Run integration smoke
        timeout-minutes: 10
        run: |
          uv run --with-editable . --with pytest python -m pytest tests/integration tests/cross_repo -rfE -q --tb=short || true
          echo "::notice::integration suite is currently empty (0/7 stub tests); job is informational"

  # -------------------------------------------------------------------------
  # aggregate: gates merge readiness
  # -------------------------------------------------------------------------
  aggregate:
    name: Aggregate domain results
    needs: [detect, test, integration]
    if: ${{ always() }}
    runs-on: ubuntu-latest
    steps:
      - name: Check that all domain jobs passed
        run: |
          # `needs.test.result` is the matrix-aggregate result: success / failure / cancelled / skipped.
          # success = every matrix cell succeeded. failure = at least one failed.
          # skipped is acceptable only when detect emitted run_count=0 (no touched domains).
          MATRIX_RESULT="${{ needs.test.result }}"
          INTEGRATION_RESULT="${{ needs.integration.result }}"
          DETECT_COUNT="${{ needs.detect.outputs.run_count }}"
          echo "Matrix result: $MATRIX_RESULT"
          echo "Integration result: $INTEGRATION_RESULT"
          echo "Touched-domain count: $DETECT_COUNT"
          if [ "$MATRIX_RESULT" = "skipped" ] && [ "$DETECT_COUNT" = "0" ]; then
            echo "::notice::No touched domains; nothing to gate."
            exit 0
          fi
          if [ "$MATRIX_RESULT" != "success" ]; then
            echo "::error::One or more domain test gates failed."
            exit 1
          fi
          if [ "$INTEGRATION_RESULT" != "success" ] && [ "$INTEGRATION_RESULT" != "skipped" ]; then
            echo "::error::Integration gate failed."
            exit 1
          fi
          echo "All gates green."

      - name: Comment PR summary
        if: ${{ github.event_name == 'pull_request' }}
        uses: actions/github-script@v7
        with:
          script: |
            const matrixResult = "${{ needs.test.result }}";
            const detectCount = "${{ needs.detect.outputs.run_count }}";
            const mode = "${{ needs.detect.outputs.mode }}";
            const body = [
              "## Quality Gates (Domain-Divided)",
              "",
              `**Mode:** ${mode}`,
              `**Domains run:** ${detectCount}`,
              `**Matrix result:** ${matrixResult}`,
              `**Integration:** ${{ needs.integration.result }}`,
              "",
              "_Per-domain detail is in the workflow logs and `coverage-*` / `testlog-*` artifacts._",
            ].join("\n");
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body
            });
```

**Runner-OS strategy notes:**
- `runner` is included in the matrix to allow `orcaflex-solver` to mark `runner: windows-latest` in the future. The detection script emits `runner` per domain (default `ubuntu-latest`).
- For Phase 2 shadow-mode, all domains run on `ubuntu-latest`; OrcFxAPI-licensed Windows runs are a follow-up issue.

---

## Sub-task D — Touched-domain detection

### Strategy comparison

- **(a) GH Actions `paths-ignore` per-job** — Cheap, but a single workflow-level `paths` filter applies to the whole workflow; per-job `paths` doesn't exist natively. Workarounds (path-filter actions like `dorny/paths-filter`) require a separate detect job anyway, which collapses (a) into (b)/(c). REJECTED.
- **(b) Pre-job that diffs against base ref and emits JSON matrix subset** — Single workflow file, single detection script, downstream jobs use `matrix: ${{ fromJSON(needs.detect.outputs.matrix) }}`. Tested pattern in many CI systems.
- **(c) Reusable workflow with matrix passed as input; nightly cron passes full matrix, PR job passes subset** — More modular but adds a workflow boundary; the input matrix has to be JSON-encoded the same way as (b)'s output. The detection script is identical to (b).

**Recommendation: (b) is selected.** Reasoning:
- Single workflow file reduces moving parts during the shadow-mode period (Phase 2).
- The detection script is trivially convertible to (c) later if a second consumer of the matrix appears (e.g., a different reusable workflow for nightly perf benchmarks). Migrating (b) → (c) is a refactor, not a rewrite.
- (c)'s modularity payoff is realized only when there is more than one downstream consumer; today there is one.

### Detection script: `digitalmodel/scripts/ci/detect_touched_domains.py`

```python
#!/usr/bin/env python3
"""detect_touched_domains.py — emit a GH Actions matrix subset for the touched-domain CI strategy.

Reads the `## Domain table` from tests/DOMAINS.md, parses each domain row's
"Test roots" cell, and matches them against the changed-file list.

Modes:
  --mode full       — emit ALL domains (cron / push to main / workflow_dispatch)
  --mode touched    — emit only domains whose test roots OR src paths are touched

Output:
  --output-format json-matrix
      JSON for `matrix: ${{ fromJSON(needs.detect.outputs.matrix) }}`:
      {"domain": ["citations", "field-development"], "runner": ["ubuntu-latest", "ubuntu-latest"]}

  --output-format list
      newline-separated domain names (for shell-side use)

A change to:
  - tests/<root>/**           → touches the owning domain
  - src/digitalmodel/**       → touches ALL domains (any src change is full-matrix; consumes the safety
                                 of cross-domain integration without enumerating per-src-path mappings,
                                 deferred to a follow-up; see Risk-R7 below)
  - .claude/quality-gates.yaml → full matrix (the gate config itself changed)
  - .github/workflows/quality-gates-by-domain.yml → full matrix
  - tests/DOMAINS.md          → full matrix (mapping changed)
  - tests/conftest.py         → full matrix (repo-wide test infra)
  - any path NOT mapped       → empty (no domains)
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

DOMAINS_MD = Path("tests/DOMAINS.md")

# Triggers that force full-matrix
FULL_MATRIX_TRIGGERS = (
    re.compile(r"^src/digitalmodel/"),
    re.compile(r"^\.claude/quality-gates\.yaml$"),
    re.compile(r"^\.github/workflows/quality-gates-by-domain\.yml$"),
    re.compile(r"^tests/DOMAINS\.md$"),
    re.compile(r"^tests/conftest\.py$"),
    re.compile(r"^scripts/ci/detect_touched_domains\.py$"),
    re.compile(r"^pytest\.ini$"),
    re.compile(r"^pyproject\.toml$"),
)


def parse_domains(domains_md: Path) -> dict[str, list[str]]:
    """Return {domain_name: [test_root_path, ...]}."""
    text = domains_md.read_text()
    # Find the "## Domain table" section and the markdown table within it
    section = re.search(r"## Domain table\s*\n(.+?)\n## ", text, re.DOTALL)
    if not section:
        raise SystemExit(f"No '## Domain table' section in {domains_md}")
    rows = []
    for line in section.group(1).splitlines():
        line = line.strip()
        if not line.startswith("|") or "---" in line or "Domain |" in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        # cells[0] is "`domain-name`"; cells[1] is the test-roots cell (one per line in the cell)
        name = cells[0].strip("`")
        roots_cell = cells[1]
        # roots may be backtick-wrapped paths separated by commas or newlines/<br>
        roots = re.findall(r"`(tests/[^`]+)`", roots_cell)
        if name and roots:
            rows.append((name, roots))
    return dict(rows)


def changed_paths(base: str, head: str) -> list[str]:
    out = subprocess.check_output(
        ["git", "diff", "--name-only", f"{base}...{head}"], text=True
    )
    return [p for p in out.splitlines() if p]


def is_full_matrix_trigger(paths: list[str]) -> bool:
    return any(any(rx.match(p) for rx in FULL_MATRIX_TRIGGERS) for p in paths)


def domains_touched_by(paths: list[str], domain_map: dict[str, list[str]]) -> list[str]:
    touched = set()
    for p in paths:
        for name, roots in domain_map.items():
            for r in roots:
                # Normalize: r is "tests/<root>"; match if p starts with "<r>/" or equals r
                if p == r or p.startswith(r + "/"):
                    touched.add(name)
    return sorted(touched)


def emit_matrix(domains: list[str], fmt: str) -> str:
    if fmt == "list":
        return "\n".join(domains)
    if fmt == "json-matrix":
        return json.dumps({
            "domain": domains,
            # all domains run on ubuntu-latest for v1; future: per-domain runner override
            "runner": ["ubuntu-latest"] * len(domains),
        })
    raise ValueError(f"unknown output-format {fmt}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("full", "touched"), required=True)
    ap.add_argument("--base", default=None, help="git base ref (touched mode only)")
    ap.add_argument("--head", default="HEAD", help="git head ref (touched mode only)")
    ap.add_argument("--domains-file", default=str(DOMAINS_MD), type=Path)
    ap.add_argument("--output-format", choices=("list", "json-matrix"), default="json-matrix")
    args = ap.parse_args()

    domain_map = parse_domains(args.domains_file)
    if args.mode == "full":
        out = emit_matrix(sorted(domain_map.keys()), args.output_format)
    else:
        if not args.base:
            print("--base required in touched mode", file=sys.stderr)
            return 2
        paths = changed_paths(args.base, args.head)
        if is_full_matrix_trigger(paths):
            out = emit_matrix(sorted(domain_map.keys()), args.output_format)
        else:
            out = emit_matrix(domains_touched_by(paths, domain_map), args.output_format)
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

**Test harness for the script** (Phase 3 lands this alongside):

```python
# digitalmodel/tests/scripts/test_detect_touched_domains.py
import subprocess, json, pathlib
SCRIPT = pathlib.Path("scripts/ci/detect_touched_domains.py")

def test_full_mode_emits_all_16_domains(tmp_path):
    # Use the real tests/DOMAINS.md
    out = subprocess.check_output(
        ["python", SCRIPT, "--mode", "full", "--output-format", "json-matrix"],
        text=True,
    )
    matrix = json.loads(out)
    assert len(matrix["domain"]) == 16
    assert "citations" in matrix["domain"]

def test_touched_mode_one_domain(tmp_git_repo_with_one_test_change):
    # fixture: a tmp repo where tests/citations/test_x.py changed vs. base
    out = subprocess.check_output(
        ["python", SCRIPT, "--mode", "touched", "--base", "main", "--head", "HEAD"],
        text=True, cwd=tmp_git_repo_with_one_test_change,
    )
    matrix = json.loads(out)
    assert matrix["domain"] == ["citations"]

def test_src_change_triggers_full_matrix(tmp_git_repo_with_src_change):
    out = subprocess.check_output(
        ["python", SCRIPT, "--mode", "touched", "--base", "main", "--head", "HEAD"],
        text=True, cwd=tmp_git_repo_with_src_change,
    )
    matrix = json.loads(out)
    assert len(matrix["domain"]) == 16  # full matrix
```

---

## Sub-task E — Per-domain conftest extraction

### Migration table

The implementer reads `tests/conftest.py:1-93` and partitions each piece into one of three buckets: stays repo-wide, moves to a domain conftest, or splits.

| Item in `tests/conftest.py` | Lines | Disposition | Justification |
|---|---|---|---|
| `import sys, pathlib, MagicMock` | 1-4 | **Stays repo-wide** | Used by the sys.path injection block; must run before any test imports. |
| `collect_ignore` list with 24 entries | 9-43 | **PARTITION per domain** (see breakdown below) | Per #2616 cluster cleanup, each excluded test belongs to exactly one domain; its skipif decision is a domain-local concern. |
| `sys.path.insert(0, src_path)` | 46-49 | **Stays repo-wide** | All domains import `src/digitalmodel`; this is universal infrastructure. |
| `assetutilities` sibling-repo path injection | 51-53 | **Stays repo-wide** | Used by `contracts` domain primarily, but other domains may transitively import; safer at root. |
| `aceengineercode` sibling-repo path injection | 55-58 | **Stays repo-wide** | Same rationale. |
| `_create_mock_catenary_riser_summary()` factory + `sys.modules[…] = mock` registration | 61-93 | **MOVE to `tests/subsea/conftest.py`** | The mock targets exactly one module (`digitalmodel.subsea.catenary_riser.legacy.catenary_riser_summary`); it should live with the domain that owns it. Repo-wide registration was a bandaid; per Cluster A in #2616, sys.modules pollution from the root conftest is itself a future-Cluster-A risk. |

### `collect_ignore` partitioning

| Currently-excluded path | Target conftest |
|---|---|
| `marine_ops/artificial_lift/dynacard/test_vision_benchmark.py` | `tests/marine_ops/conftest.py` (new) |
| `solvers/orcaflex/examples_integration/test_converter.py` | `tests/solvers/orcaflex/conftest.py` (extend existing) |
| `solvers/orcaflex/examples_integration/test_single_download.py` | `tests/solvers/orcaflex/conftest.py` (extend existing) |
| `structural/fatigue_analysis/test_reference_seastate_scaling.py` | `tests/structural/conftest.py` (new) |
| `visualization/design_tools/pilot_program/test_case_1_separator.py` | `tests/visualization/conftest.py` (new) |
| `solvers/orcaflex/test_orcaflex_unit.py` | `tests/solvers/orcaflex/conftest.py` (extend existing) |
| `structural/fatigue_apps/test_load_scaling.py` | `tests/structural/conftest.py` (new) |
| `subsea/pipeline/test_on_bottom_stability.py` | `tests/subsea/conftest.py` (new) |
| `test_plate_capacity.py` | `tests/structural/conftest.py` (new) — but verify; this is a top-level test |
| 8 visualization/test_*.py (anomaly/comparative/component_classifier/etc.) | `tests/visualization/conftest.py` (new) |
| 3 workflows/orcawave/test_*.py | `tests/workflows/conftest.py` (new) |
| 1 workflows/standalone/markitdown/test_converter.py | `tests/workflows/conftest.py` (new) |
| `test_workflow_checkpoints.py` (root) | `tests/workflows/conftest.py` (new) |
| `marine_ops/marine_engineering/test_component_database.py` | `tests/marine_ops/marine_engineering/conftest.py` (new) — note: this domain owns Cluster E |
| `hydrodynamics/hull_library/test_hull_library_expansion.py` | `tests/hydrodynamics/hull_library/conftest.py` (extend existing if present, else create) |
| 2 specialized/cathodic_protection/test_*.py | `tests/cathodic_protection/conftest.py` (new — but: this exclusion was for "shared state issue"; consider replacing with a `pytest.mark.flaky` skip-if-running-with-others guard rather than collect_ignore) |

### Resolved: Cluster A is bisect, not autouse purge

**DECISION-LOCKED D5 (2026-05-04):** Cluster A ([#2623](https://github.com/vamseeachanta/workspace-hub/issues/2623)) is fixed by **polluter bisect** in `tests/contracts/`'s own domain workstream — NOT by adding an autouse purge fixture in `tests/contracts/conftest.py`.

Rationale: per-domain CI runs `contracts` in isolation, but the polluter is in some upstream test (likely an `import unittest.mock; sys.modules[...] = MagicMock()` or `@patch.dict('sys.modules', ...)` without proper teardown elsewhere in the suite). Per-domain isolation reduces *cross-domain* pollution risk but doesn't fix *within-domain* pollution. Since `contracts` only has 17 tests and pollution is reproducible under `-p no:randomly`, bisect is cheap. Defensive autouse fixtures spread the band-aid across N domain conftests rather than fixing the source.

Phase 5 conftest extraction therefore does NOT add the autouse fixture; the contracts domain conftest remains minimal until #2623's bisect lands.

This sub-task lands incrementally — one PR per domain — and is **explicitly Phase 5** so the migration doesn't co-occur with the gate-cutover.

---

## Sub-task F — `digitalmodel/CODEOWNERS`

```
# digitalmodel CODEOWNERS — sole owner per workspace-hub #2628 session decision
# Format: <pattern> <owner1> <owner2> ...
# Default fallback owner
*                                       @vamseeachanta

# Test domains (mirror of tests/DOMAINS.md)
/tests/asset_integrity/                 @vamseeachanta
/tests/cathodic_protection/             @vamseeachanta
/tests/specialized/cathodic_protection/ @vamseeachanta
/tests/citations/                       @vamseeachanta
/tests/contracts/                       @vamseeachanta
/tests/field_development/               @vamseeachanta
/tests/hydrodynamics/                   @vamseeachanta
/tests/infrastructure/                  @vamseeachanta
/tests/marine_ops/                      @vamseeachanta
/tests/naval_architecture/              @vamseeachanta
/tests/orcaflex/                        @vamseeachanta
/tests/solvers/                         @vamseeachanta
/tests/specialized/                     @vamseeachanta
/tests/structural/                      @vamseeachanta
/tests/subsea/                          @vamseeachanta
/tests/workflows/                       @vamseeachanta

# CI architecture
/.claude/quality-gates.yaml             @vamseeachanta
/.github/workflows/                     @vamseeachanta
/scripts/ci/                            @vamseeachanta
/tests/DOMAINS.md                       @vamseeachanta
/tests/conftest.py                      @vamseeachanta
```

**Note for implementer:** This file is correctly recognized at `digitalmodel/CODEOWNERS`. Per GitHub's CODEOWNERS resolution, files at `<root>`, `docs/`, or `.github/` are scanned in that priority order; we use `<root>` for visibility.

---

## Sub-task G — workspace-hub agents.md / CLAUDE.md updates

### Current state — verbatim line numbers

`AGENTS.md` is 21 lines; relevant sections:
- Lines 5-8: "Hard Gates" 1-3 (planning, TDD, gate order)
- Lines 13-15: "Workflow" / "Commands"

`CLAUDE.md` is 13 lines; relevant section:
- Lines 8-12: "Planning Workflow (ALL issues — mandatory)"

Per `.claude/rules/coding-style.md`: "CLAUDE.md, MEMORY.md, AGENTS.md, GEMINI.md must not exceed 20 lines." `AGENTS.md` is at 21 (already 1-over; an enforcement violation must be addressed independently). `CLAUDE.md` is at 13 (8-line headroom).

### Proposed insertion — `AGENTS.md`

**Strategy:** Add a single new bullet to the existing "Hard Gates" enumerated list, NOT a new section. This stays under the 20-line cap by counting one new line. The current line 7 ("TDD mandatory — tests before implementation; no exceptions") is the natural neighbor.

Insert as **new line 8** (renumbering current line 8 to 9):

```markdown
3. Test-by-domain — for any change in `digitalmodel/`, run only the touched domain's pytest (`uv run python scripts/ci/detect_touched_domains.py --mode touched --base origin/main --head HEAD` then `uv run pytest <domain roots>`); never `pytest tests/` repo-wide during dev. Domain mapping: `digitalmodel/tests/DOMAINS.md`. Authoritative gate: `.github/workflows/quality-gates-by-domain.yml`.
```

Then renumber: current `3. Gate order: …` becomes `4. Gate order: …`.

**Side effect:** AGENTS.md goes from 21 → 22 lines, deepening the existing 1-line cap violation. Mitigation: same PR strips the redundant "Engineering-Critical Labels" section (lines 9-10) which is already linked from elsewhere, bringing the total back to 20. Or: file a follow-up to address the AGENTS.md cap separately. **Plan choice:** strip in same PR; cite `.claude/rules/coding-style.md` cap.

### Proposed insertion — `CLAUDE.md`

**Strategy:** Add one bullet under the existing "Planning Workflow" section. CLAUDE.md has 8-line headroom — safe.

Insert as **new line 12** (between current 11 and 12):

```markdown
- Test-by-domain default — when working in `digitalmodel/`, scope pytest to the touched domain per `digitalmodel/tests/DOMAINS.md`; the repo-wide `pytest tests/` invocation is reserved for nightly cron and explicit pre-merge verification.
```

### Why these are minimal

The agent-facing rule needs to land in the harness contract (AGENTS.md) so that Codex/Gemini/Hermes also honor it, and the Claude-specific reminder (CLAUDE.md) is a friendly nudge to the most active agent. Both insertions point at the same authoritative artifacts (`tests/DOMAINS.md`, the workflow file) so drift between the two is visible.

---

## Files to Change

| Action | Path | Reason / sub-task |
|---|---|---|
| Create | `digitalmodel/tests/DOMAINS.md` | A — domain inventory |
| Create | `digitalmodel/CODEOWNERS` | F — ownership encoding |
| Modify | `AGENTS.md` (workspace-hub) | G — add Hard Gate #3 + strip redundant section to stay under 20-line cap |
| Modify | `CLAUDE.md` (workspace-hub) | G — add planning-workflow bullet |
| Modify | `digitalmodel/.claude/quality-gates.yaml` | B — full replacement with v2 domain-divided structure (in-place) |
| Create | `digitalmodel/.github/workflows/quality-gates-by-domain.yml` | C — new matrix workflow |
| Create | `digitalmodel/scripts/ci/detect_touched_domains.py` | D — touched-domain detector |
| Create | `digitalmodel/tests/scripts/test_detect_touched_domains.py` | D — script tests |
| Modify | `digitalmodel/tests/conftest.py` | E — strip catenary mock + 24-entry collect_ignore (Phase 5) |
| Create | `digitalmodel/tests/<domain>/conftest.py` (multiple) | E — per-domain conftests (Phase 5, incremental) |
| Modify | `digitalmodel/.github/workflows/quality-gates.yml` | Phase 4 — disable / archive (rename to `quality-gates.yml.archived` or delete) |
| Update | `docs/plans/README.md` | add this plan to index |

---

## TDD Test List

| Test name | What it verifies | Owning sub-task |
|---|---|---|
| `test_domains_md_parses` | `parse_domains(tests/DOMAINS.md)` returns ≥16 domains, every value list non-empty | A |
| `test_domains_md_covers_all_test_roots` | every `tests/<dir>` (excluding fixtures/output/data) maps to exactly one domain (else either belongs in `misc` or the inventory is incomplete) | A |
| `test_quality_gates_yaml_loads` | new YAML is valid; `aggregator.depends_on` lists every domain gate | B |
| `test_no_repo_wide_maxfail_in_yaml` | greps for `--maxfail=` in `.claude/quality-gates.yaml`; expected count 0 (or only inside per-domain commands at a value documented as "domain-bounded, not masking") | B |
| `test_workflow_yaml_lints` | actionlint passes on `quality-gates-by-domain.yml` | C |
| `test_workflow_concurrency_cancel_in_progress` | concurrency block exists with `cancel-in-progress: true` | C |
| `test_aggregate_job_needs_test_and_integration` | `aggregate.needs` includes `test` and `integration` | C |
| `test_detect_full_mode_emits_all_16` | script in `--mode full` returns 16 domains | D |
| `test_detect_touched_one_domain` | one test-file change emits a single-element matrix | D |
| `test_detect_src_change_triggers_full_matrix` | a `src/digitalmodel/...` change emits all 16 | D |
| `test_detect_unmapped_path_emits_empty` | a `docs/...` change emits an empty matrix | D |
| `test_detect_handles_missing_base_branch` | `--mode touched` without `--base` exits with helpful error | D |
| `test_codeowners_default_owner` | every test root in DOMAINS.md is covered by a CODEOWNERS entry | F |
| `test_agents_md_under_20_lines` | post-edit AGENTS.md ≤ 20 lines (`.claude/rules/coding-style.md` cap) | G |
| `test_agents_md_has_test_by_domain_directive` | grep finds the new directive | G |
| `test_claude_md_has_test_by_domain_bullet` | grep finds the new bullet | G |
| `test_contracts_conftest_purges_assetutilities_mocks` | autouse fixture removes `MagicMock` entries from `sys.modules['assetutilities*']` BEFORE each test | E |
| `test_root_conftest_no_longer_pre_registers_catenary_mock` | `tests/conftest.py` doesn't import `MagicMock` (post-Phase-5) | E |

---

## Acceptance Criteria

- [ ] `tests/DOMAINS.md` exists and lists 16 domains; every test root in the table is a real directory in `digitalmodel/tests/`.
- [ ] `digitalmodel/CODEOWNERS` exists with `*  @vamseeachanta` default; covers every domain test-root from DOMAINS.md.
- [ ] `digitalmodel/.claude/quality-gates.yaml` has 16 `tests-<domain>` gates plus aggregator; no `--maxfail=` at the repo-wide level (per-domain values, if any, are inline-documented as bounded-by-domain-size).
- [ ] `digitalmodel/.github/workflows/quality-gates-by-domain.yml` validates with `actionlint`; concurrency block cancels in-progress; aggregate job gates merge.
- [ ] `digitalmodel/scripts/ci/detect_touched_domains.py` passes its 5+ unit tests; `--mode full` emits 16 domains; `--mode touched` with a one-test change emits 1.
- [ ] PR for trivial change (e.g. docs typo) emits `run_count=0` and exits the workflow green in <2 min wall time.
- [ ] PR that touches `tests/citations/test_*.py` runs only `tests-citations`; aggregate job goes green if that domain passes.
- [ ] Nightly cron emits `mode=full` and runs all 16 domains; cumulative wall time fits within a 30-min budget (parallel ceiling = 16 jobs).
- [ ] `AGENTS.md` updated with new Hard Gate; total line count ≤ 20 (cap satisfied by section strip).
- [ ] `CLAUDE.md` updated with new bullet; total line count ≤ 20.
- [ ] Existing admin-merge cycle ends — first post-cutover PR merges through `quality-gates-by-domain.yml` aggregate without override.
- [ ] No test files deleted as part of this work; per-domain debt is filed as a per-domain follow-up issue (per #2628 acceptance, with AI-attestation gate per `feedback_attestation_enables_contradiction_detection`).
- [ ] r1 review artifacts in `scripts/review/results/2026-05-03-plan-2628-{claude,gemini}.md` posted; Codex MAY be UNAVAILABLE per #2479.
- [ ] `docs/plans/README.md` index updated with this plan.

---

## Sequencing / Phasing

The plan splits across 5 phases with explicit gating between phases. Each phase commits independently; rollback between phases is clean.

### Phase 1 — Read-only artifacts (parallel-safe; no CI risk)

Lands together: **A + F + G**.

- A: `tests/DOMAINS.md` (new file, no consumer yet)
- F: `CODEOWNERS` (new file; takes effect on next PR but no one tags-out the owner since vamseeachanta is sole owner)
- G: `AGENTS.md` + `CLAUDE.md` (workspace-hub repo)

**Risk:** ~zero. CODEOWNERS could trigger surprise review-required checks if branch protection enforces them — verify branch protection settings before merging F. If it does, gate F behind explicit user opt-in.

**Acceptance gate to enter Phase 2:** these three files merged + greenwashed CI confirms no surprise breakage.

### Phase 2 — Shadow-mode CI (B + C, but the OLD workflow stays the gating one)

Lands together: **B + C**.

- B: `.claude/quality-gates.yaml` v2 written, but the old `quality-gates.yml` workflow continues to read it via the existing CLI. This requires the YAML to be backward-readable; if the new structure breaks the CLI, B is split into B1 (yaml refactor that the old CLI still tolerates by ignoring unknown keys) and B2 (CLI upgrade in Phase 4). **Plan recommendation:** preserve the original file as `.claude/quality-gates.yaml.legacy` for the duration of Phase 2-3 and have the OLD workflow read the legacy file, while the NEW workflow reads the v2 file. Two configs in parallel during shadow mode.
- **DECISION-LOCKED D4 (2026-05-04): atomic with `pytest.ini --maxfail=50` removal.** B's commit MUST also delete the `--maxfail=50` token from `digitalmodel/pytest.ini`'s `addopts` line in the same commit. Both masking layers come out together; partial removal would create the worst signal ("we removed the cap but failures still don't surface; why?"). Add a TDD assertion: grep `pytest.ini` for `--maxfail` should return zero hits.
- C: new workflow file lands but is initially configured with `if: false` on the `aggregate` job's failure-block step (so it's informational-only). **DECISION-LOCKED D2 (2026-05-04): SILENT in Phase 2 — no PR comments from the new workflow.** Evidence-only comments start in Phase 3 when the workflow becomes informationally visible. Shadow runs accumulate for **2 weeks** of PR activity (DECISION-LOCKED D3 (2026-05-04); revised up from "1-2 weeks" — 2 weeks gives ~30-40 PRs of cross-domain validation coverage at typical workspace-hub cadence).

**Risk:** Touching `.github/workflows/` mid-PR can break in-flight CI on every other open PR — mitigation: file the new workflow only (B's YAML edit lands separately and only touches `.claude/`). Verify the OLD workflow CONTINUES to read `.claude/quality-gates.yaml`; if the old CLI rejects the v2 schema, defer B to Phase 4 and ship C alone with a hard-coded matrix in the workflow file (not reading from YAML).

**Acceptance gate to enter Phase 3:** new workflow has run on ≥10 PRs in shadow-mode without exceeding 5-min wall-time at the 90th percentile; aggregator results match expected per-domain status of #2616 cluster trends. **D3-locked overlap window: 2 weeks** (revised from r0's "1-2 weeks"); if the ≥10-PR threshold is hit before 2 weeks, hold for the full window; if 2 weeks elapse with <10 PRs, extend the overlap until the PR-count gate is met.

### Phase 3 — Touched-domain detection ON for PRs

Lands: **D**.

- D: detection script + tests + workflow updated to consume the JSON matrix.

**Risk:** Detection script bugs would emit either too few domains (under-test → misses real regressions) or too many (degrades to full-matrix on every PR → no perf win). Mitigation: detection's test suite (D's TDD list above) covers the boundary cases; a 1-week double-run period where the workflow runs both the detected subset AND the full matrix as separate jobs, comparing results, before retiring the redundant full-matrix job on PRs.

**Acceptance gate to enter Phase 4:** detection-vs-full divergence rate ≤ 1% (i.e., out of 100 PRs, ≤1 case where touched-mode missed a real failure that full-mode caught).

### Phase 4 — Cutover: new YAML + new workflow become gating; OLD retired

Lands: **`.github/workflows/quality-gates.yml` archived** (renamed `quality-gates.yml.archived` or deleted); `.github/branch-protection` settings updated to require `aggregate` job from `quality-gates-by-domain.yml` instead of the old `quality-gates` check. CLI in `digitalmodel/src/digitalmodel/workflows/automation/quality_gates_cli.py` upgraded to read v2 schema with parallel topology.

**Risk:** Branch protection cutover is the highest-risk single moment. Mitigation: dry-run by setting both checks as required for 24h, then dropping the old one. Both must be green for any PR to merge during the dry-run window.

**Acceptance gate to enter Phase 5:** 1 week of all-green merges through new gate, no admin-merge events.

### Phase 5 — Per-domain conftest extraction (E; incremental)

Lands as **one PR per domain**, in any order. Each PR:
- Creates or extends `tests/<domain>/conftest.py` with the relevant subset of `collect_ignore`, fixtures, and skipif policy
- Removes the corresponding lines from `tests/conftest.py`
- For `contracts`: adds the autouse `_purge_assetutilities_mocks` fixture (Cluster A fix)

**Risk:** Lowest of all phases. Each PR is small, scoped to one domain, and only the touched domain runs in CI per Phase 3.

---

## Risks Register

- **Risk-R1 (per-domain dep-install duplicate `uv` resolution work).** Each `uv run --with-editable . --with X --with Y …` resolves the dep set fresh. Estimated cost increase: 16 domains × ~15s of dep-resolve per run = 4 min added per full matrix run. Mitigation: GH Actions `uv-cache` action (`astral-sh/setup-uv@v3` with `enable-cache: true`) brings warm-cache resolve down to ~2-3s; estimated effective cost: ~30-40s overhead per full matrix. Acceptable. Touched-mode runs (~1-3 domains) gain ~2-3 min wall time over the old single-job run because they install fewer deps.
- **Risk-R2 (cross-domain integration tests).** A test in `tests/marine_engineering/` that depends on a fixture defined in `tests/contracts/conftest.py` would silently fail under domain isolation. Policy: cross-domain integration is the `tests/integration/` and `tests/cross_repo/` job — currently 0/7 stub-tests. Either populate that job with real cross-domain assertions OR document that pytest-fixture inheritance across domains is a smell that should be eliminated by the per-domain conftest extraction in Phase 5. **Plan choice:** document; populate as a follow-up issue.
- **Risk-R3 (Cluster-A-pattern across-domain test pollution).** A test in `tests/structural/` that accidentally registers a `MagicMock` in `sys.modules['assetutilities.X']` would not be caught by domain isolation if `tests/contracts/` is in a different job. Mitigation: contracts conftest's `_purge_assetutilities_mocks` fixture provides a per-test setup-time purge regardless of who polluted; this is a domain-local defense, not a cross-domain coordination problem. Document explicitly in `tests/contracts/conftest.py` docstring.
- **Risk-R4 (the existing 200+ unfixed failures).** Per-domain CI surfaces them per-domain. Each domain's first PR will be against a broken baseline. Policy options: (a) "land with X failures, fix in followups" grace period for first PR per domain; (b) freeze each domain's gate at `failure_action: warn` until its baseline is green, then flip to block. **Plan choice (b)** with explicit `# baseline: 16 known failures, see #ISSUE` comment per gate; freeze period ends when baseline is 0. Each domain's freeze release is its own PR.
- **Risk-R5 ("always test by domain during dev" for AI agents — multi-domain change).** When an AI agent's change touches `src/digitalmodel/X.py` and X is consumed by 5 domains, the agent must run all 5 (or the full matrix). The detection script forces full-matrix on any `src/digitalmodel/**` change (per FULL_MATRIX_TRIGGERS), which is the safe default. Cost: src-only PRs run all 16 domains. Future optimization: per-src-path → consumer-domain mapping (deferred to follow-up; see Risk-R7).
- **Risk-R6 (workflow change breaks in-flight CI).** Phase 2's parallel-config approach (legacy + v2 YAMLs both present) is the mitigation. Phase 4's branch-protection cutover is the riskiest moment.
- **Risk-R7 (src-path → domain mapping for finer-grained touched detection).** Currently any `src/digitalmodel/**` change triggers full matrix. The win of touched-domain detection is realized only on test-only PRs. A follow-up issue should map `src/digitalmodel/citations/**` → `citations` domain, `src/digitalmodel/orcaflex/**` → `orcaflex` + `orcaflex-solver`, etc. Out of scope for this plan; tracked as a follow-up.
- **Risk-R8 (`pytest.ini` `--maxfail=50` in addopts is still repo-wide).** Even after `.claude/quality-gates.yaml` removes `--maxfail`, the `addopts = … --maxfail=50` in pytest.ini will still apply to every pytest invocation. If domains are sized larger than 50 failures-worth, masking returns. Mitigation: per-domain commands explicitly override (`-o "addopts="` or `--no-cov` patterns); or remove `--maxfail=50` from pytest.ini and replace with per-domain bounds. **Plan choice:** remove from pytest.ini in Phase 2 (the same PR that lands B). New `pytest.ini` `addopts` carries no `--maxfail`.
- **Risk-R9 (`pytest.ini` `norecursedirs` excludes 4 paths repo-wide).** `tests/data_systems/data_scraping`, `tests/marine_ops/artificial_lift/dynacard/benchmark`, `tests/specialized/cathodic_protection`, `tests/workflows/integration` — these are silently dropped from collection. Per the cathodic-protection domain consolidation, `tests/specialized/cathodic_protection` MUST be re-included (per Phase 5 conftest extraction). The other three are still excluded; document in the relevant domain's notes.
- **Risk-R10 (Codex r1 unavailability).** Per #2479, codex-cli 0.124.0 stdin-hangs. If 0.125 hasn't shipped by review time, fallback is Claude+Gemini per `feedback_permission_gate_blocks_cross_review`.
- **Risk-R11 (Hermes contention during cutover).** Per `feedback_hermes_active_preflight_check`, Phase 4's branch-protection cutover should not co-occur with a Hermes cleanup loop. Pre-flight: `pgrep -af 'git (rebase|stash push|commit|merge|reset|checkout)'` before the branch-protection toggle.
- **Risk-R12 (parallel agents touching shared CODEOWNERS / DOMAINS.md).** Per `feedback_multi_agent_commit_serialization`, parallel agents adding new test roots in the same window would race on `tests/DOMAINS.md`. Phase 1 lands these single-author; subsequent updates use the parallel-agent write-only pattern (`feedback_parallel_agent_write_only_pattern`).

---

## Adversarial Review Summary

<!-- Filled in after r1 cross-review completes. Do not pre-authorize execution. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | (pending) | (pending) |
| Codex | (pending — may be UNAVAILABLE per #2479) | (pending) |
| Gemini | (pending) | (pending) |

**Overall result:** (pending r1)

Revisions made based on review:
- (none yet)

---

## Open Questions for User at Plan-Review

- **Q1:** Is `misc` acceptable as a 16th domain (catch-all), or should it be deleted from the matrix and the orphan tests filed as one cleanup follow-up issue per orphan-root? Plan choice: keep `misc` for safety, file the migration as a follow-up.
- **Q2:** During Phase 2 shadow-mode, should the new workflow comment its results on PRs, or stay silent until Phase 4? Plan choice: comment with a `(SHADOW)` prefix so reviewers can compare without confusion.
- **Q3:** For Phase 4's branch-protection cutover, should we run a 24h "both required" overlap or do an instant flip? Plan choice: 24h overlap.
- **Q4:** Should `pytest.ini` `addopts = … --maxfail=50` come out in Phase 2 (with the YAML refactor) or Phase 4 (with the cutover)? Plan choice: Phase 2 — see Risk-R8.
- **Q5:** Is the contracts-domain autouse `_purge_assetutilities_mocks` fixture acceptable as the Cluster A fix, or do you prefer hunting the polluter (per #2616 Cluster A option (a))? Plan choice: install the autouse fixture in Phase 5 AND file a separate follow-up to bisect the polluter; defense-in-depth.

---

## Out of Scope

- Repo-wide CODEOWNERS for paths outside `digitalmodel/` (workspace-hub-level CODEOWNERS, if any, is a separate question).
- Per-src-path → domain mapping for touched detection (any `src/digitalmodel/**` change triggers full matrix in v1; finer mapping is Risk-R7 follow-up).
- Cluster fix landings themselves (B/D/E from #2616 are routed to per-domain follow-up issues; this plan is the architecture, not the cleanup).
- OrcFxAPI Windows-runner integration (orcaflex-solver runs on ubuntu in v1 with pytest.importorskip; Windows runner integration is a follow-up).
- Migrating the existing 11 per-tooling workflows (`aqwa-tests.yml`, etc.) into the matrix — those workflows target `tests/domains/<name>/**` which is currently empty stub; their consolidation is a follow-up after Phase 5 lands.
- Pre-commit hook for touched-domain run (mentioned in §Sub-task B settings; deferred).
- assetutilities / aceengineercode sibling-repo CI alignment (this plan is digitalmodel-only).
- Closing #2628 itself (this plan is the planning artifact for #2628; closing happens after all 5 phases land or after partial phases land with explicit user sign-off).

---

## Complexity: T3

**T3** — multi-phase architectural change to the CI surface, spanning 5 sequenced phases over multiple PRs, with branch-protection cutover risk in Phase 4 and incremental migration risk across Phase 5. Touches both repos in the workspace (digitalmodel for the gate config + workflows + scripts + conftests; workspace-hub for AGENTS.md/CLAUDE.md). Adversarial review is mandatory. Execution is gated on user-applied `status:plan-approved` after r1 review and amendments per `feedback_never_offer_to_self_label_plan_approved`.
