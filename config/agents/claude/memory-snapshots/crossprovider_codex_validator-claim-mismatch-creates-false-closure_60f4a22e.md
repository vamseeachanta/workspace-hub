---
name: crossprovider codex validator-claim-mismatch-creates-false-closure
description: Validator-claim mismatch creates false closure
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [validation, test-coverage, closure]
---

Tools like `validate-skills.sh` or contract-test runners often check a minimal subset (name/description, delimiters only) but claims expand to a full schema (version, category, type). Using the tool's output as proof without verifying the tool checks what's claimed leads to approved work that doesn't meet the stated criteria (WRK-577 happened twice).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
