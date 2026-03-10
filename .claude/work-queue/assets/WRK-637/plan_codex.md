OpenAI Codex v0.112.0 (research preview)
--------
workdir: /mnt/local-analysis/workspace-hub
model: gpt-5.4
provider: openai
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR, /home/vamsee/.codex/memories]
reasoning effort: medium
reasoning summaries: none
session id: 019cd52b-0ca2-7ea2-9f08-3c7eb7d05968
--------
user
# Stance: Codex Plan Draft Review

You are a software engineer agent. Your focus is on **implementation correctness, edge cases, and testability**.

You will receive a Claude-authored plan draft. Walk it section-by-section and produce your own refined version.

When reviewing:
1. Challenge any assumptions about implementation approach — is there a simpler or more robust way?
2. Identify edge cases not covered (malformed input, missing fields, timezone/date math, quota exhaustion).
3. Flag AC gaps — things implementable but not covered by the listed tests.
4. Assess integration risks (nightly cron, file writes, CLI availability).
5. Verify uv run --no-project python is used wherever Python is called.

Your output must be a complete refined plan (same structure as the input draft).
Add a "Codex Notes" section at the end with your specific findings.

---
CLAUDE DRAFT PLAN:
# WRK-637 Plan Draft — Memory Governance: Compaction, Tiering, Eviction

**Route:** B (Medium) | **Computer:** ace-linux-1 | **Drafted:** 2026-03-09

---

## Mission

Build `scripts/memory/compact-memory.py` (and `curate-memory.py`) to enforce the memory
tier model, evict stale bullets, and integrate with comprehensive-learning Phase 3b/3c —
preventing context-rot in MEMORY.md and topic files.

---

## Plan

### Phase 1 — TDD Setup (tests first)

1. Create `tests/memory/` directory with `conftest.py` and fixtures
2. Write `tests/memory/test_compact_memory.py` covering:
   - `--dry-run` runs cleanly, outputs audit report, writes no files
   - Done-WRK eviction: bullet referencing closed WRK item moved to `archive/done-wrk.md`
   - Path staleness: bullet with non-existent path flagged to `archive/stale-paths.md`
   - `# keep` marker exempts bullet from age eviction
   - Compaction frees ≥10 lines from engineering-modules.md (currently 173L, over 150L limit)
   - Idempotency: second run on already-compacted file → zero evictions
   - `compact-log.jsonl` written with required fields (timestamp, lines_freed_memory, lines_freed_topics)
3. Write `tests/memory/test_curate_memory.py` covering:
   - Bullet classification (memory-keep / domain-doc / skill-update / archive)
   - Promotion candidate file written correctly
4. All tests RED before implementation begins

### Phase 2 — `compact-memory.py` implementation

File: `scripts/memory/compact-memory.py`

**Phase A — audit:**
- Resolve memory dir: `~/.claude/projects/*/memory/` (glob, pick active project)
- Parse MEMORY.md and all topic files (`*.md`, skip `archive/`)
- Apply eviction rules in order:
  1. Done-WRK expiry: grep bullet for `WRK-NNN`; check work-queue status; >30 days done → evict
  2. Path staleness: extract file paths from bullet; `os.path.exists()` check → flag
  3. Command staleness: spot-check 3 commands/run via `subprocess.run(timeout=5)` → flag
  4. Dedup: 80% overlap (token set ratio) between bullets in same file → keep fresher
  5. Age eviction: no session signal reference for 90+ days AND no `# keep` → evict
- Write `memory/compact-audit.md` (proposed actions, no mutations yet)

**Phase B — `--dry-run`:**
- Print audit to stdout; exit 0

**Phase C — apply:**
- Create `archive/` dir if missing
- Move evicted bullets to `archive/<category>.md`
- Rewrite topic files without evicted bullets
- Update MEMORY.md section pointers if topic files changed
- Append to `memory/compact-log.jsonl`: `{timestamp, lines_freed_memory, lines_freed_topics, bullets_evicted, bullets_archived}`

**Trigger check** (at script entry):
- MEMORY.md > 180L → run compaction
- Any topic file > 150L → run compaction
- `--force` flag bypasses trigger check

### Phase 3 — `curate-memory.py` implementation

File: `scripts/memory/curate-memory.py`

- Classify each bullet: `memory-keep | domain-doc | skill-update | archive`
- Write promotion candidates to `.claude/state/candidates/memory-promotion-candidates.md`
- Used by Phase 3c of comprehensive-learning (non-mandatory, log failure and continue)

### Phase 4 — Integration

- Verify comprehensive-learning SKILL.md Phase 3b entry is correct (script path matches)
- Verify pipeline-detail.md Phase 3b/3c entries reference correct script paths
- Update WRK-637.md frontmatter: `html_output_ref`, `plan_html_review_draft_ref`, `plan_html_review_final_ref`

---

## Test Strategy

| Test | Expected | Gate |
|------|----------|------|
| `--dry-run` on current memory files | audit report, no writes | PASS |
| Done-WRK eviction | WRK refs with status:done >30d moved to archive | PASS |
| Path staleness | ≥1 stale path flagged (current files have some) | PASS |
| Frees ≥10 lines | engineering-modules.md 173L → ≤150L | PASS |
| `# keep` exemption | kept bullets survive eviction pass | PASS |
| Idempotency | second run → 0 evictions | PASS |
| compact-log.jsonl | file exists, JSON valid, required fields present | PASS |

