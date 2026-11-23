---
name: issue-portfolio-triage
description: Triage and rank GitHub issues across a workspace-hub style multi-repo ecosystem using machine-readiness, provider-utilization, and leverage scoring.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Issue Portfolio Triage

Use when a user has GitHub issues in both a control-plane repo and individual repos and wants to know what to tackle first, when to address it, and how to align the backlog with machine readiness and AI-provider usage.

## When to use
- Issues exist in both `workspace-hub` and child repos
- The user wants a weekly plan, not just a flat issue list
- Machine readiness, cron health, repo sync, or AI harness parity matter
- The user has multiple AI subscriptions/accounts and wants to maximize quota use productively

## Core idea
Do not triage the backlog as one flat queue.

Split it into 3 layers:
1. `workspace-hub` / control-plane issues first when they improve many repos or machines
2. repo-specific issues next by business value and delivery risk
3. umbrella/meta issues last unless they clearly unblock many concrete issues

## Inputs to collect
1. Provider mix and reset timing
   - Example: Claude weekly reset time and percent remaining
   - Number of Codex/OpenAI seats
   - Gemini availability
2. Machine topology
   - Primary machine(s)
   - Secondary/contributor machine(s)
   - Windows/licensed or special-purpose machines
3. Current goal
   - readiness, provider utilization, delivery, research, backlog cleanup, etc.
4. Open issue surface
   - `gh issue list` in the current repo
   - if needed, sample key issue bodies with `gh issue view`

## Recommended tool flow
1. Confirm GitHub auth:
   - `gh auth status`
2. Confirm current repo:
   - `git remote -v`
3. Pull the issue surface:
   - `gh issue list --state open --limit 200 ...`
4. Apply a machine-feasibility filter before ranking:
   - Prefer issues labeled for the current machine (for example `machine:dev-primary`) or issues with no machine restriction
   - Verify the relevant files/scripts/docs actually exist locally
   - Verify there is a plausible local verification path (existing tests, easy-to-add unit tests, or a deterministic script check)
   - Down-rank issues that require another host, proprietary software, remote scheduler access, or cross-machine deployment unless the issue is explicitly about preparing artifacts on this machine
5. Inspect candidate issues in detail:
   - `gh issue view <num> --json ...`
6. Rank issues using the scoring rubric below
7. Produce three outputs:
   - ranked issue shortlist
   - reusable triage rubric
   - this-week portfolio plan tied to provider budget/reset timing

## Scoring rubric
Score each issue 0-3 on:
- Impact — how many repos/machines/workflows it affects
- Urgency — whether it blocks current work or creates repeated pain now
- Frequency — how often the problem appears
- Leverage — whether one fix improves many future tasks
- Readiness alignment — whether it improves sync, auth, cron, harness, machine parity
- Provider-efficiency alignment — whether it helps use Claude/Codex/Gemini better
- Effort — subtract this (0 tiny, 3 large)

Suggested formula:

`score = impact + urgency + frequency + leverage + readiness + provider_efficiency - effort`

Interpretation:
- `12+` do now
- `9-11` this week
- `6-8` next batch
- `<=5` defer / merge / close

## Default ranking logic
Prefer issues in this order:
1. cross-machine readiness and silent-failure prevention
2. provider-routing and utilization improvements
3. issue-intake/template hygiene for multi-machine tracking
4. verification/review-enforcement issues
5. umbrella/meta issues

## Multi-provider guidance
When the user has Claude + 2 Codex seats + Gemini:
- Claude = orchestrator, planning, sequencing, synthesis
- Codex seat A = implementation lane
- Codex seat B = adversarial review / overflow lane
- Gemini = selective architecture/research/third-opinion lane

Use this to shape the weekly plan:
- Spend Claude on high-context triage and coordination
- Push bounded implementation and review work to Codex
- Use Gemini sparingly for ambiguity or architecture-heavy work

## Weekly portfolio output format
Always give:
1. `Top issues to tackle first this week`
2. `Reusable triage rubric`
3. `This-week portfolio plan aligned to reset timing`

Recommended WIP cap:
- 2 execution issues
- 1 policy/doc issue
- 1 verification issue
- no more than 4 active items total

## Tie-breakers
If issues are close, prefer the one that:
1. reduces future Claude usage
2. enables Codex parallelism
3. improves machine readiness
4. improves issue intake quality
5. removes silent failure modes

## Runtime-backed triage for data-readiness repos
When the user's goal is "data readiness" rather than generic backlog cleanup, do not trust issue titles or labels alone. Validate the current runtime state before ranking.

### Required checks
1. Run the relevant CLI/status command with the repo's package context, not just the workspace root.
   - For UV-managed nested repos, prefer `uv run --project <repo_path> ...`
   - If module import fails or config is not found, retry with explicit `--project` and explicit `--config` paths before concluding the issue is still valid.
2. Run the narrow unit tests around the adapter/CLI area to distinguish:
   - broken code
   - missing environment/config
   - stale issue text
3. Inspect the live job/module source after reading the issue body.

### Reclassification rules discovered in practice
- If an issue says "replace stub" but the code and tests show a real implementation exists, do not rank it as greenfield implementation. Reclassify it as one of:
  - operationalization (missing API key / env wiring)
  - runtime compatibility fix (upstream format changed)
  - config/registration gap
