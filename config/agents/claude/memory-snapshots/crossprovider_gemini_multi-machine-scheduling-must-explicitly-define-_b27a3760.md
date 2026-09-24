---
name: crossprovider gemini multi-machine-scheduling-must-explicitly-define-
description: Multi-machine scheduling must explicitly define evidence collection per platform
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [multi-machine, platform-abstraction, evidence-collection, ssh-alternatives]
---

Cross-machine automation cannot assume uniform access patterns (SSH, shell tools, paths). Must explicitly map evidence interface for each platform class (Linux/macOS/Windows) and define blocking/unsupported status when evidence collection is unavailable.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
