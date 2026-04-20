# Plan for #43: WRK-1107 — unified provider assessment + compliance audit

> **Status:** draft (v2 — absorbs Claude MINOR review 2026-04-19)
> **Complexity:** T2
> **Date:** 2026-04-19
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/43
> **Review artifacts:** scripts/review/results/2026-04-19-plan-43-claude.md (MINOR, 10 findings absorbed) | ...-codex.md (pending) | ...-gemini.md (pending)
> **Labels on issue:** `cat:harness`, `domain:session`, `priority:medium`, `agent:codex`
>
> **v2 revision notes:** Rewrote emitter to deterministic per-day filename with `--dry-run` default (Findings 1+5); added `find_hard_gate_violations` step (Finding 2); corrected false "only reference" intel claim and added WRK-1005 6.1M-tool-call runaway context (Finding 3); added issue-body amendment step (Finding 4); added `routing-rules.yaml` schema block (Finding 6); hedged Q6 for Codex sandbox write-block (Finding 7); added pipeline-consumability integration test (Finding 8); moved scripts from `scripts/analysis/compliance/` to `scripts/analysis/compliance/` (Finding 9); scoped Q1 WRK-remap to new artifacts only — plan filename and issue title retain historical marker (Finding 10).

---

## Resource Intelligence Summary

### Existing repo code

- Found: `state/session-signals/` — dated JSONL directory exists (50+ files from 2026-03-10 onward). Current event shapes in use: `stage_exit` (with `wrk`, `stage`, `date`, `timestamp`) and `codex_session` (with `session_id`, `turns`, `source`). This matches the precedent the issue cites from WRK-1102 and proves Output 4 (`gate_compliance_score`, `provider_capability` events) is additive, not pipeline-altering.
- Found: `config/agents/routing-config.yaml` — v2.0.0 smart-router config with tiers (SIMPLE/STANDARD/COMPLEX/REASONING), weighted dimensions, confidence thresholds. **Overlap risk:** issue asks to create `config/agents/routing-rules.yaml` — plan must resolve whether this is a new file, an extension of `routing-config.yaml`, or a rename.
- Found: `config/agents/provider-capabilities.yaml` — v1.1.0, capability profiles for claude/codex/gemini/hermes keyed by strengths, model IDs, context windows. **Overlap risk:** issue asks for a new `provider-assessment.md` covering six dimensions; plan must position new artifact as evaluation snapshot (derived) vs. static profile (source of truth).
- Found: `config/agents/behavior-contract.yaml` — defines artifact path `.claude/work-queue/*/WRK-*.md` but no such files currently exist under `.claude/work-queue/pending|done|assets/`. Confirms WRK-NNNN scheme was intended but is now orphaned in practice.
- Found: `.claude/work-queue/` — contains `INDEX.md`, `pending/`, `done/`, `assets/`, `scripts/generate-index.py`. None of `WRK-1005*`, `WRK-1045*`, `WRK-1107*` artifacts exist in any subdir.
- Found: `tests/session-analysis/test_classify_routing.bats` — primary test-level reference to the WRK-1005/1045/1102/1107 IDs. (Correction from v1: this is NOT the only reference. `rg` finds 11 files total; notably `docs/standards/engineering-issue-workflow-skill.md:250` documents a **6.1M-tool-call runaway incident on WRK-1005** with "no exit conditions, no completion gates," and multiple `.claude/state/session-signals/*.jsonl` files still emit stage_exit events carrying WRK IDs. The scheme is partially live on the signal side, not fully retired.)
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
2. **WRK-1005 runaway incident (added v2):** `docs/standards/engineering-issue-workflow-skill.md:250` records that "three WRK items (WRK-1022, WRK-1012, WRK-1005) consumed 6.1M tool calls across runaway sessions with no exit conditions, no completion gates." Any consolidation of WRK-1005 must treat this as the primary failure-mode baseline to score against — not an afterthought.
3. File overlap decisions (`routing-rules.yaml` vs existing `routing-config.yaml`; `provider-assessment.md` vs existing `provider-capabilities.yaml`) were open questions now resolved (see Design Decisions Q2, Q1).
4. WRK-NNNN ID scheme contradicts `feedback_no_reserved_wrk_ids` memory rule — resolved (Q1 v2) by scoping remap to new artifacts and leaving historical markers (this filename, issue title, live signal events) in place.
5. Log-format contract for parsing `claude-*.log` / `claude-stage2-*.log` files is unspecified — now an explicit first-class deliverable (Q4).
6. **Pipeline-semantic compatibility unverified (v2):** `scripts/analysis/session-analysis.sh:101` filters on `.event == "session_end"`; new event types (`gate_compliance_score`, `provider_capability`) may silently drop unless the script's downstream jq handlers are extended. Implementation must either add a handler or document the drop as intentional. See Acceptance Criteria #8 and TDD `test_pipeline_consumes_new_events`.

