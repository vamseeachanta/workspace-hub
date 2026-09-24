---
name: crossprovider codex upstream-project-metadata-must-be-verified-at-im
description: Upstream project metadata must be verified at implementation time
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [upstream-verification, metadata-drift, implementation-timing]
---

GitHub orgs redirect (NREL/MoorPy → NatLabRockies/MoorPy), licenses change (Apache → BSD-3-Clause between plan and live upstream). Do not trust plan metadata; verify licenses, maintainers, and repo URLs directly from live upstream before implementation begins.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
