---
name: crossprovider codex test-fixture-contamination-in-parameterized-loop
description: Test fixture contamination in parameterized loops
metadata:
  type: reference
  source: codex
  bridged: 2026-07-20
  tags: [testing, test-isolation, fixtures]
---

When tests loop over multiple cases with a shared fixture or resource, earlier iterations can mutate state (e.g., fetch --unshallow, modify clone) that affects later iterations. Later cases then pass for the wrong reason instead of testing their intended path. Parametrize into independent fixtures or reset state between iterations to isolate each case.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
