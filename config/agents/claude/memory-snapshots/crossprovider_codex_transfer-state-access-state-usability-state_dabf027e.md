---
name: crossprovider codex transfer-state-access-state-usability-state
description: Transfer state ≠ access state ≠ usability state
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [data-contracts, state-modeling, schema-design, coupling]
---

Conflating these in a single status field causes coupling across consumers and multiple interpretations of 'done'. Separate concerns: transfer (have I acquired this?), access (do I have rights?), usability (is it validated and ready for use?). Let each consumer derive its own interpretation; don't let one consumer's derived state become truth for all others.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