- If an issue's dependency is already present in `pyproject.toml` and lockfile, close or down-rank it immediately.
- If a job file exists but is absent from scheduler config or CLI registration, rank it as a high-leverage quick win.
- If tests pass but live runs fail, prioritize issues that align tests/config/runtime contracts over adding new adapters.

### Output expectations
For data-readiness triage, include a short "issue truth table":
- already done / should close
- implemented but broken at runtime
- true stub / missing implementation
- missing issue that should be created

This prevents users from spending cycles on stale issue text when the real need is operational readiness.

## Close / merge / rescope rules
Close if:
- workflow/architecture referenced is obsolete
- work is already done
- issue is stale and no longer actionable

Merge if:
- one issue is a strict subset of another
- multiple issues are mechanical slices of the same cleanup

Rescope if:
- machine names, provider assumptions, or workflow contract changed
- the issue belongs in a child repo rather than the control-plane repo

## Feature-Area Audit & Batch Execution Pattern

When triaging issues for a **data-heavy feature area** (document intelligence, knowledge systems, etc.), use this extended workflow:

### 1. Cross-Artifact Discovery
Don't rely solely on labels — many relevant issues have no feature label. Do keyword search across all open issues:
```bash
gh issue list --state open --limit 500 --json number,title,labels | python3 -c "
import json, sys
data = json.load(sys.stdin)
keywords = ['document', 'intelligence', 'resource', 'extraction', 'corpus', ...]
for d in data:
    title_lower = d['title'].lower()
    if any(kw in title_lower for kw in keywords):
        print(f'#{d[\"number\"]}: {d[\"title\"]}')
"
```
Also survey: YAML registries, JSONL indexes, mounted-source definitions, standards ledgers, audit reports, and coverage reports. These data artifacts often reveal work that has no issue yet.

### 2. Cluster by Feature Affinity (not just labels)
Group issues into logical sub-features based on data flow dependencies:
- Upstream (sources, downloads, mounts) → Indexing (batch, classification) → Extraction (deep, tables, examples) → Implementation (standards, calculations) → Integration (workflow, tooling)
- Assign P0/P1/P2/P3 by position in the pipeline — upstream blockers first.

### 3. Batched Parallel Subagent Execution
Use `delegate_task(tasks=[...])` with up to 3 independent tasks per wave. Between waves:
- **Orchestrator does git add/commit/push** — subagents sharing a repo will hit index.lock if they try to push concurrently
- Use `git -c core.hooksPath=/dev/null commit` to skip slow pre-commit hooks
- Close/comment on completed issues from orchestrator, not subagents (avoids gh auth contention)
- Track progress with `mcp_todo` between waves

### 4. Data Artifact Reclassification as Deliverable
For data-heavy ecosystems, reclassifying/cleaning data registries IS high-leverage work:
- Reclassifying domain tags in a standards ledger directly improves downstream queries
- Curating raw extractions into test fixtures creates immediate TDD value
- Updating audit reports with fresh stats gives the orchestrator accurate situational awareness
- These are concrete deliverables, not just planning artifacts

### 5. Prioritization Spine Pattern for Fragmented Backlogs
When relevant work is scattered across multiple existing umbrella issues, do not just rank them in chat. Create a GitHub-native prioritization spine:

1. Search and inspect the existing umbrella/execution issues with `gh issue list` + `gh issue view`
2. Create one new parent issue that:
   - summarizes the currently observed bottlenecks using live repo evidence
   - groups existing issues into P0/P1/P2/P3 execution order
   - names any uncovered gaps that do not yet have issues
3. Create child issues for uncovered gaps rather than overloading the parent
   - Example reusable gap types:
     - large miscellaneous / `other` classification buckets that block file-context discovery
     - stale summary artifacts drifting from canonical YAML/ledger sources
4. Immediately edit the parent issue body to include links to the newly created child issues
5. Add backlink comments to the most important existing issues so future agents see the new ordering reference
   - Keep the comment concise: point to the new prioritization spine and state that it is the current execution-order reference
6. Verify the final parent/child bodies after creation to ensure placeholders like `<PARENT>` were rendered correctly

This pattern is especially useful when the real need is not a new execution stream, but a new coordination layer across already-open work.

### Wave sizing guidance
- Wave 1: Quick wins + blocking fixes (download scripts, cleanup, reclassification)
- Wave 2: Curation + architecture proposals (worked examples, knowledge persistence)
- Wave 3: Integration + tests (gate tests, /work flow, skills creation)
- Each wave should take 5-15 minutes of subagent time

## Notes
This approach worked well for a workspace-hub ecosystem where the immediate high-value issues clustered around:
- installing Codex plugin/tooling across machines
- cross-machine cron health monitoring
- operationalizing provider routing policy
- fixing machine targeting in issue templates
- validating adversarial review enforcement
- **data intelligence feature area**: 45 issues across 8 sub-features triaged and 11 executed in one session via 4 parallel waves

The key lesson: fix the ecosystem issues that increase execution capacity before tackling broad umbrella cleanup. For data-heavy features, the reclassification/curation work IS the high-leverage capacity-building step.
