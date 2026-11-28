---
name: machine-readiness
description: Bring the current machine to the workspace standard using a dry census, reviewed cleanup manifests, a six-hour consistency run and a measured readiness verdict.
version: 1.0.0
---

# Machine readiness

## When to use

Use for onboarding, drift correction or a stale-worktree sweep on **this machine**. Work one physical host and one reviewed batch at a time. Keep machine details, manifests and receipts in the private `fleet-ops` repository. A files-only reviewer can initiate the same procedure through the authorized machine manager.

## The standard in ten lines

1. Resolve one work root `W` on local disk. Count aliases to it once.
2. Keep one canonical lean clone per registered repository directly under `W`, clean and fast-forwardable on its registered base.
3. Put linked task worktrees in `W/_wt/<repo-short>--<slug>` using lowercase names. Record each task, branch, HEAD and outputs.
4. Use `W/_pm/` for machine automation, work records, reports and the manager's pinned runner.
5. Keep verified recovery bundles, patches and manifests in `W/_backups/`, with an independent second copy.
6. Use `W/_archive/` for cold material with a SHA-256 manifest.
7. Reserve `W/.claude/` for workspace-level configuration.
8. Allow only the registered clones and those five reserved entries at the top of `W`. No loose files at the root and no `_scratch` anywhere.
9. Put scratch in OS temp or a repository's git-ignored `.tmp/`.
10. Place bulk solver output on the designated data store with a committed manifest. Retain originals in the owning private repository.

## Ground the run

Verify the host, physical root, account, tenant boundary and existing sessions. Check who may inspect private files, post receipts, remove items and register a schedule. An advisory session works from supplied evidence and routes commands to the authorized executor. A prompt or an issue log alone grants no destructive authority.

From each authorized canonical clone run `git fetch origin`. Record the fetched SHAs. Read the generic standards in `workspace-hub/docs/knowledge-maps/README.md` and the matching private `fleet-ops/docs/knowledge-maps/<map>.yaml` at the fetched map revision. Start with this host's entries and deviations in `machines.yaml`, `file-structure.yaml` and `repos.yaml`. Resolve roles from `org-team.yaml`, provider scope from `ai-seats.yaml` and skill locations from `skills.yaml`.

Read `fleet-ops/ECOSYSTEM.md`, the ledger revision's `fleet-ops/machine-manager/act-<host>.md` and `fleet-ops/intake/cleanup/{MACHINE-CLEANUP-PROMPT,CLEANING-RUNBOOK,WORK-LIFECYCLE}.md`. Read by ref when the maps and act list are on different branches. Recheck dated findings against the physical machine. Use the file-structure map for placement if an older helper proposes `_scratch` or a single-hyphen worktree name. Hold any operation whose root, authority or tool revision is unresolved.

## Census and classification

Inventory the agreed root and other **owned** candidate roots, including off-root clones. Record each real path, purpose, size, volume free space and measurement time. Probe links and Windows junctions before measuring. Keep mounted or FUSE volumes in a separate scoped census. Never traverse another tenant's files. Cross-check the inventory against registered repos, `git worktree list --porcelain`, holds, open PRs, work records, worker prompts, live sessions, processes and scheduled-task scripts and working directories.

Use the reviewed tools from `fleet-ops`. In the examples, substitute each uppercase path with a quoted native path. Use fresh receipt paths outside the candidates. In **both** sweep calls replace `W` with disjoint, verified owned roots if a full-root walk could enter a protected or uninspected subtree. Exclusions do not limit discovery.

Three evidence checks are easy to miss:

