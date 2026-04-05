---
name: hermes-workflow-audit
description: Systematic audit pattern for Hermes workflow health — cross-review compliance, document intelligence state, resource intelligence maturity, session governance, and pipeline status.
version: 1.0.0
tags: [hermes, workflow, audit, cross-review, document-intelligence, session-governance]
---

# Hermes Workflow Audit Pattern

## When to Use

- User asks "what's going on with our workflow?" or "are reviews happening?"
- Investigating why code quality has degraded
- Periodic health check (weekly/biweekly)
- Before making workflow changes — establish baseline
- After major repo changes — verify systems still functioning
- When user asks to "document findings" for later action

## Audit Checklist

### 1. Cross-Review Compliance

```bash
# Check review artifacts timestamp
ls -lt scripts/review/results/ | head -5

# Count commits since last review
LAST_REVIEW_DATE=$(ls -t scripts/review/results/*.md 2>/dev/null | head -1 | grep -oP '\d{4}-\d{2}-\d{2}' | head -1)
git log --oneline --since="$LAST_REVIEW_DATE" 2>/dev/null | wc -l
echo "Commits since last review ($LAST_REVIEW_DATE)"

# Check enforcement scripts
cat scripts/enforcement/require-cross-review.sh | grep -A5 "mode"
```

Red flags: >50 commits without review, review artifacts older than 7 days, enforcement in warning mode.

### 2. Document Intelligence State

```bash
# Check index health
wc -l data/document-index/index.jsonl
python3 -c "
import json
total=summaries=0
for line in open('data/document-index/index.jsonl'):
    total+=1
    d=json.loads(line)
    if d.get('summary_done'): summaries+=1
print(f'{total} records, {summaries} summarized ({summaries/total*100:.1f}%)')
"

# Check maturity tracker
cat data/document-index/resource-intelligence-maturity.yaml | grep -E "generated|summary|documents"

# Check standards ledger
wc -l data/document-index/standards-transfer-ledger.yaml
```

⚠️ CRITICAL BUG (found Apr 5, 2026): index.jsonl can appear to have 0% summary_done and all "unknown" content_type even when summaries exist elsewhere (the 1M+ record dataset has 61.9% coverage). The summary data may be stored in a parallel index or separate location — don't trust the active index.jsonl metadata blindly. Check resource-intelligence-maturity.yaml for the authoritative summary coverage number.

### 3. Session Governance

```bash
# Session volume and depth
ls ~/.hermes/sessions/session_*.json 2>/dev/null | wc -l
python3 -c "
import json,glob,os
files=glob.glob(os.path.expanduser('~/.hermes/sessions/session_*.json'))[-30:]
depths=[]
for f in files:
    d=json.load(open(f))
    tc=sum(len(m.get('tool_calls',[])) for m in d.get('messages',[]) if m.get('role')=='assistant')
    depths.append(tc)
print(f'Avg: {sum(depths)/len(depths):.0f}, Max: {max(heights)}')
"

# Check invocation patterns
grep -E '^hermes|^h-' ~/.bash_history 2>/dev/null | sort | uniq -c | sort -rn | head -10

# Check gateway
hermes gateway status
hermes cron list
```

### 4. Pipeline Health

```bash
# Cron health check
bash scripts/monitoring/cron-health-check.sh 2>&1 | grep -E "ERROR|STALE|MISSING"

# Check recent error patterns
tail -20 ~/.hermes/logs/errors.log 2>/dev/null | grep -iE "429|401|403|error"
```

## Key Findings to Report

1. Cross-review: days since last review, commits since, enforcement mode
2. Document Intelligence: index health, summary coverage, recent activity
3. Resource Intelligence: maturity %, days since last update, domain gaps
4. Session Governance: avg/max tool calls, dangerous invocation patterns (--yolo)
5. Known bugs: index metadata loss, missing skills, gateway issues

## Pitfalls

- `index.jsonl` may have lost metadata during regeneration — cross-reference with resource-intelligence-maturity.yaml
- Resource maturity YAML says "documents in scope: 5" but markdown says "documents in scope: X" — YAML is authoritative
- Hermes gateway may show "not running" even when PID is active — check with `ps aux | grep hermes`
- `hermes --yolo` bypasses ALL dangerous command prompts — common but risky
- Cross-review scripts exist but default to WARNING not BLOCKING — the existence of scripts doesn't mean enforcement
- Hard-stop policy at docs/standards/HARD-STOP-POLICY.md gates ONLY engineering-critical issues (cat:engineering*, cat:data-pipeline). Non-critical issues skip gate.
- CRITICAL: `python3` in audit scripts should be `uv run python` — user corrected this pattern
- Gate order: Issue → Plan → USER APPROVES → Implement → Cross-review → Close (plan review BEFORE implementation, not after)
- 542 commits went through with ZERO reviews between Mar 24 and Apr 5 — this is the gap to detect