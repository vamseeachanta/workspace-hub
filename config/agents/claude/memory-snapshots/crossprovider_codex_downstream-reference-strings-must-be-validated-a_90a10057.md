---
name: crossprovider codex downstream-reference-strings-must-be-validated-a
description: Downstream reference strings must be validated against output-class enum
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [schema-design, governance, modularity]
---

If a schema allows forward references to downstream consumers/systems, those reference names should be in an explicit output-class list with `raw_content_allowed=false` contract. Ungoverned references invite privacy semantics to drift across modules. Observed in llm-wiki #729 — downstream references at line 201 weren't in output-class enum (line 170), leaving #730/#734 to redefine privacy.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
