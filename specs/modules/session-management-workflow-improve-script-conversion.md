---
title: Session Management Workflow & /improve Script Conversion
description: Document all start/stop hooks, create session lifecycle schematic, convert /improve to script-executable form
version: 1.0.0
module: workspace-hub
session:
  id: magical-snuggling-melody
  agent: claude-opus-4-6
review: ready
auth_approach: oauth_token_with_api_key_fallback
---

# Session Management Workflow & /improve Script Conversion

## Context

The workspace-hub has 8 stop hooks, 3 PreToolUse hooks, 3 PostToolUse hooks, and 3 PreCompact hooks — but no unified documentation of the session lifecycle. The `/improve` skill (v1.1.0) cannot run automatically because it's a Claude skill requiring an active session, and `claude -p` cannot be invoked from stop hooks (nested session error). We need:

1. A documented session management workflow with schematic
2. Convert `/improve` to a script that can run from a stop hook via Anthropic API (`curl`)

## Key Technical Findings

- **Stop hooks fire on BOTH `/exit` AND Ctrl+C** — same Stop event
- **Stop hooks run WITHIN the session context** — `claude -p` would hit nested session error
- **Anthropic API via `curl`** works from stop hooks (just HTTP, no nesting)
- **Phases 1, 3a, 4, 6, 7** of `/improve` are pure shell (no AI needed)
- **Phases 2, 3b, 5** need AI — use `curl` to Anthropic Messages API
- **`consume-signals.sh`** (358 LOC) is the closest existing pattern

## Deliverables (Split into 2 WRK Items)

### WRK-173: Session Management Workflow Documentation + Schematic
- Document all hooks across all 4 hook types
- Create session lifecycle schematic (ASCII + Mermaid)
- Pure documentation — no code changes
- **Tackle first** (prerequisite for WRK-174)

### WRK-174: /improve Script Conversion + Stop Hook Wiring
- Convert `/improve` to `scripts/improve/improve.sh` + `lib/`
- Wire as stop hook #9 in settings.json
- Update SKILL.md v1.1.0 → v1.2.0 (script dispatch)
- **Tackle second** (builds on WRK-173 documentation)

### Phase 1: Document Session Lifecycle

**File**: `.claude/docs/session-lifecycle.md`

Document all hooks in execution order:

#### Session Start (no hooks currently — document as gap)
- No Start hooks configured
- Session loads: CLAUDE.md, rules/, memory/MEMORY.md (auto-loaded)
- Statusline initializes from `statusline-command.sh`

#### During Session — PreToolUse (runs before EVERY tool call)
| # | Matcher | Script | Purpose | Latency |
|---|---------|--------|---------|---------|
| 1 | `.*` | `session-logger.sh pre` | Log tool activity to state/sessions/ | <5ms |
| 2 | `.*` | `propagate-ecosystem-check.sh` | Daily symlink validation | <10ms |
| 3 | `Write\|Edit\|MultiEdit` | inline echo | Show "Edit: <path>" notification | <1ms |

#### During Session — PostToolUse (runs after EVERY tool call)
| # | Matcher | Script | Purpose | Latency |
|---|---------|--------|---------|---------|
| 1 | `.*` | `session-logger.sh post` | Log post-execution | <5ms |
| 2 | `Write\|Edit\|MultiEdit` | inline echo | Show "Saved: <path>" | <1ms |
| 3 | `Write\|Edit\|MultiEdit` | `capture-corrections.sh` | Record edit patterns, detect correction chains | <50ms |

#### Context Compression — PreCompact
| # | Matcher | Script | Purpose |
|---|---------|--------|---------|
| 1 | `.*` | `session-memory/pre-compact-save.sh` | Persist active plan state |
| 2 | `manual` | inline echo | Delegation pattern reminder |
| 3 | `auto` | inline echo | Auto-compact context tips |

#### Session Exit — Stop (fires on `/exit`, Ctrl+C, timeout)
| # | Script | Purpose | Latency |
|---|--------|---------|---------|
| 1 | `session-memory/session-end-evaluate.sh` | Delegation scores, session patterns | ~2s |
| 2 | inline echo | Session timestamp marker | <1ms |
| 3 | `post-task-review.sh` | Learning checklist display | ~1s |
| 4 | `consume-signals.sh` | Process signals, generate briefing, draft WRK items | ~3s |
| 5 | `generate-resource-index.sh` | Refresh RESOURCE_INDEX.md | ~2s |
| 6 | `query-quota.sh --refresh --log` | AI quota snapshot | ~5s |
| 7 | `wrk-traceability-check.sh` | Warn if no WRK touched | <1s |
| 8 | `ecosystem-health-check.sh` | Skill/memory health signals | ~1s |
| 9 | **`improve.sh`** (NEW) | Run /improve autonomously | ~30-60s |

