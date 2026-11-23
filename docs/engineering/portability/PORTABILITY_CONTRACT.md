# Portability Contract

> Canonical policy for engineering knowledge portability across the workspace-hub machine fleet.
>
> **Parent:** #1782 (zero-loss agent learnings)
> **Related:** #26 (Blender configs), #25 (OpenFOAM CFD), #1268 (CFD analysis plan), #1475 (CLI-Anything eval)

---

## Purpose

Engineering work produces durable knowledge — solver configurations, validated meshes, post-processing scripts, lessons learned. This contract defines what must be promoted into repo-tracked artifacts (portable) versus what may remain on the machine where it was created (machine-local).

The goal: a `git clone` of `workspace-hub` + `digitalmodel` on a fresh machine provides enough context to understand, reproduce, and extend prior engineering work — even if the original execution host is unavailable.

---

## Portable vs Machine-Local

### Portable (must be repo-tracked)

Portable artifacts survive machine failure and are available on any checkout. They belong in git under the owning repository.

| Category | Examples | Owning Repo | Path Convention |
|----------|----------|-------------|-----------------|
| Solver templates | OpenFOAM dict templates, CalculiX INP templates | `digitalmodel` | `data/<domain>/templates/` |
| Configuration schemas | YAML/JSON schemas for simulation inputs | `digitalmodel` | `config/` or `data/<domain>/schemas/` |
| Automation scripts | Python/Bash wrappers for headless solver execution | `digitalmodel` | `scripts/python/digitalmodel/<domain>/` |
| Validation cases | Known-good input/output pairs for regression testing | `digitalmodel` | `tests/<domain>/test_data/` |
| Engineering reference data | Material properties, S-N curves, design code tables | `digitalmodel` | `data/<domain>/` (Tier 2 per `DATA_RESIDENCE_POLICY.md`) |
| Workflow documentation | How to run a simulation end-to-end | `workspace-hub` | `docs/engineering/` or `docs/research/` |
| Capability maps | Tool inventories, format matrices, integration gaps | `workspace-hub` | `docs/research/engineering-capability-map.md` |
| Lessons learned | What worked, what failed, non-obvious solver behaviors | `workspace-hub` | `knowledge/seeds/<domain>/` |
| Baseline version pins | Which solver version is canonical for each domain | this document | see Baselines section below |

### Machine-Local (may remain on execution host)

Machine-local artifacts are either too large for git, regenerable from portable artifacts, or specific to hardware configuration.

| Category | Examples | Typical Location | Recovery Method |
|----------|----------|------------------|-----------------|
| Solver binaries | OpenFOAM v2312, Blender 4.x, CalculiX 2.21 | System packages | Reinstall from package manager |
| Compiled libraries | `libOpenFOAM.so`, CUDA kernels | `/usr/lib/`, `/opt/` | Rebuild from source or package |
| Large mesh files | `.msh`, `.vtk` > 10 MB | `${ACE_DATA_ROOT}/<repo>/<domain>/` | Regenerate from portable templates + meshing scripts |
| Simulation results | Solution fields, time directories | `${ACE_DATA_ROOT}/<repo>/<domain>/` | Re-run solver with portable inputs |
| Virtual environments | `.venv/`, `*-env/` | `/mnt/local-analysis/*-env/` | Recreate with `uv sync` or `pip install` |
| GPU/hardware configs | CUDA device settings, GPU memory limits | `/etc/`, `~/.config/` | Hardware-specific, not transferable |
| Transient caches | ParaView state files, Blender `.blend1` backups | Working directories | Ephemeral, no backup needed |

### The Promotion Rule

> **If an engineering insight took more than 30 minutes of human effort to discover, it must be promoted to a portable artifact.**

Promotion means:
1. Extract the durable knowledge into a template, script, YAML config, or knowledge seed
2. Commit it to the appropriate repo (`digitalmodel` or `workspace-hub`)
3. Add a validation case if the insight affects solver behavior
4. Reference the originating issue in the commit message

This mirrors the Tier 1/2/3 model from #1782, applied to engineering knowledge instead of agent state.

---

## Baselines

Canonical solver versions for downstream engineering phases. These are the versions that portable templates and validation cases target.

