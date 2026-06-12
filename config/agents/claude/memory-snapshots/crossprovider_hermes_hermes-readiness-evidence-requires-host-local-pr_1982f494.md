---
name: crossprovider hermes hermes-readiness-evidence-requires-host-local-pr
description: Hermes readiness evidence requires host-local proof and coordinator metadata
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, dispatch, readiness]
---

Remote dispatch hosts must generate `--evidence-dir` output (readiness proof) locally and provide it to coordinator. Host cannot be added to Telegram/Hermes control plane without evidence. This prevents stale/absent configuration from silently blocking dispatch.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
