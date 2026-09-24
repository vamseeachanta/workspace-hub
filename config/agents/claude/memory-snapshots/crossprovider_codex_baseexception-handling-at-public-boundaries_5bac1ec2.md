---
name: crossprovider codex baseexception-handling-at-public-boundaries
description: BaseException handling at public boundaries
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [exception-handling, security, api-boundaries]
---

Public API boundaries must catch all BaseException subclasses (KeyboardInterrupt, SystemExit, raw OSError), not just expected types. Construct bounded, fixed error text; never expose raw exception strings which may be unbounded or sensitive.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
