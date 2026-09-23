---
name: crossprovider codex negative-verification-required-for-release-artif
description: Negative verification required for release artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-07-19
  tags: [release-validation, artifact-cleanup, verification, negative-testing]
---

Release validation that only checks 'expected files exist' misses stale or leaked files in external storage (e.g., old Parquet/YAML files in Hugging Face after re-release). Explicitly verify artifact absence or use delete-patterns to reject any pre-existing files outside the allowlist; presence-only checks create silent false passes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
