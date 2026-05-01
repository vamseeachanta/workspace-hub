# Local Performance Tuning — ace-linux-1 / ace-linux-2

**Hardware:** 2× Intel Xeon E5-2630 v3 (Haswell-EP), 16 physical cores / 32 threads, 31 GiB RAM, 2 NUMA nodes.

This runbook captures the tuning applied to `ace-linux-1` on 2026-05-01 and serves as the replication procedure for the identical-spec `ace-linux-2`.

## Findings ranked by impact

A `perf-bench.sh` baseline on 2026-05-01 surfaced the dominant bottleneck — **the workspace filesystem, not the CPU**.

| # | Finding | Evidence | Impact |
|---|---------|----------|--------|
| 1 | `/mnt/local-analysis` is NTFS via FUSE/ntfs-3g (single-threaded driver) | `git status --porcelain` on workspace-hub took **155,707 ms** (2 min 35 s); `mount.ntfs-3g` PID 1336 sustained 21% CPU | Catastrophic — caps Hermes throughput regardless of CPU count |
| 2 | CPU governor was `powersave`/default (cores throttling to ~1.6 GHz) | `lscpu` showed `scaling MHz: 69%` at idle | Moderate — every workload runs ~30% slower than turbo ceiling |
| 3 | Hyper-Threading enabled by default | `lscpu` shows `Thread(s) per core: 2`, 16 cores → 32 threads | Workload-dependent — helps batch parallelism, hurts single-threaded numerical solvers |
| 4 | No NUMA pinning for batch jobs | `lscpu` shows 2 NUMA nodes, no scheduler affinity | Modest — cross-socket QPI traffic for memory-heavy jobs |

## Applied changes (ace-linux-1, 2026-05-01)

### 1. CPU frequency governor → `performance` (persistent)

Created `/etc/systemd/system/cpupower-performance.service` (oneshot, RemainAfterExit=yes) that calls `cpupower frequency-set -g performance` at boot. Result: idle scaling 69% → 89%, all 32 cores honor governor change, Turbo bursts to 3.2 GHz available.

Verify on any host:
```
systemctl is-enabled cpupower-performance.service   # enabled
systemctl is-active cpupower-performance.service    # active
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor | sort -u   # performance
```

### 2. Benchmark harness

`scripts/benchmarks/perf-bench.sh` runs four workloads (single-thread CPU, multi-thread CPU, `git status`, `git log`) and appends results to `scripts/benchmarks/results.tsv` for longitudinal comparison. Pure stdlib Python — no extra deps.

```
scripts/benchmarks/perf-bench.sh baseline
numactl --cpunodebind=0 --membind=0 scripts/benchmarks/perf-bench.sh numa0-pinned
column -t -s $'\t' scripts/benchmarks/results.tsv | tail -20
```

## Next action (2026-05-01) — try the in-kernel `ntfs3` driver

**Recommended next move because it has the highest impact-per-hour ratio:** if `ntfs3` accepts the volume, you get a multi-threaded driver in place of single-threaded FUSE without touching data. If it refuses, you've spent 15 minutes and learned that filesystem migration is the only path forward — either way the answer becomes clear.

**Prerequisites (verify before starting):**
- All shells, editors, and Hermes processes out of `/mnt/local-analysis` (remount requires unmount)
- A `perf-bench.sh` baseline labeled `pre-ntfs3` already in `scripts/benchmarks/results.tsv`
- 30-minute maintenance window — even if the swap succeeds, the workspace is offline during the swap

**Procedure (do not execute without explicit go-ahead):**
```bash
# 1. Confirm kernel module is available
sudo modprobe ntfs3
grep ntfs3 /proc/filesystems   # expect: "       ntfs3"

# 2. Check volume cleanliness (read-only diagnostic, safe)
sudo umount /mnt/local-analysis
sudo ntfsfix --no-action /dev/sdc1   # reports dirty/clean without writing

# 3a. If CLEAN: edit /etc/fstab to swap ntfs-3g → ntfs3, then mount
# (keep a backup of fstab first: sudo cp /etc/fstab /etc/fstab.pre-ntfs3)
sudo mount /mnt/local-analysis
mount | grep local-analysis   # expect: "type ntfs3" not "type fuseblk"

# 3b. If DIRTY: ntfs3 will refuse. Two options:
#     - sudo ntfsfix /dev/sdc1   # writes journal replay, then retry mount
#     - revert fstab and stay on ntfs-3g; escalate to migration plan

# 4. Re-bench and compare
scripts/benchmarks/perf-bench.sh post-ntfs3
column -t -s $'\t' scripts/benchmarks/results.tsv | grep -E "pre-ntfs3|post-ntfs3"
```

