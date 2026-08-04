---
name: feedback_patch_script_masks_unrunnable_generator_output
description: A manual patch step between a generator and its solver invalidates every claim that the generator emits runnable input — check for one before trusting past evidence
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 3b006eae-10ef-4664-8b7a-316d95790cce
  modified: 2026-08-04T06:43:34.686Z
---

When a generator emits a solver case and a human-authored patch script runs
between emission and execution, **every prior "the generator works" claim is
void** — the evidence was produced from the patched tree, not the emitted one.

Found 2026-08-04 on digitalmodel [#1528] (gpu-claw, OpenFOAM ESI v2312). The
builder's `fvSolution` is not `interFoam`-runnable: `alpha.water` is lumped into a
turbulence regex group, `p_rgh`/`p_rghFinal` are absent, and there is no `PIMPLE`
block. `interFoam` dies at start-up with `Entry 'cAlpha' not found`. The reason
nobody had noticed: `~/ws/cfd_work/dm1528/patch_case.sh` overwrites **nine**
generated files before the solver ever sees them. So the earlier slice-7 CFD
evidence on #1528 was never produced from the emitted tree at all. Filed as
[#1959]; blocks the 144-case matrix.

**Why:** a patch script is invisible in the artifact. The case directory that ran
looks like the case directory the generator produced, the run succeeded, and the
results are real — they just do not certify the code under test. Same shape as
[[feedback_metric_moved_work_did_not_happen]] and
[[feedback_absence_of_signal_reads_as_success]]: the correlated signal moved
while the thing being claimed never happened.

**How to apply:** before trusting any "generator produces runnable input" claim,
`ls` the run directory for wrapper/patch/fixup scripts and diff the emitted tree
against what actually executed. If a patch exists, the generator is unvalidated
until either the patch is empty or its content is folded back into the generator.
State the gap rather than inheriting the prior claim. Corollary for dispatch: a
dry-run `rc=0` proves rendering, not running — always drive at least one real
solver start before reporting a case pipeline as working.

## Two gpu-claw launch traps from the same session

- **Bracketed `pgrep` still self-matches** if your own `echo`/command text
  contains the solver name. `pgrep -f '[i]nterFoam'` protects against the ssh
  command string, not against your own launcher's echoed output.
- **`set -u` kills an OpenFOAM launcher instantly** — `etc/bashrc` dereferences
  `WM_PROJECT_DIR` before setting it. The first launch died in 8 seconds and was
  caught only because liveness was checked rather than assumed.

gpu-claw as observed 2026-08-04: Ubuntu 24.04.4, Threadripper PRO 3955WX,
**nproc = 8**, 62 GiB RAM, OpenFOAM ESI **v2312** (`patch=260127`) at
`/usr/lib/openfoam/openfoam2312`, Open MPI 4.1.6, reachable over Tailscale as
`undi@100.101.237.123` with no WireGuard needed. `machine:cfd-dedicated` is a
**role**, resolved to gpu-claw by [#1495]; alias `gpu-claw → gpu-claw-ts` lives in
`workspace-hub/config/fleet-ssh-hosts.yml`.

See [[reference_gpu_claw_wireguard_flap_detached_runs]],
[[feedback_metric_moved_work_did_not_happen]].
