---
name: crossprovider codex keep-marker-exempts-only-dedup-trim-rules-not-do
description: `# keep` marker exempts only dedup+trim rules, not done-WRK/path-staleness
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [memory-compaction, bullet-lifecycle]
---

`# keep` in memory bullets skips rules 4–5 (semantic dedup, trim-to-limit) but still triggers rules 1–2 (done-WRK expiry, path staleness). Allows preserving high-signal bullets while still cleaning truly obsolete references.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
