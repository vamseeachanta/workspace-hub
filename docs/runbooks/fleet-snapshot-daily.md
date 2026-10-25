# Daily snapshot publication

The repository-owned writer labels a private candidate before replacing or
staging `docs/reports/fleet-snapshots/latest.json`. A refused candidate leaves
the committed snapshot unchanged. Publication-state checks run under the shared
publish lock, so an edit made while the writer waits is checked before collection.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| Initial | 2026-10-22 | Document the existing writer and state-preservation regressions to support installation and refusal diagnosis. |

## Inputs and method

Run `scripts/fleet/fleet-snapshot-daily.sh` from a configured publication clone
on `main`. Use exactly one input method:

- `FLEET_SNAPSHOT_SOURCE`: an existing private JSON candidate outside the repository.
- `FLEET_SNAPSHOT_COLLECT_CMD`: the existing collection command, which must write
  JSON to the supplied `FLEET_SNAPSHOT_OUT` and must not stage, commit or push.

`FLEET_LABEL_MAP` identifies the private map. Its format and accepted public
labels are defined by
[`fleet_snapshot_labels.py`](../../scripts/fleet/fleet_snapshot_labels.py).
`FLEET_HUB` selects the publication clone. `FLEET_PUBLISH_LOCK`, if supplied,
must be the same lock used by `account-usage-cron.sh`.

The writer holds the lock while checking the branch and snapshot state,
synchronizing the publication clone, collecting, labelling, replacing, staging,
committing and pushing. It refuses tracked edits, an untracked `latest.json`,
or unrelated staged paths. Labeller failure returns nonzero before replacement
or staging. A failed commit restores the previous tracked file; if the output
was absent, it restores absence. The writer creates no dated snapshot.
An unchanged labelled candidate creates no commit.

`FLEET_NO_PUSH=1` suppresses the push only; a changed candidate is still committed.
After a failed push, inspect and recover the local commit before another run.
Do not discard local state to resume publication.

## Scheduler setup

Print a proposed command from the intended publication clone:

```bash
bash scripts/fleet/fleet-snapshot-daily.sh --print-scheduler-entry
```

The printed command is a template, not an installed schedule. The maintainer
must substitute the existing collection command and preserve the intended
cadence. Review the mutation controls in
[`mutation-surfaces.yaml`](../../config/scheduled-tasks/mutation-surfaces.yaml)
before changing scheduler configuration. Confirm that the old writer no longer
commits independently: wrapping a command which still stages raw output does
not establish the guarded commit boundary.

No scheduler was inspected or changed for this implementation. Installation,
private-map validation and observation of the next daily run remain required.

## Worked synthetic example

Use a disposable clone on `main`, with a configured Git identity. The example
uses synthetic input names. Store both the raw candidate and map in private
scratch storage outside the clone:

```bash
mkdir -p "$TMPDIR/snapshot-example"
cat > "$TMPDIR/snapshot-example/map.txt" <<'EOF'
sample-node mac-1
fleet-collector fleet-collector
EOF
cat > "$TMPDIR/snapshot-example/raw.json" <<'EOF'
{
  "generated_by": "fleet-collector",
  "machines": [{"name": "sample-node", "reachable": true}]
}
EOF
FLEET_LABEL_MAP="$TMPDIR/snapshot-example/map.txt" \
FLEET_SNAPSHOT_SOURCE="$TMPDIR/snapshot-example/raw.json" \
FLEET_NO_PUSH=1 bash scripts/fleet/fleet-snapshot-daily.sh
```

Hand derivation: the map replaces `sample-node` with `mac-1`. The identity map
preserves `fleet-collector`, and the Boolean observation is unchanged. The
expected contents of `latest.json`, ignoring whitespace, are:

```json
{
  "generated_by": "fleet-collector",
  "machines": [{"name": "mac-1", "reachable": true}]
}
```

Repeating the same input leaves the commit unchanged. Replacing the input
name with an unmapped synthetic name makes the labeller refuse the candidate;
the previous bytes, index and commit remain unchanged. The automated example
is `test_latest_only_and_repeated_identical_input_is_noop` in
[`test_fleet_snapshot_daily_guard.py`](../../tests/fleet/test_fleet_snapshot_daily_guard.py).

## Refusal diagnosis

The hourly safety net checks each snapshot with the private map. The labeller
exit contract is defined in its module docstring: zero means unchanged, one in
check mode means a rewrite is needed, and two means refusal. These are protocol
statuses, not numerical engineering limits.

Inspect `logs/fleet/account-usage-*.log` privately for `labels: refused` messages.
Then check the candidate without writing it:

```bash
python3 scripts/fleet/fleet_snapshot_labels.py --check "$SNAPSHOT"
```

Use the same configured map as the scheduled command. A missing map, malformed
map, unmapped input, or remaining physical-name fragment can cause refusal.
The hourly wrapper suppresses the labeller diagnostics, so its refusal line
alone cannot establish that an entry is missing. If the initial check requested
a rewrite but the write failed, the hourly message retains the check status;
inspect the underlying failure privately rather than treating that status as
a successful rewrite.

Report only an affected approved label when its identity can be established
from authorized private evidence. Otherwise report an unresolved map entry.
Do not publish the map, raw names, log contents or inferred identities.
No private logs or map were available in the implementation checkout; the cause
of the reported historical refusals remains NOT_EVALUATED.

## Sources and verification basis

- Issue #4027, acceptance and single-file amendment (2026): label before staging,
  refuse unknown input, write `latest.json` only, and leave scheduling to the maintainer.
- Issue #3944 and linked changes #3959 and #4026 (2026): hourly repair cannot
  replace validation at the writer's commit boundary.
- The labeller source defines the map format and exit contract; the hourly
  wrapper defines the currently logged refusal behavior.
- Regression expectations use independent comparisons of snapshot bytes,
  Git index paths and commit identity. No equations or engineering constants apply.

The existing dated snapshots are retained. Their retirement remains follow-up
under #3944 after installation; historical data removal and history rewriting
are outside this change. Repository snapshot checks can therefore still report
pre-existing layout or label failures. Local integration tests establish the
wrapper's behavior, not live scheduler adoption or a successful daily run.
