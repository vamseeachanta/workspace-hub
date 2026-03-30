# Pitfalls Research

**Domain:** OrcaWave automation, report generation, sensitivity analysis, batch processing for hydrodynamic analysis
**Researched:** 2026-03-29
**Confidence:** HIGH (based on direct codebase evidence from prior failed/stalled attempts + official Orcina documentation)

## Critical Pitfalls

### Pitfall 1: Non-Deterministic LLM Output for YAML Generation

**What goes wrong:**
LLM-generated OrcaWave YAML files are not semantically reliable. The prior approach (documented in the pending todo `2026-03-26-automate-orcawave-vessel-hull-analysis-on-licensed-machine.md`) required "100% semantic match against benchmarks" but LLMs produce non-deterministic output -- key ordering changes, value formatting varies (e.g., `1.0` vs `1.00000`), PascalCase inconsistencies in OrcaWave keys, and occasional hallucinated parameters. Even when output parses as valid YAML, the semantic content may differ in ways that affect solver behavior (e.g., wrong SolveType, missing QTF parameters).

**Why it happens:**
LLMs treat YAML generation as text completion, not schema-constrained data transformation. Temperature > 0 introduces variation. Even at temperature 0, model updates change output. OrcaWave YAML has strict PascalCase key conventions and solver-specific value types (`Yes`/`No` not `true`/`false`, specific enum strings like "Full QTF calculation" vs "Potential and source formulations") that LLMs approximate but do not guarantee.

**How to avoid:**
Replace LLM-based generation with deterministic template-based generation:
1. Define a canonical `DiffractionSpec` (already exists as Pydantic v2 schema in `input_schemas.py` with 655 lines, 20 sub-models, 9 enums)
2. Use the existing `OrcaWaveBackend` (586 lines in `orcawave_backend.py`) for spec-to-YAML conversion
3. Parametric updates are dictionary merges on the canonical spec, not LLM text generation
4. Validation: round-trip test (spec -> YAML -> reverse parse -> spec comparison) catches drift

The architecture already exists (WRK-026 diffraction-spec-converter, status: implemented). The pitfall is deciding to use LLMs for YAML generation instead of using the existing deterministic converter pipeline.

**Warning signs:**
- Any pipeline step that calls an LLM to produce a YAML file instead of using `SpecConverter`
- Semantic comparison tests showing "cosmetic" diffs that are actually value changes
- Different output on re-runs of the same input

**Phase to address:**
Phase 1 (Foundation) -- establish the deterministic generation pipeline as the sole path. No LLM-in-the-loop for YAML production.

---

### Pitfall 2: OrcaWave Frequency Unit Convention Mismatch (Hz Descending vs rad/s Ascending)

**What goes wrong:**
OrcFxAPI returns frequency data in **Hz, descending order** (highest frequency first). The rest of the engineering ecosystem (Capytaine, BEMRosetta, WAMIT, the canonical `DiffractionSpec`, numpy convention) uses **rad/s, ascending order**. If frequency arrays are consumed without conversion, RAO plots are mirrored, interpolation produces wrong results, and benchmark comparisons fail silently because correlations still compute (just against wrong frequency pairings). This was caught late in prior work (documented in `doc-intelligence-report.yaml`: "Capytaine uses rad/s internally (unlike OrcFxAPI which uses Hz descending)").

**Why it happens:**
OrcFxAPI follows Orcina's convention (periods/frequencies in the OrcaWave GUI default to Hz). Engineers loading results via `diff.frequencies` or `diff.periodsOrFrequencies` get Hz-descending arrays and pass them downstream without noticing the convention difference. The values themselves look plausible (they are valid frequencies), so the error is not caught by range checks.

**How to avoid:**
1. A single `normalize_frequencies()` function that always converts to rad/s ascending, called at every boundary where OrcFxAPI data enters the pipeline
2. Assert monotonically increasing rad/s in every function that consumes frequency arrays (fail loudly on descending input)
3. Unit metadata on every frequency array (not just values, but `FrequencyArray(values=[...], unit="rad/s", order="ascending")`)
4. The existing `orcawave_backend.py` already handles unit conversion -- ensure ALL extraction paths use it, not raw OrcFxAPI property access

**Warning signs:**
- RAO plots that look "mirrored" compared to literature
- Benchmark comparisons showing low correlation despite visually similar shapes
- Frequency arrays that decrease from left to right

