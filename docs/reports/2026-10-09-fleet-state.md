# Fleet workspace state — 2026-10-09

**Survey time:** 2026-10-10T04:20Z (2026-10-09 23:20 local). **Scope:** seven
machines, eleven canonical repositories. **Machine names:** public fleet labels
only. **Surface:** this repository is public; file names from uncommitted work,
account addresses, network addresses and user names are omitted by design.

This report supersedes the workspace columns of the 2026-10-07 machine readiness
matrix for the date above. It records state at the survey time; the hub and the
licensed-runs queue receive automated commits several times an hour, so a
checkout recorded as current trails by those commits shortly afterwards.

## 1. Result

The comparator for every row is the `main` branch tip of the repository on the
remote, read with `git ls-remote` at survey time. A checkout is `current` when
it is on `main` and its HEAD equals that tip.

| Machine | Workspace root | Canonical repos current | Not current | Reason for the remainder |
|---|---|---|---|---|
| ace-linux-1 | `/mnt/ace/ws` | 10 of 11 | 1 | Client wiki in use by the licensed-run agent |
| ace-linux-2 | `/mnt/local-analysis` | 10 of 11 | 1 | Client wiki in use by the licensed-run agent; local history diverged |
| ace-win-1 | `D:\ws` | 8 of 11 | 3 | Solver job and licensed-run agent in progress |
| ace-win-2 | `C:\ws` | 11 of 11 | 0 | n/a |
| gpu-claw | `~/ws` | 9 of 11 | 2 | Licensed-run watchdog and agent in progress |
| mac-1 | `~/Developer/ws` | 6 of 11 | 5 | Private remotes unreadable from a remote session; two private repos absent |
| spark-1 | `~/ws` | 6 of 11 | 5 | Private repos not placed on this machine (decision, section 6) |

Caption: Table 1 — canonical repositories level with the remote `main` tip, by machine.

Before this pass the same seven machines stood at: ace-linux-1 hub 2 behind with
six canonical repos off `main`; ace-linux-2 second hub checkout 483 behind;
ace-win-1 hub 113 behind and two canonical repos absent; ace-win-2 queue
checkout 25,216 behind inside an unfinished rebase; gpu-claw three canonical
repos absent; mac-1 one canonical public repo absent; spark-1 no workspace.

## 2. Machine by repository matrix

Cell format: state; branch when not `main`; `m` modified tracked files; `u`
untracked files. `current` is as defined in section 1. `behind-N` is N commits
behind the remote `main` tip. `-` is no working-tree change. `absent` is not
cloned. `unread` is a remote that could not be read from the survey session, so
currency is Not Evaluated.

| Repository | Visibility | ace-linux-1 | ace-linux-2 | ace-win-1 | ace-win-2 | gpu-claw | mac-1 | spark-1 |
|---|---|---|---|---|---|---|---|---|
| workspace-hub | public | current; m17 | current; m8 | current; m8 u2 | current; m7 u2 | current | current | current |
| digitalmodel | public | current; u3 | current | behind-241; `docs/issue-2157-plan-20260925`; u1 | current; m1 | behind-371; `test/issue-1911-single-tank-amplitude`; m1 | current | current |
| worldenergydata | public | current | current | current; m2 | current; m2 u16 | current | current | current |
| assetutilities | public | current | current | current; m2 | current | current | current | current |
| deckhand | private | current; u3 | current; u4 | behind-3 | current | current; u3 | absent | absent |
| deckhand-licensed-runs-queue | private | current | current | current | current | current | absent | absent |
| llm-wiki | private | current; u1 | current | current | current | current | unread; u2 | absent |
| llm-wiki-&lt;client&gt; | private | behind-116 | behind-1144, 915 local-only | behind-4; u1 | current; u6 | behind-1144, 861 local-only; u1 | unread | absent |
| worldenergydata-wiki | public | current | current | current | current | current | current | current |
| aceengineer-admin | private | current | current; u1 | current | current; u3 | current | unread | absent |
| raw-to-knowledge-playbook | public | current | current | current | current | current | current | current |

Caption: Table 2 — state of each canonical repository on each machine at survey time.

Notes to Table 2:

- The modified files in every `workspace-hub` cell are machine-runtime state
  written by scheduled jobs and agent sessions. They were carried through the
  fast-forward and not committed.
