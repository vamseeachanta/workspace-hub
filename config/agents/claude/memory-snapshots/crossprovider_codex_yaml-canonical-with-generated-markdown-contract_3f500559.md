---
name: crossprovider codex yaml-canonical-with-generated-markdown-contract
description: YAML-canonical with generated Markdown contract
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-architecture, consistency, multi-workstation]
---

Keep YAML ledgers as single source of truth and generate Markdown views from them. Enforce drift detection via automated checks (e.g., sync-maturity-summary.py --check) to prevent multi-workstation divergence. Use repo-relative links in Markdown to avoid churn.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
