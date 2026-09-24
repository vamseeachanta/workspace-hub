---
name: crossprovider codex generated-outputs-must-separate-from-intentional
description: Generated outputs must separate from intentional source changes in commits
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [generated-outputs, commit-hygiene, residue-review, build-artifacts]
---

Build artifacts, timestamps, UUIDs, regenerated test goldens, and nondeterministic metadata should not be committed alongside intentional code changes. Splits by generator/source are needed before merge. This is a pattern across multiple workspaces: check for fixture paths, metadata timestamps, and dashboard regeneration whenever reviewing dirty working trees.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
