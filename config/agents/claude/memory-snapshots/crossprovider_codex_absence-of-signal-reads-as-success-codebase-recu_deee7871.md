---
name: crossprovider codex absence-of-signal-reads-as-success-codebase-recu
description: Absence-of-signal reads as success (codebase recurring defect)
metadata:
  type: reference
  source: codex
  bridged: 2026-08-01
  tags: [observability, state-visibility, signal-absence]
---

When state is never written (dispatch:done label), absence is interpreted as "complete/never-attempted" instead of "incomplete." This pattern repeats (deckhand#580 unheard alarm, dispatch label gaps). Counter by checking inverted signals and TTL-based reversion to detect silent non-adoption.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
