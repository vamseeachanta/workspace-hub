# Session handoff — KCS resistance validation, learnings, and client-hull onboarding

> **Date:** 2026-08-20
> **Machines:** ace-linux-1 = CONTROL SURFACE only. Compute on gpu-claw. ace-linux-2 available.
> **Issue:** digitalmodel#1173 · branch `feat/1173-calm-water-hull-resistance`

---

## Entry prompt for the next session

```
Continue digitalmodel#1173. The validation setup had a root-cause defect that is
now FIXED; the remaining error is 5.6-8.7%, which is ordinary CFD discrepancy
rather than a broken setup. A fine-grid run is live on gpu-claw.

Preflight (read-only):
  ssh gpu-claw-ts 'D=~/cfd/dm1173/kcs_cases/kcs_fine;
    grep -c "^Time = " $D/log.interFoam;
    tail -3 $D/ittc_watch.log;
    ls $D/ITTC_CONVERGED 2>/dev/null || echo "not converged yet"'
  <workspace-hub>/scripts/fleet/lane-sweep.sh

Read digitalmodel#1173 comments from 2026-08-19 onward BEFORE touching anything.
Do NOT poll a remote lane by process name; poll marker files.
```

---

## THE RESULT

Force integration, not the flow solution, was the dominant error.

`forces` was configured `rho rhoInf; rhoInf 998.8;`, applying WATER density to the
whole hull patch — including the part above the waterline.

| | |
|---|---|
| hull patch total (half domain) | 9.4216 m² |
| submerged | 4.8601 m² (51.6%) |
| **above the waterline** | **4.5615 m² (48.4%)** |
| dry topsides' share of reported viscous force | **62.3%** |

Switching to `rho rho` (the VOF density field) on the **same solution**:

| | before | after | gate | verdict |
|---|---|---|---|---|
| V1 C_t | +113.79% | **−5.65%** | ±3% | FAIL |
| V2a C_p | +6.35% | **+6.22%** | −15%/+6% | FAIL (marginal, 0.22 pt) |
| V2b C_v | +141.40% | **−8.70%** | ±5% | FAIL |
| V3 grid | 117% | **+5.58%** | ≤1.5% | FAIL |

Committed: `fae239bd` (fix + guards), `f20634e2` (evidence + two scorer defects),
`5ac1de34` (engineering report). Evidence at
`docs/api/cfd/kcs-calm-water-resistance-verification.{json,html}`.

---

## LEARNINGS TO CARRY INTO CLIENT WORK

These are the point of the exercise. Every one cost real time to find.

### CFD / method

1. **VOF force integration must use the density FIELD.** `rho rho`, never a constant
   `rhoInf`, wherever a patch crosses the waterline. Now fixed in the ship_resistance
   template with a guard test sweeping EVERY VOF template.
2. **Half-domain force is HALF the body force**, while published wetted areas are
   full-hull. `ship_resistance.py:836` applies `factor = 2.0`. Never hand-compute from
   `force.dat`.
3. **The referent is a TUPLE**, not a number: (attitude, appendage, normalising area,
   ν/Re). A bare C_t cannot be gated at any tolerance. Two KCS lineages exist and a
   test asserts they share NO field.
4. **y+ is not the dominant error term.** Korkmaz et al. measured C_F sensitivity to
   average y+ at 2%; Wu (2025) succeeds with 3 prism layers at average y+ 155. Three
   days were spent on this hypothesis before the literature refuted it.
5. **Grid refinement was never the lever** — no normalised column improved
   monotonically with mesh size; the medium grid beat both neighbours.
6. **Cost scales as ~N^1.27, not N.** Refinement estimates on linear scaling
   underestimate by ~30%.
7. **Cells-per-core sweet spot is 50–100K** — most small-cluster cases are UNDER-
   decomposed. But measured: doubling ranks on a 2-socket Xeon bought 6.4%, so
   benchmark rather than assume.
8. **A scatter-based convergence stop cannot detect a drifting mean.** OpenFOAM's
   `runTimeControl average` compares INSTANTANEOUS to running mean; it stopped a run
   at iteration 9,011 with the mean still descending 35%. Use the ITTC window-mean
   criterion (7.5-03-01-01 §4.1, U_I = ½(S_U − S_L)).
9. **`mapFields` prolongation is ITTC-endorsed** (§4.1) and is why r = √2 is chosen.
   Do NOT re-run `setFields` afterwards — it flattens the mapped wave field.
10. **GPUs are not the answer for VOF.** OpenCFD's own developers measured 0.4×–7.7×
    against a 32-core socket on SIMPLER solvers; no published OpenFOAM VOF GPU
    benchmark exists; consumer cards are FP64-crippled.

### Process — the pattern behind almost every defect

**A name that does not match the property.** Each was correct when written and broke
silently when conditions changed. None errored; all produced plausible numbers.

