# Plan for #3702: equality collectors write generated artifacts into the tracked tree — self-sustaining STALE-CHECKOUT ratchet

> **Status:** plan-review
> **Complexity:** T2
> **Date:** 2026-07-30
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3702
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-07-30-plan-3702-claude-r1.md | scripts/review/results/2026-07-30-plan-3702-codex-r2.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/readiness/collect-equality.sh:18` — `STATE_DIR="${WS}/.claude/state"`, hard-coded into the tracked working tree. Line 522 builds `OUT="${STATE_DIR}/equality-${MACHINE}.yaml"`; line 531 writes it. **No env or flag seam for the output directory** (only `--stdout` at line 25 suppresses the write entirely).
- Found: `scripts/readiness/build-equality-matrix.py:32-33` — `STATE = REPO / ".claude" / "state"`, `REPORTS = REPO / "docs" / "reports"`, both derived from `REPO = Path(__file__).resolve().parents[2]`. Line 585 globs `STATE.glob("equality-*.yaml")`; lines 925-930 write `docs/reports/<date>-machine-equality-matrix.html` **and** the undated `docs/reports/machine-equality-matrix.html` alias. **No input or output seam.**
- Found: `scripts/readiness/publish-equality.sh:132-199` — `attempt()` already publishes **entirely out of the interactive checkout**: `git worktree add --no-checkout --detach` (line 138) onto `origin/main`, sparse-checkout of `/.claude/state/*`, `/docs/reports/*`, `/scripts/readiness/*` (line 143), copy of newer local evidence (lines 150-160), optional in-worktree rebuild (lines 163-170), allowlist-guarded scoped commit (lines 173-190), push (line 197). The interactive checkout's HEAD/index is never touched — the script header states this explicitly at lines 15-17. **The publish step is not the source of working-tree dirt.**
- Found: `scripts/readiness/equality-matrix-cron.sh:24-31` — the chain is `collect-equality.sh` → `build-equality-matrix.py` → `publish-equality.sh --rebuild`. **There is no `git fetch` / `git pull` preflight anywhere in this script.** The two generators run against whatever HEAD the box happens to sit on.
- Found: `scripts/curation/curate-session-memory.sh:75-82` — the 6-hourly session-curation cron *also* runs `collect-equality.sh` + `build-equality-matrix.py` into the tracked tree, and does **not** publish. This is a second, higher-frequency dirtying path the issue body does not mention.
- Found: `scripts/readiness/build-equality-matrix.py:800-811` — `--json` returns before the HTML write, so `reconcile-ecosystem.sh:219`'s read-only verdict query does **not** dirty the tree. Good; must stay that way.
- Found: `scripts/windows/equality-report.ps1:8-14, 334-346, 388-393` — the Windows wrapper takes the *opposite* approach: it commits+pushes the state yaml from the working checkout, discards the regenerated report HTML unless `-RefreshMatrix`, and refuses to run when the checkout is behind (`Confirm-FreshCheckout`, throw at line 214). Windows fails loud where Linux silently ratchets.
- Found: `scripts/build_pages.py:58` — `"machine-equality-matrix": ("docs/reports/machine-equality-matrix.html", "Machine Equality")`, and `.github/workflows/pages.yml` triggers `on.push.branches: [main]` with a path filter on `docs/reports/machine-equality-matrix.html`. **The published HTML must remain a tracked file on `main`** — any plan that gitignores it kills the live Pages link.
- Found: `scripts/monitoring/equivalence_state.py:5-19` — prior art for a dedicated state ref: `DEFAULT_REF = "equivalence-state"`, plumbing-built disconnected chain (`hash-object`/`mktree`/`commit-tree`), pushed with `GIT_PRE_PUSH_SKIP=1` (line 71) after the #3500 hook deadlock. The remote ref exists (`git ls-remote origin` → `refs/heads/equivalence-state` at `99037bd6e`).
- Gap: no test anywhere asserts that a collection run leaves the working tree as clean as it found it. `tests/readiness/test_publish_equality.py` covers the publisher's worktree isolation but not the generators.

### Standards

Not applicable — harness/infrastructure issue, no engineering standard involved.

### LLM Wiki pages consulted

No relevant wiki pages — this is workspace-hub-internal harness work, explicitly out of scope of `.claude/rules/wiki-sibling-routing.md` ("workspace-hub-internal artifact (rule, skill, doc, hook script)").

### Documents consulted

- `docs/plans/2026-05-26-issue-2801-machine-equality.md` — the origin plan for the matrix; establishes `.claude/state/equality-<machine>.yaml` as the tracked evidence surface.
- `docs/plans/2026-06-08-issue-2972-equality-matrix-fix.md` — introduced `equality-matrix-cron.sh` as the fail-loud wrapper.
- `docs/plans/2026-07-17-issue-3571-equality-host-identity-junction-flock.md` — introduced the mkdir-lock fallback and the public-label commit subject in `publish-equality.sh`.
- `config/scheduled-tasks/schedule-tasks.yaml:31-51` (`equality-report`, weekly Mon 04:30, 7 machines) and `:191-218` (`equality-matrix-refresh`, `50 */6 * * *`, `[dev-primary, ace-linux-1]`) and `:169-180` (`session-curation`, `47 */6 * * *`, 6 machines) — three schedules drive the generators; only two of the three publish.
- Related issue [#3557](https://github.com/vamseeachanta/workspace-hub/issues/3557) — OPEN, `status:needs-plan`: "reconcile marks dirty STALE-CHECKOUT auto-safe but apply cannot clean or make progress". Downstream symptom of this defect at the driver layer.
- Related issue [#3554](https://github.com/vamseeachanta/workspace-hub/issues/3554) — OPEN, `status:plan-approved`: Windows `publish-equality` flock misclassification. Gates the Phase-2 Windows cutover proposed below.
- Related issue [#2851](https://github.com/vamseeachanta/workspace-hub/issues/2851) — CLOSED: the freshness guard that introduced `is_stale()`. Its `MEASURED`-allowlist design is the reason the issue body's `dirty` mechanism is wrong (see Reproduction proofs).
- Drive-file index: **no relevant drive files** — all five registered indexes are unreachable from this macOS planning host (`/mnt/ace`, `/mnt/dde`, `data/document-index/index.jsonl` all report `unreachable` from `scripts/data/drive-index-search/search.py`). Coverage gap recorded, not a finding.

### Gaps identified

- No output-directory seam exists on either generator (`collect-equality.sh`, `build-equality-matrix.py`) — both must be built.
- No working-tree-cleanliness test exists for any equality entry point — must be built.
- No freshness preflight exists on the Linux cron path (Windows has one; Linux does not) — must be built.
- No enforcement check prevents a future edit from re-pointing a generator at a tracked path — must be built.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-07-30 via `gh issue view`):
- `#3702` — OPEN — bug(equality): equality-matrix-cron writes generated artifacts into the tracked tree… — labels `bug, cat:harness, domain:workstations, machine:multi, status:needs-plan`. **No `lane:` label present** — this plan proposes `lane:claude` and the label will be added at the plan-review step per [#3029](https://github.com/vamseeachanta/workspace-hub/issues/3029).
- `#3557` — OPEN — reconcile marks dirty STALE-CHECKOUT auto-safe but apply cannot clean or make progress.
- `#3554` — OPEN, `status:plan-approved` — Windows publish-equality misclassifies missing flock as contention.
- `#2851` — CLOSED — collect-equality freshness guard.

