# ace-linux-2 — data availability readiness probe (2026-05-31)

**Host:** `ace-linux-2` (192.168.1.103) — dev-secondary / overflow + CFD execution box
**Data server:** `ace-linux-1` (192.168.1.100) — dev-primary control plane
**Scope:** full storage topology for ace-linux-2 — every local disk plus the ace-linux-1 data shares (`//ace-linux-1/mnt/ace` and others) — mounted, reachable, and read/write-correct. Companion to the full pre-delegation readiness gate in `.agents/skills/coordination/workstation-aware-provider-orchestration/SKILL.md`.

## Verdict

**Data-ready.** Three local disks + two ace-linux-1 network shares are mounted and healthy. ace-linux-1 is ping-reachable; both the NFS share and local NTFS disks are writable; sshfs share auto-mounts. **One path-divergence caveat** (see §Caveats) is low-impact and needs no action.

## Storage inventory

### Local disks (3 physical + OS SSD)

| Mount | Device | Model | FS | Size | Used | Avail | Role |
|---|---|---|---|---|---|---|---|
| `/` | `/dev/sdb1` | Samsung SSD 870 EVO 500GB | ext4 | 458G | 104G | 331G (24%) | OS + `/home/vamsee` + linuxbrew |
| `/mnt/local-analysis` | `/dev/sda2` | WDC WD10EZEX 1TB | ntfs-3g (fuseblk) | 932G | 47G | **885G (6%)** | primary working disk; terminals default here; mirrors ace-linux-1 repo layout |
| `/mnt/dde` | `/dev/sdc2` | Seagate ST3000NC002 3TB | ntfs3 (kernel) | 2.8T | 2.0T | **848G (70%)** | "DDE" archive: `documents/` (1.6T), `0000 O&G/` (184G), `Orcaflex/` (124G), `Literature/` (49G), `Personal/` (26G), `g-drive/`, `o-drive/`, `dropbox_contents/` |

Notes:
- `/mnt/dde` write-tested → **writable** (touch+rm OK). NTFS via the **ntfs3 kernel driver** (≠ the fuseblk/ntfs-3g driver `/mnt/local-analysis` uses) — generally faster, but both are NTFS so preserve Windows ACL/reparse quirks (cf. the Dropbox reparse-point gotcha on `/mnt/local-analysis`).
- `/mnt/dde` is the largest single store of historical engineering data (OrcaFlex runs, O&G project archives, literature). Good cold-storage / read source; at 70% (848G free) it can also absorb large CFD output if `/mnt/local-analysis` fills.
- `sdd–sdh` and `sr*` are 0 B / removable virtual devices (IPMI virtual media, optical) — ignore.

### Remote shares (ace-linux-1)

| Mount | Source | Type | Size | Used | Avail | Health |
|---|---|---|---|---|---|---|
| `/mnt/remote/ace-linux-1/ace` | `ace-linux-1:/mnt/ace` | nfs4 (soft, timeo=50) | 7.3T | 6.5T | **382G (95%)** | mounted, writable |
| `/mnt/remote/ace-linux-1/local-analysis` | `vamsee@ace-linux-1:/mnt/local-analysis` | fuse.sshfs (autofs) | 932G | 56G | 876G (6%) | auto-mounts on access |

Config source: `/etc/fstab`. Local NTFS disks: `nofail,uid=1000,gid=1000` (ntfs-3g for `/mnt/local-analysis`, ntfs3 for `/mnt/dde`). Remote (WRK-287): NFS `nofail,bg,intr,soft,timeo=50`; sshfs `x-systemd.automount,idle-timeout=60` (unmounts when idle, remounts on first access).

## Checks run