**Phase to address:**
Phase 1 (Foundation) -- unit normalization at the OrcFxAPI boundary. Every downstream consumer receives normalized data.

---

### Pitfall 3: QTF Parameter "Change Not Allowed" Errors

**What goes wrong:**
Setting QTF-related parameters (e.g., `QTFMinCrossingAngle`, `QTFFrequencyTypes`, `FreeSurface*` zone keys) on an OrcaWave model where `SolveType` is not "Full QTF calculation" triggers "Change not allowed" errors via OrcFxAPI. The OrcaWave data model enforces parameter dependencies at the API level -- certain data items are read-only unless prerequisite settings are active. The converse also applies: a restart analysis from a "potential formulation only" parent cannot switch to full QTF.

This was discovered and documented in the `piped-splashing-peacock` plan, where cases 3.2 and 3.3 had residual semantic diffs because the comparison logic was reading the wrong model's `SolveType` to determine which keys were dormant.

**Why it happens:**
OrcaWave's data model has conditional parameter visibility. The API enforces this as runtime errors, not schema-level validation. When generating YAML programmatically or parametrically updating models, the code may set parameters in wrong order (SolveType must be set before QTF parameters) or set QTF parameters that are irrelevant for the current solve type. The official docs confirm: "if parent uses 'potential formulation only,' restart must match this" and "if parent has damping lid, restart cannot use 'full QTF calculation.'"

**How to avoid:**
1. Parameter dependency graph: define which parameters require which prerequisite settings
2. Set parameters in dependency order: `SolveType` first, then QTF parameters only if applicable
3. Guard QTF parameter writes behind `if solve_type == "Full QTF calculation":` checks
4. The existing `_DORMANT_QTF_KEYS` set in the validation script documents 20+ keys that are only meaningful when QTF is active -- use this as the guard list
5. When comparing YAML configs, use the **spec's** SolveType (not the OWD's) to determine dormant keys (the bug that was fixed in `piped-splashing-peacock`)

**Warning signs:**
- OrcFxAPI raising exceptions when loading generated YAML files
- Semantic comparison showing "significant" diffs for QTF keys when the analysis does not use QTF
- Generated YAML files that include QTF-specific keys for non-QTF analyses

**Phase to address:**
Phase 1 (Foundation) -- parameter dependency model. Phase 2 (Sensitivity Analysis) -- validate sweep parameters against dependency graph.

---

### Pitfall 4: Solver Not Verified on Target Machine Before Pipeline Development

**What goes wrong:**
The WRK-031 Phase 3 (3-way benchmark) stalled because solver installations were not verified on the target machine (`licensed-win-1`). Development proceeded on Linux (`dev-primary`) building the framework, comparator, and plotter (43 tests, all passing with synthetic data), but the actual solver execution step could not be tested because: (a) OrcaWave requires OrcFxAPI DLL which is Windows-only, (b) AQWA and BEMRosetta installations were unverified, (c) license availability was not confirmed. Phase 3 status remains "PENDING" with 6 next-steps all blocked on "verify solver installations on target machine."

**Why it happens:**
Natural tendency to build the framework first (it is satisfying, testable, and can be done locally) while deferring the hard integration step. Licensed software adds friction: remote desktop access via TightVNC, single-seat licenses, coordination with other users (documented in WRK-121). The machine inventory (`licensed-win-1.md`) still has 8 pending action items including "Verify OrcaFlex / OrcaWave license server config."

**How to avoid:**
1. Verify solver execution on target machine as the **first** task, not the last
2. Smoke test: `Diffraction()` constructor, `LoadData()` a known .owd, `Calculate()`, extract one result -- before writing any framework code
3. Document exact command to verify: `python -c "import OrcFxAPI; d = OrcFxAPI.Diffraction(); d.LoadData('test.owd'); print(d.state)"`
4. License availability check: confirm single-seat license access, document coordination protocol
5. Gate: no batch processing development until smoke test passes on licensed machine

**Warning signs:**
- All tests use synthetic data with no integration tests on real solver
- "Need to verify" appears in plans
- Framework code grows while integration code stays empty
- Development happening exclusively on Linux while execution target is Windows

**Phase to address:**
Phase 0 (Pre-work) -- solver verification gate before any milestone development begins.

