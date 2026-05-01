# Repo-Sync Handoff Prompt — parallel/fast resume

Drop the body below into a fresh Claude Code session in `/mnt/local-analysis/workspace-hub`. Token burn is not a concern; optimize for wall-clock completion.

---

I am resuming `/repo-sync` from session 2026-04-30/05-01. Read `docs/sessions/2026-05-01-repo-sync-exit-handoff.md` for full state. Goal: get every workspace-hub repo, sibling, and worktree to a clean, pushed state as fast as possible. Use agent teams aggressively (4–6 parallel subagents) for any independent work. Token burn is acceptable.

## Hard rules (Iron Law — non-negotiable)
- **No** `git push --force`, `git reset --hard`, or auto-resolve of merge conflicts without explicit user OK.
- **No** `git commit --no-verify` unless user types `bypass`. The prior session hardened the scanner so a clean commit should pass.
- **Skip** `assethold` (3-day-old codex branch with merge conflicts) and `aceengineer-website` (3-day-old branch with `[gone]` upstream) — both fall outside the 8-hour merge-to-main window. Note them; do not touch them.
- **Skip** `aceengineer-admin` — already committed and pushed last session. The user is rotating the Telegram token via `@BotFather` separately. Do not re-edit `aceengineer-admin/admin/software.md`.
- **Skip** `acma-projects/` working-tree edits — its sparse-checkout disable left ~368K files unmaterialized; rematerialization runs in background, do not block on it.
- Each worktree has its own `.git/index`; parallel commits across worktrees are safe. Do NOT run parallel commits on the same workspace-hub root.

## Phase 0 — Preflight (sequential, fast)

```bash
cd /mnt/local-analysis/workspace-hub
date -Iseconds
pgrep -af 'git (commit|merge|rebase|reset|stash push|checkout)' || echo "no active git ops"
ls .git/index.lock 2>/dev/null && rm -f .git/index.lock || echo "no lock"
git log --oneline -3
git status --porcelain | wc -l
```

If `pgrep` shows live git ops not owned by you (Hermes, auto-sync), wait 60s and re-check before proceeding.

## Phase 1 — Land workspace-hub Phase 3 commit (sequential, must come first)

The prior session staged 563 files but the commit DID NOT land. Last retry blocked with:
```
BLOCKED: 0 critical, 1 high findings.
```
Output was truncated; the HIGH finding's identity was not captured. **First action after preflight:** run the scanner directly to identify the lone HIGH finding:

```bash
cd /mnt/local-analysis/workspace-hub
git add -A
bash .claude/hooks/check-skill-content.sh 2>&1 | grep -E "^[[:space:]]+(CRITICAL|HIGH)" | head -10
```

Once you know the file:line and pattern_id:
- If false-positive (e.g. another `html_comment_injection` triggered by `secret`/`hidden`/`override`/`ignore`/`system` substring in a `<!-- scanner-allow:... -->` marker): change that line's marker to `<!-- scanner-allow:all -->`.
- If real: ask user before deciding scrub-vs-mark-vs-bypass.

Also: the prior session saw transient `.fuse_hidden*` files in `.claude/hooks/` that disappear mid-`git add`. Harmless but causes `git add -A` to print `fatal: unable to stat`. Re-run `git add -A` if you see it.

```bash
git log --oneline -1
```

- If HEAD message contains `chore(sync): /repo-sync mass-stage session artifacts + scanner hardening` → commit landed. Skip to Phase 2.
- Else retry in foreground:
  ```bash
  git add -A
  git commit -m "chore(sync): /repo-sync mass-stage session artifacts + scanner hardening" 2>&1 | tail -10
  git push 2>&1 | tail -10
  ```
- If pre-commit hook BLOCKS with new findings: surface the findings inline (no `--no-verify`), ask user before any decision. Do NOT iterate the scanner regex more — the prior session already did 4 rounds.

## Phase 2 — Kick off long-running work in parallel (background, fire-and-forget)

Three independent long jobs. Launch all three in background; do NOT block on any.

### 2A. acma-projects rematerialization (~30 min)
```bash
nohup bash -c 'cd /mnt/local-analysis/workspace-hub/acma-projects && git checkout HEAD -- .' > /tmp/acma-rematerialize.log 2>&1 &
echo "acma PID $!"
```

### 2B. Encoding health check (~2 min)
```bash
nohup bash /mnt/local-analysis/workspace-hub/.claude/hooks/check-encoding.sh > /tmp/encoding-check.log 2>&1 &
echo "encoding PID $!"
```

