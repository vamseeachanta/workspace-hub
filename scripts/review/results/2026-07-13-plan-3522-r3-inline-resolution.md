# Issue 3522 r3 inline resolution

Per the cross-provider routing rule, r1 and r2 exposed different defect classes;
the main session applied r3 inline and did not dispatch another review cycle.

| R2 defect | Normative resolution |
|---|---|
| Current/pending cutover | Dual envelopes; exact-head PENDING; owner CAS promotion/readback/rollback. |
| Immutable workflow | SHA-pinned reusable workflow owns Environment; mutable caller receives no secret. |
| Fork oracle/check | Fork constant-fails and never merges; owner privately cleans into independent same-repo PR. |
| Ledger/reuse | Canonical HMAC ledger, approved genesis, tip+1, fresh UUID, atomic append, cross-signed rotation. |
| Alternate secret artifacts | Scan pattern base64, component hashes/MACs/fields, ledger/report markers, Git pack magic; residual encodings explicit. |
| COMPLETE integrity | HMAC manifest binds authority/snapshots/coverage and every file; extra/mutation rejects. |
| Git filesystem | 0700 dirs; no group/other bits; 0400/0600 Git files; Linux stable dirfd fetch; no persisted remote. |
| GitHub bytes | Every accessible body/download is scanned with safe bounded decompression and drift checks. |
| Anchor codec | Closed canonical anchor/ledger schemas, caps, duplicate rejection, vectors. |
| CLI | Exact validate/seal/verify/audit/cleanup/promote signatures and rc table frozen. |
| Secret limit | CI map/envelope capped below 48 KiB; no truncation/fallback. |
| Mixed verdict | rc4>rc3>rc1>rc0; clean requires COMPLETE coverage. |
| Protection readback | Exact environment, CODEOWNERS surfaces, ruleset name/ref/check/no-bypass JSON in owner preview. |
| Git metadata/classes | Raw commit/tag/ref bytes, reverse edges, reports/ledger/mirror structural cases covered. |

The revised plan advances only to `plan-review`. User approval authorizes Phase A
bootstrap only; Phase B, secret provisioning, ruleset/environment mutation,
deletion-diff exposure, CAS, rewrite, force-push, and provider actions remain
separately previewed and owner-approved.
