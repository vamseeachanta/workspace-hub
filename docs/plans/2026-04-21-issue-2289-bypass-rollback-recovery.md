# Plan for #2289: bypass rollback / recovery — detect, decide, revert when enforcement gates are bypassed after commit or push

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-21
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2289
> **Parent:** #2018
> **Review artifacts:** scripts/review/results/2026-04-21-plan-2289-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/enforcement/require-review-on-push.sh` already logs push-gate bypass events to `logs/hooks/review-gate-bypass.jsonl` when `SKIP_REVIEW_GATE=1` is set (lines 149–167 — `log_bypass()` function, writes JSON with user/branch/local_oid/remote_oid).
- Found: `scripts/enforcement/compliance-dashboard.sh` reads from `logs/hooks/` and emits aggregated metrics (`stage_prompt_drift_summary_json`); it is the natural place to surface detected-but-not-yet-rolled-back bypass events as a dashboard signal.
- Found: `scripts/enforcement/enforcement-env.sh` defines bypass env vars (`FORCE_PLAN_GATE_STRICT`, `SKIP_REVIEW_GATE`, `REVIEW_GATE_STRICT`) and the bypass observability contract (default strict → bypass leaves an audit record).
- Found: `scripts/enforcement/require-plan-approval.sh` is the commit-time gate (pre-commit). It does not currently emit a bypass log — gap for this plan.
- Found: `.claude/hooks/plan-approval-gate.sh` is the runtime write gate (Claude Code only). Bypass channel here is `SKIP_PLAN_APPROVAL_GATE=1` per AGENTS.md.
- Found: `.github/workflows/enforcement-gate.yml` is the CI/PR gate; post-merge bypass is only possible if both local hooks and CI are circumvented or overridden.
- Gap: no script emits a "bypass detected, proposed rollback" signal today. No automated or guided rollback flow exists.

### Standards
| Standard | Status | Source |
|---|---|---|
| Rollback policy | partial — agent-initiated auto-rollback defined | `docs/governance/TRUST-ARCHITECTURE.md` §Rollback Rules (lines 216–248) |
| Hard-stop policy | established | `docs/standards/HARD-STOP-POLICY.md` |
| Review routing | established | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` |

### Documents consulted
- GitHub issue #2289 — parent=#2018; scope: rollback trigger conditions, mechanism comparison, audit trail contract, correctness tests.
- GitHub issue #2018 — delegates rollback to this child; #2018 closure depends on #2289 reaching `status:plan-review` or later (closure dependency in `docs/plans/2026-04-13-issue-2018-agent-bypass-resistance-technical-gates.md` §Implementation Decision).
- `docs/governance/TRUST-ARCHITECTURE.md` — §Rollback Rules already defines **agent-initiated** rollback (commit + failing test = auto-revert). #2289 scope is distinct: **bypass-initiated** rollback (gate bypassed, later detected).
- `scripts/enforcement/require-review-on-push.sh` — already produces `logs/hooks/review-gate-bypass.jsonl`; this plan extends the detection signal to include commit-gate and runtime-gate bypass events.
- `scripts/enforcement/compliance-dashboard.sh` — advisory aggregation surface; this plan adds a bypass-pending-review field.

### Gaps identified
- No script enumerates bypass events across the four gates (runtime write, pre-commit, pre-push, CI) and decides rollback disposition.
- No written policy for when a logged bypass warrants auto-revert vs. guided revert vs. log-only (advisory) — `TRUST-ARCHITECTURE.md` covers agent-initiated rollback, not bypass-initiated rollback.
- No tests under `tests/enforcement/` prove rollback correctness on false positives, partial failures, or multi-file commits.
- `require-plan-approval.sh` and `plan-approval-gate.sh` do not emit bypass logs structurally comparable to `require-review-on-push.sh`.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-21 via `gh issue view`):
- `#2289` — OPEN — "Plan rollback/recovery for enforcement bypasses detected after commit or push" — labels: priority:high, cat:harness, domain:workflow
- `#2018` — OPEN — status:plan-review (rolled back 2026-04-14 after Codex+Gemini MAJOR)