- `m2` in the `worldenergydata` and `assetutilities` cells for ace-win-1 is the
  intentional link residue described in `.claude/rules/windows-junction-restore-safety.md`.
  It is not uncommitted work.
- `u` counts are as `git status` reports them: an untracked directory counts once.
- ace-linux-2 holds a second hub checkout under `~/ws`; it is `current` with no
  working-tree change.
- ace-linux-1 exposes its workspace to ace-linux-2 as a network mount. That
  mount was not operated on from ace-linux-2.

## 3. Actions taken

| Machine | Fast-forwarded | Returned to `main` | Rescued then synced | Cloned | Held, unchanged |
|---|---|---|---|---|---|
| ace-linux-1 | 3 | 2 | 5 | 0 | 1 |
| ace-linux-2 | 7 | 0 | 3 | 0 | 2 |
| ace-win-1 | 4 | 0 | 1 | 2 | 4 |
| ace-win-2 | 8 | 0 | 3 | 0 | 0 |
| gpu-claw | 3 | 0 | 1 | 3 | 4 |
| mac-1 | 3 | 0 | 2 | 1 | 5 |
| spark-1 | 0 | 0 | 0 | 6 | 5 |

Caption: Table 3 — count of canonical checkouts by action. ace-linux-2 counts twelve checkouts (two of the hub). For mac-1 and spark-1 the last column includes repositories that are absent.

Specific interventions:

1. **ace-win-2, licensed-runs queue.** The checkout had been inside an
   unfinished rebase since 2026-09-01, on a detached HEAD carrying 1,872
   heartbeat commits that were on no remote. Those commits were pushed to a
   rescue branch and verified, the rebase was aborted, and the checkout was
   fast-forwarded to `main`. A heartbeat from this machine reached the remote
   `main` at 2026-10-10T03:42Z, the first since 2026-09-13.
2. **ace-win-2, deckhand.** One commit on a feature branch whose upstream had
   been deleted was pushed to a rescue branch; the checkout was returned to `main`.
3. **Stale lock files.** Two empty `index.lock` files with no owning process
   were removed: `worldenergydata-wiki` on ace-win-2, and `assetutilities` on
   ace-linux-1 (dated 2026-08-02).
4. **Missing repositories.** `worldenergydata-wiki` and
   `raw-to-knowledge-playbook` were cloned on ace-win-1; `worldenergydata`,
   `worldenergydata-wiki` and `aceengineer-admin` on gpu-claw; `worldenergydata`
   on mac-1; the six public repositories on spark-1.
5. **Operations not used.** No force-push, no `git reset --hard`, no stash, no
   hook bypass, no branch, worktree or repository deletion, and no login,
   credential, scheduler or system-package change was made on any machine.

## 4. Rescue branches

Uncommitted or unpushed work was preserved before any branch move. Rescue
branches in private repositories were pushed, and each was confirmed by
comparing the local commit with the remote ref. Rescue branches in public
repositories were kept local, following Phase 0 of
`docs/plans/2026-10-08-objective-first-working-style.md`, which requires a
secrets and client-data review before work in progress is pushed to a public
repository.

