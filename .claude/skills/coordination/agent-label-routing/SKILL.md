---
name: agent-label-routing
description: Deterministic multi-agent task assignment via GitHub labels — classify, label, and generate queue views from `agent:` labels instead of manual queue files
version: 1.0.0
category: coordination
type: skill
trigger: manual
auto_execute: false
capabilities:
  - agent_classification
  - batch_labeling
  - queue_generation
  - overnight_planning
tools: [terminal, gh]
scripts:
  - refresh-agent-work-queue.sh
---

# Agent Label Routing

Deterministic agent task assignment using GitHub `agent:` labels. Labels ARE the queue — separate markdown files are just filtered views.

## Label Schema

| Label | Color | Role |
|-------|-------|------|
| `agent:gemini` | F5A623 | Research, prep, large-doc ingestion, standards mapping |
| `agent:claude` | DA552F | Heavy coding, architecture, orchestration, complex TDD |
| `agent:codex` | 3182CE | Bounded implementation, test writing, review, refactoring |
| `agent:any` | 8E54E9 | No strong preference — whichever agent has capacity |

## Workflow

### Step 1: Create Labels (if missing)
```bash
gh label create "agent:gemini" --color "F5A623" --description "Research, prep, large-doc ingestion"
gh label create "agent:claude" --color "DA552F" --description "Heavy coding, architecture, orchestration"
gh label create "agent:codex" --color "3182CE" --description "Bounded implementation, tests, review"
gh label create "agent:any" --color "8E54E9" --description "No strong preference"
```

### Step 2: Classify Issues
Use rule-based scoring with keyword matching + category boosts:

```python
# GEMINI signals (+2 each)
keywords: literature, review, research, catalog, triage, summarize,
  standards gap, standards mapping, migrate literature, acquire, index,
  scrape, dedup, job market
category boost: cat:document-intelligence (+3), cat:data-pipeline + dark-intelligence (+2)

# CLAUDE signals (+2 each)
keywords: architecture, orchestration, governance, credit utilization,
  work queue, model switching, dispatch, integration, concept selection,
  capex/opex, facility sizing, production profile, floating platform,
  stability, gyradius, trim ballast, epic
category boost: cat:ai-orchestration (+3), cat:engineering + dark-intelligence (+1)

# CODEX signals (+2 each)
keywords: test coverage, bug fix, solver queue, extract metadata,
  batch-at-stop, config-protection hook, convert agent to skill,
  deduplicate skill, provider config
category boost: cat:engineering-calculations + domain:code-promotion (+2)
```

### Step 3: Batch Label (parallel)
Never use sequential `gh issue edit` — it is SLOW and hits rate limits.

**Parallel background shell (recommended):**
```bash
GEMINI=(1863 1862 1860 ... 68 issues)
for n in "${GEMINI[@]}"; do
  gh issue edit "$n" --add-label "agent:gemini" 2>/dev/null &
done
wait  # blocks until all complete, then move to next agent
```
175 issues labeled in ~15s vs 300s+ sequential.

**Alternative: one-liner per batch**
Same approach — background all `gh issue edit` calls for one agent, `wait`, then next.

### Step 4: Generate Queue View
```bash
# Query live from GitHub — never manually maintain
gh issue list -L 100 --label "agent:gemini,priority:high" --json number,title
gh issue list -L 100 --label "agent:claude,priority:high" --json number,title
gh issue list -L 100 --label "agent:codex,priority:high" --json number,title
```

### Step 5: Refresh Script
`scripts/refresh-agent-work-queue.sh` regenerates `notes/agent-work-queue.md` from live label queries. Run weekly on Sunday via cron.

## How to Reassign
```bash
# Move issue from Gemini to Codex
gh issue edit 1234 --remove-label "agent:gemini" --add-label "agent:codex"
```

### Provider Fallback / Reroute Pattern

When a routed agent cannot complete the assigned lane after work has started, preserve traceability and reroute instead of abandoning or silently switching providers.

Use `references/provider-reroute-traceability.md` for the detailed pattern. Minimum steps:

1. Preserve the original worktree, prompt, process/log path, and failure evidence.
2. Add an issue comment with the attempted provider, failure mode, artifact paths, and reroute decision.
3. Update only the `agent:` routing label (`--remove-label agent:<old> --add-label agent:<new>`); do not mutate lifecycle labels unless the plan gate actually changed.
4. Reuse the existing worktree/prompt context where safe, or write a fresh provider-specific prompt in `.planning/quick/`.
5. Verify the replacement agent's claimed writes with filesystem diff/tests before reporting success.

## Gemini Batch Execution Pattern

After labeling, execute research tasks in batches of 5-6 per Gemini session:

```bash
h-router-gemini -t terminal,file -q "You are ACE Engineer advance scout.
Working directory: /mnt/local-analysis/workspace-hub.
Execute ALL 5 tasks. Commit after each. Do NOT push. Close each issue.

TASK 1: <issue-title> (#number)
- Use search_files or terminal to gather data
- Create: <output path>
- Commit: git add <file> && git commit -m '<msg>'
- Close: gh issue close <number> -c '<close comment>'

TASK 2-5: same pattern...
"
```

- Each batch: ~2 minutes, closes 5 issues
- Toolsets: `-t terminal,file` for filesystem writes, add `web` for web search
- ~$0.00 consumed per batch from $20/mo Gemini Pro subscription
- Gemini handles search_files, read_file, write_file, terminal, gh CLI natively

## Pitfalls
- `gh issue list --json` outputs a JSON array, not newline-delimited JSON. Use `--jq` for clean output.
- Sequential `gh issue edit` hits API rate limits and is very slow. Always use background parallelism for bulk operations.
- The `gh` CLI may return exit 1 on error even for individual failures in parallel. Use `2>/dev/null` per call and `wait` to sync.
- Classification is heuristic — always review the output before bulk labeling. Some issues need manual override.
- Labels are the source of truth. Never manually edit the queue file without regenerating from labels.
- After Gemini sessions, verify files on disk with `ls -la` since sandbox isolation can sometimes prevent writes from persisting.
- Free providers (`h-nemotron`, `h-qwen`) timeout after 5 min — too short for 5+ task batches. Gemini via OpenRouter takes ~2 min per session of 5 tasks.

## Layered Kanban Flow Boards

When the user asks to review related GitHub issues and prepare a board for a flow such as **data layer → execution layer → result/output layer**, do not treat `agent:` labels as the only source of truth. Build a dependency-aware Kanban using issue metadata, parent/child links, plan state, and GitHub Project fields.

Use `references/layered-kanban-flow-routing.md` for the detailed pattern. Key guardrails:

- Classify each issue by flow layer and workflow gate/stage.
- Route Gemini to broad inventory/research/dedup work, Claude to architecture/orchestration/complex approved execution, and Codex to bounded implementation/tests/reporting/provenance.
- Prefer project fields plus a durable `docs/reports/YYYY-MM-DD-<topic>-kanban.md` artifact when the work is coordination/planning.
- Do not self-apply `status:plan-approved`, close issues, or mutate lifecycle labels just to populate the board.

## Output Artifacts
- GitHub issues with `agent:` labels applied, when label routing is explicitly part of the task
- GitHub Project fields/status updated, when preparing a workflow Kanban without lifecycle-label mutation
- `notes/agent-work-queue.md` (auto-generated view)
- `docs/reports/YYYY-MM-DD-<topic>-kanban.md` (layered Kanban flow report)
- `docs/plans/overnight-prompts-YYYY-MM-DD.md` (weekly overnight plan)
- `scripts/refresh-agent-work-queue.sh` (cron-ready refresh script)

## Session Record (2026-04-04 to 2026-04-05)
6 live Gemini sessions + 4 cron batches = 30+ research documents, 14 issues closed, ~12 min total compute, ~$0 from $20/mo Gemini Pro subscription. Sprint issues created for Claude (#1897 field dev, #1898 naval arch, #1899 governance) and Codex (#1908 test coverage).