---

### Pitfall 5: Batch Report Generation Without Per-Case Correctness Gates

**What goes wrong:**
The prior attempt tried to "batch-generate reports for all examples but couldn't ensure 100% correctness." With 200+ configurations, the failure mode is not that reports fail to generate -- it is that they generate with subtle errors that look correct. Examples: wrong vessel name in report header, RAO plot for heading 0 degrees labeled as 180 degrees, hydrostatic table using wrong reference point, QA summary showing "PASS" when results actually deviate from benchmark. At scale, manual review of each report is infeasible, so errors propagate to clients.

**Why it happens:**
Report generation is treated as a formatting step rather than a verified data pipeline. HTML templates render whatever data they receive -- they do not validate engineering content. When generating reports at scale, edge cases that were handled manually for individual reports are missed: multi-body models with different conventions, models with partial results (only radiation, no diffraction), models with non-standard symmetry settings.

**How to avoid:**
1. Per-case correctness assertion suite: before report generation, run automated checks on extracted results
   - Frequency array is monotonic, within expected range, correct units
   - RAO values are physically plausible (heave RAO near 1.0 at low frequency for floating body)
   - Added mass matrix is symmetric, positive semi-definite at low frequency
   - Report metadata matches source model (vessel name, water depth, heading list)
2. Golden reference reports: maintain 3-5 verified benchmark reports, run diff against generated output
3. Incremental rollout: generate and verify 5 reports manually, then 20, then all -- not straight to 200+
4. QA flag system: each report gets a confidence score (VERIFIED/UNVERIFIED/FLAGGED) based on automated checks

**Warning signs:**
- "Generate all reports" task with no verification step defined
- Reports that render without errors but have never been manually reviewed
- No golden reference reports to diff against
- Batch job producing 200 reports with 0 failures (suspiciously clean)

**Phase to address:**
Phase 2 (Report Generation) -- correctness gate before batch scaling. Phase 3 (Batch Processing) -- automated verification suite.

---

### Pitfall 6: Cross-Platform Path and DLL Loading Failures (Linux Dev to Windows Execution)

