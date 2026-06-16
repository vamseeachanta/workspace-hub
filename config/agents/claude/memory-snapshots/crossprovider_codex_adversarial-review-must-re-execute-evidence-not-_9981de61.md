---
name: crossprovider codex adversarial-review-must-re-execute-evidence-not-
description: Adversarial review must re-execute evidence, not trust PR body citations
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [review-methodology, evidence-verification, pr-trust-hazard, independent-validation]
---

PR bodies citing script runs (legal scans, tests, document checks) should be independently re-executed to verify evidence is meaningful, not vacuous or stale. llm-wiki #682: cited `--diff-only` legal scan was vacuous on a clean branch; full re-run showed baseline violations. Integrate evidence re-execution into review workflow.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
