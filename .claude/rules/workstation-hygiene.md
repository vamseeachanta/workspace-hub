# Workstation hygiene — agent rule

**Agent work uses `git worktree`, never a full second clone; worktrees and caches are removed
when their work is on origin; bulky output and cold reference files leave Git through the
manifest-and-fetch layout in `docs/standards/DATA_PLACEMENT.md`; parallel sessions on one
machine divide work before starting it.**

**Why:** on 2026-10-07 a Windows workstation's 475 GB system drive reached 0 bytes free and
every agent's `git` write failed with "No space left on device". The cause was eight full
clones of digitalmodel made by Codex tasks (about 49 GB of duplicate packs and virtual
environments) plus a 16 GB npm cache. The work in every clone was already merged; only the
residue remained. The same day, one riser PR proposed committing 7,300 per-case result files
(888 MB) that would have tripled the private data repository for good.

On 2026-11-24 a shared Windows host had both data drives at 10 to 14 % free. About fifteen
folders sat at the drive roots (`tmp`, `c`, `d`, `mnt`, `etc`, `x`, `invalid\path\that\does\not\exist`),
each a POSIX path that a script had resolved against a Windows drive root, and a retired
solver-manager loop still held about 396 GB of working folders. Items 7 to 11 come from that
baseline (#4532).

**How to apply:**

1. **Worktrees inside `_wt/`, not clones or root `wt-*` folders.** Start isolated work with
   `git -C <canonical checkout> worktree add <workspace root>/_wt/<repo-short>--<slug> -b <branch> origin/main`.
   Keep `<workspace root>/_wt/` strictly to linked git worktrees — never place loose files,
   scratch directories, virtual environments, or standalone clones inside `_wt/`.
   Where a sandbox makes `.git` read-only, a clone into the job's temporary directory is the
   fallback, and it is deleted once its branch is pushed. Never leave a clone at the workspace
   root. A long-running job locks its worktree (`git worktree lock --reason <job>`) and unlocks
   it when done, so cleanup never removes a worktree in use.
2. **Remove what is on origin.** After a PR merges, follow [`merge-cleanup.md`](merge-cleanup.md).
   At session close, and whenever free space drops below about 10 % of the drive, run
   `scripts/operations/workstation-hygiene.sh` (report only). It lists duplicate clones,
   linked worktrees and caches, and marks each SAFE, DIRTY, UNPUSHED, LOCKED or IN USE (a process running inside it, Linux). `--apply` removes only
   SAFE items; `--apply --caches` also prunes npm, uv and pip caches. DIRTY and UNPUSHED items
   are reported to the owner, never deleted.
3. **Bulky output and cold reference files do not go into Git.** Per-case solver results,
   large generated artifacts and cold non-source references use the one manifest-and-fetch
   layout in [`DATA_PLACEMENT.md`](../../docs/standards/DATA_PLACEMENT.md): committed manifest,
   one fetch script and content-addressed blobs under `${ACE_DATA_ROOT}/data/<repo>/`.
   A removal PR merges only after the stored copy is verified, and after the second copy is
   verified for data that cannot be re-downloaded. Raw data as received stays in the owning
   private repository. Data already stored under the earlier per-topic archive layout stays
   where it is and remains recorded in its own manifest; new moves use the one layout. No
   conversion duty is introduced.
4. **Two copies.** Data that cannot be re-downloaded gets a verified second copy on a second
   machine's own disk, not a network view of the primary disk, recorded in the manifest.
   Re-downloadable public data keeps a maintained fetch script instead of a second copy.
5. **Divide work across live sessions.** Before picking up an item, list peer sessions on the
   machine and message them with the items you intend to take; skip any a peer owns. Record
   ownership on the issue or PR when a peer may not read messages in time.
6. **A refused command stops that step:** report the exact command and never get the same
   result another way (another tool, subagent, session or model).
7. **Scratch stays local to the task.** Temporary work goes to the OS temp dir or the
   repository's git-ignored `.tmp/`. A retired desk, loop or job queue has its working
   folders inventoried and dispositioned the day it is retired, not left behind.
8. **No POSIX absolute paths in Windows-run commands.** A native Windows program resolves
   `/tmp/x`, `/mnt/x` or `/c/x` against the current drive root, which creates `C:\tmp`,
   `D:\mnt` or `C:\c`. Use the platform temp directory, `${ACE_DATA_ROOT}` or a path derived
   from the repository root. Tests build "nonexistent" paths under their own temporary
   directory, never `/invalid/...`.
9. **Baseline, plan, then clean.** Measure with `scripts/hygiene/fleet_baseline.py` (all hosts)
   or `scripts/hygiene/host_baseline.py` (one host), then tier the result with
   `scripts/hygiene/cleanup_plan.py`. Baselines name hosts and paths, so they are written to a
   private repository, never this public one. `--apply` runs only the `regenerable` and
   `safe-checkout` tiers, with a log; every `review` item goes to the owner of the data or to a
   decision card. Deletions beyond those tiers are logged on fleet-ops #577 and archived (commit bundle
   plus change archive, two verified copies on two machines) before they run.
10. **Shared hosts.** On a host with other tenants, anything outside the team's own roots
    (`--own-roots`) is reported and never touched.
11. **After a history rewrite, check the archive before calling work unpushed.** Following
    the 2026-11-23 lean archive, a HEAD absent from origin may still be held in the archive
    bundles. Pass their commit list with `cleanup_plan.py --preserved`; a HEAD found in neither
    origin nor an archive is unpushed work and stays.
12. **Registered work root (`W`) layout — repos + reserved system dirs only.** Every
    machine follows [`config/workstations/ws-root-policy.yaml`](../../config/workstations/ws-root-policy.yaml):
    - Top-level `<workspace root>/` holds **only registered git repositories** (directories with
      `.git/`) plus the reserved `_` system folders (`_wt`, `_pm`, `_backups`, `_archive`) and `.claude`.
    - Zero loose files at `<workspace root>/`; zero duplicate or ad-hoc prefixes (`_backup`,
      `.wt`, `.scratch`, `_scratch`, `_scratch-*`, `wt-*`, `outputs`, `*.pre-rollout-*`, `*.failed-checkout`).
    - Every deliverable (script, doc, plan, review, dataset manifest) belongs inside its
      destined repository; temporary scratch goes to the OS temp dir or the repository's git-ignored `.tmp/`.
    - W is the machine's registered work root; a home-directory alias, where present,
      links to W and is never traversed or deleted.
    - Verify any host with `python scripts/workstations/ws_hygiene_audit.py --root <workspace root>`.

**Do NOT apply when:** a worktree is locked, or holds uncommitted work that nobody has
reviewed; the bulk files are raw data as received, which stay in the owning private
repository per [`codes-standards-data-routing.md`](codes-standards-data-routing.md).

**Enforcement gradient** (per [`patterns.md`](patterns.md)): Level 2 scripts
`scripts/operations/workstation-hygiene.sh` (checkouts on one host),
`scripts/workstations/ws_hygiene_audit.py` (workspace-root layout & `_wt/` purity against
`ws-root-policy.yaml`), and `scripts/hygiene/fleet_baseline.py` + `cleanup_plan.py` (storage
across hosts, #4532), all report-first. Run the fleet baseline monthly and whenever a drive falls below about 15 % free;
promote to a scheduled report under #3992 once it has run clean on each host.

**Related:** [`merge-cleanup.md`](merge-cleanup.md), [`merge-authorization.md`](merge-authorization.md),
[`windows-junction-restore-safety.md`](windows-junction-restore-safety.md). Handoff:
`docs/session-handoffs/2026-10-07-session-consolidation.md`.
