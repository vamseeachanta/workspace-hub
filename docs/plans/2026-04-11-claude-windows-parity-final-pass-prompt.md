You are working in /mnt/local-analysis/workspace-hub.

Read and follow first:
- AGENTS.md
- CLAUDE.md

You are doing a narrow completion pass for the already-started Windows Claude Code parity hardening for Packages 1–3 only.

Current verified state
Modified files:
- config/agents/claude/settings.json
- .claude/hooks/skill-content-pretooluse.sh
- .claude/hooks/session-governor-check.sh
- .claude/hooks/cross-review-gate.sh
- .claude/settings.json

Unmodified files:
- .claude/hooks/session-logger.sh
- .claude/hooks/session-review.sh

Verified remaining issues
1. Package 3 is incomplete:
   - session-logger pre: False
   - session-logger post: True
   - session-review: True
   So the missing pre hook wiring still needs to be added if appropriate.

2. Remaining grep hits for python3|uv run are still present in:
   - .claude/hooks/session-governor-check.sh
   - .claude/hooks/cross-review-gate.sh
   These appear to be comments, fallback interpreter resolution, or user-facing messages rather than active execution-path issues.

3. config/agents/claude/settings.json may now be broader than necessary for a managed shared template and should be reviewed conservatively.

Your task
Do one final narrow cleanup/completion pass for Packages 1–3 only.

Allowed files to edit
- config/agents/claude/settings.json
- .claude/hooks/skill-content-pretooluse.sh
- .claude/hooks/session-governor-check.sh
- .claude/hooks/cross-review-gate.sh
- .claude/settings.json
- .claude/hooks/session-logger.sh
- .claude/hooks/session-review.sh

Rules
- Do not edit any other files
- Do not create new files
- Do not edit docs
- Do not commit
- Do not widen scope to Packages 4 or 5

Required objectives
1. Complete Package 3
- Determine whether session-logger should be wired on both pre and post.
- If yes, add the missing pre wiring in .claude/settings.json with the minimum safe change.
- Do not over-engineer the hook chain.

2. Resolve or explicitly accept remaining grep hits
- Review the remaining python3|uv run matches.
- If they are benign and should remain, say so explicitly in the output.
- If they should be cleaned for consistency, clean them conservatively.

3. Trim Package 1 if needed
- Re-check config/agents/claude/settings.json against .claude/settings.json
- Keep only repo-safe shared baseline elements in the managed template
- Remove anything that seems too aggressive/global for a managed template, if appropriate

Required verification
Run all of these and report results:
- jq empty config/agents/claude/settings.json
- bash -n .claude/hooks/skill-content-pretooluse.sh
- bash -n .claude/hooks/session-governor-check.sh
- bash -n .claude/hooks/cross-review-gate.sh
- bash -n .claude/hooks/session-logger.sh
- bash -n .claude/hooks/session-review.sh
- grep -nE 'python3|uv run' .claude/hooks/skill-content-pretooluse.sh .claude/hooks/session-governor-check.sh .claude/hooks/cross-review-gate.sh || true
- python3 - <<'PY'
import json, pathlib
cfg=json.loads(pathlib.Path('.claude/settings.json').read_text())
cmds=[]
for blocks in cfg.get('hooks', {}).values():
    for block in blocks:
        for hook in block.get('hooks', []):
            cmds.append(hook.get('command',''))
print('session-logger pre:', any('session-logger.sh pre' in c for c in cmds))
print('session-logger post:', any('session-logger.sh post' in c for c in cmds))
print('session-review:', any('session-review.sh' in c for c in cmds))
PY
- git diff -- config/agents/claude/settings.json .claude/settings.json .claude/hooks/skill-content-pretooluse.sh .claude/hooks/session-governor-check.sh .claude/hooks/cross-review-gate.sh .claude/hooks/session-logger.sh .claude/hooks/session-review.sh
- git status --short -- config/agents/claude/settings.json .claude/settings.json .claude/hooks/skill-content-pretooluse.sh .claude/hooks/session-governor-check.sh .claude/hooks/cross-review-gate.sh .claude/hooks/session-logger.sh .claude/hooks/session-review.sh

Output format
1. What you changed
2. Whether Package 3 is now complete
3. Whether remaining grep hits are benign or were fixed
4. Whether the managed template is now conservative enough
5. Verification results
6. Explicit confirmation that no files outside the allowed set were modified
7. Stop without committing
