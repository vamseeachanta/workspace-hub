---
name: project_analysis_domain_objective
description: "The north-star objective for every analysis-domain module in every analysis repo — output-driven pipeline with assumption-filling, input prep, sanity-checked output"
metadata: 
  node_type: memory
  type: project
  originSessionId: 57ba7232-71af-4ee6-92f1-0f808c39212f
---

**Domain objective (ALL domains, ALL analysis repos — e.g. digitalmodel diffraction/OrcaWave, AQWA, OrcaFlex, fatigue, …):** given (1) a *defined output/outcome* and (2) *barebones raw data*, the domain module must:

- **(a) Q&A + assume missing data** — detect what's missing for the requested outcome, ask the user, and where unanswered supply *suitable assumed/default values* (engineering defaults).
- **(b) prepare input data** — convert/assemble the solver-ready input package from the (now complete) data.
- **(c) provide output with sanity checks** — run, then return results gated by physical/range/coverage sanity validation.

**Why:** this is the unifying design contract that makes a domain module *intelligent* rather than a thin solver wrapper. It is **output-driven / inverse** (outcome defined first → infer inputs), not the usual input-driven (spec → run → results) flow.

**How to apply:**
- Assess/triage every analysis-domain issue by which pillar (a/b/c) it advances; the integrated output-driven orchestrator is the real deliverable, not the individual components.
- **(a) requires an explicit assumption ledger** — assumed values must be *recorded and surfaced*, never silent. This reconciles with digitalmodel #525 (which removed SILENT parser defaults): defaults are fine when provenance-tagged, forbidden when silent.
- Recurring anti-pattern observed in digitalmodel diffraction (2026-05-27 OrcaWave audit): the pillar capabilities exist as **disconnected libraries** — `parametric_spec_generator.estimate_mass/cog/radii_of_gyration` (a), `MeshPipeline`/`SpecConverter` (b), `GeometryQualityChecker` + `OutputValidator` (c) — but are NOT wired into one output-driven entry point. ~components present, ~0 integrated. See [[feedback_digitalmodel_reports_dir_gitignored]] scorecard. The OrcaWave open epic #605–#614 is mostly the (b) integration; no issue yet covers the (a) inverse entry + assumption ledger.
