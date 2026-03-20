Stage 19 · Close | task_agent | light | single-thread
Entry: evidence/user-review-close.yaml, evidence/gate-evidence-summary.yaml
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Checklist:
1. Run: uv run --no-project python scripts/work-queue/verify-gate-evidence.py WRK-NNN
2. Confirm exit 0; if non-zero fix gates first
3. Run: bash scripts/work-queue/close-item.sh WRK-NNN
4. Verify done/WRK-NNN.md exists; percent_complete: 100
5. Git commit + push all changes
Git:
- Commit to main + push immediately
- Conventional commits: feat|fix|chore(scope): desc
- Submodules: commit inside first, then update pointer at hub level
Legal:
- Run scripts/legal/legal-sanity-scan.sh if any code was ported from external sources
- Verify no client identifiers in code, comments, or config
Exit: done/WRK-NNN.md + lifecycle HTML Stage 19 done chip
