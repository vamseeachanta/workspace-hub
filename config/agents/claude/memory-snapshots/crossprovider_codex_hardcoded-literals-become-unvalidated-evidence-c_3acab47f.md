---
name: crossprovider codex hardcoded-literals-become-unvalidated-evidence-c
description: Hardcoded literals become unvalidated evidence claims
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [evidence, provenance, execution-fidelity, reproducibility]
---

Toolchain versions hardcoded at implementation time (e.g., OpenFOAM, OpenMPI via `dpkg` queries or literals) later become evidence artifacts without reflection of actual runtime execution. Query executables during same process, fail on mismatch, and preserve argv/output digests; do not use prior-run values as claims for new runs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
