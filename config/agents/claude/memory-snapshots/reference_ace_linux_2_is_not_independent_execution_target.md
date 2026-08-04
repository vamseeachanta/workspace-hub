---
name: reference_ace_linux_2_is_not_independent_execution_target
description: "ace-linux-2's /mnt/ace is an NFS re-export of ace-linux-1's disk — dispatching /mnt/ace repo work there buys latency, not parallelism"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 3b006eae-10ef-4664-8b7a-316d95790cce
  modified: 2026-08-04T06:49:42.061Z
---

**`ace-linux-2` is NOT an independent execution target for anything under
`/mnt/ace`.** Its `/mnt/ace` is ace-linux-1's disk over NFS.

Measured directly 2026-08-04 from ace-linux-1:

```
ace-linux-2:  ace-linux-1:/mnt/ace   nfs4   /mnt/remote/ace-linux-1/ace
              stat /mnt/ace/ws/aceengineer-website → inode=129499145 dev=75
ace-linux-1:  /dev/sda1              ext4   /mnt/ace
              stat /mnt/ace/ws/aceengineer-website → inode=129499145 dev=2049
```

Identical inode, different device IDs — same tree, one disk, two views.

**Consequences for dispatch:**

- Routing `/mnt/ace` repo work to ace-linux-2 buys **NFS latency, not
  parallelism**. The CPU is separate; the filesystem is not.
- Any build that writes into the tree (`node_modules/`, `dist/`, `.venv/`,
  pytest caches) writes into the **shared checkout** and can collide with
  ace-linux-1 work or another agent's worktree.
- Two agents "on different machines" against `/mnt/ace` are still one
  filesystem — the git index lock and sweep-contamination hazards apply exactly
  as if they were the same box. See
  [[feedback_multi_agent_commit_serialization]].

**When ace-linux-2 IS still useful:** work with its own local storage, work that
does not touch `/mnt/ace`, or CPU-bound jobs whose inputs and outputs are staged
onto local disk first. Note dm [#1495] exists specifically to offload CFD *off*
ace-linux-2 onto gpu-claw.

Host as observed 2026-08-04: reachable via `ssh ace-linux-2` (tailnet,
BatchMode, no prompt), `Linux 7.0.0-28-generic`, node `v24.18.0`, npm `11.16.0`,
near-idle (load ~0.2). Headless VNC on `:1`/5901 per
[[reference_ace_linux_2_headless_vnc]].

See [[reference_ecosystem_migrated_to_ext4_mnt_ace_ws]],
[[project_fleet_reachability_and_solver_access_2026_07_31]].
