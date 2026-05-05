# Multi-machine baseline inventory for deployable work

> **Date:** 2026-05-04 / verified 2026-05-05 UTC
> **Purpose:** Start from first principles before solver automation: which machines exist, which repos they should have, which mounts/data they can access, and which AI/simulation programs are available.

---

## 1. Machine roles

| Machine | Role | Current decision |
|---|---|---|
| `ace-linux-1` | Control plane / primary dev | Canonical workspace + scheduler + `/mnt/ace` knowledge/data center. Keep as source of truth. |
| `ace-linux-2` | Secondary dev / overflow AI worker / open-source simulation worker | Prepare for direct repo work, raw-data access through NFS, preprocessing, and solver queue ingestion. Do not treat as licensed Orca/ANSYS solver host. |
| `licensed-win-1` | Licensed solver host | Runs OrcaWave/OrcaFlex/ANSYS through Windows Task Scheduler + Git-backed queue after bootstrap. |
| `licensed-win-2` | Secondary licensed solver host | Same class as `licensed-win-1`; preferred AQWA fallback/parallel host until live probes confirm exact licenses. |
| `macbook-portable` | Portable manual dev | Manual/lightweight; no cron dependency. |
| `gali-linux-compute-1` | Future GPU compute | Not yet onboarded; not in current deploy path. |

---

## 2. Repo placement policy

### Tier 0: must exist on every active AI/dev machine

| Repo | ace-linux-1 | ace-linux-2 | licensed Windows | Why |
|---|---:|---:|---:|---|
| `workspace-hub` | required | required | required | Control plane, schedules, queue, skills, plans, scripts. |

### Tier 1 engineering repos: must exist on ace-linux-1 and ace-linux-2

| Repo | ace-linux-1 target | ace-linux-2 target | Windows target | Why |
|---|---|---|---|---|
| `digitalmodel` | `/mnt/ace/digitalmodel` or local managed clone | `/mnt/local-analysis/digitalmodel` preferred; NFS read fallback at `/mnt/remote/ace-linux-1/ace/digitalmodel` | optional only if solver input/output scripts require it | Core OrcaWave/OrcaFlex/AQWA engineering workflows. |
| `assetutilities` | `/mnt/ace/assetutilities` or local managed clone | `/mnt/local-analysis/assetutilities` preferred | optional | Shared Python utilities used by engineering repos. |
| `worldenergydata` | `/mnt/ace/worldenergydata` or local managed clone | `/mnt/local-analysis/worldenergydata` preferred | no | Energy/BSEE data processing. |
| `assethold` | `/mnt/ace/assethold` or local managed clone | `/mnt/local-analysis/assethold` if finance/data tasks are routed to ace-linux-2 | no | Asset/finance analysis. |

### Tier 2/project repos: mirror only if work is routed there

| Repo/bucket | Preferred home | ace-linux-2 policy |
|---|---|---|
| `client_projects` | `/mnt/ace/client_projects` | NFS read/write only with explicit project scope; do not clone/mirror wholesale. |
| `acma-projects` | `/mnt/ace/acma-projects` | NFS read/write only for assigned project; large at ~1.8T. |
| `docs` | `/mnt/ace/docs` | NFS read/write only; large at ~3.4T. |
| `data` | `/mnt/ace/data` | NFS read/write only; large at ~772G. |
| `O&G-Standards` | `/mnt/ace/O&G-Standards` | NFS read-only/default; standards/licensing sensitivity. |
| OSS solvers (`gmsh`, `capytaine`, `HAMS`, `MoorDyn`, etc.) | `/mnt/ace/<repo>` | NFS read or selective clone only when active. |

### Current observed repo state

- `ace-linux-1` local workspace: `/mnt/local-analysis/workspace-hub`.
- `ace-linux-1` `/mnt/ace` contains Git repos including `aceengineercode`, `capytaine`, `frontierdeepwater`, `gmsh`, `HAMS`, `MoorDyn`, `MoorPy`, `openfast`, `opm-common`, `WEC-Sim` and large data/project buckets.
- `ace-linux-2` currently has Git repos under `/mnt/local-analysis`: `workspace-hub`, `cli-anything-repo`.
- Earlier readiness showed `ace-linux-2` can see many repo buckets through `/mnt/remote/ace-linux-1/ace`, but local clones for Tier 1 repos still need normalization if we want fast direct work there.

---

## 3. Mount and file-access matrix

| Storage / data class | ace-linux-1 path | ace-linux-2 path | Windows path | Policy |
|---|---|---|---|---|
| Primary workspace | `/mnt/local-analysis/workspace-hub` | `/mnt/local-analysis/workspace-hub` observed; registry still says stale `/mnt/workspace-hub` | `D:\workspace-hub` | Fix registry/cron drift before automation. |
| Knowledge/raw-data center | `/mnt/ace` | `/mnt/remote/ace-linux-1/ace` via NFS | not verified | Canonical rawdata, llm-wikis, standards, project buckets live here. |
| ace-linux-2 bulk local disk | sshfs remote at `/mnt/remote/ace-linux-2/dde` from ace-linux-1 | `/mnt/dde` | not applicable | Use for ace-linux-2 local heavy preprocessing/cache. |
| Elements ingest drive | `/mnt/elements` mounted but currently effectively empty in this check | not verified | not applicable | Use only via established ingest conventions. |
| Windows solver workspace | not mounted from Linux | not mounted from Linux | `D:\workspace-hub` | Git-backed queue is the reliable bridge. |

Verified capacities:

