---
name: crossprovider codex hardcoded-toolchain-versions-as-attestation-clai
description: Hardcoded toolchain versions as attestation claims: measure at runtime, record digests
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, toolchain, ci, attestation]
---

Fixture constants (OpenFOAM version = '11.0') become attestation claims in CI artifacts without verification. Query actual toolchain (dpkg-query, runtime executables) during the same run, fail on mismatch, preserve probe argv and output digests. Prevents silent toolchain drift between test assumptions and production behavior.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
