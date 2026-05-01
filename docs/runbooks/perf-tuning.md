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

## Future changes (ranked by effort × impact)

### High impact, high effort
- **Migrate `/mnt/local-analysis` from NTFS → ext4 or btrfs.** This is the #1 win and will easily 10–100× small-file IO (which dominates Hermes `git` operations and Python imports). Requires: full backup of `/dev/sdc1` (~232 GB used), reformat, restore. Plan for a maintenance window. Verify backup integrity before destroying NTFS volume.
- **Interim mitigation:** Try the in-kernel `ntfs3` driver — it's multi-threaded. Check with `modprobe ntfs3 && grep ntfs3 /proc/filesystems`. Then change fstab `ntfs-3g` → `ntfs3` and remount. Memory note (2026-04-27) flags ntfs3 as refusing dirty volumes; verify clean state with `ntfsfix --no-action` first.

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
