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
