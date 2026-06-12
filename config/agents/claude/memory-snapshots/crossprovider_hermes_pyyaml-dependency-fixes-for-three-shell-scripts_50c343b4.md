---
name: crossprovider hermes pyyaml-dependency-fixes-for-three-shell-scripts
description: PyYAML dependency fixes for three shell scripts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [uv, python, dependencies, yaml]
---

batch-unsubscribe.sh, build-knowledge-index.sh, and query-knowledge.sh import yaml but invoke `uv run` without `--with pyyaml`. Safe fix: add `--with pyyaml` to existing uv invocations. Other 5 scripts (skill-evals.sh, code-version-guard.sh, migrate-memory-to-knowledge.sh, run-skill-integration-tests.sh, new-machine-setup.sh) are safe as-is—either stdlib-only or intentionally bootstrap-safe with fallback parsers.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
