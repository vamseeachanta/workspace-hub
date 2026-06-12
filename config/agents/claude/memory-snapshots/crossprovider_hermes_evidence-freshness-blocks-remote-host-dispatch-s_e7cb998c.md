---
name: crossprovider hermes evidence-freshness-blocks-remote-host-dispatch-s
description: Evidence freshness blocks remote-host dispatch spoofing
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, readiness, security, dispatch, freshness-check]
---

Readiness evidence for remote hosts requires collected_at timestamps, hostname binding, and freshness thresholds. Without them, any JSON file in evidence_dir can mark a host as dispatch-ready. scripts/readiness/telegram_hermes_readiness.py::_load_host_local_evidence and _apply_host_local_evidence need freshness enforcement; tests must cover stale/spoofed cases.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