Minimum 3 PASS before Stage 10 closes.

---

## Acceptance Criteria Map

| AC | Phase | Test |
|----|-------|------|
| dry-run works | 2 | test_compact_memory::test_dry_run |
| done-WRK eviction | 2 | test_compact_memory::test_done_wrk_eviction |
| path staleness | 2 | test_compact_memory::test_path_staleness |
| ≥10 lines freed | 2 | test_compact_memory::test_lines_freed |
| MEMORY.md ≤180L after WRK-635 bulk scan | 2+4 | integration |
| `# keep` exemption | 2 | test_compact_memory::test_keep_exemption |
| comp-learning Phase 3b updated | 4 | manual verify |
| compact-log.jsonl | 2 | test_compact_memory::test_log_written |
| scan-sessions.py headroom check | 4 | WRK-635 integration (deferred) |

---

## Out of Scope

- WRK-635 `scan-sessions.py` implementation (separate WRK)
- Memory file content decisions (what to keep/evict) — only the governance mechanism
- curate-memory.py full Phase 3c integration (script only; cron wiring deferred)
- Memory quality eval harness (% stale, % verified, signal density, usage tracking) → spin off as WRK-638
mcp startup: no servers
codex
Using `work-queue-workflow`, `workflow-gatepass`, and `plan-mode` because this is WRK-scoped planning work. I’m checking the gate requirements and the active WRK context before refining the draft.
exec
/bin/bash -lc "sed -n '1,220p' .claude/skills/workspace-hub/work-queue-workflow/SKILL.md" in /mnt/local-analysis/workspace-hubexec
/bin/bash -lc "sed -n '1,220p' .claude/skills/workspace-hub/plan-mode/SKILL.md" in /mnt/local-analysis/workspace-hubexec
/bin/bash -lc "sed -n '1,260p' .claude/skills/workspace-hub/workflow-gatepass/SKILL.md" in /mnt/local-analysis/workspace-hub succeeded in 50ms:
---
name: plan-mode
description: >
  Invoke EnterPlanMode at deliberative WRK stages before writing any artifact.
  Prevents premature file writes during analysis and synthesis phases.
version: 1.0.0
updated: 2026-03-09
category: workspace-hub
triggers:
  - Stage 4 plan draft
  - Stage 6 cross-review
  - Stage 10 work execution
  - Stage 13 agent cross-review
related_skills:
  - workspace-hub/work-queue-workflow
  - superpowers/writing-plans
---
# Plan-Mode Gates

## When to Enter Plan Mode
 succeeded in 50ms:
---
name: workflow-gatepass
description: >
  Enforce WRK lifecycle gatepass from session start through close/archive with
  machine-checkable evidence requirements and explicit no-bypass rules.
version: 1.0.6
updated: 2026-03-07
category: workspace-hub
triggers:
  - workflow gatepass
  - wrk gate enforcement
  - lifecycle gate
  - close gate evidence
related_skills:
  - workspace-hub/session-start
  - coordination/workspace/work-queue
  - workspace-hub/session-end
  - workspace-hub/wrk-lifecycle-testpack
capabilities:
  - lifecycle-gate-enforcement
 succeeded in 50ms:
---
name: work-queue-workflow
description: >
  Explicit entrypoint skill for the WRK work-queue lifecycle workflow. Points to
  the canonical work-queue process and gatepass enforcement sequence.
version: 1.7.0
updated: 2026-03-08
category: workspace-hub
triggers:
  - work-queue workflow
  - wrk workflow
  - /work workflow
  - lifecycle workflow
related_skills:
  - coordination/workspace/work-queue
  - workspace-hub/workflow-gatepass
  - workspace-hub/workflow-html
  - workspace-hub/session-start
  - workspace-hub/session-end
capabilities:
exec
/bin/bash -lc "rg --files .claude/work-queue | rg 'WRK-637|INDEX.md'" in /mnt/local-analysis/workspace-hub succeeded in 394ms:
.claude/work-queue/INDEX.md
.claude/work-queue/pending/WRK-637.md
.claude/work-queue/assets/WRK-637/WRK-637-lifecycle.html
.claude/work-queue/assets/WRK-637/workflow-final-review.html
.claude/work-queue/assets/WRK-637/stage-4-prompt.md
.claude/work-queue/assets/WRK-637/stage-3-prompt.md
.claude/work-queue/assets/WRK-637/stage-2-prompt.md
.claude/work-queue/assets/WRK-637/plan_gemini.md
.claude/work-queue/assets/WRK-637/plan_codex.md
.claude/work-queue/assets/WRK-637/plan-draft.md
.claude/work-queue/assets/WRK-637/checkpoint.yaml
.claude/work-queue/assets/WRK-637/evidence/user-review-plan-draft.yaml
.claude/work-queue/assets/WRK-637/evidence/user-review-common-draft.yaml
.claude/work-queue/assets/WRK-637/evidence/user-review-capture.yaml
.claude/work-queue/assets/WRK-637/evidence/stage-evidence.yaml
.claude/work-queue/assets/WRK-637/evidence/session-lock.yaml
.claude/work-queue/assets/WRK-637/evidence/resource-intelligence.yaml
codex
The WRK item and prior stage artifacts exist, so this can stay within Stage 5/6 planning review without touching repo state. I’m reading the WRK record and current draft artifacts to tighten the plan against actual integration points.
exec
/bin/bash -lc "sed -n '1,240p' .claude/work-queue/pending/WRK-637.md" in /mnt/local-analysis/workspace-hubexec
/bin/bash -lc "sed -n '1,260p' .claude/work-queue/assets/WRK-637/plan-draft.md" in /mnt/local-analysis/workspace-hubexec
/bin/bash -lc "sed -n '1,260p' .claude/work-queue/assets/WRK-637/plan_codex.md" in /mnt/local-analysis/workspace-hub succeeded in 51ms:
---
id: WRK-637
title: "feat(memory): memory governance — compaction, tiering, eviction to prevent context-rot"
status: pending
priority: high
complexity: medium
compound: false
created_at: 2026-02-27T00:00:00Z
target_repos:
  - workspace-hub
