# Archive Horizon Follow-up Candidates
*Generated: 2026-02-20 | WRK-228 step 4 | 135 archived items analysed*

## Follow-up Candidates

### WRK-009 / WRK-010 — Lower Tertiary BSEE Repeatability and Latest Data Rerun
**Original delivery**: Reproduced rev30 lower tertiary results and revalidated with latest BSEE data; confirmed pipeline repeatability.
**Follow-up signal**: The repeatability work established a manual validation process; with WRK-076 (data scheduler) pending, this should become an automated regression test that runs whenever BSEE data refreshes to confirm lower tertiary results remain stable.
**Suggested action**: New WRK — add automated regression test for lower tertiary field results as part of WRK-076 data refresh scheduler; one-line pytest that diffs key metrics against the rev30 baseline.

---

### WRK-011 — BSEE Analysis for All Leases with Field Nicknames and Geological Era Grouping
**Original delivery**: Ran BSEE pipeline across all leases with geological era grouping and field nicknames — a comprehensive batch analysis.
**Follow-up signal**: This was a one-time batch run; with the BSEE field development interactive map (WRK-111 pending), the era grouping and nickname taxonomy should be promoted to a persistent, queryable catalogue that agents and the website can reference — not just a one-time run output.
**Suggested action**: Wrap as skill / extend WRK-111 — make the era grouping taxonomy and field nicknames a first-class persistent data asset in worldenergydata.

---

### WRK-013 — HSE Data Analysis: Mishaps by Activity and Subactivity
**Original delivery**: HSE analysis identifying typical incident patterns by activity and subactivity using OSHA, BSEE, and PHMSA data.
**Follow-up signal**: This analysis was run once; with the HSE risk index dashboard (WRK-198 pending), the mishap-by-activity taxonomy should be exposed as a live queryable interface, not a static report. The analysis produced a classification schema that agents could use in project safety planning.
**Suggested action**: Extend WRK-198 — promote the activity/subactivity mishap classification to a queryable API endpoint in the HSE risk index dashboard; agents can call it during project risk assessment.

---

### WRK-014 — HSE Risk Index: Client-Facing Risk Scoring
**Original delivery**: HSE risk scoring module with client-facing risk insights (commit ad28cb6).
**Follow-up signal**: The risk scoring module was built but the interactive web dashboard (WRK-198) is still pending. The agentic trajectory means the dashboard should be the primary consumer of this module — agents should be able to call the risk scorer and surface results on the website automatically.
**Suggested action**: Unify with WRK-198 — connect the existing risk scoring module to the web dashboard; the backend exists, the frontend is what WRK-198 needs to deliver.

---

### WRK-017 — BSEE Field Data Analysis Pipeline
**Original delivery**: Unified pipeline runner for wellbore, casing, drilling, completions, and interventions with `FieldContext` dataclass (commit fe0168b).
**Follow-up signal**: The pipeline was built for on-demand runs; with improved agents in 3–4 months, the pipeline should be invocable as a skill — an agent should be able to call `bsee_field_pipeline(field_name)` and get a full FieldReport without human orchestration. The current interface requires too much setup knowledge.
**Suggested action**: New WRK — wrap the BSEE field pipeline as a zero-config agent-callable skill; register it in the skill catalog; standardise the invocation API so agents can call it autonomously.

---

### WRK-026 / WRK-057–WRK-063 — Unified Diffraction Solver Input Converter
**Original delivery**: Canonical spec.yml → AQWA/OrcaWave backends, mesh converter, CLI, test suite, and reverse parsers (all six sub-items delivered).
**Follow-up signal**: The converter infrastructure is complete but there is no skill registered for it; agents discovering a diffraction analysis task won't find this capability. The reverse parsers (WRK-063) enable round-trip conversion which is particularly powerful for importing legacy models into the new schema — a use case that should be documented and promoted.
**Suggested action**: New WRK — register the spec converter as a named skill with documented inputs/outputs; add an "import legacy model" workflow to the skill; the converter is foundational infrastructure that agents should be able to discover and use.

