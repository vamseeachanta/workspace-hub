# Business Brain 48-hour GTM reverse-prompt packet pattern

Session-derived pattern for converting a broad "best next move" request into repo-backed GTM throughput without bypassing GitHub gates.

## Trigger
Use when the user asks to continue from Business Brain / video / reverse-prompting context and wants the best next move for GTM or client-conversion work.

## Pattern
1. Treat the main GTM/client-conversion issue as the command center; in the observed session this was `workspace-hub#2016`.
2. Reuse active child issues instead of creating a new umbrella. For the vessel-contractor wave, the useful child set was:
   - `#2554` vessel contractor outreach matrix
   - `#2555` vessel capability charts
   - `#2556` brochure + outbound tracker
   - `#2557` weekly productivity-flow review
3. Create a dated prompt pack under `docs/plans/overnight-prompts/<date>-reverse-prompt-48h/` containing:
   - `master-plan.md` with command-center objective, issue map, ordering, gates, and approval boundaries
   - one lane prompt per child issue
   - `results/` for lane summaries
4. Post a concise command-center update to the parent issue linking the prompt pack and naming what can run autonomously vs what needs user approval.
5. Execute the highest-leverage review-readiness lanes first, not the send/outreach lane, when child plans are blocked by incomplete provider-review evidence.
6. Delegate bounded lanes only with explicit allowed/forbidden paths, no label authority, no external outreach, and no commits by the worker unless explicitly authorized.
7. Have lane workers write `results/lane-*-summary.md` and return changed files, verification, and blockers.
8. Orchestrator verifies counts / grep checks / diff stat, posts child issue comments, then commits only intended repo artifacts.

## Concrete lane ordering heuristic
For a GTM collateral wave:
1. Plan/evidence hygiene for target matrix (`#2554`-like issue)
2. Plan/storyboard hygiene for capability charts (`#2555`-like issue)
3. Brochure/outbound tracker only after upstream evidence/review gates clear (`#2556`-like issue)
4. Productivity review lane can run in parallel or after the artifact lanes (`#2557`-like issue)

## Review-gate lesson
`UNAVAILABLE`, empty, wrapper-failed, or retrieval-failed Codex/Gemini artifacts are useful blocker evidence but do not satisfy a live non-Claude adversarial-review gate. State this explicitly in the plan and child issue update.

## Evidence-boundary lesson
For public GTM target lists, separate:
- corporate/root evidence that proves the company exists or broad fit;
- deep-link evidence that proves a specific vessel/service/pain point;
- pain-point evidence that supports the outreach hook.
Do not allow generic root URLs to stand in for specific claim evidence.

## Verification examples
- Confirm target-heading patterns match the plan's grep checks.
- Confirm high-priority counts exclude field-guide/header/summary lines.
- Confirm deprecated field names such as `evidence_urls` are removed after replacing the evidence model.
- Confirm future implementation paths are named but not prematurely created in planning-only lanes.

## Live review follow-through
After the review-readiness lanes land, the next best autonomous move is live non-Claude adversarial review on the unblocked child plans.

1. Materialize one compact, self-contained prompt per issue under `.planning/quick/review-<issue>-prompt.md`.
2. Include the plan artifact plus the immediate scaffold/storyboard artifact under review; do not rely on reviewers reading paths from disk.
3. Run Codex first when Gemini capacity is uncertain; add Gemini when available or required by the current review policy.
4. Save durable artifacts under `scripts/review/results/YYYY-MM-DD-plan-<issue>-codex.md` and/or `...-gemini.md`.
5. Post concise issue comments with verdict, findings, and saved artifact paths.
6. If a provider is unavailable, save an explicit `Verdict: UNAVAILABLE` artifact and treat it as blocker evidence, not as approval evidence.
7. Only after live review evidence exists should the orchestrator consider promoting the plan toward `status:plan-review` or starting downstream brochure work.

## User-approval boundary
No outreach, contact enrichment, prospect-sensitive data publication, or external sending occurs until the user explicitly approves the final outbound packet.
