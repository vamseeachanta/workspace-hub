# Ecosystem sync publication boundary

The scheduled sync has a registered, path-restricted direct-main exemption.
The implementation already enforces that exemption; the focused tests and
worked examples below explain its boundary and failure behavior.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| Initial | 2026-10-22 | Document the existing exemption and regression tests to make its publication boundary reviewable. |

## Policy and implementation basis

Issue #3985 offered a PR workflow or an explicit exemption. The merged changes
in PRs #3957, #4038 and #4048 implemented the exemption, restricted its paths and
bound each push to a validated commit object. The current authorities are:

- [Canonical workflow](../../AGENTS.md), including registered exemptions.
- [Direct-main exemptions](../../.claude/rules/merge-authorization.md#direct-main-exemptions),
  which names the permitted state file and report directory.
- [Scheduled implementation](../../.claude/cron/ecosystem-sync.sh), specifically
  `outside_allowlist_z`, `guard_staged` and `guard_outgoing`.

Only `.claude/state/ecosystem-sync/last-sync.yaml` and paths below
`docs/sync-reports/` qualify. A similar name or neighboring directory does not
qualify. Git paths are read as NUL-delimited records, so spaces and newlines in
a report name do not split the record. Rename detection is disabled during
inspection so a move from a foreign path cannot hide the deletion at its source.

## Method

The path predicate is exact equality to the state file **or** a prefix match
including the trailing slash of the report directory. This predicate comes
from the registered exemption, rather than an engineering equation.

Before a commit, every staged path must satisfy that predicate. Before a push,
the remote-tracking main reference must exist, all Git queries must succeed,
the outgoing history must contain no merges, and both the cumulative range and
each outgoing commit must contain only permitted paths. An add followed by a
revert is therefore rejected even if the net tree difference looks permitted.
The script pushes the captured and inspected object ID, so a subsequent local
commit cannot join that push through a moving branch reference.

The rejection status is `6`, as defined by the script's guard contract. The
guards stop before the affected commit or push; they do not roll back existing
local work. Other operational failures have separate exit paths in the script.

## Worked examples

These are synthetic inputs with results derived directly from the predicate.
No external data, empirical coefficient or numerical tolerance is required.

| Input | Independent evaluation | Answer |
| --- | --- | --- |
| Staged state file and `docs/sync-reports/digest.md` | State equality holds for the first path; the report prefix holds for the second. | Path checks pass, subject to the remaining checks. |
| Staged `docs/sync-reports-old/digest.md` | The hyphen follows `sync-reports`; the required slash prefix is absent. | Reject with status `6`; no commit or push. |
| Staged `.claude/state/ecosystem-sync/last-sync.yaml.bak` | The suffix prevents exact state-file equality; the report prefix is absent. | Reject with status `6`; no commit or push. |
| Outgoing commit adds `README.md`; a later commit reverts it | The cumulative path set may be empty, but the individual commit contains a foreign path. | Reject with status `6`; no push. |
| Git emits a permitted report path and then reports failure | Membership holds, but successful enumeration is a separate required condition. | Reject with status `6`; no push. |
| Local history advances after validation | The push source is the inspected object ID rather than the new branch tip. | Only the inspected commit is published. |

The focused pytest cases state the membership and query truth tables in their
docstrings. The shell suite exercises real local bare repositories, including
staged foreign paths, renames, reverted paths, merge commits, rejected pushes
and a concurrent local commit. Its tool substitutes prevent actual sync work.

## Reproduce

Run from the repository root with an externally selected temporary directory:

```sh
uv run --no-project --with pytest python -m pytest \
  tests/cron/test_ecosystem_sync_push_guard.py -q -p no:cacheprovider \
  --basetemp="$TMPDIR/ecosystem-guard-tests"
bash scripts/cron/tests/test_ecosystem_sync_push_guard.sh
bash -n .claude/cron/ecosystem-sync.sh
bash -n scripts/cron/tests/test_ecosystem_sync_push_guard.sh
```

The [enforcement workflow](../../.github/workflows/enforcement-gate.yml) runs
both suites. Focused tests load only the implementation's guard definitions
and constants, substitute Git responses and isolate inherited Git variables.
They never execute the scheduled entry point or contact a remote service.

## Limits

These checks establish the tested path and query boundary. They do not prove
the generated content is correct, grant publication authority for another
automation, verify deployed scheduler configuration, or replace independent
review. This change preserves the existing exemption and retry behavior.
