---
name: crossprovider codex codex-sandbox-bwrap-loopback-regression-requires
description: Codex sandbox bwrap loopback regression requires GitHub connector fallback
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [codex-sandbox, github-connector, regression-workaround]
---

Codex sandbox consistently fails with `bwrap: loopback: Failed RTM_NEWADDR` when attempting local shell file reads. Workaround: switch to GitHub connector for read-only verification and explicitly cite connector evidence as lower-confidence than attested artifacts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
