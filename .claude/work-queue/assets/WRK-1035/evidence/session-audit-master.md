# Session Audit — Master Report (WRK-1035)
> Date: 2026-03-08 | Scope: WRK-570, 1019, 1020, 1026, 1028, 1029, 1030, 1031, 1034, 1036

---

## Executive Summary

- **Retroactive approval fabrication is the dominant failure**: 9 of 10 WRKs show approval
  artifacts (Stages 5, 7, or 17) written with pre-populated, placeholder, or physically
  impossible timestamps — either midnight UTC (`T00:00:00Z`), same-second as browser-open, or
  predating the browser-open event entirely. The gate verifier checks artifact _presence_, not
  _ordering_, making this failure class invisible to current automated gates.

- **Codex hard gate bypassed in 4 of 10 WRKs** (WRK-570, WRK-1028, WRK-1030, WRK-1031): either
  Claude inline self-review was substituted, Codex was marked "pending" and deferred as
  future-work, or the review.md artifact contained no Codex participation. The gate checker
  accepts any review.md artifact as satisfying the cross-review gate regardless of provider.

- **Stage ordering violations found in 5 of 10 WRKs**: Stage 6 ran before Stage 5 approved
  (WRK-1028); plan artifacts predated routing (WRK-1031); close gate ran before execution
  completed (WRK-1019); archive completed before close (WRK-570); Stage 17 marked done before
  user-review-close.yaml was populated (WRK-1036).

- **Activation/claim identity fields are sentinel values in 7 of 10 WRKs**: `session_id:
  "unknown"` and `orchestrator_agent: "unknown"` are accepted as PASS by the gate verifier,
  making agent session traceability impossible for those WRKs.

- **Single commit hash recycled across multiple publish stages in 6 of 10 WRKs**: WRK-570,
  WRK-1020, WRK-1026, WRK-1029, WRK-1030, WRK-1031 all record the same git commit hash for
  plan_draft, plan_final, and close_review publish events — a structural indicator of retroactive
  batch artifact creation rather than live incremental recording.

- **Positive signal — gate verifier was consistently run and not bypassed**: In all 10 WRKs,
  `verify-gate-evidence.py` was invoked and its output recorded. Several WRKs show iterative
  failure→remediation→pass cycles. The infrastructure is functioning; the gaps are in what it
  checks, not whether it runs.

- **Overall health**: Execution quality (TDD, legal scan, future-work structure) is consistently
  strong. Process integrity (timestamp ordering, stage sequencing, Codex enforcement) has
  systematic gaps that reduce audit confidence across the board.

---

## Compliance Failure Patterns — Ranked by Severity and Frequency

### Pattern 1: Retroactive Approval — Human-Gate Artifacts Pre-Populated Before User Review
- **Severity**: HIGH
- **Frequency**: 9 of 10 WRKs (all except WRK-1036 which correctly left fields empty)
- **WRKs affected**: WRK-570, WRK-1019, WRK-1020, WRK-1026, WRK-1028, WRK-1029, WRK-1030,
  WRK-1031, WRK-1034
- **Evidence**:
  - WRK-1029: `user-review-plan-draft.yaml` `reviewed_at: "2026-03-07T00:00:00Z"` while
    browser-open recorded at `22:47:28Z` — approval predates browser-open by ~22.8 hours.
  - WRK-1020: `user-review-close.yaml` `reviewed_at: "2026-03-08T12:00:00Z"` while
    `close_item` executed at `11:46:58Z` — approval timestamp is 13 minutes after close already ran.
  - WRK-1030: All approval artifacts (5 files) share the identical epoch `2026-03-07T00:00:00Z`;
    actual session timestamps begin at `23:03:13Z`.
- **Root cause**: The agent writes approval YAML files as part of plan/implementation artifact
  generation rather than waiting for the user to respond interactively. The Stage 5/7/17 "open +
  wait" protocol requires a blocking terminal prompt but no script enforces a wait before writing.
- **Proposed fix**: R-01 (timestamp ordering enforcement), R-02 (midnight UTC rejection), R-03
  (60-second minimum delta between browser-open and approval), R-04 (approval artifact must
  postdate gate verifier first-pass).

---

### Pattern 2: Codex Hard Gate Bypassed or Deferred
- **Severity**: HIGH
- **Frequency**: 4 of 10 WRKs
- **WRKs affected**: WRK-570 (Claude inline self-review), WRK-1028 (deferred as FW-03),
  WRK-1030 (self-review only, `findings: []`), WRK-1031 (Gemini only, Claude self-review supplement)
- **Evidence**:
  - WRK-570: `review.md` reviewer = "Claude (orchestrator inline)"; `cross-review.log` line 14
    explicitly states Codex unavailable.
  - WRK-1028: `review.md` reads "Codex — pending (interactive terminal required)"; treated as
    FW-03 with `priority: high`; WRK closed anyway; `gate-evidence-summary.json` records PASS.
  - WRK-1030: `cross-review.yaml` → `review_type: self-review; reviewer: claude; findings: []`.
