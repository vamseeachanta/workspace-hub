---
name: project-doris-demo
description: "Doris Group (Mo Dessoukey) 1-hr AI-initiative demo on 2026-06-05; prep tracked at workspace-hub#2859"
metadata: 
  node_type: memory
  type: project
  originSessionId: 980c06c6-7a70-4602-bfbc-32addeb44f9a
---

Doris Group is a **prospective client** for the AI initiative / repo ecosystem. Contact **Mo Dessoukey** (`Mo.Dessoukey@dorisgroup.com`); referred via Stephane Taxy + Charles White (Doris), user knows Mo socially (soccer). Mo set up a **1-hour Teams demo on Fri 2026-06-05** "to gauge the value it will have and how it will fit in our systems." `repo-ecosystem-flowchart.pdf` already shared.

- Prep tracked at [workspace-hub#2859](https://github.com/vamseeachanta/workspace-hub/issues/2859): ready max domains across **digitalmodel** (engineering) + **worldenergydata** (energy data).
- Doris = offshore/subsea engineering → prioritize subsea, naval_architecture, hydrodynamics, orcaflex/orcawave, marine_ops, structural, fatigue, field_development; plus worldenergydata regional production + metocean + fdas + dashboards.

**Why:** Hard deadline 2026-06-05; demo should lead with strongest (green) domains, never show broken ones.

**How to apply:** Build a green/amber/red readiness matrix + demo runbook before the meeting; frame each domain as "how it fits Doris systems." Related: [[project-hd-cfd-client]], [[project_analysis_domain_objective]].

**Status 2026-05-28 (readiness):** Readiness DONE via Codex — combined **27 GREEN / 14 AMBER / 1 RED**. Docs on pushed branches `digitalmodel:docs/hd-cfd-and-doris-demo` + `worldenergydata:docs/doris-demo-readiness`. Lead greens: bsee, metocean, fdas, lower_tertiary, vessel_fleet/hull_models (data); field development, hydrodynamics, naval architecture, orcaflex, structural/fatigue/CP/asset integrity, drilling riser, openfoam (engineering).

**Status 2026-05-28 (runbook — DONE):** Consolidated demo runbook built + smoke-verified end-to-end → `worldenergydata/docs/demos/2026-06-05-doris/RUNBOOK.md` (branch `docs/doris-demo-readiness` @ `aa0b3136`, pushed). The **sodir RED is FIXED → GREEN** (now 28 GREEN / 13 AMBER / 0 RED): `factmaps.sodir.no` DataService is dead (HTTP 400); the working live path is **SODIR factpages tableview CSV export** (`https://factpages.sodir.no/public?/Factpages/external/tableview/<report>&...&rs:Format=CSV`) — new `src/worldenergydata/sodir/factpages.py` + committed snapshots `data/modules/sodir/` (offline fallback) + `tests/unit/sodir/test_factpages.py`. lower_tertiary CSV/HTML re-pointed `/tmp`→`docs/demos/2026-06-05-doris/artifacts/`. well_production_dashboard stays AMBER (placeholder zeros), not demoed. Result posted to #2859.

**CP-for-structures track 2026-05-29 (QUEUED, not started):** Cathodic protection added as a GTM demo track — [digitalmodel#644](https://github.com/vamseeachanta/digitalmodel/issues/644) (parent) with 4 native sub-issues: **#645** demo_06 offshore structures jacket/monopile (DNV-RP-B401, `marine_structure_cp.py`), **#646** demo_07 subsea pipeline bracelet anodes (ISO 15589-2/DNV-RP-F103, `pipeline_cp.py`), **#647** demo_08 ICCP rectifier/ground-bed (`iccp_design.py`), **#648** demo_09 retrofit/remaining-life (`anode_depletion.py`). CP module is mature — **231 tests pass**, but tiered Sample-only because the `examples/demos/gtm/` pack (demos 01–05) has no CP demo/branded report. Each sub-issue = parametric sweep → branded HTML report + `--from-cache` + smoke test (mirrors demos 01–05), then promotes Sample-only→Production-ready. Backing modules all verified to have parametric entry points. Next action: build #645 first. Session doc: `session-summary-20260529-doris-cp-gtm.html`.
