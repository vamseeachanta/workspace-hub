# Verification Log: Plan #3712 Required Status Checks

Date: 2026-07-30
Repo: vamseeachanta/workspace-hub
Mode: planning only; read-only GitHub API except final issue comment/label; no working-tree edits.

## Commands and Outcomes

- `git branch --show-current && git status --short --branch`: current branch `main`; no working-tree file changes shown; local main was behind remote.
- `gh issue view 3712 --repo vamseeachanta/workspace-hub --json number,title,state,labels,body,url`: issue #3712 OPEN with `cat:harness`, `domain:workstations`, `status:needs-plan`.
- `rg --files .github/workflows`: workflow files enumerated for baseline, enforcement, legal, Claude, skills, Pages, domain, kanban, completeness, and dispatch workflows.
- `gh api repos/vamseeachanta/workspace-hub/rulesets/17369764 --jq '{id,name,target,enforcement,conditions:.conditions, rules:[.rules[] | {type:.type, parameters:.parameters}]}'`: active `protect-main` ruleset has only `deletion` and `non_fast_forward`.
- `gh api repos/vamseeachanta/workspace-hub/branches/main/protection --include`: HTTP 404 `Branch not protected`.
- `gh api repos/vamseeachanta/workspace-hub/actions/secrets --jq '.secrets[] | .name' | rg 'LEGAL_SCAN_AUTH_CURRENT|AUTH_ENVELOPE|LEGAL|AUTH'`: output `CLAUDE_CODE_OAUTH_TOKEN` and `LEGAL_CLIENT_MAP`; no `LEGAL_SCAN_AUTH_CURRENT`.
- `nl -ba .github/workflows/legal-rule-authority-reusable.yml | sed -n '35,42p'`: shows `AUTH_ENVELOPE: ${{ secrets.LEGAL_SCAN_AUTH_CURRENT }}` and `test -n "$AUTH_ENVELOPE"`.
- `gh pr checks 3590 --repo vamseeachanta/workspace-hub`: `strict-scan / authority` fail; candidate checks `Run Tests`, `Scheduler Mutation Surface Guard`, `Review Evidence Check`, and `Plan Approval Check` pass.
- `gh pr checks 3583 --repo vamseeachanta/workspace-hub`: `strict-scan / authority`, `Scheduler Mutation Surface Guard`, and `Client-PII Gate` fail; candidate checks `Run Tests`, `Review Evidence Check`, and `Plan Approval Check` pass.
- `gh pr checks 3569 --repo vamseeachanta/workspace-hub`: `strict-scan / authority`, `Scheduler Mutation Surface Guard`, and `Client-PII Gate` fail; candidate checks `Run Tests`, `Review Evidence Check`, and `Plan Approval Check` pass.
- `gh pr list --repo vamseeachanta/workspace-hub --state open --json number --jq '.[].number'`: returned 18 open PRs: 3590, 3583, 3569, 3563, 3546, 3543, 3540, 3520, 3471, 3468, 3465, 3425, 3411, 3410, 3379, 3378, 3363, 3327.
- `uv run scripts/data/drive-index-search/search.py "required status checks branch protection AUTH_ENVELOPE scheduler mutation" --json --caller plan-resource-intel`: several indexes stale/unreachable; only unrelated DNV cathodic protection token match returned.

## Unverified

- Secret values cannot be read by design; only presence and green check behavior can prove future correctness.
- Open PR check status can change; implementation must refresh all `gh pr checks` output immediately before ruleset changes.
- No local ace1 pytest baseline was rerun in planning mode to avoid mutating the shared working tree; the plan carries the user-provided baseline as no-new-failures acceptance: `tests/enforcement` 2 failed/417 passed and `tests/cron` 284 passed/0 failed.
