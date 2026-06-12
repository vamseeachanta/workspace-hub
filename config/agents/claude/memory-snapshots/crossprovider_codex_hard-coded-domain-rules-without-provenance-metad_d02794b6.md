---
name: crossprovider codex hard-coded-domain-rules-without-provenance-metad
description: Hard-coded domain rules without provenance metadata and mutation tests hide incorrect behavior
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [domain-conversion, code-smell, testing]
---

Multiple Ballymore conversion plans hard-coded bend-curvature signs, mesh segment lengths, and baseline-geometry detection without engineering justification or tests proving source fields influence the output. These pass weak tests while embedding wrong behavior. When a converter uses domain-specific hard-coded logic, require: (1) marked provenance in generated output, (2) mutation tests proving source data affects the value, (3) plan justification (standard, template-derived, or placeholder).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
