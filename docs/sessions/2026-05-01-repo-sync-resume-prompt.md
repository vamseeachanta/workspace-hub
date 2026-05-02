# Resume Prompt — /repo-sync after restart

Copy the block below into a fresh Claude Code session running in `/mnt/local-analysis/workspace-hub`.

---

I am resuming an interrupted `/repo-sync` from session 2026-04-30/05-01. Read `docs/sessions/2026-05-01-repo-sync-exit-handoff.md` first for full state, then drive the resume below. Use the `workspace-hub:repo-sync` skill's Iron Law (no force-push, no `reset --hard`, no auto-resolve conflicts) and the `Hermes-active preflight check` (pgrep before commits).

## Authorizations standing from the prior session
- All workspace-hub session artifacts staged before exit are safe to commit + push to `main`.
- `git commit --no-verify` is **NOT** authorized — the prior session hardened the scanner so a clean commit should pass; if it doesn't, surface what blocks and ask before bypass.
- `aceengineer-admin` token decision: already committed + pushed to private branch `codex/burn-20260427-issue-2493`. User will rotate the token via `@BotFather /revoke` separately. Do not re-edit that file.
- 8-hour merge-to-main rule: changes within last 8 hours are safe to merge to main; older work stays on its branch.

## Resume sequence

### Step 1 — Verify Phase 3 commit landed (or retry)

```bash
cd /mnt/local-analysis/workspace-hub
pgrep -af 'git (commit|merge|rebase|reset|stash push)' || echo "no active git ops"
git log --oneline -3
git status --porcelain | wc -l
```

- If `HEAD` shows `chore(sync): /repo-sync mass-stage session artifacts + scanner hardening` → Phase 3 landed, skip to Step 2.
- If `HEAD == 1aa2f6f47 docs(gtm): harden prospect demo SOP for #2346` → commit didn't land. Retry:
  ```bash
  rm -f .git/index.lock
  git add -A
  git commit -m "chore(sync): /repo-sync mass-stage session artifacts + scanner hardening" 2>&1 | tail -10
  ```
- If pre-commit hook still blocks: read its output; the prior session reduced it to 0 BLOCKED, so any new finding is real. Surface it and stop.

### Step 2 — Push workspace-hub to origin/main

```bash
git push 2>&1 | tail -10
```

If `[rejected]` due to upstream advancing during the long session: `git pull --no-rebase` (merge), retry push.

### Step 3 — Encoding check

```bash
bash .claude/hooks/check-encoding.sh 2>&1 | tail -15
```

Warn-only mode. Fix any UTF-16/CRLF files surfaced via `iconv -f UTF-16 -t UTF-8 <file> | sed 's/\r//' > /tmp/fixed.md && mv /tmp/fixed.md <file>` then commit individually.

### Step 4 — acma-projects rematerialization (long, background)

Sparse config was disabled but only 34 of ~368K files are on disk. To finish:

```bash
cd /mnt/local-analysis/workspace-hub/acma-projects
nohup git checkout HEAD -- . > /tmp/acma-rematerialize.log 2>&1 &
echo "PID $! launched. Expect 20-40 min runtime."
```

Do NOT block on this. Move on to Step 5.

### Step 5 — Sibling repo sweep verification

```bash
cd /mnt/local-analysis/workspace-hub
for repo in aceengineer-admin achantas-data achantas-media hobbies investments sabithaandkrishnaestates sd-work assethold assetutilities client_projects digitalmodel doris frontierdeepwater OGManufacturing rock-oil-field saipem seanation teamresumes worldenergydata aceengineer-website; do
  [ -e "$repo/.git" ] || continue
  d=$(timeout 20 git -C "$repo" status --porcelain 2>/dev/null | wc -l)
  [ "$d" != "0" ] && printf "%-25s dirty=%s branch=%s\n" "$repo" "$d" "$(git -C "$repo" branch --show-current 2>/dev/null)"
done
```

For each dirty repo: review the diff, commit only if within the 8-hour window. Skip `assethold` (3-day-old codex branch with merge conflicts) and `aceengineer-website` (3-day-old branch with deleted upstream) unless user authorizes new direction.

