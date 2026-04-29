Global rules for this next-wave autofeed follow-up worker:
- Workspace: /mnt/local-analysis/workspace-hub. cd there before any operation.
- Treat ace-linux-1 as the control plane; ace-linux-2 is overflow only.
- Planning/review/synthesis only. Do not implement production/code changes.
- Do NOT send outreach. Do NOT expose private contact details. Do NOT hardcode or print secrets.
- Do NOT apply status:plan-approved, status:plan-review, or any other label. User approval is required for label mutations.
- Do NOT run gh issue edit, gh issue comment, gh issue close, gh pr *, scripts/review/plan-review-fanout.sh, codex, gemini, or mutating Hermes commands.
- Do NOT create, edit, remove, or stage .planning/plan-approved/* markers.
- Do NOT commit or push. Do NOT stage files.
- Write exactly one primary result artifact and no other files:
  docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-label-conflict-triage-20260429-1422.md
- If evidence is insufficient, write BLOCKED/HOLD rows in the result artifact and stop.

Task: produce a read-only label-conflict resolution packet for issues #2433, #2055, #2152, #2227, and #2402, using the ace-linux-2 approved-scout as the seed but re-checking live state from ace-linux-1.

Inputs to read first:
- docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/ace2-approved-scout.md
- docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/approval-synthesis-10.md
- docs/standards/HARD-STOP-POLICY.md
- docs/plans/README.md
- Any relevant plan file under docs/plans/ and marker under .planning/plan-approved/<issue>.md for the five issues.

Do:
1. For each issue in #2433, #2055, #2152, #2227, #2402, run read-only `gh issue view <N> --json number,title,state,labels,body,comments,updatedAt,url` and record the timestamp of the live query.
2. Identify the exact conflicting state labels (for example `status:plan-approved` + `status:blocked`, `status:needs-data`, or `status:working`).
3. Read the local approval marker if present and the plan file if discoverable. If no plan file is discoverable, state that as a structural finding; do not search outside the workspace except via issue body/comments.
4. For each issue, choose exactly one recommendation and justify it in <=6 bullets:
   - KEEP-APPROVAL-CLEAR-CONFLICT (conflicting label appears stale; user/Hermes may remove it later)
   - REVOKE-APPROVAL-RESTORE-PRIOR-STATE (approval appears stale or structurally invalid; user/Hermes may demote later)
   - HOLD-FOR-USER (genuine ambiguity needing human judgment)
5. For #2055 specifically, analyze the marker-without-plan inversion and propose the least-risk reconciliation path.
6. Include a paste-ready but NOT executed command/comment appendix for the user, using `gh issue edit/comment ... --body-file` style only if mutation is recommended. Mark every command DRAFT / USER-EXECUTED ONLY.

Result artifact format:
# Label-conflict triage packet — 2026-04-29 14:22 CT

## Executive summary
- Total issues reviewed
- Recommendation counts by bucket
- Highest-risk contradiction

## Per-issue triage table
| Issue | Live labels | Marker | Plan | Conflict | Recommendation | Rationale |

## Evidence notes
One subsection per issue with live `gh` query timestamp, marker/plan paths inspected, and key comment/body evidence.

## Draft user command/comment appendix (NOT RUN)
Only commands/comments that a human could choose to run later. No status:plan-approved additions except where already present and being preserved; prefer body-file style comments. Commands must be clearly fenced and labeled DRAFT.

## Boundary compliance
- No GitHub mutations.
- No label changes.
- No comments posted.
- No approval markers created/edited/removed.
- No code/source changes.
- Exactly one result artifact written: docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-label-conflict-triage-20260429-1422.md

End with explicit lane classification: COMPLETED_WITH_RESULT or BLOCKED_WITH_RESULT.
