Global rules for this autofeed worker:
- Workspace: /mnt/local-analysis/workspace-hub. cd there before doing any work.
- Treat ace-linux-1 as the control plane; ace-linux-2 is overflow only.
- Planning/review/synthesis only. Do NOT implement production/code changes.
- Do NOT send outreach, draft outbound email to recipients, expose private contact details, or make public claims from private/raw data.
- Do NOT mutate GitHub: no gh issue edit/comment/close, no PR commands, no labels.
- Do NOT apply status:plan-approved. Do NOT apply status:plan-review.
- Do NOT create or edit .planning/plan-approved/* markers.
- Do NOT run scripts/review/plan-review-fanout.sh, codex, gemini, or mutating hermes commands.
- Do NOT commit, push, stage files, or touch unrelated dirty telemetry.
- Write exactly one result artifact, and no other files.

Task: synthesize the completed 2026-04-29 next-wave GTM/autofeed follow-up results into a single user-decision table and blocker matrix. This is a synthesis-only lane; it must not patch plans, reports, source data, GitHub issues, or generated command packs.

Inputs to read first:
- docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/gtm-review-2554-2555.md
- docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/gtm-review-2556-2557.md
- docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/approval-synthesis-10.md
- docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/ace2-approved-scout.md
- docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/ace2-blocker-prep.md
- docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-rereview-2554-20260429-1511.md
- docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-rereview-2555-standards-20260429-1712.md
- docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-rereview-2556-file-existence-20260429-1712.md
- docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-blocker-packet-2557-20260429-1559.md (if present)
- Current git status --short (read-only) and tmux session list (read-only), only to contextualize active blockers and avoid claiming clean state.

Do:
1. Build a concise table for issues #2554, #2555, #2556, #2557 with columns: current lane verdict, evidence completed, remaining blockers, whether any user decision is required, whether any autonomous next action is safe.
2. Build a second table for approved-scout / blocker-prep items from ace-linux-2 and approval-synthesis-10, noting only decisions that require the user; do not propose label mutations as autonomous.
3. Clearly distinguish artifact-layer readiness from label-layer readiness. Never say an issue is approved; use "ready for user review/disposition" where supported.
4. List exactly which follow-up lanes, if any, are safe after this synthesis. Prefer IDLE if the next step is user review, fanout permission, implementation, outreach, or status label changes.
5. Include a boundary-compliance section.

Write exactly one result artifact at:
docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-approval-synthesis-gtm-20260429-1736.md

Hard guardrails:
- No GitHub mutation, no status labels, no comments, no PRs.
- No approval markers.
- No source/code/data/report/tracker/email/outreach edits.
- No plan or storyboard patching.
- No fanout execution.
- No commits or pushes.
- If any needed input is missing, record it as UNKNOWN/MISSING in the single result artifact and stop.

End with explicit lane classification: COMPLETED_WITH_RESULT, BLOCKED_MISSING_INPUT, or BLOCKED_UNSAFE_NEXT_STEP.
