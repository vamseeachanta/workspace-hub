# Phase 1 Audit Results + Adversarial Review

## Consolidated Audit Findings

### Repo-by-Repo Summary

| Metric | digitalmodel | assetutilities | worldenergydata |
|--------|-------------|----------------|-----------------|
| Lines of code | 434,391 | 39,209 | 265,359 |
| Contract compliance | PASS | PASS | PASS |
| Tests collected | TIMEOUT (>30s) | 1,166 (2 errs, 4 skip) | 431 (5 errs) |
| Files >400 lines | 17+ | 20 | 20 |
| Largest file | curves.py: 29,666 | data.py: 1,217 | economic_template.py: 2,425 |
| Orphan modules | 2 | 7 | 10 |
| Active skills | 22 | 3 | 21 |
| Open issues | 30+ | 19 | 12+ |
| Status | Beta (largest) | Stable (foundation) | Beta (data-heavy) |

### Top 10 Refactoring Priorities (Ranked)

1. **digitalmodel/curves.py (29,666 lines)** — This is a single-file monolith. Must be decomposed into logical modules (hull geometry, hydrostatics, stability, weight estimation, etc.). Highest technical debt in the entire ecosystem.

2. **assetutilities test errors (2 failures)** — As the foundational dependency, assetutilities must have clean tests. Fix before any consumer refactoring.

3. **worldenergydata test errors (5 failures)** — Similar priority to assetutilities. Cannot trust data pipeline changes with broken tests.

4. **digitalmodel test collection timeout** — The test suite is so large/slow it cannot even collect within 30 seconds. Needs investigation — likely heavy imports or fixture overhead.

5. **assetutilities: 5 orphan CLI scripts** — `create-module-agent.py`, `create-spec-enhanced.py`, `create-spec.py`, `propagate_to_all.py`, `run_slash_command.py` — these are entry points that nothing imports, which is expected for CLI scripts. BUT: `database.py` (1,150 lines) being orphaned is concerning. Should investigate if it's truly unused or just dynamically loaded.

6. **worldenergydata: 14,145 bytecode files** — This indicates an extremely deep dependency tree. The 11.71s compile time is a code smell. Need to audit `pyproject.toml` for unnecessary dependencies and consider lazy imports.

7. **digitalmodel: 10+ files >1,000 lines** — Beyond curves.py, there are wellpath3D.py (1,985), orcaflex_model_components.py (1,899), cathodic_protection.py (1,853), pipeline_schematic.py (1,660), etc. All candidates for decomposition.

8. **Skill distribution imbalance** — digitalmodel: 22 skills, worldenergydata: 21, assetutilities: 3. The foundational library has the fewest skills, while consumer repos have the most. Suggests cross-repo skill duplication and unclear ownership boundaries.

9. **Cross-repo import coupling** — At least 32 files in digitalmodel import from assetutilities. Any changes to assetutilities APIs will ripple to all consumers. This is why assetutilities must be refactored first and with extreme care.

10. **Old assetutilities issues** — 19 open issues, many dating to 2024-2025, suggest accumulated tech debt that hasn't been tracked properly. Need to triage and close stale items.

### Adversarial Review Findings

**Codex Review: MINOR changes needed**
- The grep-based orphan detection is a weak heuristic — doesn't catch dynamic imports, __import__(), or importlib usage. A proper AST-based analysis would be more accurate.
- The 29,666-line curves.py is the single most critical finding and should be broken out into its own sub-issue with a dedicated refactoring plan.
- Assetutilities being refactored first IS the correct order, but the risk is underestimated — any API change breaks 32+ import sites in digitalmodel alone.
- Test infrastructure red flag: 1,166 tests collected but only 116 active skills suggests test-to-production ratio may be off.

**Gemini Review: MINOR changes needed**
- Contract compliance check (AGENTS.md + CLAUDE.md + .claude/) is necessary but NOT sufficient. Should also check .codex/ and .gemini/ adapters per the Control-Plane Contract.
- The 5 CLI "orphan" scripts in assetutilities are probably NOT orphans — they're entry points designed to be called from command line, not imported. The heuristic incorrectly flags them.
- 14,145 bytecode files in worldenergydata suggests either: excessive dependencies, or the project is pulling in too many development packages in its pyproject.toml.
- Dependency ordering is correct conceptually but incomplete — should add assethold (also depends on assetutilities) as #4 in the refactor sequence.

### Phase 2 Plan: What Needs to Happen

1. **Create sub-issues** for each major refactoring target:
   - Sub-issue for curves.py decomposition (digitalmodel #?)
   - Sub-issue for assetutilities CLI/orphan cleanup (#?)
   - Sub-issue for worldenergydata dependency audit (#?)
   - Sub-issue for cross-repo skill consolidation (#?)

2. **Assetutilities first** (foundational dependency):
   - Fix 2 failing tests
   - Audit database.py — is it truly orphaned or just dynamically loaded?
   - Clean up CLI scripts — confirm they're entry points or mark obsolete
   - Verify contract compliance across .codex/ and .gemini/ adapters

3. **Digitalmodel second** (largest consumer):
   - Create detailed decomposition plan for curves.py
   - Address 10+ other oversized files
   - Investigate test collection timeout
   - Cross-reference 2 orphan files with actual usage patterns

4. **Worldenergydata third** (data pipeline):
   - Audit pyproject.toml for unnecessary dependencies
   - Fix 5 failing tests
   - Investigate 14,145 bytecode compilation — identify root cause
   - Assess 10 orphan modules for archival vs. active use

5. **Cross-cutting**:
   - Skill consolidation across 3 repos (22 + 3 + 21 = 46 skills, many duplicated)
   - Standardize contract compliance (add .codex/ and .gemini/ checks)
   - Create unified test coverage dashboard

### Claude Code Ultraplan Mode Feasibility

Phase 1 (completed): Ran as a Python script, not Claude Code plan mode. The script completed in 148 seconds and produced structured results. This was more efficient than trying to run Claude Code plan mode for each repo.

For Phase 2, Claude Code `--permission-mode plan` would be effective for generating detailed refactoring plans per repo, but the initial audit was more efficiently done via direct code analysis. The plan mode is better suited for analysis of complex inter-file relationships and dependency graphs than for raw metrics gathering.

Estimated Phase 2 resource requirements:
- 3 repos x Claude Code plan runs x ~$2-5 each = ~$15-30 total
- Each plan run should produce: detailed module decomposition, import graph, test strategy, migration steps
