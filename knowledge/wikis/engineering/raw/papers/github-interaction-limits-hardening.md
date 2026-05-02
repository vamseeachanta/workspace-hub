# Archived Skill: `github-interaction-limits-hardening`

Original path: `/home/vamsee/.hermes/skills/github/github-interaction-limits-hardening`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/github/github-interaction-limits-hardening`
Consolidation date: 2026-04-29

---

---
name: github-interaction-limits-hardening
description: Lock down public GitHub repositories so only collaborators can interact with issues, PRs, comments, discussions, and other user-generated surfaces using repository interaction limits; includes expiry verification and renewal handling.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [GitHub, Repository Security, Interaction Limits, Issues, Pull Requests]
    related_skills: [github-repo-management, github-issues, github-comment-body-file-safety, cron-job-management]
---

# GitHub Interaction Limits Hardening

## When to Use

Use this skill when a public GitHub repository or a set of repositories should remain readable but prevent outside/non-collaborator interactions, such as issue comments, PRs, discussions, or drive-by solicitation. Typical triggers include spam, paid-work solicitation, unwanted outside PRs, public repo hardening, or a request like "only collaborators can touch issues/code/PRs".

## Class of Task

Repo security hardening across one or more GitHub repositories by applying collaborator-only public interaction limits, verifying the live API state, and creating a renewal path because GitHub requires expiry.

## Key GitHub Constraints

- Repository interaction limits apply to **public repositories**.
- Private repositories return `405 Interaction limits cannot be set for private repositories`; private visibility already gates repo access to collaborators/members with access.
- Interaction limits are **temporary**; GitHub requires an `expiry`.
- Use the longest supported expiry, currently `six_months`, when the intent is durable lock-down.
- Add a renewal reminder or scheduled job before expiry if the setting should remain in force.
- This setting does **not** change repo visibility, collaborators, branch protection, or existing issue/comment history.

## Workflow

### 1. Authenticate and enumerate repos

```bash
gh auth status
gh api user --jq '.login'

OWNER=<owner-or-org>
mkdir -p /tmp/github-interaction-limits
gh repo list "$OWNER" --limit 1000 \
  --json nameWithOwner,visibility,isArchived,defaultBranchRef,hasIssuesEnabled,pushedAt,url \
  > /tmp/github-interaction-limits/repos.json

python3 - <<'PY'
import json
from collections import Counter
repos=json.load(open('/tmp/github-interaction-limits/repos.json'))
print('total', len(repos))
print(Counter((r['visibility'], r['isArchived']) for r in repos))
for r in repos:
    print(f"{r['nameWithOwner']}\t{r['visibility']}\tarchived={r['isArchived']}\tissues={r['hasIssuesEnabled']}")
PY
```

### 2. Create or update a tracking issue

For multi-repo changes, create a tracking issue first. Include:
- trigger / why now
- scope and non-goals
- GitHub API limitation: `six_months` expiry
- acceptance criteria
- verification table requirement

Use a body file to avoid shell quoting problems:

```bash
cat > /tmp/github-interaction-limits/issue-body.md <<'EOF'
## Summary
Lock down public GitHub repository interactions so only collaborators can create/interact with issues, pull requests, comments, discussions, and related user-generated surfaces where GitHub supports that control.

## Scope
- Enumerate target repositories.
- Apply GitHub repository interaction limits with `limit=collaborators_only` to public repos.
- Verify final settings via GitHub API.
- Leave private repos unchanged unless GitHub supports an equivalent setting.

## Non-goals
- Do not delete existing issues/comments.
- Do not remove legitimate collaborators.
- Do not change repository visibility.
- Do not globally disable Issues unless explicitly approved.

## Acceptance criteria
- [ ] Public repos are verified as `collaborators_only`.
- [ ] Private repos are inventoried or explicitly skipped with rationale.
- [ ] Renewal path exists before expiry.
EOF

gh issue create --repo "$OWNER/<tracking-repo>" \
  --title 'chore(security): restrict public repo interactions to collaborators only' \
  --body-file /tmp/github-interaction-limits/issue-body.md
```

### 3. Apply collaborator-only interaction limits to public repos

```bash
python3 - <<'PY'
import json, subprocess, sys, time
from pathlib import Path
repos = json.load(open('/tmp/github-interaction-limits/repos.json'))
results=[]
for r in repos:
    if r['visibility'] != 'PUBLIC':
        continue
    full = r['nameWithOwner']
    row = {'repo': full, 'archived': r['isArchived'], 'url': r['url']}
    before = subprocess.run(['gh','api',f'repos/{full}/interaction-limits'], text=True, capture_output=True)
    row['before'] = before.stdout.strip() or before.stderr.strip()
    setp = subprocess.run([
        'gh','api','-X','PUT',f'repos/{full}/interaction-limits',
        '-f','limit=collaborators_only','-f','expiry=six_months'
    ], text=True, capture_output=True)
    row['set_rc'] = setp.returncode
    row['set_stderr'] = setp.stderr.strip()
    after = subprocess.run(['gh','api',f'repos/{full}/interaction-limits'], text=True, capture_output=True)
    row['after_rc'] = after.returncode
    row['after'] = after.stdout.strip() or after.stderr.strip()
    results.append(row)
    time.sleep(0.15)
