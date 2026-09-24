---
name: crossprovider codex codex-global-config-precedence-and-unconditional
description: Codex global config precedence and unconditional-policy pattern
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [codex, configuration, tooling, shell]
---

Codex precedence chain: CLI flags > project config > profile > user global config. For org-wide policies that project configs cannot override, use shell wrappers (`command codex --yolo "$@"`) at the entry point, since project configs shadow user settings and static global config alone cannot enforce policy across all repos.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
