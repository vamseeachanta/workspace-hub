---
name: crossprovider hermes package-data-replacement-silently-breaks-importl
description: Package-data replacement silently breaks importlib.resources consumers
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [packaging, wheel-build, importlib-resources, regression]
---

In pyproject.toml, replacing `package-data` patterns instead of extending them silently excludes previously bundled resources from wheels. Example: changing `digitalmodel = ["subsea/cross_sections/fixtures/*.yml"]` to `["naval_architecture/data/*.yml"]` broke existing code using `importlib.resources.files("digitalmodel.subsea.cross_sections")`. Always additive; audit all packaged resources comprehensively.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
