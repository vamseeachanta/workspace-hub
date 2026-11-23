# Core Engineering Portability Implementation Plan

> For Hermes: plan only. Do not implement this plan until the user explicitly approves execution. Use TDD for any code changes. Prefer shared repo-tracked artifacts over machine-local state.

Goal: Make OpenFOAM development and Blender animation workflows portable across the workspace-hub repo ecosystem and reproducible on other machines, with dev-secondary as the canonical engineering runtime and dev-primary as the orchestration/control plane.

Architecture:
- Standardize a repo-tracked portability layer built from shared skills, scripts, docs, examples, and validators.
- Treat dev-secondary (ace-linux-2) as the canonical execution host for engineering tools and dev-primary as the canonical propagation/documentation host.
- Capture every durable engineering learning in versioned artifacts, then propagate shared skills across repos.

Tech Stack:
- Bash, Python, uv, git
- OpenFOAM (target baseline: ESI/OpenFOAM.com v2312 unless changed explicitly)
- Blender headless CLI + bpy
- Shared skill propagation via scripts/propagate-ecosystem.sh
- Workspace documentation under docs/, scripts/, tests/, examples/, config/

---

## Current context / assumptions

1. Machine roles from `config/workstations/registry.yaml`:
   - dev-primary = `/mnt/local-analysis/workspace-hub`
   - dev-secondary = `/mnt/workspace-hub`
   - dev-secondary has Blender, OpenFOAM, FreeCAD, Gmsh, ParaView, CalculiX, meshio, GPU

2. Existing OpenFOAM research/assets already exist:
   - `docs/research/openfoam-version-landscape.md`
   - `docs/research/openfoam-wrk047-refresh.md`
   - `docs/research/openfoam-tutorials.md`
   - `docs/research/openfoam-python-ecosystem.md`
   - `scripts/openfoam/run-openfoam-tutorials.sh`
   - `scripts/pipelines/validate_cfd_convergence.py`
   - `scripts/pipelines/test_cylinder_in_flow.py`

3. Existing Blender/OpenFOAM strategy already documented:
   - `docs/research/cli-anything-blender-openfoam-eval.md`
   - Recommendation there: OpenFOAM stays CLI-native; Blender can use headless scripts first, optional CLI wrapper second.

4. Ecosystem propagation status:
   - Shared skill propagation mostly works.
   - `digitalmodel` still has placeholder shared-skill files to normalize.
   - `achantas-data` was skipped because of local modifications.

5. Constraints to preserve:
   - Plan before acting.
   - TDD required for implementation changes.
   - Keep portable knowledge in repo-tracked assets, not only `~/.hermes/`.

---

## Success criteria

This initiative is complete when all of the following are true:

1. A canonical portability contract exists in repo-tracked documentation.
2. OpenFOAM workflow is documented, scripted, and validated against a declared version baseline.
3. Blender workflow is documented, scripted, and validated for headless execution.
4. Shared skills for engineering portability are repo-tracked and propagated across ecosystem repos.
5. At least one OpenFOAM smoke workflow and one Blender smoke workflow can be re-run from scripts with documented prerequisites.
6. Machine-local assumptions are either encoded in scripts/docs/config or explicitly marked as non-portable prerequisites.

---

## Proposed artifact layout

Primary locations to use:

- Documentation
  - `docs/engineering/portability/`
  - `docs/engineering/openfoam/`
  - `docs/engineering/blender/`

- Scripts
  - `scripts/openfoam/`
  - `scripts/blender/`
  - `scripts/engineering/`

- Validation/tests
  - `tests/scripts/`
  - `tests/engineering/`

- Examples
  - `examples/openfoam/`
  - `examples/blender/`

- Shared skills
  - `.claude/skills/engineering/...`
  - `.claude/skills/devops/...` where cross-repo propagation behavior belongs

- Machine metadata
  - `config/workstations/registry.yaml`

Note: Adjust exact folder names only if repo-structure rules indicate a stricter canonical path during execution.

---

## Phase plan

### Phase 1: Define the portability contract

Objective: Create the canonical rules for what counts as portable engineering knowledge and where it lives.

Deliverables:
- `docs/engineering/portability/PORTABILITY_CONTRACT.md`
- `docs/engineering/portability/MACHINE_ROLES.md`
- `docs/engineering/portability/CHECKLIST.md`

Content to include:
- machine roles: dev-primary vs dev-secondary
- what must be repo-tracked
- what may remain machine-local
- required structure for scripts/examples/tests/docs
- definition of done for portable engineering work
- promotion rule: local learning -> skill/script/doc/test/example

Validation:
- Review docs for clear distinction between portable artifacts and machine-local state
- Verify references align with `config/workstations/registry.yaml`

