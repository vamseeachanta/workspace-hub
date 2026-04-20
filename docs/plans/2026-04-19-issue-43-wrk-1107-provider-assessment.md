# Plan for #43: WRK-1107 — unified provider assessment + compliance audit

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-19
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/43
> **Review artifacts:** scripts/review/results/2026-04-19-plan-43-claude.md | ...-codex.md | ...-gemini.md
> **Labels on issue:** `cat:harness`, `domain:session`, `priority:medium`, `agent:codex`

---

## Resource Intelligence Summary

### Existing repo code

- Found: `state/session-signals/` — dated JSONL directory exists (50+ files from 2026-03-10 onward). Current event shapes in use: `stage_exit` (with `wrk`, `stage`, `date`, `timestamp`) and `codex_session` (with `session_id`, `turns`, `source`). This matches the precedent the issue cites from WRK-1102 and proves Output 4 (`gate_compliance_score`, `provider_capability` events) is additive, not pipeline-altering.
- Found: `config/agents/routing-config.yaml` — v2.0.0 smart-router config with tiers (SIMPLE/STANDARD/COMPLEX/REASONING), weighted dimensions, confidence thresholds. **Overlap risk:** issue asks to create `config/agents/routing-rules.yaml` — plan must resolve whether this is a new file, an extension of `routing-config.yaml`, or a rename.
- Found: `config/agents/provider-capabilities.yaml` — v1.1.0, capability profiles for claude/codex/gemini/hermes keyed by strengths, model IDs, context windows. **Overlap risk:** issue asks for a new `provider-assessment.md` covering six dimensions; plan must position new artifact as evaluation snapshot (derived) vs. static profile (source of truth).
- Found: `config/agents/behavior-contract.yaml` — defines artifact path `.claude/work-queue/*/WRK-*.md` but no such files currently exist under `.claude/work-queue/pending|done|assets/`. Confirms WRK-NNNN scheme was intended but is now orphaned in practice.
- Found: `.claude/work-queue/` — contains `INDEX.md`, `pending/`, `done/`, `assets/`, `scripts/generate-index.py`. None of `WRK-1005*`, `WRK-1045*`, `WRK-1107*` artifacts exist in any subdir.
- Found: `tests/session-analysis/test_classify_routing.bats` — the only non-issue-body mention of WRK-1005/1045/1102/1107 anywhere in the repo. Confirms session-analysis.sh is the target integration point but the script itself is not yet located on disk.
- Found: `logs/` — extensive session logs (`claude-*.log` batches from 2026-04-09, `claude-stage2-t*.log`, etc.) but the 2026-03-08→15 window referenced in the issue predates most of the concentrated log output; parseability will need a concrete log-format contract before scoring can run.
- Gap: No `assets/WRK-1107/` or `assets/WRK-1107/provider-assessment.md` or `assets/WRK-1107/session-compliance-audit.md` — issue asks for these to be created.
- Found (late): `scripts/analysis/session-analysis.sh` exists — morning cron, reads from `.claude/state/session-signals/`, writes to `.claude/state/session-analysis/`, `skill-scores.yaml`, candidate/pending-review directories. Also a sibling `scripts/productivity/sections/session-analysis.sh`. Resolves the "missing script" gap but surfaces a path-contract conflict (see next bullet).
- **Path contract conflict:** `session-analysis.sh` reads from `.claude/state/session-signals/` (per-session files like `2026-02-20-091148.jsonl`). The issue body specifies `state/session-signals/YYYY-MM-DD.jsonl` (per-day files). Both stores actually exist on disk with **different filename schemas** (per-session timestamped vs. per-day aggregated). Honoring the issue verbatim writes to a store the reader never sees. See Q7.
- Gap: No `gate_compliance_score` or `provider_capability` event emitters anywhere in the repo today.

### Standards