| Path | Capacity finding |
|---|---|
| `ace-linux-1:/mnt/ace` | 7.3T total, 6.4T used, 533G free, 93% used. |
| `ace-linux-1:/mnt/local-analysis` | 932G total, 210G used, 723G free. |
| `ace-linux-2:/mnt/local-analysis` | 932G total, 53G used, 879G free. |
| `ace-linux-2:/mnt/dde` | 2.8T total, 2.0T used, 848G free. |
| `ace-linux-2:/mnt/remote/ace-linux-1/ace` | NFS view of `/mnt/ace`, 533G free. |

---

## 4. AI program availability

| Tool | ace-linux-1 | ace-linux-2 | Policy |
|---|---|---|---|
| `claude` | present | present | Use for implementation/review where quota allows. |
| `codex` | present | present | Use for coding/reviews and batch runs. |
| `gemini` | present | present | Use for adversarial review / cross-checks. |
| `hermes` | present | present | ace-linux-1 remains control surface; ace-linux-2 can be worker/control if config parity is proven. |
| `gh` | present | present | GitHub issue/PR/queue operations possible on both. |
| `git` | present | present | Repo sync possible on both. |
| `uv` | present | present | Python commands should use `uv run`. |
| `tmux` | present | present | Parallel/background terminal sessions possible. |
| `python3` | present | present | Use through `uv run` by policy. |

---

## 5. Engineering/simulation program availability

| Program/class | ace-linux-1 | ace-linux-2 | licensed Windows | Policy |
|---|---|---|---|---|
| Gmsh | not rechecked in this pass | present | optional | ace-linux-2 can run meshing/preprocessing. |
| FreeCAD | not rechecked in this pass | present | optional | ace-linux-2 can run CAD/preprocessing. |
| Blender | not rechecked in this pass | present | optional | ace-linux-2 can run visualization/previews. |
| ParaView / `pvbatch` | not rechecked in this pass | present with X-cookie warning | optional | ace-linux-2 can run headless post-processing after warning is resolved/accepted. |
| CalculiX | not rechecked in this pass | present | optional | ace-linux-2 can run OSS FEA. |
| QGIS/GDAL | not rechecked in this pass | present | optional | ace-linux-2 can run GIS workflows. |
| OrcaWave | not target | absent | target | Run only on licensed Windows hosts. |
| OrcaFlex / `OrcFxAPI` | not target | absent | target | Run only on licensed Windows hosts. |
| AQWA/ANSYS | not target | absent | target | Run only on licensed Windows hosts. |
| MATLAB | not target | absent | unknown | Do not depend on ace-linux-2. |

---

## 6. Rawdata, llm-wikis, and knowledge sources

### Canonical location

Treat `/mnt/ace` on `ace-linux-1` as the canonical knowledge/raw-data center. From `ace-linux-2`, the corresponding path is:

```text
/mnt/remote/ace-linux-1/ace
```

### Large buckets observed

| Bucket | Size observed | Role |
|---|---:|---|
| `/mnt/ace/docs` | ~3.4T | Document corpus / likely raw docs and knowledge artifacts. |
| `/mnt/ace/acma-projects` | ~1.8T | Project bucket; use project-scoped access only. |
| `/mnt/ace/data` | ~772G | Raw and processed data bucket. |
| `/mnt/ace/client_projects` | ~250G | Client/project data; scope and confidentiality required. |
| `/mnt/ace/digitalmodel` | ~106G | Engineering repo/data/docs. |
| `/mnt/ace/O&G-Standards` | ~43G | Standards corpus; default read-only. |

### Policy

- Do not copy these buckets wholesale to ace-linux-2.
- Use NFS paths for read-mostly access.
- Use local `/mnt/dde` or `/mnt/local-analysis` only for job-specific scratch/cache.
- Manifests should reference large data by stable path + checksum, not embed/copy large binaries into Git.

---

## 7. Minimum readiness tasks before deploying work directly from ace-linux-2

1. **Repo baseline**
   - Ensure local clones on ace-linux-2 for: `workspace-hub`, `digitalmodel`, `assetutilities`, `worldenergydata`.
   - Optional per workload: `assethold`, `aceengineer-admin`, `achantas-data`.
   - Keep giant project/data buckets as NFS paths, not clones.

2. **Path baseline**
   - Fix `config/workstations/registry.yaml`: ace-linux-2 `workspace_root` should be `/mnt/local-analysis/workspace-hub`, or create/test a compatibility symlink `/mnt/workspace-hub`.
   - Replace stale crontab entries on ace-linux-2 with generated entries from canonical scheduled-task config.

3. **Mount baseline**
   - Verify ace-linux-2 can read/write a scoped test path under `/mnt/remote/ace-linux-1/ace`.
   - Define permission policy for rawdata/client folders before allowing automation writes.

4. **AI baseline**
   - Verify `claude`, `codex`, `gemini`, `hermes`, `gh`, `git`, `uv`, and `tmux` auth/config parity on ace-linux-2.
   - Record quota/auth status without storing tokens.

5. **Solver baseline**
   - Keep ace-linux-2 solver role as preprocess/ingest only.
   - Bootstrap licensed Windows hosts separately for actual OrcaWave/OrcaFlex/AQWA execution.

6. **Operational baseline**
   - Add machine inventory checks as a repeatable script/report before launching multi-machine work.
   - Gate direct deployment from ace-linux-2 on a clean repo, correct branch, and synced origin state.

---

## 8. Recommended immediate next issue split

1. `fix(workstations): normalize ace-linux-2 repo/mount/path readiness`
   - local clones, registry path, crontab path, mount smoke tests, AI auth parity.
2. `feat(solver-queue): inbox ingestion and manifest routing`
   - queue/dropbox mechanics, no AQWA execution yet except schema/router support.
3. `feat(solver-queue): AQWA Windows runner adapter`
   - live Windows Task Scheduler + ANSYS/AQWA command proof.

This sequencing keeps the deployment foundation separate from the solver automation layer.
