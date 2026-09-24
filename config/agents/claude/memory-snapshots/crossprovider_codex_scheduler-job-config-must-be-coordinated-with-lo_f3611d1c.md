---
name: crossprovider codex scheduler-job-config-must-be-coordinated-with-lo
description: Scheduler job config must be coordinated with loader API changes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [scheduler, coordination, config-propagation]
---

When adding parameters to a data loader (e.g., density_registry_path), the scheduler job that instantiates it must explicitly pass those config keys via the job's config mapping. This is a coordination hazard easily missed when focused on the loader interface alone.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
