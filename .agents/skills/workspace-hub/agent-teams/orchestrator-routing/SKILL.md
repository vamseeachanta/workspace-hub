---
name: orchestrator-routing
description: Route scoped tasks to accountable agents using existing workflow context, machine/model readiness, durable checkpoints and verified integration.
version: 1.1.0
category: workspace-hub
author: workspace-hub
type: skill
last_updated: 2026-10-06
wrk_ref: WRK-212
related_skills:
- agent-teams
- improve
tags:
- orchestration
- routing
- agent-teams
- responsiveness
- delegation
platforms:
- all
capabilities: []
requires: []
see_also: []
---

# Orchestrator Routing

Keep the main session responsive while carrying the authorized task through verified closure. Delegate when it improves execution; a launch or worker summary is not completion. Use the runtime's available agent/session tools rather than assuming a provider-specific API.

## Retrieve before dispatch

1. Identify the owning repository, intended outcome, acceptance evidence and current authority. Search its instructions, skill catalog, issues/PRs, plans, handoffs and relevant history for the existing task or nearest completed workflow before opening another lane. Verify whether prior work is merged, running, blocked or superseded; reuse/resume it rather than duplicating it.
2. Retrieve a bounded source packet: authoritative workflow and template, qualified inputs, relevant implementation/tests, last accepted result, latest decision and checkpoint. Record source repo/path or permitted link, revision and as-of time. Historical examples guide mechanics; their dates, hosts, approvals and results are not current evidence. Inaccessible private sources stay with their owner; do not copy cross-client context into common skills or external research prompts.
3. Follow source links and the established retrieval/index route before asking the user to teach a workflow or supply a path. Distinguish absent, inaccessible and undiscovered context. Resolve technical gaps proactively within scope using existing code, tests and current primary documentation; distinguish researched inference from accepted project inputs. Ask only when a remaining gap changes scope, correctness, authority or a consequential choice. For FEA/report work, read [engineering context](references/engineering-context.md).

## One accountable owner and an appropriate lane

Give each scoped task one accountable owner for acceptance, integration and closure; name separate worker/reviewer responsibilities and dependencies. Reuse the existing issue/plan/handoff record rather than building a second queue. A worker may report results but cannot silently assume another owner's authority.

Classify execution using `docs/standards/PARALLEL_FIRST_EXECUTION.md`: single lane, parallel read-only, or disjoint worktrees. Before write dispatch verify the established claim backend/root, current scope, owned/read-only/forbidden paths and isolated branch/worktree. Serialize integration and git operations; preserve other sessions' work. Respect actual runtime and repository concurrency limits.

Prefer the primary/secondary Linux roles for sustained generic work; preserve the daily-use Windows workstation for interactive work and use the licensed Windows role when the application requires it. Resolve real machine bindings through the authorized inventory; do not infer SSH aliases, drives, mounts or license availability from old prompts. Read `config/workstations/registry.yaml`, the applicable current readiness evidence and `config/ai-tools/provider-routing-policy.yaml` before choosing machine/provider/model. Capability, tenancy, resource/load, data residency, license and security constraints outrank the preference. Select an available model suited to bounded implementation, context synthesis or independent review; no new installation, login or permission changes are implied. Use an established licensed dispatch route when required, not a generic remote launch.

The lane packet carries: task/owner, scope and acceptance, authorization limits, source packet, machine/model and readiness basis, paths, checks, deliverable location and return/checkpoint location. Read only relevant references. A new user message steers the active task unless it cancels/replaces it; update its existing owner/packet rather than automatically launching duplicate work.

## Checkpoint, recover and verify

Use the repository's existing handoff/checkpoint convention. At a meaningful phase boundary, before interruption/transfer, or when a long-running phase cannot finish in the current session, durably record task/owner, branch/base/HEAD, relevant source revisions, last verified outcome, current process/session/job IDs and logs, artifact paths, failed attempts, claims, blockers and the next bounded action. Checkpoint sooner when interruption would lose unique work; avoid a second ledger or empty progress churn.

On resume, read the checkpoint, recheck authorization/source/branch/claim freshness and inspect the recorded process and artifacts before restarting. A live process, queued job or prepared model is running/prepared; missing output is unverified. Recover the existing attempt where possible. Bound retries to the known failure and preserve partial/unique output; changed scope or unavailable prerequisites stop only the affected action. Use [agent CLI operations](../../../autonomous-ai-agents/agent-cli-delegation-operations/SKILL.md) for runtime recovery.

Verify worker outputs directly in the owning checkout against acceptance, not just its final message. Follow applicable TDD and `docs/standards/AI_REVIEW_ROUTING_POLICY.md`; resolve material findings. Commit, publish, merge and close only under matching established authority and passing applicable checks; a plan label, handoff, elapsed time or review verdict grants no permission. Recheck current head/base and preserve human review where required. Report exact tested, reviewed, committed, pushed, merged and operationally verified states separately.

Use [next-wave handoff](../../../coordination/next-wave-handoff-bundle/SKILL.md) for zero-loss closure: verify durable retention and final repo state, release only owned claims, and record the remaining action/owner. Save reusable sanitized learning in the existing owning wiki/skill/workflow and link it from the existing task/index; verify its saved revision and discoverable link. Private project facts stay in their private owner. Do not create a competing framework or close a task while its promised acceptance or knowledge retention remains unverified.

## Narrow human decision queue

Keep genuinely unresolved decisions in the existing task record: specific choice, evidence/options, recommended way forward, impact of waiting, accountable decision owner and needed-by basis (unknown when not established). Examples are conflicting qualified inputs, missing action authority or a material engineering acceptance change. Failed discovery alone is not a reason to ask the user for routine paths. Continue independent authorized work; never invent an owner, commitment or approval to shrink the queue. Stakeholder updates state the last verified outcome, remaining gap and next action concisely.