**File existence** (`ls -la` 2026-04-21):
- EXISTS: `scripts/enforcement/require-review-on-push.sh` (8174 bytes, 2026-04-09)
- EXISTS: `scripts/enforcement/require-plan-approval.sh` (4651 bytes, 2026-04-20)
- EXISTS: `scripts/enforcement/compliance-dashboard.sh` (9549 bytes, 2026-04-10)
- EXISTS: `scripts/enforcement/enforcement-env.sh`
- EXISTS: `docs/governance/TRUST-ARCHITECTURE.md`
- MISSING (this plan creates): `scripts/enforcement/bypass-rollback-advisor.sh`
- MISSING (this plan creates): `tests/enforcement/test_bypass_rollback_advisor.py`
- MISSING (this plan creates): `docs/governance/BYPASS-ROLLBACK-POLICY.md`

**Line excerpts** (`sed -n` from `require-review-on-push.sh`):
```
149:log_bypass() {
150:  local bypass_dir="${REPO_ROOT}/logs/hooks"
151:  local bypass_file="${bypass_dir}/review-gate-bypass.jsonl"
...
159:  echo "{\"timestamp\":\"${timestamp}\",\"user\":\"${user}\",\"branch\":\"${branch}\",\"local_oid\":\"${LOCAL_OID}\",\"remote_oid\":\"${REMOTE_OID}\",\"action\":\"bypass\"}" >> "$bypass_file"
```

**Gap proofs**:
- `grep -r "bypass-rollback" scripts/` → no matches (no rollback advisor exists).
- `ls tests/enforcement/*rollback*` → "No such file or directory" → confirms no rollback tests.

