---
name: crossprovider codex options-only-invocations-can-hide-missing-positi
description: Options-only invocations can hide missing positional-argument contracts
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [testing, cli-design, contract-enforcement]
---

A wrapper that accepts `--dry-run` but lacks a required positional machine identifier can reach downstream tools even when the identifier is missing. Include explicit RED/GREEN tests for options-only cases to enforce positional-argument requirements before delegating.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