### 2C. Worktree inventory (~3 min, lightweight)
```bash
cd /mnt/local-analysis/workspace-hub
nohup bash -c '
git worktree list --porcelain | awk "/^worktree/{print \$2}" | while read wt; do
  case "$wt" in
    /mnt/local-analysis/workspace-hub|/mnt/local-analysis/workspace-hub-issue-2515-planning) continue ;;
    *acma-projects*) continue ;;
  esac
  branch=$(timeout 10 git -C "$wt" branch --show-current 2>/dev/null)
  [ -z "$branch" ] && branch="(detached)"
  dirty=$(timeout 10 git -C "$wt" status --porcelain 2>/dev/null | wc -l)
  ahead_behind=$(timeout 10 git -C "$wt" rev-list --left-right --count HEAD...@{u} 2>/dev/null | tr "\t" "/" || echo "no-upstream")
  upstream_state=$(timeout 10 git -C "$wt" for-each-ref --format="%(upstream:track)" "refs/heads/$branch" 2>/dev/null)
  printf "%s\t%s\t%d\t%s\t%s\n" "$wt" "$branch" "$dirty" "$ahead_behind" "$upstream_state"
done | sort -t$"\t" -k3 -n -r > /tmp/worktree-inventory.tsv
' > /tmp/worktree-inventory.log 2>&1 &
echo "inventory PID $!"
```

## Phase 3 — Sibling-repo sweep (parallel agent team — 4 agents)

While the long jobs run, dispatch 4 subagents in a single message. Each owns a slice of sibling repos. Skip the locked-out repos.

**Agent slices** (sized for balance):
- Agent S1: `achantas-data achantas-media hobbies investments sabithaandkrishnaestates`
- Agent S2: `sd-work assetutilities client_projects digitalmodel doris`
- Agent S3: `frontierdeepwater OGManufacturing rock-oil-field saipem seanation`
- Agent S4: `teamresumes worldenergydata`

**Each agent prompt template** (substitute `{REPOS}`):

```
Repository ecosystem: /mnt/local-analysis/workspace-hub

Goal: For each of these sibling repos {REPOS}, commit and push any session-recent dirty state. You write file edits and per-repo commits; do not touch /mnt/local-analysis/workspace-hub itself or any worktree under /mnt/local-analysis/.

For each repo:
1. cd /mnt/local-analysis/workspace-hub/<repo>
2. Check: git status --porcelain ; git branch --show-current
3. If clean (0 dirty), skip and report CLEAN.
4. If dirty: scan for secrets first — `grep -RIE '(api[_-]?key|token|secret|password|AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{36}|[0-9]{8,}:[A-Za-z0-9_-]{30,})' --include='*.md' --include='*.py' --include='*.sh' --include='*.yaml' --include='*.yml' --include='*.json' .` against changed files. If any hit, STOP and report SECRET-RISK with file:line — do NOT commit.
5. If clean of secrets and within 8-hour window: `git add -A && git commit -m "chore(sync): /repo-sync mass-stage session artifacts" && git push` (use `git push -u origin HEAD` if no upstream).
6. If pre-commit hook blocks: surface findings, do NOT --no-verify.

Iron Law: no force-push, no reset --hard, no auto-merge-conflict-resolve.

DO NOT touch: aceengineer-admin (already done), assethold (conflicts), aceengineer-website ([gone] upstream), acma-projects (sparse transition).

Report a JSON line per repo: {"repo":"X","action":"committed|pushed|clean|secret-risk|blocked","sha":"<sha>","note":"<short>"}.
```

Dispatch all 4 in parallel (single message, multiple Agent tool calls).

## Phase 4 — Wait for inventory + dispatch worktree teams (parallel)

```bash
wait $(pgrep -f "worktree-inventory.tsv" 2>/dev/null) 2>/dev/null
cat /tmp/worktree-inventory.tsv
```

Worktrees may number ~56. Filter to actionable subset (dirty>0 AND upstream tracks remote) and split into batches of 6 per agent. Spawn agents in groups of 4–6 (parallel batch).

**Worktree-batch agent prompt template** (substitute `{WORKTREE_LIST}`):

