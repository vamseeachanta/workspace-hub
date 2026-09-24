---
name: crossprovider codex pytest-slow-collection-with-broken-plugin-metada
description: Pytest slow collection with broken plugin metadata
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pytest, environment, filesystem, performance]
---

When pytest initialization is extremely slow (~9+ minutes) on a networked filesystem, check for broken third-party plugin metadata (e.g., `vtk`, `numba`). Disable plugin autoload with pytest flags (e.g., `-p no:cacheprovider`) or the Python environment's site-packages. This resolves FUSE/NFS contention where plugin metadata loading blocks collection before any tests run.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
