---
name: crossprovider codex ascp-claim-guards-insufficient-against-verify-ba
description: ASCP claim guards insufficient against verify-batch fail-open
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [llm-wiki, race-condition, verify-batch]
---

`start_verify_batch.sh` line 48 proceeds even when ASCP preflight claims fail. Plans relying on overlapping claim keys to serialize queue writes will not prevent out-of-order batch starts if claims are not honored; final prewrite guards (branch/PR recheck, hardlock) needed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
