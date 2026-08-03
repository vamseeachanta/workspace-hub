# Windows junction restore safety — agent rule (#3571)

**When to apply:** any restore, checkout, or deletion touching `.codex/skills`, `.gemini/skills`, `.claude/skills`, or any shared-skill link path in a D:\ws-style Windows checkout — including running a remediation command that a runbook, preflight, or reconcile output hands you.

**Why:** live incident 2026-07-16 (ace-win-1). The skills-link tooling materializes shared-skill paths as **NTFS junctions targeting `workspace-hub/.claude/skills`**. A `git restore .codex/skills .gemini/skills` executed per a preflight instruction replaced such a junction — git's child-enumerating directory removal **followed the reparse point and emptied the canonical tree** (4,215 tracked files deleted; four scheduled-task failures downstream). Recovery was lossless only because the deletions were unstaged.

**How to apply:**

1. **Probe before touching.** PowerShell: `(Get-Item $path -Force).LinkType` — if it says `Junction` (or `SymbolicLink`), the path's *children belong to the link target*, not to this repo. Bash: `source scripts/lib/reparse_guard.sh; is_reparse_point "$path"`.
2. **Junction → hands off.** Do NOT `git restore`, `git checkout --`, `rm -rf`, or `Remove-Item -Recurse` it. If the link must go, remove the **node only** (`rmdir` on the junction — never touches target contents), or leave it to the link tooling (`resync-skill-links.sh` / `propagate-ecosystem.sh`, which route recursive deletes through `scripts/lib/reparse_guard.sh:guarded_rm_rf`, fail-closed).
3. **` D .codex/skills` / ` D .gemini/skills` status residue is intentional** tooling state on link-managed boxes — not damage to "fix".
4. **If the canonical tree does get wiped:** deletions are typically unstaged with the index intact — `git restore -- .claude/skills` recovers losslessly; then re-sync and re-run the curation task to green.

**Do NOT apply when:** the path probes as a plain directory or a flattened symlink-text *file* (`LinkType` empty) — those are the ordinary core.symlinks=false artifacts and the documented rm+checkout repair is fine.

**Enforcement gradient** (per [`patterns.md`](patterns.md)): Level 2 already — `scripts/lib/reparse_guard.sh` guards the tooling's recursive deletes (tests: `tests/skills/test_reparse_guard.py`); this rule covers the human/agent-driven raw-git surface the script cannot intercept.

**Related:** [#3571](https://github.com/vamseeachanta/workspace-hub/issues/3571) (incident + fixes), [`coding-style.md`](coding-style.md) (edit safety). Memory: `project-junction-skills-link-restore-hazard`.
