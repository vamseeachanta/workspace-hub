---
name: crossprovider codex dead-configuration-pattern-files-to-change-must-
description: Dead configuration pattern: Files to Change must not introduce unused config
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [dead-code, config-drift, pseudocode-alignment]
---

Plans must not list config files in 'Files to Change' unless pseudocode explicitly loads and uses them. Dead config that never runs through implementation-path code will drift immediately and either be skipped or become a latent defect if later activated. Verify pseudocode consumes every config file.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
