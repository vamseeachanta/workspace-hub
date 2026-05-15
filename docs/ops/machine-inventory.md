# Machine inventory — control-plane dispatch readiness

> **Owner:** Vamsee Achanta
> **Issue:** [#2548](https://github.com/vamseeachanta/workspace-hub/issues/2548)
> **Sources:** `config/workstations/registry.yaml` (canonical for ssh/workspace/capabilities), `docs/ops/2026-05-04-multimachine-baseline-inventory.md` (program availability), `docs/BUSINESS_BRAIN.md` §AI Provider Accounts (provider plan)
> **Purpose:** Per `docs/BUSINESS_BRAIN.md` §Machines: "Machine inventory must answer installed programs, license availability, AI-provider auth state, repo checkout locations, run/smoke-test commands, and what work may be dispatched safely."

---

## How to read this doc

Each machine row records the same five BUSINESS_BRAIN-mandated dimensions:

1. **Programs / licenses** — engineering and tooling binaries available on the host (OrcaFlex, ANSYS, OpenFOAM, etc.)
2. **AI-provider auth** — which agent CLIs are authenticated on the host (claude / codex / gemini / hermes); "unverified — no SSH" if the host has `ssh: null` in registry and has not been physically probed during this inventory
3. **Repos** — repos clone-mirrored on the host (registry `repos:` field)
4. **Smoke / run command** — the canonical one-liner to confirm the host is reachable and capable of accepting dispatched work; "N/A" if no SSH and no remote control surface
5. **Dispatch readiness** — `ready` / `partial` / `blocked` plus the specific blocker if not `ready`

Path placeholders used in the rows below (see canonical values in the reference block at the end of this doc):

| Placeholder | Resolves to |
|---|---|
| `<linux-workspace-root>` | Linux workspace clone root (ace-linux-1, ace-linux-2) |
| `<windows-workspace-root>` | Windows workspace clone root (licensed-win-*) |
| `<macos-workspace-root>` | macOS workspace clone root (macbook-portable) |
| `<ace-knowledge-root>` | ace-linux-1 NFS knowledge / data center root |
| `<ace-knowledge-root-from-secondary>` | NFS view of `<ace-knowledge-root>` from ace-linux-2 |
| `<ace-linux-2-bulk-root>` | ace-linux-2 bulk local disk |

---

## Inventory

### ace-linux-1 — `dev-primary` (Linux, primary control plane)

| Dimension | Value |
|---|---|
| Programs / licenses | python3, bash, uv, git, gh, npm, claude CLI, gemini CLI, hermes; NFS server for `<ace-knowledge-root>`; no GPU; no OrcaFlex/ANSYS/AQWA (open-source engineering stack lives on ace-linux-2) |
| AI-provider auth | claude (Claude Max, primary planning/orchestration), gemini (Google AI Pro), codex (verify per `docs/BUSINESS_BRAIN.md` §AI Provider Accounts before allocating load), hermes (control plane) — all confirmed authenticated per 2026-05-04 baseline §4 |
| Repos | `worldenergydata`, `digitalmodel`, `assetutilities`, `assethold`, `workspace-hub`, `OGManufacturing` (registry `dev-primary.repos`); plus `<ace-knowledge-root>` clones of `aceengineercode`, `capytaine`, `frontierdeepwater`, `gmsh`, `HAMS`, `MoorDyn`, `MoorPy`, `openfast`, `opm-common`, `WEC-Sim` (NFS-exported) |
| Smoke / run command | `ssh ace-linux-1 'cd <linux-workspace-root> && git status -sb'` |
| Dispatch readiness | **ready** — primary control plane; runs all nightly scheduled tasks; sources of truth for cron + queue + skills + plans |

---

### ace-linux-2 — `dev-secondary` (Linux, overflow worker / open-source simulation)

| Dimension | Value |
|---|---|
| Programs / licenses | python3, bash, uv, git, gh, tmux, claude CLI, codex CLI, gemini CLI, hermes; **open-source engineering stack**: blender, openfoam, freecad, gmsh, paraview / pvbatch, calculix, meshio, capytaine, qgis/gdal; GPU: nvidia-t400; no OrcaFlex/ANSYS/AQWA (licensed-only) |
| AI-provider auth | claude (parity confirmed per 2026-05-04 baseline §4), codex (present), gemini (present), hermes (present); ace-linux-1 remains canonical control plane for GitHub mutation and dispatch ledgers |
| Repos | `digitalmodel`, `worldenergydata` (registry `dev-secondary.repos`); recommended additions per baseline §2: `workspace-hub`, `assetutilities`; large project buckets read via NFS at `<ace-knowledge-root-from-secondary>` only |
| Smoke / run command | `ssh ace-linux-2 'cd <linux-workspace-root> && git status -sb'` |
| Dispatch readiness | **ready** for OSS engineering preprocessing (meshing, CAD, post-processing) and parallel AI execution; **blocked** for licensed-solver workloads — route OrcaFlex/OrcaWave/AQWA to licensed-win-* |

---

### licensed-win-1 (Windows, simulation-license host)

| Dimension | Value |
|---|---|
| Programs / licenses | **orcaflex (licensed)**, **ansys (licensed)**, git (MINGW64 / git-bash); claude CLI, codex CLI, gemini CLI installed per registry capabilities |
| AI-provider auth | **unverified — no SSH**. Registry lists `[claude, codex, gemini]` as agent_clis but auth state requires physical/GUI verification |
| Repos | `OGManufacturing` (registry `licensed-win-1.repos`); `workspace-hub` at `<windows-workspace-root>` (git-poll target, evidenced by `queue/failed/wamit-val-hemisphere/result.yaml`) |
| Smoke / run command | N/A from Linux — no SSH. Indirect smoke: submit a no-op job via `scripts/solver/submit-job.sh orcaflex <input> "smoke test"` and verify `queue/processing/` or `queue/done/` reflects pickup within 30 min |
| Dispatch readiness | **ready** for OrcaFlex via existing git-backed queue (`scripts/solver/submit-job.sh` → push to `queue/pending/` → 30-min `git pull` cycle on the host → solver runs, writes result yaml + artifacts, pushes back). **blocked** for AQWA — queue schema does not yet accept `solver: aqwa`; tracked by [#2641](https://github.com/vamseeachanta/workspace-hub/issues/2641) |

---

### licensed-win-2 (Windows, simulation-secondary)

| Dimension | Value |
|---|---|
| Programs / licenses | Mirrors licensed-win-1 per registry: orcaflex (licensed), ansys (licensed), git; **requires physical verification** for exact license edition + ANSYS module set |
| AI-provider auth | **unverified — no SSH** (same as licensed-win-1) |
| Repos | `OGManufacturing` (registry `licensed-win-2.repos`); `workspace-hub` at `<windows-workspace-root>` assumed but unverified |
| Smoke / run command | N/A from Linux — no SSH. Indirect smoke would require queue extension to support secondary-host targeting; not implemented |
| Dispatch readiness | **partial** — queue dispatch currently routes only to licensed-win-1 (single-host poll); licensed-win-2 is preferred AQWA fallback/parallel target per 2026-05-04 baseline §1 but **requires queue host-routing extension** (not in current schema). Until then: treat as cold standby, manual dispatch only |

---

### macbook-portable (macOS, portable manual dev)

| Dimension | Value |
|---|---|
| Programs / licenses | python3, bash, uv, git, gh, claude CLI; no GPU; no engineering solvers; macOS home-directory path conventions differ from Linux (see `<macos-workspace-root>` in the reference block) |
| AI-provider auth | claude (present per registry); codex/gemini/hermes not listed — verify before allocating planning load |
| Repos | `workspace-hub` at `<macos-workspace-root>` (registry `macbook-portable.repos`); other repos cloned manually as needed |
| Smoke / run command | N/A from Linux — no SSH from Linux hosts. Local smoke: `cd <macos-workspace-root> && git status -sb` |
| Dispatch readiness | **partial** — no cron; uses manual / launchd scheduling; not in nightly dispatch path. Use for travel / mobile interactive sessions only |

---

### gali-linux-compute-1 — `shoerack` (Linux, future GPU compute)

| Dimension | Value |
|---|---|
| Programs / licenses | python3, bash, cuda; **2x RTX 3090 (48 GB VRAM), 128 GB RAM**; no engineering solvers; not yet onboarded to workspace |
| AI-provider auth | **none configured** (registry `agent_clis: []`) |
| Repos | none (registry `repos: []`) |
| Smoke / run command | N/A — access method TBD (Tailscale or direct LAN per registry note) |
| Dispatch readiness | **blocked** — not yet onboarded; boot drive at 89% per registry notes; route heavy ML/CUDA workloads here only after onboarding |

---

### home-win (Windows, off-hours workstation)

| Dimension | Value |
|---|---|
| Programs / licenses | **unknown** — registry entry: **none**; not in `config/workstations/registry.yaml` |
| AI-provider auth | **unverified** — not in registry |
| Repos | **unknown** — not in registry |
| Smoke / run command | N/A — no registry entry, no SSH configuration |
| Dispatch readiness | **blocked** — **add to `config/workstations/registry.yaml` before scheduling work**. Appears only in BUSINESS_BRAIN.md §Machines table |

---

### acma-ws014 (Windows, on-site ACMA workstation)

| Dimension | Value |
|---|---|
| Programs / licenses | **unknown** — registry entry: **none**; not in `config/workstations/registry.yaml` |
| AI-provider auth | **unverified** — not in registry |
| Repos | **unknown** — not in registry; likely `acma-projects` per machine name |
| Smoke / run command | N/A — no registry entry, no SSH configuration |
| Dispatch readiness | **blocked** — **add to `config/workstations/registry.yaml` before scheduling work**. Appears only in BUSINESS_BRAIN.md §Machines table |

---

## OrcaFlex dispatch — documented dry-run

The control plane dispatches OrcaFlex (and OrcaWave) work to licensed-win-1 via the **Git-backed solver queue**. No SSH is involved — the Windows host polls `queue/pending/` every 30 minutes via `git pull`.

**Workflow (verified path):**

1. **Submit:** From any control-plane host, run `scripts/solver/submit-job.sh orcaflex <input_file> "<description>"`. The script:
   - Validates the solver type (`orcaflex` or `orcawave`).
   - Validates that `<input_file>` exists relative to repo root.
   - Writes `queue/pending/<TIMESTAMP>-<basename>.yaml` matching the schema at `queue/job-schema.yaml`.
   - Commits and pushes to `origin/main`.

2. **Pickup:** licensed-win-1 runs a scheduled `git pull` every 30 minutes (per 2026-05-04 baseline §1 decision and `queue/job-schema.yaml` polling assumption).

3. **Execute:** The Windows-side runner moves the YAML from `queue/pending/` → `queue/processing/`, invokes OrcaFlex with `<input_file>`, writes outputs (`result.yaml`, optional `.xlsx`, log artifacts) into a sibling directory, then moves the job YAML to `queue/done/` (or `queue/failed/` on error).

4. **Reconcile:** Control plane sees the completion when the Windows host's next `git push` lands.

**Evidence on disk:** `queue/failed/wamit-val-hemisphere/result.yaml` confirms the loop has executed for OrcaWave at least once (queue path on the Windows side resolved to `<windows-workspace-root>\...`).

**Smoke procedure:** `scripts/solver/submit-job.sh orcaflex <small-input.dat> "smoke test"` — wait up to 30 min — check `queue/processing/`, then `queue/done/` for the timestamped YAML.

---

## AQWA dispatch — current gap

AQWA dispatch is **not currently supported** by the queue schema. Per `queue/job-schema.yaml`, the `solver:` field only accepts `orcawave` or `orcaflex`. `scripts/solver/submit-job.sh` explicitly rejects any other value:

```bash
if [[ "${SOLVER}" != "orcawave" && "${SOLVER}" != "orcaflex" ]]; then
    echo "ERROR: solver must be 'orcawave' or 'orcaflex', got '${SOLVER}'" >&2
    exit 1
fi
```

AQWA queue-schema extension is **tracked by [#2641](https://github.com/vamseeachanta/workspace-hub/issues/2641)** (multimachine solver inbox ingestion). This inventory documents the gap; resolving it is out of scope for #2548.

---

## Reference paths

The placeholders used throughout this doc resolve as follows. These are the only absolute paths in this file; they appear here once with explicit allowlist markers so future plans can reference them by name. Canonical source: `config/workstations/registry.yaml`.

```yaml
linux-workspace-root: /mnt/local-analysis/workspace-hub  # abs-path-allowed
windows-workspace-root: 'D:\workspace-hub'  # abs-path-allowed
macos-workspace-root: /Users/krishna/workspace-hub  # abs-path-allowed
ace-knowledge-root: /mnt/ace  # abs-path-allowed
ace-knowledge-root-from-secondary: /mnt/remote/ace-linux-1/ace  # abs-path-allowed
ace-linux-2-bulk-root: /mnt/dde  # abs-path-allowed
```

---

## Related issues

- [#2641](https://github.com/vamseeachanta/workspace-hub/issues/2641) — multimachine solver inbox ingestion (AQWA queue extension)
- [#2548](https://github.com/vamseeachanta/workspace-hub/issues/2548) — this issue (inventory + OrcaFlex/AQWA dispatch documentation)
- `docs/BUSINESS_BRAIN.md` — §Machines, §AI Provider Accounts (this doc fulfills the BUSINESS_BRAIN.md mandate to record the five inventory dimensions)
- `docs/ops/2026-05-04-multimachine-baseline-inventory.md` — detailed baseline + repo placement + mount matrix
