# Plan for #2289: bypass rollback / recovery — detect, decide, revert when enforcement gates are bypassed after commit or push

> **Status:** draft (v2, post-adversarial-review revision)
> **Complexity:** T2
> **Date:** 2026-04-21
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2289
> **Parent:** #2018
> **Review artifacts (v1):** scripts/review/results/2026-04-21-plan-2289-claude.md (MAJOR) | scripts/review/results/2026-04-21-plan-2289-gemini.md (MAJOR) | scripts/review/results/2026-04-21-plan-2289-codex.md (dispatch timed out — v2 re-dispatched)
> **Review artifacts (v2):** scripts/review/results/2026-04-21-plan-2289-claude-v2.md | ...-codex-v2.md | ...-gemini-v2.md

---

## Adversarial Review History

| Rev | Date | Claude | Codex | Gemini | Disposition |
|---|---|---|---|---|---|
| v1 | 2026-04-21 | MAJOR | (timed out — 5-min cap) | MAJOR | Revised. Key defects: (C1-Claude) `FORCE_PLAN_GATE=1` is not an actual bypass in `require-plan-approval.sh`; (G1-Gemini) pre-commit hook cannot emit commit SHA; (G2-Gemini) no dedup across gates; (G3-Gemini) `event.pushed` undefined in schema. See revision rationale below. |
| v2 | 2026-04-21 | (pending) | (pending) | (pending) | Re-dispatch after v2 edits. |

### v2 revision rationale (what changed from v1)

1. **Hook split (fixes G1, C1)** — commit-gate bypass logging is split across two hooks. Pre-commit hook emits a "gate-passed-in-advisory-mode" event to `logs/hooks/plan-gate-events.jsonl` without a SHA (SHA does not yet exist at pre-commit time). Post-commit hook emits a follow-up "bypass-landed" event to `logs/hooks/plan-gate-bypass.jsonl` with the resulting commit SHA, correlated by branch+timestamp+file-digest. This honors the git hook lifecycle. `FORCE_PLAN_GATE=1` reference in `require-plan-approval.sh` line 105's help text is retained only as user-facing documentation; the actual bypass mechanisms detected are: (a) `FORCE_PLAN_GATE_STRICT=0` advisory mode, (b) `git commit --no-verify`, (c) explicit post-commit evidence that no approval existed when the commit landed. The plan adds a genuine `FORCE_PLAN_GATE=1` env check as a parity-with-push-gate bypass path; this is the new implementation behavior, not assumed existing.
2. **Dedup by commit SHA (fixes G2)** — pseudocode now groups events by resolved `commit_sha` in a `dedupe()` phase before dispatching verdicts. Multi-gate bypasses for the same commit produce one proposal, not N.
3. **Dynamic `pushed` resolution (fixes G3)** — the `event.pushed` field is removed. The advisor now resolves `pushed` state at runtime via `git branch -r --contains <sha>` for each candidate commit.
4. **Verdict collapse (fixes Claude H2)** — single `revert_recommended` verdict with a structured `pushed: bool` field. Downstream tooling (human or higher-scope auto-revert extension) decides the mechanism.
5. **Exit semantics (fixes Claude H3)** — advisor exits 0 by default with structured output. Optional `--strict` flag produces non-zero exit when `revert_recommended` verdicts exist. The advisor's default wiring is nightly cron + local CLI; CI integration is a separate extension issue.
6. **Marker semantics (fixes Claude H1)** — `has_approval_intent(commit_sha)` replaces naive `has_post_hoc_approval_marker()`. Intent is detected by (a) marker file contents containing explicit approval phrase, or (b) a post-commit GitHub label transition to `status:plan-approved` after the commit date — not merely marker file existence.
7. **Parity claim precision (fixes Claude M1)** — "byte-for-byte parity" is replaced with explicit field map (see §Log Schema).
8. **Precedence section (fixes Claude M3)** — new §Precedence vs TRUST-ARCHITECTURE.md in the policy doc.
9. **Test renamed (fixes Claude M2)** — `test_advisor_preserves_audit_record_before_any_action` → `test_advisor_writes_audit_before_emitting_proposal`.

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/enforcement/require-review-on-push.sh` logs push-gate bypass events to `logs/hooks/review-gate-bypass.jsonl` when `SKIP_REVIEW_GATE=1` is set (lines 149–167 — `log_bypass()`, writes JSON with timestamp/user/branch/local_oid/remote_oid/action=bypass).
- Found: `scripts/enforcement/require-plan-approval.sh` is the pre-commit gate. Currently logs `plan-gate-blocked` events to `logs/hooks/plan-gate-events.jsonl` (line 113) **when it blocks**, but has NO bypass detection path — the line 105 help text `"To bypass: FORCE_PLAN_GATE=1 git commit"` is misleading documentation; the variable is not read anywhere in the script. This plan adds (a) a real `FORCE_PLAN_GATE=1` check + log, and (b) a companion post-commit hook to capture the resulting SHA.
- Found: `scripts/enforcement/compliance-dashboard.sh` reads from `logs/hooks/` and emits aggregated metrics (`stage_prompt_drift_summary_json` at line 17). Does NOT currently aggregate bypass events — this plan adds that field.
- Found: `scripts/enforcement/enforcement-env.sh` defines `FORCE_PLAN_GATE_STRICT` (opt-in strict mode) at line 17. The commit-gate script reads this variable (line 12) but NOT `FORCE_PLAN_GATE` (non-strict). Strict-vs-advisory precedence is clean; bypass-via-force is not.
- Found: `.claude/hooks/plan-approval-gate.sh` is the runtime write gate (Claude Code). Reads `SKIP_PLAN_APPROVAL_GATE=1` as bypass (line present). Does NOT currently emit a bypass log — future advisor extension; out of v2 scope (tolerant-read).
- Found: `.github/workflows/enforcement-gate.yml` is the CI/PR gate.
- Found: `docs/governance/TRUST-ARCHITECTURE.md` §Rollback Rules (lines 216–248) defines agent-initiated auto-rollback for failing tests. Distinct from bypass-initiated rollback; see §Precedence below.
- Gap (v2): no post-commit hook exists for plan-gate bypass correlation. This plan creates `scripts/enforcement/post-commit-bypass-logger.sh`.
- Gap (v2): no dedup or advisor surface exists across gates. This plan creates `scripts/enforcement/bypass-rollback-advisor.sh`.

### Standards
| Standard | Status | Source |
|---|---|---|
| Rollback policy | partial — agent-initiated auto-rollback defined | `docs/governance/TRUST-ARCHITECTURE.md` §Rollback Rules (lines 216–248) |
| Hard-stop policy | established | `docs/standards/HARD-STOP-POLICY.md` (defines no-implementation-before-approval and precedence of approval signals) |
| Review routing | established | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` (three-provider adversarial review for plans) |

