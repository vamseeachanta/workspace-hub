---
name: crossprovider hermes pylife-dependency-optional-for-fatigue-submodule
description: pylife dependency optional for fatigue submodules
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [dependency-management, python-imports]
---

fatigue/sn_curves.py requires pylife (WoehlerCurve), but sn_library.py (221 curves) doesn't. Separate imports allow sn_library to work standalone; sn_curves import in __init__.py breaks module-level import until pylife is installed. Direct module imports bypass __init__ dependency order.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
