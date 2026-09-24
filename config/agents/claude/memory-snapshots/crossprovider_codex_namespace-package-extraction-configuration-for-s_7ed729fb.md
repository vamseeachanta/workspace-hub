---
name: crossprovider codex namespace-package-extraction-configuration-for-s
description: Namespace package extraction configuration for setuptools
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [setuptools, namespace-packages, packaging]
---

Pattern for extracting a domain module into a new namespace member: `find where=["src"]`, `include=["worldenergydata.<domain>*"]`, `namespaces=true`, NO `__init__.py` in member root, explicit dependency on core member. Import paths remain unchanged (compatibility contract). Editable-install behavior differs from wheel; test both.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
