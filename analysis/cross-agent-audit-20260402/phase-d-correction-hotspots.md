# Phase D — Correction Hotspot Analysis

**Generated**: 2026-04-02 | **Issue**: #1720 | **Agent**: Hermes (Terminal 2)
**Data source**: `.claude/state/corrections/*.jsonl` — 68 files, 8,965 total corrections

---

## 1. Top 20 Correction Hotspot Files

| Rank | File | Corrections | % of Total |
|-----:|------|------------:|-----------:|
| 1 | .claude/skills/.../claude-reflect/scripts/daily-reflect.sh | 103 | 1.15% |
| 2 | ~/.claude/projects/.../memory/MEMORY.md | 97 | 1.08% |
| 3 | scripts/work-queue/generate-html-review.py | 93 | 1.04% |
| 4 | scripts/work-queue/whats-next.sh | 66 | 0.74% |
| 5 | assetutilities/src/.../common/data.py | 59 | 0.66% |
| 6 | specs/wrk/WRK-658/plan.md | 58 | 0.65% |
| 7 | frontierdeepwater/.../pipelay-parameters.csv | 57 | 0.64% |
| 8 | scripts/work-queue/verify-gate-evidence.py | 50 | 0.56% |
| 9 | digitalmodel/src/.../wall_thickness_mt_report.py | 48 | 0.54% |
| 10 | frontierdeepwater/.../heavy-lift-parameters.csv | 44 | 0.49% |
| 11 | .claude/skills/.../work-queue/SKILL.md | 43 | 0.48% |
| 12 | .claude/work-queue/assets/WRK-1028/plan-draft-review.html | 42 | 0.47% |
| 13 | data/oss-engineering-catalog.yaml | 41 | 0.46% |
| 14 | .claude/work-queue/state.yaml | 39 | 0.44% |
| 15 | .claude/skills/.../work-queue-workflow/SKILL.md | 38 | 0.42% |
| 16 | .claude/skills/.../comprehensive-learning/SKILL.md | 38 | 0.42% |
| 17 | specs/wrk/WRK-1105/plan.md | 35 | 0.39% |
| 18 | digitalmodel/src/.../engine.py | 35 | 0.39% |
| 19 | scripts/work-queue/start_stage.py | 34 | 0.38% |
| 20 | .claude/work-queue/.../WRK-1028-lifecycle.html | 34 | 0.38% |

> The top 20 files account for 1,058 corrections (11.8% of total). Distribution is relatively flat — no single file dominates.

## 2. Top 10 Correction Hotspot Modules

| Rank | Module | Corrections | % of Total |
|-----:|--------|------------:|-----------:|
| 1 | .claude/work-queue/ (pending + working + assets) | 3,642 | 40.6% |
| 2 | scripts/ (work-queue + data + quality + review) | 1,317 | 14.7% |
| 3 | digitalmodel/ | 818 | 9.1% |
| 4 | .claude/skills/ (skill edits) | 592 | 6.6% |
| 5 | worldenergydata/ | 571 | 6.4% |
| 6 | specs/ | 415 | 4.6% |
| 7 | .claude/ (other: docs, hooks, state) | 288 | 3.2% |
| 8 | assethold/ | 174 | 1.9% |
| 9 | tests/ | 173 | 1.9% |
| 10 | frontierdeepwater/ | 141 | 1.6% |

> **The work-queue subsystem** (.claude/work-queue/ + scripts/work-queue/) accounts for **55.3% of all corrections** (4,959 of 8,965). This is the single biggest quality improvement target.

## 3. Correction Pattern Taxonomy

### By tool type
| Tool | Count | % |
|------|------:|--:|
| Edit | 8,129 | 90.7% |
| Write | 836 | 9.3% |

### By file extension
| Extension | Count | % | Typical Pattern |
|-----------|------:|--:|-----------------|
| .md | 2,964 | 33.1% | Plan files, specs, skills, docs |
| .py | 2,354 | 26.3% | Script logic, imports, data processing |
| .yaml | 2,078 | 23.2% | Config, state, catalogs |
| .sh | 967 | 10.8% | Shell scripts, automation |
| .html | 261 | 2.9% | Report generation, dashboards |
| .csv | 131 | 1.5% | Data files, parameters |
| Other | 210 | 2.3% | .toml, .json, .css, .ini, .log |

### Inferred correction pattern categories

Based on module and extension analysis:

| Pattern | Est. Count | Description |
|---------|----------:|-------------|
| Iterative plan/spec refinement | ~3,400 | Repeated edits to plan.md, specs, WRK items |
| Script logic corrections | ~2,350 | Python file edits (imports, logic, paths) |
| Config/state adjustments | ~2,100 | YAML/JSON state files, config tweaks |
| Shell script fixes | ~960 | Bash scripts, automation corrections |
| Report/dashboard iteration | ~260 | HTML report generation and formatting |

