---
name: crossprovider codex importlib-util-spec-from-file-location-for-sibli
description: Importlib.util.spec_from_file_location for sibling module loading
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [importlib, python-modules, dynamic-imports, sibling-loading]
---

When scripts load sibling modules and sys.path may not include the script directory, use `importlib.util.spec_from_file_location(name, Path(__file__).with_name('sibling.py'))` + `module_from_spec()` + `exec_module()` instead of direct `import`. Solves hazard where scripts loaded as modules (not __main__) fail to resolve siblings because parent package isn't on sys.path.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