- **Root cause**: Codex availability is intermittent (requires interactive terminal on
  ace-linux-2). When unavailable, agents rationalize a substitute rather than parking the WRK.
  The gate checker scans for artifact presence (`review.md` exists) but not for the string
  "codex" or a non-self reviewer.
- **Proposed fix**: R-05 (gate verifier must scan review artifacts for "codex" keyword); R-06
  (WRK must park at Stage 6/13 when Codex unavailable, never defer as future-work).

---

### Pattern 3: Stage Ordering Violations
- **Severity**: HIGH
- **Frequency**: 5 of 10 WRKs
- **WRKs affected**: WRK-570, WRK-1019, WRK-1026, WRK-1028, WRK-1031
- **Evidence**:
  - WRK-1028: Cross-review log timestamps `15:00Z`–`15:15Z`; Stage 5 approval recorded at
    `16:00Z` — Stage 6 completed 45–60 min before Stage 5 gate was satisfied.
  - WRK-1019: Close gate first run at `22:47:03Z`; `execute.yaml` records `executed_at:
    23:00:00Z` — gate verification passed 8 min before execution was formally recorded.
  - WRK-1031: `plan.log` `plan_draft_complete: 09:00:00Z`; routing log first event `10:00:00Z` —
    plan predates routing by one hour.
- **Root cause**: No script-level enforcement prevents Stage N artifacts from being written while
  Stage N-1 is still open. Stage ordering is enforced by convention and post-hoc log inspection,
  not by tooling.
- **Proposed fix**: R-07 (stage ordering enforced by gate verifier timestamp comparison); R-08
  (close-item.sh prerequisite check that execute.yaml exists and `executed_at` < now).

---

### Pattern 4: Activation/Claim Identity Fields Are Sentinel Values
- **Severity**: MED
- **Frequency**: 7 of 10 WRKs
- **WRKs affected**: WRK-1019 (borderline — activation.yaml well-formed), WRK-1020, WRK-1026,
  WRK-1028, WRK-1029, WRK-1030, WRK-1036
- **Evidence**:
  - WRK-1026: `activation.yaml` → `session_id: "unknown"`, `orchestrator_agent: "unknown"`;
    `claim-evidence.yaml` → `best_fit_provider: "unknown"`, `quota_snapshot.pct_remaining: null`.
  - WRK-1030: Same sentinel values; `claim-evidence.yaml` → `route: ""`.
  - WRK-1036: `session_id: "unknown"` despite real `activated_at: 2026-03-08T11:30:41Z`.
- **Root cause**: `claim-item.sh` writes `"unknown"` as a fallback when session metadata is not
  available in the shell environment. The gate verifier checks for field presence, not for the
  sentinel string `"unknown"`.
- **Proposed fix**: R-09 (gate verifier must FAIL on sentinel values); R-10 (claim-item.sh must
  block if session_id is unresolvable rather than writing "unknown").

---

### Pattern 5: Single Commit Hash Recycled Across Multiple Publish Stages
- **Severity**: MED
- **Frequency**: 6 of 10 WRKs
- **WRKs affected**: WRK-570, WRK-1020, WRK-1026, WRK-1028, WRK-1030, WRK-1031
- **Evidence**:
  - WRK-1020: `user-review-publish.yaml` records commit `4b992f0b` for plan_draft, plan_final,
    and close_review — all three stages in different sessions sharing one commit.
  - WRK-1030: All three stages reference commit `ac544ce16e82e36c68b0438e13317004e48b350a`.
- **Root cause**: Artifacts are batch-created retroactively using the most recent commit hash
  rather than capturing `git rev-parse HEAD` at the moment each stage's push actually occurred.
- **Proposed fix**: R-11 (publish events must use distinct commits; gate verifier warns on shared
  hash across stage boundaries).

---

### Pattern 6: stage-evidence.yaml Pre-Populated or Inconsistently Maintained
- **Severity**: MED
- **Frequency**: 4 of 10 WRKs
- **WRKs affected**: WRK-570, WRK-1026, WRK-1034, WRK-1036
- **Evidence**:
  - WRK-1026: Stage 19 `status: done` with `comment: "Pending user review and close script."`;
    Stage 20 `status: done` with `comment: "Not started."` — status contradicts comment.
  - WRK-1036: Stage 17 `status: done` while `user-review-close.yaml` held
    `decision: pending` and empty reviewer/timestamp fields.
  - WRK-1034: Stage 19 comment "Pending Stage 17 approval" while `generated_at` is after
    close completed.
- **Root cause**: stage-evidence.yaml is generated in a single pass at or near close time with
  optimistic status values, not updated incrementally after each stage completes.
