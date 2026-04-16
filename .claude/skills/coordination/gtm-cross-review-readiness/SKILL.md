---
name: gtm-cross-review-readiness
description: Adversarial review workflow for GTM feature work before user approval — validate shipped artifacts, live URLs, public-facing collateral, and issue/body status drift.
version: 1.0.0
category: coordination
tags: [gtm, adversarial-review, approval, github, website, collateral]
related_skills:
  - coordination/agent-work-adversarial-review
  - development/code-reviewer
  - github/github-issues
---

# GTM Cross-Review Readiness

Use when GTM/demo/collateral work looks "done" and you need to decide what is actually ready for user review/approval.

This is not a normal status summary. The goal is to find approval blockers caused by public-facing defects, stale issue bodies, broken website links, or deployment claims that exceed reality.

## When to use
- User asks to review recent GTM feature work
- Demo/media/website issues were recently closed and you need approval readiness
- Tracker issue exists and may have drifted from shipped work
- Public collateral is involved (PDF/HTML/site pages/outreach assets)

## Core idea
A GTM stream can be technically complete but still not approval-ready if any of these are true:
1. public placeholders remain (`Texas #XXXXX`, dummy contacts, TODO links)
2. live website URLs 404 even though repo artifacts exist
3. built site links point to pages that are not actually generated
4. issue bodies still describe old blockers / wrong file paths / unchecked acceptance criteria
5. tracker issue is stale and no longer reflects what is shipped vs reviewed vs approved

## Workflow

### 1. Gather recent GTM signals
Check the main tracker and recently touched issues.

Example:
```bash
gh issue list --state all --limit 50 --search 'gtm OR demo OR capability OR methodology OR aceengineer.com' --json number,title,state,updatedAt,labels,url
for n in 2016 1809 2288 2116 2118 2087 2030 2035 2090 2095 2098 1669 191 117; do
  gh issue view $n --json number,title,state,labels,updatedAt,url,body,comments
done
```

Also inspect recent repo history in the implementation repos, not just workspace-hub.

Examples:
```bash
cd /mnt/local-analysis/workspace-hub/digitalmodel
git log --since='10 days ago' --date=iso --pretty=format:'%h%x09%ad%x09%s' --stat --no-merges -- examples/demos/gtm

cd /mnt/local-analysis/workspace-hub/aceengineer-website
git log --since='10 days ago' --date=iso --pretty=format:'%h%x09%ad%x09%s' --stat --no-merges -- content/demos assets/img/demos dist/demos
```

### 2. Audit public-facing collateral directly
Search for placeholders and over-claim language.

High-signal checks:
```bash
search_files pattern='Texas #XXXXX|TODO|TBD|\[LINK_|\[DATE_|\[TIME|support@|info@|1,292|methodology pages' path=/mnt/local-analysis/workspace-hub/docs/gtm target=content
```

Read the key files directly:
- `docs/gtm/capability-summary.md`
- `docs/gtm/capability-map.md`
- `docs/gtm/website-pages/*.html`
- outreach template files if they are being treated as approval candidates

Important distinction:
- placeholders inside explicit templates are usually non-blocking
- placeholders inside public-facing collateral are blockers

### 3. Validate live website state, not just repo state
If an issue claims publication/deployment, test the live URLs.

Example:
```bash
for u in \
  https://aceengineer.com/demos/ \
  https://aceengineer.com/methodology/compound-engineering \
  https://aceengineer.com/methodology/enforcement \
  https://aceengineer.com/methodology/orchestrator-worker \
  https://aceengineer.com/methodology/multi-agent-parity
  do printf '%s -> ' "$u"; curl -k -L -s -o /dev/null -w '%{http_code}\n' "$u"; done
```

Rule:
- repo-ready is not website-ready
- if live URLs 404, do not describe the work as published

### 4. Check built artifact integrity
Public gallery pages often link to files that exist in source but not in the built output.

Example pattern:
```bash
search_files pattern='jumper-installation\.html' path=/mnt/local-analysis/workspace-hub/aceengineer-website/content/demos target=content output_mode=content
test -f /mnt/local-analysis/workspace-hub/aceengineer-website/dist/demos/jumper-installation.html; echo $?
```

Rule:
- if a built page links to a missing built artifact, treat it as a blocker for approval

### 5. Reconcile issue bodies against reality
Look for these common drift modes:
- issue body still says work is blocked by an issue that is now closed
- issue body points to paths that were not actually used
- acceptance criteria remain unchecked despite shipped work
- issue was closed even though public-facing defects remain
- tracker issue still shows old critical path

Typical examples from GTM work:
- tracker still says GIFs are pending after GIF issue closed
- website issue says deliverable lives under `docs/gtm/website-pages/...` but real implementation landed in `aceengineer-website/content/...`
- outreach issue still references old file locations after collateral was consolidated elsewhere

### 6. Use adversarial subreviews when scope spans repos + GitHub + website
Split the audit into at least two independent pressures when possible:
1. artifacts / live website / collateral quality
2. issue hygiene / tracker truth / approval readiness

Ask each reviewer for:
- exact blockers
- exact file paths and line numbers
- whether item is blocking or follow-up
- whether it needs cross-review or direct fix

### 7. Produce an approval matrix
Use four buckets:
- Ready / mostly ready
- Needs fix before approval
- Needs issue/body reconciliation before approval
- Approve only with scoped note

This is more useful than a binary pass/fail.

## Recommended final output shape
1. Executive summary: "not yet approval-ready" or equivalent if blockers exist
2. Top 3 blockers with exact evidence
3. Verified live checks
4. Approval matrix by issue number
5. Highest-value next cleanup pass

## Practical heuristics learned
- A live 404 beats any optimistic issue comment
- A broken built-site CTA is a blocker even if the source page looks good
- Tracker issues become dangerous if they are not updated after rapid execution waves
- Closed issues can still be not approval-ready if their public artifacts contain placeholders or unverifiable claims
- Template placeholders are acceptable only when clearly template-scoped; not in public collateral

## Verification checklist
Before saying something is ready for user approval, confirm all of the below:
- live public URLs return expected status
- no fake/public placeholders remain in collateral
- built links resolve to built artifacts
- tracker issue reflects current shipped reality
- issue body / acceptance / comments do not materially contradict each other

## Suggested artifact
Write the result to a durable report like:
`docs/reports/YYYY-MM-DD-gtm-cross-review-readiness.md`
so it can be referenced in issue comments or user approval requests.
