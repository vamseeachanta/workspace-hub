# Archived Skill: `external-drive-ingest-planning`

Original path: `/home/vamsee/.hermes/skills/workspace-hub/external-drive-ingest-planning`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub/external-drive-ingest-planning`
Consolidation date: 2026-04-29

---

---
name: external-drive-ingest-planning
description: "Plan safe external-drive ingests into repo-aligned storage such as /mnt/ace: read-only mounts, manifests, staged rsync, dedupe-merge gates, GitHub issue traceability, and governance/execution split."
version: 1.0.0
author: Hermes Agent
category: workspace-hub
tags: [external-drive, ntfs, data-ingest, rsync, github-issues, governance, mnt-ace]
triggers:
  - User asks to ingest, consolidate, copy, or organize an external drive into /mnt/ace or another long-lived data mount
  - External NTFS/USB drive data must be copied while preserving source provenance
  - A data migration needs destination mapping, manifests, dedupe, and GitHub issue tracking before file operations
  - Source folders need mapping into repo-aligned buckets and execution must be gated by planning approval
related_skills:
  - diagnose-and-mount-dirty-ntfs-drives
  - diagnose-dirty-ntfs-mount-errors
  - github-issues
  - gh-work-planning
  - issue-planning-mode
---

# External Drive Ingest Planning

Use this when planning a safe ingest from an external drive into `/mnt/ace` or another persistent data mount. The class of task is not just "mount the drive"; it is **source-preserving, provenance-tracked data migration with staged copy and dedupe/merge risk controls**.

## Class-first trigger

A drive or mounted folder contains legacy/project/reference data that must be mapped into durable repo-aligned destinations, copied safely, and tracked through GitHub before any destructive or ambiguous operation.

## Core principles

1. **No file operations before decisions are locked.** Ask/resolve destination ambiguities first.
2. **Mount source read-only by default.** Never write to the source drive unless explicitly approved.
3. **Separate execution and governance.** Create an execution issue for the concrete ingest and a governance/standard issue if the session surfaces reusable placement policy.
4. **Stage first, merge later.** Copy into `_from_<source-label>/` staging folders; dedupe-merge into the parent only as a second reviewed phase.
5. **Manifest before copy.** Capture source file/size inventory and bounded checksums before rsync.
6. **Cross-link prior art.** Existing layout/dedupe/inventory issues are part of resource intelligence, not optional context.
7. **No self-approval.** For plan-gated repos, create issues/plans/reviews and stop at `status:plan-review` until the user approves.

## Step-by-step workflow

### 1. Live device discovery

Run live system checks rather than relying on prior device names:

```bash
lsblk -o NAME,SIZE,FSTYPE,LABEL,MOUNTPOINT
```

If NTFS, use a non-mutating check first:

```bash
sudo ntfsfix --no-action /dev/sdXY
```

Do **not** run mutating `ntfsfix`, `force`, or a writable mount for archival/ingest work without explicit user approval.

### 2. Read-only mount pattern

After confirming the device node and source label:

```bash
sudo mkdir -p /mnt/<source-label-lower>
sudo ntfs-3g -o ro,big_writes,uid=$(id -u),gid=$(id -g),umask=022 /dev/sdXY /mnt/<source-label-lower>
```

Verify the effective mount mode before any inventory or mapping work:

```bash
findmnt /mnt/<source-label-lower> -o TARGET,SOURCE,FSTYPE,OPTIONS
```

For source-preserving ingest workflows, treat `rw` as a blocker even if ownership/perms look correct (`uid/gid`, `umask=022`) and even if `big_writes` is enabled. `big_writes` is useful for later approved high-volume copy performance, but it does not satisfy the source-immutability requirement. If the drive is already mounted read-write, remount read-only before full manifests/checksums:

```bash
sudo umount /mnt/<source-label-lower>
sudo ntfs-3g -o ro,big_writes,uid=$(id -u),gid=$(id -g),umask=022 /dev/sdXY /mnt/<source-label-lower>
```

If the drive is not visible, stop and ask the user to reconnect it. Do not fabricate source inventory.

### 3. Destination mapping

Build a source-to-destination table before copying. For `/mnt/ace`, prefer repo-aligned buckets:

```text
/mnt/ace/<repo-name>/<domain>/...
```

Clarify whether ambiguous buckets are real repos or category folders. In the ACE workspace, examples include:

- `workspace-hub` = governance/planning/orchestration, not bulk data dumping
- `client_projects` = real repo bucket for legacy client project material when appropriate
- `acma-projects` = ACMA project/client-number material
- `assethold` = asset-holding / real-estate data
- `digitalmodel` = engineering workflow/reference/tooling data
- `doris` = Doris project/training/codes material
- `acma-codes` = standards/regulatory corpus; verify before duplicating codes/regulations

### 4. Issue drafting before execution

For a non-trivial ingest, draft issues before copying:

1. **Execution issue** in the operational repo (often `workspace-hub`): exact source-to-destination map, mount policy, manifest plan, rsync/dedupe gates, acceptance criteria.
2. **Governance issue** in the strategy/policy repo if the work clarifies reusable standards: destination-selection rules, staging convention, MOVE-LOG fields, retention policy.

Before creating issues:
- search for duplicates and prior-art issues
- inspect available labels and use existing taxonomy
- write long bodies to temp files and create with `gh issue create --body-file`
- verify created issue bodies, labels, URLs
- cross-link companion issues via comments and/or body updates

### 5. Manifest plan

Create a durable planning/intel area, for example:

```text
.planning/intel/<source-label>-ingest/
  lsblk-before-mount.txt
  ntfsfix-no-action.txt
  mount-command.txt
  source-top-level-inventory.tsv
  source-file-size-manifest.tsv
  source-sha256-under-100mb.txt
  destination-preexisting-inventory/
  rsync-dry-run-logs/
  rsync-final-logs/
  post-copy-verification/
