Parent: #2

## Objective
Determine which Microsoft Teams integration paths are actually permitted for this organization and this workstation before we spend time on the wrong POC route.

## Current local evidence
- Microsoft Teams is installed and running as `MSTeams_26120.3106.4722.3411_x64__8wekyb3d8bbwe`.
- Local Teams exposes protocol/deep-link handlers (`msteams`, `web+msteams`, etc.) and `ms-teams.exe` alias.
- Local Teams client does **not** by itself host a bot endpoint.
- Hermes status does not show a Teams messaging gateway configured.

## Scope
- Check whether Teams custom app upload / sideloading is allowed.
- Check whether incoming webhooks/connectors are allowed in the target Team/channel.
- Check whether Azure Bot registration is available and who can approve it.
- Check tenant app permission policies, app setup policies, and custom app policies.
- Identify the fastest allowed path among:
  1. Bot Framework Teams bot,
  2. Teams tab wrapping local/internal chatbot,
  3. incoming webhook demo bridge,
  4. deep-link/manual demo fallback.

## Deliverable
Create an HTML permissions checklist under `reports/teams-bot/issue-2/` with:
- reviewed setting,
- observed value/evidence,
- approver/owner if admin action is needed,
- go/no-go for each POC route,
- screenshots or redacted evidence where allowed.

## Acceptance criteria
- [ ] We know if custom Teams app upload/sideload is allowed.
- [ ] We know if incoming webhooks/connectors are allowed.
- [ ] We know if Azure Bot registration/admin consent is possible.
- [ ] We select one primary POC route and one fallback route.
- [ ] No Graph message-read permissions are requested by default.
