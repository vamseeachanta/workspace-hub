---
name: crossprovider codex report-renderer-safety-mandatory-placeholders-cd
description: Report renderer safety: mandatory placeholders, CDN pinning, escaping, snapshots
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [reporting, security, testing]
---

HTML report rendering requires mandatory-section placeholders to enforce completeness, pinned/inline asset modes (no loose CDN), XSS escaping on assumptions/sources, injection tests, and structural snapshots to catch rendering regressions across solver versions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
