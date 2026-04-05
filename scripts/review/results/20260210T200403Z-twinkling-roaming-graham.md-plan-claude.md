# Review by Claude
# Source: twinkling-roaming-graham.md
# Type: plan
# Date: 20260210T200403Z

[Claude review requires interactive session or API call]
## Content to Review
```
# Plan: Semantic Equivalence for 5 Library Models

## Context

The 5 library models (4 risers + 1 generic) currently show:
- **Path B (spec-driven)**: 4/5 pass at 0.00% tension diff, 1 fails (steep wave PenetratingLine ref)
- **Path C (modular-direct)**: 5/5 pass at 0.00%

But semantic validation of the **input YAML** shows 0/5 fully matching — the generated modular YAML has differences vs the monolithic. Many of these are stale artifacts (modular files pre-date the user's environment builder edits). The goal is to get the generated YAML semantically identical to monolithic within 1%.

**YAML format equivalence is already handled** — `yaml.safe_load()` normalizes flow arrays `[1,2,3]` vs block lists (`- 1\n- 2\n- 3`), inline vs multi-line dicts, and quoting variations to identical Python objects.

## Approach: Regenerate → Measure → Fix → Verify

### Step 1: Regenerate modular files for all 5 models

Regenerate the `modular/` directory for each library model using the current code (with user's True/False booleans, "Wave 1" name, SeabedSlopeDirection=0 edits). This eliminates stale-file artifacts.

**Models:**
- `docs/modules/orcaflex/library/tier2_fast/a01_catenary_riser/`
- `docs/modules/orcaflex/library/tier2_fast/a01_lazy_wave_riser/`
- `docs/modules/orcaflex/library/tier2_fast/a01_pliant_wave_riser/`
- `docs/modules/orcaflex/library/tier2_fast/a01_steep_wave_riser/`
- `docs/modules/orcaflex/library/model_library/a02_lazy_s_detailed/`

### Step 2: Run semantic validation to measure actual diff count

```bash
uv run python scripts/semantic_validate.py --batch docs/modules/orcaflex/library/tier2_fast \
    --batch-report benchmark_output/semantic_5models.html
```

### Step 3: Cross-review — 3 independent solutions

Give the SAME task (fix semantic equivalence for 5 library models) to 3 independent agents. Each agent proposes complete code changes. Then compare and merge the best ideas.

**Known diff categories after regeneration:**

| Category | Example | Fix Location | Impact |
|----------|---------|-------------|--------|
| **6DBuoy Mass/Volume lost** | Mass: 11.51 missing in modular | `schema/generic.py` GenericBuoy6D | HIGH |
| **CurrentProfile incomplete** | Mono=`[[0,1,0],[100,0.2,0]]`, Mod=`[[0,1.0,0]]` | `extractor.py` + `environment_builder.py` | HIGH |
| **General section cosmetic props** | DefaultViewAzimuth, DefaultViewSize missing | `general_builder.py` | LOW |
| **NorthDirection extra** | In modular but not monolithic | `general_builder.py` | LOW |
| **Line properties missing** | AsLaidTension, PreBendSpecifiedBy, etc. | Riser builders scope | MEDIUM |
| **Steep wave PenetratingLine ref** | LineContactData references monolithic line names | `extractor.py` / `generic_builder.py` | HIGH |

**3 parallel agents (same task, independent solutions):**

1. **Agent 1 (Claude — coder agent)**: Write code changes focusing on extractor + builder roundtrip fidelity. Emphasize minimal changes to existing code.
2. **Agent 2 (Codex-style — general-purpose agent)**: Write code changes focusing on schema completeness and property coverage. Start from the schema and work outward.
3. **Agent 3 (Gemini-style — reviewer agent)**: Review the current codebase, identify ALL roundtrip fidelity gaps, and propose targeted fixes ranked by impact.

**Cross-review process:**
1. Launch all 3 agents in parallel with identical context (diff categories, file paths, monolithic YAML samples)
2. Compare proposed solutions: overlap = high confidence, unique ideas = evaluate individually
3. Merge best approaches into final implementation
4. Run semantic validation to verify improvement

### Step 4: Integrate semantic validation into benchmark pipeline

Modify `scripts/benchmark_model_library.py`:

1. **Import** `semantic_validate.load_monolithic`, `load_modular`, `validate`
2. **In `run_spec_driven()`**: After `gen.generate(mod_dir)`, before `OrcFxAPI.Model(str(master))`:
   ```python
   mono_yaml = load_monolithic(yml_path)
   mod_yaml = load_modular(mod_dir)
   sem_results = validate(mono_yaml, mod_yaml)
   ```
3. **Add to `ModelBenchmark`**: `semantic_total_sections`, `semantic_sections_with_diffs`, `semantic_significant_count`, `semantic_sections`
4. **Console output**: `Semantic check: N/M sections match (K significant diffs)`
5. **HTML report**: Add "Semantic" column to executive summary + per-model details

### Step 5: Verify — re-run benchmark

```bash
uv run python scripts/benchmark_model_library.py --library-only --three-way --skip-mesh
```

**Target**: All 5 models pass Path B with:
- **Tension**: <1% difference vs monolithic (currently 0.00% for passing models)
- **Bending moment**: <1% difference vs monolithic (mesh-sensitive — coarse mesh may show larger diffs)
- **Semantic equivalence**: 0 significant diffs across all YAML sections

## Files Modified

| File | Change |
|------|--------|
| `scripts/benchmark_model_library.py` | Add semantic validation pre-statics gate, ModelBenchmark fields, HTML report updates |
| `scripts/semantic_validate.py` | Add `summarize()` helper for compact JSON output |
| `src/.../extractor.py` | Fix current profile extraction for depth-varying profiles |
| `src/.../builders/general_builder.py` | Conditional NorthDirection emission, cosmetic props |
| `src/.../builders/generic_builder.py` | Cross-reference validation for line names |
| `src/.../schema/generic.py` | Verify 6DBuoy mass/volume roundtrip |
| `docs/.../tier2_fast/*/modular/` | Regenerated modular files |
| `docs/.../model_library/a02_lazy_s_detailed/modular/` | Regenerated modular files |

## Verification

1. Regenerate all 5 modular directories
2. Semantic validation: 0 significant diffs per model
3. Benchmark: 5/5 Path B converge, 5/5 Path C converge
4. HTML report shows semantic validation column in executive summary
5. JSON output contains `semantic_*` fields
```
## Review Prompt
# Plan Review Prompt

You are reviewing a technical plan/specification for a software engineering project. Evaluate the following aspects:

## Review Criteria

1. **Completeness**: Are all requirements addressed? Are there missing acceptance criteria?
2. **Feasibility**: Is the proposed approach technically sound? Are there hidden complexities?
3. **Dependencies**: Are all dependencies identified? Are there circular or missing dependencies?
4. **Risk**: What are the top 3 risks? Are mitigation strategies adequate?
5. **Scope**: Is the scope well-defined? Is there scope creep risk?
6. **Testing**: Is the test strategy adequate? Are edge cases considered?

## Output Format

Provide your review as:

### Verdict: APPROVE | REQUEST_CHANGES | REJECT

### Summary
[1-3 sentence overall assessment]

### Issues Found
- [P1] Critical: [issue description]
- [P2] Important: [issue description]
- [P3] Minor: [issue description]

### Suggestions
- [suggestion 1]
- [suggestion 2]

### Questions for Author
- [question 1]
- [question 2]
