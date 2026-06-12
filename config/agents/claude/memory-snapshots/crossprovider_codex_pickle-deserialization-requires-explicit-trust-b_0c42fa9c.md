---
name: crossprovider codex pickle-deserialization-requires-explicit-trust-b
description: Pickle deserialization requires explicit trust boundary documentation
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [security, pickle, trust-boundary]
---

Sessions 13 and 18 flagged `nosec B301` comments on pickle.load() operations; user-controllable pickle paths (e.g., via CLI --sample-bin) weaken trust assumptions. Document explicit trust boundaries or validate/sign pickle artifacts before deserialization.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