commit:
spec_ref:
related:
  - WRK-635
  - WRK-636
  - WRK-299
blocked_by: []
parent:
synced_to: []
plan_reviewed: false
 succeeded in 51ms:
# WRK-637 Plan Draft — Memory Governance: Compaction, Tiering, Eviction

**Route:** B (Medium) | **Computer:** ace-linux-1 | **Drafted:** 2026-03-09

---

## Mission

Build `scripts/memory/compact-memory.py` (and `curate-memory.py`) to enforce the memory
tier model, evict stale bullets, and integrate with comprehensive-learning Phase 3b/3c —
preventing context-rot in MEMORY.md and topic files.

---

## Plan

### Phase 1 — TDD Setup (tests first)

1. Create `tests/memory/` directory with `conftest.py` and fixtures
2. Write `tests/memory/test_compact_memory.py` covering:
 succeeded in 51ms:
OpenAI Codex v0.112.0 (research preview)
--------
workdir: /mnt/local-analysis/workspace-hub
model: gpt-5.4
provider: openai
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR, /home/vamsee/.codex/memories]
reasoning effort: medium
reasoning summaries: none
session id: 019cd52b-0ca2-7ea2-9f08-3c7eb7d05968
--------
user
# Stance: Codex Plan Draft Review

You are a software engineer agent. Your focus is on **implementation correctness, edge cases, and testability**.

You will receive a Claude-authored plan draft. Walk it section-by-section and produce your own refined version.

When reviewing:
1. Challenge any assumptions about implementation approach — is there a simpler or more robust way?
codex
# WRK-637 Plan Draft — Memory Governance: Compaction, Tiering, Eviction

**Route:** B (Medium) | **Computer:** ace-linux-1 | **Drafted:** 2026-03-10

---

## Mission

Build `scripts/memory/compact-memory.py` and `scripts/memory/curate-memory.py` to enforce the memory tier model, evict stale bullets safely, and integrate with comprehensive-learning Phase 3b/3c without introducing unsafe file writes or brittle cron behavior.

---

## Plan

### Phase 1 — TDD Setup (tests first)

1. Create `tests/memory/` with `conftest.py`, fixture builders, and isolated temp memory roots.
2. Write `tests/memory/test_compact_memory.py` covering:
   - `--dry-run` emits audit text and writes no files anywhere under the temp root.
   - Trigger gating: exits cleanly with `no-op` when thresholds are not exceeded and `--force` is not set.
   - Explicit root resolution: `--memory-root` works; multiple candidate roots without explicit selection fails with a clear error.
   - Done-WRK eviction: bullet referencing closed WRK with valid completion date older than 30 days moves to `archive/done-wrk.md`.
   - Done-WRK edge cases: missing WRK file, malformed frontmatter, missing done timestamp, and non-done status do not evict.
   - Path staleness: bullet with a non-existent path is flagged and archived to `archive/stale-paths.md`.
   - Path parsing edge cases: multiple paths in one bullet, relative paths, code spans, and punctuation-adjacent paths parse correctly.
   - `# keep` exempts only age-based eviction, not done-WRK/path-invalid/manual-review categories.
   - Dedup keeps the fresher bullet deterministically and is idempotent on re-run.
   - Age eviction handles timezone-aware date math and malformed/missing timestamps safely.
   - Compaction frees lines from an oversized topic file and preserves valid Markdown structure.
   - Idempotency: second apply run on already-compacted files performs zero mutations and appends either no log entry or a zero-change entry consistently.
   - `compact-log.jsonl` contains required fields and valid JSON for each line.
   - Partial-failure safety: if one archive write fails, source files are not left half-rewritten.
3. Write `tests/memory/test_curate_memory.py` covering:
   - Bullet classification (`memory-keep | domain-doc | skill-update | archive`) from representative bullets.
   - Unknown or malformed bullet format degrades to `archive` or `manual-review`, not crash.
   - Promotion candidate output is deterministic and created under `.claude/state/candidates/`.
   - Existing candidate file is replaced atomically, not appended with duplicates.
4. Run tests with `uv run --no-project python -m pytest tests/memory -q` and confirm RED before implementation.
5. Keep fixtures repo-local and synthetic; do not depend on the live `~/.claude/projects/...` state.

