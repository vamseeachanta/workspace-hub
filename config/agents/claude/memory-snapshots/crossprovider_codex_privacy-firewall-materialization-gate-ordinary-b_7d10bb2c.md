---
name: crossprovider codex privacy-firewall-materialization-gate-ordinary-b
description: Privacy firewall materialization gate: ordinary blobs only
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [security, git, firewall]
---

Require firewall paths to be ordinary `100644` blobs (not directories/executables/symlinks) BEFORE staging/materialization. Validation failure leaves clone untouched except `.git`. Test with both valid and invalid (dir/executable) variants at each anchor.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
