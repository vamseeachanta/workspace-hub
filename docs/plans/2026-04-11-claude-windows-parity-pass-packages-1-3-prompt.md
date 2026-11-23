```bash
cd /mnt/local-analysis/workspace-hub

PROMPT=$(cat <<'EOF'
You are working in /mnt/local-analysis/workspace-hub.

Read and follow first:
- AGENTS.md
- CLAUDE.md

You are doing a narrow follow-up pass on the already-started Windows Claude Code parity hardening for Packages 1–3 only.

Current observed state
- Modified files:
  - config/agents/claude/settings.json
  - .claude/hooks/skill-content-pretooluse.sh
  - .claude/hooks/session-governor-check.sh
  - .claude/hooks/cross-review-gate.sh
  - .claude/settings.json
- Unmodified files:
  - .claude/hooks/session-logger.sh
  - .claude/hooks/session-review.sh

Known issues from review
1. Package 3 appears incomplete:
   - .claude/settings.json wires session-logger.sh post
   - .claude/settings.json wires session-review.sh on Stop
   - but session-logger.sh pre does not appear to be wired
2. Package 2 still has grep hits for python3|uv run in comments or user-facing messages
3. Package 1 may be broader than necessary and should be checked for conservative/shared-template safety

Your task
Do a narrow completion and cleanup pass for Packages 1–3 only.

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

Specific goals
1. Finish Package 3 properly
- Verify whether session-logger.sh should be wired on both pre and post.
- If yes, add the missing pre wiring in .claude/settings.json using the minimum safe change.
- Keep session-review.sh wiring conservative and valid.

2. Tighten Package 2
- Review remaining python3|uv run references in:
  - .claude/hooks/session-governor-check.sh
  - .claude/hooks/cross-review-gate.sh
- If the remaining hits are only comments/messages and are acceptable, say so explicitly.
- If they should be updated for consistency, update them conservatively.

3. Review Package 1 conservatively
- Re-check config/agents/claude/settings.json against .claude/settings.json
- Ensure the managed template contains only repo-safe shared baseline elements
- If anything is too aggressive/global for a managed template, trim it back conservatively

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
EOF
)

claude -p --permission-mode plan --no-session-persistence --output-format text "$PROMPT" </dev/null | tee /tmp/claude-windows-parity-pass.log
```