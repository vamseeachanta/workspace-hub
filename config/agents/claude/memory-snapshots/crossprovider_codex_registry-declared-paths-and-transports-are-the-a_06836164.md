---
name: crossprovider codex registry-declared-paths-and-transports-are-the-a
description: Registry-declared paths and transports are the authority for fleet probes
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [fleet-probe, registry, determinism]
---

Use only declared SSH transports and workspace/repo paths from registry; do not infer alternate addresses or search whole filesystems. Report exactly what succeeded/failed for declared paths and state limitations (undeclared paths not probed, features not tested beyond version check).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
