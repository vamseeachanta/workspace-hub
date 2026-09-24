---
name: crossprovider gemini sha256-namespace-enforcement-with-legacy-md5-rea
description: sha256: namespace enforcement with legacy md5 read-only tolerance
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [identity-contracts, provenance, standards]
---

Canonical doc_key format is `sha256:<64-hex>`. Legacy `md5:<hex>` accepted for reads only, never written. Path-only identity is forbidden. Tools must reject bare hex, and frontmatter `doc_key` fields hash content only (excluding frontmatter to avoid circular definition).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
