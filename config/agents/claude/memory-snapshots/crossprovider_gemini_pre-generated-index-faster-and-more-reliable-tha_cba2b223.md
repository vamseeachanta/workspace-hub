---
name: crossprovider gemini pre-generated-index-faster-and-more-reliable-tha
description: Pre-generated index faster and more reliable than filesystem scan
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [architecture, performance, metadata]
---

For fleet-scale work coordination, a pre-generated INDEX.md is faster and more reliable than scanning work-item files. Regeneration is cheap (<2s for 100+ items) and must trigger after any mutation: `/work add`, `/work archive`, status changes, priority/complexity edits. INDEX becomes the source of truth; filesystem is the data store.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