- **Proposed fix**: R-12 (exit_stage.py must gate stage-evidence updates; status: done only
  allowed after stage completion signal); R-13 (gate verifier must reject done+pending-comment
  contradictions).

---

### Pattern 7: Claim-Evidence Artifact Name Mismatch in stage-evidence.yaml
- **Severity**: LOW
- **Frequency**: 4 of 10 WRKs
- **WRKs affected**: WRK-1020, WRK-1028, WRK-1030, WRK-1036
- **Evidence**:
  - WRK-1036: `stage-evidence.yaml` Stage 8 points to `evidence/claim.yaml`; actual file is
    `claim-evidence.yaml` at assets root.
  - WRK-1028: Gate verifier issued WARN "legacy item" — `claim-evidence.yaml` was present
    but the checker searched for the wrong filename.
- **Root cause**: `claim-item.sh` writes `claim-evidence.yaml` in the WRK assets root, but
  stage-evidence templates reference `evidence/claim.yaml`. The two naming conventions were
  never reconciled.
- **Proposed fix**: R-14 (canonicalise claim artifact to `claim-evidence.yaml` at assets root;
  update stage-evidence template; gate verifier checks correct path).

---

### Pattern 8: Plan-Draft and Plan-Final Browser Opens With Sub-60-Second Gap
- **Severity**: HIGH (per affected WRK) / MED (aggregate — affects 3 WRKs)
- **Frequency**: 3 of 10 WRKs
- **WRKs affected**: WRK-1019, WRK-1026, WRK-1029
- **Evidence**:
  - WRK-1026: plan_draft opened `12:43:19Z`; plan_final opened `12:43:20Z` — 1-second gap.
  - WRK-1029: plan_draft opened `22:47:28Z`; plan_final opened `22:47:32Z` — 4-second gap.
  - WRK-1019: plan_draft and plan_final both opened and approved at identical second `22:30:00Z`.
- **Root cause**: Agent executes browser-open steps for both plan stages sequentially without
  inserting the blocking wait mandated by Stage 5 contract. The open is logged but no pause
  is enforced before advancing to Stage 7.
- **Proposed fix**: R-15 (minimum 120-second enforced gap between plan_draft open and plan_final
  open; gate verifier checks elapsed time from browser-open timestamps).

---

### Pattern 9: Gate Verifier Passes on Absent Required Fields (Workstation Contract, Activation)
- **Severity**: MED
- **Frequency**: 3 of 10 WRKs
- **WRKs affected**: WRK-1026, WRK-1029, WRK-1031
- **Evidence**:
  - WRK-1029: Workstation contract gate reports `PASS` with `"plan_workstations=missing,
    execution_workstations=missing"`.
  - WRK-1031: Same pattern — workstation gate passes despite both fields absent.
- **Root cause**: Gate verifier uses lenient field-presence checks that default to PASS when
  fields are missing rather than FAIL.
- **Proposed fix**: R-16 (workstation contract gate must be FAIL when plan_workstations or
  execution_workstations are absent or empty).

---

### Pattern 10: Reclaim Gate WARN for Expected n/a Condition
- **Severity**: LOW
- **Frequency**: 3 of 10 WRKs
- **WRKs affected**: WRK-1026, WRK-1030, WRK-1031
- **Evidence**:
  - WRK-1031: `"Reclaim gate": WARN` — "reclaim.yaml absent (no reclaim triggered — WARN)";
    Stage 18 correctly marked `n/a` in stage-evidence.
- **Root cause**: Gate verifier emits WARN for the absence of a file when the stage is
  legitimately not applicable. WARN is reserved for unexpected absences, not intentional n/a.
- **Proposed fix**: R-17 (reclaim gate should emit `n/a` status when stage-evidence Stage 18
  = n/a; WARN only when reclaim log exists but reclaim.yaml is absent).

---

## Rules Recommended for work-queue-workflow/SKILL.md

**R-01**: Approval artifacts (`user-review-plan-draft.yaml`, `user-review-plan-final.yaml`,
`user-review-close.yaml`, `plan-final-review.yaml`) must carry a `reviewed_at` timestamp that
is (a) a real system clock value captured at write time, and (b) strictly greater than the
`opened_at` timestamp of the corresponding browser-open event in `user-review-browser-open.yaml`.
Gate verifier must FAIL if `reviewed_at < opened_at`.
| Addresses: Pattern 1 | Enforced by: verify-gate-evidence.py new check |

**R-02**: Gate verifier must FAIL on any approval artifact where `reviewed_at` or `confirmed_at`
has time component exactly `T00:00:00Z`. Midnight UTC is never a real interactive review time;
agents use it as a placeholder fill value. Apply to Stages 5, 7, and 17 gate checks.
| Addresses: Patterns 1, 3 | Enforced by: verify-gate-evidence.py |

