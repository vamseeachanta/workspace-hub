---
name: crossprovider codex asymmetric-validation-across-asset-types-creates
description: Asymmetric validation across asset types creates hidden behavior
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation-asymmetry, asset-handling, schema-design]
---

When different asset classes (body vs auxiliary meshes, vessel vs control-surface) are validated, warned, or handled differently, plans that assume uniform behavior document false contracts. Must enumerate validation/warning behavior per asset type, not assume symmetry from parallel naming.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
