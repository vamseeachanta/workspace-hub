---
name: crossprovider gemini 5mb-payload-limit-prevents-orchestrator-out-of-m
description: 5MB payload limit prevents orchestrator out-of-memory crashes
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [orchestration, resource-limits, shell-scripting]
---

Cross-review submit scripts clamp ingestion to 5MB to prevent bash OOMs when agents accidentally provide binaries or oversized reports. Hard constraint for orchestrator stability, not just a convenience.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
