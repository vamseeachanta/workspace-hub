## Feasibility pass: local Teams + race-to-POC breakdown

I inspected the Teams program available on this computer and created a scoped POC breakdown.

### Local Teams findings
- Microsoft Teams is installed and running locally as `MSTeams_26120.3106.4722.3411_x64__8wekyb3d8bbwe`.
- The package exposes Teams protocol/deep-link handlers such as `msteams` and `web+msteams`, plus the `ms-teams.exe` alias.
- The local Teams desktop client is a client/runtime, not a bot-hosting surface. A real interactive Teams bot still needs a Teams app package/Bot Framework route and tenant policy/admin approval.
- Hermes on this machine is configured for Telegram, but not a Teams messaging gateway/platform.

### Feasibility call
A fast POC is feasible if we split the work:
1. Build a pinned, approved repo knowledge pack from the repo ecosystem.
2. Build a local Hermes-backed Q&A service over that knowledge pack.
3. Connect that service to the fastest Teams surface allowed by org settings: Teams tab, Bot Framework bot, incoming webhook demo bridge, or deep-link/manual fallback.

HTML feasibility artifact:
https://github.com/vamseeachanta/llm-wiki-acma/blob/main/reports/teams-bot/issue-2/2026-05-28_225033-teams-local-feasibility-poc-subissues.html

### Subissues created
- [ ] #3 — Verify Teams tenant/app permissions and local Teams POC path
- [ ] #4 — Build approved repo knowledge pack for Oil & Gas Q&A POC
- [ ] #5 — Implement minimal Hermes-backed Q&A service over repo knowledge pack
- [ ] #6 — Connect Q&A POC to fastest allowed Teams surface
- [ ] #7 — Define security, identity, logging, and credential gates for Teams bot POC
- [ ] #8 — Produce HTML POC demo report and acceptance matrix

### Recommended execution order
- Run #3 and #4 in parallel.
- Then #5.
- Then #6 based on #3 outcome.
- Keep #7 active as a gate throughout.
- Finish with #8 for stakeholder review.

Security posture remains: no broad Graph message-read scopes by default, no raw `sources/` access unless explicitly approved, no prompt/answer/snippet/token logging by default, and all review artifacts are HTML-first.
