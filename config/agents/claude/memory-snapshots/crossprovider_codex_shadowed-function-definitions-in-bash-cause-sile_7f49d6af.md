---
name: crossprovider codex shadowed-function-definitions-in-bash-cause-sile
description: Shadowed function definitions in bash cause silent calling-convention failures
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash, shadowed-definitions, calling-conventions, shellcheck]
---

When bash redefinition of a function occurs, the second definition silently wins without warning. If the two definitions use different return conventions (stdout vs global variable), call sites capture the wrong value. Shellcheck flags this as SC2034 (unused variable). This pattern has caused two separate scanning defects where queries returned empty results but reported success.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
