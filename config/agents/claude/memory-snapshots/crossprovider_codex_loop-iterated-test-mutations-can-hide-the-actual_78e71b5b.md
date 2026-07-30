---
name: crossprovider codex loop-iterated-test-mutations-can-hide-the-actual
description: Loop-iterated test mutations can hide the actual rejection path
metadata:
  type: reference
  source: codex
  bridged: 2026-07-19
  tags: [test-quality, fixture-isolation, state-mutation]
---

Test loops that reuse mutable state (e.g., shallow clones) across iterations can produce false positives when later iterations run through different failure modes than intended. Use parametrization with fresh fixture scopes and assert exact terminal errors, not just exception type.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
