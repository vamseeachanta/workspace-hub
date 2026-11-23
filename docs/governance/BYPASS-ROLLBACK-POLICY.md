# Bypass Rollback / Recovery Policy

This policy defines how workspace-hub classifies enforcement bypasses detected
after commit or push. It is advisory: it detects bypass evidence, classifies the
state of the bypass, preserves audit evidence, and recommends operator action.
It does not authorize automatic revert, quarantine, force-push, or branch
mutation.

Follow-on executable implementation is tracked in
[workspace-hub #2445](https://github.com/vamseeachanta/workspace-hub/issues/2445).

## Scope

This policy applies when an enforcement surface records evidence that a workflow
gate was bypassed after a commit or push. Examples include plan-approval gate
bypasses, review-on-push bypasses, or future enforcement logs with equivalent
evidence.

Out of scope:

- Performing automatic reverts or quarantine actions.
- Rewriting the agent-initiated rollback rules in
  `docs/governance/TRUST-ARCHITECTURE.md`.
- Implementing scripts, hooks, or dashboard code in this policy issue.

## Mechanism Decision

#2289 chooses a guided advisor mechanism, not auto-revert.

The advisor must:

1. Read bypass evidence from durable logs.
2. Resolve the affected commit and branch context when possible.
3. Classify each bypass into exactly one verdict.
4. Write a structured audit record.
5. Exit non-zero only in explicit strict mode when an unresolved bypass still
   warrants human rollback review.

Any future auto-revert or quarantine mechanism must be designed as a separate
higher-scope issue and must add new verdicts or actions rather than changing the
meaning of the advisory verdicts below.

## Canonical Verdicts

Exactly one of these verdicts applies to each evaluated bypass event.

| Verdict | Applies when |
|---|---|
| `log_only_approved_later` | Post-commit approval evidence exists after the bypass and is bound to the exact bypassed SHA or a persisted revision set that still contains that unreverted SHA. |
| `log_only_reverted_later` | The bypassed commit was reverted after the bypass via `git revert` or equivalent evidence-preserving reversal. |
| `log_only_remediated_later` | A later same-branch commit materially addresses the bypassed change and explicitly identifies the bypassed SHA or revision set it corrects. |
| `log_only_safe_paths` | The bypassed commit touches only advisor-safe paths and no never-safe-listed paths. |
| `log_only_observability_gap` | The advisor cannot determine a confident verdict because required state is unavailable or ambiguous. |
| `revert_recommended` | No higher-precedence log-only verdict applies and the bypass remains actionable for human review. |

## Canonical `verdict_cause` Enum

`verdict_cause` is populated only when the verdict is
`log_only_observability_gap`; otherwise it is `null`.

Exactly these values are permitted:

| Value | Meaning |
|---|---|
| `unresolved_sha` | Bypass evidence exists but no `commit_sha` can be derived. |
| `auth_failed` | Authentication or permission failure prevented authoritative lookup for a required evidence source, including GitHub label lookup or selected push-remote state. |
| `pushed_unknown` | Git state cannot distinguish unpushed work from stale or incomplete remote refs. |
| `branch_unreachable` | The event-time branch is deleted, absent, or unavailable, including detached-HEAD events without a logged event-time branch. |
| `commit_unresolvable_locally` | The bypass event references a SHA that exists in event history but is no longer present in the local working tree. |

## Timestamp Precedence

When multiple terminal-state verdicts match the same SHA, the latest terminal
state wins.

Terminal-state verdicts are:

- `log_only_approved_later`
- `log_only_reverted_later`
- `log_only_remediated_later`

Rules:

1. Normalize all candidate timestamps to UTC RFC3339 with millisecond precision
   before comparison.
2. Use marker filesystem mtime for marker evidence, GitHub API event time for
   label evidence, and git committer date for git evidence.
3. If both marker and GitHub approval evidence bind to the same SHA or persisted
   revision set, use the later normalized timestamp as `T_approval`.
4. If approval sources imply different reviewed revisions, emit
   `log_only_observability_gap` instead of `log_only_approved_later`.
5. Emit the terminal-state verdict with the maximum timestamp.
6. If timestamps are exactly equal after normalization, prefer
   `log_only_reverted_later` over `log_only_approved_later` over
   `log_only_remediated_later`.

`log_only_safe_paths` has no timestamp. It is lower precedence than any terminal
state. `log_only_observability_gap` does not override a terminal state that can
already be proven.

## Approval Binding

`log_only_approved_later` requires persisted binding evidence. Later approval is
not enough by itself.

The binding must identify, at minimum:

- `issue_number`
- reviewed plan or marker identity
- branch context
- `commit_sha_set`, the exact ordered or sorted set of SHAs the approval was
  understood to cover

If the bypassed SHA has already been reverted, later plan approval does not
restore that SHA. The correct verdict remains `log_only_reverted_later`; any
restoration requires a new SHA and a new evaluation.

## Remediation Boundary

`log_only_remediated_later` applies only when the later commit is explicitly tied
to the bypassed SHA or revision set. Ordinary later reviewed work on the same
branch does not count as remediation.

Required remediation evidence:

1. The remediating commit is reachable from the event-time branch lineage.
2. The remediation carries explicit review or remediation evidence.
3. The evidence identifies the bypassed SHA or revision set it corrects.

Cherry-picks onto other branches do not count as same-branch remediation. Merge
commits count only when the merge commit message or uniquely introduced commits
carry the explicit remediation binding.

## Safe-List Semantics

The commit-time plan gate and the bypass advisor use different safe lists.

### `COMMIT_GATE_SAFE_PATHS`

`COMMIT_GATE_SAFE_PATHS` is defined by
`scripts/enforcement/require-plan-approval.sh` and governs whether a commit
requires plan approval before it is created.

### `ADVISOR_SAFE_PATHS`

`ADVISOR_SAFE_PATHS` governs whether a detected bypass may be classified as
`log_only_safe_paths`.

Advisor-safe paths:

- `docs/plans/**`
- `docs/reports/**`
- `.planning/**`

### Never-Safe-Listed Paths

These paths are enforcement or governance surfaces and are never eligible for
`log_only_safe_paths`, even if a future safe-list is broadened:

- `.claude/hooks/**`
- `scripts/enforcement/**`
- `.github/workflows/enforcement-gate.yml`
- `docs/governance/**`
- `docs/standards/HARD-STOP-POLICY.md`
- `docs/standards/AI_REVIEW_ROUTING_POLICY.md`
- `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md`
- `AGENTS.md`
- `CLAUDE.md`
- `GEMINI.md`
- `.codex/CODEX.md`

Paths outside the commit-gate safe list, advisor safe list, and never-safe set
receive full advisor evaluation. If no log-only verdict applies, the default is
`revert_recommended`.

## Branch Context

Same-branch remediation is determined from the bypass event's logged branch.

1. If an event-time branch is logged and still exists, same branch means commits
   reachable from that branch head.
2. A cherry-pick on another branch does not remediate the bypass on the original
   branch.
3. A merge commit on the event-time branch counts only when the merge or its
   uniquely introduced commits carry explicit remediation evidence tied to the
   bypassed SHA or revision set.
4. Branch deletion or detached-HEAD events without an event-time branch produce
   `log_only_observability_gap` with cause `branch_unreachable`, unless already
   observed terminal evidence can still be applied.

## Scenario Matrix

This matrix is normative for #2445 implementation tests.

| Scenario | Timeline | Verdict | Rationale |
|---|---|---|---|
| Bypass then approval then revert | T1 bypass, T2 approval, T3 revert | `log_only_reverted_later` | Revert is the latest terminal state. |
| Bypass then revert then plan re-approval | T1 bypass, T2 revert, T3 approval | `log_only_reverted_later` | Approval does not un-revert the SHA. |
| Bypass then remediation then approval | T1 bypass, T2 remediation, T3 approval | `log_only_approved_later` | Approval is latest while the SHA remains unreverted and bound. |
| Bypass then branch deletion | T1 bypass, T2 branch deleted | `log_only_observability_gap` with `branch_unreachable` | Branch context is unavailable. |
| Bypass in detached HEAD | T1 bypass in detached HEAD, no event branch | `log_only_observability_gap` with `branch_unreachable` | No reliable event-time branch exists. |
| Bypass then local reset removes SHA | T1 bypass, T2 local rollback removes commit | `log_only_observability_gap` with `commit_unresolvable_locally` | SHA is not locally resolvable. |
| Bypass only, pushed state unknown | T1 bypass, shallow or stale refs | `log_only_observability_gap` with `pushed_unknown` | Pushed state cannot be determined. |
| Bypass only, advisor-safe paths | T1 bypass, only `docs/plans/**` touched | `log_only_safe_paths` | Advisor safe-list applies and no terminal state exists. |
| Bypass only, enforcement path touched | T1 bypass, `.claude/hooks/**` touched | `revert_recommended` | Never-safe path, no higher verdict. |
| Bypass only, no SHA derivable | T1 bypass, missing commit SHA | `log_only_observability_gap` with `unresolved_sha` | No SHA can be evaluated. |
| Bypass, GitHub approval lookup auth fails | T1 bypass, label lookup denied | `log_only_observability_gap` with `auth_failed` | Approval state cannot be trusted. |
| Equal-timestamp approval and revert | T1 bypass, T2 approval and revert tie | `log_only_reverted_later` | Tie-break prefers revert. |
| Terminal event known, branch later unreachable | T1 bypass, T2 terminal event, T3 branch deleted | Terminal verdict from T2 | Later branch loss does not erase known terminal evidence. |

## Relationship To TRUST-ARCHITECTURE Rollback Rules

`TRUST-ARCHITECTURE.md` defines agent-initiated rollback when an agent's own
change breaks tests or violates local checks. This policy defines bypass
classification after enforcement bypass evidence exists. They are separate
decision layers.

Interaction rules:

1. Agent-initiated rollback runs first when applicable.
2. If agent rollback removes the local commit, the advisor emits
   `log_only_observability_gap` with cause `commit_unresolvable_locally` and may
   record `likely_cause: agent_initiated_rollback_per_TRUST-ARCHITECTURE`.
3. If agent rollback reverts a pushed commit through `git revert`, the advisor
   emits `log_only_reverted_later`.
4. If agent rollback was not invoked, the advisor evaluates the bypass normally.

Both policies preserve audit trails. Neither policy deletes the other's evidence.

## Audit Contract

For every evaluated or unevaluable bypass event, the advisor writes one JSONL
record to `logs/hooks/bypass-rollback-proposals.jsonl`.

Required fields:

- `timestamp`: evaluation timestamp, UTC RFC3339 with millisecond precision
- `source_event_refs`: list of `{log_file, line_offset}` references
- `commit_sha`: resolved SHA or `null`
- `commit_resolvable`: `true`, `false`, or `unknown`
- `verdict`: one of the six canonical verdicts
- `verdict_cause`: canonical cause when verdict is
  `log_only_observability_gap`; otherwise `null`
- `terminal_event_timestamp`: winning terminal timestamp, or `null` for
  timeless verdicts
- `approval_binding_source`: `marker`, `github_label`,
  `marker+github_label`, or `null`
- `bound_commit_sha_set`: sorted array of SHAs covered by approval or
  remediation evidence, or `null`
- `remediation_basis`: classification such as `same-branch-fix-commit` or
  `merge-based-remediation`, or `null`
- `pushed_state`: `true`, `false`, or `unknown`
- `branch_context`: event-time branch or `null`
- `touched_paths`: changed paths when the commit is resolvable; otherwise
  `null`
- `evaluation_rule_applied`: precedence or fallback rule name
- `commit_removed_pre_evaluation`: optional `true` for local rollback cases
- `likely_cause`: optional traceability string

Audit records must preserve bypass evidence and must not be overwritten by
later evaluations.

## Trigger Conditions

`revert_recommended` requires all of the following:

1. Bypass evidence exists for the SHA.
2. No higher-precedence verdict applies.
3. `commit_resolvable` is `true`.
4. `pushed_state` is `true` or `false`, not `unknown`.

Any other combination produces a `log_only_*` verdict.

## Operator Interface Requirements

The #2445 implementation must provide:

1. Default exit code `0`, suitable for cron and dashboards.
2. A `--strict` flag that exits non-zero when any verdict is
   `revert_recommended`.
3. A strict-mode offline exception: `pushed_unknown` does not cause non-zero
   exit only when the operator passed `--offline` or true connectivity absence
   is established for the selected push remote.
4. Runtime remote selection from the current branch's configured push remote,
   falling back to `origin` when present.
5. Runtime connectivity classification using
   `git ls-remote --exit-code <selected-remote> HEAD`.
6. Authentication or permission failures mapped to `auth_failed`, not offline.
7. JSON structured output for downstream tooling.

The documented home for future `FORCE_PLAN_GATE=1` discoverability is
`scripts/enforcement/require-plan-approval.sh --help` plus the #2445
implementation and closeout docs.

## Implementation Test Contract

#2445 must write executable tests before implementation for at least these
cases:

1. Exact `verdict_cause` enum values.
2. Latest terminal state wins after timestamp normalization.
3. Equal timestamp tie-break prefers revert.
4. Post-revert plan approval does not override revert.
5. Auth failure maps to observability gap.
6. Offline exception requires true connectivity absence or explicit flag.
7. Terminal event survives later branch deletion.
8. Detached HEAD without event branch maps to `branch_unreachable`.
9. Safe paths do not override timestamped terminal state.
10. `terminal_event_timestamp` nullability and UTC format.
11. `FORCE_PLAN_GATE=1` documentation home is discoverable.
12. Approval binding requires persisted `commit_sha_set`.
13. Later ordinary reviewed work is not remediation without explicit binding.
14. Merge-based remediation requires explicit binding.
