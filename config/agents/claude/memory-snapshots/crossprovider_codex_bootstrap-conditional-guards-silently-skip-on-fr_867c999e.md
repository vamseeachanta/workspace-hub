---
name: crossprovider codex bootstrap-conditional-guards-silently-skip-on-fr
description: Bootstrap conditional guards silently skip on fresh machines
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bootstrap, setup, fresh-machine, conditional-hazard]
---

Setup scripts that gate critical installation steps on provider directories (`if [[ -d ~/.provider ]]; then install`) will skip those steps on fresh machines where those directories don't exist yet. Plans claiming "automated setup" must pre-create guard directories or remove the conditional for first-run.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
