---
name: cfd-execution-box
description: Current dedicated CFD execution node and routing evidence
type: project-memory
---

CFD/OpenFOAM execution should route to `gpu-claw`, not `ace-linux-2`.

Evidence from [digitalmodel #1495](https://github.com/vamseeachanta/digitalmodel/issues/1495) on 2026-07-09:
- Provisioned `gpu-claw` from `ace-linux-1` over the WireGuard VPN.
- Installed OpenFOAM ESI v2312 package `2312.260127-2`, matching the ace-linux-2 baseline build.
- Installed OpenMPI `4.1.6`, `rclone`, `gh`, `uv`, and `digitalmodel`.
- `scripts/setup/verify-cfd-box.sh` passed toolchain and tiny serial/2-rank MPI smoke.
- Matched 216k-cell 3D benchmark manifest landed in [digitalmodel PR #1500](https://github.com/vamseeachanta/digitalmodel/pull/1500).

Benchmark comparison:
- `gpu-claw` best valid row: `0.5899 s/step @ np=8`.
- ace-linux-2 best baseline row: `0.9686 s/step @ np=16`.
- `gpu-claw` is 1.64x faster at each box's own best row and avoids ace-linux-2 shared-load contention.

Caveat:
- `gpu-claw` currently exposes 8 CPUs (`nproc=8`) even though the CPU model string reports a Threadripper PRO 3955WX. Treat `np=16` on the current manifest as oversubscribed evidence, not valid scaling capacity.

Operational routing:
- `.claude/memory/kanban/routing-rules.yaml` maps `domain:cfd` to `machine:cfd-dedicated`.
- `machine:cfd-dedicated` has hostname `gpu-claw`.
- Heavy production sweeps should run on `gpu-claw`; ace-linux-2 should remain available for shared interactive/dev work.