| Standard | Status | Source |
|---|---|---|
| CONTROL_PLANE_CONTRACT.md v1.0.0 | applies — AGENTS.md is canonical entry point; provider adapters MUST NOT contradict | `docs/standards/CONTROL_PLANE_CONTRACT.md` |
| AI_REVIEW_ROUTING_POLICY.md | referenced by CONTROL_PLANE_CONTRACT; must be consulted before routing-rule changes | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` (implied, not yet read) |
| HARD-STOP-POLICY.md | applies — plan must have `status:plan-approved` before implementation code is written | `docs/standards/HARD-STOP-POLICY.md` |

### LLM Wiki pages consulted

- not applicable — this is a harness/infra issue, not a domain-engineering issue.

### Documents consulted

- `docs/plans/README.md` — reviewed index of 50+ prior plans; no prior WRK-1107 plan exists; prior related plan is #2046 (`planning-compliance-audit`) which is a different-scope compliance audit for the planning-mode rollout, not for provider-gate scoring.
- `gh issue view 798, 826, 871, 950` — WRK-1005 (#798 + duplicate #871) and WRK-1045 (#826 + duplicate #950) were **all CLOSED 2026-03-19 with no closing comment**. No implementation-summary comment, no cross-reference to a landed artifact. This is a governance-drift precedent, not a clean completion to consolidate from.
- `gh issue view 43` (this issue) — full body read. The issue body itself is the primary source for requirements (6 capability dimensions, 3 compliance metrics, 4 named outputs).
- `.claude/memory/` — relevant MEMORY.md entries: `feedback_no_reserved_wrk_ids.md` (GitHub issues only, no WRK IDs), `feedback_queue_git_tracked.md` (verify files in git before queue), `feedback_adversarial_review_stance.md` (review prompts must force defect-hunting).
- Related issue #2332 (OPEN) — `chore(harness): drive provider-audit bare-python3 debt to canonical uv-run runtimes`. Signals an ongoing harness-tooling cleanup; new tooling here should use `uv run` not bare `python3`.
- Related issue #2046 (OPEN) — `Audit compliance of strict issue planning workflow after rollout`. Scope is disjoint (planning-workflow compliance vs. provider-gate compliance) but reuses the word "compliance" — ensure we disambiguate in commit messages and artifact titles to avoid confusion.

### Gaps identified

1. The WRK-1005/1045 predecessor outcomes are undocumented — no closing comment, no done/ artifact. Consolidating on top of opaque predecessors is itself a governance gap this plan must surface rather than paper over.
2. `session-analysis.sh` script is not on disk despite being referenced by a .bats fixture and this issue's output contract. Plan must either (a) locate or reconstruct it, or (b) treat it as part of the deliverable.
3. File overlap decisions (`routing-rules.yaml` vs existing `routing-config.yaml`; `provider-assessment.md` vs existing `provider-capabilities.yaml`) are open questions requiring user disposition before implementation.
4. WRK-NNNN ID scheme contradicts `feedback_no_reserved_wrk_ids` memory rule — needs user disposition on whether to honor the issue-body scheme or convert to GH-issue-only.
5. Log-format contract for parsing `claude-*.log` / `claude-stage2-*.log` files is unspecified — scoring is impossible without one.

<!-- Distinct sources listed: 8 (well above ≥3 minimum). -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-19-issue-43-wrk-1107-provider-assessment.md |
| Tests — parser | tests/session-analysis/test_parse_logs.bats (new) |
| Tests — scoring | tests/session-analysis/test_compliance_score.py (new, uv run) |
| Tests — event emitter | tests/session-analysis/test_emit_signals.py (new, uv run) |
| Implementation — parser | scripts/session-analysis/parse-session-logs.py (new) |
| Implementation — scorer | scripts/session-analysis/score-gate-compliance.py (new) |
| Implementation — emitter | scripts/session-analysis/emit-session-signals.py (new) |
| Output 1 — capability report | `assets/issue-43/provider-assessment.md` (new; remapped from `WRK-1107` per Q1) |
| Output 2 — compliance audit | `assets/issue-43/session-compliance-audit.md` (new; same remap) |
| Output 3 — routing rules | `config/agents/routing-rules.yaml` (new, policy-only; sibling to existing `routing-config.yaml` per Q2) |
| Output 4 — session signals | `.claude/state/session-signals/YYYY-MM-DD-HHMMSS.jsonl` (per-session timestamp; store that `session-analysis.sh` actually reads, per Q7) |
| Log-format contract | `docs/standards/session-log-format-contract.md` (new; prerequisite for parser tests, per Q4) |
| Behavior-contract cleanup | `config/agents/behavior-contract.yaml` (modify — drop orphan `WRK-*.md` artifact reference, per Q1) |
| Predecessor cleanup comments | GitHub comments on #798, #871, #826, #950 (reopen → cross-ref comment → reclose per `feedback_gh_issue_close_silent_comment_drop`, per Q3) |
| Plan review — Claude | scripts/review/results/2026-04-19-plan-43-claude.md |
| Plan review — Codex | scripts/review/results/2026-04-19-plan-43-codex.md |
| Plan review — Gemini | scripts/review/results/2026-04-19-plan-43-gemini.md |
| Index update | docs/plans/README.md (new row for this plan) |

---

## Deliverable

A reproducible session-analysis pipeline that parses 2026-03-08→2026-03-15 provider session logs, scores each provider against 6 capability dimensions and gate-compliance, writes two markdown audit reports to `assets/issue-43/` plus a new declarative `config/agents/routing-rules.yaml`, and emits `gate_compliance_score` + `provider_capability` events into `.claude/state/session-signals/` (the store that `scripts/analysis/session-analysis.sh` actually reads) — consumed automatically by the nightly cron with no pipeline schema change. Execution of this plan is dispatched to Codex via `codex:rescue` per the `agent:codex` label.

---

## Pseudocode

```
function parse_session_logs(start_date, end_date, log_roots):
    sessions = []
    for file in walk(log_roots) where date_in_name ∈ [start_date, end_date]:
        provider = infer_provider(file.name)   # claude/codex/gemini prefix
        events = extract_events(file, contract=LOG_FORMAT_CONTRACT)
        sessions.append(SessionRecord(provider, events, file))
    return sessions
