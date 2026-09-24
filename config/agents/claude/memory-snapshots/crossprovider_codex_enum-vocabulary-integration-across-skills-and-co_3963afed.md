---
name: crossprovider codex enum-vocabulary-integration-across-skills-and-co
description: Enum/vocabulary integration across skills and contracts requires fail-closed validation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [vocabulary-integration, enum-safety, schema-alignment]
---

A parse-status enum defined in skills/, docs, examples, and schema had divergent values. New issues consuming those enums create a silent risk of choosing a new vocabulary. Create tests that validate enum alignment across all surfaces and fail if definitions diverge.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