**File existence** (`ls -la` 2026-07-30):
- EXISTS: `scripts/readiness/collect-equality.sh` (29984 B)
- EXISTS: `scripts/readiness/build-equality-matrix.py` (53800 B)
- EXISTS: `scripts/readiness/publish-equality.sh` (9178 B)
- EXISTS: `scripts/readiness/equality-matrix-cron.sh` (1796 B)
- EXISTS: `scripts/readiness/refresh-equality-matrix.sh` (3729 B)
- EXISTS: `scripts/curation/curate-session-memory.sh`
- EXISTS: `scripts/windows/equality-report.ps1`
- EXISTS: `tests/readiness/test_publish_equality.py`, `tests/readiness/test_collect_equality.py`, `tests/readiness/test_build_equality_matrix.py`
- MISSING (new — this plan creates): `tests/readiness/test_equality_tree_cleanliness.py`
- MISSING (new — this plan creates): `scripts/enforcement/check-equality-artifacts-out-of-tree.sh`

**Line excerpts:**

`scripts/readiness/collect-equality.sh:311-327` — the `MEASURED` allowlist that scopes the `dirty` provenance field:
```
# MEASURED-PATH allowlist (BC1): dirty reflects ONLY the paths the collector actually reads,
# NOT `.claude` wholesale — else unrelated state/memory edits would false-STALE a healthy
# machine. Keep this in sync with the dimensions probed above.
MEASURED=(.claude/skills .claude/memory/context.md .claude/memory/agents.md .codex/skills \
          .claude/dispatch .claude/rules AGENTS.md \
          .claude/hooks/plan-approval-gate.sh .claude/settings.json \
          scripts/readiness/harness-config.yaml scripts/readiness/provider_harness_parity.py \
          config/agents/claude/SOUL.runtime.md config/agents/codex/AGENTS.runtime.md \
          config/agents/codex/MEMORY.runtime.md config/agents/hermes/SOUL.runtime.md \
          config/scheduled-tasks/schedule-tasks.yaml)
...
  [[ -n "$(git -C "$WS" status --porcelain --untracked-files=no -- "${MEASURED[@]}" 2>/dev/null)" ]] && dirty=true
```
Neither `.claude/state/` nor `docs/reports/` appears in `MEASURED`.

`scripts/readiness/build-equality-matrix.py:224-245` — `is_stale()`:
```
def is_stale(report: dict) -> bool:
    p = report.get("provenance")
    if not isinstance(p, dict):
        return True
    if p.get("dirty") is not False:                  # anything but an explicit clean flag ⇒ stale
        return True
    if p.get("behind_main") not in (0, "0"):         # behind OR "unknown"/absent ⇒ stale (BC2)
        return True
    if p.get("ahead_main") not in (0, "0"):          # local commits not on origin/main ⇒ non-canonical
        return True
```

`scripts/readiness/build-equality-matrix.py:551-554` — the all-dimensions stamp:
```
    # #2851: a contaminated checkout grades STALE-CHECKOUT for EVERY dim of that machine — below
    if is_stale(rep):
        return "STALE-CHECKOUT"
```

**Gap proofs:**
- `git ls-files .claude/state/ | grep -i equality` → 5 files (`equality-ace-win-1.yaml`, `equality-ace-win-2.yaml`, `equality-dev-primary.yaml`, `equality-dev-secondary.yaml`, `equality-gpu-claw.yaml`) → confirms the state yamls are **tracked**.
- `git ls-files docs/reports/ | grep -ci equality` → `42` → confirms 42 tracked matrix HTML files (41 dated + 1 alias), growing daily.
- `grep -n "docs/reports" .gitignore` → only `docs/reports/sessions/payloads/` → confirms the matrix HTML is **not** gitignored.
- `find tests -iname "*clean*tree*"` → empty → confirms no tree-cleanliness test exists.

**Reproduction proofs** (verify-against-repo-state, per Step 1.5 of `issue-planning-mode`):

*(1) The FF-pull block is real* — scratch repo, 2026-07-30:
```
$ # origin advances both artifact paths; local has uncommitted edits to the same paths
$ git status --porcelain
 M .claude/state/equality-x.yaml
 M docs/reports/machine-equality-matrix.html
$ git pull --ff-only origin master
error: Your local changes to the following files would be overwritten by merge:
	.claude/state/equality-x.yaml
	docs/reports/machine-equality-matrix.html
Please commit your changes or stash them before you merge.
Aborting
exit=1
$ git rev-list --count HEAD..origin/master
1
```

*(2) The `dirty` provenance field is NOT what drives the loop* — published evidence history for `dev-primary`, read from `main`:
```
$ for sha in $(git log --format=%h -12 -- .claude/state/equality-dev-primary.yaml); do
    git show "$sha:.claude/state/equality-dev-primary.yaml" | grep -E 'dirty|behind_main|ahead_main|generated_at'; done
3df4e913b  generated_at: "2026-07-29T12:47:13"  dirty: false  behind_main: 14  ahead_main: 1
1f99547b7  generated_at: "2026-07-29T11:28:21"  dirty: false  behind_main: 0   ahead_main: 0
85def2e32  generated_at: "2026-07-29T07:41:27"  dirty: true   behind_main: 25  ahead_main: 17
919867101  generated_at: "2026-07-29T00:51:37"  dirty: false  behind_main: 21  ahead_main: 16
7968f881d  generated_at: "2026-07-28T18:47:15"  dirty: false  behind_main: 18  ahead_main: 14
4174d5e9b  generated_at: "2026-07-28T12:47:06"  dirty: false  behind_main: 16  ahead_main: 13
733a6c50e  generated_at: "2026-07-28T06:47:18"  dirty: true   behind_main: 15  ahead_main: 11
14987386f  generated_at: "2026-07-28T00:47:09"  dirty: false  behind_main: 14  ahead_main: 10
03bc496a3  generated_at: "2026-07-27T18:47:06"  dirty: false  behind_main: 13  ahead_main: 8
442fc070f  generated_at: "2026-07-27T12:47:13"  dirty: false  behind_main: 12  ahead_main: 7
3b73a9962  generated_at: "2026-07-27T06:47:06"  dirty: true   behind_main: 8   ahead_main: 5
2f38c0ab4  generated_at: "2026-07-27T00:47:11"  dirty: false  behind_main: 5   ahead_main: 3
```

