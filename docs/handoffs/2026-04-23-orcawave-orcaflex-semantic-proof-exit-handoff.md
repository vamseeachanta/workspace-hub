# OrcaWave/OrcaFlex Canonical Spec Semantic-Proof Exit Handoff

Date: 2026-04-23
Scope: workspace-hub issues #2455, #2456, #2457; digitalmodel PR #528
Operator: Hermes

## Executive state

The current semantic-proof wave for `spec.yml -> semantically equivalent solver-native input files` is implemented in digitalmodel PR #528:

- PR: https://github.com/vamseeachanta/digitalmodel/pull/528
- Branch: `issue-2455-2457-semantic-proofs-clean`
- Commit: `f956f51209503a1fca457c5cac3ec9c098e2bea9`
- Base: `main`
- Superseded PR: #527, closed because it included an unrelated prior commit.

Workspace-hub tracking issues remain open and labeled `status:plan-approved`:

- #2455: rigid jumper family via PLET-to-PLEM semantic proof
- #2456: lazy/steep-wave riser semantic proof
- #2457: L03 ship benchmark OrcaWave roundtrip proof

## What was implemented

### OrcaWave

Files in PR #528:

- `src/digitalmodel/hydrodynamics/diffraction/orcawave_backend.py`
- `tests/hydrodynamics/diffraction/test_orcawave_semantic_roundtrip.py`

Key implementation:

- Added `_effective_solve_type(spec)` so canonical `analysis_type: full_qtf` promotes native OrcaWave `SolveType` to `Full QTF calculation` when the solver option is still defaulted to potential/source.
- Added explicit L03 ship benchmark semantic roundtrip proof using:
  - `docs/domains/orcawave/L03_ship_benchmark/spec.yml`
  - `DiffractionSpec`
  - OrcaWave backend native YAML generation
  - reverse parser / semantic roundtrip assertions

Readiness now covered:

- Single ship L03 benchmark fixture.
- Full-QTF intent from canonical spec to native OrcaWave fields.
- Mesh/source panel path intent.
- Frequency and heading domain preservation.
- Reverse parser semantic equivalence for the proof fixture.

### OrcaFlex

Files in PR #528:

- `tests/solvers/orcaflex/modular_generator/test_jumper_plet_to_plem_semantic.py`
- `tests/solvers/orcaflex/modular_generator/test_riser_variant_semantic_proof.py`

Key implementation:

- Added/verified deterministic semantic proof for PLET-to-PLEM rigid jumper canonical spec.
- Added lazy-wave and steep-wave riser variant semantic-proof tests using `ProjectInputSpec` and `ModularModelGenerator`.
- Assertions check generated OrcaFlex-native YAML structure rather than requiring licensed OrcaFlex execution.

Readiness now covered:

- PLET-to-PLEM rigid jumper family fixture.
- Lazy-wave riser fixture.
- Steep-wave riser fixture.
- Line object naming and section/line-type generation intent.
- Buoyancy/geometry intent in generated line types.
- Vessel/floater connection intent for riser fixtures.
- Stage duration and time-step intent for steep-wave fixture.

## Validation performed

Targeted local validation in `/mnt/local-analysis/workspace-hub/digitalmodel`:

```bash
PYTHONPATH=src ./.venv/bin/python -m pytest \
  tests/hydrodynamics/diffraction/test_orcawave_semantic_roundtrip.py \
  tests/hydrodynamics/diffraction/test_validate_owd_vs_spec_semantics.py \
  tests/solvers/orcaflex/modular_generator/test_jumper_plet_to_plem_semantic.py \
  tests/solvers/orcaflex/modular_generator/test_riser_variant_semantic_proof.py \
  -q
```

Result reported during session:

```text
35 passed in 20.46s
```

Adversarial review:

- First review verdict: MAJOR.
- Main finding: L03 test exposed wrong backend behavior where canonical `analysis_type: full_qtf` could still emit `SolveType: Potential and source formulations`.
- Fix: implemented `_effective_solve_type(spec)` and updated QTF/source/headings logic.
- Re-review verdict: PASS.

## Current blocker

PR #528 is open but CI Quality Gates are red due an unrelated/pre-existing missing dependency in fatigue tests:

```text
ModuleNotFoundError: No module named 'pylife'
```

Trace origin:

```text
src/digitalmodel/fatigue/sn_curves.py:15
from pylife.materiallaws.woehlercurve import WoehlerCurve
```

CI job:

- https://github.com/vamseeachanta/digitalmodel/actions/runs/24860216580/job/72783595117

Affected check state at exit:

- `GitGuardian Security Checks`: success
- `docs`: success
- `Run Quality Gates`: failure due `pylife`

The `pylife` dependency issue should remain separate from PR #528 unless explicitly approved. It appears tracked by workspace-hub #2441:

- https://github.com/vamseeachanta/workspace-hub/issues/2441

## Semantic-proof gaps still remaining

This step is the most important part of the OrcaWave/OrcaFlex workflow. The current PR establishes deterministic proof coverage for selected fixtures, but these gaps remain:

1. Licensed solver load/run proof
   - Current tests prove canonical schema load and native YAML semantic structure.
   - They do not prove OrcaWave/OrcaFlex licensed applications can load and run every generated native input file.
   - Next tier should run licensed-machine smoke/load checks and capture evidence artifacts.

2. Bidirectional OrcaFlex reverse parsing
   - OrcaWave has explicit reverse parser roundtrip coverage in this wave.
   - OrcaFlex proof is mostly canonical spec -> generated native YAML assertions.
   - Need stronger OrcaFlex native YAML -> canonical semantic extraction / equivalence checks.

3. Broader structural family coverage
   - Covered now: L03 ship benchmark, PLET-to-PLEM jumper, lazy-wave riser, steep-wave riser.
   - Not yet covered: CALM/SPM buoy systems, spread-moored FPSO, semi-submersible/FOWT, multi-body hydrodynamics, installation scenarios, mooring-only systems, vessel RAO import, OrcaWave-to-OrcaFlex hydrodynamic handoff.

4. Environmental and load-case equivalence
   - Current tests assert core object/geometry/solver intent.
   - Need matrix tests for waves, currents, wind, seeds, headings, sea states, load-case combinations, analysis durations, and restart/stage semantics.

5. Materials/section property provenance
   - Current tests check some line-type geometry fields.
   - Need stronger checks for mass, stiffness, drag, buoyancy, hydrodynamic coefficients, bend stiffness, effective tension, and material library provenance.

6. RAO / hydrodynamic database provenance
   - Need proof that OrcaWave-generated hydrodynamic outputs or external RAO datasets are traceably imported into OrcaFlex-native inputs without losing sign conventions, units, headings, frequencies, body frames, or damping assumptions.

7. YAML canonical-contract documentation
   - Need explicit llm-wiki/spec pages defining required canonical semantics for `DiffractionSpec`, `ProjectInputSpec`, and native output equivalence criteria.

## Structure readiness matrix

| Structure / workflow | Current readiness | Evidence | Next gap |
| --- | --- | --- | --- |
| OrcaWave L03 ship benchmark | Deterministic semantic proof in PR #528 | `test_orcawave_semantic_roundtrip.py`; L03 `spec.yml`; `_effective_solve_type` | Licensed OrcaWave load/run; richer QTF output evidence |
| OrcaFlex PLET-to-PLEM jumper | Deterministic semantic proof in PR #528 | `test_jumper_plet_to_plem_semantic.py` | Licensed OrcaFlex load/run; broader jumper variants |
| OrcaFlex lazy-wave riser | Deterministic semantic proof in PR #528 | `test_riser_variant_semantic_proof.py`; `a01_lazy_wave_riser/spec.yml` | Native reverse parser; more hydrodynamic/material checks |
| OrcaFlex steep-wave riser | Deterministic semantic proof in PR #528 | `test_riser_variant_semantic_proof.py`; `a01_steep_wave_riser/spec.yml` | Native reverse parser; detailed stage/restart/load-case checks |
| OrcaWave-to-OrcaFlex hydrodynamic handoff | Partial conceptual readiness only | Existing OrcaWave/OrcaFlex folders and llm-wiki context | End-to-end proof: OrcaWave output -> RAO database -> OrcaFlex vessel input |
| CALM/SPM buoy | Not yet proof-covered | Domain expected; no current semantic proof identified in this wave | Add canonical fixture + native OrcaFlex proof |
| Spread-moored FPSO / vessel system | Not yet proof-covered | Candidate from offshore workflow needs | Add vessel/mooring/RAO fixture and proof |
| Semi-sub / FOWT / multi-body | Not yet proof-covered | Candidate from hydrodynamics/offshore workflow needs | Add OrcaWave multi-body and OrcaFlex coupled-system proof |
| Mooring-only system | Not yet proof-covered | Candidate from OrcaFlex library needs | Add line/anchor/fairlead/environment proof |
| Installation analysis | Not yet proof-covered | Candidate workflow | Add staged simulation/install load-case proof |

