---
name: crossprovider codex manifest-builders-write-output-before-repo-safet
description: Manifest builders write output before repo-safety check (fail-open)
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [llm-wiki, manifest-builders, fail-open, repo-safety, output-validation]
---

Multiple manifest scripts write JSON/JSONL/HTML outputs, then call `_assert_repo_safe()` afterward, leaving unsafe content on disk if the check fails. Codex found this pattern in specialty_international_source_manifest.py and related builders. Move the safety gate to run FIRST, before opening any output file.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
