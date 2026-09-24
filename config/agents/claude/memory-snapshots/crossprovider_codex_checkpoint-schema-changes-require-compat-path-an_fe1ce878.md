---
name: crossprovider codex checkpoint-schema-changes-require-compat-path-an
description: Checkpoint schema changes require compat path and resume logic reverification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [checkpoint-semantics, schema-migration, resume-logic, WRK-1046]
---

When proposing schema changes to checkpoint files, must maintain a backwards-compatible migration path and verify that resume behavior aligns with the new schema. Codex found that a plan to switch from `current_stage`/`checkpointed_at` to `stage`/`stage_complete_at` broke resume logic because exit_stage.py would write stage N after completing it, but start_stage.py only displays resume info when checkpoint stage equals the stage being entered, creating a mismatch.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
