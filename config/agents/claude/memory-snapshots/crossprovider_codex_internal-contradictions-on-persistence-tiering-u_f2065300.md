---
name: crossprovider codex internal-contradictions-on-persistence-tiering-u
description: Internal contradictions on persistence/tiering unresolved
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [tiering, durability, consistency]
---

Plans contradict themselves on durability/tiering: claiming a result is 'not persisted' in one section while relying on it being saved in another (e.g., attestation SHA not persisted vs. reviewers cross-checking it in saved artifacts). §7 Cross-Machine Tier Assignment and §4 flow rules must be verified against stated behavior.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
