---
name: crossprovider hermes multi-provider-plan-review-flags-uncommitted-art
description: Multi-provider plan review flags uncommitted artifacts as MAJOR
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [governance, plan-review, git-workflow, multi-provider]
---

When a plan claiming concrete artifacts (stats files, generated reports) is posted to GitHub for multi-provider review (Claude/Codex/Gemini), reviewers unanimously flag it MAJOR if those artifacts don't exist in main yet. Workaround: commit and push artifacts to main BEFORE posting plan for review; forward-looking claims without evidence trigger consensus MAJOR verdicts across all providers.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
