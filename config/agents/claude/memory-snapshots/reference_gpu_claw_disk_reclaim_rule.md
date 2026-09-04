---
name: gpu-claw-disk-reclaim-rule
description: "gpu-claw / is 250 G and fills with decomposed OpenFOAM time dirs; the reclaim rule is keep-last-time-only per case, never touch dm1528 sloshing series"
metadata: 
  node_type: memory
  type: reference
  originSessionId: d40540de-bdf2-4f0d-a52f-ec7d12a1f029
  modified: 2026-09-04T00:45:26.312Z
---

gpu-claw `/dev/sda2` is 250 G total. On 2026-09-03 it sat at 95 % (14 G free) and could not
hold the B1552 free-surface rebuild (~20 G per 7 M-cell interFoam case).

**Reclaim rule that was applied (owner said "aggressively"):** for every case under
`/home/undi/cfd/{b1552/cases,dm1173}`, delete `processor*/<time>/` for every time except `0`
and the **last** written time. Keeps `postProcessing/` (force.dat, surfaces), logs, `0/`,
`constant/`, `system/`, `case_provenance.json`, and restart capability. Verified every
trimmed case had its `force.dat` before deleting. 1 720 dirs, 45 G. Plus `uv cache clean`
(17 G) and `apt-get clean`.

**Do NOT apply the rule to `/home/undi/ws/cfd_work/dm1528`** (sloshing, ~14 G): its
intermediate times are physical time series, not iteration snapshots, and digitalmodel
#1437 (VOF field viz for the sloshing page) is still open against them.

Related: [[dispatch-only-gpu-claw-and-ace-linux-2]], [[project-b1552-netsco-hull-resistance]].
