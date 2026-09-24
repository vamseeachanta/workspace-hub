---
name: crossprovider gemini integration-test-coverage-across-all-target-repo
description: Integration test coverage across all target repositories
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [testing, multi-repo, integration-tests]
---

When a plan affects multiple repositories (e.g., 5 tier-1 repos), integration tests should run on all of them, not just the smallest. Testing a single repo misses repo-specific edge cases and false-negatives.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