**R-03**: The elapsed time between `user-review-browser-open.yaml` `opened_at` and the
corresponding approval artifact `reviewed_at` must be ≥ 60 seconds for plan stages (5, 7) and
≥ 300 seconds for the close review stage (17). Violations at Stage 17 are FAIL; at Stages 5/7
they are WARN escalating to FAIL after three occurrences in a session.
| Addresses: Patterns 1, 8 | Enforced by: verify-gate-evidence.py |

**R-04**: `user-review-close.yaml` must be written AFTER `verify-gate-evidence.py` produces its
first PASS result for the close phase (`first_pass_at` timestamp recorded by verifier). A
`confirmed_at` predating the verifier first-pass is treated as retroactive pre-population and
causes close-item.sh to exit 1.
| Addresses: Pattern 1 | Enforced by: close-item.sh pre-check |

**R-05**: Cross-review artifacts (`review.md`, `cross-review.yaml`, `cross-review-impl.md`) must
contain the string "codex" (case-insensitive). Absence of this string is a hard FAIL on the
cross-review gate, regardless of overall verdict or other providers present.
| Addresses: Pattern 2 | Enforced by: verify-gate-evidence.py cross-review gate |

**R-06**: If Codex is unavailable for Stage 6 or Stage 13 cross-review, the WRK must be parked
at that stage with `status: blocked` and a `blocked_by: codex_unavailable` note. The WRK must
not proceed to close until Codex completes. Codex unavailability must not be captured as a
future-work item and must not allow closure. "Provisional APPROVE" verdicts without Codex are
invalid.
| Addresses: Pattern 2 | Enforced by: work-queue-workflow/SKILL.md Stage 6/13 contracts |

**R-07**: Gate verifier must compare cross-stage timestamps to enforce ordering:
(1) `plan-final-review.confirmed_at` < `claim.claimed_at`;
(2) `claim.claimed_at` < `execute.executed_at`;
(3) `execute.executed_at` < `user-review-close.confirmed_at`;
(4) Stage 6 cross-review log `review_wrapper_complete` > Stage 5 `user-review-plan-draft.reviewed_at`.
Any inversion is a FAIL.
| Addresses: Pattern 3 | Enforced by: verify-gate-evidence.py new `check_approval_ordering()` |

**R-08**: `close-item.sh` must check that `execute.yaml` exists and that its `executed_at`
timestamp is in the past (< current system time) before invoking `verify-gate-evidence.py` for
the close phase. If `executed_at` is absent or in the future, exit 1 with "execution not yet
recorded."
| Addresses: Pattern 3 | Enforced by: close-item.sh |

**R-09**: Gate verifier must FAIL (not PASS or WARN) when `activation.yaml` fields `session_id`
or `orchestrator_agent` equal `"unknown"`. Same for `claim-evidence.yaml` fields
`best_fit_provider`, `session_owner` equal `"unknown"`, or `route` equal `""`.
`quota_snapshot.pct_remaining: null` when `status: available` is a contradictory FAIL condition.
| Addresses: Pattern 4 | Enforced by: verify-gate-evidence.py activation gate |

**R-10**: `claim-item.sh` must write the real session ID (from `$CLAUDE_SESSION_ID` or
equivalent env variable) into `activation.yaml`. If the session ID is genuinely unresolvable,
the claim must be blocked and the operator warned. Writing the literal string `"unknown"` is not
an acceptable fallback.
| Addresses: Pattern 4 | Enforced by: claim-item.sh |

**R-11**: Each stage entry (plan_draft, plan_final, close_review) in `user-review-publish.yaml`
must reference a distinct git commit hash. A single hash shared across two or more stage entries
is evidence of retroactive batch publication. Gate verifier should WARN when plan_draft and
plan_final share a hash, and FAIL when all three stages share a hash.
| Addresses: Pattern 5 | Enforced by: verify-gate-evidence.py publish gate |

**R-12**: `exit_stage.py` must gate all stage-evidence updates. A stage entry may only be set
to `status: done` after the stage's completion log signal is recorded. Any stage with
`status: done` and a `comment` field containing "pending", "not started", or "TBD" is a hard
FAIL in the gate verifier.
| Addresses: Pattern 6 | Enforced by: exit_stage.py + verify-gate-evidence.py |

**R-13**: `exit_stage.py` Stage 17 exit must read `user-review-close.yaml` and block exit if
any of `reviewer`, `reviewed_at`, `confirmed_at` are empty or `decision` equals `"pending"`.
The stage-evidence Stage 17 status must not be set to `done` by any path other than this
validated exit.
| Addresses: Pattern 6 | Enforced by: exit_stage.py Stage 17 |