### Documents consulted
- GitHub issue #2289 (body retrieved 2026-04-21) — parent=#2018; scope locked to rollback trigger conditions, mechanism comparison, audit trail, tests.
- GitHub issue #2018 — closure dependency: "#2018 cannot close until child exists and is in `status:plan-review` or later" (from `docs/plans/2026-04-13-issue-2018-agent-bypass-resistance-technical-gates.md` §Implementation Decision).
- `docs/governance/TRUST-ARCHITECTURE.md` §Rollback Rules — agent-initiated scope, distinct from bypass-initiated.
- `scripts/enforcement/require-review-on-push.sh` lines 149–170 — canonical bypass-log schema.
- `scripts/enforcement/require-plan-approval.sh` lines 1–123 in full — verified `$FORCE_PLAN_GATE` is not currently read (counter-evidence to plan v1's test premise).
- `scripts/enforcement/compliance-dashboard.sh` lines 1–40 — confirmed no current bypass aggregation.
- Adversarial reviews v1: Claude MAJOR (C1 + H1/H2/H3 + M1/M2/M3), Gemini MAJOR (G1/G2/G3), Codex (dispatch timed out — re-dispatch in v2).

### Gaps identified
- No commit-gate bypass-logging path exists today; `FORCE_PLAN_GATE=1` must be implemented (not assumed).
- No post-commit hook exists to correlate pre-commit bypass events with resulting commit SHAs.
- No dedup-by-SHA advisor phase; multi-gate bypass of the same commit would over-report without dedup.
- No runtime `pushed` resolution; relying on event fields is fragile (v1 defect).
- No written precedence policy between agent-initiated auto-rollback (TRUST-ARCHITECTURE.md) and bypass-initiated recommendation (this plan).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-21 via `gh issue view`):
- `#2289` — OPEN — "Plan rollback/recovery for enforcement bypasses detected after commit or push" — labels: priority:high, cat:harness, domain:workflow.
- `#2018` — OPEN — labels include priority:high, cat:engineering, cat:harness, domain:workflow, `status:plan-review`.

