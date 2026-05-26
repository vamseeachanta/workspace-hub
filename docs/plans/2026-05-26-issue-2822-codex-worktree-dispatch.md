# Plan for #2822: Document/automate worktree dispatch for the Codex-under-Claude route (3-layer sandbox requirement)

> **Status:** adversarial-reviewed (awaiting user approval → `status:plan-review`)
> **Complexity:** T2
> **Date:** 2026-05-26
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2822
> **Client:** N/A
> **Review artifacts:** scripts/review/results/2026-05-26-plan-2822-claude.md (Claude, MINOR) | ...-codex.md (Codex, MAJOR — resolved)

---

## Resource Intelligence Summary

This is a **Harness/Infrastructure** issue (Codex-under-Claude execution route). It touches no
wiki content, so `Client: N/A`. The generalizable follow-on from the #2802 pilot per the
"promote generalizable review findings" rule.

### Existing repo code
- Found: `docs/reports/2026-05-26-codex-under-claude-pilot.md` (35 lines, on `origin/main` via PR #2804/#2809) —
  documents the userns/AppArmor fix and the broker route, but has **no** section on worktree or
  isolated-clone dispatch. This is the doc the issue asks to extend.
- Found: `scripts/install/setup-codex-sandbox.sh` (128 lines) — guarded installer idiom: `--check`
  default, `--dry-run`, `--accept-userns-lpe-risk` to mutate, a `MANAGED-BY:` sentinel, fail-fast
  `preflight()`, and `report_state()`. The new helper will mirror this idiom exactly.
- Found: `scripts/install/teardown-codex-sandbox.sh` — sentinel-guarded reversal; refuses to act on
  content lacking the sentinel. The new helper's cleanup mode will copy this guard.
- Found: broker `~/.claude/plugins/cache/openai-codex/codex/1.0.2/scripts/codex-companion.mjs` +
  `lib/broker-lifecycle.mjs` + `lib/broker-endpoint.mjs`. Verified: `task`/`status`/`result` all
  expose `--cwd` (`valueOptions: ["cwd", ...]`); `resolveWorkspaceRoot(cwd)` derives the workspace
  root, and `listJobs(workspaceRoot)` keys jobs by that root (so `status`/`result` for a
  non-default root need `--cwd` too). `spawnBrokerProcess` launches `serve ... --cwd <cwd>` and the
  app-server reads `config.toml` once at spawn — confirming all three documented layers.
- Gap: no helper or doc teaches the operator how to dispatch Codex into an isolated checkout.

### Standards
Not applicable (infrastructure/docs issue, no engineering-calculation standard).

### LLM Wiki pages consulted
No relevant wiki pages — `Client: N/A`, no domain knowledge added.

### Documents consulted
- Issue #2822 body — names the two options (A clone, B worktree+grant), the three fixes, and the
  target doc; explicitly defers the A/B decision to this plan.
- Route report `docs/reports/2026-05-26-codex-under-claude-pilot.md` (#2804) — the route this extends.
- Memory `feedback_codex_worktree_sandbox_three_layer` — the live-discovered three-layer requirement
  and the "cleaner alternative considered" (standalone clone) note.
- Memory `feedback_codex_sandbox_write_blocked` — the underlying #2804/#2809 userns fix.
- Memory `feedback_worktree_gitlink_pollution` — `.git/worktrees/` residue; the clone route avoids it.
- Memory `feedback_codex_needs_pushed_artifact` — Codex sandbox can't read arbitrary local files;
  relevant to how the plan-review and the route itself feed Codex.
- Open PR #2829 (`docs/follow-on-plans-2802-2804`) — checked for collision; it only adds
  `docs/plans/2026-05-26-2813-route-fleet-rollout.md`, NOT the route doc or sandbox scripts. No collision.
- Evidence dir `/mnt/local-analysis/2802-pilot-evidence/` — present on this host (t3 review logs,
  orchestrator summary, completeness HTML) from the #2802 pilot that first hit the three layers.

### Gaps identified
- No "isolated dispatch" section in the route report.
- No helper that prepares a self-contained dispatch root and emits the correct broker invocation.
- No preflight that catches the worktree anti-pattern (gitlink `.git` outside root) before dispatch.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-26 via `gh issue view`):
- `#2822` — OPEN — "Document/automate worktree dispatch for the Codex-under-Claude route (3-layer sandbox requirement)" — no labels yet.

**File existence** (`git ls-tree origin/main`, 2026-05-26):
- EXISTS: `docs/reports/2026-05-26-codex-under-claude-pilot.md`
- EXISTS: `scripts/install/setup-codex-sandbox.sh`, `scripts/install/teardown-codex-sandbox.sh`
- EXISTS: `tests/setup/test_install_provider_clis.sh` (the plain-bash installer-test idiom to mirror)
- MISSING (new — this plan creates): `scripts/install/codex-dispatch-prep.sh`
- MISSING (new — this plan creates): `tests/setup/test_codex_dispatch_prep.sh`

**Broker flag/keying excerpts** (`grep -n` codex-companion.mjs, 2026-05-26; line cites corrected per Codex plan-review #4):
```
706:    valueOptions: ["model", "effort", "cwd", "prompt-file"],   # task   accepts --cwd
769:    valueOptions: ["cwd", "job-id"]                            # result accepts --cwd
814:    valueOptions: ["cwd", "timeout-ms", "poll-interval-ms"],   # status/wait accepts --cwd
312:  const workspaceRoot = resolveWorkspaceRoot(cwd);             # jobs keyed by git toplevel
313:  const jobs = sortJobsNewestFirst(listJobs(workspaceRoot))…   # status/result scoped to that root
```
(Implication: task/status/result all accept `--cwd`, and because jobs are keyed by the resolved
workspace root, a clone-rooted job's `status`/`result` require `--cwd <clone>` or return empty.)
```
broker-lifecycle.mjs:61: spawn(... "serve","--endpoint",endpoint,"--cwd",cwd,"--pid-file",pidFile)
broker-endpoint.mjs:16:  return `unix:${path.join(sessionDir,"broker.sock")}`;  # socket per session
```

**Reproduction proofs** (verify-against-repo-state, Step 1.5):

The runtime failure (worktree `git commit` → read-only `.git`) was reproduced live during the #2802
pilot (PR #2820); the generalizing premise of the recommended fix (Option A) is reproduced here:

```
$ git worktree add /tmp/.../wt-probe ...        # a worktree's .git is a gitlink OUT of the root
$ file wt-probe/.git
wt-probe/.git: ASCII text
$ cat wt-probe/.git
gitdir: /mnt/local-analysis/workspace-hub/.git/worktrees/wt-probe   # metadata OUTSIDE worktree root

$ git clone --shared --no-checkout <src> clone-shared              # --shared: alternates OUT of root (trap)
$ cat clone-shared/.git/objects/info/alternates
/mnt/local-analysis/workspace-hub/.git/objects

$ git clone --local --no-checkout <src> clone-local               # --local: self-contained (no alternates)…
$ file clone-local/.git ; ls clone-local/.git/objects/info/alternates
clone-local/.git: directory ; (no alternates file)
$ cd clone-local && git checkout -b probe && echo x > P && git add P && git commit -m probe
COMMIT OK                                                          # commits with NO sandbox grant

# …BUT --local is NOT write-isolated — it HARDLINKS objects (Codex plan-review #1, reproduced):
$ stat -c '%i (links=%h)' <src>/.git/objects/81/6703… clone-local/.git/objects/81/6703…
2071950 (links=2)        2071950 (links=2)                        # SAME inode → sandbox write corrupts source
$ git clone --no-hardlinks --no-checkout <src> clone-nohl
$ stat -c '%i (links=%h)' clone-nohl/.git/objects/81/6703…
354792 (links=1)                                                  # DISTINCT inode → write-isolated; no alternates
$ du -sh clone-nohl/.git/objects → 228M                           # one-time object copy (the isolation cost)

$ git clone --local <src> /tmp/clone-local                        # --local CROSS-device fails (hardlinks)
fatal: failed to create link '…/objects/…': Invalid cross-device link   (/mnt dev 2081 vs /tmp dev 2066)
$ git clone --no-hardlinks <src> /tmp/clone-nohl → done           # --no-hardlinks works cross-device
```

- Reproduced at: 2026-05-26 (this session, on ace-linux-1).
- Failure mode observed matches issue claim: YES — worktree `.git` is a gitlink to
  `<main>/.git/worktrees/<n>` (outside the sandbox root), confirming the read-only `git commit`
  root cause. Decision-relevant refinement (from Codex review, reproduced): `--local` is
  self-contained but hardlinked (shared inodes → not write-isolated); `--no-hardlinks` gives
  distinct inodes (true isolation) at a one-time object-copy cost and works cross-device.

<!-- Distinct sources: issue body, route report, 3 memory files, broker source, 2 reproductions = 8 (≥3). -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-26-issue-2822-codex-worktree-dispatch.md` |
| Helper (impl) | `scripts/install/codex-dispatch-prep.sh` |
| Tests | `tests/setup/test_codex_dispatch_prep.sh` |
| Route doc (extend) | `docs/reports/2026-05-26-codex-under-claude-pilot.md` |
| Plan index row | `docs/plans/README.md` |
| Plan review — Claude | `scripts/review/results/2026-05-26-plan-2822-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-26-plan-2822-codex.md` |

---

## Decision: Option A (clone-based) is the recommended route; Option B is documented as a fallback

**Chosen: Option A — prepare a self-contained local clone as the Codex dispatch root.** Option B
(worktree + managed writable-roots grant) is *documented* in the route doc as a fallback for
operators forced to use a literal worktree, but is **not** the automated path.

**Prerequisite (do not conflate):** Option A sidesteps only the *worktree-specific* three layers. It
still runs **on top of** the #2804 base route — the AppArmor userns grant (`setup-codex-sandbox.sh
--accept-userns-lpe-risk`) and `[sandbox_workspace_write] network_access = true` — without which
Codex cannot execute at all. Option A removes the worktree grant/restart, not the base route.

Justification (each point reproduced above or read from source, not asserted):

| # | Reason | Evidence |
|---|---|---|
| 1 | **Lower blast radius.** Option B grants `writable_roots=["<main>/.git"]`, making the *entire* shared object/ref db of every branch writable to the sandboxed Codex. A `--no-hardlinks` clone has its own `.git` with **separate object inodes** inside the sandbox root — nothing the source repo reaches is writable. | memory three-layer fix #2; `--no-hardlinks` clone object inode differs from source (repro) |
| 2 | **Fewer failure modes.** Option B needs three aligned layers, one of which (app-server restart after a `config.toml` edit) blocks *silently*. Option A collapses to one requirement: `--cwd <clone>`. No config mutation, no restart, no revert step, no writable-window. | broker reads `config.toml` once at spawn (source); clone commits with no grant (repro) |
| 3 | **Truly write-isolated, at a bounded disk cost.** `git clone --no-hardlinks` copies the object db → distinct inodes from the source, so a write-capable sandbox cannot corrupt the source's objects. Cost is a one-time object-store copy (~228 MB for workspace-hub), reclaimed on `rm -rf`. Far cheaper and safer than Option B's writable shared `.git`. | repro: source inode 2071950 vs clone inode 354792, no alternates; `du`≈228 MB |
| 4 | **No gitlink pollution.** Cleanup is a guarded `rm -rf <clone>`; no `.git/worktrees/<n>` residue to garbage-collect. | `feedback_worktree_gitlink_pollution` |
| 5 | Matches the issue's own framing (A "sidesteps all three fixes") and the memory's "cleaner alternative considered". | issue body; `feedback_codex_worktree_sandbox_three_layer` |

**Default clone mode = `--no-hardlinks` (write isolation), NOT `--local`.** Codex plan-review #1
(MAJOR, reproduced) caught a conflation in the first draft: `git clone --local` produces a
*self-contained* `.git` (no external `alternates`) but **not** a *write-isolated* one — it hardlinks
object files, so the clone's `.git/objects/<x>` shares an inode with the source's. A write-capable
sandbox writing through that path corrupts the source repo's object store. Reproduced: `--local`
clone object shares inode `2071950` (links=2) with source; `--no-hardlinks` clone has a distinct
inode (`354792`, links=1) and no `alternates`. Therefore:
- **Write dispatch (default):** `--no-hardlinks` — true isolation, ~228 MB object copy, works on any
  filesystem (no cross-device failure).
- **Read-only dispatch (opt-in `--allow-hardlinks`):** `--local` is acceptable only when Codex will
  not write/commit, since immutable shared objects can't be corrupted by reads.
A full working-tree checkout costs real disk in either mode; the helper reports the size, never hides it.

**Generalizable finding (promote per SHARED_SOUL "promote generalizable review findings"):** "a
hardlinked clone is not write-isolation for a write-capable sandbox" applies to *any* future
sandbox/clone dispatch, not just this helper. Implementation will file a short follow-on (or add a
`.claude/rules/` note) so the next clone-based dispatch plan doesn't re-discover it.

---

## Deliverable

A guarded `scripts/install/codex-dispatch-prep.sh` helper that prepares a write-isolated
(`--no-hardlinks` by default) local clone as the Codex broker dispatch root and emits the exact
`codex-companion.mjs task --cwd <clone>` invocation (with an **absolute** `--prompt-file` path, plus
matching `status`/`result --cwd`), with TDD coverage; and an "Isolated dispatch (clone vs worktree)"
section added to the #2804 route report documenting the recommended write-isolated clone route, the
read-only `--local` opt-in, and the worktree+grant fallback (the three-layer requirement), plus a
preflight that flags the worktree anti-pattern and verifies object-store isolation.

---

## Pseudocode

```
# scripts/install/codex-dispatch-prep.sh  (mirrors setup-codex-sandbox.sh idiom)
# Modes: --check (default, no mutation) | --dry-run | --prepare | --cleanup <dir>
# ALL mutating ops route through a logging wrapper (run_git / run_rm) so the TDD
# harness can redefine them to log-only (per tests/setup/test_install_provider_clis.sh). [C6]
# Pure reads (rev-parse, remote get-url) may run for real against a fixture repo.

# [C3] Sentinel lives INSIDE .git so Codex can never commit it and no exclude dance is needed.
SENTINEL_REL=".git/codex-dispatch-managed"

CLONE_MODE = "--no-hardlinks"               # [Codex#1] DEFAULT = write-isolated (distinct inodes).
                                            # --allow-hardlinks flag flips to "--local" for READ-ONLY dispatch only.

resolve_dest(branch):                       # default: sibling of the source repo
    src_root  = git -C "$PWD" rev-parse --show-toplevel
    repo_name = basename(src_root)
    slug      = branch with '/' and unsafe chars → '-'      # feat/2822-x → feat-2822-x
    return realpath_m("${CODEX_DISPATCH_ROOT:-$(dirname "$src_root")}/${repo_name}-cxc-${slug}")

# [Codex#2] Reason about the OBJECT STORE device, not the worktree toplevel — a worktree/gitfile/
# separate-gitdir source keeps objects elsewhere. Only relevant to the --local opt-in (hardlinks
# can't cross devices); --no-hardlinks copies and works cross-device, so this is advisory there.
src_object_dir(src):  return git -C "$src" rev-parse --git-path objects   # absolute objects path
same_filesystem(a, b): return [ "$(stat -c %d "$a")" == "$(stat -c %d "$b")" ]

preflight_target(dir):                       # the preflight the issue asks for
    if [ -f "$dir/.git" ]:                    # [C4] regular file → gitlink → worktree
        fail "TARGET IS A WORKTREE — .git is a gitlink pointing outside the root. Prepare a clone
              (recommended) or apply the 3-layer worktree grant (route doc §Isolated dispatch)."
    [ -d "$dir/.git" ]            or fail "no .git directory — not a self-contained checkout"
    [ ! -e "$dir/.git/objects/info/alternates" ] or
        fail "alternates present → objects live OUTSIDE this root (e.g. --shared/--reference);
              sandbox commit will fail read-only. Re-clone with --no-hardlinks."
    # [Codex#6] verify true write-isolation: a sample object must NOT share an inode with the source.
    if sample object inode in "$dir/.git/objects" == same inode in "$(src_object_dir src)":
        warn "object store is HARDLINKED to the source — a write sandbox could corrupt source objects.
              OK only for read-only dispatch; re-clone with --no-hardlinks for write dispatch."

prepare(branch, base):
    src = git rev-parse --show-toplevel
    dest = resolve_dest(branch)
    if exists(dest): fail "dest exists; --cleanup first"
    parent = dirname(dest); run_mkdir -p "$parent"          # [C5] parent must exist before stat
    flag = CLONE_MODE                                       # default --no-hardlinks
    if flag == "--local" AND NOT same_filesystem(parent, src_object_dir(src)):
        warn "--local cannot cross devices; falling back to --no-hardlinks"; flag="--no-hardlinks"
    run_git clone "$flag" --no-checkout "$src" "$dest"
    run_git -C "$dest" remote set-url origin "$(git -C "$src" remote get-url origin)"  # push → GitHub
    run_git -C "$dest" fetch origin --quiet                  # [C2] base on TRUE remote, not stale source ref
    run_git -C "$dest" checkout -b "$branch" "${base:-origin/main}"
    touch "$dest/$SENTINEL_REL"                              # [C3] inside .git → never committed
    preflight_target "$dest"
    emit broker invocation (operator supplies an ABSOLUTE prompt path [Codex#5]):
        node codex-companion.mjs task   --cwd "$dest" --write --background --prompt-file "$(realpath <PROMPT>)"
        node codex-companion.mjs status --cwd "$dest"        # NOTE: --cwd required or returns empty
        node codex-companion.mjs result --cwd "$dest" <job>

# [Codex#3] cleanup must fail closed on EVERY guard, not just the sentinel:
cleanup(dir):
    d = realpath(dir)                                        # resolve symlinks up front
    [ -n "$d" ] && [ "$d" != "/" ] && [ "$d" != "$HOME" ]    or fail "refusing dangerous target $d"
    src = git rev-parse --show-toplevel
    [ "$d" != "$(realpath "$src")" ]                          or fail "refusing to delete the source repo"
    basename "$d" matches "*-cxc-*"                            or fail "name doesn't match dispatch pattern"
    expected_root = "${CODEX_DISPATCH_ROOT:-$(dirname "$src")}"
    "$d" is a path-prefix child of realpath("$expected_root") or fail "outside the dispatch root"
    [ "$(git -C "$d" rev-parse --show-toplevel 2>/dev/null)" == "$d" ] or fail "not a git toplevel"
    [ -e "$d/$SENTINEL_REL" ]                                 or fail "no .git sentinel — not a managed clone"
    run_rm -rf "$d"
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/install/codex-dispatch-prep.sh` | guarded clone-prep helper + preflight + cleanup |
| Create | `tests/setup/test_codex_dispatch_prep.sh` | TDD harness (plain bash, stubbed side-effects) |
| Modify | `docs/reports/2026-05-26-codex-under-claude-pilot.md` | add "Isolated dispatch (clone vs worktree)" section |
| Update | `docs/plans/README.md` | add this plan's index row |

---

## TDD Test List

Two layers, both mirroring `tests/setup/test_install_provider_clis.sh` (source the helper, redefine
`run_git` / `run_rm` / `run_mkdir` to append to a log, assert on the log / exit code):

**(a) Unit — decision/emission logic (stubbed side-effects):**

| Test name | What it verifies | Setup | Expected |
|---|---|---|---|
| test_default_mode_no_hardlinks | write dispatch defaults to `--no-hardlinks` (isolation) | run prepare, no opt-in | log `clone --no-hardlinks`, NOT `--local` |
| test_allow_hardlinks_opt_in | `--allow-hardlinks` flips to `--local` for read-only | run with `--allow-hardlinks`, same-FS | log `clone --local` |
| test_local_xdevice_falls_back | `--local` opt-in across devices → `--no-hardlinks` + warn | stub `stat` (obj dir) to differ | log `--no-hardlinks`; stderr warns |
| test_remote_wired_to_github | clone origin re-pointed at GitHub URL | stub remotes | log `remote … set-url origin https://github.com/…` |
| test_fetch_before_branch | `fetch origin` precedes `checkout -b` (true base) | run prepare | log order: `fetch origin` then `checkout -b` |
| test_emits_cwd_not_cd | broker invocation uses `--cwd`, never `--cd` | run prepare | stdout has `--cwd <dest>`; `grep -c -- '--cd '` == 0 |
| test_prompt_file_absolute | emitted `--prompt-file` is absolute | run prepare | emitted path starts with `/` (Codex#5) |
| test_status_result_include_cwd | emitted status/result carry `--cwd` | run prepare | stdout `status --cwd` and `result --cwd` present |
| test_dry_run_no_mutation | `--dry-run` performs zero side effects | run `--dry-run` | log empty (no clone/remote/fetch/rm) |
| test_dest_default_sibling | default dest is a sibling of the source repo | run resolve_dest | dest under `dirname(src_root)`, name `*-cxc-*` |

**(b) Cleanup guard — fail-closed on every guard (Codex#3):**

| Test name | What it verifies | Setup | Expected |
|---|---|---|---|
| test_cleanup_requires_sentinel | refuses dir without `.git/codex-dispatch-managed` | sentinel absent | exit≠0, `run_rm` never called |
| test_cleanup_rejects_non_pattern | refuses a dir whose name lacks `-cxc-` | sentinel planted, bad name | exit≠0, `run_rm` never called |
| test_cleanup_rejects_outside_root | refuses a dir outside the dispatch root | sentinel + `-cxc-` but wrong parent | exit≠0 |
| test_cleanup_rejects_source_repo | refuses the source repo itself | point cleanup at `$src` | exit≠0 |
| test_cleanup_rejects_root_home | refuses `/` and `$HOME` | cleanup `/` / `$HOME` | exit≠0 |
| test_cleanup_managed_ok | removes a fully-valid managed clone | all guards satisfied | `run_rm -rf <dir>` in log |

**(c) Integration — the isolation property itself (real clones in a tmp fixture repo, Codex#6):**

| Test name | What it verifies | Expected |
|---|---|---|
| test_nohardlinks_distinct_inode | `--no-hardlinks` clone object inode ≠ source inode | `stat -c %i` differs |
| test_local_shares_inode | `--local` clone object inode == source (documents the hazard) | `stat -c %i` equal |
| test_no_alternates_after_prepare | prepared clone has no `objects/info/alternates` | file absent |
| test_preflight_rejects_worktree | preflight fails on a gitlink `.git` (real `git worktree add` fixture) | exit≠0, message names "WORKTREE" |
| test_preflight_warns_hardlinked | preflight warns when objects share an inode with source | stderr warns |

---

## Acceptance Criteria

- [ ] All new tests pass: `bash tests/setup/test_codex_dispatch_prep.sh` (exit 0, all PASS).
- [ ] `scripts/install/codex-dispatch-prep.sh --check` and `--dry-run` run without mutation and without sudo.
- [ ] Write dispatch defaults to `--no-hardlinks` (distinct object inodes); a prepared clone's object inode differs from the source's, and `objects/info/alternates` is absent.
- [ ] `--dry-run` prints the exact `task --cwd <dest>` / `status --cwd` / `result --cwd` invocations with an absolute `--prompt-file` path.
- [ ] Cleanup fails closed unless ALL guards pass (sentinel + `-cxc-` name + under dispatch root + git toplevel + not `/`/`$HOME`/source repo).
- [ ] Preflight fails closed on a worktree (gitlink `.git`) target and warns on a hardlinked object store, with a message pointing to the route-doc fallback.
- [ ] Route report gains an "Isolated dispatch (clone vs worktree)" section covering the recommended write-isolated clone route (`--no-hardlinks`, only `--cwd` needed), the read-only `--local` opt-in, AND the worktree fallback's three-layer requirement (`--cwd`, `writable_roots=["<main>/.git"]`, app-server restart, job-namespacing), plus the #2804 base-route prerequisite and push-auth note.
- [ ] `shellcheck scripts/install/codex-dispatch-prep.sh` is clean (matches repo shell-lint expectation).
- [ ] `docs/plans/README.md` index row added; no unrelated rows touched.
- [ ] Review artifacts posted to `scripts/review/results/`.

---

## Risks

| Risk | Mitigation |
|---|---|
| Helper hard-codes `/mnt/local-analysis` and breaks on other machines/Windows | Derive paths from `git rev-parse --show-toplevel` + `dirname`; honor `$CODEX_DISPATCH_ROOT`; same-FS check via `stat -c %d`, not a hard-coded mount |
| `rm -rf` cleanup deletes the wrong directory | Multi-guard fail-closed (Codex#3): sentinel + `-cxc-` name + under dispatch root + git toplevel + not `/`/`$HOME`/source; realpath before any check; never default-delete |
| Hardlinked clone lets a write sandbox corrupt the SOURCE repo's objects (Codex#1) | Default `--no-hardlinks` → distinct object inodes; `--local` is opt-in and only for read-only dispatch; preflight warns on a shared-inode object store |
| Clone origin points at the local source path → Codex push fails | `remote set-url origin <github-url>` from the source's `origin` during prepare; test asserts it |
| Disk cost of `--no-hardlinks` object copy on a large repo (~228 MB for workspace-hub) | Bounded, transient (reclaimed on guarded `rm -rf`); helper reports the object-store + working-tree size; it is the deliberate price of write isolation |
| Push auth on a fresh host | Re-pointed GitHub origin relies on the user's ambient git credential helper (global `~/.gitconfig`); route doc notes operators must `gh auth`/configure credentials before dispatch |
| Sentinel file accidentally committed by Codex into the branch | Store sentinel at `.git/codex-dispatch-managed` (inside `.git`) — git never tracks `.git/` contents, so no exclude dance and zero commit risk |
| Branch bases on a stale main (local source ref behind GitHub) | `git fetch origin` after re-pointing origin to GitHub, before `checkout -b … origin/main` |
| Option A mistaken as a replacement for the #2804 base route | Decision + route doc state Option A runs ON TOP OF the userns grant + `network_access`; it removes only the worktree grant/restart |
| Branch contamination: this session sits on `fix/2795-…` with another session's staged changes | The plan file + new script are untracked additions; commit/push of the plan will use an isolated branch off `origin/main` (temp-index or worktree), never `git add -A` on the dirty index. See "Implementation note" below |
| Scope creep into a full broker wrapper | Helper only *prepares* the root + *emits* the command; it does not invoke the broker itself (keeps the testable surface small and the operator in control) |

---

## Implementation note — branch hygiene (not part of the deliverable, but a hard gate)

The working tree is currently on `fix/2795-dispatch-review-findings` with staged/modified files
belonging to another session. Per `feedback_multi_agent_commit_serialization` /
`feedback_temp_index_snapshot_live_repo`, implementation commits for #2822 MUST go onto a dedicated
`feat/2822-codex-dispatch-prep` branch created off `origin/main` WITHOUT disturbing the live index —
either via a temp-index snapshot commit of only the #2822 paths, or a short-lived worktree. No
`git add -A`, no commit of the unrelated staged work. PR opened with `Refs #2822` (not `Closes`),
handed to the user to merge.

---

## Adversarial Review Summary

Both reviews ran adversarially (defect-hunting prompt). Claude (r1) and Codex (r2) surfaced
**different** defect sets, so per `feedback_r3_inline_loop_break_pattern` the fixes were applied as
main-session inline patches (this revision) rather than dispatching a further review round. The
load-bearing Codex MAJOR (#1) was independently reproduced before acting.

| Provider | Verdict | Key findings (all resolved in this revision) |
|---|---|---|
| Claude | MINOR | C1 Option-A-vs-#2804-base conflation; C2 stale branch base; C3 sentinel commit risk; C4 worktree detection; C5 parent-dir stat; C6 wrapper testability. Artifact: `scripts/review/results/2026-05-26-plan-2822-claude.md` |
| Codex | MAJOR | #1 `--local` hardlinks ≠ write isolation (→ default `--no-hardlinks`, reproduced); #2 object-dir device reasoning; #3 weak `rm -rf` guard (→ multi-guard fail-closed); #4 broker line cite; #5 absolute `--prompt-file`; #6 isolation/cleanup tests. Artifact: `scripts/review/results/2026-05-26-plan-2822-codex.md` |

**Post-revision state:** no open MAJOR. Ready for `status:plan-review` and user approval.
