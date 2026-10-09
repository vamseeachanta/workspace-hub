# Workstation hygiene — agent rule

**Agent work uses `git worktree`, never a full second clone; worktrees and caches are removed
when their work is on origin; bulky solver output leaves Git for `/mnt/ace` with a hash
manifest and a second copy; parallel sessions on one machine divide work before starting it.**

**Why:** on 2026-10-07 a Windows workstation's 475 GB system drive reached 0 bytes free and
every agent's `git` write failed with "No space left on device". The cause was eight full
clones of digitalmodel made by Codex tasks (about 49 GB of duplicate packs and virtual
environments) plus a 16 GB npm cache. The work in every clone was already merged; only the
residue remained. The same day, one riser PR proposed committing 7,300 per-case result files
(888 MB) that would have tripled the private data repository for good.

**How to apply:**

1. **Worktrees, not clones.** Start isolated work with
   `git -C <canonical checkout> worktree add <root>/wt-<repo>-<topic> -b <branch> origin/main`.
   Where a sandbox makes `.git` read-only, a clone into the job's temporary directory is the
   fallback, and it is deleted once its branch is pushed. Never leave a clone at the workspace
   root.
2. **Remove what is on origin.** After a PR merges, follow [`merge-cleanup.md`](merge-cleanup.md).
   At session close, and whenever free space drops below about 10 % of the drive, run
   `scripts/operations/workstation-hygiene.sh` (report only). It lists duplicate clones,
   linked worktrees and caches, and marks each SAFE, DIRTY or UNPUSHED. `--apply` removes only
   SAFE items; `--apply --caches` also prunes npm, uv and pip caches. DIRTY and UNPUSHED items
   are reported to the owner, never deleted.
3. **Bulky regenerable output does not go into Git.** Per-case solver results and similar
   bulk files move to `ace-linux-1:/mnt/ace/data/<repo>/<topic>/` (GA01 layout). The repository
   keeps a manifest (relative path, bytes and SHA-256 for every file; archive name, SHA-256 and
   location), a restore/verify helper, a `.gitignore` entry for the moved pattern, and the small
   files reviews read (ledgers, summaries, inputs). Reference implementation:
   digitalmodel-data `data/riser-global-analysis/derived/w4/` (`RESULTS-MANIFEST.json`,
   `results_archive.py`). Merge such a PR with a squash so the bulk never reaches `main` history.
4. **Two copies.** `/mnt/ace` is a single disk with no RAID or backup job (checked 2026-10-07).
   Mirror each archive to a second host's own disk (not an NFS view of `/mnt/ace`), verify the
   SHA-256 there, and record every location in the manifest.
5. **Divide work across live sessions.** Before picking up an item, list peer sessions on the
   machine and message them with the items you intend to take; skip any a peer owns. Record
   ownership on the issue or PR when a peer may not read messages in time.
6. **Blocked actions go to the owner.** When the permission classifier refuses a merge, a
   deletion or a settings change, the action becomes a card on the owner's decision board
   ([`human-decision-boards.md`](human-decision-boards.md)) with the exact command. It is never
   retried through another tool, subagent or session.

**Do NOT apply when:** a worktree is locked, or holds uncommitted work that nobody has
reviewed; the bulk files are raw data as received, which stay in the owning private
repository per [`codes-standards-data-routing.md`](codes-standards-data-routing.md).

**Enforcement gradient** (per [`patterns.md`](patterns.md)): Level 2 script
`scripts/operations/workstation-hygiene.sh`, report-first. Promote to a scheduled report once
it has run clean on each host.

**Related:** [`merge-cleanup.md`](merge-cleanup.md), [`merge-authorization.md`](merge-authorization.md),
[`windows-junction-restore-safety.md`](windows-junction-restore-safety.md). Handoff:
`docs/session-handoffs/2026-10-07-session-consolidation.md`.
