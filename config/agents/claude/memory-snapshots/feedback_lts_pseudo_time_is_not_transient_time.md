---
name: lts-pseudo-time-is-not-transient-time
description: A Courant/dissipation finding from a transient (Euler) tank does NOT transfer to a localEuler (LTS) steady run — the converged LTS state is dt-independent and tight Co caps only starve pseudo-convection; cost 10× iteration budget on B1552 Stage 4
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d40540de-bdf2-4f0d-a52f-ec7d12a1f029
  modified: 2026-09-04T09:10:43.985Z
---

On 2026-09-03/04 a 2D Euler wave tank on the hull's own refinement ladder measured that wave
retention is first-order in Courant number (0.55/0.72/0.86/0.94 at Co 2/0.5/0.2/0.05). I
transferred that into the hull case as `maxCo 0.5 / maxAlphaCo 0.2` under `localEuler`. The
Wigley-vs-B1552 side-by-side (S1) then showed the consequence: at 5/2 the converged Wigley
reference accumulated ≈40 hull-lengths of pseudo-convection in 5000 iterations; at 0.5/0.2 the
hull case would accumulate 1.8–3.6 L in 8000 — the settling gate was unreachable. Both
converged LTS references (Wigley, parent `fs_G04_best` for 10 000 its) ran 5/2 with
`nOuterCorrectors 2`.

**Why:** under LTS each cell marches at its own pseudo-Δt; the transient dissipation the tank
measured is a property of time-accurate propagation, but the LTS steady state is independent
of the local Δt (FS-CFD §7 literature; DTCHull tutorial). Tight caps only shrink the
pseudo-time advanced per iteration and amplify `rDeltaT` at bad cells.

**How to apply:**
- Never set LTS `maxCo/maxAlphaCo` from a transient-tank Courant study; take them from a
  converged LTS reference of the same recipe (5/2 for the DTCHull lineage) and budget
  iterations in hull-lengths of pseudo-convection (`maxAlphaCo·dx/U` per iteration).
- Use a transient tank to rank SPATIAL levers (cells/λ, ladder extent, schemes) — those do
  transfer; report its Courant column as "transient only".
- Companion lessons from the same night: a source term stable under Euler Δt 5 ms is not
  stable under LTS Δt 1 s (explicit part needs f·Δt_local < 1, dm#2046); `fieldMinMax` on
  `V` from `writeCellVolumes` reads patch faces (zeros) — gate cell volumes with
  `volFieldValue min`; refinement-box z-edges in thin-dz blocks give hanging-node faces at
  atan(0.354·dx_c/dz) — 86° at 22.8 m/dz 0.56 (dm#2047).
- Related: [[never-edit-a-running-shell-script]], [[mechanism-before-publication]].