- `window` said iterations, counted rows — equivalent only at writeInterval 1
- `forces` meant one of several disagreeing directories
- `rho rhoInf` said density, applied water to air
- a test ASSERTED the defect (`rho rhoInf` pinned as "explicit")
- `coefficient.dat` was the DEAD run; OpenFOAM versions to `coefficient_0.dat`
- `pgrep -f X` matches the ssh command carrying X (one waiter ran 13.5 h past its job)

**Corollaries, learned the expensive way:**

- **Never hand-compute alongside a pipeline that computes it.** Three instances: the
  half-domain factor, the window semantics, the coarse-grid C_t. Every time the
  pipeline was right.
- **When a measurement is wrong by >2×, ask "who has done this correctly and what did
  they do differently?" BEFORE generating hypotheses.** The refuting papers had been
  downloaded three days earlier and mined for iteration counts.
- **Sample the trend, never a single value.** Three separate misreadings of an
  instantaneous value as a state.

---

## LIVE NOW

| lane | host | state |
|---|---|---|
| `kcs_fine` re-run | gpu-claw | ~460/25,000 iters, mapped IC from the converged medium grid |
| ITTC watcher | gpu-claw | ARMED — window 1500×5, spread ≤0.60%, drift ≤0.35%, hold 3, min 6,000 iters |

Stop mechanism: watcher creates `<case>/ITTC_CONVERGED`; the `abort` function object
sees it and stops with `writeNow`. `endTime 25000` is the hard cap.

**Run interFoam via `<case>/runsolve.sh`, NOT `stage45_driver.sh`** — the driver
re-runs `restore0Dir`/`setFields` before solving, which would destroy the mapped
initial field. It was skipped last time only because `runApplication` refuses to
repeat a stage whose log exists. That is an accident, not a guarantee.

---

## CLIENT-HULL ONBOARDING — blocked, and one decision needed first

**Target:** project B1552 hull model, for resistance analysis.

**Access established (my stored note was STALE and said otherwise — verify, don't trust):**

```
host    mkt-a-HOU-RDS02   tailnet 100.93.182.24   domain mkt-a-INC.LOCAL
user    vamseea          (also Administrator)    SSH: WORKS
drives  C:  D: (Data)  S: (VM storage)           <- NO J:
```

**Blocked on:** the UNC path behind `J:`. Mapped network drives are established at
interactive logon and do not carry into SSH; `net use` is empty, `HKCU\Network` has no
persistent mapping, and GPO drive-map preferences returned nothing. `net view` against
the domain namespace timed out.

**What to ask the owner for:** the `\\server\share` behind `J:` — one `net use` in an
interactive session on that box prints it.

**Layout learned:** projects live at `D:\<code>`. `D:\B1546` exists and holds
`V-Rigs (AQWA Model Archive).wbpj` — an AQWA Workbench project. B1552 is NOT on local
disk.

### The routing decision that must precede the copy

The owner asked to sync the model into `llm-wiki-mkt-a`. That repo is **PRIVATE**
(verified), which is the correct tier for client content per
`.claude/rules/wiki-sibling-routing.md` (`visibility: private-client-llm-wiki`,
`client:` required).

**But `/mnt/ace` is a public SMB share** (memory: `reference_mnt_ace_is_public_smb_share`
— 777, NFS-rw, `guest ok = yes`, browseable). A private git repo whose working copy sits
on a guest-readable share is private in GitHub and public on the LAN. This needs an
explicit decision before client geometry lands, not after.

**This is not hypothetical.** Task #3 on the board is an unresolved leak of exactly this
class: 53 files on the PUBLIC digitalmodel repo carrying a named operator's tenant, two
GoM assets, client project and vessel names, and the org machine identifier — because
client material entered a public repo without a handling decision.

---

## OPEN — owner decisions

1. **Public-leak disclosure route** (oldest, most consequential). Needs (a) disclosure
   route, (b) remediate-first or file-first. Deliberately unfiled — a public issue
   signposts it.
2. **J: UNC path**, to unblock B1552.
3. **Client-data handling** for CFD case files, meshes and reports — the wiki rule
   covers documents, not solver cases.
4. **Holtrop & Mennen primary papers** — #2020 is `status:plan-approved` but cannot
   start without an admissible source.
5. **14 GB stale scratch** on ace-linux-1 (`rm -rf /tmp/claude-1000/-mnt-local-analysis`;
   the classifier blocks agent deletion).

## Report review — 8 items decided, applied, not yet republished

D1 coarse C_t corrected (was wrong: hand-computed 3.55712e-03 vs manifest 3.54638e-03) ·
D2 V2a FAIL annotated marginal · D3 three averaging windows reconciled · D4 V2b stays a
gate with Re-dependence disclosed · D5 fine-grid re-run running · D6 wetted-area bias
+1.30% INFLATES C_t, de-biased −6.86% stated beside −5.65% · D7 y+ logs copied into the
manifest · D8 handling banner above the fold and restated in Results.

Report: `docs/reports/2026-08-19-calc-AE-CFD-1173-kcs-hull-resistance.html`
Artifact: https://claude.ai/code/artifact/21f5d62f-ab04-43c3-aa5b-a1f8f5bd9843
