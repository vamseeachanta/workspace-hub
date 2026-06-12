---
name: crossprovider hermes hard-orcfxapi-imports-block-unlicensed-machines
description: Hard OrcFxAPI imports block unlicensed machines
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [architecture, licensing, import-blocking]
---

OrcaWaveConverter (solver/orcawave_converter.py) imports OrcFxAPI at module level, causing ImportError on dev-primary without license. Use conditional imports or extract data from .xlsx sidecars instead of runtime OrcFxAPI access.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
