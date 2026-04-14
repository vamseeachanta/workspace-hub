# Machine Roles

> Role definitions and responsibilities for each workstation in the workspace-hub fleet.
>
> **Source of truth for capabilities:** `config/workstations/registry.yaml`
> **Parent contract:** `PORTABILITY_CONTRACT.md`
> **Issue:** #2268 | **Parent:** #1782

---

## Role Taxonomy

Each machine has one primary role. Roles define what category of work is expected to originate on that machine, not what the machine is physically capable of.

| Role | Definition | Machines |
|------|-----------|----------|
| **primary-dev** | Orchestration, documentation, CI/CD, nightly pipelines, git coordination | `ace-linux-1` |
| **secondary-dev** | Canonical engineering execution — CFD, FEA, meshing, visualization | `ace-linux-2` |
| **simulation-license-host** | Licensed commercial simulation (OrcaFlex, ANSYS) | `licensed-win-1`, `licensed-win-2` |
| **portable-dev** | Lightweight development, documentation, mobile workflows | `macbook-portable` |
| **gpu-compute** | Heavy GPU workloads (ML, CUDA) | `gali-linux-compute-1` |

---

## dev-primary (`ace-linux-1`)

**Hostname:** `ace-linux-1` | **OS:** Linux | **IP:** 192.168.1.100 | **Tailscale:** 10.1.0.1

### Responsibilities

- **Orchestration hub** — all nightly scheduled tasks, cron jobs, and batch pipelines run here
- **Documentation host** — primary location for writing and reviewing docs, plans, and engineering reports
- **Git coordination** — trunk sync, multi-repo push scripts, PR creation and review
- **Agent orchestration** — Claude Code, Gemini CLI, nightly researcher pipelines
- **NFS server** — exports `/mnt/ace` (7.3 TB knowledge center) to the fleet
- **Cross-machine data access** — mounts `ace-linux-2` drives via SSHFS for file retrieval

### What originates here

- Repo-tracked documentation (`docs/`, `knowledge/seeds/`)
- Issue plans and execution prompts (`docs/plans/`)
- Nightly pipeline configs and scheduled tasks (`config/scheduled-tasks/`)
- Agent memory snapshots (`config/agents/claude/memory-snapshots/`)
- Cross-repo coordination scripts

### What does NOT originate here

- Simulation runs (no OpenFOAM, Blender, CalculiX installed)
- Licensed software execution (no OrcaFlex, ANSYS)
- GPU-accelerated workloads (no GPU)

### Storage

| Mount | Path | Type | Purpose |
|-------|------|------|---------|
| Local disk | `/mnt/local-analysis` | ext4 | Primary work partition, workspace-hub checkout |
| Knowledge center | `/mnt/ace` | ext4, NFS-exported | 7.3 TB bulk storage, standards, project archives |
| Remote (ace-linux-2) | `/mnt/remote/ace-linux-2/dde` | SSHFS | Access DDE drive on secondary |
| Remote (ace-linux-2) | `/mnt/remote/ace-linux-2/local-analysis` | SSHFS | Access secondary's workspace |

---

## dev-secondary (`ace-linux-2`)

**Hostname:** `ace-linux-2` | **OS:** Linux | **IP:** 192.168.1.103 | **Tailscale:** 10.1.0.2

### Responsibilities

- **Canonical engineering execution host** — all open-source simulation work runs here
- **CFD solver host** — OpenFOAM v2312 (ESI) is the baseline
- **Meshing and geometry** — FreeCAD, Gmsh, meshio
- **Post-processing and visualization** — ParaView, Blender (headless), pyvista
- **FEA solver host** — CalculiX 2.21
- **Hydrodynamics** — Capytaine 2.3.1 (BEM solver)

### What originates here

- Simulation results (mesh files, solution fields, VTK outputs) — stored on local drives, NOT in git
- Validated solver configurations that get promoted into portable templates
- Engineering capability discoveries (format compatibility, solver behaviors)
- GPU-accelerated pre/post-processing (NVIDIA T400)

### What does NOT originate here

- Documentation and plans (those originate on dev-primary)
- Nightly scheduled pipelines (cron runs on dev-primary)
- Licensed commercial simulation (OrcaFlex, ANSYS run on Windows hosts)

### Storage