- **Local disks:** `lsblk` + `df -hT` enumerate `sdb1` (`/`, ext4 OS SSD), `sda2` (`/mnt/local-analysis`, ntfs-3g), `sdc2` (`/mnt/dde`, ntfs3). `/mnt/dde` touch+rm probe → writable; `du` confirms 1.6T `documents/` + OrcaFlex/O&G archives.
- **Reachability:** `ping ace-linux-1` OK (192.168.1.100); `getent hosts ace-linux-1` resolves.
- **NFS contents:** `/mnt/remote/ace-linux-1/ace/` lists 53 entries incl. `acma-codes/`, `acma-projects/`, `client_projects/`, `digitalmodel/`, `doris/`, `investments/`, `OGManufacturing/`, `assets.json` (1.2 GB), `capytaine/`, `HAMS/`, `MoorDyn/`, `MoorPy/`, `gmsh/`.
- **NFS writable:** touch+rm probe in share root succeeded → **writable** (rw, sec=sys).
- **sshfs contents:** `/mnt/remote/ace-linux-1/local-analysis/` lists the live ace-linux-1 workspace (workspace-hub, digitalmodel, worldenergydata, assethold, assetutilities, etc.) plus session-summary HTML and agent-worktrees.
- **Latency:** warm `ls` on both shares < 15 ms.
- **Codes/standards corpus present:** `/mnt/remote/ace-linux-1/ace/acma-codes/` resolves and contains ABS / API / ASCE / ASME / ASTM / ANSI / AISC / … vendor-code folders — the off-repo PDF source-of-truth referenced by `.claude/rules/codes-standards-data-routing.md`.

## Caveats / action items

1. **Path divergence — `/mnt/ace` does not exist on ace-linux-2 (low impact, no action needed).**
   On ace-linux-1 the corpus lives at `/mnt/ace/...`; on ace-linux-2 the same data is fully accessible at `/mnt/remote/ace-linux-1/ace/...`. There is no `/mnt/ace` symlink here, and **none is required** — the mount is directly usable.
   - The data is **not blocked**. Anything that takes a path argument, or that you point at the mount, works today.
   - The calc-citation resolver does **not** dereference `/mnt/ace` — it reads wiki pages via `LLM_WIKI_PATH` / `knowledge/wikis/`. The `/mnt/ace/acma-codes/<code>/` in `sources:` frontmatter (`.claude/rules/codes-standards-data-routing.md`) is a **provenance string**, never opened at runtime. No rule is actually broken on this box.
   - The only scenario a symlink helps: running an ace-linux-1-authored script that hardcodes the literal `/mnt/ace/...` string, *unmodified*, on ace-linux-2. ~91 ecosystem files mention `/mnt/ace`, but nearly all are kanban-board prose, not live code paths that execute here.
   **Recommendation: do NOT add the symlink pre-emptively (YAGNI).** If a concrete hardcoded-path script later fails on this host, `sudo ln -s /mnt/remote/ace-linux-1/ace /mnt/ace` is the one-line fix.

2. **NFS share is 95% full (382 GB free of 7.3 TB).** Adequate for read + light write, but not for large CFD output dumps. Heavy CFD artifacts (this is the CFD execution box per `domain:cfd` routing) should land on local disk — **`/mnt/local-analysis`** (885 GB free, ntfs-3g) for active runs, with **`/mnt/dde`** (848 GB free, ntfs3) as overflow/archive — not back onto the NFS share.

3. **soft NFS + sshfs idle-timeout:** long-running jobs that hold open file handles across idle windows can see the sshfs share unmount. For batch lanes reading from the sshfs mount, touch the path at job start or copy inputs to local disk first.

## Cross-references

- Mount provisioning: workspace-hub [#114](https://github.com/vamseeachanta/workspace-hub/issues/114) (SSHFS mounts on ace-linux-1 for ace-linux-2 — closed), WRK-287 fstab entries.
- Machine activation: [#2755](https://github.com/vamseeachanta/workspace-hub/issues/2755) (activate ace-linux-2 provider/machine).
- Prior full probe: `docs/reports/2026-04-27-issue-2519-ace-linux-2-readiness-probe.md`.
- CFD routing: ace-linux-2 is the CFD/OpenFOAM execution box (`domain:cfd`).
