---
name: crossprovider hermes hook-composition-via-append-creates-unreachable-
description: Hook composition via append creates unreachable dead code after terminal exits
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hook-composition, dead-code, installation, git-hooks]
---

Pre-push hook was hand-assembled via install-hooks.sh and appended scripts in order: repo-test-gates → review → secrets/coverage → exit → stage-prompt-drift. The exit makes stage-prompt-drift unreachable. When hooks are built from ordered fragments, need deterministic reconstruction (rebuild from template or explicit insertion points), not append-and-hope.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