*(3) Current fleet state* (all five tracked yamls at `main` HEAD `3df4e913b`, 2026-07-30):
```
ace-win-1     dirty: false  behind_main: 0   ahead_main: 0   generated_at 2026-07-27T11:18:15
ace-win-2     dirty: false  behind_main: 0   ahead_main: 0   generated_at 2026-07-19T06:59:16
dev-primary   dirty: false  behind_main: 14  ahead_main: 1   generated_at 2026-07-29T12:47:13
dev-secondary dirty: false  behind_main: 0   ahead_main: 0   generated_at 2026-07-29T11:38:59
gpu-claw      dirty: false  behind_main: 0   ahead_main: 0   generated_at 2026-07-29T12:40:12
```

- Reproduced at: 2026-07-30
- **Failure mode observed matches issue claim: PARTIALLY.** The defect and its consequence are real and live (dev-primary re-entered STALE-CHECKOUT within 79 minutes of a manual clean-up). The *causal chain* in the issue body is wrong in three places; the corrections are recorded below and this plan targets the actual mechanism.

#### Corrections to the #3702 diagnosis (the plan implements the corrected model)

1. **`dirty` is not whole-tree, and the equality artifacts cannot set it.** `collect-equality.sh:314-327` scopes the `dirty` provenance field to a 16-entry `MEASURED` allowlist that contains neither `.claude/state/` nor `docs/reports/`, and uses `--untracked-files=no`. The generated artifacts are therefore invisible to the `dirty` field by construction. Proof: the published history shows `dirty` flipping true→false→true across consecutive 6-hourly runs (Reproduction proof 2), which cannot happen if the collector's own output set it; and all five machines report `dirty: false` right now while dev-primary is still STALE. The issue's step 1→3 link ("cron dirties tree → `is_stale()` fails on `dirty != false`") is **not the operative mechanism**.
2. **The operative mechanism is `behind_main` (and `ahead_main`), with the tracked artifacts acting as the *blocker*, not the trigger.** `behind_main` grows monotonically (5→8→12→13→14→15→16→18→21→25 across ten consecutive runs) because (a) every publish moves `origin/main`, (b) the box never pulls, and (c) when something *does* try `git pull --ff-only`, git aborts because the locally regenerated `docs/reports/machine-equality-matrix.html` and `.claude/state/equality-<self>.yaml` are tracked-and-modified and appear in the incoming diff (Reproduction proof 1). `is_stale()` then fails on `behind_main != 0` at `build-equality-matrix.py:233` and `verdict_for()` stamps STALE-CHECKOUT on all 27 dimensions at `:553`. So the fix the issue asks for is the right fix — the artifacts must leave the tracked tree — but the plan must not claim it works by changing the `dirty` field, and must not regress `MEASURED`.
3. **The ratchet is permanent, not transient, because of `--rebuild`.** `publish-equality.sh --rebuild` re-renders the matrix *inside the sparse worktree* from origin's union-of-freshest evidence (lines 163-170), while the local tree renders from its own stale peer copies. The two renders therefore differ by construction on any box that is behind, so the local alias file is *permanently* modified relative to `origin/main` and the FF pull can never succeed on its own. This is why manual clean-up was required and why it re-broke within the hour.
4. **`publish-equality.sh` does not dirty the working tree.** The issue's framing implies the publish step is part of the dirtying. It is not — it has used a disposable sparse worktree since #3571 (lines 115-127, 132-145). The dirtying is entirely `collect-equality.sh:531` and `build-equality-matrix.py:926,930`.
5. **The publish amplification is real, and worse than stated.** Three schedules drive the generators: `equality-report` weekly across 7 machines, `equality-matrix-refresh` every 6h on the control-plane boxes, and `session-curation` every 6h across 6 machines (which generates but does **not** publish). Each publish is +1 `behind_main` for every box that does not pull. The issue's observed 18→20 and 24→34 growth is consistent.
6. **`ahead_main` is a second, independent STALE trigger this issue does not fix.** `is_stale()` returns True on `ahead_main != 0` (`:235`). dev-primary sat at `ahead_main: 17`. A box with a single unpushed WIP commit grades 27/27 STALE-CHECKOUT even with a perfectly clean, up-to-date tree. That is a design question about `is_stale()`, recorded as an Open Question below and deliberately **not** changed by this plan.

<!-- Distinct sources consulted: issue body, collect-equality.sh, build-equality-matrix.py, publish-equality.sh, equality-matrix-cron.sh, curate-session-memory.sh, refresh-equality-matrix.sh, equality-report.ps1, build_pages.py, .github/workflows/pages.yml, equivalence_state.py, schedule-tasks.yaml, .gitignore, git object history, three prior plans, four related issues, drive-file index. Count: 20+ (minimum 3). -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-07-30-issue-3702-equality-artifacts-out-of-tree.md |
| Tests (new) | `tests/readiness/test_equality_tree_cleanliness.py` |
| Tests (extended) | `tests/readiness/test_collect_equality.py`, `tests/readiness/test_build_equality_matrix.py`, `tests/readiness/test_publish_equality.py` |
| Implementation | `scripts/readiness/collect-equality.sh`, `scripts/readiness/build-equality-matrix.py`, `scripts/readiness/publish-equality.sh`, `scripts/readiness/equality-matrix-cron.sh`, `scripts/readiness/refresh-equality-matrix.sh`, `scripts/curation/curate-session-memory.sh` |
| Enforcement (new) | `scripts/enforcement/check-equality-artifacts-out-of-tree.sh` |
| Plan review — Claude | scripts/review/results/2026-07-30-plan-3702-claude-r1.md |
| Plan review — Codex | scripts/review/results/2026-07-30-plan-3702-codex-r2.md |
| Docs updates | docs/plans/README.md (index row) |

---

## Deliverable

After this issue, a full equality collection + build run on any Linux/macOS box will write **zero** bytes into the tracked working tree — `git status --porcelain` will be byte-identical before and after — while `origin/main` will continue to carry exactly the same published surface it does today (`.claude/state/equality-<machine>.yaml` and `docs/reports/*machine-equality-matrix.html`, written only through the existing sparse publish worktree), so the live GitHub Pages matrix and the cross-machine comparison model are unchanged.

---

## Recommended approach (and why), with rejected alternatives

**Recommended — "generate out of tree, publish through the existing worktree."**

The publisher already solved this problem correctly. `publish-equality.sh` writes the canonical artifacts into a disposable sparse worktree checked out at `origin/main` and pushes from there. The working-tree copies of those same artifacts serve exactly one purpose today — being the publisher's input — and one anti-purpose: blocking the FF pull that would clear `behind_main`. The fix is to relocate the *generation* target out of the tree and let the publisher read from the new location. The remote layout, the Pages contract, the matrix history, and `is_stale()` semantics are all untouched.

Rejected alternatives:

