---
name: crossprovider codex test-local-validators-hide-real-defects
description: Test-local validators hide real defects
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tdd, testing, windows-compatibility]
---

Tests exercising reference implementations (not production modules) mask gaps in actual behavior: symlink resolution, Windows path normalization, filesystem-existence checks, drive/UNC spelling. Replace test-local validators with imports from production helpers to catch real defects.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
