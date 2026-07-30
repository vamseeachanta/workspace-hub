---
name: crossprovider codex incomplete-file-artifact-contracts-allow-drift-i
description: Incomplete file/artifact contracts allow drift in outputs
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [execution-discipline, contract-specification]
---

Tasks that list expected outputs (e.g., pilot-evidence.json, tank-damping-coefficients.csv) but omit them from artifact maps or verification tests allow outputs to drift without failing closeout. Every produced artifact must be enumerated and verified mechanically; output absence must block completion.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
