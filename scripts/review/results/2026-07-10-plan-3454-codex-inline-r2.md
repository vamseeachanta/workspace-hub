# Codex inline r2 — issue #3454 plan

**Reviewed commit:** `baca4d25a8049b91dccd2c79af99550bf96ae4f1`
**Verdict:** MAJOR

Three parallel defect reviews agreed that v2 was not approval-ready. Blocking classes were:

1. D1 was prose-only and absent from the authority schema/editor gate.
2. Digest domains and transaction transition rules were underspecified.
3. The attestation was written before the results it claimed to record.
4. PII/legal/Pages checks read ambient working files rather than immutable staged blobs.
5. The same-mount test had no required target-mount synthetic root.
6. Regression suites and runtime-manifest cleanup were incomplete.

The v3 draft will add schema-bound D1, frozen digest byte grammars and state edges, immutable staged-tree snapshots, subject/final result separation, a required same-mount synthetic root, regression coverage, and fail-closed cleanup. This r2 verdict is not approval. Fresh review must target the later pushed v3 commit.
