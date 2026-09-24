---
name: crossprovider codex tdd-matrix-must-cover-operational-acceptance-cri
description: TDD matrix must cover operational acceptance criteria (cron, hooks, logging, artifact posting)
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tdd-coverage, acceptance-criteria, operational-testing]
---

Plans frequently include acceptance criteria for cron scheduling, hook installation, log/audit persistence, or review-artifact posting but omit corresponding tests in the TDD list. Reviewers flag these as incomplete coverage; expand the test matrix to include every acceptance criterion or document why manual verification suffices.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