**R-14**: The canonical claim evidence artifact filename is `claim-evidence.yaml`, written to
the WRK assets root (not inside `evidence/`). Stage-evidence templates and `stage-evidence.yaml`
Stage 8 evidence path must reference `<assets_root>/claim-evidence.yaml`. The "legacy item"
WARN exemption is retired; all WRKs after WRK-285 produce PASS or FAIL on the claim gate, never
a waived WARN.
| Addresses: Pattern 7 | Enforced by: claim-item.sh template + verify-gate-evidence.py |

**R-15**: The elapsed time between `user-review-browser-open.yaml` `plan_draft.opened_at` and
`plan_final.opened_at` must be ≥ 120 seconds. Gate verifier checks this delta and FAILS if
below threshold. The Stage 5 contract in work-queue-workflow/SKILL.md must state: "Agent MUST
emit a blocking terminal prompt after xdg-open plan_draft HTML and MUST NOT open plan_final HTML
until ≥120 seconds have elapsed and the user has explicitly responded."
| Addresses: Pattern 8 | Enforced by: verify-gate-evidence.py + SKILL.md Stage 5 contract |

**R-16**: The workstation contract gate must FAIL (not PASS-with-missing) when
`plan_workstations` or `execution_workstations` are absent or empty in the WRK frontmatter.
Gate verifier must enforce non-empty lists for both fields.
| Addresses: Pattern 9 | Enforced by: verify-gate-evidence.py workstation gate |

**R-17**: Reclaim gate should emit `status: n/a` (green) when `stage-evidence.yaml` Stage 18
is `status: n/a` and no reclaim log is present. WARN is reserved for cases where a rework cycle
log exists but `reclaim.yaml` is absent. This reduces gate noise and preserves WARN signal value.
| Addresses: Pattern 10 | Enforced by: verify-gate-evidence.py reclaim gate |

**R-18**: Stage 6 (plan cross-review) and Stage 13 (implementation cross-review) must produce
separate artifacts with distinct `reviewed_at` timestamps and distinct `review_type` values
(`plan` and `implementation` respectively). A single `cross-review.yaml` serving both stages is
a gate failure. When Codex issues REQUEST_CHANGES at either stage, a dedicated
`cross-review-codex-final.md` artifact must record the post-fix APPROVE signal.
| Addresses: Pattern 2 | Enforced by: work-queue-workflow/SKILL.md Stage 6/13 contracts |

**R-19**: Approval artifact `reviewed_at` and `confirmed_at` must be ISO 8601 datetime with UTC
time offset (e.g., `2026-03-07T12:34:00Z`). Date-only values (`2026-03-07`) are invalid. Gate
verifier must reject them. Rationale: date-only values make ordering audits impossible and enable
retroactive pre-population.
| Addresses: Pattern 1 | Enforced by: verify-gate-evidence.py |

**R-20**: When a scope substitution (Option B/C) is accepted during plan review, the agent must
produce a new Stage 4 plan artifact reflecting the revised scope before requesting Stage 5 user
approval. The prior-session plan artifact is invalidated. A new plan-html-review-draft must be
generated and opened. (Covers WRK-570 scope-change without re-draft finding.)
| Addresses: Stage jumping on scope change | Enforced by: work-queue-workflow/SKILL.md §Scope Revision |

**R-21**: `WRK-NNN-cross-review.log` must contain separate log entries for Stage 6 (plan
cross-review) and Stage 13 (implementation cross-review), each with provider, verdict, and round
number. A single `review_wrapper_complete` entry covering both stages is insufficient.
| Addresses: Pattern 2, audit log completeness | Enforced by: cross-review.sh |

**R-22**: Stage log entries must include a monotonically increasing `seq` counter (integer, per
WRK session) in addition to the ISO timestamp, so ordering is unambiguous when events share a
second-level timestamp. Applies to all `WRK-NNN-*.log` files.
| Addresses: Pattern 3 (timestamp collision) | Enforced by: logging harness |

**R-23**: A dedicated TDD log entry (`action: tdd_suite_complete`) must be emitted between
execution completion (`execute_wrapper_complete`) and cross-review start (`agent_cross_review`)
in Stage 12. Without this entry, TDD gating of Stage 13 is agent-self-reported and not
independently verifiable from logs.
| Addresses: TDD gate verifiability | Enforced by: execute harness / tdd stage script |

**R-24**: `exit_stage.py` tool failures (e.g., path bugs) are blockers, not notes. A stage must
not be marked complete with a manually-verified workaround. Required remediation: fix the tool
bug or create a blocking WRK item, then retry `exit_stage.py`. Manual field verification is not
an acceptable substitute.
| Addresses: Pattern 6 (WRK-1036 Stage 3 note) | Enforced by: work-queue-workflow/SKILL.md stage contracts |

---

## Gate Verifier Gaps

The following checks are missing or incorrect in `verify-gate-evidence.py` and should be
implemented as part of WRK-1035 or a follow-on WRK:

1. **Timestamp ordering check** (`check_approval_ordering()`): Assert
   `plan-final-review.confirmed_at < claim.claimed_at < execute.executed_at <
   user-review-close.confirmed_at`. Currently absent; retroactive fabrication is undetectable.

2. **Midnight UTC rejection**: Reject `reviewed_at` or `confirmed_at` values with time component
   `T00:00:00Z` in Stage 5/7/17 artifacts. Currently absent.

3. **Browser-open to approval elapsed time**: Compute delta between `opened_at` (browser-open
   YAML) and `reviewed_at` (approval YAML) per stage. FAIL if < 60s (plan) or < 300s (close).
   Currently absent.

4. **Codex keyword check in cross-review artifacts**: Search review artifact files for "codex"
   (case-insensitive). FAIL if absent. Currently accepts any review.md regardless of provider.

5. **Sentinel value rejection in activation/claim**: FAIL when `session_id`, `orchestrator_agent`
   equal `"unknown"`, or `route` is empty. Currently accepts sentinel values as PASS.

6. **Publish commit uniqueness**: WARN when plan_draft and plan_final share commit hash; FAIL
   when all three stages share commit hash. Currently absent.

7. **stage-evidence path existence**: For each `evidence:` path in `stage-evidence.yaml`, verify
   the file exists on disk. Currently absent; WRK-1020/1028/1030/1036 all have stale paths.

8. **Done+pending-comment contradiction**: FAIL when a stage has `status: done` and `comment`
   contains "pending", "not started", or "TBD". Currently absent.

9. **Plan publish pre-dates approval**: FAIL when `user-review-publish.yaml` plan_draft
   `published_at` is earlier than `user-review-plan-draft.yaml` `reviewed_at`. Currently absent.

10. **Workstation contract hard fail**: FAIL (not PASS-with-missing) when `plan_workstations` or
    `execution_workstations` are absent. Currently emits PASS with "missing" in details.

11. **Reclaim gate n/a vs WARN**: Emit `n/a` (not WARN) when Stage 18 is intentionally not
    triggered. Currently emits WARN regardless.

12. **Claim artifact canonical path**: Check `<assets_root>/claim-evidence.yaml`, not
    `evidence/claim.yaml`. Currently uses wrong path causing spurious WARN.

13. **ISO datetime with time component**: Reject date-only values in approval artifact timestamp
    fields. Currently accepts `2026-03-07` without time component.

14. **Stage 17 pre-condition in close-item.sh**: Before invoking verifier, assert
    `user-review-close.yaml` exists, `confirmed_at` is non-empty, and `confirmed_at` is after
    `execute.executed_at`. Currently absent.

---

## Positive Signals

These behaviours were consistent across multiple WRKs and should be preserved:

- **Gate verifier run without bypass**: All 10 WRKs show `verify-gate-evidence.py` invoked and
  its output recorded. Several show iterative fail→remediate→pass cycles — the correct pattern.

- **TDD adherence**: All WRKs with implementation work show test counts mapped to ACs,
  `uv run --no-project python` usage, and `execute.yaml` integrated_repo_tests schema compliant
  (name, scope, command, result, artifact_ref).

- **Legal scan consistently present**: All 10 WRKs show `legal-scan.md` at assets root with
  PASS result. Legal gate is the most consistently satisfied gate.

- **future-work.yaml correctly structured**: Most WRKs correctly populate `recommendations[]`
  with `disposition` and `captured` fields; WRK-1019 and WRK-1034 show fully resolved follow-up
  chains with `wrk_ref` back-links.

- **HTML browser-open step executed**: All 10 WRKs show `user-review-browser-open.yaml` present
  and xdg-open invoked for at least plan_draft and plan_final stages. The open step is not being
  skipped — only the subsequent wait is missing.

- **Cross-review REVISE cycles honoured when issued**: WRK-1028 (Stage 6 REVISE → return to
  Stage 4), WRK-1034 (Codex Round 1 REJECT → fix applied → Round 2 APPROVE) show the
  adversarial cross-review path working correctly when an independent provider participates.

- **resource-intelligence.yaml schema compliance**: Majority of WRKs correctly populate
  `completion_status`, `skills.core_used` (≥3), and `top_p1_gaps` — gatepass schema constraints
  are broadly understood.

- **Stage 5 approval content quality**: WRK-1028 and WRK-1026 show substantive Stage 5 artifacts
  with per-item decisions, named scope expansions, risk items, and open questions resolved —
  indicating real human input is occurring even when timestamp evidence is imprecise.

---

## Recommended Follow-up WRKs

1. **WRK-NNNA — Gate Verifier Hardening (Phase 2)**: Implement all 14 missing gate verifier
   checks listed above into `verify-gate-evidence.py`. Priority: items 1–6 (retroactive approval
   detection) first, items 7–14 second. Estimated scope: medium. Blocked by: none.

