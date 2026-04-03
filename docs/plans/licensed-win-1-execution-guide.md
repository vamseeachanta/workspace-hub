# Licensed-Win-1 Execution Guide

Updated: 2026-04-02
Machine: licensed-win-1 (Windows, D:\workspace-hub)
Available: Claude Code CLI, Codex CLI, Gemini CLI, Python, Git Bash, OrcFxAPI
NOT available: Hermes (installation restriction)

## Best execution approach for this machine

Since Hermes cannot be installed but all 3 agent CLIs (claude, codex, gemini) work,
the recommended pattern is:

### Option A: Claude Code CLI (recommended for most prompts)

Claude Code can read the repo, run Python, and commit/push. Use it as the
primary executor for all 4 licensed-win-1 prompts.

```powershell
cd D:\workspace-hub
git pull origin main

claude -p "Read docs/plans/licensed-win-1-orcawave-orcaflex-prompts.md, execute PROMPT 1 (queue validation). Use python (not uv run). Commit and push results when done."
```

Then for subsequent prompts:
```powershell
claude -p "Read docs/plans/licensed-win-1-orcawave-orcaflex-prompts.md, execute PROMPT 2 (minimal .sim fixture). Use python (not uv run). Commit and push results when done."
```

### Option B: Codex CLI (good for parallelism if Claude is busy)

```powershell
codex -p "Read docs/plans/licensed-win-1-orcawave-orcaflex-prompts.md, execute PROMPT 3 (.owr fixtures). Use python (not uv run). Commit and push results when done."
```

### Option C: Gemini CLI (architecture review after execution)

Use Gemini for post-execution review rather than primary execution:
```powershell
gemini -p "Review queue/completed/ for recent solver results. Verify result.yaml files are well-formed. Check .owr and .sim files exist. Report any issues."
```

## Execution plan — 3 terminals, no git contention

### Terminal 1 (Claude Code) — sequential, file-creating prompts
```powershell
cd D:\workspace-hub
git pull origin main

# Run prompts 1-4 in sequence (each creates files + commits)
claude -p "Read docs/plans/licensed-win-1-orcawave-orcaflex-prompts.md. Execute PROMPT 1 (queue validation with WAMIT batch). Use python (not uv run). OrcFxAPI is available. Commit and push when done. Comment on GH issue #1761."

claude -p "Read docs/plans/licensed-win-1-orcawave-orcaflex-prompts.md. Execute PROMPT 2 (minimal .sim fixture). Use python (not uv run). Create digitalmodel/tests/fixtures/ if needed. Commit and push when done. Comment on GH issue #1762."

claude -p "Read docs/plans/licensed-win-1-orcawave-orcaflex-prompts.md. Execute PROMPT 3 (.owr result fixtures). Use python (not uv run). Commit and push when done. Comment on GH issue #1763."

claude -p "Read docs/plans/licensed-win-1-orcawave-orcaflex-prompts.md. Execute PROMPT 4 (mooring .sim with RAO vessel). Use python (not uv run). Commit and push when done. Comment on GH issue #1764."
```

### Terminal 2 (Codex) — verification after each prompt completes
```powershell
cd D:\workspace-hub

# After Terminal 1 finishes Prompt 1:
codex -p "git pull origin main. Verify queue/completed/ has new results. Check result.yaml status. List .owr and .xlsx files. Report summary."

# After Terminal 1 finishes Prompt 2-3:
codex -p "git pull origin main. Verify digitalmodel/tests/fixtures/ has .sim and .owr files. Check file sizes. Try loading each with: python -c 'import OrcFxAPI; m=OrcFxAPI.Model(path); print(m.objectCount)' and python -c 'import OrcFxAPI; d=OrcFxAPI.Diffraction(); d.LoadResults(path); print(d.frequencyCount)'. Report."
```

### Terminal 3 (Gemini) — adversarial review
```powershell
cd D:\workspace-hub

# After all prompts complete:
gemini -p "Review all changes made today in this repo. Check: (1) are committed fixture files valid and under size limits, (2) are result.yaml files well-formed, (3) are commit messages linked to correct issues, (4) anything left uncommitted. Provide APPROVE or ISSUES FOUND verdict."
```

## Git contention avoidance

Since all prompts run sequentially in Terminal 1, there is no git contention.
Terminal 2 and 3 only read (git pull) — they do not commit.

File creation map:
- PROMPT 1 writes to: queue/pending/, queue/completed/
- PROMPT 2 writes to: digitalmodel/tests/fixtures/, scripts/solver/
- PROMPT 3 writes to: digitalmodel/tests/fixtures/
- PROMPT 4 writes to: digitalmodel/tests/fixtures/

No overlap between prompts.

## Key differences from Hermes-based execution

| Aspect | Hermes (dev-primary) | Claude Code CLI (licensed-win-1) |
|--------|---------------------|----------------------------------|
| Python command | `uv run python3` | `python` |
| Memory/skills | persistent across sessions | none — pass full context in prompt |
| File editing | patch tool | Claude Code native |
| Issue comments | `gh issue comment` | `gh issue comment` (same) |
| Background tasks | process manager | not available — run foreground |
| Subagents | delegate_task | not available — sequential only |

## Important notes

1. Always `git pull origin main` before starting any prompt
2. Always `git push origin main` after completing each prompt
3. Use `python` not `uv run` (Windows, no uv expected)
4. If OrcFxAPI import fails: `pip install OrcFxAPI`
5. If gh CLI not authenticated: `gh auth login`
6. The prompts file (`docs/plans/licensed-win-1-orcawave-orcaflex-prompts.md`) contains
   full step-by-step instructions that Claude Code can follow directly
7. Each prompt is self-contained — no cross-prompt dependencies beyond file existence

## After licensed-win-1 completes all 4 prompts

On dev-primary, pull and verify:
```bash
cd /mnt/local-analysis/workspace-hub
git pull origin main

# Verify fixtures arrived
ls digitalmodel/tests/fixtures/*.sim
ls digitalmodel/tests/fixtures/*.owr

# Verify queue results
ls queue/completed/

# Then proceed with dev-primary issues #1765, #1766, #1767, #1768
```
