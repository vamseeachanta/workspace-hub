---
name: crossprovider hermes commit-scope-gates-exclude-telemetry-and-state-c
description: Commit scope gates exclude telemetry and state churn
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, commit-discipline, artifact-scope]
---

When committing next-wave planning/review artifacts, use exact `git add -- path1 path2...` to include only planning/synthesis docs. Exclude provider telemetry (config/ai-tools/*.json), state files (.claude/state/), and session signals (*.jsonl) via negative pattern or explicit listing. Use `git diff --stat` to audit scope before committing.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
