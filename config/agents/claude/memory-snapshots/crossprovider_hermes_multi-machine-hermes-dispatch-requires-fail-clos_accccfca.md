---
name: crossprovider hermes multi-machine-hermes-dispatch-requires-fail-clos
description: Multi-machine Hermes dispatch requires fail-closed validation gates
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, dispatch, multi-machine, fail-closed]
---

Registry metadata (dispatch_enabled, telegram_mode, hermes_profile, sync_policy, data_access_profile) gates dispatch eligibility; reachability, GitHub-auth, and per-machine readiness checks are blocking dependencies. Telegram is command/notification plane only; canonical sync remains in git/GitHub/repo-backed Hermes config and explicit job/host routing records.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
