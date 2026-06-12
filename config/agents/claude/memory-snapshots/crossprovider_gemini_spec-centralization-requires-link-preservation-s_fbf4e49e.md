---
name: crossprovider gemini spec-centralization-requires-link-preservation-s
description: Spec centralization requires link preservation strategy
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [migration, links, specs]
---

Moving 5500+ files from repo-local specs/ to centralized specs/repos/ breaks relative Markdown links and cross-references within specs themselves. Pointer README templates address local lookup, but internal linking structure within spec files requires separate migration/update plan. (WRK-185 review, P1 critical)

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
