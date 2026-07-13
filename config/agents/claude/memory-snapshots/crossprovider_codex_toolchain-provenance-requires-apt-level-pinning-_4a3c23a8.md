---
name: crossprovider codex toolchain-provenance-requires-apt-level-pinning-
description: Toolchain provenance requires apt-level pinning beyond uv --frozen
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [reproducibility, dependencies, toolchain, provisioning]
---

Python dependency pinning via `uv --frozen` does not guarantee reproducible system-level toolchain (OpenFOAM, OpenMPI, compiler versions). Full reproducibility requires explicit versioning at the apt/system level, not just Python layer.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