---

### WRK-038 — Global LNG Terminal Dataset
**Original delivery**: Comprehensive LNG terminal project dataset compiled with parameters across global terminals.
**Follow-up signal**: This dataset was compiled as a one-time output; with WRK-076 (data scheduler) pending, LNG terminal data should be refreshable. More importantly, the dataset is not yet surfaced on the aceengineer website — it's a high-value differentiating asset for client demonstrations and lead generation.
**Suggested action**: New WRK — (a) expose the LNG dataset as a queryable module in worldenergydata, and (b) add a data card or interactive table to the aceengineer website; agents can generate the web content from the dataset automatically.

---

### WRK-044 — Pipeline Wall Thickness Calculations with Parametric Utilisation
**Original delivery**: Pipeline wall thickness calculations with parametric utilisation analysis (completed 2026-02-16).
**Follow-up signal**: This was delivered alongside WRK-155 (DNV-ST-F101) and WRK-158 (parametric engine). Together they form a complete wall thickness assessment suite. The FFS work (WRK-156 pending, WRK-138 archived) is the next layer. These three deliverables should now be unified into a single "pipeline integrity assessment" skill that agents can invoke end-to-end: wall thickness → utilisation → FFS acceptance.
**Suggested action**: New WRK — create a "pipeline integrity skill" that chains wall thickness (WRK-044/WRK-155), parametric engine (WRK-158), and FFS assessment (WRK-156/WRK-138) into a single callable workflow; this is the key engineering deliverable for the asset integrity market.

---

### WRK-051 / WRK-052 / WRK-053 / WRK-054 — Test Coverage Improvements (All Repos)
**Original delivery**: Test coverage improvements across digitalmodel, assetutilities, assethold, and worldenergydata.
**Follow-up signal**: Coverage was improved but there is no ongoing mechanism to prevent regression. WRK-236 (pending: test health trends) addresses this conceptually, but the delivered coverage improvements should be locked in via coverage gates in CI — not just a one-time uplift.
**Suggested action**: Extend WRK-236 — add coverage regression gates to CI for each repo; the gate enforces that coverage never drops below what was achieved in these items; pair with WRK-149 and WRK-150 (still pending) for remaining gaps.

---

### WRK-066 — Review and Improve digitalmodel Module Structure for Discoverability
**Original delivery**: Module structure review and improvement for discoverability in digitalmodel.
**Follow-up signal**: Discoverability was improved manually; with the domain knowledge graph (WRK-183 pending) and skills knowledge graph (WRK-205 archived-done), the module structure should now feed a machine-readable capability index that agents can query. The manual review is now outdated and the standard has risen.
**Suggested action**: New WRK — generate a machine-readable capability manifest for digitalmodel modules (similar to what WRK-205 did for skills); wire it into the skills knowledge graph so agents can discover engineering capabilities by type.

---

### WRK-067 / WRK-068 — OSHA and BSEE Incident Data Acquisition
**Original delivery**: OSHA enforcement/fatality data and BSEE incident investigation data acquired and imported.
**Follow-up signal**: Data was acquired once; with WRK-076 (data scheduler) pending, these safety databases should be on a refresh schedule — OSHA and BSEE update regularly. The current data may already be 2–4 months stale.
**Suggested action**: Add to WRK-076 — include OSHA enforcement and BSEE incident data in the automated refresh scheduler; these are live regulatory databases that require periodic re-acquisition to keep the HSE risk index current.

---

### WRK-070 — PHMSA Pipeline Data and Pipeline Safety Module
**Original delivery**: PHMSA pipeline incident data imported and `pipeline_safety` module built.
**Follow-up signal**: This is a rich dataset that has not been connected to the aceengineer website case studies or the HSE risk index (WRK-198). Pipeline safety data is directly relevant to the FFS/asset integrity market that WRK-156 targets. The module was built but not yet leveraged for client-facing content.
**Suggested action**: New WRK — create a PHMSA pipeline safety case study for the aceengineer website using the existing module; tie it to the FFS skill (WRK-206) to show a data-to-assessment workflow; this is a high-value marketing asset.