| Machine | Repository | Branch | Commit | Content | Remote |
|---|---|---|---|---|---|
| ace-win-2 | deckhand-licensed-runs-queue | `rescue/ace-win-2-2026-10-09` | `33c7dc97b` | 1,872 heartbeat commits | Pushed, verified |
| ace-win-2 | deckhand | `rescue/ace-win-2-2026-10-09` | `3de8dbabb` | 1 commit | Pushed, verified |
| ace-win-2 | llm-wiki | `rescue/ace-win-2-2026-10-09` | `918da2478` | 4 modified, 4 new files | Pushed, verified |
| ace-linux-1 | deckhand | `rescue/ace-linux-1-2026-10-09` | `f3a58bba7` | Working-tree state | Pushed, verified |
| ace-linux-1 | llm-wiki | `rescue/ace-linux-1-2026-10-09` | `068b869c7` | Working-tree state | Pushed, verified |
| ace-win-1 | llm-wiki | `rescue/ace-win-1-2026-10-09` | `6a5da64d0` | 1 modified file | Pushed, verified |
| ace-linux-2 | aceengineer-admin | `rescue/ace-linux-2-2026-10-09` | `603d8c619` | 4 files, identical to `main` | Pushed, verified |
| ace-linux-1 | digitalmodel | `rescue/ace-linux-1-2026-10-09` | `fe19a2b1f` | 1 automated lockfile commit | Local only |
| ace-linux-1 | worldenergydata | `rescue/ace-linux-1-2026-10-09` | `97ffbb461` | 1 new test helper | Local only |
| ace-linux-1 | worldenergydata | `rescue/ace-linux-1-2026-10-09-b` | `314dc26f` | 1 automated lockfile commit | Local only |
| ace-linux-1 | assetutilities | `rescue/ace-linux-1-2026-10-09` | `1b38089c8` | 72 modified files | Local only |
| ace-linux-2 | digitalmodel | `rescue/ace-linux-2-2026-10-09` | `404c1ecad` | 4 commits | Local only |
| ace-linux-2 | workspace-hub (second checkout) | `rescue/ace-linux-2-2026-10-09` | `090bbb8fa` | 5 files | Local only |
| gpu-claw | workspace-hub | `rescue/gpu-claw-2026-10-09` | `ed9a5c5cb` | 218 paths | Local only |
| mac-1 | workspace-hub | `rescue/mac-1-2026-10-09` | `8ad86c74d` | 4 documents | Local only |
| mac-1 | digitalmodel | `rescue/mac-1-2026-10-09` | `57904572` | 2 commits | Local only |

Caption: Table 4 — rescue branches created on 2026-10-09.

### 4.1 Review of the local-only branches

Each local-only branch was compared with `main` path by path. The criterion for
proposing content was that it be absent from `main`, be source or test code
with no data, credential or authority content, and pass the repository's pinned
lint tools.

| Machine | Repository | Finding | Disposition |
|---|---|---|---|
| ace-linux-1 | worldenergydata | The test helper is imported by a test on the published branch `fix/3787-startup-tax` and was never committed there. | Pushed as branch `fix/3787-startup-tax-helper` (`9c9036e2f`), formatted with the pinned black 25.9.0 and isort 8.0.1; flake8 7.3.0 passes. The tests were not run. A pull request has not been opened. |
| ace-linux-1 | digitalmodel; worldenergydata `-b` | Lockfile-only automated commits dated 2026-08-02; `main` carries a later lockfile. | Stays local. No further use identified. |
| ace-linux-1 | assetutilities | 67 regenerated test outputs and 5 files that differ only in a timestamp. | Stays local. No further use identified. |
| ace-linux-2 | digitalmodel | 2 of 4 paths are identical to `main`; the remainder is a lockfile and one plan document. | Stays local. |
| ace-linux-2 | workspace-hub (second checkout) | 3 generated reports and 2 runtime-state files. | Stays local. |
| gpu-claw | workspace-hub | 179 of 218 paths are identical to `main`; 15 are earlier versions of files on `main`; 24 differ, and these are agent-instruction and authority documents dated 2026-10-05. | Stays local. Changes to agent authority are an owner decision. |
| mac-1 | workspace-hub | 3 data-ownership documents dated 2026-09-08 absent from `main`, and an earlier draft of one document now on `main`. | Stays local pending owner review of data references. |
| mac-1 | digitalmodel | Data curation: inventory data, a dataset ledger, and related source and tests. | Stays local pending a source-rights review of the data. |

Caption: Table 5 — review outcome for each local-only rescue branch.

## 5. Accounts and command-line tools

Account labels are those of `config/ai-tools/ai-accounts.yaml`. The binding was
read with `scripts/ai/assessment/collect-account-usage.py`, which reports a
fingerprint and never an address. "Headless" is a one-token task run
non-interactively over SSH with exit code 0 as the criterion.

| Machine | Claude Code | Claude account | Claude headless | Codex CLI | Codex account | Codex headless |
|---|---|---|---|---|---|---|
| ace-linux-1 | 2.1.295 | claude-owner | Pass | 0.162.0 | codex-owner | Pass |
| ace-linux-2 | 2.1.295 | claude-owner | Pass | 0.162.0 | codex-owner | Pass |
| ace-win-1 | 2.1.296 | claude-professional | Pass | 0.162.0 | codex-professional | Pass |
| ace-win-2 | 2.1.296 | claude-owner | Not Evaluated | 0.162.0 | codex-owner | Not Evaluated |
| gpu-claw | 2.1.295 | claude-owner (login expired) | Fail | 0.162.0 | codex-owner (session rejected) | Fail |
| mac-1 | 2.1.295 | Not established from a remote session | Not Evaluated | 0.162.0 | codex-owner | Not Evaluated |
| spark-1 | Not installed | n/a | n/a | Not installed | n/a | n/a |

