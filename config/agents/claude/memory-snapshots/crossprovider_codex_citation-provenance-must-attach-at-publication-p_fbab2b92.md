---
name: crossprovider codex citation-provenance-must-attach-at-publication-p
description: Citation provenance must attach at publication point, not just function results
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [standards-implementation, citation-design, public-data]
---

Standards-derived numeric constants in public libraries (e.g., breakdown_factor_initial in COATING_LIBRARY) need their own citation metadata; function-result sidecars don't reach all callers. A constant exposed publicly must carry traceable provenance at library definition, not only when returned from a helper function.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
