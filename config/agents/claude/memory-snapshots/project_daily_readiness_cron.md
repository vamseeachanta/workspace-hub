---
name: Daily readiness cron
description: Scheduled remote agent that runs daily at 6am America/Chicago to check repo readiness (GSD drift, hygiene, PRs, planning, deps) and post to a rolling GitHub issue labeled repo-readiness
type: project
originSessionId: 57335aaf-c168-418e-9e12-dafe06cf553a
---
Trigger `daily-repo-readiness` (id `trig_019GWtRosbZ9rw1HxrGpsvy9`) runs at 6am America/Chicago daily (cron `0 11 * * *` UTC) against https://github.com/vamseeachanta/workspace-hub. Posts a markdown report as a comment on the single rolling GitHub issue tagged `repo-readiness`, creating the issue + label on first run.

Checks: (1) GSD drift via `npm view get-shit-done-cc version` vs `.claude/get-shit-done/VERSION`, (2) repo hygiene on main, (3) open PRs >7d / drafts >14d, (4) issue backlog by label, (5) `.planning/` phase-status drift, (6) `npm outdated` and Python deps. Read-only; only mutation is the tracking-issue comment.

**Why:** User asked for `/gsd:update` and related readiness commands to run automatically as a daily cron rather than manually each morning. Remote (cloud) execution was chosen over local cron so it runs independent of whether the dev machine is on.

**How to apply:** Before proposing new cron/automation work for this repo, check if this existing trigger already covers it — extend this prompt rather than creating parallel triggers. For scope changes, update via `RemoteTrigger action:update trigger_id:trig_019GWtRosbZ9rw1HxrGpsvy9`. Manage UI at https://claude.ai/code/scheduled/trig_019GWtRosbZ9rw1HxrGpsvy9. Delete via https://claude.ai/code/scheduled (API does not support delete).
