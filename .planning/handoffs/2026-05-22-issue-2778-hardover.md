# Fresh Session Hardover — Issue #2778

Use this as the fresh-session handover prompt:

```markdown
You are Hermes Agent operating in `/mnt/local-analysis/workspace-hub`.

## Mission

Continue from the completed #2775 sibling SSoT landing work. The user asked for the next logical step after #2775, and the recommended next step is to prepare/drive the follow-up plan for GitHub issue #2778:

> #2778 feat(architecture): lock data/knowledge/result search routing across llm-wiki + llm-wiki-<client> siblings

Do **not** implement #2778 yet. It is `status:needs-plan`, so follow the workspace-hub hard gate: Issue → Resource Intel → Plan → Adversarial Review → `status:plan-review` → USER APPROVES → `status:plan-approved` → Implement TDD.

## Required skills / governing workflow

Load and follow:
- `coordination/issue-planning-mode`
- `development/planning/writing-plans` if drafting the plan
- `coordination/gh-work-planning` or equivalent GitHub planning workflow if available/relevant
- Any workspace-hub SSoT / Hermes ecosystem skill relevant to sibling memory/skills/tools contracts, especially:
  - `devops/hermes-ecosystem-integration`
  - `coordination/memory-bridge-operation` or related memory canonicalization skills if applicable
  - `workspace-hub/repo-structure` if touching sibling AGENTS/contracts
  - `research/llm-wiki-*` skills if planning llm-wiki routing/search behavior

If a skill name is ambiguous between `~/.hermes/skills` and repo `.claude/skills`, prefer the repo-tracked workspace-hub skill as canonical and inspect it directly if the skill tool refuses to resolve.

## Current verified state from prior session

#2775 is complete and closed.

Evidence:
- Issue #2775 closed with `status:done`
- Closeout comment: https://github.com/vamseeachanta/workspace-hub/issues/2775#issuecomment-4521901000
- Implementation pushed to `main`
  - Main commit: `326ada4cd`
  - Follow-up skill-learning commits: `906519b6c`, `3b084f75d`
  - Remote `main` was verified at `3b084f75d`
- Issue worktree `/mnt/local-analysis/agent-worktrees/workspace-hub-issue-2775-landing` was clean.
- Targeted tests passed:
  - `uv run pytest tests/readiness/test_sibling_agents_contract.py tests/readiness/test_sibling_sso_repair_dry_run.py tests/readiness/test_sync_agent_configs_pyyaml_fallback.py -q`
  - Result: `30 passed`
- SSoT checker after #2775:
  - `memory=pass`
  - `skills=pass`
  - `registry=pass`
  - `harness_contracts=fail` only for known residual sibling blockers:
    - `llm-wiki`: `missing_agents`
    - `llm-wiki-acma`: `missing_agents`
    - `aceengineer-strategy`: `missing_agents`
    - `kaggle-rogii-2026`: `missing_agents`
    - `CAD-DEVELOPMENTS`: `missing_workspace_hub_contract`
- Implementation adversarial review:
  - Codex r2: `APPROVE`
  - Gemini r2: `APPROVE`
  - No CRITICAL/HIGH/MEDIUM findings remained.
- Review artifacts were committed under:
  - `scripts/review/results/2026-05-22-implementation-2775-*.md`

## Important workspace warning

The main checkout `/mnt/local-analysis/workspace-hub` was dirty/diverged after #2775 closeout:

```text
## main...origin/main [ahead 2, behind 5]
```

Observed dirty/untracked state included unrelated runtime/session/provider artifacts, for example:
- `.claude/skills/software-development/gh-work-execution/SKILL.md`
- `.claude/state/session-signals/2026-05-22.jsonl`
- provider quota/kanban/report files under `config/ai-tools/` and `docs/reports/`
- `logs/orchestrator/hermes/skill-patches.jsonl`
- untracked review/log/report artifacts

Do **not** blindly commit or clean this state. First inspect and classify. Prefer creating a clean issue worktree for #2778 rather than working directly in the dirty main checkout.

## Recommended next action

1. Inspect live issue #2778:
   ```bash
   gh issue view 2778 --json number,title,state,labels,body,url,comments
   ```

2. Inspect current repo state:
   ```bash
   git status --short --branch
   git log --oneline --decorate -10
   git fetch origin
   git status --short --branch
   ```

3. Create or select a clean planning worktree for #2778. Preferred location pattern:
   ```bash
   /mnt/local-analysis/agent-worktrees/workspace-hub-issue-2778-llm-wiki-routing
   ```

4. Perform resource intelligence before drafting:
   - Read `docs/plans/README.md`
   - Read `docs/plans/_template-issue-plan.md`
   - Search existing plans/issues/docs for:
     - `llm-wiki`
     - `llm-wiki-acma`
     - `sibling SSoT`
     - `memory`
     - `skills`
     - `tools`
     - `AGENTS.md`
     - `workspace-hub contract`
     - `search routing`
     - `data/knowledge/result routing`
   - Inspect the #2775 plan/review/implementation artifacts if present.
   - Inspect SSoT checker scripts/tests from #2775:
     - `tests/readiness/test_sibling_agents_contract.py`
     - `tests/readiness/test_sibling_sso_repair_dry_run.py`
     - `tests/readiness/test_sync_agent_configs_pyyaml_fallback.py`
     - any sibling SSoT checker script added for #2775.

5. Draft the plan only after resource intelligence:
   - Plan path likely:
     ```text
     docs/plans/2026-05-22-issue-2778-llm-wiki-routing-sibling-sso.md
     ```
   - Add/update index row in:
     ```text
     docs/plans/README.md
     ```
   - Keep status `draft` until adversarial review artifacts exist.

6. The plan should explicitly address whether the #2775 residual blockers are:
   - in-scope for #2778,
   - prerequisites,
   - or separate child issues.

Known residual blocker list to classify:
- `llm-wiki`: missing `AGENTS.md`
- `llm-wiki-acma`: missing `AGENTS.md`
- `aceengineer-strategy`: missing `AGENTS.md`
- `kaggle-rogii-2026`: missing `AGENTS.md`
- `CAD-DEVELOPMENTS`: missing workspace-hub contract

## Planning requirements for #2778

The plan should likely define:
- SSoT routing contract for memory/skills/tools across sibling repos.
- How `workspace-hub` remains canonical control plane while sibling repos consume its memory/skills/tools/contracts.
- How public `llm-wiki` and private `llm-wiki-<client>` repos route:
  - data search,
  - knowledge search,
  - result/report search,
  - source/public-private boundaries,
  - redaction/leakage gates.
- How sibling `AGENTS.md` files should point to workspace-hub SSoT without duplicating canonical content.
- Acceptance tests/checkers for sibling accessibility.
- Fail-closed behavior when a sibling lacks `AGENTS.md` or workspace-hub contract.
- Explicit public/private leakage protections.
- A TDD test list before any implementation.

## Governance constraints

- Do not self-apply `status:plan-approved`.
- Do not implement while #2778 is `status:needs-plan`.
- Plan must go through adversarial review before `status:plan-review`.
- Use `uv run`, never bare `python3`, for repo Python commands.
- If implementation eventually happens, tests must be written before implementation.
- Preserve traceability with exact commands, file paths, issue links, and review artifact paths.

## User preference / operating style

The user wants:
- zero-waste AI spend,
- throughput-first execution,
- concise but evidence-grounded status,
- repo-tracked canonical artifacts instead of local-only summaries,
- explicit separation of known state, blocker, and recommended next action,
- no vague future promises — use tools and verify before claiming.

## Suggested first response in new session

Do not give a generic summary. Start by verifying live state with tools, then say something like:

> I’ll start #2778 planning from a clean worktree and first verify live issue/repo state so we do not mix into the dirty/diverged main checkout.

Then immediately run the relevant `gh`/`git` inspections.
```
