---
name: crossprovider codex registry-schemas-for-multi-backend-systems-need-
description: Registry schemas for multi-backend systems need operation-level targets, not path-level
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-design, multi-backend, ownership-model, registry, completeness]
---

Path-level registries cannot represent systems with dual ownership branches (e.g., crontab vs systemd-user vs Windows Task Scheduler). Schema must support operation-level targets that distinguish destructive classification per backend and enumerate a closed evaluator set to prevent incomplete ownership discovery.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
