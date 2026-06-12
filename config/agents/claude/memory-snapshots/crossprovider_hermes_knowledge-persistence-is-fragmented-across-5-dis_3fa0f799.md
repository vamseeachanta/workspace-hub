---
name: crossprovider hermes knowledge-persistence-is-fragmented-across-5-dis
description: Knowledge persistence is fragmented across 5+ disconnected stores
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [knowledge-management, architecture, data-consolidation]
---

Current knowledge architecture splits across: wrk-completions.jsonl (420 raw records), knowledge/seeds/*.yaml (5 structured files with different entry schema), dark-intelligence/ (gitignored YAML), resource-intelligence-maturity.yaml (5 documents, 0% maturity), and flat MEMORY.md. Each uses different query interface. Solution: consolidate via unified resource-intelligence-maturity v2.0.0 schema with `type: wrk` and `documents[]` array.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
