---
name: crossprovider hermes arbitrary-token-fragments-in-remote-evidence-lea
description: Arbitrary token fragments in remote evidence leak through contextual regex
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [redaction, remote-evidence, untrusted-input]
---

Remote evidence redaction uses narrow contextual regex (e.g., `token tail|fragment ...`) that misses bare token fragments. Freeform failure/warning/missing_data strings from untrusted remote evidence can leak `ZYXWV` or similar private values. Add `fragment <alnum>` pattern or redact entire failure/warning/missing_data lists from remote hosts.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
