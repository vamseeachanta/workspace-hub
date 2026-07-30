---
name: crossprovider codex scheduler-config-passes-new-yaml-keys-directly-t
description: Scheduler config passes new YAML keys directly to job without schema validation
metadata:
  type: reference
  source: codex
  bridged: 2026-07-06
  tags: [scheduler, config, architecture, integration]
---

The scheduler accepts arbitrary YAML keys under job config (e.g., `oil_density_registry_path`, `allow_default_density`) and passes them through to the job constructor; this allows config-only integration before job logic is updated, without requiring central schema validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
