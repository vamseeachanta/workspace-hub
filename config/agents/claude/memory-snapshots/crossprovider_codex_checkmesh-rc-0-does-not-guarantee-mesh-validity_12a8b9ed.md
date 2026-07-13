---
name: crossprovider codex checkmesh-rc-0-does-not-guarantee-mesh-validity
description: checkMesh rc=0 does not guarantee mesh validity
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [openfoam, mesh-validation]
---

Zero exit code is insufficient; must also check for fatal markers and non-zero 'Failed N mesh checks' in output. rc=0 with semantic failure is a false positive that blocks detection.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
