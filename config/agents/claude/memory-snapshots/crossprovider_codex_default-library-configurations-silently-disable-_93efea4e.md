---
name: crossprovider codex default-library-configurations-silently-disable-
description: Default library configurations silently disable features — `.keep_vba=False` prevents macro detection
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [library-defaults, feature-availability, vba-detection]
---

Libraries often default to safe/minimal modes that disable inspection features. XLSX libraries skip VBA by default, so macro detection fails without explicit `keep_vba=True`. Check library defaults before assuming features work; document required config explicitly in code.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
