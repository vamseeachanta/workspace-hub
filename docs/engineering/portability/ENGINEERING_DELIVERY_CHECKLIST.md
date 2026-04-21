# Engineering Delivery Checklist

> Minimum reusable artifact bundle that must be committed before an engineering task is considered complete.
>
> **Parent contract:** `PORTABILITY_CONTRACT.md`
> **Issue:** #2268 | **Parent:** #1782

---

## Purpose

Every engineering task that involves simulation, analysis, or tool configuration must produce a minimum set of repo-tracked artifacts. This checklist ensures that durable learnings are captured before the task is closed — not left as machine-local files that are invisible to the rest of the team and at risk of loss.

This checklist applies to work on **any** execution host (dev-secondary, licensed-win-1/2, gpu-compute) and covers the artifacts that must be **promoted** into git per the Portability Contract.

---

## The Checklist

### 1. Solver Configuration Template

- [ ] Parameterized template for the solver input files used in this task
- [ ] Template placed in the owning repo under `data/<domain>/templates/` or equivalent
- [ ] Template uses variables/placeholders instead of hardcoded project-specific values
- [ ] Comments in the template explain non-obvious settings and why they were chosen

**Applies to:** OpenFOAM dict files, CalculiX INP files, OrcaFlex model configs, Blender Python scripts, Capytaine input definitions.

**Example paths:**
- `digitalmodel/data/cfd/templates/simpleFoam-steady-state/`
- `digitalmodel/data/structural/templates/calculix-fatigue/`

### 2. Automation Script

- [ ] Python or Bash script that can regenerate the simulation setup from the template
- [ ] Script uses relative paths or `${REPO_ROOT}` / `$(git rev-parse --show-toplevel)` — no hardcoded absolute paths
- [ ] Script is executable and has appropriate shebang (`#!/usr/bin/env bash` or `#!/usr/bin/env python3`)
- [ ] Script documents its dependencies (solver version, Python packages) in a docstring or header comment

**Applies to:** Any workflow that required more than manual file editing to set up.

**Example paths:**
- `digitalmodel/scripts/python/digitalmodel/cfd/run_openfoam_case.py`
- `digitalmodel/scripts/python/digitalmodel/visualization/render_blender.py`

### 3. Validation Case

- [ ] At least one known-good input/output pair committed as test data
- [ ] Test data is small enough for git (< 10 MB) — use representative subsets, not full simulation outputs
- [ ] A test script or test function that runs the template against the validation case
- [ ] Test can run without the licensed solver if the solver is commercial (use pre-computed reference outputs)

**Applies to:** Any template or script that produces numerical results.

**Example paths:**
- `digitalmodel/tests/cfd/test_data/simpleFoam-validation/`
- `digitalmodel/tests/structural/test_calculix_fatigue.py`

### 4. Workflow Documentation

- [ ] Concise description of the end-to-end workflow: geometry → mesh → solve → post-process
- [ ] Tool versions used (must match baselines in `PORTABILITY_CONTRACT.md`)
- [ ] Known limitations, gotchas, or non-obvious solver behaviors
- [ ] Cross-references to related issues and upstream research docs
- [ ] For OpenFOAM baseline work, link the canonical workflow doc `openfoam-v2312-baseline-workflow.md`

**Placement rules:**
- If the doc describes a general capability → `docs/engineering/` or `docs/research/` in `workspace-hub`
- If the doc describes how to use a specific `digitalmodel` module → `digitalmodel/docs/`

### 5. Knowledge Seed (if applicable)

- [ ] For non-obvious findings: create a knowledge seed entry in `knowledge/seeds/<domain>/`
- [ ] Seed follows the existing YAML format with `finding`, `context`, `source`, and `confidence` fields
- [ ] Seed references the originating issue number

**Applies to:** Solver behaviors that are surprising, undocumented, or differ between versions/forks. Not required for routine work.

**Example:** "OpenFOAM v2312 silently ignores `wallFunction` entries when `yPlus < 1`" — this kind of finding prevents future engineers from wasting hours rediscovering it.

### 6. Data Placement Compliance

- [ ] No simulation outputs (mesh files, solution fields, VTK results) committed to git
- [ ] Large outputs stored on ace drive under `${ACE_DATA_ROOT}/<repo>/<domain>/` per `docs/standards/DATA_PLACEMENT.md`
- [ ] If outputs are needed for validation, commit only a minimal representative subset (< 10 MB)
- [ ] Gitignore rules updated if new output directories are created

### 7. Issue Closure

- [ ] Originating issue referenced in commit messages
- [ ] Issue updated with a completion summary
- [ ] Any follow-up work captured as new issues (not left as TODOs in code)

---

## When to Apply

| Task Type | Required Items | Notes |
|-----------|----------------|-------|
| New solver integration (e.g., first OpenFOAM case) | All 7 | Full bundle — this is the most critical case |
| New analysis type with existing solver | Items 1-4, 6-7 | Knowledge seed only if surprising findings |
| Bug fix in existing template | Items 3, 7 | Update validation case to cover the bug |
| Documentation-only update | Item 4, 7 | No solver artifacts needed |
| Exploratory / research spike | Items 4-5, 7 | Capture what was learned, even if no template yet |

---

## Minimum Viable Bundle

For teams or agents that need the absolute minimum: items **1** (template), **3** (validation case), and **7** (issue closure) are non-negotiable. Without these three, the work is not reproducible and not considered delivered.

---

## Integration with Existing Workflows

### GSD Framework

When using the GSD workflow (`/gsd:execute-phase`, `/gsd:verify-work`), the phase verification step should include this checklist. The `VERIFICATION.md` report produced by GSD should confirm that all applicable items are present.

### Agent Batch Execution

Agents executing engineering tasks via overnight batch runs (see `docs/plans/overnight-prompts/`) must include this checklist in their execution prompts. The agent should not close an issue until all applicable items are committed.

### Cross-Review Policy

Per the cross-review policy (`config/agents/claude/memory-snapshots/project_cross_review_policy.md`), engineering deliverables are subject to review before merge. Reviewers should verify checklist compliance.

---

## Enforcement

This checklist is currently at **Level 0 (Prose)** per `.claude/rules/patterns.md`. Planned progression:

| Level | Mechanism | Status |
|-------|-----------|--------|
| 0 — Prose | This document | Active |
| 1 — Micro-skill | Checklist loaded automatically when engineering tasks are started | Planned |
| 2 — Script | `scripts/testing/check-engineering-delivery.sh` validates artifact presence | Planned |
| 3 — Hook | Pre-push check blocks engineering issue closure without minimum bundle | Future |

---

## Cross-References

- `PORTABILITY_CONTRACT.md` — defines portable vs machine-local knowledge
- `MACHINE_ROLES.md` — which machines produce which types of artifacts
- `docs/DATA_RESIDENCE_POLICY.md` — three-tier data residence model (ADR-004)
- `docs/standards/DATA_PLACEMENT.md` — size-based placement rules
- `docs/research/engineering-capability-map.md` — tool inventory, format matrix, integration gaps
- `.claude/rules/patterns.md` — enforcement gradient (Level 0-3)
- Issue #1782 — parent epic (zero-loss agent learnings)
- Issue #25 — OpenFOAM CFD analysis capability
- Issue #26 — Blender working configurations
- Issue #1268 — CFD analysis plan
