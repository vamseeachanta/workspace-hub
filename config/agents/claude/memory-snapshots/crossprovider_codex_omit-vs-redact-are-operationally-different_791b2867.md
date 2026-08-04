---
name: crossprovider codex omit-vs-redact-are-operationally-different
description: Omit vs. redact are operationally different
metadata:
  type: reference
  source: codex
  bridged: 2026-08-02
  tags: [privacy, dispatch, design-pattern]
---

For tracked files carrying sensitive data, omission (absence of field) signals policy; blanking or redaction (empty string or `<redacted>`) signals breakage/outage. A redacted queue is indistinguishable from a broken one. Use explicit policy declaration (e.g., `title_policy: omitted_at_serialization`) to distinguish deliberate omission from failure.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
