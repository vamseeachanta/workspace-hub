---
name: crossprovider hermes execution-pre-check-scope-mismatch-causes-tdd-te
description: Execution pre-check scope mismatch causes TDD test failure cascade
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [tdd, pre-checks, acceptance-criteria]
---

For TDD-first tasks with acceptance criteria including artifact counts/metrics, the pre-check command scope (e.g., flake8 target directory) must match acceptance criteria exactly. Scope drift (checking 'src/subdir' instead of 'src/') causes artifact-count mismatches and wastes TDD iterations.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
