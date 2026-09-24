---
name: crossprovider codex high-privilege-cli-modes-require-explicit-securi
description: High-privilege CLI modes require explicit security warnings in documentation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, documentation, tooling]
---

Flags that disable approval processes or sandboxing (e.g., `--yolo`) must include: clear warning about removed protections, description of required external hardening, and explicit rollback procedure. Missing warnings risk unsafe deployments in contexts where risk is underestimated.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
