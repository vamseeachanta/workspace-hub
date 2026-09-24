---
name: crossprovider codex standards-documentation-identity-validation-has-
description: Standards documentation identity validation has gaps
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [knowledge-wiki, metadata-integrity, standards-management]
---

Multiple pages can carry conflicting identities for the same standard code (e.g., BS 7608 combined as 1993/1993+A1/2014 in one field, with independent amendment claims elsewhere). Validation scripts enforce `doc_key` presence but not amendment/source-edition match, resolver role designation, or exact-identity uniqueness. Legacy pages lacking required metadata can still be indexed via retrieval, creating duplicate candidates. Use a single canonical-resolver selection pattern with explicit amendment constraints.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
