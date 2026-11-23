# Define canonical llm-wiki repo placement

## Scope
Define canonical placement for public llm-wiki, private/domain wiki staging, and client-private wiki targets under `/mnt/local-analysis` without silently moving repositories or creating public references to client-specific roots.

## Non-goals
- Do not move repositories in this issue.
- Do not publish private/client corpus content.

## Acceptance criteria
- Public, private/domain, and client-private wiki targets have distinct canonical naming rules.
- Repo-placement decisions cite live filesystem/git evidence.
- Any migration work is split into plan-gated follow-up issues.
