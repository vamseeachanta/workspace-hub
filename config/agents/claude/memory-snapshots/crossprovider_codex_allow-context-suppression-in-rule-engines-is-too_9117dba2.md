---
name: crossprovider codex allow-context-suppression-in-rule-engines-is-too
description: Allow-context suppression in rule engines is too coarse-grained
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [validation-design, security, rule-engines]
---

When implementing rule exemptions via allow-blocks, suppressing by rule-ID suppresses the entire line, not individual matched values. A block containing `source_id: vendor_doc_001` can hide a private-source-key assignment because the rule class is blanket-suppressed. Exemptions need value-level or pattern-level scoping, not category-level.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