```
Repository: /mnt/local-analysis/workspace-hub (multi-worktree)

You own these worktrees, one at a time: {WORKTREE_LIST}.
For each path:
1. cd <path>
2. branch=$(git branch --show-current); [ -z "$branch" ] && echo "DETACHED-SKIP" && continue
3. Check upstream tracking: git for-each-ref --format='%(upstream:short) %(upstream:track)' "refs/heads/$branch"
4. If upstream is "" or contains "[gone]": report STALE-NEEDS-DECISION and skip.
5. If dirty: secret scan with grep (same regex as sibling-sweep). If hit, STOP and report SECRET-RISK.
6. git add -A && git commit -m "chore(sync): /repo-sync session artifacts on $branch"
7. If commit blocked by pre-commit hook: surface findings and STOP for that worktree (no --no-verify).
8. git push 2>&1 (no -u; upstream already exists per step 3)
9. If push rejected: git pull --no-rebase ; git push. If still rejected, report PUSH-BLOCKED.

Each worktree has its own .git/index, so no cross-lock contention with parallel agents.
DO NOT touch: /mnt/local-analysis/workspace-hub itself, workspace-hub-issue-2515-planning, anything under acma-projects.

Iron Law: no force-push, no reset --hard, no auto-resolve.

Report JSON line per worktree: {"path":"X","branch":"B","action":"pushed|stale-skip|detached-skip|secret-risk|push-blocked|blocked","sha":"<sha>","note":"<short>"}.
```

Dispatch all worktree-batch agents in parallel in one message (4–6 agents at once).

## Phase 5 — Drain results, handle exceptions (sequential)

When all sibling and worktree subagents return:

1. Collate JSON lines. Tally: pushed / clean / stale-skip / detached-skip / secret-risk / push-blocked / blocked.
2. **secret-risk**: surface to user immediately with file:line; do not auto-redact.
3. **detached-skip**: report path + last commit. User decides per detached HEAD.
4. **stale-skip** (`[gone]` upstream): report path. User decides preserve-or-prune.
5. **blocked** (pre-commit hook): surface scanner findings inline.
6. **push-blocked**: usually means parallel push race; retry once after `pull --no-rebase`.

## Phase 6 — Special-case worktrees (sequential, ask before each)

These need user decisions, not automation:

- `/mnt/local-analysis/workspace-hub-issue-2515-planning` — has 31,718 staged deletions from branch work pre-dating this sync. Options: (a) commit the deletions on `issue-2515-planning` branch, (b) `git reset --mixed` to unstage, (c) leave alone. Ask user.

- Any worktree whose branch is `[gone]` upstream and has local-only commits: ask user (preserve via patch export, prune, or push as new branch).

## Phase 7 — Drain background jobs

```bash
# acma rematerialize
ps -p $(cat /tmp/acma-pid 2>/dev/null) 2>&1 | tail -1 || echo "acma done or never launched"
tail -5 /tmp/acma-rematerialize.log
cd /mnt/local-analysis/workspace-hub/acma-projects && ls | wc -l   # expect ~368K dirs visible after success

# Encoding
cat /tmp/encoding-check.log
# fix any UTF-16/CRLF flagged: iconv -f UTF-16 -t UTF-8 <file> | sed 's/\r//' > /tmp/fixed.md && mv /tmp/fixed.md <file>
```

If acma rematerialization is still running at this point, leave it; it will complete on its own and `git status` will show 0 dirty when done.

## Phase 8 — Final report

Output a single markdown table with columns:
`scope | action | count | notes`

Rows:
- workspace-hub commit (Phase 1)
- Sibling repos (per-status counts from agent team)
- Worktrees (per-status counts from agent team)
- 2515-planning worktree (decision pending or applied)
- Encoding check
- acma-projects rematerialize (running / done)
- aceengineer-admin (DONE — prior session)
- assethold + aceengineer-website (SKIPPED — outside 8h window)

Then list any items still requiring user decision. Then suggest a `/schedule` agent for ~2 weeks out to re-run `/repo-sync` to catch drift if any worktrees were left undecided.

## Memory candidates to save after success

```
- feedback_worktree_config_sparsecheckout.md — sparseCheckout lives in .git/config.worktree, not local config; --unset --local misses it
- feedback_scanner_marker_self_defeat.md — <!-- scanner-allow:hardcoded_secret --> matches html_comment_injection (word "secret" in comment); use scanner-allow:all for HTML comments
- feedback_aceengineer_admin_no_scanner.md — sibling repos don't run workspace-hub's check-skill-content.sh; secrets can slip through
- feedback_subagent_survey_token_burn.md — direct bash beats subagents for read-only surveys (56-worktree inventory: bash 3min vs subagent 14min @ 17%)
- feedback_pre_commit_scanner_cascade.md — scanner false-positives surface in tiers; plan multi-round hardening
- feedback_parallel_worktree_commits_safe.md — each worktree has its own .git/index; parallel commits across worktrees don't race; only the superproject root locks
```

End of handoff.
