---
name: crossprovider codex manifest-snapshot-registry-is-empty-until-eviden
description: Manifest snapshot registry is empty until evidence is published
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [sampling, runtime-blocker, evidence-availability]
---

Operational downstream sampling cannot proceed even when planning is approved, because the trusted evidence registry (#70) remains unpopulated until #62 evidence is committed. This is a hidden runtime blocker separate from plan-review gates. Plans should explicitly defer operational sampling to after evidence publication.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
