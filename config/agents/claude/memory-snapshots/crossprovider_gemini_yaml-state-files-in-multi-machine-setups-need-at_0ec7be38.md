---
name: crossprovider gemini yaml-state-files-in-multi-machine-setups-need-at
description: YAML state files in multi-machine setups need atomic ID generation
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [state-management, concurrency, multi-agent]
---

Even if 'not expected' to run concurrently, multi-machine setups (Hermes + Claude + Codex agents) read/write shared YAML state files and can race. Use atomic ID generation via separate service (e.g., next-id.sh) for any incrementing counter or lock-free state. Design state stores as append-only or transactional from the start.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
