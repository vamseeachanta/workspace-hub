---
name: crossprovider codex dispatch-mock-canary-success-does-not-prove-end-
description: Dispatch mock-canary success does not prove end-to-end real solve
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [dispatch-testing, queue-validation, mock-vs-real]
---

Queue plumbing (mock:true dispatch) can succeed while real (mock:false) jobs fail due to data path issues, serialization contention, or solver input errors. A working mock pipeline is necessary but not sufficient; a real solve must complete end-to-end before claiming proof-of-dispatch.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
