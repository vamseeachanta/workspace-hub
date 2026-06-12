---
name: crossprovider hermes auto-host-selection-contradicts-final-dispatch-g
description: Auto-host selection contradicts final dispatch gate
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [dispatch-routing, host-selection, policy-logic, workspace-hub-2720]
---

`_select_host()` accepts hosts with `status in {"pass", "warn"}` but `evaluate_dispatch_request()` rejects anything not exactly `pass`. When first auto-eligible host is warn and a later host is pass, auto-select picks warn first, then rejects the entire dispatch request instead of continuing to the pass host.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
