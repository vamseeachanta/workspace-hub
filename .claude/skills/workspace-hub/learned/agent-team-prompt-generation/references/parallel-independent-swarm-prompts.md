# Parallel Independent Swarm Prompt Pattern

Use when the orchestrator needs to submit 3-5+ independent AI swarms against the same repo ecosystem and wants comparable, mergeable outputs without live coordination between workers.

## Prompt shape

Each swarm prompt should be self-contained and include:

1. **Lane identity** — swarm number, audit/workstream title, and exact output path.
2. **Repo ecosystem scope** — exact workspace path and repos in scope.
3. **Independence contract** — no coordination with other swarms; read-only unless explicitly allowed; do not modify shared state except the assigned artifact/log.
4. **Grounding checklist** — exact files/commands to inspect first, with live-state checks before conclusions.
5. **Output schema** — same headings across all swarms so the orchestrator can compare results.
6. **Evidence rules** — cite repo paths, GitHub issue URLs, command outputs, or docs; avoid ungrounded recommendations.
7. **Priority lens** — a distinct question for each swarm, not five variants of the same generic audit.
8. **Stop conditions** — bounded time/scope and when to report blockers rather than drift.

## `/goal` reverse-prompt mode

When the user asks for "reverse prompts" or prompts "we can submit" to independent `/goal` swarms, treat the deliverable as prompt text, not execution. Produce five copy-paste-ready blocks (or files if requested) with:

- a short `/goal` title line or objective line suitable for the target agent interface;
- exact repo ecosystem scope and current working directory;
- lane-specific mission, read-only/write boundaries, and output path;
- shared evidence/output schema so results are comparable;
- explicit instruction not to coordinate with other swarms and not to close issues/push unless separately authorized.

Do not dispatch, background, close, label, commit, or push from reverse-prompt mode unless the user adds explicit execution language such as "launch", "run", "submit now", or "dispatch".

## Five-lane audit decomposition

A useful 5-swarm split for workspace-hub ecosystem governance/audit work:

- **Swarm 1 — live-state gate audit:** verify current issue labels, plan states, dirty repos, and closeout gates against policy.
- **Swarm 2 — capability gap map:** identify missing repo/domain capabilities and convert them into issue-ready gaps.
- **Swarm 3 — plan-review drift:** find stale approvals, stale review artifacts, or issues whose GitHub state no longer matches the plan artifact.
- **Swarm 4 — execution-readiness partition:** separate approved/executable work from planning-needed/governance-blocked work.
- **Swarm 5 — learning transfer:** identify reusable lessons and where they belong in skills, docs, or issue templates.

## Launcher/logging pattern

When actually dispatching the swarms, create a deterministic run directory:

```text
docs/plans/agent-swarm-audits/YYYY-MM-DD/
  prompts/swarm-1-<slug>.md
  logs/swarm-1-<provider>.jsonl
  logs/<provider>-swarm-pids.txt
  swarm-1-<slug>.md
```

Capture PID, provider, prompt path, log path, and expected artifact path. After launch, verify each log advances past startup (for example `turn.started`) before reporting success. Report artifacts as pending until files exist.

## Pitfalls

- Do not make the five prompts mutually dependent; independent workers should not wait for one another.
- Do not ask workers to close issues or push branches unless the lane explicitly owns transactional closeout.
- Do not report a swarm as complete just because the process launched; distinguish `RUNNING`, `EXITED`, and artifact-created states.
- Do not let broad audit prompts write into arbitrary repo paths; assign one artifact per swarm.
