---
name: crossprovider codex remove-stale-status-labels-post-merge-do-not-rep
description: Remove stale status labels post-merge; do not replace with new status
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [github, issue-workflow, label-hygiene]
---

After merging a PR, remove transient status labels (e.g., `status:plan-approved`) that no longer apply. Do not invent replacement status labels; let the issue close naturally. Status transitions are driven by workflow state, not manual relabeling.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