**File existence** (`ls -la` 2026-04-21):
- EXISTS: `scripts/enforcement/require-review-on-push.sh`, `require-plan-approval.sh`, `compliance-dashboard.sh`, `enforcement-env.sh`.
- EXISTS: `docs/governance/TRUST-ARCHITECTURE.md`.
- MISSING (this plan creates): `scripts/enforcement/bypass-rollback-advisor.sh`, `scripts/enforcement/post-commit-bypass-logger.sh`, `tests/enforcement/test_bypass_rollback_advisor.py`, `docs/governance/BYPASS-ROLLBACK-POLICY.md`.

**Line excerpts verifying v1 defect claims:**
```
# v1 defect evidence: require-plan-approval.sh never reads $FORCE_PLAN_GATE
$ grep -n '^[^#]*FORCE_PLAN_GATE\b' scripts/enforcement/require-plan-approval.sh
12:STRICT_MODE="${FORCE_PLAN_GATE_STRICT:-0}"
# (no match for bare FORCE_PLAN_GATE — only STRICT variant is read)
```

**Gap proofs:**
- `grep -r "bypass-rollback" scripts/` → no matches.
- `ls tests/enforcement/*rollback*` → does not exist.
- `grep -n bypass scripts/enforcement/compliance-dashboard.sh` → no matches (confirms dashboard does not currently surface bypass count).

Source count: 6 repo files + 2 GitHub issues + 3 review artifacts + 1 governance doc = 12 distinct sources.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-21-issue-2289-bypass-rollback-recovery.md` |
| Policy doc (new) | `docs/governance/BYPASS-ROLLBACK-POLICY.md` |
| Advisor script (new) | `scripts/enforcement/bypass-rollback-advisor.sh` |
| Post-commit correlator (new) | `scripts/enforcement/post-commit-bypass-logger.sh` |
| Install-hook wiring (new post-commit entry) | `scripts/enforcement/install-hooks.sh` (modify) |
| Tests (new) | `tests/enforcement/test_bypass_rollback_advisor.py` |
| Commit-gate bypass path (modified) | `scripts/enforcement/require-plan-approval.sh` (adds real `$FORCE_PLAN_GATE=1` check + `log_bypass()`) |
| Dashboard signal (modified) | `scripts/enforcement/compliance-dashboard.sh` (new `bypass_pending_review` field) |
| Plan review — Claude v2 | `scripts/review/results/2026-04-21-plan-2289-claude-v2.md` |
| Plan review — Codex v2 | `scripts/review/results/2026-04-21-plan-2289-codex-v2.md` |
| Plan review — Gemini v2 | `scripts/review/results/2026-04-21-plan-2289-gemini-v2.md` |
| README index row | `docs/plans/README.md` |

---

## Deliverable

A written bypass-rollback policy (`BYPASS-ROLLBACK-POLICY.md`), an advisor script that enumerates deduplicated commit-level bypass events and emits a structured `revert_recommended` recommendation with `pushed` resolved at runtime, a two-hook bypass-logging mechanism (pre-commit flags intent, post-commit logs the resulting SHA), parity-aware commit-gate `log_bypass()`, a compliance dashboard field for unresolved bypasses, and TDD coverage proving correctness on the scenarios in §TDD Test List.

---

## Key Design Decisions (reviewer-contestable)

1. **Advisory not automatic.** The advisor produces a `revert_recommended` verdict; human or a higher-scope tool executes. Rationale: `git reset --hard` or `git revert` on main is high-blast-radius. Future auto-revert is a separate extension issue.
2. **Bypass event ≠ rollback trigger.** A logged bypass produces `revert_recommended` only when: (a) `has_approval_intent(commit_sha)` returns false (no post-commit explicit-intent marker), AND (b) the commit touches implementation-scope files per `require-plan-approval.sh` classification (lines 26-44), AND (c) no later commit on the same branch has landed review evidence, AND (d) after dedup-by-SHA across all gate logs.
3. **Audit trail preservation.** Advisor writes an audit record to `logs/hooks/bypass-rollback-proposals.jsonl` (including source-event SHAs, files, verdict, timestamp, git-remote-pushed-state) BEFORE emitting any `revert_recommended`. Audit outlives any rollback.
4. **Scope boundary vs. #2018.** #2018 owns detection/prevention. This issue owns recovery. If rollback-time work requires gate hardening, that is a #2018 child issue.
5. **Hook split for SHA capture.** Pre-commit hook writes `plan-gate-events.jsonl` (no SHA yet available). Post-commit hook writes `plan-gate-bypass.jsonl` with resolved SHA. Advisor correlates via branch+timestamp+staged-file-digest when SHA-to-event mapping is needed.
6. **Default exit zero.** Advisor exits 0 with structured output by default. `--strict` produces non-zero when `revert_recommended` verdicts exist. Cron and CI integrations choose their own mode.

---

## Pseudocode

```
bypass_rollback_advisor(argv):
    strict_mode = parse_strict(argv)

    events = []
    events += read_jsonl(logs/hooks/review-gate-bypass.jsonl)     # push gate
    events += read_jsonl(logs/hooks/plan-gate-bypass.jsonl)       # post-commit correlator (new)
    # runtime-write bypass source (Claude hook) is future; tolerant-read
    if exists(logs/hooks/runtime-write-bypass.jsonl):
        events += read_jsonl(logs/hooks/runtime-write-bypass.jsonl)

    # Resolve commit SHA for every event before dedup.
    # Push events have local_oid (=commit SHA); plan-gate events have commit_sha
    # (written by the post-commit correlator).
    for event in events:
        event.resolved_sha = event.get("commit_sha") or event.get("local_oid") or None
        if not event.resolved_sha:
            event.verdict = "log_only_unresolved"
            continue

    # Dedup by resolved_sha.
    grouped = group_by(events, key="resolved_sha")

    for sha, sha_events in grouped.items():
        if has_approval_intent(sha):            # marker with explicit-intent phrase OR GH label transition
            emit_verdict(sha, "log_only_approved_later", sha_events)
            continue

        touched = git_show_names_only(sha)
        if all_paths_in_safe_list(touched):     # docs/plans/, docs/governance/, etc.
            emit_verdict(sha, "log_only_safe_paths", sha_events)
            continue

        if any_later_commit_has_review_evidence(sha):
            emit_verdict(sha, "log_only_remediated_later", sha_events)
            continue

        pushed = git_branch_remote_contains(sha)   # dynamic resolution (replaces event.pushed)
        audit_write(sha, sha_events, touched, pushed, verdict="revert_recommended")
        emit_verdict(sha, "revert_recommended", sha_events, pushed=pushed)

    exit_code = 0
    if strict_mode and any_verdict_is("revert_recommended"):
        exit_code = 1
    return exit_code