Path('/tmp/github-interaction-limits/results.json').write_text(json.dumps(results, indent=2))
for row in results:
    print(f"{row['repo']}\tset_rc={row['set_rc']}\tafter={row['after'][:200]}")
if any(r['set_rc'] != 0 or r['after_rc'] != 0 for r in results):
    sys.exit(1)
PY
```

### 4. Verify final state

```bash
python3 - <<'PY'
import json, subprocess, sys
repos=json.load(open('/tmp/github-interaction-limits/repos.json'))
fail=[]
for r in repos:
    if r['visibility'] != 'PUBLIC':
        continue
    full=r['nameWithOwner']
    p=subprocess.run(['gh','api',f'repos/{full}/interaction-limits'], text=True, capture_output=True, check=True)
    data=json.loads(p.stdout or '{}')
    print(f"{full}: {data.get('limit')} expires {data.get('expires_at')}")
    if data.get('limit') != 'collaborators_only':
        fail.append((full, data))
if fail:
    print('FAIL', fail, file=sys.stderr)
    sys.exit(1)
PY
```

### 5. Check private repos only if needed

If the user asked for "all repos," document that private repos are already visibility-gated. If you attempt the API for uniformity, expect:

```text
405 Interaction limits cannot be set for private repositories.
```

Treat that as confirmation of GitHub's public-only interaction-limit constraint, not as a failure requiring repo changes.

### 6. Post verification and close the tracking issue

```bash
cat > /tmp/github-interaction-limits/verification-comment.md <<'EOF'
## Verification update

Applied and verified GitHub repository interaction limits for all public repositories in scope.

Important GitHub limitation: repository interaction limits require an expiry; the longest supported expiry is `six_months`. A renewal path is required if this should remain durable.

| Repo | Visibility | Archived | Limit | Expires |
|---|---:|---:|---|---|
| ... | PUBLIC | false | `collaborators_only` | `...` |

Private repositories were inventoried but not modified because GitHub interaction limits cannot be set for private repositories; private visibility already restricts access to collaborators/members.
EOF

gh issue comment <issue-number> --repo "$OWNER/<tracking-repo>" --body-file /tmp/github-interaction-limits/verification-comment.md
gh issue close <issue-number> --repo "$OWNER/<tracking-repo>" --reason completed
```

## Renewal Pattern

Because `six_months` expires, create a renewal job/reminder before expiry. A safe cadence is every 150 days.

Renewal job prompt should:
1. verify `gh auth status`
2. list repos
3. re-apply `limit=collaborators_only` / `expiry=six_months` to public repos
4. verify every public repo
5. post a concise verification comment to the tracking issue
6. avoid changing visibility, collaborators, branch protection, repository contents, or issues beyond the verification comment

## Future Follow-Up Issues and Exit Handoff

For emergency/public-repo lockdown tasks, create future issues before exit so the temporary API setting turns into durable governance. Typical follow-ups:

1. **Scheduled renewal / control-plane codification**
   - Move any local/Hermes renewal reminder into the repo's canonical scheduled-task system.
   - Include deterministic script, dry-run mode, verification report, schedule metadata, and tests.
2. **Branch protection / ruleset audit**
   - Audit branch protection, repository rulesets, PR settings, status checks, and enabled public surfaces (Issues, Discussions, Wiki, Projects, Actions).
   - Keep this separate from interaction limits because code-path protection can block workflows and usually needs explicit approval.
3. **External contributor / solicitation response runbook**
   - Document when to ignore, hide, report, or safely route non-collaborator comments, unsolicited paid-help offers, and legitimate contributor requests.
   - Include templates and collaborator-onboarding guardrails.

Exit handoff pattern:
- Write a concise handoff under `docs/handoffs/` or the repo's canonical handoff location.
- Link the completed tracking issue, future issues, verified public repo table, private-repo limitation (`405`), renewal job/reminder, and next-session order.
- Commit the handoff as a narrow docs-only change, push, verify local `HEAD` equals remote, and check the CI run triggered by the handoff commit.
- Post the handoff commit and CI link back to the completed tracking issue.
- Keep unrelated pre-existing working-tree modifications out of the handoff commit.

## Pitfalls

- Do not promise permanent interaction limits; GitHub requires expiry.
- Do not treat private repo 405 responses as errors that need remediation.
- Do not disable Issues as a first response unless the user explicitly approves; interaction limits preserve existing issue workflows for collaborators.
- Use body files for issue bodies/comments to avoid shell quoting and command-substitution bugs.
- Archived public repos can still accept the interaction-limit API; include them in the public-repo pass unless intentionally skipped.
- Do not conflate interaction limits with branch protection/rulesets; create a separate audit/plan for code-path hardening.

## Verification Checklist

- [ ] `gh auth status` passes for the intended owner/admin account.
- [ ] Repo inventory includes visibility and archived state.
- [ ] Every public repo returns `{"limit":"collaborators_only", ...}` from `GET /repos/{owner}/{repo}/interaction-limits`.
- [ ] Private repo behavior is documented as visibility-gated / public-only API constraint.
- [ ] Tracking issue has a verification table.
- [ ] Renewal path exists before `expires_at`.
