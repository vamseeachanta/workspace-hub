---
name: crossprovider codex standards-helper-scope-creep-via-enum-aliasing
description: Standards-helper scope creep via enum aliasing
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [standards-implementation, citation-hygiene, public-api]
---

Including coatings not in the referenced standard as silent enum aliases (e.g., COAL_TAR_EPOXY → ENAMEL, or POLYURETHANE when DNV-RP-F106 2003 has no polyurethane sheet) creates false citation provenance. Callers can emit F106 citations for out-of-scope materials. Better: enumerate only what's in the standard, document scope boundaries explicitly, or use distinct enums for extended families.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
