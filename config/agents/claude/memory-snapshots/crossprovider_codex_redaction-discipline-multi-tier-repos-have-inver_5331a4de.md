---
name: crossprovider codex redaction-discipline-multi-tier-repos-have-inver
description: Redaction discipline: multi-tier repos have inverted label rules
metadata:
  type: reference
  source: codex
  bridged: 2026-07-31
  tags: [redaction, multi-tier-repos, privacy, label-discipline]
---

Public/promotable repos (deckhand, workspace-hub) use neutral tokens (ace-linux-1); private repos (aceengineer-admin) use physical hostnames, IPs, and account principals. Scan exceptions must be narrow (exact values, not patterns that might accidentally cover new hostnames). Never copy hostnames from private tier into public issues.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