## llm-wiki gaps to fill

The existing llm-wiki/domain material should be used as the knowledge base for the next planning wave, but the following gaps need explicit pages/examples/case studies:

1. Canonical spec equivalence contract
   - Define what counts as semantic equivalence for `spec.yml -> native solver input`.
   - Include mandatory unit normalization, coordinate frames, sign conventions, object identity, solver-option mapping, and acceptable native-default differences.

2. OrcaWave `DiffractionSpec` examples
   - L03 single ship full-QTF case.
   - Multi-body interaction case.
   - Mesh/source-panel path conventions.
   - QTF / diagonal-QTF / potential-source solve-type mapping examples.

3. OrcaFlex `ProjectInputSpec` examples
   - PLET-to-PLEM jumper.
   - Lazy-wave riser.
   - Steep-wave riser.
   - CALM/SPM buoy.
   - Spread-moored FPSO.
   - Semi-sub/FOWT.
   - Mooring-only system.

4. OrcaWave-to-OrcaFlex handoff case study
   - OrcaWave hydrodynamic solve outputs.
   - RAO / damping / added-mass provenance.
   - OrcaFlex vessel type and hydrodynamic database import.
   - Verification checks for headings, frequencies, phase/sign, body axes, and units.

5. Licensed solver proof protocol
   - How to run native load/run on a licensed machine.
   - What output artifacts to capture.
   - What failures are semantic vs application-version/default differences.
   - How to attach proof evidence back to GitHub issues/PRs.

6. Fixture expansion cookbook
   - How to add a new structure family fixture.
   - Minimal canonical `spec.yml` fields.
   - Expected native YAML assertions.
   - Required reverse-parser assertions where available.
   - How to avoid overfitting to one generated formatting style.

## Recommended next wave

1. Merge PR #528 after handling or acknowledging the unrelated `pylife` CI blocker.
2. Close workspace-hub #2455/#2456/#2457 only after PR #528 is merged or otherwise accepted.
3. Open/advance a separate #2441 CI-health PR for `pylife` if Quality Gates must be green before merge.
4. Create next semantic-proof issues for:
   - OrcaFlex CALM/SPM buoy proof.
   - OrcaFlex spread-moored FPSO / vessel+mooring proof.
   - OrcaWave-to-OrcaFlex RAO/hydrodynamic handoff proof.
   - OrcaFlex native reverse-parser equivalence proof.
   - Licensed-machine load/run proof protocol.
5. Create llm-wiki pages for the six gaps listed above before broadening fixture coverage.

## Exit commands / verification reference

Current digitalmodel branch state at exit was clean:

```bash
cd /mnt/local-analysis/workspace-hub/digitalmodel
git status --short --branch
# ## issue-2455-2457-semantic-proofs-clean...origin/issue-2455-2457-semantic-proofs-clean
```

Current workspace-hub repo had unrelated dirty state already present. This handoff file is additive under `docs/handoffs/` and should be committed separately only after reviewing unrelated workspace-hub changes.

Useful status commands:

```bash
cd /mnt/local-analysis/workspace-hub/digitalmodel
gh pr view 528 --repo vamseeachanta/digitalmodel --json url,state,headRefName,baseRefName,commits,statusCheckRollup

cd /mnt/local-analysis/workspace-hub
gh issue view 2455 --json number,title,state,labels,url,updatedAt
gh issue view 2456 --json number,title,state,labels,url,updatedAt
gh issue view 2457 --json number,title,state,labels,url,updatedAt
gh issue view 2441 --json number,title,state,labels,url,updatedAt
```

## Do not repeat

- Do not reopen PR #527; it was intentionally superseded by clean PR #528.
- Do not fold unrelated `pylife` dependency repair into semantic-proof PR #528 without explicit approval.
- Do not treat deterministic semantic tests as licensed solver execution proof.
- Do not close #2455/#2456/#2457 until PR #528 is merged/accepted and final issue comments are updated.
