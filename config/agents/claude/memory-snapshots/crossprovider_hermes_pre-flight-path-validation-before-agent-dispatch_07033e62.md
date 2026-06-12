---
name: crossprovider hermes pre-flight-path-validation-before-agent-dispatch
description: Pre-flight path validation before agent dispatch
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [dispatch, validation, path-resolution]
---

Abstract paths in plans may not exist in the repo (e.g., `src/digitalmodel/worldenergydata/subseaiq/normalize.py` doesn't exist; should be elsewhere). Use `find`/`ls` to confirm concrete paths before handing prompts to agents—unresolved paths are silent blockers.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
