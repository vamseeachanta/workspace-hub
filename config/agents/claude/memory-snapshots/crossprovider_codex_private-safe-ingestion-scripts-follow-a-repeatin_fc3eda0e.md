---
name: crossprovider codex private-safe-ingestion-scripts-follow-a-repeatin
description: Private-safe ingestion scripts follow a repeating pattern
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [llm-wiki, ingest-patterns, private-safe, schema-enforcement]
---

JSONL rows use sorted keys and allowlists, JSON/HTML reports are deterministic with `indent=2, sort_keys=True`. No raw bodies, identifiers, filenames, or paths in outputs. Required: enum validation, dependency fail-closed gates, monkeypatch tests for source-body reads. See #729/#730/#733/#734 implementations in `scripts/ingest/` for the canonical forms.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
