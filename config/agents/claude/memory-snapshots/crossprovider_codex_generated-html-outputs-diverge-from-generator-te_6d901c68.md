---
name: crossprovider codex generated-html-outputs-diverge-from-generator-te
description: Generated HTML outputs diverge from generator templates post-migration
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [generator-staleness, brand-migration, output-divergence]
---

19 Python generators emit 54 committed HTML pages; 51 outputs were brand-migrated in-place (e.g., `896a0955`, `79503ac6`, `21e75a4c`), but generator templates remain stale with old token declarations (navy/teal hardcodes). Regenerating any output overwrites committed brand with old styles. Committed pages link externalized `brand.css` while generators still redeclare core tokens.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
