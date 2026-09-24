---
name: crossprovider codex ckan-endpoint-heterogeneity-creates-silent-failu
description: CKAN endpoint heterogeneity creates silent failures
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ckan, api, silent-failure, discovery]
---

Public CKAN instances grant access to `package_show` but restrict `resource_show`, `datastore_search`, and related endpoints with 403 responses. Don't assume all CKAN methods work if some do; verify each endpoint independently before designing automated workflows.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