### Phase 2: Session Lifecycle Schematic

**File**: `.claude/docs/session-lifecycle-schematic.md`

ASCII/Mermaid diagram showing the full pipeline:

```
Session Start
  │
  ├── Load: CLAUDE.md, rules/, memory/MEMORY.md
  ├── Init: statusline-command.sh
  │
  ▼
┌─────────────────────────────────────────────┐
│  ACTIVE SESSION                             │
│                                             │
│  PreToolUse ──┐                             │
│    session-logger.sh (pre)                  │
│    propagate-ecosystem-check.sh             │
│    edit-notification (Write/Edit only)      │
│               │                             │
│  [Tool Executes]                            │
│               │                             │
│  PostToolUse ─┘                             │
│    session-logger.sh (post)                 │
│    save-notification (Write/Edit only)      │
│    capture-corrections.sh (Write/Edit only) │
│               │                             │
│  PreCompact (on context compression)        │
│    pre-compact-save.sh                      │
│    compaction reminders                     │
│                                             │
│  Signal Accumulation:                       │
│    state/sessions/*.jsonl                   │
│    state/corrections/*.jsonl                │
│    state/pending-reviews/*.jsonl            │
└─────────────────────────────────────────────┘
  │
  ▼  /exit OR Ctrl+C OR timeout
┌─────────────────────────────────────────────┐
│  STOP HOOKS (sequential)                    │
│                                             │
│  1. session-end-evaluate.sh    (~2s)        │
│  2. session timestamp          (<1ms)       │
│  3. post-task-review.sh        (~1s)        │
│  4. consume-signals.sh         (~3s)        │
│  5. generate-resource-index.sh (~2s)        │
│  6. query-quota.sh             (~5s)        │
│  7. wrk-traceability-check.sh  (<1s)        │
│  8. ecosystem-health-check.sh  (~1s)        │
│  9. improve.sh                 (~30-60s)    │
│     ├── Phase 1: Collect (shell)            │
│     ├── Phase 2: Classify (API call)        │
│     ├── Phase 3: Ecosystem Review (hybrid)  │
│     ├── Phase 4: Guard (shell)              │
│     ├── Phase 5: Apply (API call + write)   │
│     ├── Phase 6: Log (shell)                │
│     └── Phase 7: Cleanup (shell)            │
└─────────────────────────────────────────────┘
  │
  ▼
Session End
  state/improve-changelog.yaml updated
  state/pending-reviews/ archived
  state/session-briefing.md generated
```

### Phase 3: Convert `/improve` to Script

**File**: `scripts/improve/improve.sh` (~600 LOC)
**Supporting**: `scripts/improve/lib/` (shared functions)

#### Architecture: Hybrid Shell + Anthropic API

```
improve.sh
├── lib/
│   ├── collect.sh      # Phase 1: merge all JSONL signals
│   ├── classify.sh     # Phase 2: curl Anthropic API for classification
│   ├── ecosystem.sh    # Phase 3: filesystem checks + API analysis
│   ├── guard.sh        # Phase 4: size/dedup/no-clobber guards
│   ├── apply.sh        # Phase 5: API-generated content + file writes
│   ├── log.sh          # Phase 6: YAML changelog append
│   └── cleanup.sh      # Phase 7: archive + truncate signals
├── improve.sh          # Main orchestrator (~100 LOC)
└── README.md           # Usage docs
```

#### Phase Classification

| Phase | Shell | API | Notes |
|-------|-------|-----|-------|
| 1. COLLECT | 100% | 0% | Merge JSONL files with `jq` |
| 2. CLASSIFY | 10% | 90% | `curl` Anthropic API with structured prompt |
| 3. ECOSYSTEM REVIEW | 70% | 30% | Filesystem metrics (shell) + analysis (API) |
| 4. GUARD | 100% | 0% | File size, dedup, git status checks |
| 5. APPLY | 40% | 60% | API generates content, shell writes files |
| 6. LOG | 100% | 0% | Append YAML to changelog |
| 7. CLEANUP | 100% | 0% | Archive JSONL, truncate pending |

#### API Call Pattern (replaces `claude -p`)

