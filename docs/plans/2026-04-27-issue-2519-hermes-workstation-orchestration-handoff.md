# Issue #2519 Handoff — Hermes Workstation + Provider Orchestration

Date: 2026-04-27
Primary issue: #2519 — https://github.com/vamseeachanta/workspace-hub/issues/2519
Blocker issue: #2520 — https://github.com/vamseeachanta/workspace-hub/issues/2520

## Purpose

Prepare a clean handoff to a parallel Hermes terminal/session whose next task is to generate continuous and parallel work prompts for both priority workstations:

1. `ace-linux-1` — primary Hermes control plane and GitHub mutation authority.
2. `ace-linux-2` — first overflow / execution worker, especially for Codex-heavy bounded work while Codex credit is expiring.

The user wants this flow reviewed and matured so Hermes orchestrates:

- AI provider/model usage,
- provider-credit burn-down priorities,
- work assignment among all reachable workstations,
- GitHub issue gating and traceability,
- continuous / parallel work prompts for both machines.

## Current user priorities

1. Workstation priority:
   - First: `ace-linux-1`
   - Second: `ace-linux-2`
   - Both are expected to be reachable over VPN / LAN.

2. Provider priority:
   - First: OpenAI Codex because user reports Codex credit expires in roughly 24 hours with about 50% usage remaining.
   - Default provider/model: `openai-codex / gpt-5.5`.
   - Gemini/Copilot are explicit-use only; do not use them as silent fallback/default.

3. Governance priority:
   - Do not dispatch implementation except for issues that are truly `status:plan-approved` and locally gate-ready.
   - Planning, audit, review, prompt generation, and readiness checks are safe before plan approval.
   - Continue using adversarial review by default.

## Current issue state

### #2519 — orchestration feature

Created issue:

- https://github.com/vamseeachanta/workspace-hub/issues/2519
- Title: `feat(hermes): orchestrate AI provider usage and workstation dispatch`

Relevant comments already posted:

- Planning intake: https://github.com/vamseeachanta/workspace-hub/issues/2519#issuecomment-4328722316
- `ace-linux-1` control-plane objective: https://github.com/vamseeachanta/workspace-hub/issues/2519#issuecomment-4328726084
- `ace-linux-2` readiness probe: https://github.com/vamseeachanta/workspace-hub/issues/2519#issuecomment-4329088875
- Readiness report committed: https://github.com/vamseeachanta/workspace-hub/issues/2519#issuecomment-4329099298
- Hermes/Codex correction: https://github.com/vamseeachanta/workspace-hub/issues/2519#issuecomment-4329229692
- GitHub auth re-check / blocker link: https://github.com/vamseeachanta/workspace-hub/issues/2519#issuecomment-4329242339

### #2520 — `ace-linux-2` GitHub auth blocker

Created issue:

- https://github.com/vamseeachanta/workspace-hub/issues/2520
- Title: `fix(workstations): repair and gate ace-linux-2 GitHub auth before delegation`
- State: open as of this handoff.

Reason:

- `gh` is installed on `ace-linux-2`, but auth token is invalid.
- `gh api user` returns HTTP 401.
- Therefore `ace-linux-2` should not perform GitHub mutations until repaired.

## Verified `ace-linux-2` state

### Use login shell

Always launch checks/work from `ace-linux-2` through a login shell:

```bash
ssh ace-linux-2 'bash -lc "<command>"'
```

Plain/non-login SSH misses user-level paths and can falsely report Hermes/Codex unavailable.

### Hermes / Codex

Latest verified via login shell:

```text
hermes: /home/vamsee/.local/bin/hermes
Hermes Agent v0.11.0 (2026.4.23)

Hermes model:
{'default': 'gpt-5.5', 'provider': 'openai-codex', 'base_url': 'https://chatgpt.com/backend-api/codex'}

codex: /home/vamsee/.npm-global/bin/codex
codex-cli 0.123.0
```

Codex auth files exist under `~/.codex/`, but no token/secret contents were read or recorded.

### GitHub CLI

Latest verified via login shell:

```text
GH_PATH=/usr/bin/gh
gh version 2.90.0 (2026-04-16)

github.com
  X Failed to log in to github.com account vamseeachanta (default)
  - Active account: true
  - The token in default is invalid.

gh api user -> Requires authentication (HTTP 401)
```

Current operational rule:

- `ace-linux-1` remains GitHub mutation authority.
- `ace-linux-2` may run local Hermes/Codex execution if launched correctly, but should not comment, label, create issues/PRs, or close issues locally until #2520 is resolved.

### Repo / tools baseline

Committed report:

- `docs/reports/2026-04-27-issue-2519-ace-linux-2-readiness-probe.md`
- Initial commit: `2dcc94b25`
- Correction commit: `4abf2a76d`

Summary from report:

- `ace-linux-2` reachable via SSH.
- Canonical root: `/mnt/local-analysis/workspace-hub`.
- Tier-1 repos mostly clean on `main`:
  - `digitalmodel`: clean, `.venv` present
  - `worldenergydata`: clean, `.venv` present
  - `assetutilities`: clean, `.venv` present
  - `teamresumes`: clean, no `.venv`
- Workspace root on `ace-linux-2` had local session/tooling dirt; avoid root-level implementation there unless rechecked.
- Open-source engineering tools detected: OpenFOAM ESI, Gmsh, FreeCAD packages, Blender, ParaView/pvpython/pvbatch, CalculiX, QGIS, GDAL/OGR.
- Proprietary/licensed tools not detected in PATH: OrcaFlex/OrcaWave, ANSYS/AQWA, MATLAB, SALOME/Code_Aster.

