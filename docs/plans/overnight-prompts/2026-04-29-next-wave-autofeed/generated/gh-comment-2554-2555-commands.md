# Exact gh commands to post the next-wave progress comments

These are NOT auto-executed by this lane. The user (or a permitted lane) should run them in the order below. Both comments use `--body-file` to preserve markdown formatting per the [comment-on-issues](feedback_gh_issue_comment.md) memory.

```bash
# Repository root
cd /mnt/local-analysis/workspace-hub

# #2554 — vessel-contractor outreach matrix
gh issue comment 2554 --repo vamseeachanta/workspace-hub \
  --body-file docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/generated/gh-comment-2554-nextwave.md

# #2555 — vessel capability charts
gh issue comment 2555 --repo vamseeachanta/workspace-hub \
  --body-file docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/generated/gh-comment-2555-nextwave.md
```

## Labels — DO NOT apply `status:plan-review` on either issue this wave

Both plans' acceptance criteria for `status:plan-review` require Claude + at least one of Codex/Gemini live adversarial evidence. This wave produced **only** Claude self-review (Codex + Gemini both UNAVAILABLE due to lane permission). Therefore neither issue qualifies for `status:plan-review` yet.

If a future permitted lane runs the canonical fanout and lands at least one of `scripts/review/results/2026-04-29-plan-2554-{codex,gemini}.md` (or `…-2555-{codex,gemini}.md`) with verdict APPROVE/MINOR, *then* it may apply the label. The exact gh command for that future moment is:

```bash
# Future use, after canonical Codex or Gemini artifact lands and shows APPROVE/MINOR:
gh issue edit 2554 --repo vamseeachanta/workspace-hub --add-label status:plan-review
gh issue edit 2555 --repo vamseeachanta/workspace-hub --add-label status:plan-review
```

Never apply `status:plan-approved` from any agent lane. That label is the user's gate per `feedback_never_offer_to_self_label_plan_approved.md` and the planning-workflow rules.
