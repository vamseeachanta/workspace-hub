# Canonical Drive References

> One unique, machine-independent path per shared drive, used consistently
> across the whole repo ecosystem. Reconciled by
> `scripts/setup/canonical-drive-links.sh`.

## The rule

Every shared drive has exactly ONE canonical reference: **`/mnt/<drive>`**.
It resolves on **every** machine in the fleet:

- on the **owner machine** it is the physical disk mount;
- on **every other machine** it is a symlink to the NFS transport path
  `/mnt/remote/<owner-host>/<drive>`.

Repos, scripts, configs, docs, and agent prompts reference the canonical
path only. The transport path (`/mnt/remote/...`) is plumbing — never
hardcode it in ecosystem code.

## Index artifacts and enforcement

Drive-index live configs and small catalogs store canonical `/mnt/<drive>`
paths only. Historical aliases remain legal only in the shared alias map at
`config/drive-index-registry.yml` and in frozen legacy artifacts that are
normalized at read time by `scripts/data/drive-index-search/pathnorm.py`.

Run `scripts/enforcement/check-canonical-drive-paths.sh` to reject new
transport-path aliases in tracked drive-index YAML/JSON configs. YAML lines
that intentionally document transport plumbing may use the trailing
`# transport-path-allowed` sentinel; JSON files must use the baseline because
JSON has no comments.

## Drive registry

| Drive | Canonical path | Owner host | Physical FS | Transport (on non-owners) | Setup script |
|-------|----------------|------------|-------------|---------------------------|--------------|
| ace | `/mnt/ace` | ace-linux-1 | ext4 (7.3 TB) | `/mnt/remote/ace-linux-1/ace` (NFS) | `scripts/setup/nfs-ace-drive.sh` |
| dde | `/mnt/dde` | ace-linux-2 | NTFS/ntfs3 (2.8 TB) | `/mnt/remote/ace-linux-2/dde` (NFS) | `scripts/setup/nfs-dde-drive.sh` |

**Not shared** (per-machine local disks, never symlinked, no transport):
`/mnt/local-analysis` — exists independently on each machine with different
content (workspace/checkout area).

## Transport convention

- NFS mount point: `/mnt/remote/<owner-host>/<drive>` — fstab-managed, options
  `defaults,nofail,rw,bg,intr,soft,timeo=50` (established by the ace mapping).
- Exports live in `/etc/exports` on the owner host, scoped to the fleet
  hostnames (not open subnets).
- Legacy sshfs automounts at the same paths are retired by the per-drive
  setup scripts when the NFS mount takes over (sshfs remains acceptable for
  `local-analysis` cross-machine peeks, which have no canonical alias).

## Adding a new shared drive

1. Mount the disk on its owner at `/mnt/<drive>` (fstab, `nofail`).
2. Copy `scripts/setup/nfs-dde-drive.sh` → `nfs-<drive>-drive.sh`; set
   `EXPORT_PATH`, hosts; run `server` mode on the owner, `client` on others.
3. Add the drive to the `DRIVE_OWNER` registry in
   `scripts/setup/canonical-drive-links.sh`; run it on every machine.
4. Add a row to the registry table above.

## Verification

```bash
sudo bash scripts/setup/canonical-drive-links.sh   # per machine
bash scripts/setup/nfs-dde-drive.sh verify         # per drive
```
