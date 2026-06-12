---
name: crossprovider hermes url-safety-checks-must-decode-and-scan-all-url-c
description: URL safety checks must decode and scan all URL components
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [security, url-validation, public-safety]
---

External URL safety validators that check only the decoded path miss private paths hidden in query/fragment parameters. `https://example.com/?p=%2Fhome%2Fvamsee%2F.secret` bypasses path-only checks. Fix: scan decoded path, query params, and fragment separately; reject on match in any component.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
