---
name: crossprovider gemini config-files-define-but-are-not-consumed-design-
description: Config files define but are not consumed: design mismatch signal
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [configuration, design-mismatch, automation]
---

Per-repo config files (e.g. worldenergydata.conf defining ADDOPTS_OVERRIDE, TEST_DIR_PATTERNS) are ignored by consuming scripts (invoke-pytest.sh, map-tests.sh), which hardcode the logic instead. This negates configurability. Always verify consuming scripts read defined values. (WRK-119 review finding, MAJOR severity)

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