---

### WRK-072 — Technical Safety Analysis Module (ENIGMA Theory)
**Original delivery**: Technical safety analysis module for worldenergydata using ENIGMA theory for fault propagation modelling.
**Follow-up signal**: ENIGMA-based safety analysis was implemented but has no skill wrapper and is not surfaced as an agent-callable capability. With improved reasoning agents in 3–4 months, the ENIGMA methodology could be combined with live HSE data to automatically generate safety assessment narratives for client projects.
**Suggested action**: New WRK — register ENIGMA safety analysis as a skill; pair it with the HSE risk index (WRK-198) and marine safety data (WRK-074) to create an automated safety assessment workflow that agents can invoke for project briefings.

---

### WRK-073 — Market digitalmodel and worldenergydata on aceengineer Website
**Original delivery**: Marketing content for digitalmodel and worldenergydata capabilities published on the aceengineer website.
**Follow-up signal**: This content was written once but the standard has risen — the website overhaul (WRK-146 pending) requires updated positioning. The original content described capabilities that have since been significantly extended (WRK-155, WRK-157, WRK-190, WRK-194, WRK-218 etc.). The marketing content is now outdated relative to what the platform can actually do.
**Suggested action**: Fold into WRK-146 — as part of the website overhaul, generate fresh capability descriptions from the current skill catalog and module inventory; agents can draft the updated copy from the existing module documentation.

---

### WRK-074 — Marine Safety Database Importers (MAIB, IMO, EMSA, TSB)
**Original delivery**: Complete marine safety database importers with real data validated (WRK-152 confirmed).
**Follow-up signal**: Four international marine safety databases are now importable but there is no cross-database correlation analysis tool. The original marine safety case study (WRK-079) connected OSHA and BSEE — a similar cross-database case study combining MAIB/IMO/EMSA/TSB would be a compelling client-facing asset and would directly support the aceengineer website.
**Suggested action**: New WRK — create a cross-database marine safety case study combining MAIB, IMO, EMSA, and TSB data; publish on the aceengineer website; agents can generate the analysis automatically from the existing importers.

---

### WRK-078 — Energy Data Case Study: BSEE Field Economics with NPV/IRR
**Original delivery**: BSEE field economics case study with NPV/IRR workflow published.
**Follow-up signal**: WRK-153 (pending: re-create this case study) exists as a separate item, suggesting the original is stale or needs updating. With WRK-019 (cost data layer) and WRK-171 (cost calibration) pending, there will be a significantly richer cost data foundation in 2–3 months. The case study should be rebuilt on that foundation, not the current proxy-based estimates.
**Suggested action**: Close WRK-153 as superseded — defer the case study rebuild to after WRK-019 and WRK-171 are delivered; the result will be substantially more credible with calibrated cost data.

---

### WRK-083 — Multi-Format Export (Excel, PDF, Parquet) with Real BSEE Data
**Original delivery**: Validated multi-format export capability with real BSEE data.
**Follow-up signal**: Format export was validated but not wrapped as a skill. Agents producing client deliverables need to export results in the appropriate format without manual intervention. The export capability should be an automatic output step in every analysis pipeline, not a manual call.
**Suggested action**: New WRK — register the multi-format export as an automatic pipeline output stage; agents should call `export_report(result, formats=['xlsx','pdf','parquet'])` as the final step of every analysis; wire it into the BSEE pipeline and fatigue module.

---