### Step 6 — Worktree decisions

```bash
cd /mnt/local-analysis/workspace-hub
git worktree list --porcelain | awk '/^worktree/{print $2}' | while read wt; do
  [ "$wt" = "/mnt/local-analysis/workspace-hub" ] && continue
  [ "$wt" = "/mnt/local-analysis/workspace-hub-issue-2515-planning" ] && continue
  case "$wt" in *acma-projects*) continue;; esac
  branch=$(timeout 10 git -C "$wt" branch --show-current 2>/dev/null)
  [ -z "$branch" ] && branch="(detached)"
  d=$(timeout 10 git -C "$wt" status --porcelain 2>/dev/null | wc -l)
  printf "%-90s %-50s dirty=%d\n" "$wt" "$branch" "$d"
done | sort -k3 -n -r > /tmp/worktree-inventory.txt
head -30 /tmp/worktree-inventory.txt
echo "total: $(wc -l < /tmp/worktree-inventory.txt) ; dirty: $(awk '$NF !~ /=0$/' /tmp/worktree-inventory.txt | wc -l)"
```

Then dispatch agent teams for the dirty subset (per user's "use agent teams" directive). Group ~6 worktrees per agent. Per `Multi-agent commit serialization` memory rule: subagents do file-edits + per-worktree commits (each worktree has its own .git/index, so no cross-lock); main session monitors. **Do NOT** dispatch agents that touch the main workspace-hub `.git/index` in parallel — only worktree-local commits.

Each subagent prompt template:
```
Repository: workspace-hub. You own these worktrees: [list].
For each: (a) verify branch tracks remote, (b) `git add -A`, (c) commit with message "chore(sync): /repo-sync session artifacts on <branch>", (d) `git push -u origin HEAD`.
Skip detached-HEAD worktrees and worktrees with [gone] upstream — report those for main-session decision.
Run `bash .claude/hooks/check-skill-content.sh` blocks: surface findings, do not --no-verify.
Do NOT touch /mnt/local-analysis/workspace-hub itself or the 2515-planning worktree.
```

### Step 7 — 2515-planning worktree decision

This worktree has 31,718 staged deletions on branch `issue-2515-planning`. Those are pre-existing in-progress branch work, NOT artifacts of the sparse-checkout disable. Ask user: keep deletions (commit), revert (reset --mixed), or leave alone.

### Step 8 — Final report

Output a markdown table of:
- Phase 3 commit SHA
- aceengineer-admin push status (already done last session)
- Encoding-check findings
- Sibling repos still dirty after sweep
- Worktrees committed by subagents (count)
- Worktrees needing user decision (list)
- acma-projects rematerialize PID + log location

## Memory candidates to save after success

These were observed but not written by the interrupted session:

1. **feedback_worktree_config_sparsecheckout.md** — `sparseCheckout` config lives in `.git/config.worktree` for multi-worktree repos; `git config --local --unset` doesn't reach it. Use `git config --worktree --unset core.sparseCheckout` or operate on `.git/config.worktree` directly.

2. **feedback_scanner_marker_self_defeat.md** — using `<!-- scanner-allow:hardcoded_secret -->` triggers `html_comment_injection` because that pattern matches the literal word "secret" in HTML comments. Use `scanner-allow:all` for HTML-comment markers, or `# scanner-allow:<id>` (shell-comment) where context allows.

3. **feedback_aceengineer_admin_no_scanner.md** — `aceengineer-admin/.git/hooks/pre-commit` doesn't run the workspace-hub `check-skill-content.sh` scanner. A token committed there bypasses the scan that catches it elsewhere. Treat scanner coverage as workspace-hub-only.

4. **feedback_subagent_survey_token_burn.md** — read-only worktree-inventory subagent timed out at 17% in 14 min for 56 worktrees. Direct bash inventory is 30× faster for survey work. Reserve subagents for write/decision tasks, not surveys.

5. **feedback_pre_commit_scanner_cascade.md** — pre-commit security scanner false-positives cascade: each iteration's regex fix exposes a new tier (uv_run → agent_config_mod → html_comment_injection on the marker itself). Plan multi-round when hardening, not single-pass.

End of resume prompt.