- **Ledger references count as use.** A worktree named in the private ledger's `intake/**` desk logs, pass prompts or act lists is in use even when no local file names it. Collect them with `git grep` on the fetched ledger. A reference counts when it equals the worktree path or lies beneath it; a reference to a parent folder does not. Inventory, census, sweep and receipt files list every worktree, so they are not evidence of use; exclude the sweep's own output folder from the local scan for the same reason.
- **Earlier refusals stay refused.** Keep a refused-paths list beside each host's receipts and subtract it before building a batch. A path git refused once is refused again until its cause is resolved.
- **Audit reads must not touch the index.** Run every evidence-gathering git command with `GIT_OPTIONAL_LOCKS=0` (for example `GIT_OPTIONAL_LOCKS=0 git -C <wt> status --porcelain`). A plain `git status` refreshes the index file, which resets the 12-hour idle clock and makes the reviewed tool keep the row until the next day.
- **Clean means clean to git.** Run `git status --porcelain --ignore-submodules=none` in the worktree; any output means git's unforced remove will refuse it. That is the exact command `git worktree remove` runs (`check_clean_worktree` in `builtin/worktree.c`). Its output can differ from a file-by-file scan: with `core.untrackedCache` holding a stale entry, git 2.43 lists an empty folder (`?? dir/`) that a file scan finds empty.

Map each process directory, script path and hold to every candidate that **contains it or lies beneath it**. Pass the entire affected worktree as `--exclude HELD`, repeated for each one in both calls. Omit the option when the verified hold list is empty. `MERGED` holds the per-repo merged-PR evidence. If temporary fetch refs are outside read-only census authority, omit `--merged-prs MERGED` from both calls and retain detached trees without independent restore evidence.

```sh
python intake/cleanup/tools/wt_sweep.py W --merged-prs MERGED --exclude HELD --out DRY_JSON --manifest SAFE_TSV
python intake/cleanup/tools/clone_retire.py REPO
```

The first command previews linked worktrees. The second inventories one standalone clone. On Linux and macOS, the reviewed wrapper `intake/cleanup/tools/sweep_dryrun.sh OUT TOOLDIR ROOT...` runs the first command with `GIT_OPTIONAL_LOCKS=0`. It also writes the scheduler, process and recent-brief references to `OUT/*-refs.txt`, leaving out its own output and earlier receipts. Put the merged-PR evidence in `OUT/merged-prs/` first, and use `SWEEP_PY` to choose a Python 3.11 or newer interpreter. Capture stdout and stderr and account for paths neither tool visited. From the pinned hub run `python scripts/operations/check-work-layout.py --json --host HOST --private-config PRIVATE_LAYOUT` with the verified private layout file for this host. Confirm the policy resolves the observed `W`. A missing checker, registry or reading leaves layout unverified.

| Class | Evidence and disposition |
|---|---|
| LOCKED | Git lock or explicit hold. Keep it locked and untouched. |
| IN USE | A live process, worker, solver lane, schedule, open job or recent activity needs the path. Keep it. Unreadable usage or uncertain ownership also means keep. |
| DIRTY | Inspect staged, unstaged, untracked, non-cache ignored files, submodules and stashes. Preserve changes before considering retirement. |
| UNPUSHED | The current tip or its content cannot be verified on the fetched origin. Keep it even if the worktree is clean or a local ref or backup exists. |
| SAFE | Owned, idle, unlocked and unreferenced. The tree is clean, the work is verified on origin, declared outputs have been retained, and the reviewed sweep accepts it. |

Locks, use and uncertainty take precedence. **Nothing touched in the last 12 h may be changed.** Check file, directory, HEAD and index activity, protected data, agent memory, verified archives and other tenants. Retain anything the checks cannot clear. Use `work.py` records to trace outputs. A `solver_run_match.py` byte match helps locate files but cannot release a dataset or a licensed solver lane. Follow the hub's `.claude/rules/licensed-solver-dispatch.md` for live work.

Check the repo and base of each merged PR and match its actual head SHA. After a squash or history reset, compare **every changed path** (including renames and deletions) against the freshly fetched base, including `origin/intake/ledger` where applicable. Preserve detached commits through a verified restore ref or merged head. Branch names, ancestry across a reset and the sweep's SAFE label alone cannot establish that the work landed. Never push from pre-reset clones or publish backup refs.

## Review, log, archive and remove