| Alternative | Why rejected |
|---|---|
| **A. Gitignore the artifacts and `git rm --cached` them.** | Kills the live Pages link: `scripts/build_pages.py:58` copies `docs/reports/machine-equality-matrix.html` verbatim into `public/`, and `.github/workflows/pages.yml` path-filters on that exact tracked path. Also destroys the 42-file dated matrix history and breaks the publisher's whole model — `publish-equality.sh:5-9` states the matrix "only compares machines equally when every machine's evidence reaches origin/main". Untracking the evidence removes the comparison surface. Rejected outright. |
| **B. Move everything to a dedicated ref (`equality-state`), mirroring `equivalence-state`.** | Genuinely attractive and there is working prior art in this repo (`scripts/monitoring/equivalence_state.py:5-19`, remote ref live at `99037bd6e`). But Pages builds only from `main` (`pages.yml` `on.push.branches: [main]` + default `actions/checkout@v6` ref), so the HTML must land on `main` regardless; and moving the yaml evidence to a ref forces a second reader path through `build-equality-matrix.py`, `reconcile-ecosystem.sh`, `refresh-equality-matrix.sh`, `equality-report.ps1`, and the `gap-actions/` scripts. Large blast radius for a benefit the recommended approach already delivers. **Deferred, not discarded** — recorded as the follow-on for retiring the 41 dated snapshots (see Risks). |
| **C. Have the collector commit+push atomically so the tree returns to clean.** | This is what Windows does (`equality-report.ps1:334-346`) and what `refresh-equality-matrix.sh` used to do. It fails exactly when it matters: on a diverged or behind checkout the push is rejected, the commit stays local, `ahead_main` grows, and `is_stale()` fails on `ahead_main != 0` instead of `behind_main != 0` — the same 27/27 STALE with a different field. `publish-equality.sh:5-16` documents this precise failure as the reason the sparse worktree exists. Adopting C would re-introduce the defect that design already fixed. Rejected. |
| **D. Keep artifacts in-tree, add `git stash`/`git checkout --` before each pull.** | Discards evidence unattended, and `reconcile-ecosystem.sh:14` explicitly holds the line "Dirty work is NEVER discarded". Rejected. |
| **E. Do nothing to generation; only serialize fleet reconciliation.** | Serialization reduces the *rate* of `behind_main` growth but does not stop it — a single peer publish still permanently blocks the FF pull because of correction 3 above. Necessary-but-insufficient. Rejected as a standalone fix; the amplification is addressed by the preflight in Phase 1 instead. |

**Cross-host push amplification (issue requirement 3).** Once Phase 1 lands, the FF pull is no longer blocked, so the existing `repository_sync-auto:_safe_ff_only_pull` (line 87) and `reconcile-ecosystem.sh:142` can actually succeed and `behind_main` returns to 0 on its own — the amplification stops being a ratchet and becomes ordinary lag. Phase 1 additionally adds a **best-effort FF-pull preflight** to `equality-matrix-cron.sh` (mirroring the Windows `Confirm-FreshCheckout`, but warn-not-fail so a genuinely diverged box still publishes its evidence). No cross-host serialization lock is proposed: `publish-equality.sh:176-179` already no-ops when nothing is newer, and `collect-equality.sh:523-529` already suppresses rewrites when the canonical payload is unchanged, so residual churn is genuinely-changed evidence. A documented serialization order is added for the **manual** fleet-reconcile case only.

---

## Pseudocode

```
# collect-equality.sh — output seam
EQ_STATE_DIR resolution order:
    1. --state-dir <path>            (explicit flag, wins)
    2. $EQ_STATE_DIR                 (env seam; publisher + tests set this)
    3. ${XDG_STATE_HOME:-$HOME/.local/state}/workspace-hub/equality   (new default: OUT OF TREE)
  never fall back to $WS/.claude/state
  mkdir -p the resolved dir; write equality-<machine>.yaml there
  keep the existing canonical-payload commit-on-change guard unchanged
```

```
# build-equality-matrix.py — input list + output seam
#
# CRITICAL (r1 M1): --state-dir REPLACES the default input list; it does NOT
# add another overlay layer. Otherwise the publisher's in-worktree render would
# fold the interactive checkout's STALE peer evidence back into the published
# matrix and destroy the union-of-freshest guarantee publish-equality.sh exists
# to provide.
resolve_state_inputs():
    if any --state-dir given (repeatable):
        return that ordered list, verbatim, later-wins        # NO default layers
    # default (local operator render only):
    layers = [ REPO/.claude/state,          # PEER evidence as published to main (read-only)
               EQ_STATE_DIR ]               # this box's freshly collected evidence
    merged = {}
    for layer in layers:
        for f in sorted(layer.glob("equality-*.yaml")): merged[f.name] = f   # later wins
    return merged.values()

resolve_report_out():
    1. --out-dir <path>
    2. $EQ_REPORT_DIR
    3. ${XDG_STATE_HOME:-$HOME/.local/state}/workspace-hub/equality/reports   # OUT OF TREE
  write <date>-machine-equality-matrix.html + machine-equality-matrix.html alias there
  NOTE: reading REPO/.claude/state is read-only and never dirties the tree
```

```
# publish-equality.sh — read local evidence from the seam
local_dir = resolve EQ_STATE_DIR (same precedence as the collector)
n = count of "$local_dir"/equality-*.yaml
if n == 0:
    fail "no local equality evidence at $local_dir"      # r1 M7: NEVER exit 0 silently
for f in "$local_dir"/equality-*.yaml:                   # was $REPO_ROOT/.claude/state/...
    copy into $WT/.claude/state/  when generated_at > origin's
# --rebuild renders INSIDE the worktree, from the worktree ONLY:
(cd "$WT" && build-equality-matrix.py \
    --state-dir "$WT/.claude/state" --out-dir "$WT/docs/reports")
# allowlist guard at lines 181-187 unchanged
```

```
# scripts/readiness/lib/ff-preflight.sh  (NEW — shared by BOTH collection entry points)
#
# r1 M3: a `git merge --ff-only` that rewrites a script bash is still reading can
# make bash execute truncated input. So the preflight NEVER runs inside a script
# that will keep executing repo code afterwards — it runs in a thin wrapper that
# exec()s the real entry point after the merge lands.
ff_preflight():
    return early unless branch == main
    return early if `git status --porcelain --untracked-files=no` is non-empty
    git fetch --quiet origin main            (timeout-bounded)
    git merge --ff-only origin/main  || warn "checkout diverged; continuing anyway"
    # never a rebase, never a reset, never a stash, never a branch switch

# scripts/readiness/equality-preflight.sh  (NEW — thin wrapper)
    . lib/ff-preflight.sh; ff_preflight
    exec bash "$REPO_ROOT/scripts/readiness/equality-matrix-cron.sh" "$@"

# scripts/curation/curate-session-memory.sh  (r1 M2)
#   its equality block (lines 75-82) is the 6-hourly, 6-machine collector that
#   never publishes. It gets the same preflight, via the same wrapper idiom, or
#   its recorded behind_main keeps ratcheting and this issue does not land.
```

