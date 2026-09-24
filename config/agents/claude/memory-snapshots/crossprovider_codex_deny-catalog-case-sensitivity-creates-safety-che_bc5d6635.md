---
name: crossprovider codex deny-catalog-case-sensitivity-creates-safety-che
description: Deny-catalog case-sensitivity creates safety-check bypasses
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [safety-checks, case-sensitivity, deny-catalog, code-review]
---

When safety-checking normalized (lowercased) output text, catalog items must also be normalized, or mixed-case patterns like C:\ and /Volumes/ become ineffective. Verified directly: `C:\client\source.pdf` bypasses while `c:\client\source.pdf` is blocked. Applies to any safety guard using normalized text comparison.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
