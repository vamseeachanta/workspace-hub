---
title: Session Replay & Time Travel
description: >
  Record session state (tool calls, file diffs, WRK progress) at checkpoints to
  enable replay from any point. Supports debugging agent behavior, "what-if"
  exploration from mid-session, and training data for agent improvement.
version: "1.0"
module: platform
wrk_ref: WRK-181
status: parked
parked_until: "2026-05-24"
session:
  id: ""
  agent: claude-sonnet-4-6
review:
  required_iterations: 3
  current_iteration: 0
  status: pending
  reviewers:
    openai_codex:
      status: pending
      iteration: 0
      feedback: ""
    google_gemini:
      status: pending
      iteration: 0
      feedback: ""
    legal_sanity:
      status: pending
      iteration: 0
      violations: 0
  ready_for_next_step: false
progress: 0
created: "2026-02-24"
updated: "2026-02-24"
target_completion: "2026-05-24"
priority: low
tags:
  - session-lifecycle
  - replay
  - debugging
  - visionary
links:
  spec: specs/modules/session-replay-time-travel.md
  branch: ""
---

# Session Replay & Time Travel

> **Module**: platform | **Status**: parked (until 2026-05-24) | **Created**: 2026-02-24

## Summary

Record enough session state (tool calls, file diffs, WRK progress) to replay a
session from any checkpoint. Enables: (a) debugging agent behavior, (b) "what-if"
exploration from mid-session, (c) training data for agent improvement.

**Disposition**: Park until 2026-05-24. Agentic platforms (Claude Code, Codex CLI)
are actively building session management primitives; a custom implementation may be
superseded by May 2026. Revisit when the landscape is clearer.

---

## Context

The workspace-hub already records session signals in JSONL format:

- `state/session-signals/<timestamp>.jsonl` — tool invocations, WRK items touched
- `state/sessions/<uuid>.json` — delegation scores, session patterns
- `state/corrections/*.jsonl` — edit correction chains
- `state/pending-reviews/*.jsonl` — skill/ecosystem signals

What is missing is a **checkpoint** concept: a point-in-time snapshot sufficient to
resume or replay the session from that state. Current session logs are append-only
with no branching or restore capability.

---

## SME Discussion Required

- **Platform Architecture**: What granularity of replay? Tool-call level or task
  level? Tool-call replay is complete but large; task-level replay is coarser but
  more tractable.
- **All**: Privacy implications of recording full session transcripts? Session logs
  may contain client identifiers, API responses, or other sensitive context.
- **AI Operations**: How to use replay data for agent improvement without
  overfitting to a single agent's style?

---

## Design

### Checkpoint Record Format (JSONL extension)

Checkpoints extend the existing session-signals JSONL with a `checkpoint` event type:

```jsonl
{
  "ts": "2026-05-24T10:00:00Z",
  "event": "checkpoint",
  "checkpoint_id": "ckpt-abc123",
  "session_id": "00a600ff-...",
  "label": "after WRK-181 phase-1",
  "wrk_state": {
    "active": ["WRK-181"],
    "touched": ["WRK-181"],
    "percent_complete": {"WRK-181": 25}
  },
  "git_state": {
    "branch": "feature/wrk-181-session-replay",
    "head_sha": "abc1234",
    "dirty": false
  },
  "tool_call_count": 42,
  "file_diffs": [
    {
      "path": ".claude/work-queue/pending/WRK-181.md",
      "patch": "@@ -1,3 +1,4 @@\n ..."
    }
  ],
  "context_summary": "Implemented checkpoint save. Tests passing."
}
```

Key fields:
- `checkpoint_id` — unique ID, stable reference for replay
- `wrk_state` — which WRK items were active and their progress
- `git_state` — branch + HEAD SHA to reconstruct file state via `git checkout`
- `file_diffs` — incremental patches since last checkpoint (not full content)
- `context_summary` — AI-generated one-sentence state summary

### Checkpoint Store

```
state/checkpoints/
  <session-id>/
    index.jsonl          # one line per checkpoint, metadata only
    ckpt-<id>.jsonl      # full checkpoint record including diffs
```

### Replay Mechanism

Replay works by:
1. Starting from a git state (`git_state.head_sha`)
2. Applying `file_diffs` patches in sequence up to the target checkpoint
3. Restoring `wrk_state` (WRK percent_complete values)
4. Presenting the reconstructed state to the agent as context

"What-if" branching:
- From checkpoint N, create a new git branch
- Agent continues from that branch — original session history preserved

### Time Travel CLI

```
scripts/replay/replay.sh [options]

Options:
  --list                      List checkpoints for current or specified session
  --session <id>              Target session (default: latest)
  --checkpoint <id>           Replay to this checkpoint
  --what-if <checkpoint-id>   Branch from checkpoint, create new git branch
  --dry-run                   Show replay plan, do not apply
  --format [terminal|html]    Output format for replay viewer
```