```

```
function score_provider(sessions, provider):
    lifecycle = count(stage_exits covering stages 1..20) / total_expected
    gate_first_pass = count(verify-gate-evidence pass on first try) / total_gates
    tdd_faithfulness = count(test_write_event before impl_write_event) / total_tdd_windows
    user_review_adherence = count(stage 5/7/17 halts) / total_stage_5_7_17_events
    tool_skill_invocation = count(skill_invoke events) / total_tool_opportunities
    log_completeness = count(sessions with all required event types) / total_sessions
    return {lifecycle, gate_first_pass, tdd_faithfulness,
            user_review_adherence, tool_skill_invocation, log_completeness}
```

```
function emit_signals(scores, date, now):
    # per Q7: write to the store session-analysis.sh actually reads
    path = f".claude/state/session-signals/{date}-{now.strftime('%H%M%S')}.jsonl"
    records = []
    for p, s in per_provider_scores(scores):
        records.append({"event":"gate_compliance_score", "provider":p, "score":s, "date":date})
    for p, c in per_provider_lifecycle(scores):
        records.append({"event":"provider_capability", "provider":p, "lifecycle_complete":c, "date":date})
    # idempotency: skip records whose (event, provider, date) tuple already appears
    # in any file under .claude/state/session-signals/ for the same date
    write_jsonl(path, dedupe(records, against=scan_existing_signals(date)))
