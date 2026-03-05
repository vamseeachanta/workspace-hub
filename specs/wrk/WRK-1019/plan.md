# WRK-1019 Plan: repo-portfolio-steering Skill
date: 2026-03-05
wrk_id: WRK-1019
route: C
complexity: complex
orchestrator: claude

## Objective

Create `.claude/skills/workspace-hub/repo-portfolio-steering/SKILL.md` — a thin
workspace-specific orchestration skill that reads the current work queue state and
produces a one-page actionable steering report. The report answers: *"Am I investing
the right proportion of effort on harness vs engineering work, and what are the next
highest-leverage actions to fund the repos?"*

The skill is a custom composition layer. It references official plugins for structural
mechanics (do NOT copy their logic). It reads workspace-native inputs (INDEX.md,
brochure_status fields, specs/data-sources/, WRK category fields).

## Resource Intelligence Summary

Queue state confirmed (2026-03-05):
- Total active items: ~215
- harness: 40 items (18.5%) — **below 30% threshold — healthy**
- engineering: 117 items (54%)
- data: 26, platform: 12, business: 7, maintenance: ~10, personal: ~3

Top HIGH-priority engineering items (GTM candidates):
- Pipeline/subsea (DNV RP F105, API 1111, pipeline integrity)
- Cathodic protection (API 1632, ISO 15589-2)
- Marine/offshore (planing hull dynamics, structural)
- Drilling (BourgoineYoung ROP, dysfunction detector)
- Production forecasting (Arps decline curve — worldenergydata)

Brochure-ready engineering repos:
- `digitalmodel`: 3+ implemented domains with tests (subsea pipeline, CP, ansys, drilling)
- `worldenergydata`: production forecasting, EIA analytics
- `assethold`: net_lease CRE model, stocks portfolio

## Skill Design

### Official Plugin References (composition pattern — do NOT copy logic)

| Official Plugin | Role in This Skill |
|---|---|
| `feature-dev@claude-plugin-directory` | 7-phase workflow structure (discover→explore→design→implement→review→summarise) |
| `skill-creator@claude-plugin-directory` | If steering report recommends creating a new skill, delegate to this plugin |

### 5 Output Sections

1. **Balance Snapshot** — reads INDEX.md Category View, computes:
   - `harness_pct = harness_count / total_active * 100`
   - `engineering_pct = engineering_count / total_active * 100`
   - Table: category → count → % → trend indicator

2. **Harness Saturation Signal** — threshold check:
   - Default threshold: 30% (configurable via `HARNESS_THRESHOLD` in skill frontmatter)
   - `HEALTHY` if harness_pct ≤ threshold; `OVER-INVESTED` if exceeded
   - Recommendation: "Run X harness items max before returning to engineering"

3. **GTM-Ready Technical Capabilities** — rank engineering modules by demo-readiness:
   - Inputs: `brochure_status` field in WRK frontmatter + test coverage proxy (test count in execute.yaml)
   - Rank criteria: brochure_status=ready > brochure_status=draft > brochure_status=n/a
   - Secondary rank: estimated test count (≥10 tests = mature, <5 = immature)
   - Output table: module → domain → brochure_status → maturity_signal → demo_ready?

4. **Next 3 Actions to Fund** — map high-maturity engineering items to GTM opportunities:
   - Domain → Client Persona → Project Type mapping (see Domain Mapping table below)
   - Select top 3 HIGH-priority engineering WRK items closest to completion
   - Output: WRK-NNN | domain | client_persona | project_type | recommended_action

5. **Recommended Harness Budget** — spend-rate formula:
   - If harness_pct ≤ 15%: "1 harness per 3 engineering (ramp up harness)"
   - If 15% < harness_pct ≤ 30%: "1 harness per 5 engineering (maintain)"
   - If harness_pct > 30%: "0 harness — pure engineering until below threshold"

### Domain → Client Persona → Project Type Mapping

| Engineering Domain | Client Persona | Project Type |
|---|---|---|
| subsea pipeline / DNV RP F105 | Offshore operator / pipeline integrity engineer | VIV/freespam assessment |
| cathodic protection | Corrosion engineer / asset manager | CP system design report |
| marine / hydrodynamics | Naval architect / offshore designer | Motions & loads study |
| drilling / ROP models | Drilling engineer / well planner | Drilling performance analysis |
| production forecasting / Arps | Reservoir engineer / E&P consultant | Decline curve + reserves |
| net lease / CRE | Real estate investor / asset manager | NNN lease underwriting |
| structural / FEA | Structural engineer / EPC contractor | Plate/beam design check |

### Inputs Read at Runtime

| Input | Path | Purpose |
|---|---|---|
| Category View | INDEX.md `## By Category` section | Balance snapshot raw data |
| WRK frontmatter | `.claude/work-queue/pending/*.md` + `working/*.md` | brochure_status, category, priority |
| Data-source specs | `specs/data-sources/*.yaml` | Module maturity proxies |
| Engineering module index | `specs/modules/` (per repo) | Module-level completeness |

### Session-Start Integration

