# Session handoff — tmux persistence (#3784), codex retry (#3578), dispatch verification (#3740)

> **Date:** 2026-08-02 → 2026-08-03
> **Machine:** ace-linux-1 (dispatch surface)
> **Exit state:** all work committed and pushed; nothing deployed to any machine
> **Blocking on:** human merge of PR #3791 after CI re-run

---

## Entry prompt for the next session

```
Continue workspace-hub#3784 (tmux persistence). All repo-side work is done and
pushed on branch fix/3784-tmux-persistence; PR #3791 is open.

Preflight:
  gh pr checks 3791                    # confirm the Scheduler Mutation Surface Guard is green
  gh run view <run-id> --json conclusion --jq .conclusion   # 'cancelled' renders as 'fail' in pr checks
  git -C /mnt/local-analysis/workspace-hub log --oneline origin/main..origin/fix/3784-tmux-persistence

If green -> hand the owner the merge line (do NOT self-merge).
After merge -> rollout R1..R6, ace-linux-2 FIRST, gated on the R2 smoke.
```

---

## What shipped

### #3578 — codex compact-retry (IMPLEMENTED, not closed)

Branch `fix/3578-codex-retry-stdin` @ `4ea9d923c`.

**Diagnosis outcome: no code fix was warranted.** The hang does not reproduce on codex-cli 0.146.0 —
`submit-to-codex.sh` exits 0 on a small payload and on a **26 KB** plan file (5,029 B of real
structured review), against an acceptance criterion written for 12 KB. The version guard already
passes (installed 0.146.0 ≥ ceiling 0.130.0, past the openai/codex#19945 band), and `</dev/null`
isolation is intact on both the first call and the retry.

Deliverable is therefore the regression lock: `scripts/review/tests/test_submit_codex_retry.sh`,
6 mock-driven tests, no live provider call and no quota spend.

**Not closed** — two owner calls outstanding: the plan-stage review artifacts its header names were
never produced, and whether a "nothing is broken" outcome should close the issue or keep it as a
watch item.

### #3740 — dispatch lifecycle (VERIFIED, rescoped, left open)

The wall is broken. All four `dispatch:*` labels exist, and three durable records show state
advancing end-to-end; wh#3757 and #3759 reached `done` with the label projected. Current spread:
`ready` **638**, `done` **2**. The mechanism is proven but has been exercised twice — that is a
throughput/adoption problem, not the structural dead end the issue describes.

Filed **#3788** from that verification: `reconcile.py:707` builds its label snapshot from
`route.fetch_open_issues()` (`--state open`), so **every closed issue reports a false
`LABEL-MISSING`**. Since a `done` issue is the one most likely to be closed, this corrupts exactly
the completion reporting deckhand#584 §4 depends on.

### #3784 — tmux persistence (ALL REPO-SIDE WORK DONE)

Branch `fix/3784-tmux-persistence` @ `cc56646af`, PR **#3791**. **57/57** tmux tests, **119/119**
scheduler enforcement tests, shellcheck clean, legal PASS, checker `REAL_RC=0`.

| Artifact | Purpose |
|---|---|
| `config/tmux/autoattach.sh` | guarded auto-attach, sourced from `~/.bashrc` |
| `scripts/tmux/tmux-autosave.sh` | attach-independent save wrapper |
| `config/tmux/tmux-autosave.{service,timer}` | `OnBootSec=5min`, no `Persistent=` |
| `scripts/install/setup-tmux-autosave-timer.sh` | governed installer |
| `scripts/enforcement/scheduler_mutation_dispositions.py` | **new** — extracted pinned contract |
| `scripts/setup/deploy-tmux.sh` | pinned plugin install, backup, bashrc block, chain check |
| `config/tmux/tmux.conf` | plugin absence warns on `client-attached` |
| `config/tmux/start-session.sh` | one canonical session name, gpu-claw case |

---

## Load-bearing decisions (do not silently revert)

1. **No `exec tmux`** in the auto-attach guard. `exec` behaves identically while tmux is healthy, but
   a tmux that cannot start then closes the connection — on the dispatch surface that leaves no way
   in to repair it. Two tests pin the non-`exec` form.

2. **The autosave wrapper calls `continuum_save.sh`, never resurrect's `save.sh`.** Adversarial
   review refuted the original design: **no durable restore-in-progress marker exists**
   (`restore.sh:19` `RESTORING_FROM_SCRATCH` is a process-local shell variable). `continuum_save.sh`
   already carries a PID-keyed auto-expiring lock, an interval self-throttle, and the timestamp
   bookkeeping the defect was measured from. The timer is a **second writer by construction**, so
   that lock is required, not decorative.

3. **`OnBootSec=5min`, no `Persistent=`.** At a fresh server start
   `@continuum-save-last-timestamp` defaults to 0, so an early tick saves over an in-flight restore.
   `Persistent=` is separately inert on a monotonic timer.

4. **The registry declares `missing_transaction`, not `reference_transaction`** — see #3792. The
   reference shape is proven by `python-*-v1` attestations analysing a Python crontab
   implementation; nothing equivalent exists for a shell systemd-unit installer. Declaring the
   stronger flags would be vocabulary reading as capability.

5. **The 400-line cap was NOT raised.** `scheduler_mutation_contract.py` was at exactly 400;
   constants were extracted to a sibling module instead. Relaxing a guard so a change fits under it
   is the failure the guard exists to prevent.

---

## Remaining work

- [ ] **PR #3791** — CI re-run needed after `cc56646af`; then human merge (agent must not self-merge)
- [ ] Rollout R1–R6, **ace-linux-2 first**, gated on the smoke check before ace-linux-1
- [ ] gpu-claw needs `git pull` before deploy — its clone is 6 commits behind `origin/main`
- [ ] **#3788** — reconcile.py open-only snapshot (repro + acceptance criteria filed, unplanned)
- [ ] **#3792** — systemd-user transaction attestation (unplanned)
- [ ] **#3578** — owner call on closing
- [ ] **#3740** — rescope or split the 638-at-ready adoption problem

---

## Repo / machine state at exit

| | State |
|---|---|
| `fix/3784-tmux-persistence` | `cc56646af`, pushed, verified on remote by content |
| `fix/3578-codex-retry-stdin` | `4ea9d923c`, pushed, verified |
| `plan/3784-tmux-persistence` | `3948a1da4`, pushed |
| Working tree | left on `fix/3784-tmux-persistence`; `.claude/state/*` dirty = **auto-sync, not mine** |
| ace-linux-1 | no tmux server, no stale sockets |
| ace-linux-2 | no tmux server, no stale sockets |
| Deployed anywhere | **nothing** |

**Both `overnight` sessions were killed** after verifying neither was computing — both parked at
idle prompts, and ace-linux-1's pending action (worldenergydata PR #1054) had been merged nine days
earlier. Transcripts persist independently at `~/.claude/projects/-mnt-local-analysis/`
(`c2b08463-…jsonl` is the ace-linux-1 session, verified by content). This removed the riskiest
rollout steps: there is no live session left to rename.

**No external actions taken** beyond GitHub issue/PR writes. No emails, no client-facing surfaces,
no deployments.

---

## Verification traps hit this session

Recorded because each produced a **confident wrong signal**, and several nearly caused a "fix" to
working code.

| Trap | Consequence |
|---|---|
| `cmd \| tail; echo $?` reports **tail's** status | Claimed the scheduler checker passed when it returned 1; the false claim reached a commit message and the PR body |
| The scheduler checker reads the **git index**, not the working tree | An unstaged fix validates the OLD bytes; identical error after a correct fix |
| `gh pr checks` renders **`cancelled` as `fail`** | Nearly sent me hunting a defect that did not exist |
| `gh label list --limit 200` truncated | A label read as nonexistent; concluded "nothing was ever written" |
| `search/issues … is:open` | Hid the two closed `dispatch:done` issues — the same blind spot as the #3788 defect |
| `set -i` is rejected by bash | Every should-fire test failed against a **correct** guard |
| Structural asserts matching their subject's **comments** | Three tests failed against correct files; fixed with a comment-stripping helper |
| `PATH` leaking `/usr/bin` into a "binary absent" case | The wrapper found the real tmux and probed this host's real server |
| `close` is an **awk builtin** | `-v close=…` is a runtime error |
| A 0-byte artifact read **mid-flight** | Matched a known failure signature exactly; posted a wrong root-cause to #3578, retracted |

Saved as `feedback_inflight_artifact_looks_like_known_failure`; the rest are in commit messages and
on the issues.

---

## Environment notes for the next session

- **Four Claude sessions shared this checkout.** One ran `git checkout main` plus what looked like
  `git clean -fd` mid-work and deleted an untracked test file. Commit each TDD step immediately;
  do not leave work untracked.
- **Auto-sync pushes silently.** Three `push` calls returned `[rejected]` or `Everything
  up-to-date` because the branch had already been pushed. Always verify by content
  (`git cat-file -e origin/<branch>:<path>`), never by push output.
- `systemctl` is auto-denied to the agent — the `mx-720-cnh-source-watch` timer disable remains an
  owner action (14th unactioned ask).
