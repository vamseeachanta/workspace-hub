---
id: workspace-hub#1311
title: "Mount /mnt/ace from ace-linux-1 via NFS on ace-linux-2"
repo: workspace-hub
category: infrastructure
route: A
priority: medium
created: 2026-03-23
machine: ace-linux-2
tags: [nfs, mount, network, research-literature]
github_issue_ref: https://github.com/vamseeachanta/workspace-hub/issues/1311
---

# WRK-5125: Mount /mnt/ace from ace-linux-1 via NFS on ace-linux-2

## Goal

Give ace-linux-2 direct NFS read-write access to the 7.5TB `/mnt/ace` drive on ace-linux-1, replacing the need for slow SSHFS mounts. This enables ace-linux-2 agents to access research literature at `/mnt/ace-data/digitalmodel/docs/domains/` at near-native speed.

## Steps

### 1. Server setup (on ace-linux-1)

```bash
sudo bash scripts/setup/nfs-ace-drive.sh server
```

Installs `nfs-kernel-server`, adds `/mnt/ace` to `/etc/exports` (read-write to ace-linux-2), starts the NFS service.

### 2. Client setup (on ace-linux-2)

```bash
sudo bash scripts/setup/nfs-ace-drive.sh client
```

Installs `nfs-common`, creates `/mnt/remote/ace-linux-1/ace`, adds fstab entry, mounts.

### 3. Verify

```bash
bash scripts/setup/nfs-ace-drive.sh verify
```

Run on both machines to confirm export and mount are live.

## Acceptance Criteria

- [ ] `showmount -e ace-linux-1` shows `/mnt/ace` from ace-linux-2
- [ ] `ls /mnt/remote/ace-linux-1/ace/digitalmodel/docs/domains/` lists domain folders from ace-linux-2
- [ ] Mount persists across reboot (fstab entry with `nofail`)
- [ ] ace-linux-2 boots normally if ace-linux-1 is offline (`nofail,bg,soft`)

## Script

`scripts/setup/nfs-ace-drive.sh` — already written, supports `server`, `client`, `verify` subcommands.
