---
name: crossprovider codex extract-pure-shell-helpers-to-enable-testable-si
description: Extract pure shell helpers to enable testable, side-effect-free unit testing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, shell, test-patterns, isolation]
---

For bash scripts with environment-dependent behavior (device selection, environment variable parsing), extract pure helper functions into sourced libraries. Tests can then stub `arecord`, `gsettings`, `HOME`, repo paths without triggering side effects like audio recording or user env mutation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
