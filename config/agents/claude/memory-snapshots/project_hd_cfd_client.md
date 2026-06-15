---
name: project-hd-cfd-client
description: "Howard Day (HD) is a paying client; active automotive CFD job (T1 Suzuka aero) tracked at digitalmodel#630"
metadata: 
  node_type: memory
  type: project
  originSessionId: 980c06c6-7a70-4602-bfbc-32addeb44f9a
---

Howard Day ("HD", emails from `howardday7777@gmail.com` and work `rigsystemsandequipment.sme@gmail.com`, US cell 281-216-8235 / OZ 0426-280-533) is a **paying client**. Prior job: drag-race car chute-frame structural analysis (Mar 2026, $125/hr, NDAs signed Feb 2026). Current ask: **automotive external-aero CFD** on `T1 Suzuka Aero.zip` (Google Drive).

- HD is OK **offshoring the scope to the India team under the existing NDA**.
- He may buy a **3D scanner** for additional geometry data if needed.
- Tracked at [digitalmodel#630](https://github.com/vamseeachanta/digitalmodel/issues/630); Gmail reply drafted 2026-05-28 (interim, promising a feasibility verdict "early next week").

**Why:** Live revenue opportunity while user is consulting/job-hunting; HD nudged twice (last 2026-05-25) waiting on an informed "can we run this in CFD?" answer.

**How to apply:** Our OpenFOAM stack (`digitalmodel/src/digitalmodel/solvers/openfoam/`) is **marine/seakeeping-oriented** — automotive external aero (simpleFoam, MRF wheels, road BC) is a different workflow; don't assume drop-in. Give HD a grounded verdict only after inspecting the actual geometry. Related: [[project-lng-a-demo]].

**Status 2026-05-28:** Feasibility DONE (verdict can-do-with-additional-data; `T1.zip` is photos + bracket IGES + downforce spreadsheets, no watertight car/wing surface). Memo on pushed branch `digitalmodel:docs/hd-cfd-and-lng-a-demo`. NDA data in `.scratch/` protected via `.git/info/exclude`. Execution (build automotive external-aero OpenFOAM case) BLOCKED until HD sends scanned geometry + answers the 3 scoping questions.

**Geometry load-test (2026-05-28, empirical):** all 11 IGES load cleanly via gmsh/OpenCASCADE but **every file has 0 solids** — 10 are mounting hardware (≤509 mm: brackets/posts/spacers/clevis/pedestals), and the only wing-named file (`Ver2 Wing lower mount location.igs`, 7919 mm) is **wireframe-only (0 surfaces)** holding a 2-D car side-profile + mount curves. Hardens the verdict: no aero surface exists. Tunnel data in spreadsheets = the validation target (`Stock and drag wing aero details.xlsx`: CD 0.25–0.28, CLF/CLR per config; `Speed vs DF.xls`: S_front 2.268 m², CLr 0.53@15°). Self-contained **investigation HTML** (all 95 client photos + 9 CAD renders + scale chart + CFD-workflow plan) at `digitalmodel/.scratch/hd-t1-suzuka/HD-T1-Suzuka-CFD-investigation.html` (gitignored, NDA-safe; view via `python -m http.server` — Chrome ext can't open `file://`).

**Email state (2026-05-29):** user SENT only the **interim/holding reply** (msg `19e715c72a6c123e`: "going through it now, verdict early next week", asks objectives). ⚠️ The full geometry-gap verdict (draft `19e6f5054b5ff418`: brackets-not-surface + scanner fidelity spec + 3 Qs + India/NDA-yes) is **still UNSENT and now CONTRADICTS the holding reply** ("went through it properly") — must be REFRAMED as the promised follow-up, NOT sent verbatim. Holding reply also left HD's direct "India under NDA — can do?" unconfirmed and asked only 1 of 3 scoping Qs (objectives; still owed: speed/yaw/ride-height envelope + geometry finality).