### WRK-093 — Dynacard AI Diagnostics
**Original delivery**: Improved dynacard AI diagnostics for pump card pattern recognition.
**Follow-up signal**: The dynacard diagnostics were improved but the module is disconnected from any agent-callable workflow. With improved multimodal models in 3–4 months, dynacard card pattern recognition could be significantly more accurate using vision models rather than manual heuristics. The current implementation may become a good baseline for comparison.
**Suggested action**: New WRK — evaluate replacing or augmenting dynacard heuristics with vision model classification (GPT-4V / Claude Vision); benchmark against the current WRK-093 implementation; this is a clear case where model improvements create a step change in capability.

---

### WRK-096 — worldenergydata Module Structure Review
**Original delivery**: Module structure review and improvement for discoverability in worldenergydata.
**Follow-up signal**: Like WRK-066 for digitalmodel, the module structure review is now outdated — significant new modules have been added (NCS/WRK-190, Brazil ANP/WRK-194, adapters/WRK-018). The module index needs to be regenerated and the discoverability improvements re-applied.
**Suggested action**: New WRK — re-run the module discoverability review for worldenergydata after all the new data source modules are in place; generate a machine-readable module manifest; fold into the skills knowledge graph.

---

### WRK-097 — Three-Tier Data Residence Strategy
**Original delivery**: Implemented the three-tier data residence strategy between worldenergydata and digitalmodel.
**Follow-up signal**: The data residence strategy was implemented but WRK-200 (filesystem naming cleanup, still working) may have affected the tier boundaries. Additionally, the strategy was never extended to assethold — which has its own data (daily_strategy, stocks, property) that should be tier-classified.
**Suggested action**: New WRK — audit data residence tier compliance after WRK-200 (naming cleanup) is complete; extend the three-tier classification to assethold; generate a data residence compliance report agents can check.

---

### WRK-103 — Heavy Construction/Installation Vessel Data
**Original delivery**: Heavy construction and installation vessel data added to worldenergydata.
**Follow-up signal**: Vessel data is a static dataset that was added once; with the GIS skill (WRK-020 pending), this vessel data should be mappable — showing vessel locations and operational areas on a GIS map. Additionally, the vessel data has not been connected to the BSEE pipeline or the deployment analysis (WRK-036).
**Suggested action**: New WRK — connect the heavy vessel dataset to the GIS skill (WRK-020) and BSEE field pipeline; enable agents to query "which vessels operate in [field area]" as an integrated analysis step.

---

### WRK-105 — Drilling Riser Component Data
**Original delivery**: Drilling riser component data (catalog of standard components) added to worldenergydata.
**Follow-up signal**: Riser component data is in worldenergydata but the riser analysis (WRK-046 pending) doesn't reference it yet. The data should feed directly into the OrcaFlex drilling riser parametric analysis — the component catalog defines the valid parameter ranges for the campaign matrix.
**Suggested action**: Extend WRK-046 — wire the worldenergydata riser component catalog into the OrcaFlex drilling riser parametric analysis as the source of truth for component dimensions and material properties.

---

### WRK-110 — Hull Size Library (FST, LNGC, OrcaFlex Benchmark Shapes)
**Original delivery**: Expanded hull size library with FST, LNGC, and OrcaFlex benchmark shapes.
**Follow-up signal**: The hull library was expanded but has no agent-callable lookup interface. Agents setting up hydrodynamic analyses need to select a hull form from the library; currently this requires manual inspection of the catalogue. With WRK-106 (hull panel geometry generator pending), the library should be the source that feeds the panel generator automatically.
**Suggested action**: New WRK — build a hull library lookup skill: given target dimensions, returns the closest matching hull form from the library; agents use this as the first step in any hydrodynamic analysis setup.

---

### WRK-113 — Always-Current Data Index with Freshness Tracking
**Original delivery**: Maintained always-current data index with freshness metadata and source information.
**Follow-up signal**: The freshness index was built but not integrated into session start. WRK-224 (tool-readiness skill) checks CLI and tooling; the data freshness index should be an additional readiness signal — if key data sources are stale by more than N days, session start should warn the agent.
**Suggested action**: Extend WRK-224 — add data freshness check to the tool-readiness skill; surface stale datasets at session start alongside CLI health; threshold: warn if any critical data source is more than 30 days old.

