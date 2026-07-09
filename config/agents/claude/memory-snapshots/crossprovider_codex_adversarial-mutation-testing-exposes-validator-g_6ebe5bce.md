---
name: crossprovider codex adversarial-mutation-testing-exposes-validator-g
description: Adversarial mutation testing exposes validator gaps that happy-path tests miss
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [testing, validation, code-review]
---

Unit tests covering only valid fixtures overlook common failure modes: malformed nested structures (dict vs list), missing cross-field constraints, and field-type mismatches. Mutation probes (e.g., swapping pair IDs, deleting required nested keys, changing types) catch failures that occur in adversarial/malformed input paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