<!-- Distinct sources listed: 9 (well above ≥3 minimum). -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-19-issue-43-wrk-1107-provider-assessment.md |
| Tests — parser | tests/session-analysis/test_parse_logs.bats (new) |
| Tests — scoring | tests/session-analysis/test_compliance_score.py (new, uv run) |
| Tests — event emitter | tests/session-analysis/test_emit_signals.py (new, uv run) |
| Implementation — parser | scripts/analysis/compliance/parse-session-logs.py (new) |
| Implementation — scorer | scripts/analysis/compliance/score-gate-compliance.py (new) |
| Implementation — emitter | scripts/analysis/compliance/emit-session-signals.py (new) |
| Output 1 — capability report | `assets/issue-43/provider-assessment.md` (new; remapped from `WRK-1107` per Q1) |
| Output 2 — compliance audit | `assets/issue-43/session-compliance-audit.md` (new; same remap) |
| Output 3 — routing rules | `config/agents/routing-rules.yaml` (new, policy-only; sibling to existing `routing-config.yaml` per Q2) |
| Output 4 — session signals | `.claude/state/session-signals/43-compliance-YYYY-MM-DD.jsonl` (per-day, prefix `43-compliance-` so rollback is `rm 43-compliance-*.jsonl`; dedupe-append in place per Finding 1+5) |
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
function find_hard_gate_violations(sessions) -> list[Violation]:
    # Finding 2: acceptance criterion "Zero stage 5/7/17 violations" needs a list, not a ratio.
    # Violation shape is defined in docs/standards/session-log-format-contract.md.
    violations = []
    for session in sessions:
        for evt in session.events:
            if evt.stage in {5, 7, 17} and evt.type == "gate_bypass":
                violations.append(Violation(
                    session_id=session.id, stage=evt.stage,
                    evidence_path=session.log_path, timestamp=evt.ts,
                    provider=session.provider, excerpt=evt.raw_line))
    return violations
```

```
function emit_signals(scores, date, dry_run=True):
    # v2 (Findings 1+5): deterministic per-day filename + issue-prefixed for one-glob rollback
    path = f".claude/state/session-signals/43-compliance-{date}.jsonl"
    records = []
    for p, s in per_provider_scores(scores):
        records.append({"event":"gate_compliance_score", "provider":p, "score":s, "date":date})
    for p, c in per_provider_lifecycle(scores):
        records.append({"event":"provider_capability", "provider":p, "lifecycle_complete":c, "date":date})
    # idempotency: read existing file, keep records with new (event, provider, date) tuples
    existing = read_jsonl_if_exists(path)
    seen = {(r["event"], r["provider"], r["date"]) for r in existing}
    new_records = [r for r in records if (r["event"], r["provider"], r["date"]) not in seen]
    if not new_records:
        return {"status": "noop", "path": path}           # no empty-file creation on rerun
    if dry_run:
        return {"status": "dry_run", "would_append": len(new_records), "path": path}
    append_jsonl(path, new_records)                         # real append, not overwrite
    return {"status": "appended", "n": len(new_records), "path": path}