```

Typical pre-copy commands:

```bash
find /mnt/<source> -type f -printf '%P\t%s\n' > .planning/intel/<source>-ingest/source-file-size-manifest.tsv
find /mnt/<source> -type f -size -100M -print0 \
  | sort -z \
  | xargs -0 sha256sum > .planning/intel/<source>-ingest/source-sha256-under-100mb.txt
```

### 6. Staged rsync pattern

Dry-run first:

```bash
rsync -aHAXn --info=progress2 --stats \
  /mnt/<source>/<folder>/ \
  /mnt/ace/<repo>/<domain>/_from_<source-label>/
```

Final copy only after dry-run review and plan approval:

```bash
rsync -aHAX --info=progress2 --stats \
  /mnt/<source>/<folder>/ \
  /mnt/ace/<repo>/<domain>/_from_<source-label>/
```

Use `--link-dest` only after validating the parent destination and confirming the option points to the intended existing corpus.

If the assistant cannot run `sudo` non-interactively, generate a small auditable helper script under the planning/intel directory that the user can execute locally. The script should:

1. remount the source drive read-only and verify `findmnt -no OPTIONS` contains `ro`
2. generate source inventory and bounded checksums before copy
3. run dry-run rsync before real rsync for each bucket
4. copy only into `_from_<source-label>/` staging destinations
5. append/update `MOVE-LOG.md` beside each staging destination
6. skip known verify-only corpora (for example duplicate codes/regulations) unless missing content is proven
7. perform no source deletion and no parent-folder dedupe merge

When `umount` reports `target is busy`, do not force-unmount first. Identify holders:

```bash
lsof +f -- /mnt/<source>
sudo fuser -vm /mnt/<source>
```

Common benign holder: a desktop file manager (for example Nautilus) opened at the mountpoint. Close the file-manager window or kill that process, ensure no shell has `cwd` under the mount, then rerun the read-only remount.

### 7. MOVE-LOG template

Each destination bucket should record provenance:

```markdown
## <source-drive-label> ingest

- Source drive label:
- Source filesystem:
- Source device node at ingest:
- Source path:
- Destination staging path:
- Final destination path:
- Ingest date:
- Operator/agent:
- File count:
- Byte count:
- Manifest path:
- Checksum policy:
- Rsync dry-run log:
- Rsync final log:
- Dedupe/merge status:
- Retention decision:
- Related GitHub issue:
```

### 8. Plan-gated repo handling

If the repo enforces planning:

```text
Issue → Resource Intel → Plan → Adversarial Review → status:plan-review → USER APPROVES → status:plan-approved → Execute
```

Do not mount/copy/rsync as implementation until the approved plan gate is satisfied if the task has been scoped as execution work. Discovery commands like `lsblk` are fine; source mutation and destination writes are not.

### 9. Dedupe-merge assessment phase after staged copy

After staged copy verification passes, continue with **assessment and dry-run only** unless the user explicitly approves a merge scope. The class of work is now parent-vs-staging reconciliation, not source ingest.

Recommended artifact layout:

```text
.planning/intel/<source>-ingest/
  dedupe-merge-assessment-report.md
  dedupe-merge-assessment-summary.tsv
  dedupe-merge-rsync-dry-run-summary.tsv
  dedupe-merge-assessment/
    NN-<bucket>.stage-only.tsv
    NN-<bucket>.parent-only.tsv
    NN-<bucket>.same-path-same-size.tsv
    NN-<bucket>.same-path-different-size.tsv
    NN-<bucket>.rsync-ignore-existing-dry-run.log
