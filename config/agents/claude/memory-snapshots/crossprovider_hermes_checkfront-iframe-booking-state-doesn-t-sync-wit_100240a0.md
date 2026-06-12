---
name: crossprovider hermes checkfront-iframe-booking-state-doesn-t-sync-wit
description: Checkfront iframe booking state doesn't sync with programmatic date input
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [booking-automation, iframe-limitations, vendor-quirk]
---

Typing dates into Checkfront reservation form (embedded booking system) doesn't update page state; dates stay at defaults. Workaround: use direct property URLs or vendor API rather than iframe form-filling. Embedded booking engines resist automation to preserve user intent capture.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
