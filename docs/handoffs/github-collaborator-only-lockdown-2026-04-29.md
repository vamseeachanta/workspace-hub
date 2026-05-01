# GitHub collaborator-only public repo lockdown — exit handoff

Timestamp: 2026-04-29T02:04:38Z

## What triggered this

An external account (`Baijack-star`) commented on workspace-hub issue [#2401](https://github.com/vamseeachanta/workspace-hub/issues/2401) offering paid execution help. The user requested a review and repo settings changes so only collaborators can touch issues, code, PRs, etc., mainly for public repositories.

## Completed during this session

1. Created tracking issue [#2546](https://github.com/vamseeachanta/workspace-hub/issues/2546): `chore(security): restrict public repo interactions to collaborators only`.
2. Applied GitHub repository interaction limits to every public `vamseeachanta/*` repository:
   - `limit=collaborators_only`
   - `expiry=six_months` (longest GitHub-supported expiry)
3. Verified all public repos report `collaborators_only` after the API update.
4. Attempted equivalent interaction-limit check for private repos; GitHub returns `405 Interaction limits cannot be set for private repositories`, confirming this setting applies only to public repos. Private repositories remain collaborator/member gated by visibility.
5. Created Hermes-local renewal cron job `d9b2d1c2270d` (`renew-github-collaborator-only-interaction-limits`) to re-apply the public repo limits every 150 days.
6. Closed [#2546](https://github.com/vamseeachanta/workspace-hub/issues/2546) as completed with verification comments.

## Public repo verification snapshot

All public repos below were verified as `collaborators_only` with expiry on 2026-10-29 UTC:

| Repo | Archived? | Status |
|---|---:|---|
| `vamseeachanta/worldenergydata` | false | collaborator-only interaction limit applied |
| `vamseeachanta/workspace-hub` | false | collaborator-only interaction limit applied |
| `vamseeachanta/assethold` | false | collaborator-only interaction limit applied |
| `vamseeachanta/aceengineer-website` | false | collaborator-only interaction limit applied |
| `vamseeachanta/assetutilities` | false | collaborator-only interaction limit applied |
| `vamseeachanta/digitalmodel` | false | collaborator-only interaction limit applied |
| `vamseeachanta/teamresumes` | false | collaborator-only interaction limit applied |
| `vamseeachanta/hobbies` | false | collaborator-only interaction limit applied |
| `vamseeachanta/pdf-large-reader` | false | collaborator-only interaction limit applied |
| `vamseeachanta/aceengineercode` | true | collaborator-only interaction limit applied |

## Future GitHub issues created

These are intentionally future follow-ups, not part of the completed emergency lockdown:

1. [#2550](https://github.com/vamseeachanta/workspace-hub/issues/2550) — `chore(security): codify public repo interaction-limit renewal in scheduled tasks`
   - Move the renewal from Hermes-local cron into workspace-hub's canonical scheduled-task system.
   - Add deterministic script, dry-run mode, verification report, and schedule metadata.

2. [#2551](https://github.com/vamseeachanta/workspace-hub/issues/2551) — `audit(security): verify branch/ruleset protections across public repos after collaborator-only lockdown`
   - Audit branch protection, repository rulesets, PR settings, issue/discussion/wiki/project surfaces, and repo baseline by repo class.
   - This is the issue that should address the broader "code/PR path" hardening beyond GitHub interaction limits.

3. [#2552](https://github.com/vamseeachanta/workspace-hub/issues/2552) — `docs(security): external contributor and unsolicited paid-help response runbook`
   - Document when to ignore, hide, report, or safely route external contributor / paid-help requests.
   - Add templates and onboarding guardrails.

## Important limitation / risk

GitHub repository interaction limits are temporary. Current API supports `one_day`, `three_days`, `one_week`, `one_month`, and `six_months`; there is no permanent setting at repo level through this API. Current protection therefore depends on renewal before expiry.

Next operator should treat [#2550](https://github.com/vamseeachanta/workspace-hub/issues/2550) as the durable-control-plane follow-up.

## Exit state

- [#2546](https://github.com/vamseeachanta/workspace-hub/issues/2546) is closed as completed.
- Follow-up issues [#2550](https://github.com/vamseeachanta/workspace-hub/issues/2550), [#2551](https://github.com/vamseeachanta/workspace-hub/issues/2551), and [#2552](https://github.com/vamseeachanta/workspace-hub/issues/2552) are open.
- No response was posted to the external commenter.
- Repo working tree had unrelated pre-existing modifications before this handoff; this handoff doc is the only intended new repo artifact from the exit step.

## Suggested next session order

1. Plan [#2550](https://github.com/vamseeachanta/workspace-hub/issues/2550) first so renewal becomes repo-tracked, testable, and visible.
2. Plan [#2551](https://github.com/vamseeachanta/workspace-hub/issues/2551) next for branch/ruleset/code-path hardening.
3. Plan [#2552](https://github.com/vamseeachanta/workspace-hub/issues/2552) for human/operator policy.