**What goes wrong:**
Development happens on Linux (`dev-primary`, the orchestration machine) but execution must happen on Windows (`licensed-win-1`). Path separators (`/` vs `\`), file system case sensitivity (Linux is case-sensitive, Windows NTFS is case-preserving but case-insensitive), DLL loading (OrcFxAPI is a Windows DLL), and environment differences (Python paths, `uv` behavior, TLS certificates) all create failures that do not manifest during development. The 2026-03-29 synthesis research flagged: "uv 0.11.0 TLS change could break uv sync on licensed-win-1."

**Why it happens:**
Linux development is comfortable and fast (no license constraints, no remote desktop). Code is written and tested locally with mocks/synthetic data, then deployed to Windows for actual execution. Path construction using `os.path.join` or `pathlib.Path` works differently. File references in YAML configs may use Linux paths that break on Windows. The `OrcFxAPI` import itself fails on Linux (DLL not available), requiring conditional imports or mocks.

**How to avoid:**
1. Use `pathlib.Path` exclusively (never string concatenation for paths)
2. YAML configs use relative paths only -- no absolute paths in generated files
3. Conditional OrcFxAPI import pattern: `try: import OrcFxAPI except ImportError: OrcFxAPI = None` with clear error messages
4. CI matrix: test on both Linux (unit tests with mocks) and Windows (integration tests with real solver) -- GitHub Actions supports Windows runners
5. File case consistency: enforce lowercase for all generated file names
6. Separate "generation" (runs anywhere) from "execution" (requires licensed machine) cleanly in architecture
7. Test the `uv sync` command on `licensed-win-1` before depending on it for package installation

**Warning signs:**
- Tests pass on Linux but fail on Windows with `FileNotFoundError` or `ImportError`
- Hardcoded paths with `/` in configuration files
- OrcFxAPI import at module level (crashes import on Linux)
- No Windows CI runner configured

**Phase to address:**
Phase 1 (Foundation) -- cross-platform compatibility layer. Phase 0 (Pre-work) -- verify uv/Python/OrcFxAPI on licensed machine.

---

### Pitfall 7: Sensitivity Analysis Parameter Space Explosion

**What goes wrong:**
Sensitivity analysis with multiple parameters creates a combinatorial explosion. For a hydrodynamic analysis, varying water depth (5 values) x wave period range (5 configurations) x heading set (4 configurations) x mesh refinement (3 levels) = 300 OrcaWave runs, each taking 5-60 minutes depending on mesh size and QTF settings. A full QTF analysis on a 1500-panel spar mesh can take 2+ hours per case. The sensitivity study becomes infeasible or ties up the licensed machine for days.

**Why it happens:**
One-at-a-time (OAT) sensitivity is straightforward but does not capture interactions. Full factorial design captures everything but is computationally prohibitive. Engineers default to full factorial or do not plan the DOE (Design of Experiments) before launching runs.

**How to avoid:**
1. OAT first: vary one parameter at a time around a base case to identify which parameters actually matter
2. Screen before sweep: use coarse mesh (100-200 panels) for screening, fine mesh only for final analysis
3. Fractional factorial or Latin Hypercube Sampling (LHS) for multi-parameter studies
4. Time estimation before launch: `n_cases * estimated_minutes_per_case` with buffer for failures
5. Checkpoint/resume: save intermediate results so a crash does not require restarting from scratch
6. Prioritize: sensitivity of RAOs to water depth is well-known (minimal for deep water) -- do not sweep parameters that engineering judgment already bounds

**Warning signs:**
- Sensitivity study plan with > 50 cases and no time estimate
- Full factorial design as the default
- No screening step before detailed sweep
- Single-threaded execution of independent cases on a 64-core machine

**Phase to address:**
Phase 2 (Sensitivity Analysis) -- DOE planning tool with time estimator.

---

### Pitfall 8: Report Template Coupling to Data Model Schema

**What goes wrong:**
The report HTML template directly accesses data model attributes. When the data model schema changes (e.g., adding a new DOF, changing from `vessel_name` to `body_name` for multi-body support, restructuring frequency storage), every report template breaks. This was observed in the WRK-129 OrcaFlex reporting spec, which required 14 iterations of review to stabilize the data model and template interaction -- and that was for a spec, before implementation.

**Why it happens:**
HTML templates are tightly coupled to Python data models. Template engines (Jinja2 or raw f-strings) reference attribute names directly. No intermediate "view model" or "report context" layer isolates the template from the data model. When the data model evolves (it will -- multi-body support, new result types, OrcaFlex vessel type export), templates silently produce empty sections or crash.

**How to avoid:**
1. Report context layer: a dedicated `ReportContext` dataclass that the template renders, populated from the data model but decoupled from it
2. Template validation: test that all template variables are populated (no `None` or missing keys in rendered output)
3. Golden HTML snapshots: compare rendered HTML against a known-good snapshot (ignoring dynamic content like timestamps)
4. Explicit versioning: report template version tracked alongside data model version

**Warning signs:**
- Template files referencing deep attribute chains (`result.bodies[0].raos.heave.amplitude`)
- Report rendering that silently produces empty sections instead of raising errors
- Data model changes causing template failures discovered only during manual review

**Phase to address:**
Phase 2 (Report Generation) -- report context layer as part of template design.

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Mock OrcFxAPI everywhere, never test real solver | Fast development, all tests pass on Linux | Integration failures discovered at deployment; framework code assumes wrong API behavior | Early prototyping only; must be replaced with real integration tests before batch processing |
| Store frequencies as raw floats without unit metadata | Simpler arrays, less boilerplate | Unit confusion propagates silently; the Hz/rad/s bug | Never -- always tag with units from day 1 |
| Single-file reports (inline CSS/JS/Plotly) | Easy to share, no dependencies | 3MB Plotly bundle per report x 200 reports = 600MB; slow email attachments | Acceptable with CDN default (existing pattern), inline only for air-gapped |
| Hard-code example paths in batch runner | Quick to get running | Breaks on different machines, different repo layouts | Only in throwaway scripts; production batch runner uses config-driven paths |
| Skip QTF parameter validation | Faster YAML generation | "Change not allowed" errors at runtime, wasted licensed-machine time | Never -- always validate against dependency graph |
| Generate YAML via string concatenation | No Pydantic overhead | Malformed YAML, missing keys, wrong types, no round-trip guarantee | Never -- use the existing `SpecConverter` pipeline |

## Integration Gotchas

Common mistakes when connecting to external services.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| OrcFxAPI `Diffraction` class | Setting QTF parameters before SolveType | Set SolveType first, then conditionally set QTF params. Check `SolveType` value, not presence of QTF keys. |
| OrcFxAPI `Diffraction.type` | Trying to assign `ModelType.Variation` or `ModelType.Restart` directly | Use `NewVariationModel(parentFileName)` or `NewRestartAnalysis(parentFileName)` methods instead. Direct assignment only works for `ModelType.Standard`. |
| OrcFxAPI frequency results | Consuming `frequencies` property as-is (Hz descending) | Always convert through `normalize_frequencies()`: Hz to rad/s, reverse to ascending order. |
| OrcFxAPI `reportingOrigins` | Passing wrong-shaped array to `addedMassRelativeTo()` | Must be numpy array with shape `[Nb, 3]` where Nb is number of bodies. Validate shape before calling. |
| OrcaWave YAML format | Using Python `True`/`False` or `yes`/`no` | OrcaWave expects `Yes`/`No` (PascalCase). Use the existing `orcawave_backend.py` serializer. |
| OrcaWave batch (.lst) files | Absolute paths in .lst files | Relative paths resolved against .lst file directory. Use relative paths for portability. |
| OrcaWave restart analysis | Changing mesh, water depth, or frequency range from parent | These must be identical to parent. Restart only adds QTF or changes non-structural parameters. Validated at load time. |
| OrcaWave variation models | Saving in binary (.owd) format | Binary variations do not inherit parent changes. Use YAML text format for variation models. |
| Licensed machine access | Assuming license is always available | Single-seat license, one user at a time. Check availability before launching batch. Handle `LicenseError` gracefully. |
| `uv sync` on Windows | Assuming same behavior as Linux | TLS certificate handling differs (rustls-platform-verifier in uv 0.11.0+). Test explicitly on licensed-win-1. |

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Sequential batch execution on 64-core machine | 200 cases x 15 min = 50 hours serial | OrcaWave supports `threadCount` per calculation. Run multiple independent cases in parallel (process-level parallelism for independent models, thread-level for single model). | > 20 cases |
| Full QTF for every sensitivity case | Each case takes 2+ hours instead of 10 minutes | Use "Potential and source formulations" for sensitivity screening. Full QTF only for final selected cases. | > 5 sensitivity cases with QTF |
| Loading/saving entire model per parameter change | Disk I/O bottleneck, 50ms overhead per load/save | Use variation models: base model + YAML overlay with only changed parameters. OrcaWave handles the merge. | > 50 parameter variations |
| Embedding full Plotly.js in every batch report | 3MB x 200 reports = 600MB of identical JS | Use CDN reference (`include_plotlyjs='cdn'`). Already the project convention. Inline only for air-gapped delivery. | > 10 reports |
| Extracting all results for every case | Memory spike for QTF results (large 4D arrays) | Extract only needed results (e.g., `displacementRAOs` for RAO comparison, skip `panelPressure` unless needed). Lazy extraction pattern. | Models with > 1000 panels and QTF |
| Regenerating reports from scratch on every change | Full pipeline run for a template tweak | Separate data extraction (slow, requires solver) from report rendering (fast, template-only). Cache extracted data as intermediate JSON/Parquet. | Development iteration cycle |

## Security Mistakes

Domain-specific security issues beyond general web security.

| Mistake | Risk | Prevention |
|---------|------|------------|
| Hardcoded license server credentials in scripts | Credential exposure in git history | Environment variables for all credentials. The WRK-121 audit found plaintext passwords in `acma_vpn.md` -- do not repeat this pattern. |
| HTML reports with unescaped user strings | XSS in shared reports (vessel names, analyst names, project IDs can contain malicious content) | The WRK-129 spec mandates `_escape()` helper wrapping `html.escape()` for ALL user-supplied strings. 6+ field-specific escaping tests required. Already specified -- enforce it. |
| OrcaWave .owd files containing proprietary client data | Client data leakage if example files are committed to public repo | Keep client data in private repos only. Example/benchmark files use synthetic or published geometries (unit box, standard barge, WAMIT validation cases). |
| Batch results left on shared licensed machine | Other users accessing confidential analysis results | Automated cleanup: copy results to secure storage, delete from shared machine after batch completion. |

## UX Pitfalls

Common user experience mistakes in this domain.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Report shows raw solver output (Hz descending frequency table) | Engineer expects rad/s ascending or periods; mentally converting is error-prone | Always present in user's chosen unit system with configurable axis (period vs frequency) -- already supported in `BenchmarkPlotter` |
| Sensitivity results as raw numbers only | Engineer cannot quickly identify which parameter matters most | Tornado diagram or spider plot showing parameter sensitivity ranking |
| Batch status as console log only | No visibility into which cases passed/failed, how many remain | HTML dashboard with per-case status, progress bar, links to individual reports -- like the existing `validation_summary.html` pattern |
| Error messages from OrcFxAPI passed through verbatim | Cryptic messages like "Change not allowed" without context | Wrap OrcFxAPI errors with context: "Cannot set QTFMinCrossingAngle: SolveType is 'Potential and source formulations'. QTF parameters require SolveType = 'Full QTF calculation'." |
| Report layout optimized for screen, not print | Engineers print reports for project archives; wide Plotly charts get cut off | CSS print media queries in HTML reports; A4/Letter-aware layout. The WRK-129 spec uses single-file HTML -- add `@media print` styles. |

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **YAML Generation:** Generates valid YAML that OrcaWave loads -- but does it round-trip? Load the generated YAML into OrcaWave via OrcFxAPI, save it back, diff against original. OrcaWave may normalize/reorder keys.
- [ ] **Batch Runner:** Runs all 200+ cases without errors -- but were results validated? Check that extracted RAOs are physically plausible, not just non-null. A model can "complete" but produce garbage results if mesh is inverted or frequency range misses resonance.
- [ ] **Report Generation:** Report renders in browser -- but does it render correctly in print? Open print preview, check all 6 DOF plots fit, check page breaks, check table column widths.
- [ ] **Sensitivity Analysis:** Parameter sweep completes -- but was the base case validated first? If the base case is wrong, all sensitivity deltas are meaningless.
- [ ] **Cross-Platform:** Tests pass on Linux -- but has the actual pipeline been run on `licensed-win-1`? Mock-based tests do not catch DLL loading, path separator, or license issues.
- [ ] **Frequency Handling:** Values are in correct units -- but is the array sorted correctly? A reversed array still plots (just mirrored) and still computes correlation (just against wrong pairings).
- [ ] **Multi-Body Support:** Single-body reports work -- but multi-body models have per-body meshes, per-body origins, and cross-coupling terms in the added mass matrix. Does the report handle body indexing?
- [ ] **OrcaFlex Integration:** RAOs export to OrcaFlex vessel type format -- but does OrcaFlex accept the frequency convention? OrcaFlex may expect different units or ordering than OrcaWave.
- [ ] **QTF Handling:** QTF results extract correctly -- but only when `SolveType` is "Full QTF calculation". Does the pipeline gracefully handle non-QTF models (return empty, not crash)?
- [ ] **Variation Models:** Generation works -- but are you saving as YAML text, not binary? Binary variation models do not inherit parent changes.

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Wrong frequency units propagated through pipeline | MEDIUM | Identify all downstream consumers of frequency data. Add unit normalization at source. Re-run affected analyses. Diff results before/after to confirm fix. |
| QTF "Change not allowed" errors in batch | LOW | Catch OrcFxAPI exception, log the offending parameter and current SolveType, skip the case, continue batch. Fix YAML generation logic. Re-run failed cases only. |
| Solver not installed/licensed on target machine | HIGH | Blocked until IT/licensing resolves. No workaround. Entire milestone stalls. This is why verification must be Phase 0. |
| Non-deterministic LLM output in generated YAML | HIGH | Revert to deterministic pipeline. Diff all LLM-generated files against deterministic output. Any that differ need re-generation. May require re-running analyses on licensed machine. |
| Report template breaks due to data model change | LOW | Fix template, regenerate affected reports. If report context layer exists, only the context adapter needs updating. |
| Batch produces 200 incorrect reports | HIGH | Need to identify which reports are wrong and why. If no per-case validation exists, must manually review a sample and add validation retroactively. May need to re-generate all reports. |
| Sensitivity results on wrong base case | MEDIUM | Fix base case, re-run all sensitivity deltas. Sensitivity infrastructure itself is reusable. |
| Cross-platform path failures on Windows | LOW | Fix paths to use pathlib, re-deploy. Unit tests with path validation prevent recurrence. |

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| P1: Non-deterministic LLM YAML | Phase 1 (Foundation) | Round-trip test: spec -> YAML -> reverse parse -> spec == original |
| P2: Frequency unit mismatch | Phase 1 (Foundation) | Assertion: all frequency arrays entering pipeline are rad/s ascending |
| P3: QTF "Change not allowed" | Phase 1 (Foundation) | Parametric generation test: generate YAML for every SolveType, load into OrcFxAPI without errors |
| P4: Solver not verified | Phase 0 (Pre-work) | Smoke test script runs on licensed-win-1, returns solver version and "READY" |
| P5: Batch without correctness gates | Phase 3 (Batch Processing) | Each batch report includes automated QA section with pass/fail assertions |
| P6: Cross-platform failures | Phase 0 + Phase 1 | CI matrix with Linux (mock) and Windows (real) runners; pathlib-only paths |
| P7: Sensitivity space explosion | Phase 2 (Sensitivity) | DOE planning tool produces case count and time estimate before execution |
| P8: Report template coupling | Phase 2 (Report Generation) | Template uses only `ReportContext` attributes; data model changes do not require template changes |

## Sources

- [OrcaWave Batch Processing Documentation](https://www.orcina.com/webhelp/OrcaWave/Content/html/Automation,Batchprocessing.htm) -- batch processing capabilities and limitations
- [OrcaWave Automation Introduction](https://www.orcina.com/webhelp/OrcaWave/Content/html/Automation,Introduction.htm) -- OrcFxAPI integration overview
- [OrcFxAPI Diffraction Class Reference](https://www.orcina.com/webhelp/OrcFxAPI/Content/html/Pythonreference,Diffraction.htm) -- property constraints, methods, model type restrictions
- [OrcaWave Data Model](https://www.orcina.com/webhelp/OrcaWave/Content/html/Data,Model.htm) -- parameter dependencies, restart analysis constraints
- [OrcFxAPI Python Module Reference](https://www.orcina.com/webhelp/OrcFxAPI/Content/html/Pythonreference,OrcFxAPImodule.htm) -- DLL loading, Python 3.8 bug
- [OrcFxAPI PyPI](https://pypi.org/project/OrcFxAPI/) -- version 11.6.2 (Feb 2026)
- [OrcFxAPI Python Installation](https://www.orcina.com/webhelp/OrcFxAPI/Content/html/Pythoninterface,Installation.htm) -- InstallPythonInterface.bat, DPI awareness
- Codebase: `.planning/archive/modules/wrk-031-3way-benchmark-aqwa-orcawave-bemrosetta.md` -- Phase 3 stalled, solver verification pending
- Codebase: `.planning/archive/modules/piped-splashing-peacock.md` -- QTF dormant key bug, SolveType comparison fix
- Codebase: `.planning/archive/modules/diffraction-spec-converter.md` -- existing deterministic spec-to-YAML pipeline (implemented)
- Codebase: `.planning/archive/modules/wrk-129-orcaflex-analysis-reporting.md` -- 14-iteration review, data model / template coupling
- Codebase: `.planning/archive/catalog/doc-intelligence-report.yaml` -- Hz descending vs rad/s ascending documentation
- Codebase: `.planning/todos/pending/2026-03-26-automate-orcawave-vessel-hull-analysis-on-licensed-machine.md` -- LLM-driven generation approach
- Codebase: `.planning/archive/modules/hardware-inventory/licensed-win-1.md` -- target machine capabilities and pending actions
- Codebase: `.planning/archive/modules/wrk-121-licensed-software-usage-workflow-burden-reduction.md` -- license access workflow, plaintext password issue
- Codebase: `.planning/research/2026-03-29-synthesis.md` -- uv TLS change affecting Windows machines
- [Sensitivity Analysis Best Practices (LinkedIn)](https://www.linkedin.com/advice/0/what-most-common-pitfalls-mistakes-avoid) -- OAT vs factorial design
- [Batch Error Handling Patterns](https://oneuptime.com/blog/post/2026-01-30-batch-processing-error-handling/view) -- skip/retry/checkpoint strategies

---
*Pitfalls research for: OrcaWave automation, report generation, sensitivity analysis, batch processing*
*Researched: 2026-03-29*