Risks:
- Over-designing policy before implementation
- Duplicating content already in existing docs

Mitigation:
- Keep docs concise and link to existing source docs where possible

### Phase 2: Standardize OpenFOAM portability baseline

Objective: Make OpenFOAM workflows explicitly portable and version-aware.

Deliverables:
- `docs/engineering/openfoam/BASELINE.md`
- `docs/engineering/openfoam/WORKFLOW.md`
- `docs/engineering/openfoam/TROUBLESHOOTING.md`
- Shared skill update or new skill for canonical OpenFOAM execution
- Minimal reproducible OpenFOAM smoke case under `examples/openfoam/`
- Validation entrypoints under `scripts/openfoam/` and/or `tests/engineering/`

Required decisions:
- Declare ESI/OpenFOAM.com v2312 as current baseline unless changed by explicit decision
- Document fork/version incompatibilities from `docs/research/openfoam-version-landscape.md`
- Define standard runner and validator commands

Recommended content:
- environment setup commands
- case directory assumptions
- mesh generation path
- solver invocation patterns
- post-processing expectations
- convergence validation criteria
- common failure modes

Validation:
- Smoke case has documented runner
- Validator has deterministic pass/fail criteria
- Version assumptions are explicit

Risks:
- Hidden dependence on dev-secondary environment layout
- Inconsistent dictionary syntax between OpenFOAM forks

Mitigation:
- Add explicit version/fork banner in docs and scripts
- Fail fast in scripts if the wrong OpenFOAM version is detected

### Phase 3: Standardize Blender portability baseline

Objective: Make Blender automation portable using headless scripts as the canonical baseline.

Deliverables:
- `docs/engineering/blender/BASELINE.md`
- `docs/engineering/blender/WORKFLOW.md`
- `docs/engineering/blender/TROUBLESHOOTING.md`
- `scripts/blender/` entrypoints for headless automation
- `examples/blender/` minimal reproducible scene/render workflow
- Shared skill update or new skill for canonical Blender execution

Required decisions:
- Canonical path = `blender -b --python ...`
- Optional ergonomic layer = CLI-Anything harness, but not required for portability

Recommended content:
- headless invocation patterns
- bpy scene generation conventions
- render output conventions
- asset dependency rules
- deterministic render validation approach
- machine/GPU notes if relevant

Validation:
- Minimal scene can be generated and rendered from script
- Workflow does not depend on manual GUI-only hidden state

Risks:
- `.blend` files can hide manual state not reflected in code
- Render outputs may vary by version/device

Mitigation:
- Prefer procedural scene generation from script
- Keep validation focused on successful execution + structural output checks, not pixel-perfect equality initially

### Phase 4: Build a reusable engineering portability checklist

Objective: Turn the portability doctrine into an implementation checklist used for every future engineering feature.

Deliverables:
- `docs/engineering/portability/ENGINEERING_DELIVERY_CHECKLIST.md`
- optional shared skill or sub-skill for “portable-by-default engineering work”

Checklist sections:
- docs updated
- script added
- validator added
- example added
- machine assumptions documented
- skill updated
- ecosystem propagation run
- cross-machine follow-up recorded if needed

Validation:
- Checklist is short enough to use repeatedly
- Checklist maps directly to OpenFOAM and Blender cases

### Phase 5: Normalize ecosystem skill propagation

Objective: Ensure portability learnings reach all applicable repos.

Deliverables:
- resolved placeholder-link state in `digitalmodel`
- resolved skip/debt status for `achantas-data`
- documented propagation workflow and reporting template
- regression test coverage if propagation script changes are needed

Likely files:
- `scripts/propagate-ecosystem.sh`
- `tests/scripts/test_propagate_ecosystem.sh`
- relevant docs under `docs/engineering/portability/` or `docs/operations/`

Validation:
- dry-run summary is clean or explicitly justified
- real propagation succeeds for intended repos
- skipped repos are documented with reasons and follow-up

Risks:
- local repo modifications blocking propagation
- placeholder/symlink edge cases

Mitigation:
- always dry-run first
- keep propagation test coverage current

### Phase 6: Add smoke tests and verification commands

Objective: Make portability measurable, not aspirational.

Deliverables:
- one OpenFOAM smoke test command
- one Blender smoke test command
- verification docs showing expected outputs and failure modes

Suggested validation shape:
- OpenFOAM smoke:
  - prepare case
  - run short solver sequence
  - run convergence/structure validator
- Blender smoke:
  - generate scene from bpy script
  - render one frame in background mode
  - validate expected output files/metadata

Validation:
- both smoke flows can be invoked via documented commands
- both produce human-readable pass/fail signals

---

## Execution order

Recommended order of implementation:

