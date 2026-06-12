---
name: crossprovider hermes plan-revision-summaries-overclaim-fixes-not-pres
description: Plan revision summaries overclaim fixes not present in artifact
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [plans, documentation, verification]
---

MAJOR finding pattern: revision notes asserting "fixed X" but the file still contains the defect. Indicates author/artifact state mismatch. Adversarial review must check revision prose against actual diff; never trust prose alone. Update revision notes during patching, not before.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