**Pseudocode**

```text
build_fixture_memory_tree(kind) -> Path
  1. Create temp root with MEMORY.md, topic files, archive/, and optional WRK files.
  2. Populate bullets covering valid, malformed, stale, duplicate, and keep-marker cases.
  3. Return root path for the test.

assert_dry_run_no_writes(root) -> None
  1. Snapshot file hashes/mtimes under root.
  2. Run compact-memory with --dry-run and --memory-root <root>.
  3. Re-scan files and assert hashes/mtimes unchanged.
```

### Phase 2 — `compact-memory.py` implementation

File: `scripts/memory/compact-memory.py`

**Phase A — CLI and root resolution**
- Accept `--memory-root` explicitly; make this the preferred path for tests and integration.
- Allow auto-discovery of `~/.claude/projects/*/memory/` only as a fallback.
- If auto-discovery yields zero or multiple candidates, exit non-zero with an actionable message instead of guessing the “active” project.
- Support `--dry-run`, `--force`, `--audit-path`, and `--check-commands`.
- Default command execution to off for safety on nightly runs; command staleness stays audit-only unless `--check-commands` is explicitly supplied.

**Phase B — parse and audit**
- Parse `MEMORY.md` and topic files (`*.md`, excluding `archive/`).
- Treat bullets as list items only; ignore headings, prose, fenced code blocks, and archive files.
- Normalize bullets into structured records: source file, line span, text, marker flags, extracted WRK refs, extracted paths, extracted commands, timestamps/signals if present.
- Apply eviction rules in this order:
  1. Done-WRK expiry: WRK status `done/closed` plus completion timestamp older than 30 days.
  2. Path staleness: extracted path does not exist relative to workspace or as absolute path.
  3. Command staleness: only when `--check-commands`; cap at 3 audited commands/run, 5s timeout each, no shell interpolation.
  4. Dedup: near-duplicate bullets within the same topic file; keep newest or more specific using deterministic tie-breakers.
  5. Age eviction: last-seen/session signal older than 90 days and no `# keep`.
- Write audit output to `compact-audit.md` under the memory root by default.
- Audit must distinguish `evict`, `manual-review`, and `keep` so unsafe heuristics do not silently delete content.

**Phase C — apply**
- Create `archive/` if missing.
- Write archived bullets grouped by reason to:
  - `archive/done-wrk.md`
  - `archive/stale-paths.md`
  - `archive/stale-commands.md`
  - `archive/age-evicted.md`
  - `archive/deduped.md`
- Rewrite topic files atomically after computing the full plan of changes.
- Preserve original file ordering for retained bullets.
- Update `MEMORY.md` only if section pointers are invalid, duplicated, or point to removed topic files; do not rewrite unrelated content.
- Append to `compact-log.jsonl` with:
  - `timestamp`
  - `memory_root`
  - `dry_run`
  - `lines_freed_memory`
  - `lines_freed_topics`
  - `bullets_evicted`
  - `bullets_flagged_manual_review`
  - `archive_counts_by_reason`
  - `command_checks_attempted`
  - `command_checks_failed`

**Trigger check**
- Run compaction when:
  - `MEMORY.md` > 180 lines
  - any topic file > 150 lines
  - `--force` is set
- If thresholds are not crossed, exit 0 with a clear `no-op` summary.
- Keep “Phase 3 flags ≥5 stale entries” and quarterly scheduling out of the script’s own trigger logic unless an explicit input file or flag provides that signal; otherwise the script becomes coupled to external state it cannot verify robustly.

**Operational rules**
- Use `uv run --no-project python scripts/memory/compact-memory.py ...` for all documented invocations.
- Use atomic file writes (`tmp` + rename) for audit, archive, rewritten topics, and candidate outputs.
- Return non-zero on malformed root layout only when running standalone; comprehensive-learning integration should catch and log failures, then continue.

**Pseudocode**

```text
resolve_memory_root(cli_root) -> Path
  1. If cli_root is provided, validate required files/directories and return it.
  2. Else glob ~/.claude/projects/*/memory/.
  3. If exactly one valid root exists, return it.
  4. Else raise a descriptive error requiring --memory-root.

audit_memory(root, check_commands) -> AuditResult
  1. Parse MEMORY.md and topic files into bullet records.
  2. For each bullet, evaluate rules in priority order and assign one disposition.
  3. Collect archive actions, manual-review findings, retained bullets, and line deltas.
  4. Return a complete mutation plan without writing files.

apply_compaction(audit_result) -> ApplyResult
  1. Write/update archive files from grouped actions.
  2. Rewrite only changed topic files atomically.
  3. Conditionally update MEMORY.md pointers.
  4. Append one log record and return summary metrics.
```

### Phase 3 — `curate-memory.py` implementation

File: `scripts/memory/curate-memory.py`

- Accept `--memory-root` and optional `--input-audit` / `--output`.
- Classify each active bullet as `memory-keep | domain-doc | skill-update | archive`.
- Keep classification deterministic and rule-based; do not couple it to live LLM availability.
- Write promotion candidates to `.claude/state/candidates/memory-promotion-candidates.md` atomically.
- If the output directory is missing, create it.
- If curation fails during comprehensive-learning Phase 3c, log and continue.

