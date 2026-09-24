---
name: crossprovider codex removing-published-extras-creates-silent-depende
description: Removing published extras creates silent dependency loss for external consumers
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [release-safety, package-api, semver]
---

Deleting a pyproject.toml [extra] causes external consumers using pkg[extra-name] to receive a warning but no error, silently installing without the intended sub-dependencies. This affects any external deployment manifests or lock files expecting that extra.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
