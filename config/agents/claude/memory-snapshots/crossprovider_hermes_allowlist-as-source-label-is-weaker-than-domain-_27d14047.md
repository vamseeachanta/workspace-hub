---
name: crossprovider hermes allowlist-as-source-label-is-weaker-than-domain-
description: Allowlist as source-label is weaker than domain-allowlist
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [security, allowlisting, request-control]
---

GTM scanner's 'allowlist' validates source labels (career_page, google) but not actual URL domains. Any caller can pass source='career_page' for an arbitrary domain and bypass the intended control. True request compliance needs per-host/domain validation, not just label checking.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
