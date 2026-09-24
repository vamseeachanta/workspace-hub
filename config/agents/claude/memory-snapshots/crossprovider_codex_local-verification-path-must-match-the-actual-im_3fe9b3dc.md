---
name: crossprovider codex local-verification-path-must-match-the-actual-im
description: Local verification path must match the actual implementation changes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [reproducibility, local-testing, implementation-parity]
---

If the fix adds a dependency only to the GitHub Actions workflow (e.g., 'types-PyYAML added in workflow install step'), local pre-edit TDD verification cannot pass with only the workflow change. The dependency must also be added to local pyproject.toml/environment, or the acceptance path is not reproducible.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
