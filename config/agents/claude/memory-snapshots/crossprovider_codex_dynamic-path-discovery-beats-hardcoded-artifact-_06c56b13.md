---
name: crossprovider codex dynamic-path-discovery-beats-hardcoded-artifact-
description: Dynamic path discovery beats hardcoded artifact specs in plans
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, schema-specifications, artifact-drift, ci-correctness]
---

Plans that enumerate public-surface files, review artifacts, or CI test paths drift from live tracked inventory. Prefer schemes where specs derive from validator logic (e.g., `public_scan_paths()`) or use locked manifests; hand-enumerated lists accumulate drift across commits. Codex sessions repeatedly found that workflow hardcodes (`*.md` globs, `*-r1.md` subsets) mismatch the validator's dynamic expansion, causing incomplete CI coverage or stale test assertions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
