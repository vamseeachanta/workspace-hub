---
name: crossprovider codex threat-modeling-must-cover-domain-specific-hazar
description: Threat modeling must cover domain-specific hazards: paths, hooks, logs
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, threat-model, code-review, plan-review]
---

Generic threat sections (API failures, input validation) miss critical domain hazards: path traversal/symlinks for file-scanning tools, commit-trailer spoofing/injection for log-writing hooks, concurrent-writer and mount-substitution risks for shared-mount writes, oversized payload DoS for YAML/frontmatter parsing. Expand threat models to include these classes explicitly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