**Rules**
- `memory-keep`: stable, high-signal facts suitable for active topic files.
- `domain-doc`: belongs in repo docs or skill references, not memory.
- `skill-update`: indicates a reusable process gap or skill improvement.
- `archive`: stale, low-signal, malformed, or superseded content.

**Operational rules**
- Use `uv run --no-project python scripts/memory/curate-memory.py ...` for all documented invocations.
- Do not mutate `MEMORY.md` or topic files; this script only emits candidate artifacts.

**Pseudocode**

```text
classify_bullet(bullet) -> Category
  1. Check for stale/superseded markers first -> archive.
  2. Check for process/skill-improvement signals -> skill-update.
  3. Check for durable reference-value signals -> memory-keep.
  4. Else map documentation-oriented content -> domain-doc.

write_candidates(categories, output_path) -> None
  1. Group bullets by category.
  2. Render deterministic markdown sections.
  3. Write file atomically to the requested output path.
```

### Phase 4 — Integration

- Verify comprehensive-learning references use `uv run --no-project python` for both scripts.
- Verify the Phase 3b/3c docs reference the correct paths and failure behavior: log failure, continue pipeline.
- Verify nightly execution does not require interactive root selection; integration should pass `--memory-root` explicitly.
- Verify command checks are not enabled in unattended cron runs unless explicitly intended.
- Update WRK-637 planning artifacts only if required by the workflow stage owner; this WRK should not claim WRK-635 implementation.
- Add one integration test or fixture-driven smoke path for the documented comprehensive-learning invocation.

**Pseudocode**

```text
verify_integration_docs() -> None
  1. Inspect comprehensive-learning skill/docs for compact-memory and curate-memory invocations.
  2. Confirm each Python call uses uv run --no-project python.
  3. Confirm failure mode is "log and continue" for non-mandatory phases.
  4. Confirm a deterministic --memory-root argument is supplied where needed.
```

---

## Test Strategy

| Test | Expected | Gate |
|------|----------|------|
| `--dry-run` on fixture memory root | audit report emitted, zero file writes | PASS |
| trigger gating | no-op exit when below thresholds; `--force` bypasses | PASS |
| root resolution | explicit `--memory-root` works; ambiguous auto-discovery fails clearly | PASS |
| Done-WRK eviction | WRK refs with valid done timestamp older than 30 days moved to archive | PASS |
| Done-WRK malformed metadata | missing/malformed status dates do not evict or crash | PASS |
| Path staleness | stale paths are archived/flagged correctly | PASS |
| `# keep` exemption | exempt from age eviction only | PASS |
| dedup | deterministic survivor retained; second run has zero changes | PASS |
| age eviction | 90-day cutoff is timezone-safe and deterministic | PASS |
| oversize topic compaction | oversized topic reduced while preserving Markdown validity | PASS |
| `compact-log.jsonl` | JSON valid; required fields present | PASS |
| curate classification | all categories rendered deterministically | PASS |
| integration invocation | documented pipeline calls use `uv run --no-project python` | PASS |

Minimum 3 PASS is too weak for this WRK. Require all unit tests passing plus at least 1 integration/smoke PASS before Stage 10 closes.

---

## Acceptance Criteria Map

| AC | Phase | Test |
|----|-------|------|
| dry-run works | 1+2 | `test_compact_memory::test_dry_run_no_writes` |
| done-WRK eviction | 1+2 | `test_compact_memory::test_done_wrk_eviction` |
| path staleness | 1+2 | `test_compact_memory::test_path_staleness` |
| ≥10 lines freed | 1+2 | `test_compact_memory::test_oversize_topic_compaction` |
| MEMORY.md ≤180L after WRK-635 bulk scan | 2+4 | integration smoke with oversized fixture root |
| `# keep` exemption | 1+2 | `test_compact_memory::test_keep_applies_only_to_age_eviction` |
| comp-learning Phase 3b updated | 4 | integration/doc invocation verification |
| compact-log.jsonl | 1+2 | `test_compact_memory::test_log_written` |
| curate-memory classification | 1+3 | `test_curate_memory::test_classification_matrix` |
| promotion candidate file written | 1+3 | `test_curate_memory::test_candidate_output_atomic` |
| scan-sessions.py headroom check | 4 | explicitly out of scope for implementation here; note dependency only |
| ambiguous/missing root handled safely | 1+2 | `test_compact_memory::test_root_resolution_errors` |
| malformed WRK/date metadata handled safely | 1+2 | `test_compact_memory::test_done_wrk_malformed_metadata` |
| unattended cron safety | 2+4 | integration verification that command checks are opt-in and failures are non-fatal |

---

## Out of Scope

- WRK-635 `scan-sessions.py` implementation; this WRK only defines the contract it must call into.
- Direct mutation policy for what content humans should keep or evict beyond the scripted rule set.
- Full Phase 3c cron wiring; only script and documented invocation contract are in scope.
- Any LLM-based semantic classifier for curation; keep Phase 3 rule-based and deterministic.
- A full memory quality scoring harness (`% stale`, `% verified`, `signal density`, usage tracking); spin off separately.

---

## Codex Notes

