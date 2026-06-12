---
name: crossprovider codex yaml-placeholder-substitution-is-manual-not-auto
description: YAML ${PLACEHOLDER} substitution is manual, not automatic
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing, yaml-config, gotcha]
---

yaml.safe_load() does not resolve ${REPO_ROOT} or other placeholders. Tests expecting templated paths in YAML fixtures must implement explicit substitution code before passing config to engine(). Without substitution, placeholder strings are treated as literal paths and fail at runtime.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
