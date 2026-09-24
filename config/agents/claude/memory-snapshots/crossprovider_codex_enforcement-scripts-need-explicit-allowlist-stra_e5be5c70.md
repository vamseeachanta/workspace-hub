---
name: crossprovider codex enforcement-scripts-need-explicit-allowlist-stra
description: Enforcement scripts need explicit allowlist strategy for test violations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, enforcement, scanner-design]
---

When a test intentionally violates rules it's checking (negative fixtures), the enforcement script must have an explicit strategy: per-line sentinels (like `# legal-scan:skip`), path restrictions, or explicit exclusions. Without this, the test fixtures self-block the scan. Session 6 finding #3 showed negative fixtures for private-field names could trigger the public-surface scanner's own deny patterns.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