- The draft’s “glob, pick active project” assumption is too brittle for correctness and unsafe for cron. The script should prefer explicit `--memory-root` and fail on ambiguous discovery.
- Running arbitrary commands from bullets during nightly compaction is a risk. Command checks should be opt-in via `--check-commands`, capped, timeout-bounded, and not enabled by default in unattended flows.
- “Minimum 3 PASS before Stage 10 closes” is not a credible gate for a file-rewriting governance script. This needs full unit coverage for mutation logic plus at least one integration smoke test.
- The original AC map did not cover malformed WRK metadata, missing timestamps, ambiguous root discovery, trigger no-op behavior, or atomic-write rollback safety.
- `# keep` should exempt age eviction only. It should not override invalid path or done-WRK archival, otherwise stale facts become permanently sticky.
- The draft referenced “Phase 3 flags ≥5 stale entries” and quarterly compaction, but those inputs are external and not defined in the script interface. Keep them out of core trigger logic unless passed explicitly.
- Every Python invocation in docs/tests/integration should use `uv run --no-project python ...`. That includes `pytest`, `compact-memory.py`, `curate-memory.py`, and any verification snippets in comprehensive-learning docs.
- For date math, use explicit timezone-aware parsing and compare against absolute timestamps; missing or malformed dates must degrade to `manual-review` or `keep`, not crash or silently evict.
- Idempotency needs a precise contract: either no log entry on zero-change apply or a zero-change log entry every time. Pick one and test it.
tokens used
51,524
# WRK-637 Plan Draft — Memory Governance: Compaction, Tiering, Eviction

**Route:** B (Medium) | **Computer:** ace-linux-1 | **Drafted:** 2026-03-10

---

## Mission

Build `scripts/memory/compact-memory.py` and `scripts/memory/curate-memory.py` to enforce the memory tier model, evict stale bullets safely, and integrate with comprehensive-learning Phase 3b/3c without introducing unsafe file writes or brittle cron behavior.

---

## Plan

### Phase 1 — TDD Setup (tests first)

1. Create `tests/memory/` with `conftest.py`, fixture builders, and isolated temp memory roots.
2. Write `tests/memory/test_compact_memory.py` covering:
   - `--dry-run` emits audit text and writes no files anywhere under the temp root.
   - Trigger gating: exits cleanly with `no-op` when thresholds are not exceeded and `--force` is not set.
   - Explicit root resolution: `--memory-root` works; multiple candidate roots without explicit selection fails with a clear error.
   - Done-WRK eviction: bullet referencing closed WRK with valid completion date older than 30 days moves to `archive/done-wrk.md`.
   - Done-WRK edge cases: missing WRK file, malformed frontmatter, missing done timestamp, and non-done status do not evict.
   - Path staleness: bullet with a non-existent path is flagged and archived to `archive/stale-paths.md`.
   - Path parsing edge cases: multiple paths in one bullet, relative paths, code spans, and punctuation-adjacent paths parse correctly.
   - `# keep` exempts only age-based eviction, not done-WRK/path-invalid/manual-review categories.
   - Dedup keeps the fresher bullet deterministically and is idempotent on re-run.
   - Age eviction handles timezone-aware date math and malformed/missing timestamps safely.
   - Compaction frees lines from an oversized topic file and preserves valid Markdown structure.
   - Idempotency: second apply run on already-compacted files performs zero mutations and appends either no log entry or a zero-change entry consistently.
   - `compact-log.jsonl` contains required fields and valid JSON for each line.
   - Partial-failure safety: if one archive write fails, source files are not left half-rewritten.
3. Write `tests/memory/test_curate_memory.py` covering:
   - Bullet classification (`memory-keep | domain-doc | skill-update | archive`) from representative bullets.
   - Unknown or malformed bullet format degrades to `archive` or `manual-review`, not crash.
   - Promotion candidate output is deterministic and created under `.claude/state/candidates/`.
   - Existing candidate file is replaced atomically, not appended with duplicates.
4. Run tests with `uv run --no-project python -m pytest tests/memory -q` and confirm RED before implementation.
5. Keep fixtures repo-local and synthetic; do not depend on the live `~/.claude/projects/...` state.

**Pseudocode**

```text
build_fixture_memory_tree(kind) -> Path
  1. Create temp root with MEMORY.md, topic files, archive/, and optional WRK files.
  2. Populate bullets covering valid, malformed, stale, duplicate, and keep-marker cases.
  3. Return root path for the test.

assert_dry_run_no_writes(root) -> None
  1. Snapshot file hashes/mtimes under root.
  2. Run compact-memory with --dry-run and --memory-root <root>.
  3. Re-scan files and assert hashes/mtimes unchanged.
```

### Phase 2 — `compact-memory.py` implementation

File: `scripts/memory/compact-memory.py`

**Phase A — CLI and root resolution**
- Accept `--memory-root` explicitly; make this the preferred path for tests and integration.
- Allow auto-discovery of `~/.claude/projects/*/memory/` only as a fallback.
- If auto-discovery yields zero or multiple candidates, exit non-zero with an actionable message instead of guessing the “active” project.
- Support `--dry-run`, `--force`, `--audit-path`, and `--check-commands`.
- Default command execution to off for safety on nightly runs; command staleness stays audit-only unless `--check-commands` is explicitly supplied.

