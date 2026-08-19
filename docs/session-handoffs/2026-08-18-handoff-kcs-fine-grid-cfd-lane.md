# Session handoff — KCS fine-grid CFD lane (digitalmodel#1173)

> **Date:** 2026-08-18
> **Machine:** ace-linux-1 is the CONTROL SURFACE. All compute is on gpu-claw.
> **Owns:** one long-running solve and the scoring that follows it.
> **Does NOT own:** four items blocked on the owner — listed under Out of scope.

---

## Entry prompt for the next session

```
You own the KCS fine-grid CFD lane for digitalmodel#1173. A ~34-hour solve is
running detached on gpu-claw. Your job is to let it finish, score it, and
report -- not to restart or retune it.

Preflight (all read-only):
  ssh gpu-claw-ts 'D=~/cfd/dm1173/kcs_cases/kcs_fine;
    grep -c "^Time = " $D/log.interFoam;      # iterations so far, of 25000
    grep ClockTime $D/log.interFoam | tail -1;
    tail -2 $D/PROGRESS;
    ls $D/detached_run.terminated.json 2>/dev/null || echo "no kill marker"'

  <workspace-hub>/scripts/fleet/lane-sweep.sh

Read digitalmodel#1173 comments dated 2026-08-14 through 2026-08-18 before
touching anything. The half-domain correction comment is load-bearing.

Do NOT poll by process name. `pgrep -f "<pattern>"` matches the ssh command
line carrying it; one waiter ran 13.5 hours past its job that way. Poll the
marker files named below.
```

---

## State at handoff

| item | value |
|---|---|
| case | `~/cfd/dm1173/kcs_cases/kcs_fine` on **gpu-claw** (reach as `ssh gpu-claw-ts`) |
| cells | **4,330,961** — `Mesh OK`, zero failed checks, max skewness 3.021 |
| launched | 2026-08-18T02:22:55Z, pid 3946889, 8 ranks, budget 120 h |
| progress | 7,128 / 25,000 iterations at 84,361 s → **11.83 s/iter** |
| stop rule | `runTimeControl` on `Cd`, `nIterStartUp 9000`, `window 4000`, `tolerance 4e-5` |
| branch | `feat/1173-calm-water-hull-resistance` @ `dfce1b58`, clean, pushed |

**Projection at the measured rate:** earliest stop (9,000 iters) ≈ 29.6 h total;
production analogue (13,000) ≈ 42.7 h; backstop (25,000) ≈ 82 h.

`plain gpu-claw` in `~/.ssh/config` points at a dead LAN IP. **Always `gpu-claw-ts`.**

---

## Why this run exists

Three levels now exist, at a near-perfect grid family:

```
companion    546,978 -> production 1,539,965   ratio 2.8154  linear 1.4119
production 1,539,965 -> fine      4,330,961   ratio 2.8123  linear 1.4118
```

Two grids give a difference and force you to *assume* an order of accuracy.
Three at a consistent ratio give the **observed** order, which is what ITTC's
uncertainty procedure is built on. That is the entire point of this run.

Production's result (half-domain doubling applied):

| | computed | reference | error | tolerance | verdict |
|---|---|---|---|---|---|
| V1 C_t | 7.61086e-3 | 3.56e-3 | +113.79% | ±3.00% | FAIL |
| V2a C_p | 7.74168e-4 | 7.27955e-4 | **+6.35%** | −15%/+6% | FAIL, marginal |
| V2b C_v | 6.83667e-3 | 2.832045e-3 | +141.40% | ±5% | FAIL |

Pressure is nearly right; friction is 2.4× the ITTC line. Mechanism is
wall-function misapplication — y+ max 1075.67 against a function valid to ~300.
Expect the fine grid to fail too. **A failed gate is a result**; that decision
was recorded before any number existed and must not be renegotiated now.

---

## How to read the outcome — four possibilities

| outcome | marker |
|---|---|
| **converged early** | `SOLVE PHASE COMPLETE` in `PROGRESS` with iterations < 25000 |
| **ran to backstop** | same marker at exactly 25000 |
| **solver failure** | `FATAL` in `PROGRESS` / non-zero rc in `driver.log` |
| **budget kill** | `detached_run.terminated.json` exists (120 h poller) |

Silence in all four means still running. Confirm with the lane sweep, never
with a `pgrep` pattern you also typed into the ssh command.

---

## Scoring, once it finishes

```
scripts/cfd/generate-kcs-verification.py --production <case> --companion <case>
```