```
# scripts/enforcement/check-equality-artifacts-out-of-tree.sh  (Level 2)
fail if collect-equality.sh contains a default STATE_DIR under $WS/.claude
fail if build-equality-matrix.py writes REPORTS derived from REPO without an explicit override
fail if curate-session-memory.sh invokes the generators without the out-of-tree seam
exit 0 otherwise
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/readiness/collect-equality.sh` | add `--state-dir`/`$EQ_STATE_DIR` seam; default out of tree (lines 18, 21-27, 522-531) |
| Modify | `scripts/readiness/build-equality-matrix.py` | add `--state-dir`/`--out-dir` + env seams; overlay repo peer evidence with local (lines 31-33, 585, 924-930); leave `is_stale()` and `verdict_for()` untouched |
| Modify | `scripts/readiness/publish-equality.sh` | read local evidence from the seam (line 150); fail loud on an empty seam dir (r1 M7); pass explicit `--state-dir`/`--out-dir` to the `--rebuild` invocation (lines 163-170) |
| Create | `scripts/readiness/lib/ff-preflight.sh` | shared, guard-gated, best-effort FF-pull helper |
| Create | `scripts/readiness/equality-preflight.sh` | thin wrapper: preflight then `exec` the cron script (r1 M3 — avoids rewriting a running script) |
| Modify | `scripts/readiness/refresh-equality-matrix.sh` | line 68's `grep … .claude/state/equality-*.yaml` provenance echo must read the seam |
| Modify | `scripts/curation/curate-session-memory.sh` | lines 75-82 invoke the generators; inherit the out-of-tree default **and** the FF preflight (r1 M2 — this is the 6-hourly, 6-machine path) |
| Update | `config/scheduled-tasks/schedule-tasks.yaml` | point `equality-report` and `equality-matrix-refresh` commands at `equality-preflight.sh`; note the installed crontabs must be re-verified per box (they are known to drift from this file) |
| Create | `tests/readiness/test_equality_tree_cleanliness.py` | the TDD core: tree-cleanliness + FF-pull-unblocked |
| Modify | `tests/readiness/test_collect_equality.py` | seam + default-location assertions |
| Modify | `tests/readiness/test_build_equality_matrix.py` | seam + overlay assertions |
| Modify | `tests/readiness/test_publish_equality.py` | publisher reads the seam; worktree render still lands in-tree |
| Create | `scripts/enforcement/check-equality-artifacts-out-of-tree.sh` | Level-2 regression guard per `.claude/rules/patterns.md` |
| Update | `docs/plans/README.md` | index row for this plan |

| Modify | `scripts/windows/equality-report.ps1` | pin `EQ_STATE_DIR`/`EQ_REPORT_DIR` to the in-tree paths before invoking the collector (`:372-377`) and builder (`:380-387`) — preserves current Windows behaviour exactly (Codex r2 M2) |
| Modify | `scripts/readiness/collect-equality.ps1` | forward `EQ_STATE_DIR` when set, pin the in-tree default otherwise (`:196-206` delegates to the bash collector — Codex r2 M1) |

**Explicitly NOT changed in this issue:** `.gitignore` (the published artifacts stay tracked on `main`); `MEASURED` in `collect-equality.sh:314-320`; `is_stale()` / `verdict_for()` in `build-equality-matrix.py`; `scripts/build_pages.py`; `.github/workflows/pages.yml`; `scripts/readiness/refresh-equality-matrix.ps1` and `scripts/readiness/gap-actions/ace-win-2/01-refresh-curation-and-matrix.sh` (both reach the artifacts only through `equality-report.ps1`, which Phase 1 pins — pinned by static test, not by assumption).

**Closed reader enumeration** (`grep -rn "state/equality" scripts/ .github/ config/`, 2026-07-30) — every consumer of `.claude/state/equality-*.yaml` or `docs/reports/*machine-equality-matrix.html`, and its disposition:

| Consumer | Line(s) | Disposition in Phase 1 |
|---|---|---|
| `scripts/readiness/collect-equality.sh` | 18, 522-531 | **changed** — writes via the seam |
| `scripts/readiness/build-equality-matrix.py` | 32-33, 585, 924-930 | **changed** — reads/writes via the seam |
| `scripts/readiness/publish-equality.sh` | 150, 183 | **changed** — reads via the seam; allowlist untouched |
| `scripts/readiness/refresh-equality-matrix.sh` | 68 | **changed** — provenance echo reads the seam |
| `scripts/curation/curate-session-memory.sh` | 75-82 | **changed** — inherits the seam + gains the preflight |
| `scripts/readiness/reconcile-ecosystem.sh` | 219 | unchanged — consumes `--json`, which writes nothing (`build-equality-matrix.py:802-811`) |
| `scripts/readiness/collect-equality.ps1` | 196-206 | **changed** — pins the in-tree seam |
| `scripts/windows/equality-report.ps1` | 306-308, 372-377 | **changed** — pins the in-tree seam |
| `scripts/readiness/refresh-equality-matrix.ps1` | 54-65 | unchanged — reaches the artifacts via `equality-report.ps1` |
| `scripts/readiness/gap-actions/ace-win-2/01-refresh-curation-and-matrix.sh` | 47-65 | unchanged — same |
| `scripts/build_pages.py` | 58 | unchanged — reads the tracked file on `main`, which still exists |
| `.github/workflows/pages.yml` | path filter | unchanged |

### Rollback (r1 M7)

Setting `EQ_STATE_DIR="$WORKSPACE_HUB/.claude/state"` and `EQ_REPORT_DIR="$WORKSPACE_HUB/docs/reports"` in the cron environment restores the pre-change behaviour exactly, without a revert commit. The implementation must keep both seams honoured on every entry point so this holds. The riskiest failure mode is silent: if the seam resolves somewhere unexpected, `publish-equality.sh:176-179` would report `nothing newer … no commit needed` and **exit 0**, taking a box dark on the matrix while every cron reports success — which is why the publisher must fail loud on an empty seam directory (see §Pseudocode).

### Phasing

> **Corrected after adversarial review (Codex r2 MAJOR 1-3).** An earlier draft of this section claimed "no Windows file is touched, so no Windows regression is possible." **That was false.** `scripts/readiness/collect-equality.ps1:196-206` is a *thin overlay* that delegates straight to `bash scripts/readiness/collect-equality.sh` (its own header, line 9: "then delegates to `bash scripts/readiness/collect-equality.sh`"). Changing the bash collector's default output location therefore changes **Windows** collection too — and `scripts/windows/equality-report.ps1:306-308` then looks for `.claude/state/equality-$Machine.yaml`, finds nothing, and commits nothing. Both Windows boxes would go dark on the matrix while every scheduled task reported success. Two further callers inherit the same break: `scripts/readiness/refresh-equality-matrix.ps1:54-65` and `scripts/readiness/gap-actions/ace-win-2/01-refresh-curation-and-matrix.sh:47-65`.

