# Retroactive Review Prompt — Provider Session Learning Transfer

Use this prompt shape when reviewing the provider-session learning transfer retroactively.

## Role
You are an independent adversarial reviewer. Find gaps, risks, missing evidence, workflow-policy violations, and duplicate issue creation. Do not rubber-stamp.

## Scope
Review the provider-session learning transfer and skill updates around:
- `916743102 docs(provider): transfer session learning audit`
- `513378ecb docs: clarify adversarial review requirements for skill transfers`
- `docs/reports/2026-05-08-provider-session-learning-transfer.md`
- `.claude/skills/coordination/provider-session-learning-transfer/SKILL.md`
- `.claude/skills/software-development/multi-provider-adversarial-review/SKILL.md`

## User correction to enforce
All meaningful work is important, including harness, file structure, test suite, docs/report, skill-transfer, governance, policy, and workflow changes. Do not skip workflow compliance or adversarial review merely because a change is docs-only, skill-only, harness-only, or workflow/report-only. Scale prompt depth instead: use high-level sanity-check prompts for low-risk transfer/report work and thorough review prompts for code, tests, harness, file structure, policy, and workflow-impacting changes.

## Review questions
1. Does the transfer land learnings durably in the repo ecosystem, or is it only a local/session summary?
2. Are the issue tracker links, report paths, and review evidence sufficient to resume later without chat context?
3. Do the skill patches encode the user correction without weakening the repository's three-provider review default?
4. Are there duplicate issue risks, especially #2657 versus broader llm-wiki spinout cleanup trackers like #2650?
5. Are there material overclaims, especially around Hermes versus Claude memory bridge parity?
6. Are there blockers before this work is considered closed?

## Required output
Verdict: `APPROVE`, `MINOR`, or `MAJOR`.

Then list findings by severity:
- Critical / High: must fix before closeout.
- Medium: should fix before this becomes durable precedent.
- Low: clarity or follow-up cleanup.

For every finding, include exact remediation.
