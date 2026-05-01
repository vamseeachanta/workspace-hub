# Archived Skill: `overnight-wave-pack-worktree-isolation`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/overnight-wave-pack-worktree-isolation`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/overnight-wave-pack-worktree-isolation`
Consolidation date: 2026-04-29

---

---
name: overnight-wave-pack-worktree-isolation
description: Safely launch overnight multi-terminal workspace-hub planning packs from isolated worktrees when the main checkout is dirty or prompts share planning/index files.
version: 1.0.0
---

# Overnight wave-pack worktree isolation

Use when:
- an overnight prompt pack is ready to launch
- the main workspace-hub checkout is already dirty, or
- multiple prompts may touch shared planning surfaces like `docs/plans/README.md`

Problem
Launching all prompts from one dirty checkout creates avoidable git contention and mixes unrelated working-tree state into the overnight run, even if prompts claim "owned rows only".

Reusable approach
1. Inspect the current checkout first:
   - `git status --short`
   - `git worktree list`
2. If main is dirty or shared planning files are in prompt scope, create one fresh worktree per terminal from the current HEAD.
3. Copy the master overnight pack and prompt files into each worktree.
4. Rewrite absolute repo paths inside each copied prompt from the original checkout path to that worktree path.
5. Launch Claude from inside each worktree with the copied prompt file loaded into a shell variable.
6. Point logs and expected result artifacts to the worktree-local paths.
7. If a morning monitor job already exists, update it to inspect the worktree result paths instead of the original checkout.

Concrete pattern
```bash
git worktree add -b nightly/foo-t1 /mnt/local-analysis/worktrees/ws-foo-t1 HEAD
cp docs/plans/master-pack.md /mnt/local-analysis/worktrees/ws-foo-t1/docs/plans/
cp docs/plans/overnight-prompts/foo/*.md /mnt/local-analysis/worktrees/ws-foo-t1/docs/plans/overnight-prompts/foo/
perl -0pi -e 's#/mnt/local-analysis/workspace-hub#/mnt/local-analysis/worktrees/ws-foo-t1#g' \
  /mnt/local-analysis/worktrees/ws-foo-t1/docs/plans/overnight-prompts/foo/*.md \
  /mnt/local-analysis/worktrees/ws-foo-t1/docs/plans/master-pack.md
cd /mnt/local-analysis/worktrees/ws-foo-t1
PROMPT=$(< docs/plans/overnight-prompts/foo/terminal-1.md)
claude -p --permission-mode acceptEdits --no-session-persistence --output-format text --max-budget-usd 20 \
  "$PROMPT" </dev/null > logs/terminal-1.log 2>&1
```

Verification
- read back the copied prompt file and confirm the worktree path was rewritten
- verify all launched processes are running
- verify the monitor/cron references the worktree output paths

Pitfalls
- Do not launch from the dirty main checkout when prompts share `docs/plans/README.md`
- Do not leave prompts pointing at the original repo path after copying into a worktree
- Do not forget to update the morning monitor job; otherwise it will report false missing artifacts
