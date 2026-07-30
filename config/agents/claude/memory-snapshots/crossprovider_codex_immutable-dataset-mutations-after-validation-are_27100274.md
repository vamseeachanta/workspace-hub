---
name: crossprovider codex immutable-dataset-mutations-after-validation-are
description: Immutable dataset mutations after validation are unrecoverable
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [immutable-storage, transaction-boundaries, recovery-design]
---

Appending acceptance records to an immutable dataset (e.g., Hugging Face revision) after main-data cross-verification means those appends are unvalidated and cannot be corrected. If the append succeeds but bytes are corrupt, reverting requires a new immutable revision. Include all bytes (data + metadata) in a single validated immutable commit, or store acceptance records outside the immutable dataset with explicit ordering/atomicity rules.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
