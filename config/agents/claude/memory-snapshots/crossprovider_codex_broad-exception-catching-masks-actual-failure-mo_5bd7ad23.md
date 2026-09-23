---
name: crossprovider codex broad-exception-catching-masks-actual-failure-mo
description: Broad exception catching masks actual failure modes
metadata:
  type: reference
  source: codex
  bridged: 2026-07-20
  tags: [testing, pytest, exception-handling]
---

Using `pytest.raises(ValueError)` without asserting specific messages allows different failure causes to satisfy the same assertion. A case may fail through an unintended path and still pass. Parametrize into separate fixtures, assert exact exception messages, or split into independent assertions to verify the intended failure.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
