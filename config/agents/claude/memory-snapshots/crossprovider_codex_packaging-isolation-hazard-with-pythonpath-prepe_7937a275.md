---
name: crossprovider codex packaging-isolation-hazard-with-pythonpath-prepe
description: Packaging isolation hazard with PYTHONPATH prepending
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [python-packaging, testing, false-positives]
---

Wheel smoke tests that prepend the host interpreter's site-packages to PYTHONPATH can satisfy imports from host-installed split modules, producing false-positive package completeness checks. Packaging isolation must not include host site-packages; use strict, clean environments or skip the prepend entirely.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
