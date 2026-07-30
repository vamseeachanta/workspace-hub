---
name: crossprovider codex evidence-schema-design-requires-explicit-role-en
description: Evidence schema design requires explicit role enumeration and solver binding
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [schema-design, acceptance-workflow, evidence-provenance]
---

When designing schemas for evidence/result provenance in acceptance workflows, roles (primary/context/comparison) and solver/run identity cannot be implicit or prose-documented—they must be mandatory enumerated fields in the schema itself. Evidence-graph rules (e.g., solver conclusions use only same-solver primary evidence, comparisons bind only accepted upstream manifests) must be enforced by schema constraints and regression tests, not just planning text. Absence of these fields allows cross-solver evidence to be relabeled as context and influence conclusions without detecting the violation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
