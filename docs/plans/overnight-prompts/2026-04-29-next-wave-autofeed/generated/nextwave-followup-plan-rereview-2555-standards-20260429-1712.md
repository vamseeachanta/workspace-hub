Global rules for this next-wave follow-up worker:
- Workspace: /mnt/local-analysis/workspace-hub. cd there before any operation.
- Treat ace-linux-1 as the control plane; do not use ace-linux-2 from this lane.
- Do NOT send outreach. Do NOT expose private contact details. Do NOT hardcode or print secrets.
- Do NOT apply status:plan-approved or status:plan-review to any GitHub issue.
- Do NOT mutate GitHub: no gh issue edit/comment/close, no gh pr actions.
- Do NOT create or edit .planning/plan-approved/* markers.
- Do NOT implement code or production changes. This is a read-only planning/review lane.
- Do NOT run scripts/review/plan-review-fanout.sh, codex, gemini, hermes mutating commands, git commit, or git push.
- Write exactly one primary result artifact and no other files:
  docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-rereview-2555-standards-20260429-1712.md
- Do NOT overwrite any existing result artifact. If the target exists, stop and report BLOCKED in final output only.

Task: Cold-context re-review of issue #2555 after the 16:49 standards-completeness patch. Verify whether the patch resolved the two pre-existing observations from the 16:24 re-review without introducing new regressions. This is not an approval lane.

Inputs to read first:
- docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md
- docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md
- docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-rereview-2555-consistency-20260429-1624.md
- docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2555-standards-20260429-1649.md
- digitalmodel/examples/demos/gtm/data/csv_hlv_vessels.json
- digitalmodel/examples/demos/gtm/data/pipelay_vessels.json
- scripts/review/results/2026-04-29-plan-2555-claude.md
- scripts/review/results/2026-04-29-plan-2555-codex.md
- scripts/review/results/2026-04-29-plan-2555-gemini.md

Do:
1. Re-check live issue #2555 labels/state with read-only `gh issue view 2555 --json state,labels,updatedAt` if gh is available. If unavailable, mark label state as UNKNOWN and continue from filesystem evidence only.
2. Verify the current plan standards table enumerates the full distinct union of `_references` from the two JSON files, and that any intentionally omitted standards have explicit rationale.
3. Verify the C3 storyboard caption cites or rationalizes the full inherited set from csv_hlv_vessels.json, especially DNV-OS-H101.
4. Run a narrow regression hunt: provider-review gate still requires Claude+Codex+Gemini live evidence; no permissive fallback language; no self-approval/status mutation language; no source JSON/report-code/data edits; chart heading patterns and acceptance criteria remain coherent.
5. Write the single result artifact named above with sections: Executive verdict, Evidence checked, Finding-by-finding verification, New/regression findings if any, Blockers/next user decisions, Boundary compliance, Lane classification.

Allowed verdict vocabulary:
- APPROVE_FOR_USER_REVIEW (all patch objectives verified; user gate remains)
- MINOR_PATCH_NEEDED (small planning-doc issue remains)
- MAJOR_PATCH_NEEDED (substantive contradiction/regression remains)
- BLOCKED (missing evidence prevents review)

Hard guardrails:
- Do NOT mutate GitHub.
- Do NOT edit the plan/storyboard/source JSON/review artifacts.
- Do NOT create approval markers.
- Do NOT run fanout or provider CLIs.
- Do NOT write any file except the single result artifact.
- Do NOT claim status:plan-approved or status:plan-review may be applied automatically.

End with explicit lane classification.