Copy the case directories back first — the cases live on the host, the repo does
not. Preserve `postProcessing/`, `log.interFoam`, `log.checkMesh`, `PROGRESS`,
`TIMING.csv`. A re-solve is ~34 h.

**Use the script. Do not hand-compute from `force.dat`.** The domain is cut at
the centreplane (`midPlane`, `symmetryPlane`; bounding box y ∈ [−23.28, 0]), so
`force.dat` carries **half** the body force while published wetted areas are
full-hull. `ship_resistance.py:836` applies `factor = 2.0`. Bypassing it with
awk cost a full day on this issue and silently halved every coefficient.

The fine case's `forceCoeffs1` uses `Aref 4.71895` — half the published S —
precisely so its `Cd` equals the true full-hull `C_t` with no mental arithmetic.

For y+ afterwards: `mpirun -np 8 interFoam -postProcess -func yPlus -parallel
-latestTime`. **Bare `postProcess` does not construct the turbulence model** —
it writes zeros and exits 0.

---

## Decisions that must not be quietly reversed

1. **Gates stay as fixed.** V1 ±3%, V2a −15%/+6%, V2b ±5%, V3 ≤1.5%, all set
   against published values before any result existed.
2. **Normalisation is the published S = 9.4379 m²**, never the mesh-derived
   9.5609. Asserted in code at `ship_resistance.py:862`.
3. **LTS parameters must not differ between grid levels.** LTS violates temporal
   conservation, so changing `maxCo`/`maxAlphaCo` moves the answer, not the path.
   Every held-constant file was verified byte-identical when `kcs_fine` was built.
4. **checkMesh verdict is read from the OUTPUT TEXT, not the exit code** —
   checkMesh returns 0 while reporting failures. Held twice under pressure.
5. **Wu (2025) is not condition-matched** (with rudder, different Re and wetted
   area). Usable for convergence behaviour and timing only, never error-vs-EFD.

---

## Traps specific to this environment

- `.venv` has **no pytest**. Use `uv run --with-editable '.[test]' python -m pytest`.
  `addopts` carries `-v`, which overrides `-q`; override addopts when you need
  terse node IDs.
- On a **standalone clone**, that command aborts before collection —
  `pyproject.toml:386` pins `assetutilities` to `../assetutilities`. Add
  `--no-sources`.
- `uv run` dirties `uv.lock`. Restore it before committing; auto-sync will
  otherwise commit 390 lines of churn onto your branch (it did, once).
- ace-linux-1's root filesystem is tight (~23 G). **No worktrees.** Commit with
  the pathspec form `git commit -m "..." -- <paths>`; an untracked `.worktrees/`
  exists and must never be staged.
- After any push, verify on the remote: `git log --oneline -2 origin/<branch>`.
  A lane reported "pushed" while its commit sat on a different local branch.

---

## Out of scope — blocked on the owner, do not action

1. **Public leak** — 53 files under `docs/domains/orcaflex/` on the PUBLIC
   digitalmodel repo carry a named operator's tenant, two GoM assets, client
   project and vessel names, and the org machine identifier. Sanitizer regex at
   `scripts/sanitize_s7_models.py:163` matches **zero** real headers, and
   `SANITIZATION_MAP` is a 57-entry cleartext re-identification key.
   Deliberately **unfiled** — a public issue signposts it. Needs a disclosure
   route and a remediate-first-or-file-first call from the owner.
2. **#2020** is `status:plan-approved` but cannot start: Stage 1 needs a lawfully
   obtained Holtrop & Mennen primary paper, and there is no fallback oracle by
   design.
3. **14 G** of stale scratch under `/tmp/claude-1000/-mnt-local-analysis` on
   ace-linux-1 (18 G already reclaimed). The permission classifier blocks agent
   deletion.
4. **Follow-ons filed, not started:** #2021 (bounding/boundingBox divergence
   marker), #2022 (Froude sweep), #1992, #2008.

---

## Reference

- Live record: digitalmodel#1173, comments 2026-08-14 → 2026-08-18.
- Wiki (generic sibling): `wikis/naval-architecture/wiki/concepts/openfoam-ship-resistance-performance.md`
  and `.../cfd-iterative-convergence-criteria.md` — measured scaling, cells-per-core,
  GPU viability, ITTC convergence criteria with citations.
- Lane tracking: `scripts/fleet/lane-sweep.sh` + `~/.claude/fleet-lanes.tsv`.
