---
name: crossprovider codex fixture-values-must-carry-source-citations-to-re
description: Fixture values must carry source citations to remain valid
metadata:
  type: reference
  source: codex
  bridged: 2026-08-23
  tags: [testing, fixtures, validation]
---

Test fixture values without documented sources (a citation to spec, reference implementation, or paper) decay into un-validated test vectors that stop catching regressions. Always pair fixture data with its provenance; undocumented fixtures should be treated as suspect and risky to trust.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