```

```
function write_reports(scores, out_dir="assets/issue-43/"):
    render provider-assessment.md       from capability_scores template
    render session-compliance-audit.md  from gate_scores + baseline_recomputed_inline template
    # baseline recomputed inline from the same cohort per "consolidation without predecessor artifacts" risk
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/standards/session-log-format-contract.md` | Q4 — first-class log-format contract; parser tests reference it |
| Create | `scripts/session-analysis/parse-session-logs.py` | Log-format parser (uv-run shebang, not bare python3 per #2332) |
| Create | `scripts/session-analysis/score-gate-compliance.py` | 6-dimension scorer with inline baseline recomputation |
| Create | `scripts/session-analysis/emit-session-signals.py` | JSONL event emitter with cross-file dedupe scan |
| Create | `tests/session-analysis/test_parse_logs.bats` | Parser contract tests |
| Create | `tests/session-analysis/test_compliance_score.py` | Scorer unit tests |
| Create | `tests/session-analysis/test_emit_signals.py` | Emitter idempotency tests |
| Create | `assets/issue-43/provider-assessment.md` | Output 1 (path resolved per Q1: `issue-43/`, not `WRK-1107/`) |
| Create | `assets/issue-43/session-compliance-audit.md` | Output 2 (same) |
| Create | `config/agents/routing-rules.yaml` | Output 3 — new declarative policy file, sibling to `routing-config.yaml` (Q2) |
| Create | `.claude/state/session-signals/YYYY-MM-DD-HHMMSS.jsonl` | Output 4 — per-session timestamped JSONL (Q7) |
| Modify | `config/agents/behavior-contract.yaml` | Drop orphan `.claude/work-queue/*/WRK-*.md` artifact reference (Q1) |
| Modify | `docs/plans/README.md` | Add index row (done in this commit) |
| Cross-ref | GitHub #798, #871, #826, #950 | Reopen → comment linking this plan → reclose (Q3) |
| Dispatch | `codex:rescue` invocation | Q6 — implementation is executed by Codex, not Claude |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_parse_logs_claude_nominal | parses a canonical claude log into ordered events | `logs/claude-stage2-t1.log` | N stage_exit events in chronological order |
| test_parse_logs_missing_provider_prefix | raises ValueError on file without provider prefix | `logs/orphan.log` | ValueError("unknown provider") |
| test_parse_logs_date_window | filters by [start,end] date range | 2026-03-08 .. 2026-03-15 | only in-window records |
| test_score_lifecycle_complete | lifecycle=1.0 when all 20 stages present | stages {1..20} | 1.0 |
| test_score_lifecycle_partial | lifecycle=0.5 when half the stages present | stages {1..10} | 0.5 |
| test_score_gate_first_pass_baseline | matches simulation baseline (claude=1.0, codex=1.0, gemini=0.95) | sample log cohort | per-provider scores ±0.02 |
| test_score_tdd_faithfulness_test_before_impl | counts test-then-impl ordering | paired write events | ratio in [0,1] |
| test_score_zero_sessions | returns explicit "insufficient data" sentinel | empty input | `{status: "insufficient_data"}` |
| test_emit_signals_shape | JSONL lines match the exact issue-specified shape | scores dict | three lines identical to issue example |
| test_emit_signals_idempotent | second run with same (event,provider,date) writes nothing | re-run | file size unchanged |
| test_emit_signals_pipeline_compat | `session-analysis.sh`-style reader can ingest new events alongside existing `stage_exit`/`codex_session` | mixed JSONL | all events parseable |

---

## Acceptance Criteria

- [ ] All new tests pass: `uv run pytest tests/session-analysis/ -v` and `bats tests/session-analysis/*.bats`
- [ ] No regression: full test suite passes as configured in CI
- [ ] `docs/standards/session-log-format-contract.md` exists and parser tests reference it
- [ ] `assets/issue-43/provider-assessment.md` exists with 6-dimension scores for claude/codex/gemini
- [ ] `assets/issue-43/session-compliance-audit.md` exists with per-provider gate-compliance scores ≥0.90 OR documented explanation of why the ≥0.90 target was not met
- [ ] Zero stage 5/7/17 hard-gate violations reported in the audit window, OR each violation is listed with evidence
- [ ] `.claude/state/session-signals/YYYY-MM-DD-HHMMSS.jsonl` contains at least one `gate_compliance_score` and one `provider_capability` event for each of claude/codex/gemini
- [ ] `scripts/analysis/session-analysis.sh` ingests the new events in a dry-run against the emitted file without schema-change errors
- [ ] `config/agents/routing-rules.yaml` exists as declarative policy, with a header comment pointing to `routing-config.yaml` as the dynamic runtime config
- [ ] `config/agents/behavior-contract.yaml` no longer references the orphan `.claude/work-queue/*/WRK-*.md` artifact path (or the reference is replaced with `issue-NNN` path convention)
- [ ] WRK-1005 (#798, #871) and WRK-1045 (#826, #950) each carry a GitHub comment cross-referencing #43 and this plan — applied via reopen→comment→reclose to defeat the silent-drop bug
- [ ] Plan review artifacts exist for Claude, Codex, Gemini under `scripts/review/results/2026-04-19-plan-43-<provider>.md`
- [ ] Implementation commit authored by Codex (via `codex:rescue`), not Claude, per `agent:codex` label

---

## Adversarial Review Summary

<!-- Filled after Step 4 completes. Do NOT post to GitHub until this section has real verdicts. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | — |
| Codex | PENDING | — |
| Gemini | PENDING | — |

**Overall result:** PENDING (cannot surface for user approval until adversarial review completes and this section is populated)

Revisions made based on review:
- (none yet)

---

## Design Decisions (all 7 open questions resolved by user 2026-04-19)

| # | Question | Decision |
|---|---|---|
| Q1 | WRK-NNNN work-ID scheme vs `feedback_no_reserved_wrk_ids` | **Remap to `assets/issue-43/`** AND clean up `config/agents/behavior-contract.yaml` to drop the orphan `.claude/work-queue/*/WRK-*.md` artifact reference. One-time resolution of the contradiction. |
| Q2 | `routing-rules.yaml` vs existing `routing-config.yaml` | **New file, policy-layer only.** `routing-rules.yaml` = declarative static policy; `routing-config.yaml` continues as the dynamic smart-router runtime config. Header comment in each points to the other. |
| Q3 | Closed predecessors #798/#871/#826/#950 (no closing comment) | **Reopen → comment linking #43 + this plan → reclose**, per `feedback_gh_issue_close_silent_comment_drop`. Four issues, four cycles. |
| Q4 | Log-format contract | **New first-class deliverable:** `docs/standards/session-log-format-contract.md`. Parser tests reference it; not a hidden assumption. |
| Q5 | `session-analysis.sh` location | **Resolved** — `scripts/analysis/session-analysis.sh` (sibling `scripts/productivity/sections/session-analysis.sh` noted but out of scope). |
| Q6 | `agent:codex` execution | **Plan authored by Claude; implementation dispatched to Codex via `codex:rescue`.** Codex writes the code; Claude only orchestrates and verifies the plan landed. |
| Q7 | session-signals path divergence | **Emit to `.claude/state/session-signals/` per-session timestamped schema** — the store `session-analysis.sh` actually reads. Deviates from literal path string in issue body but honors its stated intent ("pipeline consumes signals automatically — no pipeline changes needed"). Flag this deviation in the GitHub comment when posting the plan. |

### Risks

- **Risk — log volume / log-format drift:** the 2026-03-08→15 window spans hundreds of log files with inconsistent formats; a brittle parser will score noise as non-compliance. Mitigation: treat log-format contract as a first-class output with its own tests.
- **Risk — consolidation without predecessor artifacts:** scoring against baselines "claude=100, codex=100, gemini=95" lifted from the closed predecessors, when those predecessors left no artifact, makes the baseline unverifiable. Mitigation: recompute baselines inline from the same input cohort and document the computation.
- **Risk — routing-rule change lands broader than intended:** routing changes cascade across all provider-selection code paths. Mitigation: keep Output 3 data-only in this plan; defer behavioral routing changes to a follow-up issue.
- **Risk — self-approval / status gate:** Claude cannot self-approve this plan. Plan must halt at `status:plan-review` for user approval.

---

## Complexity: T2

Multiple new files across `scripts/`, `tests/`, `assets/`, `config/agents/`, `docs/standards/`, and `.claude/state/`; requires TDD for three modules; touches governance (closed predecessor issues, behavior-contract cleanup). All 7 open questions resolved upstream of review. Not T3 because it does not cross architectural boundaries or re-define control-plane contracts — it composes within the existing `session-signals` + `routing-config` + `work-queue` primitives.
