---
name: crossprovider hermes package-wheel-testing-can-use-independent-build-
description: Package/wheel testing can use independent build verification when import environment is fragile
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [packaging, testing, workaround]
---

Direct pytest imports may fail due to missing editable dependencies (#2564 case: `/mnt/local-analysis/assetutilities` absent). Build wheel independently and inspect package contents with `zipfile` to verify package-data inclusion without relying on import success.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
