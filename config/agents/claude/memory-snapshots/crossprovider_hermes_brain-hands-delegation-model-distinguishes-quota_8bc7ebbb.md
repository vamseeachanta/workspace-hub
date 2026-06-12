---
name: crossprovider hermes brain-hands-delegation-model-distinguishes-quota
description: Brain/hands delegation model distinguishes quota pools
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, resource-allocation, multi-provider]
---

Per /goal catalog (#2695 D7), Hermes enforces a provider-quota delegation: Claude main = planning brain (Anthropic Max base), Codex/Claude Code = execution hands (OpenAI/Anthropic overage respectively). This distinction is not capability-based but quota-resource-based, guiding which agent runs which work stage.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
