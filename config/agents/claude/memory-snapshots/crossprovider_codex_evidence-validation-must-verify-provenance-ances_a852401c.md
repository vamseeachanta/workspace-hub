---
name: crossprovider codex evidence-validation-must-verify-provenance-ances
description: Evidence validation must verify provenance (ancestry, tree identity, package locks), not just format
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [testing, CI, validation]
---

Committed evidence (hashes, digests) are untrusted until they verify source ancestry, exact tree identity via git objects, and resolved package versions against uv.lock. Format-only validators accept fake values; add committed-artifact mode with ancestry/digest checks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
