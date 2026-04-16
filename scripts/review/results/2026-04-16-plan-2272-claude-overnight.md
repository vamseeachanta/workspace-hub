# Overnight Claude Review — Plan #2272

> **Date:** 2026-04-16
> **Context:** Overnight planning review pass
> **Plan reviewed:** `docs/plans/2026-04-16-issue-2272-repeatable-openfoam-and-blender-smoke-verification.md`
> **Prior reviews:** None (initial draft)

## Verdict: MINOR (blocked)

## Assessment

The plan is well-structured and correctly identifies the dependency chain: #2272 cannot be implemented until #2269 (OpenFOAM baseline) and #2270 (Blender baseline) produce the per-tool validators. The unified runner design is pragmatic — it aggregates existing per-tool validators rather than reimplementing solver-level logic. The Resource Intelligence Summary cites 9 distinct sources. The dependency graph is clearly documented.

### Strengths

1. **Dependency chain is explicit.** The plan clearly states the BLOCKER on #2269 and #2270, includes a visual dependency graph, and separates plan approval (can proceed now) from implementation (gated on dependencies).
2. **Three exit codes (0/1/2) provide clean error stratification.** Overall pass (0), tool failure (1), and runner-level error (2) enable callers to distinguish between solver issues and infrastructure issues.
3. **Partial runs (`--tool openfoam|blender|all`) are well-designed.** This enables incremental verification as each tool's baseline is completed, avoiding an all-or-nothing gate.
4. **Drift detection is scoped correctly.** On-demand re-run with version comparison is the simplest useful approach; scheduling is correctly deferred to a follow-up.
5. **Fixture-based testing is appropriate.** Since the unified runner aggregates verdicts from per-tool validators, testing against fixture YAML files is sufficient without requiring live solver execution.

### Issues requiring revision

1. **Consolidated verdict schema should inherit constraints from per-tool schemas.** The plan defines a consolidated schema but does not specify how it handles schema version mismatches between the OpenFOAM verdict (#2269) and Blender verdict (#2270). Resolution: add a "schema compatibility" note specifying that the unified runner validates per-tool verdicts against a minimum expected schema before aggregating.

2. **The `--json` flag adds a third output format (YAML + terminal + JSON).** This may be premature for a first implementation. Resolution: consider whether `--json` should be a stretch goal or required for v1. If required, specify the exact JSON schema (is it the same as YAML but in JSON format?).

3. **Drift detection logic is underspecified.** The pseudocode mentions "compare current consolidated-verdict.yaml against a known-good reference" but does not define where the reference lives, how it is established, or what constitutes a meaningful drift (version change only, or also timing/output changes?). Resolution: add a "reference verdict" section specifying the path (e.g., `tests/portability/fixtures/reference-verdict.yaml`), how it is created (manual snapshot after first successful run), and what fields are compared.

4. **No error handling for partial tool availability.** If OpenFOAM is installed but Blender is not (or vice versa), the `--tool all` mode should gracefully handle the missing tool as SKIPPED rather than crashing. The pseudocode does not address this. Resolution: add explicit handling for missing validator scripts when running in `all` mode.

5. **Human-readable output format is described but not specified.** The pseudocode says "print summary table" but does not specify column widths, alignment, or whether ANSI colors are used. Resolution: this is low priority but should at least specify "plain text, no ANSI colors when piped" for CI compatibility.

### Blocker assessment

- **#2269 (OpenFOAM baseline):** Currently at `plan-review` status with three rounds of adversarial review completed. Not yet `plan-approved`. Estimated 1-2 more revision cycles before implementation can begin.
- **#2270 (Blender baseline):** Plan drafted today (2026-04-16), at `draft` status. Requires minor revisions, adversarial review, approval, and implementation. Estimated 3-5 days minimum before the validator exists.
- **Net effect:** #2272 implementation is likely 1-2 weeks away. Plan approval can proceed in parallel.

### Retrieval adequacy

- **adequate** — 9 distinct sources with specific file paths and findings. The plan correctly cross-references both dependency plans and all relevant portability/engineering docs.

### Recommendation

**approval-ready after minor revisions** — Address the 5 items above (schema compatibility, JSON flag scope, drift detection specifics, partial tool availability, output format) and the plan can advance to adversarial review. Implementation remains blocked on #2269 and #2270.

**Execute tomorrow?** No — plan is blocked on dependencies. Can proceed with adversarial review in parallel with dependency work.