1. Phase 1 — Portability contract
2. Phase 2 — OpenFOAM baseline
3. Phase 3 — Blender baseline
4. Phase 4 — Engineering delivery checklist
5. Phase 5 — Ecosystem propagation normalization
6. Phase 6 — Smoke tests and verification hardening

Reasoning:
- policy first to avoid inconsistent structure
- then the two domain workflows
- then checklist codification
- then ecosystem propagation
- then final measurable smoke validation

---

## Likely files to inspect before execution

Documentation and config:
- `config/workstations/registry.yaml`
- `docs/research/openfoam-version-landscape.md`
- `docs/research/openfoam-wrk047-refresh.md`
- `docs/research/openfoam-tutorials.md`
- `docs/research/openfoam-python-ecosystem.md`
- `docs/research/cli-anything-blender-openfoam-eval.md`

Scripts/tests:
- `scripts/openfoam/run-openfoam-tutorials.sh`
- `scripts/pipelines/validate_cfd_convergence.py`
- `scripts/pipelines/test_cylinder_in_flow.py`
- `scripts/propagate-ecosystem.sh`
- `tests/scripts/test_propagate_ecosystem.sh`

Skills to inspect/update during execution:
- `engineering/cfd/openfoam`
- `engineering/cad/blender`
- `devops/workspace-ecosystem-skill-propagation`
- `workspace-hub/repo-structure`

---

## TDD-oriented implementation slices

When execution begins, each code/doc change should follow small slices.

Example slice pattern for each scriptable deliverable:
1. Write/extend test for expected behavior
2. Run test and confirm failure
3. Implement minimum change
4. Run targeted test and confirm pass
5. Run broader verification command
6. Commit

Use this pattern especially for:
- propagation script adjustments
- smoke-test runners
- validators
- generated-path conventions

---

## Open questions to resolve during execution

1. Should the portability docs live under `docs/engineering/` or another already-established top-level docs taxonomy?
2. Which repo should host the canonical Blender smoke example if multiple repos may consume it?
3. Should OpenFOAM smoke tests run only on dev-secondary or also have stubbed validation on dev-primary?
4. Do we want a single shared portability skill, or separate OpenFOAM/Blender portability skills plus a checklist doc?
5. Should CLI-Anything Blender be documented as optional tooling now, or deferred until baseline headless scripts are mature?

Default recommendation if no contrary evidence appears:
- use `docs/engineering/...`
- host canonical baseline in `workspace-hub`
- real OpenFOAM/Blender execution on dev-secondary; docs/checks/orchestration on dev-primary
- use separate domain skills plus one concise portability checklist
- keep CLI-Anything optional and non-blocking

---

## Risks and tradeoffs

1. Risk: Documentation without enforcement
- Tradeoff: easy to write, easy to ignore
- Response: add smoke tests/checklists and propagation steps

2. Risk: Over-centralizing in workspace-hub while domain repos drift
- Tradeoff: one canonical place vs local flexibility
- Response: keep canonical patterns in workspace-hub, then propagate shared skills and reference docs

3. Risk: Version drift on OpenFOAM/Blender across machines
- Tradeoff: portability vs tool-version realism
- Response: version-pin the baseline in docs/scripts and detect mismatch early

4. Risk: Hidden manual Blender state
- Tradeoff: `.blend` convenience vs procedural reproducibility
- Response: prefer script-generated scenes for smoke tests and tutorials

5. Risk: Ecosystem propagation conflicts with local repo edits
- Tradeoff: shared consistency vs local autonomy
- Response: dry-run first, report skips explicitly, and resolve skipped repos intentionally

---

## Verification plan

Before declaring the implementation complete, verify:

1. Documentation
- all new docs exist and cross-link correctly
- machine roles match `registry.yaml`

2. OpenFOAM
- baseline version is explicit
- smoke example exists
- runner exists
- validator exists
- failure modes documented

3. Blender
- headless example exists
- script-based scene/render path exists
- outputs documented
- failure modes documented

4. Ecosystem
- shared skills propagated or skips documented
- provider adapters remain intact

5. Portability
- another machine/user can follow the documented steps without relying on hidden memory

---

## Recommended execution mode

Use implementation phases with explicit approval gates:

- Gate A: approve Phase 1 docs structure
- Gate B: approve OpenFOAM baseline decisions
- Gate C: approve Blender baseline decisions
- Gate D: approve ecosystem propagation changes
- Gate E: approve smoke-test rollout

This keeps changes reviewable and reduces accidental sprawl.

---

## Immediate next step after approval

Start with Phase 1 only:
1. inspect repo-structure constraints in detail
2. choose exact docs paths
3. draft the portability contract + machine roles + checklist docs
4. stop for review before touching OpenFOAM/Blender workflow assets