---

### WRK-115 / WRK-116 / WRK-117 — Hull Library RAO Linking, Scaling, and Mesh Refinement
**Original delivery**: RAO data linked to hull shapes (WRK-115), hull panels scaled to target dimensions (WRK-116), and mesh refinement/coarsening for convergence (WRK-117).
**Follow-up signal**: Together these three items constitute a complete hull analysis preparation workflow (select → scale → mesh → link RAO). This should be wrapped as a single "hull analysis setup" skill that agents invoke as one step, not three separate manual operations.
**Suggested action**: New WRK — create a "hull analysis setup" skill that chains WRK-115/116/117 into a single agent-callable workflow: `setup_hull_analysis(target_dimensions) → (scaled_mesh, rao_data)`; register in the skills catalog; this makes WRK-043 and WRK-126 execution fully agentisable.

---

### WRK-127 — Sanitize and Categorize Ideal spec.yml Templates for OrcaFlex
**Original delivery**: Sanitised and categorised reference spec.yml templates for all OrcaFlex structure types.
**Follow-up signal**: The templates exist but are not connected to a template selection skill. When an agent starts a new OrcaFlex analysis, it should be able to call `get_orcaflex_template(structure_type='riser')` and receive the appropriate sanitised template rather than starting from scratch or copying manually.
**Suggested action**: New WRK — build an OrcaFlex template library skill: given a structure type, returns the canonical spec.yml template; register alongside the existing OrcaFlex modular generator skill; this dramatically reduces setup time for new analysis models.

---

### WRK-138 — FFS Module Enhancement (Wall Thickness Grid, Industry Targeting, Asset Lifecycle)
**Original delivery**: FFS (Fitness-for-Service) module enhanced with wall thickness grid input, industry targeting, and asset lifecycle framing.
**Follow-up signal**: WRK-138 delivered the Phase 0 foundation for FFS; WRK-156 (pending) is Phase 1. With the FFS skill (WRK-206) already registered and the design code versioning (WRK-145) delivered, there is now enough infrastructure to make FFS a fully agent-callable assessment workflow. The current state is "capability exists but needs a callable interface."
**Suggested action**: Accelerate WRK-156 — the FFS infrastructure is ready; Phase 1 wall thickness grid + Level 1/2 accept-reject workflow is the next concrete deliverable; completing it makes FFS a complete, agent-callable engineering assessment.

---

### WRK-145 — Design Code Versioning (Handling Changing Revisions of Standards)
**Original delivery**: Design code version management system for tracking edition changes (DNV-ST-F101, API RP 2RD, BS 7910 etc.).
**Follow-up signal**: Design code versioning was delivered but WRK-176 (pending: design code version guard at session start) is still not implemented. The guard would use the versioning system to alert agents when codes have been superseded — closing a safety-critical gap. These two items should be tightly linked.
**Suggested action**: Fast-track WRK-176 — the design code versioning system (WRK-145) provides all the data needed; WRK-176 is just a session-start hook that queries it; this is a 1–2 hour implementation with high safety value.

---

### WRK-157 — Fatigue Analysis Module Enhancement (S-N Curves, Parametric Sweeps)
**Original delivery**: Fatigue analysis module enhanced with S-N curve reporting, parametric sweeps, and design code report (676 tests, all phases complete per memory).
**Follow-up signal**: The fatigue module is comprehensive (676 tests) but is not yet wrapped as a complete agent-callable skill with documented input/output contract. Agents running fatigue assessments need a clear invocation pattern. Additionally, the parametric sweep output format should be compatible with the multi-format export (WRK-083) so client reports can be auto-generated.
**Suggested action**: New WRK — create a "fatigue assessment skill" wrapping the full module; document the input schema, S-N curve selection logic, and expected output; wire into the multi-format export (WRK-083) for auto-generated PDF/Excel client reports.

