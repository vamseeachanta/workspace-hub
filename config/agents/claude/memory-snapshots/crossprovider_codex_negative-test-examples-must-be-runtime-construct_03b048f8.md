---
name: crossprovider codex negative-test-examples-must-be-runtime-construct
description: Negative test examples must be runtime-constructed or use neutral fragments
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [testing, public-safety, negative-examples]
---

Committing hostile examples (real paths, source hashes, client IDs) to demonstrate what NOT to do will always fail public scan. Either assemble them at test time from neutral fragments, use synthetically-generated values, or keep negative examples in temp/runtime files outside the commit tree.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