| Mount | Path | Type | Purpose |
|-------|------|------|---------|
| Local disk | `/mnt/local-analysis` | NTFS (fuseblk) | Workspace-hub checkout, Python venvs |
| DDE drive | `/mnt/dde` | Local | Legacy engineering documents, Orcaflex models |
| Remote (ace-linux-1) | `/mnt/remote/ace-linux-1/ace` | NFS4 | Access knowledge center |
| Remote (ace-linux-1) | `/mnt/remote/ace-linux-1/local-analysis` | SSHFS | Access primary's workspace |

### Promotion Workflow

When engineering work on dev-secondary produces a durable insight:

1. **Discover** — solver configuration, mesh approach, or workflow that works
2. **Extract** — isolate the reusable parts from project-specific details
3. **Template** — create a parameterized template or script in `digitalmodel`
4. **Validate** — add a test case that confirms the template produces correct results
5. **Commit** — push to `digitalmodel` (or `workspace-hub` for docs/knowledge)
6. **Reference** — link the originating issue in the commit message

This ensures learnings from dev-secondary are available to anyone with a `git clone`.

---

## simulation-license-host (`licensed-win-1`, `licensed-win-2`)

**Hostname:** `licensed-win-1` / `licensed-win-2` | **OS:** Windows | **Access:** Physical/GUI only (no SSH)

### Responsibilities

- **OrcaFlex execution** — licensed dynamic analysis for risers, moorings, installation
- **ANSYS execution** — licensed FEA for structural analysis
- **Result export** — export simulation results to formats accessible from Linux hosts

### Constraints

- No SSH access — all work requires physical presence or GUI remote
- Git Bash (MINGW64) for script execution — limited shell capabilities
- No NFS/SSHFS — files must be manually transferred or synced via git
- `schedule_variant: contribute-minimal` — not suitable for automation-heavy workflows

### Coordination with dev-primary

- Execution prompts and plans originate on dev-primary (see `docs/plans/licensed-win-1-*.md`)
- Results are committed to project repos (e.g., `OGManufacturing`) and pushed
- dev-primary pulls results for cross-referencing and report generation

---

## portable-dev (`macbook-portable`)

**Hostname:** `Vamsees-MacBook-Air` | **OS:** macOS (ARM64 M1)

### Responsibilities

- Lightweight development and documentation while mobile
- Code review and PR management
- Agent CLI usage (Claude Code)

### Constraints

- No simulation tools installed
- No NFS — standalone, git-only sync
- Path conventions differ (`/Users/` vs `/home/`, `/mnt/`)
- `schedule_variant: none` — no cron or scheduled tasks

---

## gpu-compute (`gali-linux-compute-1`)

**Hostname:** `shoerack` | **OS:** Linux | **GPU:** 2x RTX 3090 (48 GB VRAM) | **RAM:** 128 GB

### Status: Not yet onboarded

This machine is not yet integrated into the workspace-hub fleet. When onboarded:

- Route heavy ML/CUDA workloads here
- Boot drive at 89% — needs cleanup before heavy use
- No agent CLIs or workspace-hub checkout yet configured

---

## Cross-Machine Communication Patterns

| From | To | Method | Use Case |
|------|----|--------|----------|
| dev-primary | dev-secondary | SSH (`ssh vamsee@ace-linux-2`) | Remote command execution, file retrieval |
| dev-primary | dev-secondary | SSHFS mount | Browse files without copy |
| dev-secondary | dev-primary | NFS4 mount | Access knowledge center and standards |
| dev-secondary | dev-primary | SSHFS mount | Access primary's workspace |
| dev-primary | licensed-win-1 | Git push/pull | Exchange execution prompts and results |
| Any | Any | Tailscale (ace-linux-1 ↔ ace-linux-2) | Overlay network for remote access |

See `docs/ops/mount-map.yaml` for the complete mount inventory.

---

## Cross-References

- `PORTABILITY_CONTRACT.md` — what must be portable vs machine-local
- `ENGINEERING_DELIVERY_CHECKLIST.md` — minimum artifact bundle per engineering task
- `config/workstations/registry.yaml` — canonical machine identity and capabilities
- `config/ai_agents/status/dev-primary.yaml` — agent CLI versions on primary
- `config/ai_agents/status/dev-secondary.yaml` — agent CLI versions on secondary
- `docs/ops/mount-map.yaml` — NFS/SSHFS mount inventory
- `docs/research/engineering-capability-map.md` — tool inventory and format matrix
