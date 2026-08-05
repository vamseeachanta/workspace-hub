---
name: crossprovider codex bash-duplicate-function-definitions-second-wins-
description: Bash duplicate function definitions — second wins, causing silent empty-string failures
metadata:
  type: reference
  source: codex
  bridged: 2026-08-04
  tags: [bash, functions, definitions, silent-failures]
---

In bash, when a function is defined twice with different calling conventions (first uses stdout, second uses a global variable), the second definition overwrites the first. Callers capturing stdout get an empty string, not an error. This pattern silently defeats fail-safe gates and is flagged by shellcheck SC2034.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
