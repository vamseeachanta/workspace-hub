---
name: crossprovider codex stale-handoff-detection-before-nested-agent-exec
description: Stale handoff detection before nested-agent execution
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [nested-agent, handoff, stale-automation, pr-workflow]
---

Saved `codex exec` handoff prompts can become stale if the PR merges before execution (head branch deleted, PR already squashed). Check GitHub PR status before running saved commands to avoid nested-agent attempts to push to deleted branches, which recreates orphan commits.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