---

### WRK-158 — Wall Thickness Parametric Engine (Cartesian Sweep)
**Original delivery**: Parametric engine for Cartesian sweeps across D/t ratio, pressure, and material parameters for wall thickness analysis.
**Follow-up signal**: The parametric engine is a building block that should be composed with the campaign infrastructure in digitalmodel. With the OrcaFlex campaign generator (WRK-032) and the wall thickness engine, there is now enough infrastructure to build end-to-end parametric engineering study workflows — but they are disconnected silos.
**Suggested action**: New WRK — create a unified parametric study coordinator that can run Cartesian sweeps across both OrcaFlex models (WRK-032 campaign) and wall thickness / fatigue parameters (WRK-158 engine); agents orchestrate the full study with one invocation.

---

### WRK-164 — Well Production Test Data Quality and Nodal Analysis Foundation
**Original delivery**: Well production test data quality module and nodal analysis foundation in worldenergydata.
**Follow-up signal**: Nodal analysis foundation was built but not yet connected to the drilling economics analysis (WRK-219 pending) or the well bore design (WRK-218 pending). Production test data quality is a critical input to decline curve analysis (WRK-077 archived/wired) and NPV calculations. The foundational work should now be extended into these connected analyses.
**Suggested action**: Extend WRK-218 and WRK-219 — connect the nodal analysis foundation (WRK-164) as the production profile input to well bore design hydraulics and batch drilling economics; the data quality layer ensures inputs are validated before economic analysis.

---

### WRK-172 — AI Agent Usage Tracking (Quota Display, OAuth API, Session Hooks)
**Original delivery**: Real-time quota display, OAuth API integration, and session hooks for AI agent usage tracking.
**Follow-up signal**: Usage tracking was built but WRK-207 (pending: fix weekly reporting bug) shows it is still not fully reliable. More importantly, WRK-237 (pending: provider cost tracking per session and per WRK item) is a natural extension — the infrastructure from WRK-172 should feed granular cost attribution per WRK item, which doesn't exist yet.
**Suggested action**: Accelerate WRK-207 + WRK-237 in sequence — fix the weekly reporting bug (WRK-207) first, then extend to per-WRK cost attribution (WRK-237); together they close the "how much did each work item cost to execute?" visibility gap.

---

### WRK-179 — Agent Capacity Pre-flight Start Hook
**Original delivery**: Session-start pre-flight hook checking agent capacity (quota, CLI health).
**Follow-up signal**: The pre-flight hook checks capacity but WRK-175 (pending: engineering context loader) and WRK-176 (pending: design code version guard) should also run at session start. The pre-flight should be extended into a comprehensive session readiness suite rather than growing as separate hooks.
**Suggested action**: Extend WRK-230 (pending: holistic session lifecycle) — consolidate WRK-179 pre-flight, WRK-175 context loader, WRK-176 version guard, and WRK-224 tool-readiness into a single unified session-start sequence; one hook to rule them all.

---

### WRK-184 / WRK-187 — /improve Skill Enhancements
**Original delivery**: /improve skill enhanced with bug fixes, recommendations output, startup readiness (WRK-184) and usage-based skill health, retry classification, API content application (WRK-187).
**Follow-up signal**: The /improve skill is now more capable but WRK-231 (pending: session-analysis as first-class skill) proposes mining session transcripts for improvement signals. The current /improve runs manually at session end; with session-analysis capabilities it could run continuously in the background and surface insights proactively.
**Suggested action**: Extend via WRK-231 — use session-analysis to feed /improve automatically; the /improve skill should have a "background mode" that monitors session activity and queues improvement suggestions without requiring explicit invocation.

---

