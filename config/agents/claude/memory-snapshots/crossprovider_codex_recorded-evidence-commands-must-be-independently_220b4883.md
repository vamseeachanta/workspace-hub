---
name: crossprovider codex recorded-evidence-commands-must-be-independently
description: Recorded evidence commands must be independently replayable
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [audit, reproducibility, command-recording]
---

If a validation/emit operation records a command for audit purposes, ensure that exact command (with all required arguments) actually executes successfully when run independently. Omitting required flags like `--share-root` in the recorded emit command makes provenance falsely claimable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
