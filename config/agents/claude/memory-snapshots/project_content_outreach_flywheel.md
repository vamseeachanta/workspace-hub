---
name: project-content-outreach-flywheel
description: LinkedIn feed-scan → content engine → outreach pipeline flywheel; proposed 8-issue set awaiting user answers; key artifact locations
metadata: 
  node_type: memory
  type: project
  originSessionId: 1daf7a74-ab59-41d0-b8b4-cc98fe331289
---

**Content→Outreach flywheel (started 2026-06-04, handoff 2026-06-06).** LinkedIn feed scan produced: marketing playbook `aceengineer-strategy/content/linkedin-feed-scan-2026-06-04.md` (PR #27 MERGED), Case Study #1 draft `content/case-study-drafts/case-study-01-dnv-f105-parametric-freespan.md` (PR #28 — check state; voice-edit + manual post pending), llm-wiki ingest PR #349 MERGED (SOFEC→MODEC consolidation, Fervo limiter-redesign, Prescient RUL → trends-and-strategies + drilling-engineering wikis).

**Proposed 8-issue flywheel set NOT yet published** — full table + 4 open user questions in `aceengineer-strategy/docs/plans/2026-06-06-content-outreach-flywheel-issue-plan.md` (PR #49). Do NOT duplicate existing outreach issues (#25/#30–#36 ace-strategy; deckhand#24/#22/#2 PAT-rotation due 2026-06-08).

**Key link:** Case Study #1 (DNV-RP-F105 free-span, from digitalmodel #632/#663 — see [[project_gtm_parametric_pilot]]) = the SAME ask-domain as EXP-002 demand-validation hypothesis and Open Deck deck #1 (#31, due ~2026-06-11); sequence the post with the Intermoor canary DM (#30, ON HOLD on Doris-demo gate).

**Git hazards learned:** aceengineer-strategy local main = parallel session's unpushed pipeline/EXP-003 commits (NEVER reset it — restored from reflog once after a reset --hard orphaned its Intermoor commit); branch new work from origin/main; direct push to its main is classifier-denied → PR route. digitalmodel local clone dirty/behind → read merged facts via `git show origin/main:<path>`.
