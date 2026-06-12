---
name: crossprovider hermes ci-test-invocation-gaps-break-repo-structure-val
description: CI test invocation gaps break repo-structure validation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [ci-cd, repo-structure, test-coverage]
---

aceengineer-website Phase 1 added new repo-structure contract tests but CI job does not execute them (pytest excluded by directory naming or config). Checker validation requires both pre-commit (local gate) AND CI (verification gate); missing CI wiring is correctness violation for multi-repo rollout.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
