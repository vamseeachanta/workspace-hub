# Session handoff — tmux fleet rollout (#3784) exit

> **Date:** 2026-08-03
> **Machine:** ace-linux-1 (dispatch surface)
> **Exit state:** all work committed, pushed, and verified on `origin/main` by content
> **Deployed:** all 3 Linux boxes. **2 of 3 fully verified.**
> **#3784 is OPEN** — deliberately, see Blockers

---

## Entry prompt for the next session

```
Continue workspace-hub#3784. Everything is merged (PR #3791) and deployed to
all three Linux boxes. It is NOT closed and should not be closed yet.

Preflight:
  gh issue view 3795 --json state          # the blocker: ace-linux-1 autosave
  gh issue view 3784 --json labels         # gate:completeness needs owner action
  ssh gpu-claw-ts 'ls -lt ~/.tmux/resurrect/ | head -3'        # working
  ssh ace-linux-2  'ls -lt ~/.tmux/resurrect/ | head -3'       # working

First real task is #3795: on ace-linux-1 the autosave timestamp advances but
NO save file is written. Needs operator-run:
  systemctl --user status tmux-autosave.service -n 50
  journalctl --user -u tmux-autosave.service -n 100 --no-pager
(systemctl is agent-denied on that box.)
```

---

## Fleet state

| Check | gpu-claw | ace-linux-1 | ace-linux-2 |
|---|---|---|---|
| Repo current | ✅ | ✅ | ✅ |
| Config symlink | ✅ (26-line original backed up) | ✅ | ✅ |
| Plugins `v4.0.0`/`v3.1.0` | ✅ | ✅ | ✅ |
| Single bashrc auto-attach block | ✅ | ✅ | ✅ |
| Timer active+enabled, `KillMode=process` | ✅ | ✅ | ✅ |
| Session `main` | ✅ | ✅ | ✅ |
| Non-interactive clean (BatchMode/scp) | ✅ | ✅ | ✅ |
| **Save FILE written, zero clients** | ✅ | ❌ **#3795** | ✅ |

**Resurrect's save path differs per box** — `~/.tmux/resurrect` on gpu-claw and
ace-linux-2, `~/.local/share/tmux/resurrect` on ace-linux-1. It derives from XDG
state present when the tmux **server** started. Any health check must cover both;
one hardcoding a single path reports a false failure on two thirds of the fleet.

---

## Why #3784 is not closed

1. **#3795 — ace-linux-1's autosave does not work.** Timestamp advances, no file
   anywhere. Ruled out: `KillMode` (present, and it reproduces outside systemd),
   missing plugins, the interval throttle, the search path, and `save.sh` itself
   (works synchronously — produced a full save at 10:39). Narrowed to: fails only
   when continuum *backgrounds* it, only on this box. That box is the dispatch
   surface **and** where the original 75.8-hour defect was measured, so closing
   would claim the fix works exactly where it was found.
2. **`gate:completeness`** is on the issue — closure needs a computed score plus
   an owner-applied `status:completeness-verified`. The agent records; it cannot
   self-verify.

---

## Load-bearing decisions (do not silently revert)

1. **No `exec tmux`** in the auto-attach guard. This earned itself live: tmux
   genuinely failed on gpu-claw (unknown `TERM`) and the guard handed over a
   working shell. With `exec` every interactive login to that box would have been
   dropped with no way back in to repair it.
2. **Wrapper delegates to `continuum_save.sh`**, never resurrect's `save.sh` —
   inherits the PID-keyed lock, interval throttle and timestamp bookkeeping. The
   timer is a *second writer by construction*.
3. **`KillMode=process`** on the service. Without it systemd tears down the
   cgroup when the oneshot main process exits, reaping the backgrounded save.
4. **`OnBootSec=5min`, no `Persistent=`.** `@continuum-save-last-timestamp`
   defaults to 0 at a fresh server start, so an early tick saves over an
   in-flight restore.
5. **Registry declares `missing_transaction`** — see #3792. No attestation can
   verify a transaction on a *shell* installer writing systemd units.
6. **The 400-line cap was NOT raised** — constants extracted to
   `scheduler_mutation_dispositions.py` instead.

---

## The acceptance criterion was wrong, and that is the main lesson

Original: *"the autosave timestamp advances with zero clients attached."*

A system saving **nothing** satisfies it perfectly. `continuum_save.sh`
backgrounds `save.sh` and *then* calls `set_last_save_timestamp` synchronously in
the parent, so the clock keeps perfect time over an empty directory.

```
zero clients, timer fired:
  @continuum-save-last-timestamp  1785767109 -> 1785770709   ADVANCED
  ~/.tmux/resurrect/                                          no such directory
```

