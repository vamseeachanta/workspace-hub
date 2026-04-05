---
name: workflow-compliance-audit
description: Systematic audit of whether agents are following established workflows — cross-review, plan approval, TDD compliance, and document intelligence status.
category: coordination
triggers:
  - When asked to review current workflow compliance across agents
  - When checking if cross-review or plan review is actually happening
  - When auditing engineering work against established process standards
  - Before closing workflow governance issues to verify adherence
version: 1.0.0
---

# Workflow Compliance Audit

Audit whether agents are following established workflows (plan review, cross-review, TDD, document intelligence) by examining git history, review artifacts, session data, and intelligence pipelines.

## What Gets Audited

| Area | What to Check | Evidence Sources |
|------|-------------|------------------|
| **Cross-Review** | Are engineering commits getting reviewed? | `scripts/review/results/`, git log |
| **Plan Review** | Are plans written and approved before implementation? | Issue comments, `.planning/` files |
| **TDD Compliance** | Are tests written before implementation? | Commit order, test file timestamps |
| **Doc Intelligence** | Is the document index healthy and current? | `data/document-index/index.jsonl`, `standards-transfer-ledger.yaml` |
| **Resource Intelligence** | Is the resource maturity tracker being updated? | `data/document-index/resource-intelligence-maturity.yaml` |
| **Session Governance** | Any runaway sessions, bypass patterns? | Session logs, bypass logs |

## Audit Procedure

### 1. Cross-Review Status

Check `scripts/review/results/` for recent artifacts:
```
ls -lt scripts/review/results/ | head -15
```
- Find the date of the most recent review artifact
- Count engineering commits since that date
- Calculate review compliance rate: reviews / engineering_commits

**Engineering commits** = commits with `feat:`, `fix:`, `refactor:` prefixes that touch `digitalmodel/`, `worldenergydata/`, `assetutilities/`, or have `cat:engineering` labels.

### 2. Plan Review Compliance

Check if engineering issues had plans before implementation:
```
gh issue list --state open --label cat:engineering --json number,title | python3 -c "..."
```
- For recent engineering commits, check if the referenced issue had a plan comment before the implementation commit date
- Check `.planning/` for phase plans that were approved

### 3. Document Intelligence Health

Check the primary index file:
```
wc -l data/document-index/index.jsonl
python3 -c "import json; d=json.loads(open('data/document-index/index.jsonl').readline()); print(d.get('summary_done'), d.get('content_type'))"
```
- Total records count
- Sample a few records - check if `summary_done` and `content_type` fields are populated
- **GOTCHA if all records show `content_type: "unknown"` and `summary_done: false`**: The index metadata has been wiped/regenerated. The summary data lives elsewhere. Use `online-resource-registry.yaml` and `standards-transfer-ledger.yaml` as reliable sources instead.
- Conference papers indexed? Check `conference-index-batch.jsonl`

### 4. Resource Intelligence Status

Read `data/document-index/resource-intelligence-maturity.yaml`:
- Documents marked read: count and percentage
- Target: typically >80% within 3 months
- Key calculations implemented: list with percentages
- Check the `generated` field — is the tracker being updated or is it stale?

### 5. Bypass Pattern Analysis

Check for agents bypassing established gates:
```
grep -r "SKIP_REVIEW_GATE\|GIT_PRE_PUSH_SKIP\|skip.*plan\|bypass" logs/ docs/handoffs/ 2>/dev/null
```
- Count bypass events
- Check if bypasses are justified or habitual

## Expected Output

Structured audit report with:
- **Status**: HEALTHY | WARNING | CRITICAL for each area
- **Evidence**: Specific dates, commit hashes, file paths
- **Trend**: Improving | Stable | Declining (if historical data available)
- **Action Items**: What needs fixing

## Example Finding Format

```
## Cross-Review: CRITICAL
Last review artifact: Apr 2 (one Codex retroactive review)
Prior review cluster: Mar 24
542 commits since reviews stopped
Compliance rate: ~0.2%
```

## Pitfalls

- **Session signals directory**: `.claude/state/session-signals/` may have stale data. The `check_claude_usage.sh` script may never have run, so generated log files don't exist.
- **Hermes sessions**: Not tracked in the same way as Claude sessions. Check `~/.hermes/sessions/` for Hermes-specific data.
- **Auto-sync noise**: `chore(sync): auto-sync` commits inflate total commit counts. Filter these out.
- **Review artifacts vs review execution**: Having review files in `scripts/review/results/` doesn't mean the review was performed — check file sizes and content. Some artifacts are empty or contain only error messages.
- **Document index vs registry**: The index.jsonl is NOT the same as the online-resource-registry.yaml or standards-transfer-ledger.yaml. The index tracks all documents (647K+), while registries track specific collections.
- **Resource maturity YAML vs Markdown**: The YAML is authoritative, the Markdown is generated. Always check the YAML for current state.

## Related

- `engineering-issue-workflow` skill — the workflow being audited
- `hermes-workflow-audit` — cron and agent health specifically
- Issue #1839 — workflow hard-stops and session governance
- Issue #1515 — AI review routing policy
