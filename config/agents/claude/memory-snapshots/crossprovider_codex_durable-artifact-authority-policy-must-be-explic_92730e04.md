---
name: crossprovider codex durable-artifact-authority-policy-must-be-explic
description: Durable artifact authority policy must be explicit before approval
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [durability, governance, artifact-authority, plan-review]
---

Plans that mark outputs as tier-1 authoritative or scheduled-committed must specify: exact frontmatter requirements (title, doc_key, last_updated, source_ref) with authority chain, write triggers (every run / only-on-change / manual), change-detection rules, and whether generated outputs are committed or runtime-only. Leaving policy as `TBD` or answering it only in risk sections violates the durable-artifact contract.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