**Review the manifest.** Present the full census, keep reasons, expected savings and proposed actions for independent review under the cleanup prompt. Copy only cleared SAFE rows verbatim from `SAFE_TSV` into the reviewed UTF-8 manifest. Each headerless row contains the absolute path, full branch ref (empty if detached) and full HEAD SHA, separated by tabs in that order. Pin the reviewed bytes. List DIRTY or UNPUSHED items separately for preservation. Keep LOCKED, IN USE and other protected items outside the apply list.

**Log before acting.** Record the review, selection rules, exact batch and counts, planned backup locations and restore commands on private `fleet-ops #577`. Resolve the issue from the private clone. Confirm the entry can be read back and the action and destination are authorized before applying. Keep the machine reachable.

**Archive non-SAFE work eligible for retirement.** Use the reviewed `wt_archive.py` to capture a full, independently restorable Git bundle plus a change archive. Include the required refs, detached commits, stash history, staged and unstaged binary patches, and untracked and non-cache ignored files. Record file sizes, SHA-256 and restore instructions. Screen artifacts for secrets before copying. For a whole clone, use `clone_retire.py --prepare` with its documented copy parameters.

Restore from the bundle into an empty repository, compare refs and files, and test patch applicability on a fresh lean base while the source exists. Use `wt_replica.py` to replicate to a second authorized machine's own disk. Read and hash **both** copies of the bundle and change archive on their respective machines against the manifest. For a clone, run `clone_retire.py --check-copy` and verify the stated second host independently. Missing tools, failed restoration or a missing replica keep the source in place. An archive receipt alone never changes a row to SAFE.

**Remove through the reviewed tool only.** For each reviewed SAFE worktree use an exact one-row copy of the pinned manifest as `ROW_TSV` and distinct outputs per row. Immediately beforehand recheck holds for the whole worktree, ownership, activity and landed evidence. Before **any** deletion probe the candidate, its ancestors and descendants for links or junctions without following them. On Windows inspect `(Get-Item -LiteralPath $path -Force).LinkType` and reparse attributes. Keep linked or unresolved paths.

```sh
python intake/cleanup/tools/wt_sweep.py W --merged-prs MERGED --exclude HELD --apply --only ROW_TSV --out APPLY_JSON --manifest REMOVED_TSV
```

The tool rechecks the tuple and eligibility immediately before calling Git's unforced worktree removal. Read the selected row's JSON status and removal TSV before the next row. A refused command, changed tuple, missing row or failed check **stops that step**. Record the command and reason. Never retry through a different tool, agent, forced operation or recursive directory deletion.

On Linux and macOS, `intake/cleanup/tools/sweep_apply_rows.sh OUT TOOLDIR REVIEWED_TSV ROOT...` applies a whole reviewed manifest this way, one row per call. It first refuses the whole file if it has a header, CRLF, a BOM or any row that is not byte-identical to a row of `OUT/sweep-safe.tsv`. It then prints the selection's SHA-256 to compare with the reviewed file, and stops at the first row whose removal is not confirmed.

For a preserved clone or other non-SAFE item, follow the private reviewed-manifest executor in `fleet-ops/intake/cleanup/` only if its own release, backup and quiet-period checks pass for that exact item. `clone_retire.py` only inventories and verifies backups. `work.py close` stages evidence. Neither removes the source. Keep the item if the available executor cannot accept it. Branch deletion is a separate action under `.claude/rules/merge-cleanup.md`.

For approved layout repairs, release dependent worktrees before replacing a pre-reset clone from the fetched lean origin. Route idle task worktrees to `_wt/`, launchers to `_pm/`, and bulk output to its manifested store. Verify Git registration, launcher references and retained hashes after each change. Protect active paths until the owning job releases them.

