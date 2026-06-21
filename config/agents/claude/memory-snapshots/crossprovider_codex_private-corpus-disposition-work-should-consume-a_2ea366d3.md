---
name: crossprovider codex private-corpus-disposition-work-should-consume-a
description: Private-corpus disposition work should consume artifacts, not re-traverse sources
metadata:
  type: reference
  source: codex
  bridged: 2026-06-20
  tags: [llm-wiki, private-corpus, safety-pattern]
---

For disposition/routing lanes (e.g., O&G standards #719), implementation should consume existing tracked routing/disposition artifacts rather than re-traverse the corpus. This keeps private paths out of reports and avoids duplicating filtered data. Use small deterministic artifact builders, not corpus walkers; emit repo-safe JSON/JSONL only.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
