---
name: crossprovider hermes stale-path-remediation-mapping-to-current-ecosys
description: Stale path remediation mapping to current ecosystem
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [migration, ecosystem, audit, stale-paths]
---

Top migration artifacts (scripts/work-queue/generate-html-review.py:249 reads, parse-session-logs.sh, etc.) map to current replacements in logs/orchestrator ecosystem: provider_session_ecosystem_audit.py, logs/orchestrator/<provider>/session_*.jsonl, and provider exporters (hermes-session-export.sh, codex-session-export.sh, gemini-session-export.sh). One known gap: generate-html-review.py is top stale path but not currently listed in legacy-claude-reference-map.md.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
