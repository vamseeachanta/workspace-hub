---
name: crossprovider codex enforcement-script-sentinels-over-blanket-exempt
description: Enforcement script sentinels over blanket exempts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [enforcement, automation, security]
---

When designing path/pattern enforcement checks, use per-line sentinels (e.g., `# abs-path-allowed`) rather than blanket file exempts. Sentinels preserve forensic auditability and prevent exemption backdoors; they also fail safely when the sentinel is removed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