Caption: Table 6 — installed command-line tool versions, bound accounts and headless result.

Findings:

- ace-win-1 runs both tools on the professional accounts, as assigned. It is
  the only machine on those accounts, so work dispatched there draws on a
  separate usage allowance from the five machines on the owner accounts.
- ace-win-2 is assigned the professional accounts in `ai-accounts.yaml` and is
  bound to the owner accounts. Correcting this requires an interactive login.
- ace-linux-1 reported an expired Claude access token before the headless
  task. The task refreshed it; no login was required.
- gpu-claw fails on both tools: Claude reports an expired session that cannot
  be refreshed, and Codex is rejected with an authorisation error. Both require
  an interactive login.
- mac-1 keeps Claude credentials in the system keychain, which a remote session
  cannot read; the binding is therefore not established here.

Other tools: `git`, `gh`, `uv` and `node` are present on all six machines that
hold a full workspace. `gh`, `git` and `node` are present on spark-1; `uv` is
not. The bare `python` command is absent on the three Linux machines
(`python3` is present). On gpu-claw `uv` is installed outside the
non-interactive PATH. On ace-win-1 `gh auth status` exits non-zero because of a
stale stored entry while the active account works.

`scripts/enforcement/check-soul-deployment-drift.sh` exits 0 on ace-linux-1,
ace-linux-2 and gpu-claw. It exits 1 on ace-win-1 (Claude runtime blocked;
two provider runtimes absent). It was not run on ace-win-2, mac-1 or spark-1.

## 6. Held and blocked items

| Item | Machine | State | What releases it |
|---|---|---|---|
| digitalmodel | ace-win-1 | On a documentation branch, 241 behind. A licensed solver run and a parallel Python run were using the checkout's environment. | Completion of the runs; then `git checkout main` and `git merge --ff-only origin/main`. |
| deckhand; client wiki | ace-win-1 | 3 and 4 behind. The licensed-run agent executes from one and uses the other as its scope root. | A quiet point in the agent's cycle; fast-forward only. |
| digitalmodel | gpu-claw | On a test branch, 371 behind, one modified lockfile. Named as the solver root of the licensed-run watchdog. | Owner decision on the watchdog's checkout. |
| Client wiki | ace-linux-2, gpu-claw | Local `main` shares no common ancestor with the remote `main`; 915 and 861 commits respectively are absent from the remote `main`. On ace-linux-2 those commits are contained in a remote backup branch. On gpu-claw 494 commits are on no remote and about 10,000 files are untracked. | Owner decision. The pattern is consistent with a rewrite of the remote history; that cause is a hypothesis and was not established. |
| Client wiki | ace-linux-1 | Clean, 116 behind, in use as the licensed-run agent's scope root. | A quiet point in the agent's cycle; fast-forward only. |
| Private repositories | mac-1 | Three present but unreadable from a remote session; two absent. Git credentials are held in the system keychain. | A local, unlocked session on the machine. |
| Private repositories | spark-1 | Not cloned. The machine is administered by another party and holds no Git credential. | Owner decision on whether private and client content may reside there. |
| Account logins | gpu-claw, ace-win-2 | See section 5. | Interactive login by the owner. |
| Pull request | n/a | Branch `fix/3787-startup-tax-helper` is pushed in `worldenergydata`; the pull request is not opened. | Owner action. |
| Scheduled repository sync | gpu-claw | A four-hourly job on this machine contains add, commit and push steps. Its behaviour against the now-clean public hub checkout is not established. | Owner review before its next cycle is relied on. |
| Display driver | ace-linux-2 | See section 7. | Owner action with administrative rights. |

Caption: Table 7 — items left unchanged, with the condition that releases each.

Uncommitted work carried in place on ace-win-2 and not committed: one modified
file in `digitalmodel`; two modified and sixteen untracked paths in
`worldenergydata`; six untracked paths in the client wiki, where a data intake
is in progress; three untracked paths in `aceengineer-admin`.

