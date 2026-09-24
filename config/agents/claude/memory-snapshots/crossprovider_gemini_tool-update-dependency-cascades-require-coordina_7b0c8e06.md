---
name: crossprovider gemini tool-update-dependency-cascades-require-coordina
description: Tool update dependency cascades require coordinated version bumps
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [tool-updates, dependency-management, version-coordination, smoke-testing]
---

Updating an AI CLI tool often requires coordinated updates to underlying dependencies (Node.js versions, Python, system libraries). Smoke tests that only validate the tool binary can pass despite the tool being broken due to missing dependency versions.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
