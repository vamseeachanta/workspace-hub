# Disagreement report — plan #2541 (2026-05-02)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | UNAVAILABLE (claude CLI failed, rc=124: no stderr captured) |
| codex | MAJOR |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

- (none)

### codex

- The plan body under review does not match the repository source-of-record I could fetch. The inline plan says `Status: plan-review (2026-05-02 nightly batch 2 patch...)`, but `docs/plans/2026-04-28-issue-2541-elements-sesa-curated-extraction-plan.md` on `main` still contains the older unsafe pseudocode line: `write extracted text to .planning/intel/elements-deep-extraction/sesa/<slug>.txt`. If implementers use the path named in the prompt, they may execute the stale raw-text-staging plan rather than the patched inline text.
- The inline plan’s `Review artifacts` claim references `scripts/review/results/2026-05-02-plan-2541-{codex,claude}.md`, but both concrete files returned 404 when fetched as `scripts/review/results/2026-05-02-plan-2541-codex.md` and `scripts/review/results/2026-05-02-plan-2541-claude.md`. This directly conflicts with the plan’s own `Adversarial Review Summary`, which says the patched plan “needs rerun” and “valid fresh review evidence.”
- The `Acceptance Criteria` require “Adversarial review (Claude + Codex + Gemini) is invoked on this plan before user approval,” but the inline `Adversarial Review Summary` says “Gemini rerun unavailable/pending.” That means the plan’s own approval gate is unmet.
- The inline `Approval blocker` requires `docs/governance/sesa-extraction-clearance-2026.md` or an owner issue comment before extraction/publication, but `docs/governance/sesa-extraction-clearance-2026.md` returned 404. The plan correctly blocks implementation on clearance, but it is not approval-ready while the required clearance artifact is absent and the alternative issue-comment evidence is not cited.
- The repository copy of the plan still treats the vendor policy as merely an open question: `Acceptance Criteria / Vendor brochure redistribution policy is flagged as an open question for plan review`. The inline patched plan tightens this, but because the path artifact is stale, the old acceptance criterion remains a live approval risk unless the repository file is updated or reviewers are explicitly told the inline text supersedes it.

