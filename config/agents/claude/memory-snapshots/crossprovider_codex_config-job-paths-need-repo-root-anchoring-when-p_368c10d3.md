---
name: crossprovider codex config-job-paths-need-repo-root-anchoring-when-p
description: Config/job paths need repo-root anchoring when passed to async contexts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [scheduler-design, path-resolution, configuration]
---

Relative config paths passed to scheduler jobs fail if cwd != repo root. Paths must be resolved through a shared repo-root anchor (e.g., `_scheduler_repo_root`) so the job finds files regardless of execution context.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
