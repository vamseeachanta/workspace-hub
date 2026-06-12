---
name: crossprovider hermes canonical-test-commands-are-repo-specific-and-lo
description: Canonical test commands are repo-specific and load-bearing
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, ci, python, uv]
---

Each repo has specific PYTHONPATH, --noconftest flags, and uv run patterns. E.g., digitalmodel uses `PYTHONPATH=src`, worldenergydata uses `PYTHONPATH='src:../assetutilities/src' --noconftest`. Store in AGENTS.md or repo docs, and use exactly as specified for CI validation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