**Success criteria:** `git_status` workload drops from ~155 s to under 5 s. `cpu_*` workloads should be unchanged (this isn't a CPU change). If `git_status` is still >10 s, ntfs3 alone is not enough and migration is the only remaining lever.

**Rollback:** `sudo cp /etc/fstab.pre-ntfs3 /etc/fstab && sudo umount /mnt/local-analysis && sudo mount /mnt/local-analysis` returns to ntfs-3g. Data is untouched throughout — both drivers read the same on-disk format.

**Memory caveat (2026-04-27):** ntfs3 refused the Elements drive because it was dirty. `/dev/sdc1` is a different volume, mounted continuously, and likely clean — but `ntfsfix --no-action` is the test of record before swapping the driver.

## Future changes (ranked by effort × impact)

### High impact, high effort (only if ntfs3 trial fails)
- **Migrate `/mnt/local-analysis` from NTFS → ext4 or btrfs.** Will 10–100× small-file IO (which dominates Hermes `git` operations and Python imports). Requires: full backup of `/dev/sdc1` (~232 GB used), reformat, restore. Plan for a maintenance window. Verify backup integrity before destroying NTFS volume.

### Medium impact, low effort
- **NUMA-pin heavy batch jobs.** Prefix compute-heavy commands with `numactl --cpunodebind=0 --membind=0` (or `=1`). Two independent jobs can run socket-pinned and never touch each other's L3 cache or memory controller. Helpful for the overnight 5-terminal batch pattern.
- **Turn off `tracker3` for paths you don't search from GNOME Files.** It's currently scoped sanely (`$HOME` + Downloads, no workspace-hub) but verify per host: `gsettings get org.freedesktop.Tracker3.Miner.Files index-recursive-directories`.

### Workload-specific (BIOS reboot required)
- **Disable Hyper-Threading** *only* if the dominant workload is compute-bound (FEA, OpenFOAM, OrcaFlex solver). For mixed batch (your overnight pattern with 5 parallel terminals), leave HT on — 32 threads at 80% efficiency beats 16 at 100%. Benchmark first with `perf-bench.sh ht-on` before reboot, then `ht-off` after, and compare `cpu_multi` ms.
- **BIOS power profile → "Performance" / "Max Performance"** to lock uncore frequency and memory controller speed.
- **Leave C-states ENABLED** (counter-intuitive). On Haswell-EP, deeper idle on unused cores frees power budget for active cores to Turbo higher.
- **Verify Memory Frequency = Auto / 1866 MT/s** (this CPU's rated max at 1 DPC).

### Low impact, low effort
- Ensure `/swap.img` is unused (currently 0 B — good); confirms no memory pressure.
- Free space on `/` (currently 78% full at 167/229 GB on `/dev/sdb2`); journal/log writes slow as the filesystem fills.

## Replication procedure for ace-linux-2

ace-linux-2 is the identical-spec twin. Apply changes 1 and 2 above:

```bash
# 1. Install persistent governor service (run from workspace-hub root on ace-linux-2)
sudo tee /etc/systemd/system/cpupower-performance.service > /dev/null <<'EOF'
[Unit]
Description=Set CPU frequency governor to performance
Documentation=man:cpupower(1)

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/cpupower frequency-set -g performance
ExecStop=/usr/bin/cpupower frequency-set -g powersave

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable --now cpupower-performance.service

# 2. Run benchmark baseline
scripts/benchmarks/perf-bench.sh baseline-ace-linux-2

# 3. Inspect filesystem of the workspace mount on ace-linux-2 (the most important diagnostic)
mount | grep "$(git rev-parse --show-toplevel | cut -d/ -f1-3)"
# If output shows ntfs/ntfs-3g/fuseblk: same bottleneck as ace-linux-1. Plan migration.
# If output shows ext4/xfs/btrfs: the headline finding does not apply — focus elsewhere.

# 4. Compare results across hosts
column -t -s $'\t' scripts/benchmarks/results.tsv
```

## Post-tuning verification checklist
- [ ] `systemctl is-enabled cpupower-performance.service` → `enabled`
- [ ] All cores show `performance`: `cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor | sort -u`
- [ ] `lscpu | grep "scaling MHz"` shows >80% under load
- [ ] `perf-bench.sh` results saved with hostname + governor label
- [ ] Filesystem of workspace root identified and recorded
