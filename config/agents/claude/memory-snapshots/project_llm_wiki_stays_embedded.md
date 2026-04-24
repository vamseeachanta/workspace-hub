---
name: llm-wiki stays embedded in workspace-hub (decision closed #2398)
description: Architecture decision 2026-04-23 — llm-wikis remain at `knowledge/wikis/`, no spinout. Explicit re-eval triggers listed. #2398 closed as decided.
type: project
originSessionId: 3415d1dc-e37e-4069-a1eb-a2a3a2c2ca83
---
llm-wikis remain embedded inside `workspace-hub` at `knowledge/wikis/`. No spinout to a standalone repo, no split into platform+content repos. #2398 is CLOSED as decided.

**Why:** Current footprint (63MB, ~19.6k .md, 6 domain wikis) is not at scale where boundary cost exceeds coupling benefit. Tooling coupling is heavy (20+ scripts with hardcoded `knowledge/wikis/` paths) — clean spinout would be a real migration, not a `git mv`. No external-repo consumers yet. Risk of decision drift is bounded by the explicit triggers below.

**How to apply:**
- Do NOT propose spinout/split migrations proactively. Treat the decision as stable unless a trigger fires.
- Re-evaluation triggers (any one fires → open a NEW issue, do not reopen #2398):
  1. Total `knowledge/wikis/` size exceeds 200MB
  2. First external repo needs to consume wikis directly (not via workspace-hub clone)
  3. Release cadence conflict — someone actively waits on workspace-hub release for wiki delivery or vice-versa
  4. Wiki-related CI exceeds 5 minutes on workspace-hub pipeline
  5. Date trigger: 2026-10-23 (6-month soak)
- New re-eval issue title form: `feat(knowledge): llm-wiki spinout re-evaluation triggered by <signal>`.
- Questions like "should we extract the wiki system?" route to: answer "no — decision 2026-04-23, see #2398 comment; these triggers not yet met".
- Per-wiki organization (engineering / marine-engineering / naval-architecture / maritime-law / personal / health-reports) stays as-is.
- Standards routing is a SEPARATE decision — see `project_wiki_standards_path_decision.md` (#2471).
