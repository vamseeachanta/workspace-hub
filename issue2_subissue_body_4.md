Parent: #2

## Objective
Wire the minimal Q&A service into Microsoft Teams using the fastest route allowed by the tenant settings discovered in the permission-gate subissue.

## Candidate routes
1. Teams tab wrapping local/internal web chatbot.
2. Bot Framework Teams bot endpoint.
3. Incoming webhook bridge for demo-only posting.
4. Deep-link/manual share fallback if tenant blocks app install.

## Scope
- Select route based on documented permission evidence.
- Create minimal Teams app package/manifest or webhook config as applicable.
- Use Bot Framework activity context if using a bot; do not request broad Graph message-read scopes.
- Add a simple answer card/message format with citations and follow-up suggestions.

## Deliverable
- HTML integration report with screenshots/redacted evidence.
- Teams manifest or webhook/tab configuration files as appropriate.
- End-to-end demo transcript.

## Acceptance criteria
- [ ] The chosen route works in the local/org Teams environment or the exact blocker is documented.
- [ ] User can ask or submit a question and receive a cited answer/result in or through Teams.
- [ ] No broad Graph message-read scopes are used by default.
- [ ] All config/secrets are kept out of logs and repo commits.
