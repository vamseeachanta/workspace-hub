---
name: crossprovider hermes module-compat-symlinks-for-dual-layout-refactori
description: Module compat symlinks for dual-layout refactoring
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [python-packaging, compatibility-layers, refactoring]
---

Legacy paths (modules.bsee.analysis.*) vs. flat namespace (bsee.analysis.*) coexist via symlinks in flat namespace pointing to module implementation. Avoids modifying legacy imports or _compat layer.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
