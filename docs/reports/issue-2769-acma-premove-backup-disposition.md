# Issue #2769 — ACMA pre-move backup disposition (Phase A dry-run contract)

## Status

- **Phase:** A (metadata-only, dry-run).
- **Branch:** `issue-2769-backup-disposition-claude`.
- **Plan:** [`docs/plans/2026-05-21-issue-2769-acma-premove-backup-disposition.md`](../plans/2026-05-21-issue-2769-acma-premove-backup-disposition.md).
- **Dependency:** [#2767](https://github.com/vamseeachanta/workspace-hub/issues/2767) Phase A inventory module landed on `main` at commit `86149e5e4`.
- **Upstream gates:** [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) and [#2732](https://github.com/vamseeachanta/workspace-hub/issues/2732) (raw/source bucket placement) must close before any disposition recommendation moves out of `blocked` for live data.

## What this phase delivers

A repo-safe reporting tool that compares one backup root against the corresponding active root via content-hash metadata. The tool:

- emits no client names, raw paths, filenames, or file bodies;
- emits no shell commands (no `rm`, `mv`, `tar`, `dd`, `shred`, `gzip`, `zstd`, etc.);
- never executes a destructive disposition action (`move`/`delete`/`archive`/`compress`/`merge`/`tar`) — the helper raises `DestructiveActionBlocked`;
- declares `disposition_status` as either `blocked` or `ready_for_recommendation`, never `proceed`.

The live ACMA scan against the redacted pre-move backup root is **not** invoked here. It is an operator action gated on a separate execution issue.

## Module surface

`scripts/data/backup_disposition.py` (composed over `scripts/data/preexisting_inventory.py`):

| Symbol | Role |
| --- | --- |
| `compare_backup_to_active(backup_root, active_root)` | Returns a `BackupComparison` with classification in `{fully_redundant, partially_unique, entirely_unique, incomplete_scan}` and overlap/unique counts. |
| `measure_disk_pressure(mount_path, disk_usage_fn=shutil.disk_usage)` | Returns a `DiskPressureSnapshot` with severity in `{normal, elevated, high}`; thresholds 85% / 95%. |
| `build_disposition_report(...)` | Composes comparison + pressure + dependency gates into a `BackupDispositionReport`. |
| `render_public_report(report)` | Lines of redacted Markdown — no raw paths, no filenames. |
| `write_disposition_report(...)` | Persists the rendered report to a target Markdown path. |
| `execute_disposition_recommendation(action_kind, backup_source_id, dry_run)` | Always refuses destructive kinds; only `retain` / `report_only` permitted, and only as no-op dry-runs. |
| `main(argv)` | CLI: `--backup-root`, `--active-root`, `--mount-path`, `--output`, `--blocked-by issue:status` (repeatable), `--dry-run`. |

## Gate priority (highest to lowest)

When `build_disposition_report` computes `disposition_status` / `recommended_action`:

1. Any `BlockedByItem` with status not `closed` → `blocked` / `deferred:dependency_open`.
2. Comparison classification `incomplete_scan` → `blocked` / `deferred:incomplete_scan`.
3. Disk pressure severity `high` (≥ 95%) → `blocked` / `deferred:high_disk_pressure_requires_human_review`.
4. Otherwise → `ready_for_recommendation` / `deferred:awaiting_approved_execution_issue`.

Even at status `ready_for_recommendation`, the action is `deferred:awaiting_approved_execution_issue`. Phase A never authorizes destructive execution; the most permissive output it can emit is "open a separate execution issue".

## Redaction guarantees

The redaction contract is property-tested in `tests/test_backup_disposition.py`:

- the rendered report contains no client name token, no raw filesystem path, no filename;
- a sweep of forbidden command patterns (`rm -…`, `mv /…`, `tar -c…`, `shred`, `dd if=`, `find … -delete`, `gzip`, `zstd`) matches zero substrings;
- the CLI-written Markdown carries the literal phrase `metadata-only`.

The redaction model is inherited from #2767: evidence IDs are `sha256(...)[:16]` digests of `source_id:relative_path` tokens. The same digest collides only on identical relative-path tokens within the same source.

## When the live scan is authorized

A separate execution issue is required. It must include:

- the exact invocation command, in full;
- the rollback source (the backup itself, or an offload destination);
- the verification command;
- a risk rating;
- explicit `status:plan-approved` from the user.

Until that issue exists, the live scan runs as an operator-supervised dry-run only:

```text
uv run python scripts/data/backup_disposition.py \
  --backup-root <BACKUP_PATH_REDACTED> \
  --active-root <ACTIVE_PATH_REDACTED> \
  --mount-path <MOUNT_PATH_REDACTED> \
  --output docs/reports/issue-2769-live-redacted.md \
  --blocked-by "#2731:open" \
  --blocked-by "#2732:open" \
  --dry-run
```

The actual paths are intentionally left as redacted placeholders in this repo-tracked doc.

## Verification

```text
uv run pytest tests/test_backup_disposition.py tests/test_preexisting_inventory.py
# 27 passed
uv run python -m py_compile scripts/data/backup_disposition.py tests/test_backup_disposition.py
# OK
```

## Out of scope for this phase

- Live execution against the local ACMA data root.
- Multi-backup batch comparison (Phase A is one backup vs one active).
- Bounded-sampling strategy for very large trees — Phase A relies on the upstream `preexisting_inventory` walker's existing inaccessible-path handling and would degrade to `incomplete_scan` rather than risk an unbounded scan in a constrained environment.
- Any local data-mount expansion or hardware decision.
