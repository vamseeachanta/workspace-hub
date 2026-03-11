# Skill Knowledge Map — WRK-624 Governance Skill Set

**Produced by:** WRK-1010 Stage 10 (Work Execution)
**Date:** 2026-03-10
**Scope:** 8 skills assessed for WRK-624 workflow governance review

---

## DAG — Skill Dependency and Handoff Flow

```
                        ┌─────────────────────────┐
                        │      session-start        │
                        │  (session entry point)    │
                        └────────────┬────────────-─┘
                                     │ hands off to
                                     ▼
                        ┌────────────────────────────┐
                        │    work-queue-workflow      │
                        │  (lifecycle entrypoint)    │
                        └──┬──────────┬─────────────-┘
                           │          │
              delegates to │          │ delegates to
                           ▼          ▼
              ┌────────────────┐   ┌──────────────────────┐
              │   work-queue   │   │   workflow-gatepass   │
              │ (queue ops,    │   │  (gate enforcement,   │
              │  20-stage ref) │   │   stage contracts)    │
              └──┬─────────────┘   └──────────┬───────────┘
                 │                             │
       triggers  │                  requires   │
                 ▼                             ▼
  ┌──────────────────────┐      ┌──────────────────────────┐
  │  resource-intelligence│      │  wrk-lifecycle-testpack  │
  │  (Stage 2 + 16 only)  │      │  (TDD harness for gate   │
  └──────────────────────┘      │   compliance; used when  │
                                 │   workflow code changes)  │
                                 └──────────────────────────┘

  Stage 6 / 13 (cross-review) — inline in work-queue-workflow/SKILL.md:
  ┌─────────────────────────────────────────────────────┐
  │  cross-review (no standalone file)                  │
  │  Triggered from: work-queue §Cross-Review           │
  │  and work-queue-workflow §Stage 6                   │
  └─────────────────────────────────────────────────────┘

  Post-archive learning path:
  ┌──────────────┐    triggers   ┌──────────────────────────┐
  │  work-queue  │ ─────────────▶│  comprehensive-learning  │
  │  (Stage 20   │               │  (nightly / session-end) │
  │   archive)   │               └──────────────────────────┘
  └──────────────┘
```

**Reading the DAG:**
- `session-start` is the mandatory entry gate; it hands off to `work-queue` (via `/work` command)
  for item selection and execution — NOT directly to `work-queue-workflow` (corrected per
  session-start/SKILL.md §Step 3 which calls `/work run`, routing through work-queue).
- `work-queue-workflow` is the start-to-finish entrypoint that delegates execution policy
  to `work-queue` (data model, scripts) and gate enforcement to `workflow-gatepass`.
- `resource-intelligence` is a stage-scoped sub-skill invoked at Stages 2 and 16 only.
- `wrk-lifecycle-testpack` is invoked when implementing or validating workflow compliance code,
  not during every WRK lifecycle run.
- `cross-review` has no standalone SKILL.md; its protocol lives inline in `work-queue`
  §Cross-Review and `work-queue-workflow` §Stage 6.
