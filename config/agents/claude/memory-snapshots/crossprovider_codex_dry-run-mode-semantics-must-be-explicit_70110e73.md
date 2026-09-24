---
name: crossprovider codex dry-run-mode-semantics-must-be-explicit
description: Dry-run mode semantics must be explicit
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [design, testing, specification, cli-contracts]
---

Dry-run flags can be either state-reporting-only (always exit 0) or compliance-checking (exit non-zero on violations). These modes have incompatible test expectations, implementation paths, and exit code contracts. Plans must unambiguously declare which mode applies; ambiguity creates contradictions between pseudocode and acceptance criteria.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