Source count: 4 repo files + 2 GitHub issues + 2 governance docs = 8 distinct sources.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-21-issue-2289-bypass-rollback-recovery.md` |
| Policy doc (new) | `docs/governance/BYPASS-ROLLBACK-POLICY.md` |
| Advisor script (new) | `scripts/enforcement/bypass-rollback-advisor.sh` |
| Tests (new) | `tests/enforcement/test_bypass_rollback_advisor.py` |
| Commit-gate bypass logger (added) | `scripts/enforcement/require-plan-approval.sh` (added `log_bypass()` parallel to push gate) |
| Dashboard signal (updated) | `scripts/enforcement/compliance-dashboard.sh` (new `bypass_pending_review` field) |
| Plan review — Claude | `scripts/review/results/2026-04-21-plan-2289-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-21-plan-2289-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-21-plan-2289-gemini.md` |
| README index row | `docs/plans/README.md` |

---

## Deliverable

A written bypass-rollback policy (`docs/governance/BYPASS-ROLLBACK-POLICY.md`), an advisory script (`scripts/enforcement/bypass-rollback-advisor.sh`) that enumerates logged bypass events across all gates and emits a structured recommendation (`log_only` | `guided_revert` | `auto_revert_proposed`), commit-gate bypass logging parity with the push gate, a dashboard field exposing unresolved bypass events, and TDD coverage proving correctness on the bypass scenarios enumerated in §TDD Test List.

---

## Key Design Decisions (resolve in plan, reviewer-contestable)

1. **Rollback is advisory, not automatic, in this child's scope.** The advisor produces a recommendation; the human or a higher-scope tool executes. Rationale: `git reset --hard` or `git revert` on main is high-blast-radius — per the "executing actions with care" guidance, destructive rollback of shared state requires human confirmation. If a future issue needs true auto-revert, it extends this advisor; this plan does not commit to auto-revert.
2. **Bypass event ≠ rollback trigger.** A logged bypass is a *signal*. Rollback is proposed only when: (a) the bypassed commit lacks a post-hoc approval marker **and** (b) the bypassed commit touched implementation-scope files (per `require-plan-approval.sh` classification) **and** (c) no follow-up commit in the same branch has landed review evidence. This avoids false positives on ad-hoc `SKIP_REVIEW_GATE=1` pushes of doc-only changes.
3. **Audit trail preservation is mandatory.** Before any `git revert` is proposed, the advisor writes an audit record to `logs/hooks/bypass-rollback-proposals.jsonl` including: original commit SHA, bypass log entry, files touched, proposed revert SHA range, timestamp, advisor verdict. The audit record outlives the rollback.
4. **Scope boundary vs. #2018.** #2018 owns detection/prevention. This issue owns recovery. If a rollback-time requirement turns out to require hardening a gate, that is an #2018 child issue, not this issue's scope.

---

## Pseudocode

```
bypass_rollback_advisor():
    bypass_events = read_jsonl(logs/hooks/review-gate-bypass.jsonl)
    bypass_events += read_jsonl(logs/hooks/plan-gate-bypass.jsonl)    # new log from commit gate
    bypass_events += read_jsonl(logs/hooks/runtime-write-bypass.jsonl) # future: Claude hook

    for event in bypass_events:
        commit_sha = event.commit_sha or resolve_from_local_oid(event)
        if has_post_hoc_approval_marker(commit_sha):
            mark(event, "log_only_approved_later")
            continue

        touched = git_show_names_only(commit_sha)
        if all_paths_in_safe_list(touched):
            mark(event, "log_only_safe_paths")
            continue

        if any_later_commit_has_review_evidence(branch, after=commit_sha):
            mark(event, "log_only_remediated_later")
            continue

        verdict = "guided_revert" if event.pushed else "auto_revert_proposed"
        write_audit_record(event, commit_sha, touched, verdict)
        emit_recommendation(event, commit_sha, verdict)

    return non_zero_exit_if_any(guided_revert, auto_revert_proposed)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/governance/BYPASS-ROLLBACK-POLICY.md` | Written policy — trigger conditions, mechanism choice (advisory), audit contract, precedence vs TRUST-ARCHITECTURE |
| Create | `scripts/enforcement/bypass-rollback-advisor.sh` | Advisor implementation |
| Create | `tests/enforcement/test_bypass_rollback_advisor.py` | TDD suite (see §TDD Test List) |
| Modify | `scripts/enforcement/require-plan-approval.sh` | Add `log_bypass()` producing `logs/hooks/plan-gate-bypass.jsonl` with same schema as push gate |
| Modify | `scripts/enforcement/compliance-dashboard.sh` | Add `bypass_pending_review` field derived from advisor output |
| Update | `docs/plans/README.md` | New plan row |
| Update | `docs/governance/TRUST-ARCHITECTURE.md` | Cross-reference to new BYPASS-ROLLBACK-POLICY.md in §Rollback Rules |

No changes to CI workflow or runtime hooks in this issue.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_advisor_no_events_clean_exit` | No bypass events → exit 0, empty verdict list | empty log files | exit 0, `{}` |
| `test_advisor_log_only_when_post_hoc_approved` | Bypassed commit has later approval marker → verdict `log_only_approved_later` | fixture: commit + bypass log + `.planning/plan-approved/NNN.md` | verdict = log_only; no proposal |
| `test_advisor_log_only_when_safe_path_only` | Bypassed commit touched only docs/plans/ or docs/governance/ → verdict `log_only_safe_paths` | fixture: commit touching only safe paths + bypass log | verdict = log_only; no proposal |
| `test_advisor_log_only_when_remediated_later` | Later commit on same branch has review evidence → verdict `log_only_remediated_later` | fixture: bypass commit + later cross-review commit | verdict = log_only; no proposal |
| `test_advisor_proposes_guided_revert_when_pushed` | Bypassed + pushed + impl-scope + no remediation → `guided_revert` | fixture: pushed commit + bypass log + impl files | verdict = guided_revert; audit record written; exit 1 |
| `test_advisor_proposes_auto_revert_when_local_only` | Bypassed + not pushed + impl-scope + no remediation → `auto_revert_proposed` | fixture: local commit + bypass log + impl files | verdict = auto_revert_proposed; audit record written; exit 1 |
| `test_advisor_preserves_audit_record_before_any_action` | Audit record in `logs/hooks/bypass-rollback-proposals.jsonl` is written before any revert is proposed | fixture with bypass + impl change | audit JSONL line exists; contains commit_sha, files, verdict, timestamp |
| `test_advisor_multi_file_commit_reported_atomically` | Commit touching N files produces one advisor entry, not N | fixture: commit with 5 changed files | exactly one verdict entry; file list has 5 entries |
| `test_commit_gate_emits_bypass_log` | `require-plan-approval.sh` writes to `logs/hooks/plan-gate-bypass.jsonl` when `FORCE_PLAN_GATE=1` is used to bypass | fixture: staged impl change + `FORCE_PLAN_GATE=1 git commit` | bypass JSONL line exists with SHA + user + timestamp |
| `test_dashboard_surfaces_pending_bypass_count` | Compliance dashboard output includes `bypass_pending_review` count matching advisor's non-log-only count | fixture: 3 bypass events (2 log_only, 1 guided_revert) | dashboard JSON has `bypass_pending_review: 1` |

