# Verify equivalence fingerprint publication

The sentinel now reads the current fingerprint back from the shared ref before
recording successful publish health. This supplies the remote-presence evidence
required by issue #3506. Live scheduler installation and a current green equality
matrix still require validation on the target workstation.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| Initial | 2026-10-22 | Add exact read-back verification to reject missing or corrupt publication evidence. |

## Method and sources

Publication passes this check when all of the following hold:

- The shared ref can be fetched.
- Its tree contains the exact `<machine_id>.json` key.
- That entry has regular-file mode `100644` and type `blob`, as written by
  `scripts/monitoring/equivalence_state.py::_commit_fingerprint`.
- Its content passes the version-1 contract in
  `scripts/monitoring/equivalence_schema.py::validate_fingerprint`.
- Its raw bytes equal the UTF-8 publication payload from the current fingerprint.

The method uses exact equality, without a numerical tolerance or a new acceptance
limit. Raw binary reads preserve carriage returns rather than hiding text-mode
corruption. The existing health-duration policy includes both push and read-back
time; its limits remain in `scripts/readiness/build-equality-matrix.py`.

Sources:

- Issue #3506: required remote-presence and matrix outcome.
- Issue #3511: empty fingerprint and tree-name corruption evidence.
- [Existing fingerprint schema](../../scripts/monitoring/equivalence_schema.py).
- [Existing publisher tree format and read-back command](../../scripts/monitoring/equivalence_state.py).

These are software protocol requirements; no engineering equations, coefficients
or licensed publications are used.

## Worked example

The synthetic identifier `sample` below is a fixture key. Let `F` be the valid
fingerprint constructed in
`tests/monitoring/test_equivalence_state.py::test_verify_publish_returns_observed_tip_and_only_reads`.
It has `machine_id = sample`; let `B` be its UTF-8 bytes. All other fields are
fixed in that test's fixture and validated against the existing schema.

| Input | Method | Answer |
| --- | --- | --- |
| Tree key `sample.json`, regular blob, content `B` | Exact key, schema and byte equality | Verification returns the fetched tip. |
| No `sample.json`, even if a role-keyed entry exists | Exact key lookup fails | Store unavailable; successful health is blocked. |
| Tree key `sample.json` followed by a carriage return | Exact key lookup fails | Store unavailable; successful health is blocked. |
| Exact key but empty content | Schema validation fails | Store unavailable; successful health is blocked. |
| Exact key but a different timestamp in the content | Current payload differs from `B` | Store unavailable; successful health is blocked. |
| Local payload ends in LF; stored payload ends in CRLF | Raw byte sequences differ | Store unavailable; successful health is blocked. |

These answers follow directly from key membership and byte equality. The tests
construct the alternate bytes independently; they do not compute expected values
with the verifier. Process-boundary tests additionally prove that a failed
read-back records failure health and stops before comparison.

## Operator sequence

Use a clean, current canonical checkout on the target Windows workstation.
Preserve unrelated work before updating it through the repository's normal
procedure. Do not substitute a clean auxiliary clone for canonical evidence.

Install the existing scheduled tasks from Windows Git Bash:

```bash
bash scripts/windows/schedule-equivalence-tasks.sh
```

Run the sentinel once and retain its status:

```bash
rc=0
bash scripts/monitoring/equivalence-sentinel.sh || rc=$?
```

The sentinel's documented statuses distinguish comparison drift from publication
failure. A WARNING or CRITICAL comparison status can follow a verified publish;
it must not be mistaken for a failed publication. A fingerprint, store or health
persistence failure must be investigated before refreshing successful evidence.

For an explicit read-only recheck, provide the registry identifier through
`MACHINE_ID` and use the repository's working Python resolver:

```bash
source scripts/lib/python-resolver.sh
"${PYTHON_CMD[@]}" scripts/monitoring/equivalence_state.py verify-publish \
  --machine "${MACHINE_ID:?registry identifier required}" \
  --file .claude/state/equivalence/local-fingerprint.json
```

The command prints `verified` on success. It fetches the shared ref and reads Git
objects; it does not create a commit, push, install a task or refresh health.
After a verified publication, refresh the canonical equality report using the
existing Windows report command and inspect its publish-health row.

## Limits and follow-up

Read-back proves one fetched snapshot. A later writer can change the ref, and a
network failure can make a successful push temporarily unverifiable. The sentinel
records that outcome conservatively as failure; it does not roll back remote data.
A concurrent update to a different fingerprint is preserved. A replacement of the
same fingerprint with different bytes fails this current-cycle check.

This change does not install or prove execution of any scheduled task. It does
not establish matrix freshness, remote availability after the snapshot, or the
issue's live target acceptance result. Live installation, one successful cycle,
and a refreshed green publish-health row remain operational follow-up.