| Domain | Tool | Baseline Version | Installed On | Reference |
|--------|------|-----------------|--------------|-----------|
| CFD | OpenFOAM (ESI) | v2312 | dev-secondary (`ace-linux-2`) | `docs/research/openfoam-version-landscape.md` |
| 3D / Visualization | Blender | headless via `blender -b --python ...` | dev-secondary (`ace-linux-2`) | Issue #26 |
| FEA | CalculiX | 2.21 | dev-secondary (`ace-linux-2`) | `docs/research/engineering-capability-map.md` |
| Meshing | Gmsh | 4.x | dev-secondary (`ace-linux-2`) | `docs/research/engineering-capability-map.md` |
| Post-processing | ParaView | 5.x | dev-secondary (`ace-linux-2`) | `docs/research/engineering-capability-map.md` |
| Hydrodynamics | Capytaine | 2.3.1 | dev-secondary (`ace-linux-2`) | `docs/research/capytaine-bem-eval.md` |
| Mooring dynamics | OrcaFlex | Licensed | licensed-win-1 | `docs/roadmaps/orcawave-orcaflex-capability-roadmap.md` |

---

## Data Placement Integration

This contract inherits data placement rules from two existing policies:

- **`docs/DATA_RESIDENCE_POLICY.md`** (ADR-004) — Three-tier data model: collection (Tier 1, `worldenergydata`), engineering reference (Tier 2, `digitalmodel`), project (Tier 3, project repos)
- **`docs/standards/DATA_PLACEMENT.md`** — Size thresholds: < 10 MB in git, 10-100 MB in Git LFS, > 100 MB on ace drive (`${ACE_DATA_ROOT}`)

Engineering simulation outputs (mesh files, solution fields, VTK results) almost always exceed 10 MB and belong on the ace drive, not in git. The portable artifact is the *template* and *script* that regenerates them.

---

## Machine Fleet Reference

The current workstation registry lives at `config/workstations/registry.yaml`. For role definitions and responsibilities, see `MACHINE_ROLES.md` in this directory.

| Machine | Role | Key Engineering Capabilities |
|---------|------|------------------------------|
| `ace-linux-1` (dev-primary) | Orchestration / documentation | Python, `uv`, `gh`, nightly pipelines |
| `ace-linux-2` (dev-secondary) | Engineering execution | OpenFOAM, Blender, FreeCAD, Gmsh, ParaView, CalculiX, GPU (T400) |
| `licensed-win-1` | Licensed simulation | OrcaFlex, ANSYS |
| `licensed-win-2` | Licensed simulation (backup) | OrcaFlex, ANSYS |
| `macbook-portable` | Portable development | Python, `uv`, `gh` (no simulation tools) |
| `gali-linux-compute-1` | GPU compute (not yet onboarded) | 2x RTX 3090, CUDA |

---

## Enforcement

This contract is currently at **Level 0 (Prose)** per the enforcement gradient in `.claude/rules/patterns.md`. Planned progression:

| Level | Mechanism | Status |
|-------|-----------|--------|
| 0 — Prose | This document | Active |
| 1 — Micro-skill | Per-stage checklist loaded at engineering task entry | Planned |
| 2 — Script | Audit script checking for untracked templates in simulation dirs | Planned |
| 3 — Hook | Pre-commit check for orphaned engineering knowledge | Future |

---

## Cross-References

- `MACHINE_ROLES.md` — dev-primary vs dev-secondary responsibilities
- `ENGINEERING_DELIVERY_CHECKLIST.md` — minimum reusable artifact bundle
- `config/workstations/registry.yaml` — machine capabilities and identities
- `docs/DATA_RESIDENCE_POLICY.md` — three-tier data residence model
- `docs/standards/DATA_PLACEMENT.md` — size-based placement rules
- `docs/ops/mount-map.yaml` — NFS/SSHFS mount inventory
- `docs/research/engineering-capability-map.md` — tool inventory and format matrix
- `docs/research/openfoam-version-landscape.md` — OpenFOAM fork comparison
- Issue #1782 — parent epic (zero-loss agent learnings)
- Issue #26 — Blender working configurations
- Issue #25 — OpenFOAM CFD analysis capability
- Issue #1268 — CFD analysis plan
