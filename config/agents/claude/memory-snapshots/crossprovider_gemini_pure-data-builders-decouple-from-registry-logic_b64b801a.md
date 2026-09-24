---
name: crossprovider gemini pure-data-builders-decouple-from-registry-logic
description: Pure data/builders decouple from registry logic
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [architecture-pattern, refactoring, modularity]
---

Builder functions and data models (pure configuration, no coupling) can live in a separate module from registry management. Reduces caller surface area and enables independent testing. Import order: definitions → registry → queries (no cycles).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
