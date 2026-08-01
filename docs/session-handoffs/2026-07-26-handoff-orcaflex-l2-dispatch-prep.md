# Session handoff — OrcaFlex capability review + L2 attestation dispatch prep (2026-07-26)

Session ran on **dev-secondary (ace-linux-2)**. Continuation of the 2026-07-23 machine-equivalence session (see `2026-07-23-handoff-machine-equivalence-reconcile-3591.md`). **No code was written this session** — the work was assessment, measurement, and preparing an executable handoff for the licensed Windows host. All output landed as GitHub issue comments; the only repo change is this handoff.

## What was asked

1. Review the OrcaFlex analysis work and identify what would let us prepare analysis files for a wider set of assets.
2. Prepare the L2 attestation dispatch (digitalmodel [#718](https://github.com/vamseeachanta/digitalmodel/issues/718)).

## 1. OrcaFlex review — delivered in-session (no artifact committed)

Asset coverage as it stands:

- **READY**: risers, moorings, installation, pipeline, post-processing
- **PARTIAL**: riser fatigue, FOWT cable, J-lay/reel-lay, extreme-value
- **MISSING**: SALM, TLP/spar, jack-up, towing, sloshing multibody

Prioritized work list (1 = highest): merge [dm PR#1628](https://github.com/vamseeachanta/digitalmodel/pull/1628) (awaiting owner eyeball on mooring MBL/EA + CoG deltas) → run L2 [#718](https://github.com/vamseeachanta/digitalmodel/issues/718) then L3 [#719](https://github.com/vamseeachanta/digitalmodel/issues/719) → land the [#941](https://github.com/vamseeachanta/digitalmodel/issues/941) use-case catalog and gap-fill → unify the three overlapping generators and fix template-path drift → typed generation → licensed-run manifest → new asset templates → hygiene/stubs → parametric scale-out ([#834](https://github.com/vamseeachanta/digitalmodel/issues/834)/[#1602](https://github.com/vamseeachanta/digitalmodel/issues/1602)/[#1603](https://github.com/vamseeachanta/digitalmodel/issues/1603)).

## 2. L2 dispatch prep — two blocking findings, then a prepared sitting

### Finding A — the licensed host pair has FLIPPED since the 2026-07-10 record

Measured from `queue/heartbeat/*.json` + `queue/results/*.json` in the queue clone and `~/.deckhand/licensed-run-alarm.log`:

| Host | State 2026-07-26 |
|---|---|
| **ace-win-1** (RDS-002) | **Healthy executor** — current heartbeat, `code_sha 2027c64`, 3× `aqwa-diffraction-solve` rc=0 on 07-13 / 07-17 / 07-18 with returned files. The "No module named digitalmodel" break the owner was fixing is fixed. Per [dm#1553](https://github.com/vamseeachanta/digitalmodel/issues/1553): 64 cores / 256 GiB, OrcaFlex + OrcaWave + AQWA + ANSYS licensed. |
| ace-win-2 (WS014) | **Agent down** since `2026-07-13T21:37:48Z` (~318 h). Alarm has fired every cycle since; the log is ~300 KB of the same finding. |

This inverts the standing guidance ("ace-win-1 broken, dispatch to ace-win-2"). **Re-verify heartbeat + recent results before choosing a host — this pair has now flipped twice.** Owner directive still holds: address hosts explicitly with `--host`, never the default lane.

### Finding B — the licensed-run lane cannot carry repo-internal runs

`scripts/deckhand/licensed-run-dispatch.py --dry-run` denies at two independent fail-closed gates:

```
--scope acma --workflow orcaflex-l2-attestation      → gates 1-5: DENIED -> only license-gated workflows use this lane
--scope ecosystem --workflow orcaflex-strength-post  → gates 1-5: DENIED -> scope 'ecosystem' has no workdir
```

The allowlist (`licensed_run.workflows`) carries only orcaflex-strength-post / orcawave-diffraction-solve / aqwa-diffraction-solve / openfoam-run-batch, and **every scope with a `workdir` is a client scope** — `ecosystem` and `software-ops` have no digitalmodel workdir. Consequence: digitalmodel's licensed-machine issues ([#718](https://github.com/vamseeachanta/digitalmodel/issues/718), [#719](https://github.com/vamseeachanta/digitalmodel/issues/719), [#691](https://github.com/vamseeachanta/digitalmodel/issues/691), [#604](https://github.com/vamseeachanta/digitalmodel/issues/604)) have never had a lane. That is the structural reason they have sat open since June, not neglect.

Both gaps already had issues, so evidence went there rather than into duplicates: [deckhand#550](https://github.com/vamseeachanta/deckhand/issues/550) (workflow onboarding, paired with dm#1554 `orcaflex-run-batch`) pointing at [deckhand#543](https://github.com/vamseeachanta/deckhand/issues/543) (neutral scope).

### What was prepared

A paste-ready **on-host sitting for ace-win-1**, posted as [dm#718 comment 5087048839](https://github.com/vamseeachanta/digitalmodel/issues/718#issuecomment-5087048839). Needs no new code and no lane changes — it uses only module CLIs on current main, which is what the issue's `machine:licensed-win-1` label always implied.

Verified on this box (license-free half) before writing it:

| Registry model | spec.yml | generate |
|---|---|---|
| `a01_catenary_riser` | `docs/domains/orcaflex/library/model_library/a01_catenary_riser/spec.yml` | OK |
| `c03_turret_moored_fpso` | `docs/domains/orcaflex/library/model_library/c03_turret_moored_fpso/spec.yml` | OK |
| `rigid_jumper_plet_plem` | `docs/domains/orcaflex/jumper/plet_to_plem/spec.yml` | OK |

The jumper spec path is **not recorded in the registry** — recovered from `tests/solvers/orcaflex/modular_generator/test_jumper_plet_to_plem_semantic.py::SPEC_PATH`. `modular_input_validation.cli` also runs here and degrades correctly (`Level 1 ✓ / Level 2: skipped / Software available: no`); on the licensed host the same command exercises the real `LoadData` + statics path.

The runbook covers: sync + commit capture → license probe → generate the three masters → an `attest_l2.py` scratch script writing machine-readable per-model pass/fail plus the exact OrcaFlex error and failing object → validator L1+L2 per master → the two never-executed scaffolds (`test_environment_defaults_vs_orcfxapi.py -m solver`, which closes the #515 OQ-3 item, and `modular_generator/test_modular_vs_monolithic.py`) → report template → registry promotion rule (promote only on recorded passing load, never on a skip) → branch/PR + transcript back to #718 and #519.

Minor defect noted on the issue, not fixed: `modular_input_validation` writes its CSV/MD/HTML to `reports/validation/calm_buoy/` regardless of the input model — the project name is a config default, not derived from the spec. Gitignored, so harmless, but misleading evidence paths.

## Repo states at exit

| Repo | State |
|---|---|
| workspace-hub | `main`, this handoff is the only change; rebased onto origin/main and pushed. Untracked `docs/reports/sessions/2026-07-2{2,4,5,6}-main.html` = generated session reports, left alone as usual. |
| digitalmodel | **Untouched.** `main` @ `6d5623233`, 1 ahead / 82 behind, 2 untracked CFD viz PNGs — the LIVE compute clone (memory `digitalmodel-compute-clone-is-live`). Generation smoke-tests wrote only to the session scratchpad; the one ignored artifact they created in-clone (`reports/validation/calm_buoy/`) was removed. |
| deckhand | **Untouched.** `main` @ `555605c`, untracked `.codex/`, `.gemini/`, `ace-win-2`, `.claude/skills/.gitignore` pre-existing. Only `--dry-run` dispatch calls were made — nothing enqueued, no queue writes. |
| deckhand-licensed-runs-queue | Read-only inspection. No requests created. |

## Next steps / decisions for the owner

1. **Run the sitting** — the only step that needs a session on RDS-002; everything else is prepared. Or wait for dk#550 + dk#543 to make it a queue payload.
2. **ace-win-2**: revive the agent or add a known-down suppression to the alarm. ~318 h of identical findings is training the operator to ignore the channel.
3. **[dm PR#1628](https://github.com/vamseeachanta/digitalmodel/pull/1628)** still open awaiting owner eyeball on mooring MBL/EA + CoG deltas (carried from the previous session; not self-merged by design).
4. Carried watch items from the 2026-07-23 handoff are unchanged (peer-box R-MODEL-DRIFT; ace-win-1/2 schema-5 equality evidence).

## Auto-memory updated

- `licensed-run-producer-wiring-2026-06-18.md` — 2026-07-26 entries: host-state inversion (with the "verify heartbeat before choosing a host, this pair has flipped twice" rule) and the client-scope-only lane constraint with both measured denial strings.
- `MEMORY.md` index line for that topic rewritten to the corrected state (also shrank the index, which was over its 17 KB target).
