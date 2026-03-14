# WRK-1200: Strategic Prioritization Skill

## Context

The workspace has ~450 WRK items. Without strategic filtering, harness/tooling work absorbs all capacity while engineering modules (CP, fatigue, hydrodynamics, energy data) — the actual O&G industry value — stagnate. This skill encodes visionary product thinking (Jobs, Musk, Bezos, Grove) into a deterministic scoring engine that answers: "What moves the needle most?"

## Design Decisions

1. **Hybrid WSJF + RICE scoring**: WSJF for items with deadlines/`blocked_by` chains (captures time criticality + enablement). RICE for open backlog (majority of items). Both normalized to 0-100.
2. **`track:` field maps FROM `category:`**: No backfill needed. Deterministic mapping table. WRKs can override with explicit `track:` in frontmatter.
3. **Composable Python scripts**: `strategic-score.py` (rank all), `strategic-classify.py` (classify one), `strategic-brief.sh` (display). Each independently testable.
4. **Phase 1 is standalone**: Scoring engine + CLI brief. No skill wiring yet. Immediately useful via `bash scripts/strategic/strategic-brief.sh`.

## Scoring Formula

```
base_score = has_deadline_or_blocked_by ? wsjf_normalized : rice_normalized
track_penalty = (actual_track_pct - target_track_pct) * 0.5
strategic_score = base_score - track_penalty + roadmap_bonus(15) + enablement_bonus(10/dep, cap 30)
```

Track balance = working + archived(30d) items per track vs targets: **harness 20%, engineering 50%, market 20%, other 10%**.

## Phase 1: Core Scoring Engine (this WRK)

### New Files (6)

| # | File | Purpose |
|---|------|---------|
| 1 | `config/strategic-prioritization/track-mapping.yaml` | category → track mapping table |
| 2 | `config/strategic-prioritization/scoring-weights.yaml` | RICE/WSJF weights, track targets, bonuses |
| 3 | `scripts/strategic/strategic-score.py` | Core engine: parse all WRKs, score, rank, output YAML |
| 4 | `scripts/strategic/strategic-classify.py` | Classify single WRK (used at capture + triage) |
| 5 | `scripts/strategic/strategic-brief.sh` | Terminal display: track balance bars + top items table |
| 6 | `.claude/skills/workspace-hub/strategic-prioritization/SKILL.md` | Skill definition + invocation docs |

### Test Files (TDD — written first)

| # | File | Tests |
|---|------|-------|
| 1 | `tests/strategic/test_strategic_score.py` | 16 tests: frontmatter parsing, track classification, RICE/WSJF scoring, enablement bonus, track balance, full ranking |
| 2 | `tests/strategic/fixtures/WRK-TEST-*.md` | 6 fixture WRKs with known categories/priorities/blocked_by for deterministic test assertions |

### Key Functions in `strategic-score.py`

- `parse_wrk_frontmatter(path) → dict` — extract YAML frontmatter
- `classify_track(category, mapping) → str` — category → track
- `score_rice(wrk, weights) → float` — Reach×Impact×Confidence / Effort
- `score_wsjf(wrk, weights) → float` — CoD / Job Size
- `calculate_enablement(wrk_id, all_wrks) → int` — count downstream blocked items
- `calculate_track_balance(working, archived_30d, targets) → dict` — actual vs target per track
- `apply_bonuses(base, wrk, critical_ids, enablement, balance) → float` — final score
- `main()` — orchestrator, outputs YAML

### Output Schema (`strategic-brief` YAML)

```yaml
generated_at: "2026-03-14T10:00:00Z"
track_balance:
  harness: {target_pct: 20, actual_pct: 35, status: over_served, delta: 15}
  engineering: {target_pct: 50, actual_pct: 30, status: under_served, delta: -20}
  market: {target_pct: 20, actual_pct: 10, status: under_served, delta: -10}
ranked_items:
  - id: WRK-376
    track: engineering
    strategic_score: 87.5
    score_breakdown: {base: 72.5, roadmap: 15, enablement: 10, track_penalty: -10}
    scoring_method: rice
top_3_by_track:
  harness: [WRK-xxx, ...]
  engineering: [WRK-aaa, ...]
  market: [WRK-ddd, ...]
recommendation:
  next_item: WRK-376
  rationale: "Engineering under-served by 20pp. Roadmap critical path. Enables WRK-379."
```

## Phase 2: Integration (future WRK)

| Integration Point | Target File | Change |
|---|---|---|
| session-start Step 4b | `session-start/SKILL.md` | Call `strategic-brief.sh --top 3` after whats-next |
| whats-next `--sort-by strategic` | `scripts/work-queue/whats-next.sh` | New flag, reorders MED_UNBLOCKED by score |
| `/work add` post-capture | `work-queue/SKILL.md` capture section | Call `strategic-classify.py` to set `track:` |
| Stage 3 triage | `stage-03-triage.yaml` | New exit artifact `triage-scoring.yaml` |

## Phase 3: Track Balance Reporting (future WRK)

| Integration Point | Target | Change |
|---|---|---|
| `/today --eod` | `today/SKILL.md` | Track balance section in wrap-up |
| `/reflect` | `claude-reflect/SKILL.md` | Phase 5: WRK bottleneck analysis |
| Stage 15 future work | `work-queue-workflow` | Pre-classify follow-ups with `strategic-classify.py` |
| Feature decomposition | Stage 7 exit | Score children, front-load demo-able |

## Build Sequence

1. Write test fixtures (`tests/strategic/fixtures/WRK-TEST-*.md`)
2. Write test suite (`tests/strategic/test_strategic_score.py`) — all 16 tests RED
3. Write config files (`config/strategic-prioritization/*.yaml`)
4. Implement `strategic-score.py` — make tests GREEN
5. Implement `strategic-classify.py`
6. Implement `strategic-brief.sh`
7. Write SKILL.md
8. Run full suite, verify end-to-end with real pending WRKs

## Verification

```bash
# TDD tests
uv run --no-project python -m pytest tests/strategic/ -v

# Manual end-to-end
bash scripts/strategic/strategic-brief.sh --top 5

# Classify single item
uv run --no-project python scripts/strategic/strategic-classify.py WRK-1200

# Full scoring output
uv run --no-project python scripts/strategic/strategic-score.py --top 10
```

## Reused Patterns

- `scripts/coordination/routing/lib/task_classifier.sh` — weighted multi-dimension scoring pattern
- `scripts/work-queue/whats-next.sh` — box-drawing terminal table format
- Reflect skill's 4-factor weighted model — scoring architecture pattern
