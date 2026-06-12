---
name: crossprovider hermes plan-grounding-in-live-issues-is-load-bearing-fo
description: Plan grounding in live issues is load-bearing for implementation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [planning, dispatch, grounding]
---

Issue #2127 showed that shallow local planning (without repo-state grounding) triggers worker flagging ("local corpus is thinner than expected"). Plans need to reference live issues, repo history, and current state; static templates don't work. Hermes cascades (issue → review → handoff → implementation) beat ad-hoc dispatch.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