## 7. ace-linux-2 display driver

**Observed (read-only, 2026-10-10, 03:15Z to 04:25Z).**

- `nvidia-smi` fails: it cannot communicate with the driver.
- The running kernel is `7.0.0-31-generic`. No NVIDIA kernel module is
  installed for it and none is loaded.
- `linux-modules-nvidia-580-open-generic-hwe-24.04` is installed at
  `7.0.0-28.28`; the archive candidate is `7.0.0-38.38`. Kernels `-28`, `-31`
  and `-38` are installed. The system flags a pending reboot.
- No package is held (`apt-mark showhold` returns nothing).
- `/etc/apt/apt.conf.d/50unattended-upgrades` still lists `"nvidia"` and
  `"libnvidia"` in its package blacklist, and the unattended-upgrades log
  records NVIDIA packages as blacklisted on 2026-10-09.

**Not established.** The log contains no line naming the modules meta-package
itself as blacklisted. That the blacklist is what left the modules package at
`-28` while kernels advanced is therefore a hypothesis, consistent with the
mechanism recorded in
`docs/session-handoffs/2026-06-04-ace-linux-2-nvidia-hold-drift-fix.md`, and
not a finding of this pass.

**Not applied.** The change needs administrative rights, which require a
password on this machine, and takes effect only after a reboot. Meshing and
solver processes were running at the time of the survey.

**Commands for the owner**, to be run in a terminal on ace-linux-2. They follow
the procedure that restored the driver on 2026-06-04, plus the recurrence step
that handoff left open. They were not executed in this pass.

```bash
# 1. Confirm no solver or meshing job is running. The last step reboots.
pgrep -af 'mpirun|simpleFoam|interFoam|snappyHexMesh' || echo "no solver running"

# 2. Record the current state.
uname -r
apt-mark showhold | grep -i nvidia || echo "no nvidia holds"
dpkg -l | grep -E 'linux-modules-nvidia|nvidia-driver|nvidia-kernel-common'

# 3. Recurrence step: stop unattended-upgrades from excluding the NVIDIA stack.
#    The backup is written outside apt.conf.d so that apt does not parse it.
sudo cp -a /etc/apt/apt.conf.d/50unattended-upgrades /var/backups/50unattended-upgrades.bak-20261009
sudo sed -i -E 's|^([[:space:]]*)"(lib)?nvidia";|\1// "\2nvidia";|' /etc/apt/apt.conf.d/50unattended-upgrades
grep -n -i nvidia /etc/apt/apt.conf.d/50unattended-upgrades   # both entries now begin with //

# 4. Release any hold, then bring the driver stack level with the newest kernel.
apt-mark showhold | grep -i nvidia | xargs -r sudo apt-mark unhold
sudo apt-get update
sudo apt-get full-upgrade

# 5. Confirm a module package exists for the newest installed kernel.
dpkg -l | grep -E 'linux-modules-nvidia-580-open-[0-9]'

# 6. Reboot only when step 1 reports no job.
sudo reboot

# 7. After the reboot.
uname -r
nvidia-smi
systemctl status gdm3 --no-pager | head -5
```

Acceptance is `nvidia-smi` listing the adapter and `gdm3` active after the
reboot. If the display manager sits at the greeter, `sudo systemctl restart
gdm3` re-triggers the automatic login, as recorded in the 2026-06-04 handoff.

## 8. Method and limits

- One agent per machine ran a written protocol; the final matrix was then
  re-surveyed from a single script (`git ls-remote` against each remote, no
  fetch) so that Table 2 does not depend on the agents' own reports.
- A checkout was left unchanged when a lock file, an in-progress Git operation,
  a process running from it, or a file modified in the preceding 30 minutes was
  found.
- The live-activity check on ace-linux-1 cannot see processes on ace-linux-2
  that use the same tree through the network mount; file modification time was
  the only evidence available for that case.
- Non-canonical repositories and worktrees (77 on ace-linux-1, 40 on
  ace-linux-2, 45 on ace-win-1, 2 on gpu-claw) were surveyed without change and
  are not listed here.
- Engineering readiness of any checkout — environments, datasets, licences —
  was not assessed. `current` describes the Git revision only.
