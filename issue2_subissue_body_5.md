Parent: #2

## Objective
Document and enforce the security baseline for any Teams/Hermes/repo POC before it touches real users or broader repo content.

## Scope
- Identity mapping: Teams user/channel/team context to repo content entitlements.
- Credential handling: pinned knowledge pack preferred; otherwise read-only GitHub App/deploy key stored in approved secret store.
- Logging: do not persist prompts, model answers, retrieved snippets, tokens, raw Teams message bodies, or credentials by default.
- Graph posture: Bot Framework activity context only unless a separate admin-approved Graph scope is justified.
- Prompt injection and data exfiltration test cases.

## Deliverable
HTML security checklist under `reports/teams-bot/issue-2/` with pass/fail status and required approvers.

## Acceptance criteria
- [ ] Least-privilege permissions documented.
- [ ] No forbidden Graph scopes in default POC.
- [ ] Secrets are not committed, dumped, logged, or included in transcripts.
- [ ] Repo access method has owner, rotation, and revocation path.
- [ ] Prompt-injection and unauthorized-content tests are listed and run before broader demo.