- **Phase 1 (this issue) — Linux/macOS move out of tree; Windows is explicitly *pinned in place*.** The bash default moves out of tree, and the Windows wrappers set the seam back to the current location so their behaviour is byte-for-byte unchanged:
  - `scripts/windows/equality-report.ps1` sets `$env:EQ_STATE_DIR = "$WorkspaceRoot\.claude\state"` and `$env:EQ_REPORT_DIR = "$WorkspaceRoot\docs\reports"` before invoking the collector (`:372-377`) and the builder (`:380-387`).
  - `scripts/readiness/collect-equality.ps1` forwards `EQ_STATE_DIR` if the caller set it and otherwise pins the in-tree default, so a direct `collect-equality.ps1` invocation keeps working.
  - `scripts/readiness/refresh-equality-matrix.ps1` and `gap-actions/ace-win-2/01-refresh-curation-and-matrix.sh` need no change once the wrappers pin the seam — verified by the static Windows-contract tests below.
  This is *more* Windows surface than the earlier draft admitted, but every edit preserves existing behaviour rather than changing it, which is the safer trade.
- **Phase 2 (follow-on issue, to be filed):** cut Windows over to `publish-equality.sh` under Git Bash and move it out of tree too, retiring the working-checkout commit+push. **Gated on [#3554](https://github.com/vamseeachanta/workspace-hub/issues/3554)** (Windows `publish-equality` flock misclassification, currently `status:plan-approved`) landing first — cutting over onto a publisher that silently reports success on Windows would be strictly worse than today.

---

## TDD Test List

The table is split into **RED** (must be written first and must FAIL against `main` — these are the TDD gate) and **REGRESSION** (must pass both before and after — these are guards, not TDD). An earlier draft conflated the two; both r1 (M4) and Codex r2 flagged it. The implementation PR must paste the actual failing output of every RED row before any implementation commit.

### RED — must fail against `main` before implementation

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_build_matrix_leaves_working_tree_clean` | builder writes nothing into the tracked tree | fixture repo with seeded peer evidence, run builder with default env | `git status --porcelain=v1 -z --untracked-files=all` byte-identical before/after |
| `test_collect_leaves_working_tree_clean` | `collect-equality.sh` writes nothing into the tracked tree | fixture repo whose **committed** `equality-<machine>.yaml` has a canonical payload that *differs* from what the collector will emit (r1 M5 — otherwise `collect-equality.sh:523-529` suppresses the write and the test passes vacuously against unfixed code) | identical status snapshot |
| `test_cron_leaves_working_tree_clean` | end-to-end `equality-matrix-cron.sh` with a stubbed publisher | fixture repo, same differing-payload seeding | identical status snapshot |
| `test_curate_session_memory_leaves_tree_clean` | the 6-hourly, 6-machine path also stays clean | fixture repo, run curation's equality block | identical status snapshot |
| `test_ff_pull_unblocked_after_collect_and_build` | **the regression this issue exists for** | bare origin one commit ahead on `.claude/state/equality-*.yaml` + `docs/reports/machine-equality-matrix.html`; local collect+build; `git pull --ff-only` | exit 0; `rev-list --count HEAD..origin/main` == 0 |
| `test_collect_default_state_dir_is_outside_repo` | default resolves out of tree | no env, no flag | resolved dir is not under `git rev-parse --show-toplevel` |
| `test_collect_honors_eq_state_dir_env` | env seam exists | `EQ_STATE_DIR=<tmp>` | yaml at `<tmp>/equality-<machine>.yaml` |
| `test_collect_honors_state_dir_flag_over_env` | flag precedence | both set, differing | flag wins |
| `test_build_matrix_honors_out_dir` | output seam exists | `--out-dir <tmp>` | dated file + alias in `<tmp>`, none in `docs/reports/` |
| `test_build_matrix_state_dir_replaces_default_layers` | **r1 M1** — `--state-dir` must REPLACE, not overlay | repo state seeded with a *fresher* peer than the `--state-dir` copy | render uses only the `--state-dir` contents; the repo copy is not folded in |
| `test_build_matrix_overlays_local_over_repo_in_default_mode` | default (no `--state-dir`) overlays local on top of repo | repo copy older, seam copy newer | render uses the seam copy |
| `test_publish_reads_local_evidence_from_seam` | publisher consumes the new location | `EQ_STATE_DIR=<tmp>` with newer stamp | pushed commit contains that content |
| `test_publish_ignores_stale_in_tree_copy` | publisher must not resurrect a stale `.claude/state` working copy | in-tree copy newer than seam copy | seam copy is authoritative |
| `test_publish_fails_loud_on_empty_seam_dir` | **r1 M7** — silent dark-box is the worst failure mode | `EQ_STATE_DIR` points at an empty dir | non-zero exit + `notify.sh … fail`; must NOT report `nothing newer … no commit needed` and exit 0 |
| `test_preflight_ff_pulls_when_clean_on_main` | preflight advances a clean, behind box | clean tree, behind origin | `behind_main` == 0 at collect time |
| `test_preflight_warns_and_continues_when_diverged` | preflight must never block publishing | diverged clone | warning on stderr, exit 0, publish still attempted |
| `test_preflight_skips_when_not_on_main` | preflight must not switch branches | detached HEAD / feature branch | no fetch/merge, no branch change, exit 0 |
| `test_preflight_skips_when_tracked_files_dirty` | preflight must never clobber operator work | unrelated dirty tracked file | no merge attempted, file untouched |
| `test_preflight_execs_rather_than_sourcing_after_merge` | **r1 M3** — no repo script may be rewritten mid-read | wrapper invoked with a merge that touches `equality-matrix-cron.sh` | the merge completes before the cron script is opened (assert via ordering probe / `exec` in the wrapper) |
| `test_windows_report_ps1_pins_state_and_report_dirs` | **Codex r2 M2** — static contract test | parse `scripts/windows/equality-report.ps1` | it sets `EQ_STATE_DIR` and `EQ_REPORT_DIR` to the in-tree paths before invoking collector/builder |
| `test_windows_collect_ps1_pins_or_forwards_seam` | **Codex r2 M1** — static contract test | parse `scripts/readiness/collect-equality.ps1` | delegation at `:196-206` carries the seam; the in-tree default is preserved when unset |
| `test_enforcement_check_flags_in_tree_default` | the Level-2 guard fires | mutated copy re-pointing the bash default at `.claude/state` | non-zero exit naming the offending path |

### REGRESSION — must pass before AND after (guards, not TDD)

| Test name | What it guards |
|---|---|
| `test_build_matrix_json_mode_writes_nothing` | `--json` (reconcile's read path) never writes — `build-equality-matrix.py:802-811`; already covered by `tests/readiness/test_build_equality_matrix.py:525-549` |
| `test_collect_state_output_does_not_self_trigger_dirty` | already covered by `tests/readiness/test_collect_equality.py:538-545` |
| `test_measured_allowlist_unchanged` | `dirty` scoping stays the 16-entry list at `collect-equality.sh:314-320` |
| `test_is_stale_semantics_unchanged` | no verdict-logic drift in this issue |
| `test_collect_commit_on_change_still_suppresses_rewrite` | canonical-payload guard survives relocation |
| `test_build_matrix_reads_repo_peer_evidence_readonly` | peer evidence still read from the tracked tree without mutating it |
| `test_publish_rebuild_renders_inside_worktree` | `--rebuild` still lands the HTML in the worktree's `docs/reports/` |
| `test_publish_allowlist_still_refuses_unexpected_paths` | existing `test_refuses_unexpected_staged_paths` (`publish-equality.sh:181-187`) |
| `test_publish_still_publishes_when_checkout_diverged_and_dirty` | existing `test_publishes_even_when_local_checkout_diverged_and_dirty` |
| `test_enforcement_check_passes_on_head` | the Level-2 guard is not a false-positive machine |

### Known semantic this plan does NOT change (Codex r2 MINOR 1)

`behind_main` is a **pre-collect snapshot**, not a proof of freshness at publish time. `publish-equality.sh:71-77` locks per host (`publish-equality-${HOST}.lock`), so a peer can push between this box's preflight and its publish, and the evidence will land stamped `behind_main: 0` while `origin/main` has already moved. That is acceptable and unchanged — the stamp describes the tree the dimensions were measured from, which is what `is_stale()` is for. It is recorded here so a reviewer does not read it as a hole this plan opened. A cross-host serialization lock is explicitly **not** proposed (see §Recommended approach); the interleaving window is bounded by the preflight and no longer ratchets.

### Test-authoring notes

- Snapshot with `git status --porcelain=v1 -z --untracked-files=all` and compare bytes — `--untracked-files=no` would hide a stray new dated HTML file, which is one of the failure modes.
- The fixture must place the seam dir **outside** the fixture repo, or `test_collect_default_state_dir_is_outside_repo` passes vacuously.
- macOS `/bin/bash` is 3.2; tests must invoke `bash <script>` (as `tests/readiness/test_publish_equality.py` does), not `sh`.
- Do not assert on absolute `$HOME` paths — resolve via the same precedence the script uses, or the tests break on every machine.
- The two Windows rows are **static contract tests** (parse the `.ps1` text). PowerShell is not available on the Linux/macOS test hosts, so behavioural Windows tests are out of reach; say so rather than pretending coverage.

---

## Acceptance Criteria

- [ ] **RED first:** every row in the RED table above is written and its failing output against `main` is pasted into the implementation PR **before** any implementation commit
- [ ] New tests pass: `uv run pytest tests/readiness/test_equality_tree_cleanliness.py -v`
- [ ] No regression: `uv run pytest tests/readiness/ -v` passes, including all 17 pre-existing `test_publish_equality.py` cases
- [ ] On a real Linux box, two consecutive `bash scripts/readiness/equality-preflight.sh` runs leave `git status --porcelain=v1 -z --untracked-files=all` byte-identical to the pre-run snapshot (transcript captured in the closeout comment)
- [ ] On a real Linux box that is behind `origin/main`, `git pull --ff-only` succeeds immediately after a collection run
- [ ] **Falsifiable end-to-end proof on `gpu-claw`** (chosen because it currently reports `dirty: false / behind_main: 0 / ahead_main: 0` and therefore *can* demonstrate the fix): after one full cycle its published evidence shows `behind_main: 0, ahead_main: 0` and its matrix column is not STALE-CHECKOUT
- [ ] **`dev-primary` is explicitly NOT expected to reach green from this issue alone.** It carries `ahead_main: 1`, and `is_stale()` fails closed on `ahead_main != 0` (`build-equality-matrix.py:235`), so it will remain 27/27 STALE-CHECKOUT while unpushed local commits sit on its `main`. The closeout must state its post-fix `behind_main`/`ahead_main` values and attribute any residual to operator commits — measured, not asserted. (r1 M6: the earlier "or …" escape clause made this criterion unfalsifiable.)
- [ ] `origin/main` still receives `.claude/state/equality-<machine>.yaml` and `docs/reports/<date>-machine-equality-matrix.html` + alias on each publish; the Pages workflow still triggers (verify a run in `gh run list --workflow pages.yml`)
- [ ] The live matrix at `https://vamseeachanta.github.io/workspace-hub/machine-equality-matrix.html` renders and its date line advances after a publish
- [ ] `git diff main -- scripts/readiness/build-equality-matrix.py` shows **no** change to `is_stale()` or `verdict_for()`; `MEASURED` in `collect-equality.sh` is byte-identical
- [ ] No `.gitignore` change; `git ls-files .claude/state/ | grep -c equality` and `git ls-files docs/reports/ | grep -ci equality` are unchanged in kind (counts may grow by daily publishes)
- [ ] `bash scripts/enforcement/check-equality-artifacts-out-of-tree.sh` exits 0 on the implemented branch and non-zero on a deliberately regressed copy
- [ ] **Windows behaviour is byte-for-byte unchanged:** on `ace-win-1`, one `equality-report.ps1` run still commits `.claude/state/equality-ace-win-1.yaml` from the working checkout exactly as today, and the published yaml's `generated_at` advances. Verified on the box, not inferred.
- [ ] Rollback proven: setting `EQ_STATE_DIR`/`EQ_REPORT_DIR` to the in-tree paths reproduces pre-change behaviour on one Linux box
- [ ] Phase-2 follow-on issue filed and linked from #3702, blocked-on [#3554](https://github.com/vamseeachanta/workspace-hub/issues/3554)
- [ ] Issue #3702 carries exactly one `lane:` label matching this plan's `Lane: lane:claude` header (per [#3029](https://github.com/vamseeachanta/workspace-hub/issues/3029)) — it currently has none
- [ ] `bash scripts/legal/legal-sanity-scan.sh --diff-only` passes
- [ ] Review artifacts posted to `scripts/review/results/`

---

## Adversarial Review Summary

T2 scope → 2 providers per `SOUL.runtime.md` Hard Gate 4. Agy/Gemini are not installed on this host (`command -v agy` / `gemini` → MISSING); recorded as UNAVAILABLE per the `scripts/review/results/` convention rather than blocking.

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (r1, inline) | **MAJOR** (7 MAJOR, 5 MINOR) | M1 `--state-dir` overlay semantics would fold stale peer evidence into the *published* render; M2 the preflight was applied to only one of two collection entry points, so `behind_main` keeps ratcheting on the 6-hourly path; M3 a mid-run `git merge --ff-only` can rewrite the script bash is executing; M4 five "TDD" rows are green today; M5 the headline cleanliness test was vacuous as specified; M6 AC5 was unfalsifiable and cannot be met on `dev-primary`; M7 no rollback, and an empty seam dir makes the publisher exit 0 while a box goes dark |
| Codex (r2, `submit-to-codex.sh`) | **MAJOR** (3 MAJOR, 2 MINOR) | M1 `collect-equality.ps1:196-206` delegates to `collect-equality.sh`, so "no Windows file touched ⇒ no Windows regression" was **false**; M2 `equality-report.ps1:306-308,372-377` would find no state yaml and commit nothing; M3 `refresh-equality-matrix.ps1:54-65` and `gap-actions/ace-win-2/01-…:47-65` inherit the same break; m1 `behind_main` is a pre-collect snapshot and the publisher lock is per-host, so a peer can push inside the window; m2 the RED suite does not exist yet, so its non-vacuity cannot be inspected |
| Agy / Gemini | UNAVAILABLE | not installed on the planning host |

**Overall result:** FAIL on the first round — the plan was revised, not approved. Both providers returned MAJOR independently and their findings did not overlap, which is the argument for having run both.

Revisions made in response (all applied to this document):

1. **§Pseudocode** — `--state-dir` now *replaces* the default input list rather than adding an overlay layer, and the publisher passes exactly the worktree dir. Pinned by the new `test_build_matrix_state_dir_replaces_default_layers`. *(r1 M1)*
2. **§Pseudocode, §Files to Change** — the FF preflight is factored into `scripts/readiness/lib/ff-preflight.sh` and applied to **both** `equality-matrix-cron.sh` and `curate-session-memory.sh`. *(r1 M2)*
3. **§Pseudocode, §Files to Change** — the preflight runs in a thin `scripts/readiness/equality-preflight.sh` that `exec`s the real entry point after the merge, so no repo script is rewritten while bash is reading it. *(r1 M3)*
4. **§TDD Test List** — split into RED (must fail first) and REGRESSION (guards); the implementation PR must paste the RED failures before implementing. *(r1 M4, Codex m2)*
5. **§TDD Test List** — `test_collect_leaves_working_tree_clean` now specifies a committed yaml whose canonical payload *differs*, so `collect-equality.sh:523-529` cannot make it pass vacuously. *(r1 M5)*
6. **§Acceptance Criteria** — the unfalsifiable "or …" clause is gone; `gpu-claw` is the falsifiable end-to-end proof box, and `dev-primary` is stated up front as **not** expected to reach green from this issue because of `ahead_main`. *(r1 M6)*
7. **§Files to Change** — new §Rollback (env-var restore), and the publisher must fail loud on an empty seam directory instead of exiting 0. *(r1 M7)*
8. **§Phasing** — the false "no Windows regression is possible" claim is retracted in place, with the delegation chain quoted. Phase 1 now **pins** Windows to the in-tree location via `equality-report.ps1` and `collect-equality.ps1`, preserving current Windows behaviour exactly instead of silently changing it. *(Codex M1, M2)*
9. **§Files to Change** — a closed 12-row reader-enumeration table with the disposition of every consumer, including the two Windows callers Codex named. *(Codex M3, r1 m1)*
10. **§TDD Test List** — two static Windows-contract tests added, plus an explicit note that behavioural Windows tests are out of reach on the Linux/macOS test hosts. *(Codex M1/M2)*
11. **§TDD Test List** — new "Known semantic this plan does NOT change" subsection recording that `behind_main` is a pre-collect snapshot and the publisher lock is per-host. *(Codex m1)*
12. **§Risks** — `refresh-equality-matrix.sh:42` uses `pull --rebase --autostash` and so already works around the defect, which is why operators running manual refreshes never saw it. *(r1 m2)*
13. Header `Project:` removed; the `lane:` label gap is now an explicit acceptance-criteria line. *(r1 m3, m4)*

**Not yet done:** the RED tests are not written, so no reviewer has inspected their actual failure output. Codex m2 and r1 M4 are therefore *mitigated by process* (an acceptance criterion), not *closed by evidence*. A reviewer who wants them closed before approval should say so.

---

## Risks and Open Questions

- **Risk (HIGH): the `is_stale()` `ahead_main != 0` condition is a second STALE trigger this plan does not remove.** dev-primary held `ahead_main: 17`. Even a perfectly clean, fully-pulled box with one unpushed WIP commit will still grade 27/27 STALE-CHECKOUT. Phase 1 will therefore **not** by itself return dev-primary to green if operators keep local commits on `main`. Acceptance criterion 5 is written to expose this rather than hide it.
- **Risk (HIGH): losing the local `.claude/state/equality-<self>.yaml` changes what the fleet sees during the transition.** Between the code landing and the first successful publish, a box's own row comes from whatever is on `origin/main`. Mitigation: the publisher is unchanged in its "newer evidence wins" semantics (`publish-equality.sh:156`), so the first post-change run republishes immediately. Verify on one box before fleet rollout.
- **Risk (MEDIUM): the out-of-tree state dir is not backed up or synced.** A box reimaged or with `$HOME` cleared loses its local evidence until the next collect. Acceptable — the evidence is regenerable and the canonical copy lives on `origin/main`. Worth stating in the script header.
- **Risk (MEDIUM): `$XDG_STATE_HOME` semantics on macOS and Git-Bash-on-Windows.** macOS does not set `XDG_STATE_HOME`; the `${XDG_STATE_HOME:-$HOME/.local/state}` fallback covers it. Git Bash on Windows maps `$HOME` to the user profile; Phase 1 does not run the bash collector on Windows, but `publish-equality.sh` does — its seam resolution must be tested under a Windows-shaped `$HOME` or explicitly deferred to Phase 2.
- **Risk (MEDIUM): partial-fleet rollout skew.** Boxes running the old code keep dirtying their trees; boxes running the new code do not. Both still publish compatible evidence, so the matrix stays coherent; but `behind_main` on old-code boxes will not self-heal until they pull the change. Roll out to `dev-primary` first (it is the worst-affected and the control plane).
- **Risk (LOW): the FF-pull preflight could surprise an operator mid-work.** Mitigated by three guards — only on `main`, only when no tracked file is modified, and `--ff-only` (never a merge or rebase). Tests `test_cron_preflight_skips_when_not_on_main` and `test_cron_preflight_skips_when_tracked_files_dirty` pin this.
- **Risk (MEDIUM): the manual refresh path already masks this defect, which is why it went unnoticed.** `refresh-equality-matrix.sh:42` uses `git pull --rebase --autostash`, which succeeds even with the artifacts dirty; only the *cron* path ratchets. An operator running a manual refresh sees a healthy box and cannot reproduce the fleet symptom. Rollout verification must therefore exercise the cron entry point, not the manual one. (r1 m2)
- **Risk (LOW): 41 dated matrix HTML files and growing 1/day forever.** Not caused by this defect and not fixed here. Candidate follow-on: retire dated snapshots to an `equality-state` ref using the `equivalence_state.py` idiom, keeping only the alias on `main`.
- **Open:** should `is_stale()` distinguish "behind because peers published" from "behind because this box is genuinely stale"? A publish-only delta is not evidence of harness drift. Flagging for the user — **not** changed in this plan because it alters verdict semantics for every machine.
- **Open:** should `ahead_main != 0` remain fail-closed, or should it be narrowed to "ahead with commits that touch `MEASURED` paths"? Same reason for deferral.
- **Open:** the installed crontabs are known to drift from `config/scheduled-tasks/schedule-tasks.yaml` (the file declares `equality-report` as weekly, while the published evidence shows a 6-hourly cadence). Rollout should verify the *installed* crontab on each box, not the YAML.

---

## Complexity: T2

**T2** — multi-file harness change across two languages (bash + Python) with a new test module and a new Level-2 enforcement script, but no new subsystem, no schema change, and no verdict-logic change. Two-provider adversarial review per `SOUL.runtime.md` Hard Gate 4.
