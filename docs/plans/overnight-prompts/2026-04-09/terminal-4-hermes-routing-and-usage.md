# Terminal 4 — Hermes Routing + AI Credit Utilization Tooling (Claude)

We are in /mnt/local-analysis/workspace-hub.
Use `uv run` for all Python.
Commit to `main` and push after each completed implementation/fix cycle.
Do not branch.
TDD first where code changes are made. Do NOT ask the user any questions.
Run `git pull origin main` before every push.

IMPORTANT: first inspect current state before coding.
1. Read issue bodies for #1855 and #1856.
2. Inspect existing implementations before modifying anything:
   - scripts/ai/credit-utilization-tracker.py
   - scripts/ai/generate-agent-radar.py
   - config/agents/routing-config.yaml
   - config/agents/provider-capabilities.yaml
   - any Hermes config references mentioned in the issues
3. Narrow to the missing delta only.

Do NOT write to paths owned by other terminals:
- digitalmodel/src/digitalmodel/field_development/
- digitalmodel/tests/field_development/
- digitalmodel/src/digitalmodel/naval_architecture/
- digitalmodel/tests/naval_architecture/
- notes/agent-work-queue.md, scripts/refresh-agent-work-queue.*
- docs/governance/, docs/reports/session-governance/

Only write to:
- scripts/ai/credit-utilization-tracker.py
- scripts/ai/task-dispatcher.py
- scripts/ai/generate-agent-radar.py
- scripts/cron/setup-cron.sh
- config/agents/routing-config.yaml
- config/agents/provider-capabilities.yaml
- config/ai-tools/weekly-utilization.json
- notes/ai-credit-utilization-weekly.md
- tests/ai/ or scripts/ai/tests/ (new targeted tests only)

## TASK 1: Issue #1855

Harden or complete the weekly AI credit utilization tracker.

Minimum deliverables:
1. Ensure the tracker can produce one consistent weekly snapshot artifact.
2. Add/update one targeted test covering the highest-risk parsing/aggregation logic.
3. If stale placeholder data files are still referenced, either replace the pathing logic or clearly remove the dead path dependency.
4. If the weekly markdown report can be generated deterministically, generate/update a sample report artifact.

Required verification:
- targeted pytest for the touched test(s)
- one dry-run invocation of the tracker if safe

Commit message:
`feat(ai): harden weekly credit utilization tracking pipeline (#1855)`

## TASK 2: Issue #1856

Implement the narrowest valuable slice of Hermes task dispatch / quick model routing without undoing current explicit Codex defaults.

Guardrails:
- Preserve the repo's current explicit default model behavior unless the code clearly supports a safe extension.
- Do not silently re-enable routing behavior that would send work to an undesired provider by default.
- Prefer additive tooling (dispatcher script, config mapping, report output) over risky global default changes.

Minimum deliverables:
1. `scripts/ai/task-dispatcher.py` or equivalent small dispatcher utility.
2. Routing/provider config updated only as needed for the dispatcher to reason over Hermes roles.
3. One targeted test for the dispatcher or routing logic.
4. Keep config changes reviewable and minimal.

Required verification:
- targeted pytest for touched test(s)
- one example dispatcher invocation if safe

Commit message:
`feat(ai): add Hermes task dispatcher and routing metadata updates (#1856)`

## IMPLEMENTATION CROSS-REVIEW (mandatory)

This stream is architecture/policy-heavy. Run both Codex and Gemini review if Gemini CLI is available.

After each task commit is pushed:
1. Capture the committed diff:
   - `git show --stat --patch HEAD > /tmp/terminal-4-impl.diff`
2. Write `/tmp/terminal-4-review.md` with:
   - issue context (#1855 or #1856)
   - changed files
   - risks around provider defaults, fallbacks, and stale quota data
   - verification command/result
   - the exact diff
3. Run Codex review:
   - `codex exec "$(cat /tmp/terminal-4-review.md)" | tee /tmp/terminal-4-codex-review.txt`
4. If available, run Gemini review:
   - `gemini exec "$(cat /tmp/terminal-4-review.md)" | tee /tmp/terminal-4-gemini-review.txt`
5. Fix MAJOR/HIGH findings once, commit, push, and rerun the reviewer(s) that found them.
6. Post brief issue comments on #1855 and/or #1856 with implementation summary, verification, and final review verdicts.

If Gemini CLI is unavailable, note that in the issue comment and proceed with Codex review only.
