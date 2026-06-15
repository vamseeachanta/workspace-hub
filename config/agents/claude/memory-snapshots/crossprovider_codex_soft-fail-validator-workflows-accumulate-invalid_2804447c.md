---
name: crossprovider codex soft-fail-validator-workflows-accumulate-invalid
description: Soft-fail validator workflows accumulate invalid configuration state undetected
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [validation, tooling, ci-discipline]
---

Validators using grep/regex instead of real parsers (e.g., shell checks for YAML instead of PyYAML) miss syntax errors. Soft-fail CI workflows (`continue-on-error: true`) then allow invalid files to accumulate in the repo while the validator appears to run. Requires real parsers and hard CI failure to prevent silent accumulation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
