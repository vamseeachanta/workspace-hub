---
name: crossprovider hermes cross-provider-review-dispatch-blocks-on-plan-ap
description: Cross-provider review dispatch blocks on plan-approved marker file presence
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cross-provider-review, approval-gating, marker-driven]
---

Issues with `plan-approved` label but missing `.planning/plan-approved/<N>.md` marker file fail to clear the review gate, even if external artifacts are pending. Marker presence is the gate trigger; pending artifacts that don't exist in repo snapshot block approval. Marker creation must precede artifact generation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
