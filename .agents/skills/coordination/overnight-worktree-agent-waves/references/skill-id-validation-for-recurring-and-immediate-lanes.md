# Skill ID Validation for Recurring and Immediate Lanes

## Trigger
Use when launching continuous/nightly Hermes lanes with both cron jobs and immediate background `hermes chat` sessions.

## Failure observed
A lane can fail immediately with:

```text
Error: Unknown skill(s): development/test-driven-development
```

If the same invalid skill was also baked into a recurring cron job, future scheduled runs will repeat the failure even if the current manual lane is relaunched correctly.

## Recovery pattern
1. Poll all immediate sessions by captured session ID; do not rely only on `process list`.
2. Inspect failed lane output/log for `Unknown skill(s)`.
3. Resolve the valid class-level skill name with `skills_list`/`skill_view`.
4. Update the recurring cron job skill list as well as the immediate relaunch command.
5. Relaunch only the failed lane with the corrected skill list and absolute prompt/log paths.
6. Re-poll the new session ID and record PID/log path in the handoff.

## Known mapping
- Use `software-development/test-driven-development` rather than `development/test-driven-development` for Hermes skill loading in this workspace.