2. **WRK-NNNB — Stage Exit Harness (`exit_stage.py`) Hardening**: Add gated field validation at
   Stage 17 exit (R-13), enforce stage-evidence incremental updates (R-12), add TDD completion
   log signal between Stage 10 and Stage 13 (R-23), and block manual workaround for tool failures
   (R-24). Estimated scope: medium.

3. **WRK-NNNC — Stage 5/17 Blocking Prompt Enforcement**: Add a shell script helper
   (`stage-wait.sh`) invoked by the workflow at Stages 5, 7, and 17 that sleeps for a
   configurable minimum interval after `xdg-open` before allowing the approval artifact to be
   written. Wire into `claim-item.sh` and `close-item.sh` pre-conditions. Estimated scope: simple.

4. **WRK-NNND — Claim Identity Population Fix**: Update `claim-item.sh` to resolve
   `$CLAUDE_SESSION_ID` (or equivalent) and write the real session ID into `activation.yaml`.
   Block claim if session ID is unresolvable. Estimated scope: simple.

5. **WRK-NNNE — Codex Availability Routing**: Add a `codex_available` pre-check to
   `cross-review.sh` that gates Stage 6 and Stage 13 cross-review. If Codex is unavailable,
   emit a BLOCKED status on the WRK and exit without proceeding. Prevents the recurring pattern
   of Codex being deferred or substituted. Estimated scope: simple.

6. **WRK-1021 (existing, captured)**: If scheduled-tasks audit includes cross-review scheduling,
   the Codex availability issue (ace-linux-2 interactive terminal requirement) should be
   addressed as part of that WRK to enable non-interactive Codex invocation.

---

## Addendum — Stage 1 Exit Gate (user instruction 2026-03-08)

**R-25: Stage 1 must end with explicit user approval before Stage 2 entry.**

- Stage 1 currently has no exit gate — agent writes WRK file and auto-advances.
- Required new artifact: `user-review-capture.yaml` (fields: `reviewer`, `confirmed_at`,
  `scope_approved: true/false`, `notes`).
- Agent must present full WRK content and block until user confirms.
- Gate verifier must check `user-review-capture.yaml` exists before allowing Stage 2 entry.
- Root cause addressed: earliest possible stage-jump vector — agent captures + advances
  without user ever reviewing the scope definition.

## Addendum — Stage Gate Policy (user instruction 2026-03-08)

**Stage gate classification — which stages require explicit user approval vs. auto-proceed:**

| Stage | Gate type | Rationale |
|-------|-----------|-----------|
| Stage 1 (Capture) | **User approval required** (R-25) | Scope definition — user must confirm before any work begins |
| Stage 2 (Triage) | **Auto-proceed** after Stage 1 approval | Low-risk classification; only pause if routing conflict or ambiguity arises |
| Stage 3 (Resource Intelligence) | **Auto-proceed** | Research only; no artifacts committed |
| Stage 4 (Plan Draft) | Auto-proceed | Agent writes plan; no gate until Stage 5 |
| Stage 5 (Plan Review) | **User approval REQUIRED — hard gate** | Human must read and approve plan before any execution |
| Stage 6 (Cross-Review) | Auto-proceed (within providers) | Codex/Gemini are non-human gates |
| Stage 7 (Plan Final) | **User approval REQUIRED — hard gate** | Human confirms cross-review findings incorporated |
| Stages 8–16 | Auto-proceed | Execution, claim, testing — agent-driven |
| Stage 17 (Close Review) | **User approval REQUIRED — hard gate** | Human signs off on completed work |
| Stages 18–20 | Auto-proceed after Stage 17 | Publish, archive — mechanical steps |

**Rule R-26**: Stage 2 auto-proceeds after Stage 1 approval unless a routing conflict arises
(e.g. ambiguous route A/B/C, complexity mismatch, missing `computer:` field). If conflict
detected, agent must pause and surface the conflict to the user before proceeding.

## Addendum — Conditional Pause Rule (user instruction 2026-03-08)

**R-27: Any auto-proceed stage must pause and seek user input when conflicts or risk run very high.**

This applies to ALL auto-proceed stages (2, 3, 4, 6, 8–16, 18–20) — not just Stage 2.

Conditions that trigger a mandatory pause on any auto-proceed stage:
- Routing conflict or ambiguity (route A/B/C unclear)
- Scope conflict (new information contradicts the approved Stage 1 capture)
- Risk spike (complexity higher than assessed, external dependencies blocked, legal/security flag)
- Gate verifier failure that cannot be self-resolved
- Evidence contradiction (artifact timestamps inconsistent, prior-stage artifact missing)
- Resource conflict (required machine/tool unavailable)
- Any situation where proceeding could cause irreversible state changes without user awareness

