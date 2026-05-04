# Disagreement report — plan #2552 (2026-05-01)

## Verdicts

| Provider | Verdict |
|---|---|
| codex | MAJOR |
| gemini | UNAVAILABLE (gemini CLI failed, rc=1: [WARN] Skipping unreadable directory: /tmp/snap-private-tmp (EACCES: permission denied, scandir '/tmp/snap-private-tmp') [WARN] Skipping unreadable directory: /tmp/systemd-private-384f6636782f40648bb07a1bce9c9cef-ModemManager.service-hqDDIK (EACCES: permission denied, scandir '/tmp/systemd-private-384f6636782f40648bb07a1bce9c9cef-ModemManager.service-hqDDIK') [WARN] Skipping unreadable directory: ) |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### codex

- The plan explicitly says it is not approval-ready, so it cannot receive APPROVE. Header quote: `not approval-ready until fresh cross-provider re-review returns no MAJOR or the user explicitly waives remaining cross-provider evidence`. The `Adversarial Review Summary` repeats that full cross-provider approval is blocked until fresh Codex/Gemini reruns return no MAJOR or the user waives it. No waiver is present in the plan.
- Issue #2552 acceptance criteria require the runbook to cover `collaborator onboarding`, but the plan’s “Runbook document outline” covers `Unsolicited paid-help offer`, `Suspected spam / bot comment`, `Legitimate external contributor request`, and `Paid external execution request`. “Collaborator onboarding” is not a first-class scenario with criteria, approval steps, access transition, or revocation/least-privilege handling. This is an issue-AC coverage gap.
- Scenario 3 still permits a `temporary lift of the limit` as one path for non-collaborator contribution. That conflicts with the lockdown purpose verified in issue #2546: configure repos so only collaborators can create/interact with issues, PRs, comments, and related surfaces where GitHub supports it. If a global interaction-limit lift is allowed, the plan needs explicit owner approval, duration, repo scope, monitoring, rollback, and why collaborator invitation/off-GitHub intake is insufficient. Those controls are absent.
- The plan’s `CONTRIBUTOR_INTEREST_TEMPLATE` requirement is underspecified for the active lockdown. It says the template should direct contributors first to `https://aceengineer.com/#contact`, but the tests only require the string `collaborators_only`, the URL, and conditional language before fork/PR. This can pass while still producing a template intended for GitHub replies that non-collaborators cannot receive or act on during lockdown.
- The inline plan claims `https://aceengineer.com/#contact` was `verified 200 on 2026-04-30`, but the review could not verify that unstable external claim from the local workspace, and no durable artifact or command output is cited. Because README discoverability depends on this exact route, the plan should either cite committed verification evidence or make execution re-verify the URL before publishing it.
- The plan under review diverges materially from the `main` copy of `docs/plans/2026-04-29-issue-2552-external-contributor-runbook.md`, which still says `Complexity: T1`, lacks the README pointer, and presents a T1 deferred-review path. If the inline plan is the intended artifact, it must be committed or otherwise bound to the reviewed revision before approval; otherwise implementers may follow the stale `main` plan.

### gemini

- (none)

