---
name: crossprovider codex wrk-frontmatter-has-separate-category-and-subcat
description: WRK frontmatter has separate category and subcategory fields
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [wrk-model, data-schema, workspace-hub]
---

WRK spec items use `category:` and `subcategory:` as distinct frontmatter fields. The spec file's `domain:` metadata is used for spec organization only, not by capture scripts. Capture logic must read category/subcategory directly from WRK frontmatter, not derive from domain.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