- `comprehensive-learning` sits outside the main execution loop; it harvests learnings
  post-archive and is cron-safe (not called from within a WRK's live execution).

---

## Per-Skill Boundary Table

### 1. work-queue

| Field | Content |
|-------|---------|
| **Triggers** | `/work add`, `/work run`, `/work list`, `/work status`, `/work archive`, `/work report`; smart routing: action verbs → Process, descriptive content → Capture |
| **Inputs** | User description (capture); `.claude/work-queue/` directory state; `checkpoint.yaml` (resume); `INDEX.md` (list); WRK frontmatter (status/routing) |
| **Outputs** | New WRK-NNN files in `pending/`; queue state mutations (`working/`, `done/`, `archive/`); `checkpoint.yaml`; lifecycle HTML; `INDEX.md` updates; stage exit artifacts per stage contract table |
| **Handoffs** | → `work-queue-workflow` for full lifecycle; → `workflow-gatepass` for gate enforcement; → `resource-intelligence` at Stage 2; → `session-start` at session init; → `comprehensive-learning` post-archive |
| **Negative scope** | Does NOT define gate enforcement rules (delegated to workflow-gatepass); does NOT run tests (delegated to wrk-lifecycle-testpack); does NOT define cross-review protocol beyond script invocation |

---

### 2. workflow-gatepass

| Field | Content |
|-------|---------|
| **Triggers** | "workflow gatepass", "wrk gate enforcement", "lifecycle gate", "close gate evidence"; invoked any time a WRK is being progressed or closed |
| **Inputs** | Active WRK item; evidence artifacts in `assets/WRK-NNN/evidence/`; `scripts/work-queue/verify-gate-evidence.py`; stage YAML contracts |
| **Outputs** | Enforcement decisions (pass/block); canonical no-bypass rule set; close-gate checklist (12 items); evidence location reference; reusable script table |
| **Handoffs** | → `session-start` (pre-condition); → `work-queue` (queue operations); → `wrk-lifecycle-testpack` (gate compliance testing); → `session-end` (close path) |
| **Negative scope** | Does NOT capture new WRK items; does NOT generate lifecycle HTML; does NOT mine resources; does NOT run cross-reviews (describes the requirement, scripts do the work) |

---

### 3. wrk-lifecycle-testpack

| Field | Content |
|-------|---------|
| **Triggers** | "lifecycle testpack", "wrk workflow tests", "gatepass tests"; invoked when implementing or changing workflow gate logic |
| **Inputs** | `scripts/work-queue/verify-gate-evidence.py`; `scripts/review/orchestrator-variation-check.sh`; `scripts/work-queue/parse-session-logs.sh`; test data in WRK assets |
| **Outputs** | 6-test minimum suite spec; `execute.yaml` shape contract; `variation-test-results.md`; recommendation to add/update tests when gate contracts change |
| **Handoffs** | → `workflow-gatepass` (consumes gate contracts defined there); → `work-queue` (shares `parse-session-logs.sh` and `orchestrator-variation-check.sh`) |
| **Negative scope** | Does NOT enforce gates during live WRK execution; does NOT generate HTML; does NOT define what the gate rules are (that is workflow-gatepass's domain); does NOT run as part of every WRK's lifecycle — only when workflow code itself changes |

---

### 4. work-queue-workflow

| Field | Content |
|-------|---------|
| **Triggers** | "work-queue workflow", "wrk workflow", "/work workflow", "lifecycle workflow" |
| **Inputs** | `.claude/work-queue/process.md`; active WRK item; `work-queue` and `workflow-gatepass` SKILL.md content |
| **Outputs** | Start-to-finish orchestration chain; canonical terminology table (WRK session/stage/phase/step/checkpoint/resume); Stage Gate Policy table; Stage 4/5/6/10 detailed protocols; Plan-Mode gates table; Orchestrator Team Pattern; Source of Truth table |
| **Handoffs** | → `session-start` (Step 1 of chain); → `work-queue` (Step 2 — item selection); → `workflow-gatepass` (Step 4 — canonical lifecycle); → `workflow-html` for lifecycle HTML; "Source of Truth" table explicitly names all authoritative files |
| **Negative scope** | Does NOT maintain the queue data model; does NOT define gate enforcement rules (delegates to workflow-gatepass); does NOT run tests; explicitly says "do not use shortened lifecycle variants" |

---

### 5. comprehensive-learning

| Field | Content |
|-------|---------|
| **Triggers** | Session ends, nightly cron (22:00), user invokes `/comprehensive-learning`; "fire-and-forget" — not triggered mid-WRK |
| **Inputs** | `logs/orchestrator/` JSONL and plain-text session logs; `candidates/`, `corrections/`, `patterns/`, `session-signals/` state dirs; per-machine committed derived state |
| **Outputs** | Phase 1-9 outputs on all machines: insights, reflect, knowledge, patterns, memory compaction, action candidates, WRK items from candidates; Phase 10a/10 on ace-linux-1: cross-machine compilation report |
| **Handoffs** | → `/improve` (Phase 4); → `/reflect` (Phase 2); → `/knowledge` (Phase 3); → `/insights` (Phase 1); these sub-skills must NOT run standalone during sessions |
| **Negative scope** | Does NOT govern WRK lifecycle stages; does NOT enforce gates; does NOT run during live WRK execution; explicitly prohibits standalone sub-skills during sessions |

---

### 6. session-start

| Field | Content |
|-------|---------|
| **Triggers** | "session start", "start session", "morning briefing", "what should I work on", "session briefing", "startup check"; also triggered by first action of any session or after `/clear` |
| **Inputs** | `.claude/state/readiness-report.md`; `.claude/state/session-snapshot.md`; `config/ai-tools/agent-quota-latest.json`; `.claude/work-queue/INDEX.md`; `~/.claude/teams/` |
| **Outputs** | Session Briefing block (readiness, snapshot, quota, top items per category); computer context note; repo-map surface (when active WRK has target_repos); session collision audit result; mandatory /work handoff gate |
| **Handoffs** | → `work-queue` (mandatory /work handoff at Step 6); → `workflow-gatepass` (referenced as related skill); → `/improve` (referenced as related skill) |
| **Negative scope** | Does NOT execute work; does NOT define lifecycle stages; does NOT enforce WRK gates; does NOT run learning pipeline (deferred to comprehensive-learning / nightly) |

---

### 7. resource-intelligence

| Field | Content |
|-------|---------|
| **Triggers** | Manual; called at Stage 2 (Resource Intelligence) and Stage 16 (Resource Intelligence Update) of the WRK lifecycle |
| **Inputs** | WRK `## Mission`, `category`, `subcategory`, `target_repos`; 10-category Resource Mining Checklist; Category→Mining Map; `references/source-registry.md` |
| **Outputs** | Stage 2: `evidence/resource-intelligence.yaml` (gate-passing) + 7 companion artifacts (`resource-intelligence-summary.md`, `resource-pack.md`, `sources.md`, `constraints.md`, `domain-notes.md`, `open-questions.md`, `resources.yaml`); Stage 16: `evidence/resource-intelligence-update.yaml` + `stage-evidence.yaml` update |
| **Handoffs** | → `work-queue` (gate artifact consumed by `verify-gate-evidence.py`); explicit STOP guards at Stage 2 and Stage 16 to prevent bleed into planning |
| **Negative scope** | Does NOT do planning; does NOT define gate policy (that is workflow-gatepass); does NOT produce HTML; does NOT execute; hard STOP guards prevent advancing to Stage 3 or Stage 17 |

---

### 8. cross-review (inline — no standalone SKILL.md)

| Field | Content |
|-------|---------|
| **Triggers** | Invoked at Stage 6 (Plan Cross-Review) and Stage 13 (Agent Cross-Review) in the WRK lifecycle; triggered implicitly by `work-queue` §Cross-Review and `work-queue-workflow` §Stage 6 |
| **Inputs** | Review input file (plan or implementation); provider selection (Claude, Codex, Gemini); `scripts/review/cross-review.sh`; `scripts/review/submit-to-codex.sh`; `scripts/review/submit-to-gemini.sh` |
| **Outputs** | `cross-review-<provider>.md` per reviewer with Verdict (APPROVE/MINOR/REQUEST_CHANGES), Pseudocode Review section, Findings (P1/P2/P3); `variation-test-results.md` for orchestrator variation check |
| **Handoffs** | Codex is a HARD GATE; quota fallback: auto-substitutes Claude Opus when Codex exhausted or ≥2 Codex reviews already exist for this WRK |
| **Negative scope** | No standalone file — gap finding of this assessment. Does NOT define gate enforcement; does NOT generate HTML; cross-review is described across two skills with no single authoritative file |

---

## Structural Gap Finding

**cross-review has no SKILL.md.** Its protocol is duplicated (with slight variation) between:
- `work-queue/SKILL.md` §Cross-Review (Route B/C)
- `work-queue-workflow/SKILL.md` §Stage 6

This is a documentation gap — not a functional gap. A future WRK should extract this into
`.claude/skills/workspace-hub/cross-review/SKILL.md`.

---

*Map living doc: update when any of the 8 SKILL.md files changes. Trigger update via
comprehensive-learning Phase 6 (WRK Feedback + Ecosystem) or a dedicated maintenance WRK.*
