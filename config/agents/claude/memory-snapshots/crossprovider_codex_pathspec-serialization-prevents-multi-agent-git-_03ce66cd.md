---
name: crossprovider codex pathspec-serialization-prevents-multi-agent-git-
description: Pathspec serialization prevents multi-agent git race
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, multi-agent, serialization, workspace-hub]
---

When parallel agents commit to the same repo, use `git commit -m "..." -- <file1> <file2>` form to avoid lock contention and sweep contamination. Bare `git add -A` followed by commit risks one agent staging unintended files from another agent's concurrent work. Workspace-hub rule `feedback_multi_agent_commit_serialization` enforces this pattern.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