```

For each bucket, build parent and staging inventories while excluding `_from_elements` from the parent scan. Compare relative paths into these categories:

- same relative path + same size: duplicate by path/size; keep parent and do not overwrite
- same relative path + different size: conflict; block automatic merge and review case-by-case
- stage-only: candidate for `--ignore-existing` merge
- parent-only: existing retained destination content

Dry-run the candidate merge for each bucket and summarize in a table before any real copy:

```bash
rsync -aHAXn --ignore-existing --itemize-changes --stats "$STAGE/" "$PARENT/" \
  > ".planning/intel/<source>-ingest/dedupe-merge-assessment/NN-<bucket>.rsync-ignore-existing-dry-run.log"
```

Only after explicit bucket/batch approval, run the same command without `-n` when there is enough destination free space for a byte-copy:

```bash
rsync -aHAX --ignore-existing "$STAGE/" "$PARENT/"
```

For very large staged data where the parent and staging paths are on the same filesystem and destination free space is lower than the staged byte count, prefer a hardlink-preserving parent materialization rather than duplicating bytes. Preflight first:

```bash
df -hT "$PARENT"
stat -c '%d %n' "$PARENT" "$STAGE"   # device IDs must match
# Optional disposable hardlink test on the same filesystem before bulk work.
```

Dry-run and then execute with `--link-dest` pointing at the staging directory:

```bash
rsync -aHAXn --ignore-existing --link-dest="$STAGE" --itemize-changes --stats "$STAGE/" "$PARENT/"
rsync -aHAX  --ignore-existing --link-dest="$STAGE" --itemize-changes --stats "$STAGE/" "$PARENT/"
```

This creates parent directory entries hardlinked to staged file data, avoiding a second full copy while still preserving `_from_elements` staging. After a hardlink merge, verify every staged file has a parent counterpart with the same relative path, same size, and the same `(st_dev, st_ino)` identity. Remember that hardlinked parent and staging entries share data until staging is deliberately removed; do not edit parent files in place if the staging copy is meant to remain an immutable retention artifact.

Then verify the parent, update `MOVE-LOG.md`, and continue retaining both source media and `_from_elements` staging until retention gates are satisfied. Post the assessment/merge report to the execution issue with target-location tables and clear statements about what did and did not get deleted.

Execution closeout should not silently imply cleanup. After the approved merge verifies cleanly:

1. Post a final closeout comment to the execution issue with the bucket table, artifact paths, and explicit retained-source/staging guardrails.
2. Close the execution issue as completed.
3. Open a separate retention-gated cleanup issue that lists every retained `_from_elements` path, requires the minimum retention window to elapse, requires a fresh dry-run/verification table, and blocks deletion until explicit approval.
4. Link the cleanup issue back to the closed execution issue.
5. If the ingest clarified durable placement policy, update the governance/strategy issue with reusable lessons (layout, staging, source read-only, hardlink merge, MOVE-LOG, retention).

### 10. Retention-gated cleanup issue execution

When the user asks to "execute" a retention-gated cleanup issue before the not-before date, interpret execution as the **non-destructive readiness phase** unless the user explicitly overrides the retention policy. Do not delete staging/source data, unmount/release the source drive, or close the cleanup issue while the retention gate has not elapsed.

Readiness execution should:

1. Inspect the cleanup issue state/body/comments and confirm the not-before date.
2. Check the live current date and source mount state (`findmnt /mnt/<source> -o TARGET,SOURCE,FSTYPE,OPTIONS`).
3. Verify parent-vs-staging candidates still match. For hardlink merges, require each staged file to have a parent counterpart with the same relative path, same size, and same `(st_dev, st_ino)` identity.
4. Write durable readiness artifacts under `.planning/intel/<source>-ingest/`, including a script, markdown report, summary TSV, and failure TSV.
5. Post a GitHub issue comment with a concise table of bucket readiness, mount state, retention status, and the explicit decision: cleanup remains blocked until the not-before date unless the user explicitly overrides.
6. Leave the cleanup issue open and preserve all retained `_from_elements` staging/source media.

After the retention date elapses, rerun the same readiness verification immediately before any destructive cleanup, then require explicit cleanup approval/scope before removing staging or releasing source media.

## Post-ingest LLM-wiki / overnight planning wave

After a staged copy, dedupe/merge, metadata-first wiki indexing, or first-pass deep extraction completes, the next logical work is often **not** more copying. Treat large remaining corpora as planning targets:

1. Create one umbrella coordination issue plus file-disjoint child issues for each remaining corpus/domain.
2. Cross-link the ingest/retention issues and prior layout/governance issues so the new wave preserves source-of-record and retention context.
3. Use planning-only overnight prompts unless the user has explicitly approved implementation. Prompts must forbid writes to `/mnt/ace`, source mounts, `_from_<source>/` staging, and raw bulk wiki folders.
4. Give each worker one unique result artifact and allowed write directory. Include negative write boundaries for every other corpus to prevent git contention.
5. Reference raw `/mnt/ace/...` paths as source-of-record inputs only. Workers should propose curated extraction scope, taxonomy, risks, and approval gates rather than bulk-copying or deep-extracting entire large corpora.
6. Comment on the umbrella issue with the issue-to-terminal map, prompt paths, PIDs/log paths, and the next approval gate for morning reconciliation.

## Pitfalls

- Treating `/dev/sdXY` from a prior session as stable; USB device nodes change.
- Treating a successfully accessible read-write NTFS mount as good enough for archival ingest. Check `findmnt` and require `ro` unless the user explicitly overrides source immutability.
- Letting a dirty NTFS troubleshooting skill push you into mutating `ntfsfix` before source-preservation decisions are approved.
- Copying directly into final parent directories and losing the ability to review dedupe/merge separately.
- Using a top-level `_inbox` when per-destination staging better preserves destination ownership.
- Creating a governance issue but forgetting to update the execution issue body/comment with the final cross-link.
- Using non-existent labels instead of inspecting repo label taxonomy first.
- Assuming a folder name is a repo bucket; verify repo existence and local `/mnt/ace` layout.
- Treating Windows metadata folders like `$RECYCLE.BIN` and `System Volume Information` as project data; include them in top-level inventory but normally classify as skip/metadata unless the user asks otherwise.
- Pasting long Claude prompts directly into a TUI/terminal can inject escape garbage. Prefer writing prompt files with `cat > /tmp/prompt.txt <<'EOF' ... EOF` or `nano`, then running `claude -p "$(cat /tmp/prompt.txt)"`.

## Verification checklist

Before finalizing issue creation or handoff, verify:

- live drive visibility or explicitly document that it is not attached
- prior-art issues are linked
- source-to-destination map reflects user decisions
- labels actually exist or issue creation avoids invalid labels
- created issue URLs, labels, and body cross-links are correct
- no rsync/mount mutation occurred before approval
- `Elements` or other source drive remains read-only / untouched until the plan is approved

After staged copy completes, run a source-vs-staging verifier before any dedupe merge. A simple robust verifier scans each source folder and matching `_from_<source-label>/` destination, comparing relative paths and file sizes, then writes:

```text
.planning/intel/<source>-ingest/post-copy-verification-summary.tsv
.planning/intel/<source>-ingest/post-copy-verification-report.md
.planning/intel/<source>-ingest/post-copy-verification/*.tsv
```

Post-copy closure should be an explicit checklist, especially when the user wants step-by-step execution:

1. Read the verifier summary/report and identify any failed buckets (`missing`, size mismatch, or unexpected extras).
2. Inspect every rsync final log for a normal completion footer (for example `total size is ... speedup is ...`) and error count/patterns.
3. Re-check the source mount remains read-only with `findmnt` before reporting success.
4. Confirm intentional skips/verify-only corpora have a durable note (for example `codes-regulations-skip-note.txt`).
5. Confirm each staged destination has a `MOVE-LOG.md` with source path, file/byte count, related issue, and dedupe status.
6. Write a concise staged-copy status report artifact under `.planning/intel/<source>-ingest/`.
7. Post a GitHub issue comment with the pass/fail bucket table, links/paths to artifacts, and explicit statements: no parent merge, no source deletion.
8. Create the next-phase dedupe/merge checklist, ordered from smallest/lowest-risk bucket to largest/highest-risk bucket, with dry-run analysis commands only.

Treat a clean staged-copy verification as permission only to report completion and plan the next phase. It is **not** permission to merge into parent folders. The next logical phase is bucket-by-bucket dedupe/merge planning with dry-run commands and rollback/retention notes.
