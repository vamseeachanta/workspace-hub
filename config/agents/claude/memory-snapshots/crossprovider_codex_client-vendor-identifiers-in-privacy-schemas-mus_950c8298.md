---
name: crossprovider codex client-vendor-identifiers-in-privacy-schemas-mus
description: Client/vendor identifiers in privacy schemas must be opaque IDs
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [privacy, schema-design, governance]
---

When a plan allows "approved root labels" in a privacy-governed schema, using raw client/project/vendor names defeats anonymization. Replace with opaque IDs; keep any raw-label map private/off-repo. Observed across llm-wiki #729/#730/#733 — all three plans leaked identity by allowing raw root labels in fields governed by privacy denylist.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
