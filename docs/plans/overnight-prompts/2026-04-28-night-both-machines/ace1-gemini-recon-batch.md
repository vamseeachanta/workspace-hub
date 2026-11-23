# A2 — ace-linux-1 Gemini recon batch

You are running from `/mnt/local-analysis/workspace-hub` through Hermes OpenRouter Gemini. This is a planning/research-only lane. Do not change source code, labels, issue state, or implementation files. Do not ask the user questions.

## Purpose

Gemini is currently underused and best suited for batched research/recon/risk enumeration. Produce operator-ready planning artifacts that can feed tomorrow's plan-gated queue without violating implementation gates.

## Allowed writes

Only write files under:

`docs/plans/overnight-prompts/2026-04-28-night-both-machines/results/`

Use these filenames:

- `gemini-2295-tax-franchise-recon.md`
- `gemini-2501-governance-lock-discrepancy.md`
- `gemini-2254-provider-telemetry-plan.md`
- `gemini-2519-workstation-orchestration-plan.md`
- `gemini-2520-ace2-auth-gate-plan.md`
- `gemini-batch-summary.md`

## Issues to research / harden

1. #2295 — WRK: 2025 TX franchise No Tax Due + PIR — SKEstates and AceEngineer  
   URL: https://github.com/vamseeachanta/workspace-hub/issues/2295  
   Output: checklist of filing/data prerequisites, risk list, exact next actions, no private-data assumptions.

2. #2501 — #2105 governance-lock handoff vs live-state discrepancy  
   URL: https://github.com/vamseeachanta/workspace-hub/issues/2501  
   Output: live-state reconciliation plan, sources to inspect, acceptance criteria, proposed plan-gate labels.

3. #2254 — improve Claude and Gemini quota observability for exact weekly targeting  
   URL: https://github.com/vamseeachanta/workspace-hub/issues/2254  
   Output: telemetry gap analysis using existing provider reports, implementation plan, tests/fixtures needed, no code edits.

4. #2519 — orchestrate AI provider usage and workstation dispatch  
   URL: https://github.com/vamseeachanta/workspace-hub/issues/2519  
   Output: plan hardening and acceptance criteria for a durable control plane, including ledger schema and machine-readiness gates.

5. #2520 — repair and gate ace-linux-2 GitHub auth before delegation  
   URL: https://github.com/vamseeachanta/workspace-hub/issues/2520  
   Output: update the plan based on current evidence that ace-linux-2 `gh auth` is now OK, and identify remaining gates: dirty/behind checkout, provider smoke, launch-shell path.

## Required method

For each issue:

1. Fetch latest issue body/comments with `gh issue view`.
2. Inspect relevant local docs/scripts/reports as read-only evidence.
3. Write a concise markdown artifact with:
   - current state
   - gaps/blockers
   - recommended labels/status transition, if any
   - exact next implementation prompt for Codex/Claude
   - verification commands that tomorrow's worker should run
4. End with `gemini-batch-summary.md` ranking the five items by next-action readiness and expected AI-credit value.
