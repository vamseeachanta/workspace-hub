---
name: crossprovider codex prerequisite-validation-must-include-tool-versio
description: Prerequisite validation must include tool version checks
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [prerequisites, tool-detection, bash]
---

Complex bash-driven migrations should validate not just tool presence but version/flavor (e.g., GNU vs. mawk for awk, GNU findutils); off-flavor tools silently fail in non-obvious ways. Test tool versions early in prerequisites.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
