---
name: crossprovider codex pre-completion-cleanup-audit-generates-artifacts
description: Pre-completion cleanup audit generates artifacts despite read-only intent
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cleanup, workflow, residue]
---

Running the pre-completion-cleanup-audit skill in read-only form can still leave generated residue: `__pycache__/`, `.uv-cache/`, pytest coverage directories. These are output from the audit script itself, not from the work being audited. Must account for them and clean or ignore them explicitly in final status checks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