```

---

## Log Schema (explicit field map — replaces "byte-for-byte parity")

All three logs share base fields: `timestamp`, `user`, `branch`, `action`.

| Field | push-gate bypass (existing) | pre-commit plan-gate events (modified) | post-commit plan-gate bypass (new) |
|---|---|---|---|
| `timestamp` | ✓ | ✓ | ✓ |
| `user` | ✓ | — (add) | ✓ |
| `branch` | ✓ | ✓ | ✓ |
| `action` | `"bypass"` | `"plan-gate-blocked"` or `"plan-gate-bypass-attempted"` | `"bypass-landed"` |
| `local_oid` | ✓ | — (n/a pre-commit) | — |
| `remote_oid` | ✓ | — (n/a pre-commit) | — |
| `staged_files_digest` | — | ✓ (sha256 of staged file names) | ✓ (for correlation with pre-commit event) |
| `commit_sha` | — | — (not yet available) | ✓ (from `$GIT_COMMIT` post-commit) |

The post-commit correlator finds the matching pre-commit event by `(branch, timestamp-within-5s, staged_files_digest)` and emits a consolidated bypass record.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/governance/BYPASS-ROLLBACK-POLICY.md` | Policy: trigger rules, advisory decision, audit contract, precedence |
| Create | `scripts/enforcement/bypass-rollback-advisor.sh` | Advisor implementation per §Pseudocode |
| Create | `scripts/enforcement/post-commit-bypass-logger.sh` | Post-commit hook: correlates pre-commit event + writes bypass log with SHA |
| Create | `tests/enforcement/test_bypass_rollback_advisor.py` | TDD suite |
| Modify | `scripts/enforcement/require-plan-approval.sh` | Add real `$FORCE_PLAN_GATE=1` check + `log_bypass()` emitting `plan-gate-bypass-attempted` with staged_files_digest |
| Modify | `scripts/enforcement/install-hooks.sh` | Wire post-commit hook |
| Modify | `scripts/enforcement/compliance-dashboard.sh` | Add `bypass_pending_review` field derived from advisor |
| Update | `docs/plans/README.md` | Plan row |
| Update | `docs/governance/TRUST-ARCHITECTURE.md` | Cross-reference to BYPASS-ROLLBACK-POLICY.md §Rollback Rules |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_advisor_no_events_clean_exit` | No events → exit 0, empty verdict list | empty logs | exit 0, `{}` |
| `test_advisor_log_only_when_approval_intent_exists` | Explicit-intent marker → `log_only_approved_later` | fixture: commit + bypass log + marker with approval phrase | `log_only` |
| `test_advisor_distinguishes_advisory_mode_from_explicit_approval` | Commit from advisory-mode gate (no explicit intent) is NOT masked as approved | fixture: commit + bypass log + marker without approval phrase | `revert_recommended` |
| `test_advisor_log_only_when_safe_path_only` | Commit touching only safe paths → `log_only_safe_paths` | fixture: commit touching docs/plans/ only | `log_only` |
| `test_advisor_log_only_when_remediated_later` | Later commit on same branch has review evidence → `log_only_remediated_later` | fixture: bypass commit + later cross-review commit | `log_only` |
| `test_advisor_deduplicates_events_by_sha` | Same commit bypassing commit-gate AND push-gate produces ONE verdict, not two | fixture: commit + plan-gate-bypass + push-gate-bypass both referencing SHA `abc123` | exactly one verdict entry; audit records original events both contribute |
| `test_advisor_resolves_pushed_state_dynamically` | Advisor calls `git branch -r --contains` not `event.pushed` | fixture: unpushed commit bypass | `revert_recommended` with `pushed=false` |
| `test_advisor_revert_recommended_pushed_true` | Pushed commit → `revert_recommended` with `pushed=true` | fixture: pushed commit + bypass + impl files | verdict + audit; exit 0 (1 with --strict) |
| `test_advisor_revert_recommended_pushed_false` | Local-only bypass → `revert_recommended` with `pushed=false` | fixture: local commit + bypass + impl files | verdict + audit; exit 0 (1 with --strict) |
| `test_advisor_writes_audit_before_emitting_proposal` | Audit record written before verdict emission | fixture with bypass + impl | audit JSONL line present; contains SHA/files/verdict/timestamp/pushed |
| `test_advisor_multi_file_commit_reported_atomically` | N-file commit → one advisor entry with all N file paths | fixture: 5-file commit | one verdict entry; file list has 5 entries |
| `test_commit_gate_detects_force_plan_gate_env_var` | `FORCE_PLAN_GATE=1 git commit` is now genuinely honored by `require-plan-approval.sh` | fixture: staged impl change + `FORCE_PLAN_GATE=1 git commit` | commit succeeds; `plan-gate-events.jsonl` has action=`plan-gate-bypass-attempted` |
| `test_post_commit_correlator_emits_sha` | Post-commit hook writes bypass log with resolved SHA after pre-commit bypass event | fixture: pre-commit bypass event → commit lands | `plan-gate-bypass.jsonl` entry has `commit_sha` matching HEAD |
| `test_post_commit_correlator_matches_on_staged_file_digest` | Correlator joins on file-digest, not just branch+time | fixture: two concurrent pre-commit events on same branch, different files | correlator emits two distinct bypass records |
| `test_dashboard_surfaces_pending_bypass_count` | `compliance-dashboard.sh` output includes `bypass_pending_review` matching advisor's non-log-only count | fixture: 3 events (2 log_only, 1 revert_recommended) | dashboard JSON `bypass_pending_review: 1` |

**TDD-first rule:** all 15 tests written and failing before implementation lands.

---

## Acceptance Criteria

- [ ] All 15 tests pass: `uv run pytest tests/enforcement/test_bypass_rollback_advisor.py -v`
- [ ] No regression: `uv run pytest tests/enforcement/ -v`
- [ ] `docs/governance/BYPASS-ROLLBACK-POLICY.md` exists, is referenced from TRUST-ARCHITECTURE.md, and includes §Precedence vs agent-initiated rollback.
- [ ] `scripts/enforcement/bypass-rollback-advisor.sh` exists, executable, default exit 0, `--strict` supports non-zero on `revert_recommended`.
- [ ] `scripts/enforcement/post-commit-bypass-logger.sh` exists, installed via `install-hooks.sh`, correlates pre-commit events into `plan-gate-bypass.jsonl`.
- [ ] `scripts/enforcement/require-plan-approval.sh` genuinely honors `$FORCE_PLAN_GATE=1` and emits `plan-gate-bypass-attempted` event with staged_files_digest.
- [ ] Compliance dashboard exposes `bypass_pending_review` field.
- [ ] All three v2 review artifacts exist under `scripts/review/results/` with dates 2026-04-21.
- [ ] Adversarial review v2 returns APPROVE or MINOR (no unresolved MAJOR).

---

## Adversarial Review Summary

See §Adversarial Review History at top. v2 awaiting re-dispatch.

| Provider | Verdict | Key findings |
|---|---|---|
| Claude v1 | MAJOR | C1 (FORCE_PLAN_GATE not honored), H1-H3 (marker/verdict/CI tensions), M1-M3 (parity/precedence/test-name) — all addressed in v2 |
| Gemini v1 | MAJOR | G1 (pre-commit SHA impossibility), G2 (no dedup), G3 (event.pushed undefined) — all addressed in v2 |
| Codex v1 | dispatch timed out | re-dispatched for v2 |
| Claude v2 | (pending) | |
| Codex v2 | (pending) | |
| Gemini v2 | (pending) | |

**Overall result:** v1 NOT approval-ready; v2 pending re-review.

---

## Risks and Open Questions

- **Risk:** post-commit correlator could miss events under race conditions (two commits on same branch within 5s with identical staged-files-digest). Mitigation: staged_files_digest includes staged-file content-hash, not just names; correlator logs a `correlation_ambiguous` warning when multiple candidate pre-commit events match.
- **Risk:** `has_approval_intent()` via GitHub label transition requires `gh` auth; advisor must degrade gracefully if `gh` is unavailable (treats approval-intent as false → may over-propose reverts). Mitigation: `test_advisor_degrades_when_gh_unavailable` (add to TDD list — see Open #1 below).
- **Risk:** retrofit test `test_commit_gate_detects_force_plan_gate_env_var` changes observed behavior of `require-plan-approval.sh` for users who set `FORCE_PLAN_GATE=1` today expecting no-op. Mitigation: the pre-commit gate currently already blocks in strict mode regardless; users using `FORCE_PLAN_GATE=1` today would have found it didn't work. New behavior is additive, not breaking.
- **Resolved v1:** rollback ownership — delegated to this issue, scope locked to advisory per §Key Design Decision #1.
- **Resolved v1:** commit-SHA-at-pre-commit impossibility — addressed by hook split per §Key Design Decision #5.
- **Resolved v1:** dedup and `event.pushed` — addressed per §Pseudocode.
- **Open #1:** should `test_advisor_degrades_when_gh_unavailable` be added to the TDD list as AC-required, or tracked as follow-up? Current stance: add it in v2 implementation and mark AC-required.
- **Open #2:** scope of `install-hooks.sh` change — should this plan also add pre-push hook wiring for any new advisor output, or leave hook-wiring narrow to post-commit only? Current stance: narrow to post-commit only; pre-push advisor integration is a future extension.

---

## Precedence vs TRUST-ARCHITECTURE.md §Rollback Rules

`TRUST-ARCHITECTURE.md` §Rollback Rules (lines 216–248) defines **agent-initiated** rollback: when an agent's own commit breaks tests (auto-revert) or requires human confirmation (pushed/unrecoverable). This plan's advisor defines **bypass-initiated** rollback: when any actor's commit bypassed the enforcement gates.

Precedence when both apply to the same commit:
1. Agent-initiated auto-revert (per TRUST-ARCHITECTURE.md line 222, "Git commit (not pushed) / Reversible: Yes / Rollback method: `git reset HEAD~1`") fires first — the commit is local and has failing tests, agent reverts autonomously.
2. If agent-initiated rollback reverts the commit, bypass-rollback-advisor's later run will find no resolving commit on the branch and emit `log_only_remediated_later`.
3. If agent-initiated rollback was skipped (agent not involved, or tests passed), bypass-advisor's verdict stands.

This precedence will be re-stated in `BYPASS-ROLLBACK-POLICY.md` §Precedence.

---

## Complexity: T2

**T2** — one new shell script (~150 lines), one new post-commit hook (~60 lines), one new policy doc, one new test file (~15 tests), three modified files (commit-gate bypass logger + hooks installer + dashboard field). No cross-repo changes, no new infrastructure surface, no CI wiring. Each design decision is concrete and reviewer-contestable.