**Phase B — parse and audit**
- Parse `MEMORY.md` and topic files (`*.md`, excluding `archive/`).
- Treat bullets as list items only; ignore headings, prose, fenced code blocks, and archive files.
- Normalize bullets into structured records: source file, line span, text, marker flags, extracted WRK refs, extracted paths, extracted commands, timestamps/signals if present.
- Apply eviction rules in this order:
  1. Done-WRK expiry: WRK status `done/closed` plus completion timestamp older than 30 days.
  2. Path staleness: extracted path does not exist relative to workspace or as absolute path.
  3. Command staleness: only when `--check-commands`; cap at 3 audited commands/run, 5s timeout each, no shell interpolation.
  4. Dedup: near-duplicate bullets within the same topic file; keep newest or more specific using deterministic tie-breakers.
  5. Age eviction: last-seen/session signal older than 90 days and no `# keep`.
- Write audit output to `compact-audit.md` under the memory root by default.
- Audit must distinguish `evict`, `manual-review`, and `keep` so unsafe heuristics do not silently delete content.

**Phase C — apply**
- Create `archive/` if missing.
- Write archived bullets grouped by reason to:
  - `archive/done-wrk.md`
  - `archive/stale-paths.md`
  - `archive/stale-commands.md`
  - `archive/age-evicted.md`
  - `archive/deduped.md`
- Rewrite topic files atomically after computing the full plan of changes.
- Preserve original file ordering for retained bullets.
- Update `MEMORY.md` only if section pointers are invalid, duplicated, or point to removed topic files; do not rewrite unrelated content.
- Append to `compact-log.jsonl` with:
  - `timestamp`
  - `memory_root`
  - `dry_run`
  - `lines_freed_memory`
  - `lines_freed_topics`
  - `bullets_evicted`
  - `bullets_flagged_manual_review`
  - `archive_counts_by_reason`
  - `command_checks_attempted`
  - `command_checks_failed`

**Trigger check**
- Run compaction when:
  - `MEMORY.md` > 180 lines
  - any topic file > 150 lines
  - `--force` is set
- If thresholds are not crossed, exit 0 with a clear `no-op` summary.
- Keep “Phase 3 flags ≥5 stale entries” and quarterly scheduling out of the script’s own trigger logic unless an explicit input file or flag provides that signal; otherwise the script becomes coupled to external state it cannot verify robustly.

**Operational rules**
- Use `uv run --no-project python scripts/memory/compact-memory.py ...` for all documented invocations.
- Use atomic file writes (`tmp` + rename) for audit, archive, rewritten topics, and candidate outputs.
- Return non-zero on malformed root layout only when running standalone; comprehensive-learning integration should catch and log failures, then continue.

**Pseudocode**

```text
resolve_memory_root(cli_root) -> Path
  1. If cli_root is provided, validate required files/directories and return it.
  2. Else glob ~/.claude/projects/*/memory/.
  3. If exactly one valid root exists, return it.
  4. Else raise a descriptive error requiring --memory-root.

audit_memory(root, check_commands) -> AuditResult
  1. Parse MEMORY.md and topic files into bullet records.
  2. For each bullet, evaluate rules in priority order and assign one disposition.
  3. Collect archive actions, manual-review findings, retained bullets, and line deltas.
  4. Return a complete mutation plan without writing files.

apply_compaction(audit_result) -> ApplyResult
  1. Write/update archive files from grouped actions.
  2. Rewrite only changed topic files atomically.
  3. Conditionally update MEMORY.md pointers.
  4. Append one log record and return summary metrics.
```

### Phase 3 — `curate-memory.py` implementation

File: `scripts/memory/curate-memory.py`

- Accept `--memory-root` and optional `--input-audit` / `--output`.
- Classify each active bullet as `memory-keep | domain-doc | skill-update | archive`.
- Keep classification deterministic and rule-based; do not couple it to live LLM availability.
- Write promotion candidates to `.claude/state/candidates/memory-promotion-candidates.md` atomically.
- If the output directory is missing, create it.
- If curation fails during comprehensive-learning Phase 3c, log and continue.

**Rules**
- `memory-keep`: stable, high-signal facts suitable for active topic files.
- `domain-doc`: belongs in repo docs or skill references, not memory.
- `skill-update`: indicates a reusable process gap or skill improvement.
- `archive`: stale, low-signal, malformed, or superseded content.

**Operational rules**
- Use `uv run --no-project python scripts/memory/curate-memory.py ...` for all documented invocations.
- Do not mutate `MEMORY.md` or topic files; this script only emits candidate artifacts.

**Pseudocode**

```text
classify_bullet(bullet) -> Category
  1. Check for stale/superseded markers first -> archive.
  2. Check for process/skill-improvement signals -> skill-update.
  3. Check for durable reference-value signals -> memory-keep.
  4. Else map documentation-oriented content -> domain-doc.

write_candidates(categories, output_path) -> None
  1. Group bullets by category.
  2. Render deterministic markdown sections.
  3. Write file atomically to the requested output path.
```

### Phase 4 — Integration

- Verify comprehensive-learning references use `uv run --no-project python` for both scripts.
- Verify the Phase 3b/3c docs reference the correct paths and failure behavior: log failure, continue pipeline.
- Verify nightly execution does not require interactive root selection; integration should pass `--memory-root` explicitly.
- Verify command checks are not enabled in unattended cron runs unless explicitly intended.
- Update WRK-637 planning artifacts only if required by the workflow stage owner; this WRK should not claim WRK-635 implementation.
- Add one integration test or fixture-driven smoke path for the documented comprehensive-learning invocation.

