---
name: crossprovider gemini submodule-pointer-commits-show-cross-module-cont
description: Submodule pointer commits show cross-module contamination when working directory is dirty
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [submodules, workflow-hygiene, audit]
---

Submodule pointer-only commits can mask workspace leakage: diffs show metadata from unrelated modules (e.g., assethold PDF paths appearing in worldenergydata submodule diffs). This indicates the commit was made in a dirty working directory, risking cross-project contamination.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
