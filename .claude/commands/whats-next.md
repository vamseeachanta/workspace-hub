---
type: prompt
name: whats-next
description: Pick 5 actionable GH issues for this machine and generate agent dispatch prompts
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
  - Write
  - Agent
---

<objective>
Identify 5 GitHub issues from workspace-hub that can be executed NOW on this machine ({{hostname}}),
then produce ready-to-paste agent prompts for each — one per terminal.

Output: ranked table of 5 issues + 5 fenced agent prompt blocks ready for dispatch.
</objective>

<process>

## Step 1 — Gather machine context

```bash
HOSTNAME=$(hostname)
```

Read the machine registry memory to understand what this host can do:
- `memory/user_workstation_topology.md` for machine roles
- Check available tooling: Python version, uv, conda envs, GPU, disk space, NFS mounts

```bash
python3 --version
uv --version 2>/dev/null
which conda 2>/dev/null && conda env list 2>/dev/null | head -10
ls /mnt/ace 2>/dev/null | head -5
df -h / /mnt/local-analysis 2>/dev/null | tail -2
nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo "No GPU"
```

## Step 2 — Fetch candidate issues from GitHub

Always fetch fresh (never cached). Pull open issues with useful metadata:

```bash
gh issue list --limit 100 --state open \
  --json number,title,labels,body,createdAt \
  | python3 -c "
import json, sys, re

issues = json.load(sys.stdin)
results = []
for iss in issues:
    labels = [l['name'] for l in iss.get('labels', [])]
    body = iss.get('body', '') or ''

    # Extract priority
    prio = 'none'
    prio_rank = 99
    for l in labels:
        if l == 'priority:critical': prio, prio_rank = l, 0
        elif l == 'priority:high': prio, prio_rank = l, 1
        elif l == 'priority:P1': prio, prio_rank = l, 1
        elif l == 'priority:medium': prio, prio_rank = l, 2
        elif l == 'priority:low': prio, prio_rank = l, 3

    # Extract Machine: field from body (if present)
    machine_match = re.search(r'\*\*Machine:\*\*\s*(.+)', body)
    machines = machine_match.group(1).strip() if machine_match else ''

    # Skip issues claimed by any machine (wip:* label)
    if any(l.startswith('wip:') for l in labels):
        continue

    # Extract categories
    cats = [l for l in labels if l.startswith('cat:') or l.startswith('domain:')]

    results.append({
        'number': iss['number'],
        'title': iss['title'],
        'prio': prio,
        'prio_rank': prio_rank,
        'machines': machines,
        'cats': cats,
        'labels': labels,
        'body_len': len(body),
    })

# Sort: priority first, then issue number descending (newer first)
results.sort(key=lambda x: (x['prio_rank'], -x['number']))
for r in results:
    cats_str = ' '.join(r['cats'])
    print(f\"#{r['number']}|{r['title']}|{r['prio']}|{r['machines']}|{cats_str}\")
"
```

## Step 3 — Filter and rank for THIS machine

Apply these filters in order:

1. **Exclude claimed issues** — if any `wip:*` label is present, skip it (another machine is working on it).
2. **Exclude machine-locked issues** — if `Machine:` field exists and does NOT include
   this host's alias (dev-primary for ace-linux-1, dev-secondary for ace-linux-2), skip it.
3. **Exclude issues requiring licensed Windows software** (ANSYS, etc.) unless on a Windows host.
4. **Exclude issues in `archived` or `wontfix` state**.
4. **Prefer issues that are**:
   - Higher priority (critical > high > medium > low > none)
   - Self-contained (can complete in one agent session)
   - Research / integration / tooling / harness work (agent-friendly)
   - Have clear acceptance criteria in the body
5. **Diversity** — pick across categories, don't stack 5 identical "Integrate X library" issues.

Present a ranked table:

| # | Issue | Priority | Category | Why this machine |
|---|-------|----------|----------|------------------|
| 1 | #NNN: Title | high | cat:X | reason |
| ... | | | | |

## Step 4 — Read full issue bodies

For each of the 5 selected issues, fetch the full body:

```bash
gh issue view <NUMBER> --json number,title,body,labels
```

## Step 5 — Generate agent dispatch prompts

For each issue, produce a fenced code block that can be pasted directly into a new
Claude Code terminal on this machine. Each prompt must include:

```
## Agent Prompt — Issue #NNN: <title>

**Working directory:** /mnt/local-analysis/workspace-hub
**Issue:** https://github.com/vamseeachanta/workspace-hub/issues/NNN

### First action — claim the issue
gh issue edit NNN --add-label "wip:{{hostname}}"

### Context
<2-3 sentences summarizing the issue and any dependencies>

### Research phase (do this FIRST)
1. <online research task — what to search, what to evaluate>
2. <codebase research — what existing code/skills to check>

### Implementation scope
1. <numbered deliverable>
2. ...

### Standards
- Follow CLAUDE.md and .claude/rules/ conventions
- Commit with descriptive message referencing #NNN
- Push to main when done (single-session work)

### Last action — release the claim
gh issue edit NNN --remove-label "wip:{{hostname}}"

### Constraints
- Do NOT create new repos or branches for this work
- Do NOT modify unrelated files
- If blocked, comment on #NNN with what's needed and stop
```

## Step 6 — Terminal dispatch summary

End with a quick-reference block:

```
## Quick dispatch (copy each to a separate terminal)

Terminal 1: Issue #NNN — <short title>
Terminal 2: Issue #NNN — <short title>
Terminal 3: Issue #NNN — <short title>
Terminal 4: Issue #NNN — <short title>
Terminal 5: Issue #NNN — <short title>
```

</process>

<critical_rules>
- Agent prompts MUST include claim (`gh issue edit NNN --add-label "wip:<hostname>"`) as first action
  and release (`--remove-label`) as last action — this prevents other machines from picking the same issue
- ALWAYS fetch fresh from GitHub — never use cached issue data
- ALWAYS check machine capabilities before recommending compute-heavy issues
- Agent prompts must include a research phase FIRST (per user feedback)
- Each prompt must be self-contained — pasteable without extra context
- Respect machine field in issue bodies (dev-primary vs dev-secondary)
- Prefer diversity across categories over stacking similar issues
- Skip template issues (e.g., "[Template] Prospect")
- Skip issues that are clearly multi-day epics — prefer 1-session work
</critical_rules>
