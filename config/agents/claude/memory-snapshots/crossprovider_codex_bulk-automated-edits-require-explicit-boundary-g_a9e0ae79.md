---
name: crossprovider codex bulk-automated-edits-require-explicit-boundary-g
description: Bulk automated edits require explicit boundary guards plus post-hoc validation
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [automation, sed, boundary-safety, verification]
---

Blind sed replacements across shell scripts (WRK-209 uv enforcement) risk breaking shebangs, command checks, and help text; excluding submodules via grep naming alone is insufficient. Instead: allowlisted file-by-file approach, explicit exclusion patterns (`--exclude` flags), and mandatory diff validation (`git diff --name-only` boundary checks, `bash -n` on changed shells) before commit.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
