---
name: crossprovider codex missing-runtime-prerequisites-are-a-hard-stop-po
description: Missing runtime prerequisites are a hard stop—post blocker, don't workaround
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workflow, prerequisites, blocking, gates]
---

When execution prerequisites (Python imports, CLI tools, external runtimes like CadQuery or AQWA) are unavailable, post a blocker comment on the issue with evidence and stop. Do not attempt partial implementation, environment setup, or workarounds; leave edits for when prerequisites are satisfied.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