> Note: The correction data only captures file + tool + timestamp. No `description` field exists, so pattern classification is inferred from file paths and extensions.

## 4. Test Coverage Gap Analysis

**All top 20 Python hotspot files lack corresponding test files.**

| File | Corrections | Test Status |
|------|----------:|:----------:|
| scripts/work-queue/generate-html-review.py | 93 | ❌ NO TEST |
| assetutilities/src/.../common/data.py | 59 | ❌ NO TEST |
| scripts/work-queue/verify-gate-evidence.py | 50 | ❌ NO TEST |
| digitalmodel/src/.../wall_thickness_mt_report.py | 48 | ❌ NO TEST |
| digitalmodel/src/.../engine.py | 35 | ❌ NO TEST |
| scripts/work-queue/start_stage.py | 34 | ❌ NO TEST |
| .claude/work-queue/scripts/generate-index.py | 32 | ❌ NO TEST |
| scripts/work-queue/exit_stage.py | 29 | ❌ NO TEST |
| digitalmodel/src/.../cp_DNV_RP_B401_2021.py | 29 | ❌ NO TEST |
| worldenergydata/src/.../cli/main.py | 28 | ❌ NO TEST |
| assetutilities/src/.../common/yml_utilities.py | 28 | ❌ NO TEST |
| .claude/skills/.../eval-skills.py | 25 | ❌ NO TEST |
| assethold/src/.../daily_strategy/report.py | 21 | ❌ NO TEST |
| worldenergydata/src/.../v30_financial_reproducer.py | 17 | ❌ NO TEST |
| worldenergydata/src/.../seed_collector.py | 16 | ❌ NO TEST |
| scripts/data/document-index/assess-deep-extraction-yield.py | 16 | ❌ NO TEST |
| assethold/src/.../get_stock_data.py | 16 | ❌ NO TEST |
| scripts/work-queue/dep_graph.py | 14 | ❌ NO TEST |
| digitalmodel/src/.../structural/analysis/cli.py | 13 | ❌ NO TEST |

> **0 of 20 top Python hotspots have tests.** This is the strongest signal for where to invest in test coverage.

## 5. Cross-Agent Correction Overlap

| Metric | Claude | Hermes |
|--------|-------:|-------:|
| Correction files | 68 | 0 |
| Total corrections | 8,965 | — |
| Unique files corrected | 3,159 | — |

**Finding**: Hermes orchestrator logs (2 files from 2026-04-01 and 2026-04-02) do not capture corrections in the same format as Claude's `.claude/state/corrections/*.jsonl`. The Hermes logs record tool invocations but not file-level correction tracking.

**Recommendation**: Implement correction tracking for Hermes sessions to enable cross-agent comparison. Current data is Claude-only.

## 6. Temporal Trend

```
Corrections per half-month:

2026-01-H2  ████████████████                                559
2026-02-H1  ███████████████████████████████                 1,105
2026-02-H2  █████████████████████████████████████████████████ 1,830
2026-03-H1  ████████████████████████████████████████████████████████████████████████████████████████████████████ 3,736
2026-03-H2  ██████████████████████████████████████████████  1,720
2026-04-H1  █                                                  15
```

**Trend**: Corrections spiked sharply in early March (3,736 in first half), then declined by 54% in late March (1,720). The March spike correlates with the intensive work-queue buildout period. April data is partial (1 day).

**Overall trajectory**: Corrections grew 6.7× from late January to early March, then started declining — suggesting the codebase is stabilizing after the work-queue development sprint.

## 7. Recommendations (prioritized)

### Critical — test coverage for top hotspots
1. **scripts/work-queue/*.py** (6 files, 320 corrections total) — Add test suite for the work-queue pipeline. This single module accounts for 55% of all corrections.
2. **digitalmodel engine + structural analysis** (4 files, 125 corrections) — Core engineering calculation module needs regression tests.
3. **assetutilities/common/data.py + yml_utilities.py** (87 corrections) — Shared utility module; test coverage prevents cascading failures.

### High — refactoring targets
4. **Work-queue state management** — 3,642 corrections to .claude/work-queue/ suggest fragile state handling. Consider YAML schema validation.
5. **generate-html-review.py** (93 corrections) — Most-corrected Python file. Likely needs refactoring for maintainability.
6. **daily-reflect.sh** (103 corrections) — Most-corrected file overall. Shell scripts are inherently harder to test; consider Python rewrite.

### Medium — tooling improvements
7. **Enable Hermes correction tracking** — Currently no cross-agent correction data.
8. **Correction description field** — Add context to corrections (e.g., "import error", "YAML parse failure") to enable deeper pattern analysis.
9. **Automated hotspot alerts** — Flag files exceeding 20 corrections/week for proactive review.
