---
name: crossprovider codex pdfplumber-environment-isolation
description: pdfplumber environment isolation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [environment, dependencies, isolation]
---

pdfplumber is not in base Python; install in isolated `/tmp/venv` for extraction rather than modifying repo/user Python. Remove the venv after use to avoid residue.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
