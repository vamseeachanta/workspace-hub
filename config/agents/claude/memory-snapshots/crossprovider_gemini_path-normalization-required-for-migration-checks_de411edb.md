---
name: crossprovider gemini path-normalization-required-for-migration-checks
description: Path normalization required for migration checksum verification
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [migration, verification, scripting]
---

Checksum parity check for migrations mapping source/**/specs/* to specs/repos/<repo>/**/specs/* requires sed/awk path normalization (strip leading dir, sort both sides) not naive diff. Raw hash mismatches occur due to path prefix differences despite content parity.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
