---
name: crossprovider hermes classification-fails-open-on-partially-inaccessi
description: Classification fails-open on partially-inaccessible data
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-safety, permissions-handling, classification-conservatism]
---

Classification schemes that compute duplicate/unique/partial disposition without checking `SourceInventory.errors` risk unsafe results. A source with unreadable subdirectories is still labeled definitive (e.g., `unique_only`) based on visible files only. Hidden content could reverse the classification. Solution: mark classifications as `incomplete` or `unsafe` when errors exist; never emit definitive disposition on partial inventory.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