```bash
call_anthropic_api() {
  local prompt="$1" max_tokens="${2:-2000}"
  local model
  model=$(yq -r '.latest_models.claude_balanced // "claude-sonnet-4-5-20250929"' \
    "$WORKSPACE_HUB/config/agents/model-registry.yaml" 2>/dev/null)

  local token
  token=$(jq -r '.claudeAiOauth.accessToken // empty' \
    ~/.claude/.credentials.json 2>/dev/null)

  # Fallback to ANTHROPIC_API_KEY env var
  local auth_header
  if [[ -n "$token" ]]; then
    auth_header="Authorization: Bearer $token"
  elif [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
    auth_header="x-api-key: $ANTHROPIC_API_KEY"
  else
    echo "SKIP: No API credentials available" >&2
    return 1
  fi

  curl -s "https://api.anthropic.com/v1/messages" \
    -H "Content-Type: application/json" \
    -H "$auth_header" \
    -H "anthropic-version: 2023-06-01" \
    -d "$(jq -n \
      --arg model "$model" \
      --arg prompt "$prompt" \
      --argjson max_tokens "$max_tokens" \
      '{model: $model, max_tokens: $max_tokens,
        messages: [{role: "user", content: $prompt}]}')" \
    | jq -r '.content[0].text // empty'
}
```

#### Exit Behavior: Both `/exit` and Ctrl+C

- Stop hooks fire on **both** triggers (confirmed by exploration)
- All hooks use `2>/dev/null || true` wrapper — **safe on interrupt**
- `improve.sh` guards:
  - `set -euo pipefail` for strict error handling
  - Each phase checks if previous phase output exists before proceeding
  - Atomic writes: write to `.tmp` file, then `mv` to final location
  - Signal archival happens LAST (Phase 7) — interrupted run doesn't lose signals
  - If interrupted mid-API-call, signals remain in `pending-reviews/` for next run
- **Ctrl+C worst case**: API call times out, script exits, signals preserved for next session
- **`--quick` flag**: Skip API phases (2, 3b, 5) for fast exit — only run shell phases

### Phase 4: Wire into Stop Hook

**File**: `.claude/settings.json` — add as Stop hook #9 (after ecosystem-health-check)

```json
{
  "hooks": [
    {
      "type": "command",
      "statusMessage": "Running /improve",
      "command": "bash -c 'SCRIPT=\"${WORKSPACE_HUB:-...}/scripts/improve/improve.sh\"; [ -f \"$SCRIPT\" ] && bash \"$SCRIPT\" 2>/dev/null || true'"
    }
  ]
}
```

### Phase 5: Update SKILL.md to dispatch to script

**File**: `.claude/skills/workspace-hub/improve/SKILL.md` — v1.1.0 → v1.2.0

Add to the skill:
- When invoked manually (`/improve`), run in Claude session (current behavior, full AI reasoning)
- When invoked from stop hook, dispatch to `scripts/improve/improve.sh` (script mode, API calls)
- Script mode uses `--quick` flag on Ctrl+C (skip API phases), full mode on `/exit`

## Files to Create/Modify

| Action | File | LOC |
|--------|------|-----|
| CREATE | `.claude/docs/session-lifecycle.md` | ~120 |
| CREATE | `.claude/docs/session-lifecycle-schematic.md` | ~80 |
| CREATE | `scripts/improve/improve.sh` | ~100 |
| CREATE | `scripts/improve/lib/collect.sh` | ~80 |
| CREATE | `scripts/improve/lib/classify.sh` | ~120 |
| CREATE | `scripts/improve/lib/ecosystem.sh` | ~100 |
| CREATE | `scripts/improve/lib/guard.sh` | ~60 |
| CREATE | `scripts/improve/lib/apply.sh` | ~150 |
| CREATE | `scripts/improve/lib/log.sh` | ~40 |
| CREATE | `scripts/improve/lib/cleanup.sh` | ~30 |
| MODIFY | `.claude/settings.json` | +8 lines |
| MODIFY | `.claude/skills/workspace-hub/improve/SKILL.md` | +15 lines |
| CREATE | `.claude/work-queue/pending/WRK-173.md` | ~30 |

## Verification

1. **Test `improve.sh` standalone**: `bash scripts/improve/improve.sh --dry-run`
2. **Test Ctrl+C resilience**: Start `improve.sh`, Ctrl+C during API call, verify signals preserved
3. **Test stop hook**: End a session, verify `improve.sh` runs in stop hook output
4. **Test `--quick` mode**: `bash scripts/improve/improve.sh --quick` (no API calls)
5. **Verify schematic**: Read `.claude/docs/session-lifecycle-schematic.md` matches actual hooks
6. **Signal preservation**: After interrupted run, signals remain in `pending-reviews/`
