---
name: crossprovider codex domain-divided-ci-via-domains-md-table-and-touch
description: Domain-divided CI via DOMAINS.md table and touched-domain matrix detection
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ci, testing, github-actions]
---

Replace single maxfail-masked test gate with per-domain gates. Create `tests/DOMAINS.md` (domain → test-roots table). Script parses table, outputs GitHub Actions matrix (full or touched modes). Each domain runs separate pytest (no `--maxfail`); aggregator depends on all required domains. Full-matrix triggers: `src/**`, CI config changes, the script itself. Exposes true failure counts instead of masking.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
