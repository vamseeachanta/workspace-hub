---
name: crossprovider gemini tdd-pairing-rate-as-readiness-metric-across-all-
description: TDD pairing rate as readiness metric across all repos
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [tdd, test-health, git-history, multi-repo, readiness-check]
---

Scan 7 days of git history across hub and all submodules to detect implementation commits without matching test files. Derive expected test basename per language (test_*.py for Python, *.test.ts for TypeScript, etc.). Calculate pairing rate = (impl files with matching test) / total impl files. Run best-effort (no failure blocks); emit JSONL per-repo and aggregate pairing stats.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