---

## Phases

### Phase 1: Design session state capture format (extend existing JSONL)

- [ ] Define checkpoint record schema (extends `state/session-signals/` JSONL)
- [ ] Define checkpoint store layout (`state/checkpoints/<session-id>/`)
- [ ] Define diff capture strategy: whole-file vs. patch vs. git-based
- [ ] Prototype `scripts/replay/lib/capture.sh` — writes checkpoint on demand

### Phase 2: Implement checkpoint save/restore mechanism

- [ ] `scripts/replay/lib/save.sh` — capture checkpoint at current session state
- [ ] `scripts/replay/lib/restore.sh` — apply checkpoint diffs, restore WRK state
- [ ] `scripts/replay/lib/branch.sh` — create git branch from checkpoint for what-if
- [ ] Wire save as a PostToolUse hook (every N tool calls) + manual `/checkpoint`
- [ ] Guard: checkpoint only if `git_state.dirty == false` or explicit `--force`

### Phase 3: Build replay viewer (terminal-based or HTML report)

- [ ] `scripts/replay/viewer/terminal.sh` — ASCII timeline of checkpoints with diffs
- [ ] `scripts/replay/viewer/html.sh` — HTML report with expandable diff sections
- [ ] `scripts/replay/replay.sh` — main CLI integrating save/restore/viewer

### Phase 4: Integrate with git

- [ ] Each checkpoint maps to a git stash or lightweight tag
- [ ] Tag format: `replay/<session-id>/<checkpoint-id>`
- [ ] `scripts/replay/lib/git-bridge.sh` — create/list/delete replay tags
- [ ] Prune old replay tags on session close (configurable retention: default 30 days)

---

## Files to Create

| Action | File | Approx LOC |
|--------|------|------------|
| CREATE | `scripts/replay/replay.sh` | ~80 |
| CREATE | `scripts/replay/lib/capture.sh` | ~60 |
| CREATE | `scripts/replay/lib/save.sh` | ~80 |
| CREATE | `scripts/replay/lib/restore.sh` | ~100 |
| CREATE | `scripts/replay/lib/branch.sh` | ~50 |
| CREATE | `scripts/replay/lib/git-bridge.sh` | ~60 |
| CREATE | `scripts/replay/viewer/terminal.sh` | ~80 |
| CREATE | `scripts/replay/viewer/html.sh` | ~120 |
| MODIFY | `.claude/hooks/session-logger.sh` | +checkpoint trigger |
| MODIFY | `.claude/settings.json` | +PostToolUse checkpoint hook |

Total: ~700 LOC across 8 new files + 2 modifications.

---

## Risks & Open Questions

| Risk | Mitigation |
|------|------------|
| Checkpoint size growth | Store patches not full content; prune after 30 days |
| Platform supersedes custom replay | Park until May 2026 — reassess then |
| Privacy: full session content in diffs | Legal scan gate before any checkpoint commit |
| Interrupted checkpoint write | Atomic writes: `.tmp` → `mv` final; index written last |
| Git dirty state at checkpoint | Guard rejects unless `--force`; warn user |

---

## Cross-Review Process (MANDATORY)

> **REQUIREMENT**: Minimum **3 review iterations** with OpenAI Codex and Google Gemini
> before implementation. **Not started** — parked until 2026-05-24.

### Review Status

| Gate | Status |
|------|--------|
| Legal Sanity | pending |
| Iterations (>= 3) | 0/3 |
| OpenAI Codex | pending |
| Google Gemini | pending |
| **Ready** | false |

### Review Log

| Iter | Date | Reviewer | Status | Feedback Summary |
|------|------|----------|--------|------------------|
| 1 | — | Codex | Pending | |
| 1 | — | Gemini | Pending | |
| 2 | — | Codex | Pending | |
| 2 | — | Gemini | Pending | |
| 3 | — | Codex | Pending | |
| 3 | — | Gemini | Pending | |

---

## Progress

| Phase | Status | Notes |
|-------|--------|-------|
| Review Iteration 1 | Pending | Parked until 2026-05-24 |
| Review Iteration 2 | Pending | |
| Review Iteration 3 | Pending | |
| Plan Approved | Pending | |
| Phase 1: Capture Format | Pending | |
| Phase 2: Save/Restore | Pending | |
| Phase 3: Replay Viewer | Pending | |
| Phase 4: Git Integration | Pending | |

---

## Session Log

| Date | Session ID | Agent | Notes |
|------|------------|-------|-------|
| 2026-02-24 | — | claude-sonnet-4-6 | Spec created; WRK-181 parked until 2026-05-24 |
