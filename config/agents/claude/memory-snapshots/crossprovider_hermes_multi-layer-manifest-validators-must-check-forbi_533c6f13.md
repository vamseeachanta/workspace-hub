---
name: crossprovider hermes multi-layer-manifest-validators-must-check-forbi
description: Multi-layer manifest validators must check forbidden patterns, target existence, and link context separately
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validator-design, manifest-checks, code-span-paths]
---

Single-layer validators (checking only `/mnt/ace` or only markdown syntax) miss entire defect classes. Effective validators need: (1) broad forbidden pattern scanning (`/home|/mnt|/tmp|/var|/etc` for absolute paths), (2) code-span path existence checks (repo-relative references must point to real files), (3) Markdown link context validation (resolve each link from its file's perspective). Also guard against `sys.modules` pollution in Python validators—tests may pollute the module cache.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