```

```
function write_reports(scores, violations, out_dir="assets/issue-43/"):
    render provider-assessment.md       from capability_scores template
    render session-compliance-audit.md  from gate_scores
                                           + violations_list (Finding 2)
                                           + baseline_recomputed_inline (predecessor-artifact-absence risk)
                                           + wrk_1005_runaway_context (Gap #2)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/standards/session-log-format-contract.md` | Q4 — first-class log-format contract; parser tests reference it |
| Create | `scripts/analysis/compliance/parse-session-logs.py` | Log-format parser (uv-run shebang, not bare python3 per #2332) |
| Create | `scripts/analysis/compliance/score-gate-compliance.py` | 6-dimension scorer with inline baseline recomputation |
| Create | `scripts/analysis/compliance/emit-session-signals.py` | JSONL event emitter with cross-file dedupe scan |
| Create | `tests/session-analysis/test_parse_logs.bats` | Parser contract tests |
| Create | `tests/session-analysis/test_compliance_score.py` | Scorer unit tests |
| Create | `tests/session-analysis/test_emit_signals.py` | Emitter idempotency tests |
| Create | `assets/issue-43/provider-assessment.md` | Output 1 (path resolved per Q1: `issue-43/`, not `WRK-1107/`) |
| Create | `assets/issue-43/session-compliance-audit.md` | Output 2 (same) |
| Create | `config/agents/routing-rules.yaml` | Output 3 — new declarative policy file, sibling to `routing-config.yaml` (Q2) |
| Create/Append | `.claude/state/session-signals/43-compliance-YYYY-MM-DD.jsonl` | Output 4 — deterministic per-day, prefixed for rollback (Findings 1+5) |
| Modify | `config/agents/behavior-contract.yaml` | Drop orphan `.claude/work-queue/*/WRK-*.md` artifact reference (Q1) |
| Amend | Issue #43 body (via amendment comment cross-linked from description) | Reconcile Output 4 spec with plan's actual emit path, per Finding 4 |
| Create | `scripts/analysis/compliance/schemas/routing-rules.schema.json` | JSON Schema for `routing-rules.yaml` (Finding 6); used by `test_routing_rules_schema` |
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
| test_emit_signals_shape | JSONL lines match the exact issue-body shape | scores dict | records with `{event, provider, score\|lifecycle_complete, date}` keys |
| test_emit_signals_idempotent_no_new_file | rerun with same inputs creates **no** new file (Finding 1 fix) | first-run then re-run | `status: "noop"`, no file listed beyond the first |
| test_emit_signals_dry_run_default | emitter refuses to write without `--no-dry-run` | default invocation | `status: "dry_run"`, zero bytes written |
| test_emit_signals_append_not_overwrite | second run with NEW (event,provider,date) appends, doesn't overwrite | run A then run B with different date | file contains both sets of records |
| test_hard_gate_violation_extraction | `find_hard_gate_violations` returns a list with session id + evidence path + stage (Finding 2) | synthetic sessions with 2 gate_bypass events at stage 5 and 17 | list of 2 Violation records |
| test_pipeline_consumes_new_events | `scripts/analysis/session-analysis.sh --date X` produces non-empty output when fed ONLY new event types (Finding 8) | fixture dir with only `gate_compliance_score` + `provider_capability` events | `ANALYSIS_DIR/X.md` contains new-events section OR documented drop with warning log |
| test_routing_rules_schema | `config/agents/routing-rules.yaml` validates against `routing-rules.schema.json` (Finding 6) | live artifact | JSON-Schema validation passes |
| test_rollback_glob | `rm .claude/state/session-signals/43-compliance-*.jsonl` removes exactly this issue's output, nothing else (Finding 5) | populated signals dir + other issues' output | only prefixed files removed |

---

## Acceptance Criteria

- [ ] All new tests pass: `uv run pytest tests/session-analysis/ -v` and `bats tests/session-analysis/*.bats`
- [ ] No regression: full test suite passes as configured in CI
- [ ] `docs/standards/session-log-format-contract.md` exists and parser tests reference it
- [ ] `assets/issue-43/provider-assessment.md` exists with 6-dimension scores for claude/codex/gemini
- [ ] `assets/issue-43/session-compliance-audit.md` exists with per-provider gate-compliance scores ≥0.90 OR documented explanation of why the ≥0.90 target was not met
- [ ] Zero stage 5/7/17 hard-gate violations reported in the audit window, OR each violation is listed with evidence
- [ ] `.claude/state/session-signals/43-compliance-YYYY-MM-DD.jsonl` contains at least one `gate_compliance_score` and one `provider_capability` event for each of claude/codex/gemini; rerun produces `status: "noop"` and creates no new files
- [ ] `scripts/analysis/session-analysis.sh` produces a non-empty downstream artifact when fed the new event types (per `test_pipeline_consumes_new_events`), OR the drop behavior is documented with a warning log
- [ ] Emitter defaults to `--dry-run`; `--no-dry-run` flag required for real writes; rollback via `rm .claude/state/session-signals/43-compliance-*.jsonl` leaves all other files intact
- [ ] `config/agents/routing-rules.yaml` exists with header comment pointing to `routing-config.yaml`, a concrete top-level key set (see §Routing-Rules Schema below), and validates against `scripts/analysis/compliance/schemas/routing-rules.schema.json`
- [ ] `config/agents/behavior-contract.yaml` no longer references the orphan `.claude/work-queue/*/WRK-*.md` artifact path (or reference is replaced with `issue-NNN` path convention)
- [ ] `find_hard_gate_violations` returns a list (not just a ratio) surfaced in `session-compliance-audit.md`; zero violations is a literal empty list, not an implicit claim
- [ ] GitHub issue #43 body has an amendment comment reconciling Output 4 spec with the plan's actual emit path (Finding 4), and the description cross-links to it
- [ ] WRK-1005 (#798, #871) and WRK-1045 (#826, #950) each carry a GitHub comment cross-referencing #43 and this plan — applied via reopen→comment→reclose to defeat the silent-drop bug
- [ ] Plan review artifacts exist for Claude, Codex, Gemini under `scripts/review/results/2026-04-19-plan-43-<provider>.md`
- [ ] Implementation authored primarily by Codex via `codex:rescue`; when the Codex sandbox blocks `apply_patch` (per `feedback_codex_sandbox_write_blocked`), manual transcription by Claude is permitted AND the commit message attributes Codex as the original author (Finding 7)

---

## Adversarial Review Summary

<!-- Filled after Step 4 completes. Do NOT post to GitHub until this section has real verdicts. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MINOR | 10 findings, all absorbed in v2 (see Status header revision notes). Claude verified 10+ load-bearing claims; 5 material findings (idempotency, violation-list, intel accuracy, sandbox hedge, pipeline consumption) required structural fixes. |
| Codex | PENDING | — (queued after commit+push of v2) |
| Gemini | PENDING | — (queued after commit+push of v2) |

**Overall result:** NOT YET APPROVAL-READY — Codex + Gemini v2 reviews pending.

Revisions made based on v1 Claude review:
1. Emitter filename schema: `{date}-{HHMMSS}.jsonl` → `43-compliance-{date}.jsonl` deterministic, append-in-place (Finding 1)
2. Added `find_hard_gate_violations` pseudocode + TDD + compliance-audit section for violation list (Finding 2)
3. Corrected false "only non-issue-body mention" intel claim; added WRK-1005 6.1M-tool-call runaway context to Gaps (Finding 3)
4. Added issue-body amendment step reconciling Output 4 spec with plan's emit path (Finding 4)
5. Added `--dry-run` default + prefix-based one-glob rollback (Finding 5)
6. Added routing-rules.yaml top-level schema block + JSON Schema artifact + `test_routing_rules_schema` (Finding 6)
7. Relaxed "Codex commits" AC to permit Claude transcription when sandbox blocks writes, with author-attribution commit-message requirement (Finding 7)
8. Added `test_pipeline_consumes_new_events` integration test that actually runs `session-analysis.sh` against a new-event-only fixture (Finding 8)
9. Moved `scripts/session-analysis/` → `scripts/analysis/compliance/` to colocate with existing `scripts/analysis/session-analysis.sh` (Finding 9)
10. Scoped Q1 WRK-remap to **new artifacts only**; plan filename, issue title, and live signal events retain WRK-1107 as historical markers (Finding 10)

---

## Design Decisions (all 7 open questions resolved by user 2026-04-19)

| # | Question | Decision |
|---|---|---|
| Q1 (v2) | WRK-NNNN work-ID scheme vs `feedback_no_reserved_wrk_ids` | **Scope remap to NEW artifacts only** (per Finding 10). New asset dir is `assets/issue-43/`. Historical markers retain WRK-1107: this plan's filename, the GitHub issue title, and existing `.claude/state/session-signals/*.jsonl` stage_exit events referencing WRK IDs stay untouched (rewriting emitted signals is out of scope). `config/agents/behavior-contract.yaml` still gets its orphan `.claude/work-queue/*/WRK-*.md` reference cleaned up. |
| Q2 | `routing-rules.yaml` vs existing `routing-config.yaml` | **New file, policy-layer only**, with a concrete schema (§Routing-Rules Schema). `routing-rules.yaml` = declarative static policy; `routing-config.yaml` continues as the dynamic smart-router runtime config. Header comment in each points to the other. A JSON Schema under `scripts/analysis/compliance/schemas/` and `test_routing_rules_schema` enforce shape. |
| Q3 | Closed predecessors #798/#871/#826/#950 (no closing comment) | **Reopen → comment linking #43 + this plan → reclose**, per `feedback_gh_issue_close_silent_comment_drop`. Four issues, four cycles. |
| Q4 | Log-format contract | **New first-class deliverable:** `docs/standards/session-log-format-contract.md`. Parser tests reference it; must name a `Violation` event shape so `find_hard_gate_violations` has a spec. |
| Q5 | `session-analysis.sh` location | **Resolved** — `scripts/analysis/session-analysis.sh` (sibling `scripts/productivity/sections/session-analysis.sh` noted but out of scope). New Python modules live under `scripts/analysis/compliance/` to colocate (Finding 9). |
| Q6 (v2) | `agent:codex` execution | **Plan authored by Claude; implementation primarily dispatched to Codex via `codex:rescue`.** Hedged for sandbox-write-block (Finding 7): when Codex sandbox returns with `apply_patch` blocked, Claude transcribes Codex's emitted patch manually and the commit message attributes Codex as the original author. A pre-flight write-smoke-test is run before accepting the label. |
| Q7 (v2) | session-signals path divergence | **Emit to `.claude/state/session-signals/43-compliance-{date}.jsonl`** (deterministic per-day, issue-prefixed — replaces v1's per-session `{date}-{HHMMSS}.jsonl` which broke idempotency per Finding 1 and dropped rollback per Finding 5). Per Finding 4: also **post an amendment comment on issue #43 cross-linked from the description**, so the canonical spec matches the plan's actual emit path rather than living only in this plan's footnote. |

## Routing-Rules Schema (§)

Concrete top-level shape for `config/agents/routing-rules.yaml` (Finding 6 fix). Full JSON Schema at `scripts/analysis/compliance/schemas/routing-rules.schema.json`; enforced by `test_routing_rules_schema`.

```yaml
# config/agents/routing-rules.yaml
# Declarative static routing policy. See routing-config.yaml for dynamic runtime config.
version: 1.0.0
last_updated: "2026-04-19"

# Provider-label routing: which provider executes issues with which label.
label_routing:
  - label: "agent:claude"
    provider: claude
  - label: "agent:codex"
    provider: codex
    sandbox_hedge: claude-transcribes-when-blocked   # per Finding 7
  - label: "agent:gemini"
    provider: gemini

# Category-based defaults when no agent:* label is present.
category_defaults:
  - category: "cat:harness"
    primary: claude
    fallback: [codex, hermes]
  - category: "cat:engineering"
    primary: claude
    fallback: [gemini]

# Hard prohibitions (policy, not suggestion).
prohibitions:
  - rule: "never_route_security_review_to_sandboxed_provider"
    applies_to: ["security-review"]
  - rule: "never_self_approve"
    applies_to: ["plan-approval"]

# Cross-references to dynamic config.
see_also:
  dynamic_runtime: "config/agents/routing-config.yaml"
  provider_profiles: "config/agents/provider-capabilities.yaml"
  behavior_contract: "config/agents/behavior-contract.yaml"
```

### Risks

- **Risk — log volume / log-format drift:** the 2026-03-08→15 window spans hundreds of log files with inconsistent formats; a brittle parser will score noise as non-compliance. Mitigation: treat log-format contract as a first-class output with its own tests.
- **Risk — consolidation without predecessor artifacts:** scoring against baselines "claude=100, codex=100, gemini=95" lifted from the closed predecessors, when those predecessors left no artifact, makes the baseline unverifiable. Mitigation: recompute baselines inline from the same input cohort and document the computation.
- **Risk (v2) — production session-signals corruption:** emitter writes into the live store that `session-analysis.sh` auto-consumes nightly. Malformed or wrong-provider records would silently drive downstream reports. Mitigation: `--dry-run` default ON; `43-compliance-` filename prefix so rollback is one glob (`rm .claude/state/session-signals/43-compliance-*.jsonl`). Covered by `test_rollback_glob`.
- **Risk (v2) — pipeline silently drops new event types:** `session-analysis.sh:101` filters for `session_end`; downstream jq handlers may not recognize `gate_compliance_score`/`provider_capability`. Mitigation: `test_pipeline_consumes_new_events` runs the actual shell script against a fixture; failing the test blocks implementation.
- **Risk (v2) — Codex sandbox blocks writes mid-implementation:** `feedback_codex_sandbox_write_blocked` documents this failure mode occurred twice on issue #2342. Mitigation: Q6 v2 hedge — Claude transcribes Codex's emitted patch and attributes Codex as author; pre-flight sandbox smoke-test before label acceptance.
- **Risk — routing-rule change lands broader than intended:** routing changes cascade across all provider-selection code paths. Mitigation: keep Output 3 data-only in this plan; defer behavioral routing changes to a follow-up issue.
- **Risk — self-approval / status gate:** Claude cannot self-approve this plan. Plan must halt at `status:plan-review` for user approval.

---

## Complexity: T2

Multiple new files across `scripts/analysis/compliance/`, `tests/session-analysis/`, `assets/issue-43/`, `config/agents/`, `docs/standards/`, and `.claude/state/`; requires TDD for three modules plus integration test against `session-analysis.sh`; touches governance (closed predecessor issues, behavior-contract cleanup, issue-body amendment). All 7 original design questions resolved 2026-04-19; v2 revision absorbed 10 MINOR findings from Claude adversarial review. Not T3 because it does not cross architectural boundaries or re-define control-plane contracts — it composes within the existing `session-signals` + `routing-config` + `work-queue` primitives.
