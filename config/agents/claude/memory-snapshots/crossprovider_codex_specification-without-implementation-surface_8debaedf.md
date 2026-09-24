---
name: crossprovider codex specification-without-implementation-surface
description: Specification without implementation surface
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [specification, api-contract, data-structures, acceptance-criteria]
---

Plans can mandate a behavior (warnings serialized into preflight manifests, result artifacts exposed via a field) without ensuring the data structure or API surface exists to carry it. Example: plan #609 required warnings in manifests but SpecConverter and RunResult have no warning/manifest fields, and files-to-change deferred runner modifications. Acceptance criteria become impossible to verify.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