It certified one broken box (fixed: `KillMode=process`) and would have certified
a second (#3795). Amended to assert on the **artifact** — `last` +
`tmux_resurrect_<ts>.txt` + `pane_contents.tar.gz` — and the regression test pins
the unit's directives, not the timestamp.

Saved as `feedback_metric_moved_work_did_not_happen`.

---

## Six defects the rollout found that 57 passing tests did not

| # | Defect | Why the suite missed it |
|---|---|---|
| 1 | `TERM=xterm-ghostty` absent from remote terminfo | needs a real client terminal |
| 2 | Installer committed `100644` | mode correct on disk, wrong in git |
| 3 | `-x` guard said "missing" for a present file | only misleads a human reading real output |
| 4 | SC2148 on the sourced guard | lint not wired into the suite |
| 5 | `KillMode` reaping the backgrounded save | the metric moved; only the artifact was absent |
| 6 | Restore resurrected the stale `overnight` session | needs a real restore cycle |

All six fixed and on `origin/main`. 60/60 tests, legal PASS.

**Restore was observed working end-to-end** on ace-linux-1 — continuum rebuilt a
session from saved state at server start. Note a restored pane wears the
*scrollback* of the work it once held while running plain `bash`; check
`pane_current_command`, not the screen.

---

## Repo / machine state at exit

| | State |
|---|---|
| Working tree | `main`, **0 unpushed**, none of my paths dirty |
| 3784 branches / worktrees | none remaining (all deleted) |
| Backup tag | `backup/pre-3784-drift-reset-2026-08-03` on origin |
| Live session | `main` on ace-linux-1, zero clients |
| Stray processes | none |

**ace-linux-2 drift resolved without the destructive path.** It was 277 behind /
17 ahead with a dirty tree. `reset --hard` was blocked by the safety classifier;
a **merge** achieved the same result non-destructively and *preserved* the 17
auto-sync commits. All 17 were proven `chore(sync): auto-sync` first.

---

## Open items

- [ ] **#3795** — ace-linux-1 autosave (blocks #3784)
- [ ] **#3784** completeness score + owner `status:completeness-verified`
- [ ] **#3788** — `reconcile.py` open-only snapshot → false `LABEL-MISSING` on every closed issue
- [ ] **#3792** — no transaction attestation for systemd-user surfaces
- [ ] **#3578 / #3740** — owner calls on closing / rescoping
- [ ] `mx-720-cnh-source-watch` timer disable — 15th unactioned ask, needs owner `systemctl`

---

## Environment hazards for the next session

- **`/mnt/local-analysis` dropped its NTFS mount mid-session.** `ntfs-3g` stayed
  alive (pid 1544) while the mount detached from the namespace; the path became an
  empty dir on root ext4. Load was low — *not* the process-storm mode. It
  recovered. `gh --repo` works without the mount, which is how work continued.
- **Four Claude sessions share this checkout.** One ran `git checkout main` plus
  what looked like `git clean -fd` and deleted an untracked test file; files were
  reverted under me ~5 times. Commit every TDD step immediately; for multi-file
  edits use one atomic script.
- **Auto-sync pushes silently.** Several pushes returned `[rejected]` or
  `Everything up-to-date` because the branch was already pushed. Always verify by
  content (`git cat-file -e origin/<branch>:<path>`), never by push output.
- **`systemctl` is agent-denied on ace-linux-1** but works over SSH to the other
  boxes — drive verification remotely.
- **Generated artifacts tracked in git** (equality matrices, scheduler audit HTML,
  session manifests) blocked or conflicted on nearly every merge this session.
  #3702 already proposes moving the equality ones out of the tracked tree.

---

## The recurring failure mode, ~10 instances in one session

A query that answers a *narrower* question than the one asked, while looking like
it answered the broad one:

| Trap | What it hid |
|---|---|
| `cmd \| tail; echo $?` reports **tail's** status | a checker returning 1 read as passing; the false claim reached a commit message and a PR body |
| The scheduler checker reads the **git index** | an unstaged fix validates the OLD bytes |
| `gh pr checks` renders **`cancelled` as `fail`** | nearly sent me hunting a defect that did not exist |
| `gh label list --limit 200` truncated | a label read as nonexistent |
| `search/issues … is:open` | hid two closed `dispatch:done` issues — the same blind spot as the #3788 defect |
| `set -i` is rejected by bash | every should-fire test failed against a **correct** guard |
| Structural asserts matching their subject's **comments** | three tests failed against correct files |
| `PATH` leaking `/usr/bin` into a "binary absent" case | the wrapper found the real tmux and probed this host's real server |
| A waiter keyed on a file appearing mid-checkout | a merge ran against a 78%-complete tree |
| A watcher catching **my own** manual save | nearly certified a timer that never fired |

Recorded in `feedback_metric_moved_work_did_not_happen` and
`feedback_inflight_artifact_looks_like_known_failure`.
