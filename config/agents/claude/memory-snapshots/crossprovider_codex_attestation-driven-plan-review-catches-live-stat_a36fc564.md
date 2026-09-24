---
name: crossprovider codex attestation-driven-plan-review-catches-live-stat
description: Attestation-driven plan review catches live-state mismatches
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, verification, ci-cd]
---

Using `attest-plan-claims.sh` to verify plan claims against live repo state (file existence via `ls -la`, issue states via `gh issue view`, commit SHAs) catches real divergences that text-only review misses. For example, it revealed `.gitignore` tracking gaps and file-existence claims that were stale or wrong.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
