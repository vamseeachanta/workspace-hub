---
name: crossprovider hermes pytest-testpaths-scope-pollution-across-director
description: pytest testpaths scope pollution across directories
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [pytest-config, tooling-quirk]
---

pytest.ini testpaths= is relative to pytest invocation directory, not file location. Running `pytest` from workspace-hub root with pytest.ini in digitalmodel/ collects from both spaces, mixing unrelated collection errors (work-queue, doc_intelligence, gis, pipeline tests pollute digitalmodel collection). Run from correct directory or use explicit --ignore.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
