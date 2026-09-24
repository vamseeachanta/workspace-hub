---
name: crossprovider gemini gate-configuration-define-one-machine-readable-s
description: Gate configuration: define one machine-readable source for activation commit and update rules
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [workflow-gates, backwards-compatibility, configuration]
---

Create a single YAML configuration file that defines `gate_activation_commit` (the commit where the gate became mandatory), ownership, and update rules. All callers derive legacy/backfill decisions from this file, preventing inconsistent gate behavior across entry points.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
