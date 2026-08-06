# Session handoff — fleet reachability, cleanup sweep, solver dispatch

**Date:** 2026-07-31 · **Control surface:** ace-linux-1 · **Scope:** fleet-wide branch/worktree sweep, Windows host provisioning, licensed-solver dispatch

---

## Headline

**The fleet went from 3/5 to 5/5 SSH-reachable, and OrcaFlex/OrcaWave/AQWA are now all dispatchable from the control surface.** Neither was true this morning.

Two Windows hosts were provisioned with inbound SSH, a durable job-dispatch mechanism was built and verified, and the licensed-solver access question was settled by measurement after two false conclusions.

---

## 1. Fleet cleanup sweep

Seven agents swept 67 repo checkouts across three machines.

| | ace-linux-1 | gpu-claw | ace-linux-2 | total |
|---|---|---|---|---|
| PRs merged | 10 | 0 | 2 | **12** |
| Local branches deleted | 239 | 3 | 45 | **287** |
| Remote branches deleted | 22 | 1 | 13 | **36** |
| Worktrees removed | 14 | 0 | 2 | **16** |
| **Branches rescued** | 20 | 0 | 17 | **39** |

**~1 in 8 things that looked stale held commits existing nowhere else.** Two outright near-misses where `[gone]` alone would have destroyed real work: a branch whose PR was *closed* unmerged, and one with 3 commits and no PR at all. Both caught only by checking the forge.

Also rescued: two detached HEADs on ace-linux-2 reachable from **zero refs** (anchored and pushed), and a 404-commit archive branch pushed with `GIT_LFS_SKIP_PUSH=1` — its git history is now off-disk, but **its LFS blobs are still local-only** pending an LFS budget raise.

## 2. Windows hosts

Both provisioned with SSH, POSIX shell (`DefaultShell` = Git Bash), exit-code propagation, `uv` Python, and `gh` via machine-level PAT.

- **ace-win-1** — fully green. Repo current, dispatch wrapper present, SessionCuration `rc=0`, firewall tailnet-scoped.
- **ace-win-2** — provisioned and verified, then **went down ~11:00 and is still down**. Tailnet pings 1 ms and ports 22/3389/445/135 all *accept TCP*, but SSH stalls at key exchange and RDP is dead. Kernel accepts, userland cannot service — resource exhaustion (16 GB, ~2.2 GB free), not config. `Restart-Service sshd` does not help. **Needs a power-cycle.**

## 3. Solver dispatch — the settled facts

Full rule in **PR #3739** (`.claude/rules/licensed-solver-dispatch.md`). Summary:

**Two independent lanes, no contention between them:**

| lane | server | slots |
|---|---|---|
| Orcina | `27002` | **1**, shared by OrcaFlex **and** OrcaWave |
| ANSYS | `1055` | **2** `aqwa_solve` + 4 `anshpc` |

- **Never dispatch Orcina products over direct SSH** — the public-key logon token cannot complete a FlexNet checkout (`Error 21`). Use `scripts/windows/dispatch-run.ps1`; a Scheduled Task gets its own batch logon. Verified: SSH fails, dispatch returns `LICENCE_OK`, reproduced twice.
- A `Flex` seat licenses a **session, not a job** — parallel models inside one dispatched job are fine.
- **AQWA runs concurrently with Orcina work.** Do not serialise across lanes.
- **Unmeasured:** OrcaWave's core/RAM draw. Recorded as unknown rather than guessed.

---

## Open work

**PRs awaiting review**

| PR | Note |
|---|---|
| #3739 | Solver-dispatch rule — land first; it prevents re-deriving all of the above |
| #3732 | `update-model-ids.sh` self-corruption fix + 5 regression tests |
| #3733 | **Partial by design** — leaves the scheduler guard red with a *truthful* error. The remaining step is an owner attestation, not a mechanical fix |

**Issues filed:** #3721 (ace-win-2 SSH), #3723 (derive `fleet-ssh-hosts.yml`), #3724 (equality staleness + saturating `memory_files_changed`), #3731 (register dispatch as a mutation surface), #3734 (idle AQWA capacity).

**Closed:** #3720 (premise wrong — SSH already worked), PR #3738 (premise wrong — no credential path needed).

**Needs a human**

1. **Power-cycle ace-win-2.** Capture `Get-Process | Sort-Object WS -Descending` at the console *first* — rebooting destroys the only evidence of what exhausted it.
2. **Raise the LFS budget** on worldenergydata and deckhand-sandbox.
3. **`claude` CLI is missing on ace-linux-2** — the most capable Linux worker has no agent binary.
4. **deckhand#579's Sentinel prerequisite targets the wrong layer** — corrected there with evidence; OrcaFlex is a FlexNet client of a live Orcina daemon.

**Deliberately not done:** `cleanup-digitalmodel.sh` must **not** be run — 83 disjoint remote branches hold the only copy of pre-2026-07-04 history.

---

## Corrections made this session

Recorded because the reasoning is the reusable part:

- **"No `orca*` feature exists"** — false. I queried one FlexNet port and generalised to the host; there are four. Corrected on deckhand#579.
- **"Scheduled tasks inherit the caller's token"** — false, and PR #3738 was built on it before being tested. Task Scheduler creates its own batch logon.
- **"ws014 has no checkout"** — false. A shallow probe hit `C:\ws\.git` and I concluded "no repos"; it holds 11 repos plus 15 worktrees.
- **A test that restated the fix** instead of exercising it — passed against the known-buggy script. Rewritten to derive the behaviour from source.
- **I leaked a PAT** into the transcript via `${VAR:+x}${VAR:-y}`, which returns the *value* when set. Rotated.

---

## Repo state at exit

`workspace-hub` clean apart from generated `.claude/state/*` and coverage artifacts (expected, machine-local). No uncommitted work of mine anywhere. All Windows temp files and dispatch test jobs removed and verified; the licensed-run agent was never touched. Nothing dispatched through the live lane.