The skill registers an optional **weekly steering mode** for `/session-start`:
- Trigger: user invokes `/repo-portfolio-steering` OR session_start detects `--mode weekly`
- Output replaces the "top items per category" summary with the full steering report
- No changes to session-start SKILL.md body — steering is invoked as a delegate, not embedded

## Acceptance Criteria (from WRK-1019.md — map to tests)

| # | Criterion | Test Approach |
|---|---|---|
| 1 | Skill file at correct path | `test_skill_file_exists` — path check |
| 2 | Balance snapshot reads INDEX.md By Category | `test_balance_snapshot_parses_index` |
| 3 | Harness saturation threshold default 30% + configurable | `test_harness_threshold_default`, `test_harness_threshold_custom` |
| 4 | GTM-readiness scan ranks modules by brochure_status + test proxy | `test_gtm_readiness_ranking` |
| 5 | Next 3 to fund section maps domains to personas | `test_next3_fund_mapping` |
| 6 | Recommended harness budget outputs spend-rate | `test_harness_budget_formula` |
| 7 | Session-start integration point documented | `test_session_start_trigger_documented` |
| 8 | Skill description triggers on correct phrases | `test_description_trigger_phrases` |

## Execution Steps

1. Create skill directory `mkdir -p .claude/skills/workspace-hub/repo-portfolio-steering/`
2. Write `SKILL.md` with:
   - Frontmatter (name, description with trigger phrases, version, category, official_plugin refs)
   - Overview + Quick Start
   - Official Plugin Reference section (composition pattern)
   - 5 output sections with instructions and example output format
   - Domain mapping table
   - Runtime inputs table
   - Session-start integration section
   - Acceptance criteria checklist
3. Write `scripts/skills/repo-portfolio-steering/compute-balance.py`:
   - Parses `INDEX.md` `## By Category` section
   - Returns JSON: `{category: count, ...}`, `harness_pct`, `engineering_pct`
   - Used by the skill at runtime and in tests
4. Write TDD tests `tests/skills/test_repo_portfolio_steering.py`:
   - 8 tests (one per acceptance criterion above)
   - Tests run against real INDEX.md state + fixture SKILL.md
5. Run TDD cycle: red → green → refactor
6. Agent cross-review (Codex + Gemini) on SKILL.md + compute-balance.py
7. Update related skills: session-start `related_skills` + skill-creator `related_skills`
8. Run `verify-gate-evidence.py WRK-1019` — all gates pass
9. Generate final HTML review artifact

## TDD Plan

Tests in `tests/skills/test_repo_portfolio_steering.py`:

```python
# 8 tests targeting acceptance criteria
test_skill_file_exists()                    # path + name + version in frontmatter
test_balance_snapshot_parses_index()        # compute-balance.py against real INDEX.md
test_harness_threshold_default()            # default 30% fires correctly
test_harness_threshold_custom()             # HARNESS_THRESHOLD override
test_gtm_readiness_ranking()               # brochure_status sort order
test_next3_fund_mapping()                  # domain → persona mapping table present
test_harness_budget_formula()              # all 3 spend-rate tiers correct
test_description_trigger_phrases()         # required phrases in description field
```

Script under test: `scripts/skills/repo-portfolio-steering/compute-balance.py`
(pure Python, no external deps beyond stdlib + yaml)

## Output Files

All evidence paths under `.claude/work-queue/assets/WRK-1019/`.

| File | Purpose |
|---|---|
| `evidence/stage-evidence.yaml` | 20-stage lifecycle evidence |
| `evidence/resource-intelligence.yaml` | Queue balance + GTM analysis |
| `evidence/resource-intelligence-update.yaml` | Post-work additions |
| `evidence/claim.yaml` | Claim gate + claim_expires_at |
| `evidence/activation.yaml` | Activation record |
| `evidence/execute.yaml` | 3-5 integrated tests with artifact_ref |
| `evidence/future-work.yaml` | Follow-up ideas (disposition: spun-off-new|existing-updated) |
| `evidence/user-review-browser-open.yaml` | Browser open records (plan_draft/plan_final/close_review) |
| `evidence/user-review-close.yaml` | Close decision |
| `evidence/gate-evidence-summary.json` | Auto-generated by verify-gate-evidence.py |
| `evidence/gate-evidence-summary.md` | Human-readable gate summary |
| `test-results.md` | TDD evidence (8 tests pass) |
| `legal-scan.md` | Legal scan result: pass |
| `review.md` | Codex + Gemini cross-review verdicts |
| `plan-draft.md` | This file (plan draft) |
| `plan-html-review-final.md` | User plan approval record |
| `workflow-final-review.html` | Final HTML review artifact |

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| INDEX.md format may drift | compute-balance.py uses regex not positional parsing |
| brochure_status rarely set | Fallback: count tests in execute.yaml as maturity proxy |
| Official plugins may not exist yet | Skill references them by name only — no runtime dependency |
| compute-balance.py out of scope for Route C | Keep it simple: ~50 lines, single function, stdlib only |

## Workstation

ace-linux-1 (plan + execution)