**Reconcile receipts.** Read back the worktree registry, retained paths and volume free space. Compare full tuples in the reviewed and removed sets. Success requires zero extra, zero left and zero failed for the selected batch. Record any partial result as such. Commit redacted dry-run JSON, reviewed TSV, apply JSON/TSV, tool revision and exact tool, output logs, archive digests and restore proof privately under `fleet-ops/intake/cleanup/receipts/<host>-wt-<tranche>-<date>/`. Post the outcome on the same issue. Keep secrets out of reports and use the private runbook's redaction rules.

## Install the six-hour consistency run

Use `fleet-ops/machine-manager/CONSISTENCY.md`, `consistency-schedule.md` and `UPKEEP.md`. Check the fetched ledger revision for compatible `work.py adopt` and `sweep` interfaces, hub checkers at the fetched hub revision, and Python 3.11 or later with YAML support in the scheduler account. Verify the existing schedule first. Reuse a matching entry.

For an authorized installation, log the exact physical host, account, `W`, runner and cadence on `fleet-ops #577` first. Check the entrypoints in `workspace-hub/config/scheduled-tasks/mutation-surfaces.yaml`. Follow `.claude/rules/scheduler-mutation-safety.md` for locking, baseline, durable backup, compare-and-swap, readback and rollback. If those checks cannot be met, report installation pending.

Install the reviewed bootstrap and matching hourly upkeep writer through the manager. The platform recipe in `consistency-schedule.md` uses `cron-add.sh` with `consistency-boot.sh` on Linux/macOS, or one hidden `FleetOps-Consistency` Scheduled Task with `consistency-boot.ps1` on Windows. Verify the actual six-hour trigger, account and command. The bootstrap fetches and runs the pinned ledger commit in `W/_pm/fleet-ops-run`. Worktree removal stays with the separate reviewed executor.

## Check the structure guides and decide readiness

Account for each entry in `W` against `workspace-hub/config/workstations/ws-structure.yaml` and the private registry. Run `python scripts/operations/check-structure-guide.py REPO --json` from the hub for each registered repository on this machine. Repair stale or missing entries through the owning repo's normal change process. State each folder's purpose to the declared depth in `docs/structure.yaml`, then render `docs/STRUCTURE.md` with `--render`. Recheck the installed guide. An undocumented folder stays on the census until its purpose is established.

Read the actual scheduled run in `W/_pm/consistency/latest.json`. Require the expected host, pinned commit, completion less than 6 h old, and every applicable check complete with zero findings. After the hourly manager and collector run, match `host`, `pinned`, `last_completed` and `counts` in `W/_pm/consistency/state.json`, the `consistency` record in `W/_pm/machine-manager/readiness.json`, and the host row in private `dashboard/machine-readiness.json`.

**Done** requires exit 0 and zero findings from the layout and guide checkers, evidence for the applicable machine-map criteria R01–R16, and a current manager `verdict` of **READY**. Report the recorded reason for AMBER or NOT-READY. Missing, stale, skipped or conflicting required evidence leaves readiness unverified. A clean sweep, scheduler registration or process exit alone cannot establish readiness.

Report the host and resolved root privately, observation time, revisions, checked scope, counts by class, proposed/removed/kept/refused items with reasons, measured free space before and after, and receipt and replica references. Give schedule identity, last completed run, checker counts, native verdict and reason, open findings and the next authorized action.

## Short prompts to paste

**Claude**

```text
Read workspace-hub/.claude/skills/operations/machine-readiness/SKILL.md and run it for this machine.
Start with the private host map and act list. Present the dry census and reviewed manifest before applying.
Report the receipts, checker findings and measured readiness verdict.
```

**Codex**

```text
Use workspace-hub/.claude/skills/operations/machine-readiness/SKILL.md for this machine.
Follow the dry-run, review and receipt gates within this job's authority. Route any remaining action to the manager.
Return checker results, the native readiness verdict and any held items.
```

**Gemini / Agy**

```text
Read workspace-hub/.claude/skills/operations/machine-readiness/SKILL.md for this machine.
Follow the procedure within the session's role. In an advisory lane, review the supplied evidence and route actions to the manager.
Report the verified receipts, checker findings, readiness verdict and any missing evidence.
```
