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

2. **Harness Saturation Signal** — 2-layer check (Layer 3 deferred to WRK-1020):

   **Layer 1 — Queue balance** (static):
   - Default threshold: 30% (configurable via `HARNESS_THRESHOLD` in skill frontmatter)
   - `HEALTHY` if harness_pct ≤ threshold; `OVER-INVESTED` if exceeded
   - Recommendation: "Run X harness items max before returning to engineering"

   **Layer 2 — Agentic activity by provider** (from `.claude/state/portfolio-signals.yaml`):
   - Per-provider (claude / codex / gemini) breakdown of WRK items closed in **last 30 days**
     by category: harness vs engineering vs other
   - Shows whether a specific provider is drifting toward harness-only work
   - Example output:
     ```
     Provider   | Harness (30d) | Engineering (30d) | Harness%
     claude     | 4             | 3                 | 57% ⚠ OVER
     codex      | 1             | 5                 | 17% ✓
     gemini     | 0             | 2                 | 0%  ✓
     ```
   - Source: `portfolio-signals.yaml` `provider_activity` section (committed to git — auditable)

   **Layer 3 — deferred to WRK-1020**: capability research cron will update
   `portfolio-signals.yaml` with new AI capability signals; skill reads the file
   but Layer 3 display section is omitted until WRK-1020 delivers the cron.

3. **GTM-Ready Technical Capabilities** — rank engineering modules by demo-readiness:
   - Inputs: `brochure_status` field in WRK frontmatter + test coverage proxy (test count in execute.yaml)
   - Rank criteria: brochure_status=ready > brochure_status=draft > brochure_status=n/a
   - Secondary rank: estimated test count (≥10 tests = mature, <5 = immature)
   - Output table: module → domain → brochure_status → maturity_signal → demo_ready?

4. **Next 3 Actions to Fund** — map high-maturity engineering items to GTM opportunities:
   - Domain → Client Persona → Project Type mapping (see Domain Mapping table below)
   - Select top 3 HIGH-priority engineering WRK items ranked by:
     1. `percent_complete` descending (higher = closer to done)
     2. Fallback: `priority` score (high=3, medium=2, low=1) descending
     3. Fallback: WRK ID ascending (lower ID = older, more considered)
   - When `percent_complete` is absent or 0, treat as 0 in ranking
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
| **Portfolio signals** | `.claude/state/portfolio-signals.yaml` | Per-provider agentic activity + capability research |

### Portfolio Signals File (`.claude/state/portfolio-signals.yaml`)

Maintained by daily cron (`scripts/cron/update-portfolio-signals.sh` or as a new
Phase in `comprehensive-learning`). Schema:

```yaml
generated_at: "2026-03-05T06:00:00Z"
lookback_days: 30

# Layer 2: per-provider WRK activity by category
provider_activity:
  claude:
    harness: 4
    engineering: 3
    data: 0
    other: 1
  codex:
    harness: 1
    engineering: 5
    data: 0
    other: 0
  gemini:
    harness: 0
    engineering: 2
    data: 1
    other: 0

# Layer 3: agentic capability research (updated by cron)
capability_signals:
  - date: "2026-03-04"
    provider: claude
    capability: "extended thinking on complex reasoning"
    engineering_domains: ["structural", "pipeline", "reservoir"]
    impact: medium
    source: "https://www.anthropic.com/..."
  - date: "2026-03-03"
    provider: codex
    capability: "o3-mini available in CLI"
    engineering_domains: ["all"]
    impact: high
    source: "https://platform.openai.com/..."
```

**Update mechanism (WRK-1019 scope — Layer 2 only):**
- Provider activity: parsed from closed WRK YAML files archived in last **30 days**
  (reads `category:` and `orchestrator:` fields from archive files)
- Written to `.claude/state/portfolio-signals.yaml` — **committed to git** (auditable history)
- Capability research (Layer 3): deferred to WRK-1020; `capability_signals:` key will be
  added to the schema by WRK-1020 cron work without breaking the existing L1+L2 skill

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
| 7 | Harness saturation signal includes per-provider agentic activity (Layer 2) | `test_provider_activity_parsed` |
| 8 | portfolio-signals.yaml with `capability_signals` key present does not crash skill (L3 compat, WRK-1019 scope only) | `test_capability_signals_compat_no_crash` |
| 9 | Missing portfolio-signals.yaml handled gracefully (no crash) | `test_portfolio_signals_missing_graceful` |
| 10 | Session-start integration point documented | `test_session_start_trigger_documented` |
| 11 | Skill description triggers on correct phrases | `test_description_trigger_phrases` |

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
   - **L1 only**: parses `INDEX.md` `## By Category` section
   - Returns JSON: `{category: count, ...}`, `harness_pct`, `engineering_pct`, `total`
   - Also reads `portfolio-signals.yaml` (L2, pre-computed) and returns `provider_activity` dict
   - Does NOT write or update `portfolio-signals.yaml` — that is WRK-1020 scope
   - Used by the skill at runtime and in tests
4. Write TDD tests `tests/skills/test_repo_portfolio_steering.py`:
   - 11 tests (one per acceptance criterion above)
   - Tests run against real INDEX.md state + fixture SKILL.md + fixture portfolio-signals.yaml
5. Run TDD cycle: red → green → refactor
6. Agent cross-review (Codex + Gemini) on SKILL.md + compute-balance.py
7. Update related skills: session-start `related_skills` + skill-creator `related_skills`
8. Run `verify-gate-evidence.py WRK-1019` — all gates pass
9. Generate final HTML review artifact

## TDD Plan

Tests in `tests/skills/test_repo_portfolio_steering.py`:

```python
# 11 tests targeting acceptance criteria (1:1 with AC table above)
test_skill_file_exists()                        # AC-1: path + name + version in frontmatter
test_balance_snapshot_parses_index()            # AC-2: compute-balance.py L1 against real INDEX.md
test_harness_threshold_default()                # AC-3a: default 30% fires correctly
test_harness_threshold_custom()                 # AC-3b: HARNESS_THRESHOLD override
test_gtm_readiness_ranking()                    # AC-4: brochure_status sort order
test_next3_fund_mapping()                       # AC-5: domain → persona mapping table present
                                                #        ranking: percent_complete desc → priority desc → ID asc
test_harness_budget_formula()                   # AC-6: all 3 spend-rate tiers correct
test_provider_activity_parsed()                 # AC-7: portfolio-signals.yaml provider_activity read
test_capability_signals_compat_no_crash()       # AC-8: capability_signals key present → no crash (L3 compat)
test_portfolio_signals_missing_graceful()       # AC-9: missing yaml → Layer 2 skipped, L1 still works
test_session_start_trigger_documented()         # AC-10: session-start integration point in SKILL.md
test_description_trigger_phrases()              # AC-11: required phrases in description field
```

Scripts under test:
- `scripts/skills/repo-portfolio-steering/compute-balance.py` — L1 INDEX.md parsing + L2 portfolio-signals.yaml read
- `scripts/cron/update-portfolio-signals.sh` — **WRK-1020 scope only**; not tested here

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

dev-primary (plan + execution)
