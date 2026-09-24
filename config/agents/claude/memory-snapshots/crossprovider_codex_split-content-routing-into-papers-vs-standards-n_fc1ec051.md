---
name: crossprovider codex split-content-routing-into-papers-vs-standards-n
description: Split content routing into papers vs. standards namespaces
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [routing, namespace-separation, extensible-design]
---

Papers (proceedings, SPE, ONS) extract to `papers/<paper-id>/...` with datasets under `datasets/papers/<paper-id>/`. Standards extract to `standards/<code-id>/...`. Route by content markers (e.g., `spe/proceedings` in filename/text → papers). This pattern extends to other content types by adding new markers and namespace branches.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
