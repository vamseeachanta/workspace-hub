# Scheduler reader and mutation contract

A scheduler consumer can inspect runtime dependencies without changing a
scheduler. The `read-only-consumer` kind records those reads without inventing a
mutation primitive. This classification describes scheduler effects only: the
relocation tool can still move or remove data when explicitly invoked.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| Initial | 2026-10-22 | Added source-pinned reader evidence and a worked classification example to distinguish scheduler inspection from mutation. |

## Closed reader schema

```yaml
path: scripts/operations/relocate-to-bulk.sh
kind: read-only-consumer
reads: [current-user-cron, systemd-system, systemd-user]
source_attestation: relocation-scheduler-reads-v1
```

The record has exactly these fields. Mutation operations, delegation,
transactions, authored status and disposition groups are forbidden. Reader
inputs use a closed vocabulary: current-user crontab, root crontab, user and
system systemd units, and current-user Windows tasks. `systemd-system` is a
reader input only; it does not add a mutation primitive or authorize a writer.

The [reader contract](../../scripts/enforcement/scheduler_mutation_consumers.py)
pins the path, source attestation identifier, complete read-target set and
SHA-256 of the reviewed source bytes. The pin includes remote command strings.
A YAML declaration alone cannot establish a reader. Any changed byte, missing
source, extra reader, omitted registration or mismatched target fails validation.
A source change requires renewed inspection and a reviewed contract update.

Discovery retains conservative direct candidates. A pinned reader can account
for a candidate without claiming a write primitive. Unknown indirection and
mutation delegation still fail; unreviewed writers cannot acquire read-only
status by changing their registry kind. No general shell or remote execution
proof is claimed by the byte pin.

## Worked example: dependency reader and timer installer

Inputs are the tracked source of
[the relocation tool](../../scripts/operations/relocate-to-bulk.sh) and
[the sentinel installer](../../scripts/monitoring/bundle-sentinel-install/install.sh).
The method is manual inspection of scheduler effects, followed by exact source
comparison and registry validation. Neither script is executed for this example.

| Input | Observed scheduler effects | Answer |
| --- | --- | --- |
| Relocation dependency gates | List current-user crontab; search user and system unit files, including the remote inspection command. | `read-only-consumer`, derived status `read-only`, no mutation primitive or migration disposition. |
| Sentinel installer | Copy user unit files, reload the user manager, enable and start timers, request lingering. | `direct-owner`, declared `systemd-user-unit-write` and `systemd-user-enable-disable`, derived status `migration-required`. |

The installer keeps its exact `bundle-integrity-sentinel` disposition, tracked by
issue #3792. The [pinned disposition contract](../../scripts/enforcement/scheduler_mutation_dispositions.py)
and [registry](../../config/scheduled-tasks/mutation-surfaces.yaml) must agree on
its tracking issue, defect class and exact membership. New non-compliant writers
require a reviewed change to both; appending a YAML group is insufficient.
The historical resolved disposition remains unchanged. A closed issue does not
supply evidence that another script is compliant.

The installer declares all transaction flags false and no source attestations.
This neither implements nor claims the reference transaction. Reload, start and
lingering are observed effects beyond the current primitive vocabulary; this
change does not establish a complete systemd transaction model.

Independent expected classifications and adversarial mutations appear in
[the regression tests](../../tests/enforcement/test_scheduler_mutation_consumers.py).
Appending a crontab replacement or timer enablement to the reader changes its
bytes and invalidates its evidence. Relabelling the installer as a reader fails
because no reviewed reader contract exists for its path.

## Verification and limits

Run the scheduler enforcement test files and Ruff on the changed Python files.
Unit tests build an explicit source snapshot; separate Git transport tests prove
that production reads index blobs rather than dirty working files. The canonical
checker and HTML generator continue to read the index. Unstaged edits cannot
validate the eventual committed registry through the production CLI; validate
the staged snapshot before publication.

The audit renders reader inputs and evidence with disposition `not applicable`,
without a transaction-compliance or resolved-migration claim. Source bytes,
reader evidence code and regression tests participate in the audit input digest.
No live crontab, systemd manager, relocation command or licensed solver is run.
Runtime permissions, issue lifecycle, systemd transaction attestations and merge
readiness are outside this classification check.

## Sources

- Issue #3789 (2026), acceptance criteria for honest reader vocabulary and explicit migration coverage.
- Issue #3470 (2026), tracked scheduler mutation scope and fail-closed inventory contract.
- Issue #3792 (2026), unavailable systemd transaction attestations.
- The linked source files and registry provide the observed command effects and exact disposition membership.

No engineering equations, empirical coefficients or numerical acceptance limits
are used. Expected results follow the source-inspection method above.
