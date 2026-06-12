---
name: crossprovider gemini document-identity-join-contract-sha256-canonical
description: Document identity join contract: sha256 canonical, md5 read-only
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [document-intelligence, schema-migration, identity-matching]
---

For matching sources with wiki pages: sha256 is the authoritative join key; md5 is accepted for reads but never positive-matches against sha256; bare hex is a conformance violation. Prevents false-positive coverage gaps during schema migrations with incomplete identity metadata.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