### WRK-190 — NCS Production Data (NPD/Sodir)
**Original delivery**: Norwegian Continental Shelf production data module integrated from NPD/Sodir open data.
**Follow-up signal**: NCS data was integrated but not yet connected to the benchmarking capability (WRK-018 adapters) or the cost data layer (WRK-019). North Sea cost and production benchmarks are a key client deliverable — the Sodir data should feed the cross-regional benchmarking comparison directly.
**Suggested action**: Wire into WRK-019 cost layer — when WRK-019 (drilling/completion costs) is executed, the NCS data from WRK-190 should automatically populate the North Sea regional cost profile; this closes the GoM vs North Sea benchmarking gap.

---

### WRK-194 — Brazil ANP Production Data
**Original delivery**: Brazil ANP well-level monthly production data integrated from CSV sources.
**Follow-up signal**: ANP data was integrated but the ANP adapter in WRK-018 is still a skeleton (6 domains unavailable). With the production data now available, the ANP adapter should be wired to at least production data, improving coverage from 0/6 to 1/6 domains.
**Suggested action**: Extend WRK-018 ANP adapter — wire the WRK-194 production data into the ANP adapter's production domain; this is the minimal step to give the ANP adapter meaningful output.

---

### WRK-200 — Filesystem Naming Cleanup
**Original delivery**: Filesystem naming cleanup across workspace-hub, digitalmodel, worldenergydata (status: working, not yet fully complete).
**Follow-up signal**: This cleanup is an ongoing working item; the risk is that the naming conventions established here are not propagated to the test infrastructure (test paths mirror source paths). The cleanup should include a validation step that confirms all test discovery paths match the new naming scheme.
**Suggested action**: Add to WRK-200 — include a test discovery validation step as part of the naming cleanup; run `pytest --collect-only` after each rename batch to confirm no tests are lost; document the final naming convention in a coding-style rule update.

---

### WRK-205 — Skills Knowledge Graph
**Original delivery**: Skills knowledge graph with capability metadata and relationship layer beyond flat index.
**Follow-up signal**: The knowledge graph was built for skills; WRK-183 (pending: domain knowledge graph) proposes extending this to engineering concepts. The skills graph and the domain concept graph should be unified — a skill is a node in the domain graph, not a separate structure. Building two separate graphs wastes effort.
**Suggested action**: Merge WRK-183 into WRK-205 scope — extend the skills knowledge graph to include domain concept nodes (hull form, fatigue, riser, etc.) and link them to the skills that implement them; this is one graph, not two.

---

### WRK-213 — Codex Multi-Agent Roles Assessment
**Original delivery**: Assessment of Codex native role system vs workspace-hub agent skill approach for multi-agent coordination.
**Follow-up signal**: The assessment was done but the outcome (use workspace-hub agent skills, not Codex native roles) should be codified as a rule or decision record so future sessions don't re-evaluate the same question. Currently the insight lives only in the WRK file.
**Suggested action**: New WRK — write a decision record (ADR-style) for "agent coordination model choice" and add it to `.claude/docs/`; reference it from the agent-library README; prevents repeated re-evaluation of settled architectural questions.

---

### WRK-216 — Subagent Learning Capture
**Original delivery**: Mechanism for subagents to emit learning signals to pending-reviews before task completion.
**Follow-up signal**: Signals are emitted but the downstream processing (turning signals into skill updates) is manual. WRK-231 (pending: session-analysis skill) should consume these learning signals and automatically propose skill updates — closing the feedback loop from subagent execution to skill improvement.
**Suggested action**: Wire into WRK-231 — session-analysis should consume pending-reviews from WRK-216 as input signals; the learning capture is only valuable if downstream processing is automatic.

---

### WRK-222 — Pre-clear Session Snapshot (/save skill)
**Original delivery**: Session snapshot capability with /save skill and save-snapshot.sh script.
**Follow-up signal**: Session snapshots are taken but not yet mined for patterns. WRK-231 (pending: session-analysis) should read session snapshots as its primary input — the snapshot format should be designed to be machine-parseable for session analysis, not just human-readable.
**Suggested action**: Coordinate with WRK-231 — ensure the snapshot format (WRK-222) is parseable by the session-analysis skill (WRK-231); define a snapshot schema that includes tool calls, file diffs, WRK items touched, and elapsed time; this is the data foundation for the self-improving loop.

