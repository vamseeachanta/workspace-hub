---
name: crossprovider codex mesh-sentinel-padding-requires-explicit-filterin
description: Mesh sentinel padding requires explicit filtering
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [implementation, data-structures, mesh-handling]
---

Panel/mesh data structures using `-1` sentinels for quad-padding need explicit filtering when computing statistics (max panel length, wavelength checks, etc.). Pseudocode using raw `vertices[-1]` or unfiltered panel counts produces false findings. This detail is easy to miss.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