**Pseudocode**

```text
verify_integration_docs() -> None
  1. Inspect comprehensive-learning skill/docs for compact-memory and curate-memory invocations.
  2. Confirm each Python call uses uv run --no-project python.
  3. Confirm failure mode is "log and continue" for non-mandatory phases.
  4. Confirm a deterministic --memory-root argument is supplied where needed.
```

---

## Test Strategy

| Test | Expected | Gate |
|------|----------|------|
| `--dry-run` on fixture memory root | audit report emitted, zero file writes | PASS |
| trigger gating | no-op exit when below thresholds; `--force` bypasses | PASS |
| root resolution | explicit `--memory-root` works; ambiguous auto-discovery fails clearly | PASS |
| Done-WRK eviction | WRK refs with valid done timestamp older than 30 days moved to archive | PASS |
| Done-WRK malformed metadata | missing/malformed status dates do not evict or crash | PASS |
| Path staleness | stale paths are archived/flagged correctly | PASS |
| `# keep` exemption | exempt from age eviction only | PASS |
| dedup | deterministic survivor retained; second run has zero changes | PASS |
| age eviction | 90-day cutoff is timezone-safe and deterministic | PASS |
| oversize topic compaction | oversized topic reduced while preserving Markdown validity | PASS |
| `compact-log.jsonl` | JSON valid; required fields present | PASS |
| curate classification | all categories rendered deterministically | PASS |
| integration invocation | documented pipeline calls use `uv run --no-project python` | PASS |

Minimum 3 PASS is too weak for this WRK. Require all unit tests passing plus at least 1 integration/smoke PASS before Stage 10 closes.

---

## Acceptance Criteria Map

| AC | Phase | Test |
|----|-------|------|
| dry-run works | 1+2 | `test_compact_memory::test_dry_run_no_writes` |
| done-WRK eviction | 1+2 | `test_compact_memory::test_done_wrk_eviction` |
| path staleness | 1+2 | `test_compact_memory::test_path_staleness` |
| ≥10 lines freed | 1+2 | `test_compact_memory::test_oversize_topic_compaction` |
| MEMORY.md ≤180L after WRK-635 bulk scan | 2+4 | integration smoke with oversized fixture root |
| `# keep` exemption | 1+2 | `test_compact_memory::test_keep_applies_only_to_age_eviction` |
| comp-learning Phase 3b updated | 4 | integration/doc invocation verification |
| compact-log.jsonl | 1+2 | `test_compact_memory::test_log_written` |
| curate-memory classification | 1+3 | `test_curate_memory::test_classification_matrix` |
| promotion candidate file written | 1+3 | `test_curate_memory::test_candidate_output_atomic` |
| scan-sessions.py headroom check | 4 | explicitly out of scope for implementation here; note dependency only |
| ambiguous/missing root handled safely | 1+2 | `test_compact_memory::test_root_resolution_errors` |
| malformed WRK/date metadata handled safely | 1+2 | `test_compact_memory::test_done_wrk_malformed_metadata` |
| unattended cron safety | 2+4 | integration verification that command checks are opt-in and failures are non-fatal |

---

## Out of Scope

- WRK-635 `scan-sessions.py` implementation; this WRK only defines the contract it must call into.
- Direct mutation policy for what content humans should keep or evict beyond the scripted rule set.
- Full Phase 3c cron wiring; only script and documented invocation contract are in scope.
- Any LLM-based semantic classifier for curation; keep Phase 3 rule-based and deterministic.
- A full memory quality scoring harness (`% stale`, `% verified`, `signal density`, usage tracking); spin off separately.

---

## Codex Notes

- The draft’s “glob, pick active project” assumption is too brittle for correctness and unsafe for cron. The script should prefer explicit `--memory-root` and fail on ambiguous discovery.
- Running arbitrary commands from bullets during nightly compaction is a risk. Command checks should be opt-in via `--check-commands`, capped, timeout-bounded, and not enabled by default in unattended flows.
- “Minimum 3 PASS before Stage 10 closes” is not a credible gate for a file-rewriting governance script. This needs full unit coverage for mutation logic plus at least one integration smoke test.
- The original AC map did not cover malformed WRK metadata, missing timestamps, ambiguous root discovery, trigger no-op behavior, or atomic-write rollback safety.
- `# keep` should exempt age eviction only. It should not override invalid path or done-WRK archival, otherwise stale facts become permanently sticky.
- The draft referenced “Phase 3 flags ≥5 stale entries” and quarterly compaction, but those inputs are external and not defined in the script interface. Keep them out of core trigger logic unless passed explicitly.
- Every Python invocation in docs/tests/integration should use `uv run --no-project python ...`. That includes `pytest`, `compact-memory.py`, `curate-memory.py`, and any verification snippets in comprehensive-learning docs.
- For date math, use explicit timezone-aware parsing and compare against absolute timestamps; missing or malformed dates must degrade to `manual-review` or `keep`, not crash or silently evict.
- Idempotency needs a precise contract: either no log entry on zero-change apply or a zero-change log entry every time. Pick one and test it.