---

### WRK-223 — Workstations Registry
**Original delivery**: Hardware inventory, hardware-info.sh, and ace-linux-1 specs registered as a workstation registry.
**Follow-up signal**: The registry was created but WRK-050 (hardware consolidation, still pending) has not yet been executed. The registry should drive the hardware consolidation plan — agents should query it to identify underutilised machines and recommend repurposing. Currently it's read-only reference data.
**Suggested action**: Connect to WRK-050 — use the workstations registry as the input for the hardware consolidation plan; agents can query the registry, identify gaps in dev environment readiness, and propose prioritised actions.

---

## Items Reviewed With No Follow-up
97 archived items reviewed with no significant follow-up signal. These include:

- Completed personal/household items (WRK-001, WRK-002, WRK-003, WRK-004, WRK-007): fully done, no engineering follow-up.
- Merged/superseded items (WRK-033, WRK-034, WRK-035, WRK-040, WRK-082, WRK-087): absorbed into active items.
- Simple archived administrative items (WRK-037, WRK-071, WRK-088, WRK-089, WRK-107, WRK-120): one-time tasks, no follow-up value.
- Completed tooling/governance items that are now standard practice (WRK-134, WRK-185, WRK-186, WRK-201, WRK-207, WRK-208, WRK-209, WRK-210, WRK-211, WRK-212, WRK-215, WRK-217, WRK-224): delivered and embedded in workflow; no new work suggested.
- Benchmarking sub-items for AQWA/OrcaWave where the parent work (WRK-026 suite) has a follow-up noted above (WRK-025, WRK-027, WRK-028, WRK-029, WRK-030, WRK-031): covered by the parent item follow-up.
- Analysis pipeline sub-items absorbed into larger deliverables (WRK-057, WRK-058, WRK-059, WRK-060, WRK-061, WRK-062, WRK-063): follow-up covered by WRK-026 entry.
- Coverage improvement items for aceengineer-admin and aceengineer-website (WRK-055, WRK-056): low-value targets; test coverage for website and admin repos is not a strategic priority.
- Session management / administrative snapshots (WRK-124): auto-generated session file; no follow-up.
- Standard data quality and import fixes (WRK-160, WRK-161): completed cleanup; no new work.
- Dynacard module direction (WRK-049, WRK-091, WRK-092): direction decided and implemented; no further follow-up beyond the WRK-093 vision model evaluation noted above.
- CI/CD and repo maintenance (WRK-086, WRK-154): completed infrastructure items; no new work.
- Context budget and rules trimming (WRK-186): completed housekeeping; no follow-up.
- Sodir NCS data (WRK-190): follow-up already captured above; not double-counted.
- Skill maintenance items (WRK-187, WRK-205, WRK-206, WRK-207): covered above or self-contained.
- Hull mesh items (WRK-100, WRK-114, WRK-132): merged into the hull library follow-up (WRK-110/115/116/117 entry above).
- OrcaFlex spec templates (WRK-127): covered in WRK-127 entry above.
- Remaining data acquisition items (WRK-135): XLS rig fleet data ingestion was archived; data is in worldenergydata via other means.
- Archived architecture items (WRK-139): unified multi-agent architecture was superseded by existing workspace-hub approach.
- gmsh skill (WRK-139-gmsh): covered by WRK-140 (pending: gmsh integration); no additional follow-up.
- Anthropic outreach (WRK-142): personal/business development; done.
- M-T envelope (WRK-143): specific analysis deliverable; no follow-up.
- Wall thickness archived item (WRK-144): superseded by WRK-155 (DNV-ST-F101) which is complete.
- Workforce/business items (WRK-108, WRK-122, WRK-134): completed; no engineering follow-up.
- uv enforcement (WRK-209): completed; standard practice now.
