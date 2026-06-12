---
name: crossprovider hermes remote-host-readiness-evidence-lacks-provenance-
description: Remote host readiness evidence lacks provenance verification, is trivially forgeable
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, telegram-dispatch, readiness, security, remote-dispatch]
---

Host-local readiness evidence ingestion verifies only `host_id`, `hostname`, and `generated_at` freshness, then trusts a handcrafted JSON blob as proof of clean git state and valid env gates. Accepts minimal evidence with `status=pass`, `dirty=false`, `ahead=0`, `behind=0`, `missing_data=[]` without confirming evidence actually came from host-local evaluation of env gates (missing token, missing allowlist, GATEWAY_ALLOW_ALL_USERS, etc.); fail-closed for remote dispatch depends on evidence file existence, not gate validation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
