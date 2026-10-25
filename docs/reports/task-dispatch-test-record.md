# Task dispatch readiness test record

The synthetic dispatch tests verify source-local grading, qualified provider
identities, freshness limits and timestamp validation. Operational readiness
requires separately retrieved dispatch evidence and verified deployment mappings.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| 1 | 2026-10-25 | Record receipt-grading regressions and verification limits. |

## Scope and method

The starting commit is `3c08b4c415971298c5c5e4ea210cad1b4702ac78`.
The recorded main reference is `d8a3861ac511844a7d9f801dbba8fd24ee2f5bf7`;
the merge base is `ccd270b1f199f7e9204d8314934fe89aaada2563`.
Validation runs against the uncommitted tree because publication occurs later.
No base integration occurs in this change.

Commands use `uv run --no-project --with pytest --with pyyaml python -m pytest`,
with `-q -rA -p no:cacheprovider` and a separate temporary directory per run.
The test paths are `tests/workstations` and `tests/readiness`; the focused paths
are `tests/workstations/test_task_dispatch.py` and
`tests/readiness/test_build_equality_matrix.py`.
The initial command with only `--with pytest` encountered 26 collection errors
because PyYAML was unavailable. Adding the declared YAML dependency allowed
collection without changing project dependencies or lockfiles.

## Results

| Check | Passed | Failed | Skipped |
| --- | ---: | ---: | ---: |
| Original test folders at the starting commit | 666 | 113 | 34 |
| New dispatch regressions before implementation | 12 | 13 | 0 |
| Final focused dispatch and matrix tests | 132 | 0 | 0 |
| Original test folders with receipt fixes | 685 | 113 | 34 |

The initial and final broad runs have exactly the same 113 failed test identifiers;
there are no new failed test identifiers. These counts describe the two named
test folders, rather than the full repository. Logs remain in temporary storage.

The dispatch suite contributes 32 focused tests. Seven synthetic roles exercise
42 ordered pairs and 84 provider-qualified receipts. Source-local grading counts
only outgoing pairs. Missing provider evidence, changed intended identities,
ambiguous duplicate receipts and mismatched payload identities cannot grade
ready. Endpoint freshness windows and any explicit tighter cap apply together.
Offset-free timestamps are rejected; explicit offsets are normalized.

The collector regression executes its embedded dispatch block against temporary
registry and receipt fixtures. It also checks that the shell passes the collecting
source. No live provider command or remote dispatch is needed by that regression.

## Baseline

All 113 broad-suite failures also occurred at the starting commit. Failure
identifiers were compared as sets, without rerunning an exported base tree.
The unchanged failures by test file are:

| Test file under `tests/` | Failures |
| --- | ---: |
| `readiness/test_collect_equality.py` | 45 |
| `readiness/test_collect_equality_ps1_schema.py` | 6 |
| `readiness/test_equality_tree_cleanliness.py` | 14 |
| `readiness/test_publish_equality.py` | 23 |
| `readiness/test_sync_agent_configs_sso.py` | 5 |
| `readiness/test_telegram_hermes_readiness.py` | 15 |
| `readiness/test_telegram_hermes_readiness_tier1_baseline.py` | 2 |
| `workstations/test_dispatch.py` | 1 |
| `workstations/test_handoff_and_status.py` | 2 |

Representative causes include `mktemp failed` when existing fixture environments
drop the temporary-directory setting, denied writes from configuration-sync
scripts, inherited out-of-tree equality behaviour, legacy readiness expectations,
and local identity/path assumptions. These areas were not changed by the receipt
fix. Main was read for comparison: the local-status and path assertions in
`tests/workstations/test_handoff_and_status.py` at lines 214 and 243 remain, and
the collector's temporary-directory allocation remains at line 261 on main.
The publish and legacy-readiness test files also match main byte for byte.
This comparison does not establish that every broad-suite failure reproduces on
current main; no broad-suite execution on main was performed.

## File checks

- `bash -n scripts/readiness/collect-equality.sh`: passed.
- `git diff --check`: passed.
- `uv run --no-project --with pyyaml python scripts/enforcement/check-scheduler-mutation-surfaces.py --json`: passed.
- `uv run --no-project --with pyyaml python scripts/cron/build-cron-identity-inventory.py --check`: passed.
- `uv run --no-project --with pyyaml python scripts/enforcement/check-scheduler-mutation-surfaces.py --check-html docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html`: passed.

The scheduler guard reads index blobs; it validates the starting tracked state
until staging occurs. No governed scheduler input was edited, so regeneration
was unnecessary for these permitted edits. The inventory and HTML comparisons
passed against the existing artifacts. Hooks run during subsequent publication.

## Known limits

The configured deployment subset remains five roles and 20 ordered pairs.
Seven-role algorithm coverage does not establish seven-role deployment coverage.
The two remaining roles lack verified connection and provider mappings in the
registry. Provider identity mappings are deliberately not inferred from aliases;
unconfigured accounts or configurations remain missing evidence.

No live canary, quota, independent log retrieval, duplicate-invocation or
disconnect-survival evidence is established by these synthetic tests. Receipt
content is graded as supplied; this change does not authenticate receipt writers.
Neutral Windows task-folder deployment mappings have not been verified. Base
conflict resolution, governed scheduler configuration and PR metadata changes
remain outside the permitted edits for this change.
