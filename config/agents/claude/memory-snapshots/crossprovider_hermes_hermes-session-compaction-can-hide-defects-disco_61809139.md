---
name: crossprovider hermes hermes-session-compaction-can-hide-defects-disco
description: Hermes session compaction can hide defects discovered in later turns
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [session-management, cross-session-consistency]
---

Multiple sessions showed 'context compaction' summaries claiming work was 'complete and closed' (e.g., #2508), but subsequent parallel sessions or adversarial reviews uncovered MAJOR blockers. Auto-summary can mask transitive dependencies and defects across session boundaries. Always cross-reference live issue state + review artifacts, not just session summaries.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