**TDD-first rule:** all 10 tests are written and failing before any implementation is landed.

---

## Acceptance Criteria

- [ ] All 10 tests pass: `uv run pytest tests/enforcement/test_bypass_rollback_advisor.py -v`
- [ ] No regression on existing enforcement tests: `uv run pytest tests/enforcement/ -v`
- [ ] `docs/governance/BYPASS-ROLLBACK-POLICY.md` exists, is referenced from TRUST-ARCHITECTURE.md §Rollback Rules, and specifies: trigger rules, advisor-not-auto-revert decision, audit contract.
- [ ] `scripts/enforcement/bypass-rollback-advisor.sh` exists, executable, exits non-zero when guided_revert/auto_revert_proposed verdicts are emitted (so it is CI-composable).
- [ ] `scripts/enforcement/require-plan-approval.sh` emits `logs/hooks/plan-gate-bypass.jsonl` on bypass with schema parallel to push-gate bypass log.
- [ ] Compliance dashboard exposes `bypass_pending_review` field.
- [ ] Review artifacts for Claude + Codex + Gemini exist under `scripts/review/results/` with dates 2026-04-21.
- [ ] Adversarial review returns APPROVE or MINOR (no unresolved MAJOR).

---

## Adversarial Review Summary

*Filled in after Step 4 — do not post to GitHub until populated.*

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | (pending) | |
| Codex | (pending) | |
| Gemini | (pending) | |

**Overall result:** (pending)

Revisions made based on review:
- (list after review)

---

## Risks and Open Questions

- **Risk:** an advisory-only design may be seen as under-delivering against the parent intent. Mitigation: the parent #2018 explicitly says rollback "need not be *implemented* before #2018 closes" — this plan honors that boundary, and any future auto-revert is tracked as an extension issue.
- **Risk:** bypass-log schema drift between push gate and new commit-gate log. Mitigation: commit-gate `log_bypass()` mirrors push-gate schema byte-for-byte; test `test_commit_gate_emits_bypass_log` asserts exact key set.
- **Risk:** false positives on the "touched implementation-scope files" check when a commit touches both safe and impl paths. Mitigation: test `test_advisor_multi_file_commit_reported_atomically` + classifier reuses `require-plan-approval.sh` existing path-classification logic (no duplication).
- **Open:** should the advisor be wired into CI? Current plan says no — CI already blocks via `enforcement-gate.yml`; the advisor is a local/nightly tool. Reviewers: please contest if CI integration should be in-scope.
- **Open:** scope of `logs/hooks/runtime-write-bypass.jsonl` — Claude Code hook does not currently emit this. This plan lists it as a future source the advisor reads lazily; if the file is absent, the advisor skips it cleanly. Reviewers: is this tolerant-read behavior acceptable?

---

## Complexity: T2

**T2** — one new module (~100-line shell script), one new doc, one new test file (~10 tests), two modified files (logger parity + dashboard field). No cross-repo changes, no new infrastructure. Design decisions are concrete and contestable.
