---
name: crossprovider codex phase-a-metadata-only-tooling-must-provide-expli
description: Phase A metadata-only tooling must provide explicit CLI/output path contract
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [phase-a-contract, dry-run-safety, redaction]
---

Metadata-only discovery tooling (#2767, #2769) that provides only library functions without a CLI or output destination fails adversarial review. Phase A implementations must expose an explicit command-line interface, output path handling (with guardrails against /mnt/ace writes for dry-run), and tests proving redacted/public-safe outputs. Redaction must cover both the report schema and any committed example artifacts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
