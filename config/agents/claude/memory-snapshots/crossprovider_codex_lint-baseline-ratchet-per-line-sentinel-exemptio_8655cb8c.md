---
name: crossprovider codex lint-baseline-ratchet-per-line-sentinel-exemptio
description: Lint baseline ratchet + per-line sentinel exemption pattern
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [enforcement, baseline-ratchet, linting]
---

Use persistent baseline files for known violations instead of blanket per-file exempts (which are backdoors). Exempt specific lines with inline `# sentinel-comment-allowed` for transport/test/historical exceptions. Regex matches lines; baseline exempts by exact content; sentinels override baseline. Prevents scope creep.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
