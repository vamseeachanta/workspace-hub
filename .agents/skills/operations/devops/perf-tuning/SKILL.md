---
name: perf-tuning
description: Diagnose local machine slowness and apply CPU/IO/governor tuning. Use when work feels slow on ace-linux-1 / ace-linux-2 — Hermes lagging, git operations taking minutes, builds dragging, Codex feeling sluggish. Runs perf-bench.sh, identifies the dominant bottleneck (CPU governor, filesystem driver, NUMA, memory pressure, I/O contention), and applies fixes from the perf-tuning runbook.
---

# Performance Tuning

When the user complains about slowness ("Hermes is slow", "work is lagging", "builds are crawling", "everything feels sluggish"), do not guess. Diagnose, then act.

## Mental model

The most common failure mode is assuming "slow" means "CPU-bound". On these 32-thread Xeon boxes, CPU is rarely the bottleneck. The usual suspects in order:

1. **Filesystem driver** (NTFS/ntfs-3g via FUSE on `/mnt/local-analysis` is single-threaded and serializes IO across all 32 cores)
2. **CPU frequency governor** (`powersave` default keeps cores at ~1.6 GHz)
3. **Background indexers** (`tracker-miner-fs-3`, `baloo`, `mlocate.updatedb`)
4. **Memory pressure / swap** (rare on 31 GiB box, but check)
5. **Network mounts** (sshfs, NFS — slow when remote host is unreachable)
6. **Genuinely CPU-bound** (only after eliminating the above)

## Diagnostic order (5 minutes total)

Run these in order. Stop as soon as you find a clear answer.

### 1. System pulse
```bash
uptime           # load avg vs nproc — if load << threads, CPU is NOT the bottleneck
free -h          # check available memory and swap usage
ps -eo pid,user,pcpu,pmem,etime,comm --sort=-pcpu | head -10
```

### 2. Filesystem of the working directory (the most-missed diagnostic)
```bash
mount | grep "$(git rev-parse --show-toplevel | cut -d/ -f1-3)"
```
If the line contains `ntfs`, `ntfs-3g`, or `fuseblk` → **this is the bottleneck**. No further CPU diagnosis needed; route to runbook section "Migrate /mnt/local-analysis from NTFS".

### 3. Governor state
```bash
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
lscpu | grep "scaling MHz"
```
If governor is not `performance` or scaling is <80%, install the cpupower service from the runbook.

### 4. Background indexer noise
```bash
ps -eo pcpu,comm --sort=-pcpu | grep -E "tracker|baloo|updatedb|spotlight" | head
```

### 5. Run the benchmark for hard numbers
```bash
scripts/benchmarks/perf-bench.sh diag-$(date +%s)
column -t -s $'\t' scripts/benchmarks/results.tsv | tail -10
```
**Reference numbers on ace-linux-1 (governor=performance, NTFS-3G workspace):**
- `cpu_single` ~500 ms — anything >800 ms means CPU contention
- `cpu_multi` ~1400 ms — should be close to `cpu_single` on a dedicated box; >3× means IO/scheduling contention
- `git_status` was 155,707 ms with NTFS-3G — anything >2 s is a filesystem-driver smell
- `git_log` ~50 ms — should always be fast (cached)

If `git_status` is in the seconds, suspect IO contention. If in the minutes, suspect filesystem driver.

## Fixes (apply via the runbook)

The runbook at `docs/runbooks/perf-tuning.md` is the canonical procedure. This skill's job is to **reach the right runbook section quickly**:

| Symptom | Runbook section |
|---------|-----------------|
| `git status` >5 s on workspace-hub | "Migrate /mnt/local-analysis from NTFS" + interim ntfs3 mitigation |
| Idle scaling MHz <80% | "CPU frequency governor → performance (persistent)" |
| Cross-socket memory thrashing on heavy job | "NUMA-pin heavy batch jobs" |
| Compute-bound solver (FEA/CFD) under-performing | "Disable Hyper-Threading" + benchmark |
| `tracker-miner-fs-3` >20% sustained | "Turn off tracker3 for paths you don't search" |

## Anti-patterns to avoid

- **Don't reach for BIOS toggles before running the benchmark.** HT-off blindly can hurt the overnight 5-terminal batch pattern. Numbers first.
- **Don't recommend `tracker reset --hard`** without checking `tracker3 status` first — on ace-linux-1 it's idle and indexes only `$HOME` (not workspace-hub). Resetting it would just re-index later.
- **Don't remount the live workspace filesystem** (`umount /mnt/local-analysis`) while the user has a shell or editor in it. Plan filesystem changes for a maintenance window.
- **Don't skip the "filesystem of the working directory" check.** This is the diagnostic most likely to surface a 100× win and the one most often missed.

## Persisting findings

After diagnosis, append a row to `scripts/benchmarks/results.tsv` with a meaningful label so the next session can compare. Memorable labels: `pre-{change}`, `post-{change}`, `diag-{date}`.

If you discover a new bottleneck class not in the runbook, propose an addition rather than fixing in-place. The runbook is the durable artifact; this skill is the routing layer.