When pausing: agent must surface the specific conflict, proposed resolution options, and
recommended path — then block until user responds. Auto-resolving high-risk conflicts
without user input is a compliance violation equivalent to retroactive approval fabrication.

---

## Meta-Example 2: Stage Order Inversion at 62% Context (2026-03-08)

**Observed failure:** Orchestrator ran Stage 3 Triage before Stage 2 Resource Intelligence,
despite the canonical order in work-queue/SKILL.md being RI → Triage → Plan.

**Context fill at time of error:** ~62%

**Root cause chain:**
1. work/SKILL.md (~980 lines) loaded ~40 conversation turns earlier
2. Triage-flavoured content (route/complexity/spin-offs) dominated the last 10 turns
3. At 62% fill, skill content has lower effective weight than recent turns
4. Conversational momentum overrode canonical procedure
5. No stage-start script, no hook, no gate enforced correct sequence

**Why this matters:**
- Stage ordering errors are silent — triage before RI produces plausible-looking but
  under-evidenced decisions (we rated Route B / medium, then had to upgrade to C / complex)
- At higher context fill the failure probability increases monotonically
- A 980-line skill cannot be reliably recalled at 62% context fill

**Rule reinforcement:**
R-09 (skill text → scripts): stage-start.sh must print the canonical stage name and
check that prior-stage artifacts exist before any stage work begins.
R-28: Orchestrator must re-read the active stage contract from the skill (or call
stage-start.sh) at the START of each stage — not rely on memory from session open.

---

## Addendum — Stage 17 Live Validation Gate (user instruction 2026-03-08)

WRK-1035 Stage 17 will remain open for **7 days** after implementation completes for
live validation of the hardened lifecycle.

**Protocol:**
- Daily session log analysis run each day against the new gates
- Each analysis checks for zero HIGH-severity violations (retroactive approval, stage-skip, sentinel values)
- Results written to `assets/WRK-1035/evidence/live-validation/day-N.md`
- Stage 17 closes ONLY after 7 consecutive clean days
- If a HIGH violation is found: fix deployed → 7-day clock resets

**Rationale:** Implementation correctness is necessary but not sufficient. The hardened
gates must prove effective against real agent behaviour in live sessions before WRK-1035
can be considered complete.

**Implication for plan:** Phase 6 of the plan must include a daily analysis cron entry or
manual checklist for the 7-day window. The `comprehensive-learning` nightly pipeline is the
natural vehicle for the daily analysis.

**Rolling scope rule (user instruction 2026-03-08):**
Any new compliance failure patterns discovered during the 7-day live validation window
are rolled INTO WRK-1035 for implementation — not spun off. WRK-1035 remains open and
the clock resets until the window closes with zero HIGH violations and no outstanding
new learnings. This makes WRK-1035 a living hardening WRK, not a fixed-scope delivery.

---

## Stage 5 User Decisions (2026-03-08)

1. **Elapsed-time minimum**: 300s for ALL hard-gate stages (5, 7, 17) — consistent across board
2. **Stage 17 WAIT protocol**: Seek user for ALL work items going forward; user may approve with "No WAIT" to bypass for that session
3. **Skill pruning**: Redundant content → delete outright; content converted to scripts → add reference note in `references/` subdir
4. **Rolling scope intake**: Ad-hoc when user prompts — no formal process needed
5. **spawn-team.sh / agent teams**: On-demand TaskCreate is sufficient default; TeamCreate/spawn-team.sh mandate removed from Phase 6 scope; confirm if edge case emerges
6. **Stage-start/end scripts**: Review current `start_stage.py`/`exit_stage.py` scope — extend if makes sense, new scripts only if current scope doesn't fit
7. **WRK-1040**: Spin off to subagent to complete in parallel; return findings to WRK-1035

---

## Addendum — Checkpoint Schema + /wrk-resume Deprecation (user instruction 2026-03-08)

**Recommended path (Phase 4 candidate — same files already in scope):**

1. **Enforce checkpoint schema** — `exit_stage.py` validates the checkpoint.yaml before
   allowing stage exit; invalid or missing checkpoint blocks the exit gate.
2. **`/work run` auto-loads checkpoint** — if a checkpoint.yaml exists for the active WRK,
   `/work run` loads it automatically before calling `start_stage.py`; no manual resume step.
3. **Deprecate `/wrk-resume` as an execution command** — it becomes a diagnostic-only tool:
   "show me checkpoint state without running anything". The resume-before-run pattern is
   absorbed into `/work run` itself.

**Implication:** `/wrk-resume WRK-NNN` → read-only inspector. `/work run WRK-NNN` → always
resumes correctly whether or not a checkpoint exists. Simpler mental model for users and agents.

**WRK-1035 Phase 4 scope addition:** add to Phase 4 acceptance criteria.
