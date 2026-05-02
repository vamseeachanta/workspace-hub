# Post-MAJOR Plan Hardening with Dirty Tree (2026-04-30)

Use this reference when a session resumes from a handoff with plan-review issues that have preserved MAJOR provider artifacts, local plan files that need hardening, and a broadly dirty repository.

## Pattern
1. Treat preserved review artifacts as evidence, not stale noise. Read the latest provider files and quote/extract exact MAJOR blockers before editing.
2. Patch only the plan files needed to address the cited blockers. Keep issue labels, approval markers, and GitHub comments unchanged until fresh evidence exists.
3. Verify the patches with targeted content searches against the original blocker phrases and with `git diff --check` for the modified plan files.
4. Separately report:
   - narrow intentional modified files;
   - broad dirty-tree counts (`M`, `??`, etc.);
   - approval marker presence/absence;
   - latest provider verdict artifacts still saying `MAJOR` until rerun.
5. Do not claim approval readiness from local edits. Required next evidence is fresh post-patch Codex/Gemini/Claude review with no MAJORs, or an explicit user waiver naming the missing review evidence.
6. If Codex had stdin-stall signatures, use EOF-safe stdin-file or stdin-closed invocation and verify the fanout runner before launching long reruns.
7. If Gemini capacity returns 429/no-capacity, record it as provider unavailability, not as review approval evidence.

## Example blockers resolved in-session
- Unresolved `Open Questions` converted to decisions.
- Missing binary/runtime dependencies made explicit or avoided.
- Log directories created before appending reports.
- Operational cron cutover changed from vague instruction to explicit command/manual sequence.
- Permanent CI tests kept focused on durable behavior, not historical one-time plan-index rows.
- Public contributor contact path moved into `README.md` when no `CONTRIBUTING*` file existed.

## Reporting template
- **Reviewed:** issue numbers and latest artifact verdicts.
- **Patched:** plan files and blocker classes addressed.
- **Not mutated:** labels, approval markers, comments.
- **Still blocked by:** missing fresh post-patch no-MAJOR review or missing user waiver.
- **Dirty state:** broad counts plus narrow intentional files.
- **Next action:** rerun focused reviews, then approve only if evidence threshold is met.
