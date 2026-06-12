---
name: crossprovider hermes waiver-suppression-expiry-must-be-enforced-in-co
description: Waiver/suppression expiry must be enforced in code, not just documented
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [safety, audit, suppression, expiry]
---

Documented expiry that isn't checked in code allows stale waivers to suppress findings indefinitely, creating a safety issue. If suppression system supports expiry, make it active: drop expired waivers from the active set before applying suppressions. Test that expired waivers no longer hide findings.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
