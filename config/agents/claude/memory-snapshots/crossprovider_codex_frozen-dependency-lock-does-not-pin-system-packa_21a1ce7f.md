---
name: crossprovider codex frozen-dependency-lock-does-not-pin-system-packa
description: Frozen dependency lock does not pin system packages
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [provenance, dependencies, openfoam]
---

uv --frozen pins Python dependencies but not apt packages (OpenFOAM, OpenMPI). Toolchain provenance requires pinning at both language-package and system-package levels.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