## Current local workspace caveat on `ace-linux-1`

The current `ace-linux-1` working tree has generated provider/report modifications from quota refresh commands. Do not mix them into unrelated commits unless intentionally refreshing provider artifacts:

```text
M config/ai-tools/agent-quota-latest.json
M config/ai-tools/provider-autolabel-candidates.json
M config/ai-tools/provider-routing-scorecard.json
M config/ai-tools/provider-utilization-weekly.json
M config/ai-tools/provider-work-queue.json
M docs/reports/provider-autolabel-candidates.md
M docs/reports/provider-routing-scorecard.md
M docs/reports/provider-utilization-weekly.md
M docs/reports/provider-work-queue.md
```

If committing handoff docs, add only the intended handoff file(s).

## Recommended next task for parallel Hermes terminal

Ask the parallel Hermes terminal/session to produce an operator-ready continuous/parallel work prompt pack for both machines, not to execute implementation yet.

### Suggested prompt to give the next Hermes terminal

```text
You are operating from /mnt/local-analysis/workspace-hub on ace-linux-1.
Load relevant skills before acting: workstation-aware-provider-orchestration, overnight-parallel-agent-prompts, agent-usage-optimizer, gh-work-planning, github-issues, hermes-agent.

Goal: Create a continuous and parallel work prompt pack for Hermes-led orchestration across ace-linux-1 and ace-linux-2 for issue #2519.

Context:
- Primary issue: #2519 https://github.com/vamseeachanta/workspace-hub/issues/2519
- Blocker issue: #2520 https://github.com/vamseeachanta/workspace-hub/issues/2520
- ace-linux-1 is the primary control plane and GitHub mutation authority.
- ace-linux-2 is first overflow / execution worker.
- ace-linux-2 must be invoked with login shell: ssh ace-linux-2 'bash -lc "<command>"'.
- ace-linux-2 Hermes/Codex are available through login shell and configured for openai-codex / gpt-5.5.
- ace-linux-2 gh auth is invalid; do not ask ace-linux-2 to perform GitHub mutation until #2520 is repaired.
- User reports Codex credit expires in about 24 hours with about 50% usage remaining. Prioritize Codex-heavy bounded work, but respect plan gates.
- Default provider/model: openai-codex / gpt-5.5.
- Gemini/Copilot explicit-use only; never silent fallback/default.
- Do not dispatch implementation unless issue is truly status:plan-approved and local gates are ready.

Deliverables:
1. Write a markdown prompt pack under docs/plans/ for issue #2519.
2. Include separate prompts for:
   A. ace-linux-1 control-plane Hermes terminal.
   B. ace-linux-2 Codex/Hermes worker terminal.
   C. optional monitor/reconciler terminal on ace-linux-1.
3. Include preflight checks for each prompt:
   - git status / branch / remote state,
   - provider config,
   - gh auth where relevant,
   - ace-linux-2 login-shell readiness,
   - issue gate labels and local plan-approved markers.
4. Include a dispatch ledger schema and exact evidence artifacts each terminal must produce.
5. Include a contention map: which terminal may write which files/directories and which paths are forbidden.
6. Include a Codex-credit burn-down strategy that prefers planning/review/prompting if implementation gates are not approved, and bounded TDD work only for plan-approved issues.
7. Include exact launch command examples for both machines.
8. Post a short comment to #2519 linking the prompt pack after creating it.
9. If writing docs only, commit and push the prompt pack as a narrow docs-only commit. Do not commit generated provider telemetry artifacts unless intentionally refreshing them.

Verification:
- Verify #2519 and #2520 still exist and labels/state are current.
- Verify ace-linux-2 gh auth status remains treated as blocker unless a fresh check proves it repaired.
- Verify git diff includes only the intended docs/prompt-pack files before commit.
```

## Recommended prompt-pack structure

The next terminal should create something like:

```text
docs/plans/2026-04-27-issue-2519-continuous-parallel-work-prompts.md
```

Suggested sections:

1. Current state and constraints.
2. Provider priority and Codex-credit strategy.
3. Workstation roles.
4. Preflight check commands.
5. Dispatch ledger template.
6. Prompt A — `ace-linux-1` control plane.
7. Prompt B — `ace-linux-2` Codex/Hermes worker.
8. Prompt C — `ace-linux-1` monitor/reconciler.
9. Contention map and negative write boundaries.
10. Stop/fallback conditions.
11. Morning/next-checkpoint evidence summary.

## Immediate safe operating posture

Until #2520 is fixed:

- `ace-linux-1`: owns GitHub mutations, labels, comments, issue state, commits/pushes for orchestration docs.
- `ace-linux-2`: can execute local Codex/Hermes read/write work only in controlled worktrees or clean tier-1 child repos, launched through login shell, with evidence returned to `ace-linux-1` for GitHub updates.

Preferred short-term actions:

1. Generate prompt pack and dispatch ledger for #2519.
2. Repair or manually re-authenticate `gh` on `ace-linux-2` under #2520.
3. Refresh provider queue and select Codex-fit candidates.
4. Only launch implementation for issues that pass both GitHub label and local marker gates.
5. Use Codex credit on bounded, verifiable, low-contention workstreams.

## Exit note

This handoff is intentionally a docs/planning handoff. It does not launch long-running workers and does not repair authentication. It preserves the verified state so the next Hermes terminal can generate the continuous/parallel prompt pack with minimal rediscovery.
