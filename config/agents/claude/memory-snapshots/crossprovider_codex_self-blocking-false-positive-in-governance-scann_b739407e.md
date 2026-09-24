---
name: crossprovider codex self-blocking-false-positive-in-governance-scann
description: Self-blocking false positive in governance scanners
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [governance-logic, scanner-design, edge-cases]
---

If a governance doc contains a keyword that the validator treats as a violation, the doc blocks itself. Example: policy prose about stripping GPS metadata triggers GPS-keyword deny rule. Threat-model validator keywords; add doc-scoped exemptions or rephrase policy with synonyms.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
