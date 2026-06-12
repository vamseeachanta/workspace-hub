---
name: crossprovider hermes canonical-test-commands-per-repo-are-load-bearin
description: Canonical test commands per repo are load-bearing; wrong flags mask failures
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, ci-cd, canonical-patterns]
---

Each tier-1 repo requires specific `uv run` incantation (PYTHONPATH, --noconftest flags vary). Using wrong command produces silent pass where error should surface, creating false-confidence test coverage.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
