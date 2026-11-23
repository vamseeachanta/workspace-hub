# Plan for #3138: Backfill historical skill-invocation events from transcripts

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-06-15
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3138
> **Client:** N/A
> **Project:** (none)
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-15-plan-3138-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

This plan reconstructs `{skill_name (rel-path), ts, session_id}` skill-invocation
events from historical logs so the `skill-invocation-scanner.py` → `skill-usage-report.py`
demotion chain (shipped in #3112) can act on a ≥14-day coverage window **now**,
instead of waiting ~2 weeks for the forward-looking emit signal to accrue.

### Existing repo code

- Found: `scripts/skills/skill_execution_tracker.py:37-43` — `_extract_skill_name_from_path(file_path)` is the canonical SKILL.md-path parser. Its regex is `SKILL_PATH_RE = re.compile(r"/\.claude/skills/([^/]+/[^/]+)/SKILL\.md$")` (line 17). On match it returns `m.group(1).split("/")[-1]` — i.e. the **basename only** (`"workspace-hub/work-queue" -> "work-queue"`). **This is the wrong key for the scanner's session-log input** (see Gap below); the plan reuses the module's regex and the captured **`m.group(1)` rel-path group** (NOT the basename split), and adds a thin rel-path helper alongside it rather than duplicating the regex.
- Found: `.claude/hooks/session-logger.sh:34-40` — the live forward-looking emit. It sets `SKILL_NAME="${FILE##*/.claude/skills/}"` then strips `/SKILL.md`, producing the **full rel-path** (`email/gmail-triage`), and writes it to the `skill_name` field of each `session_YYYYMMDD.jsonl` line (line 59-64). It also **dual-writes** the same envelope to `logs/orchestrator/claude/session_YYYYMMDD.jsonl` (lines 84-86). The backfill output format must match this exactly.
- Found: `scripts/skills/skill-invocation-scanner.py:54-92` `scan_sessions()` reads `session_*.jsonl`, keys events by the raw `skill_name` string (line 77-87), and at line 144-146 joins them via `event_ts.get(skill_rel)` where `skill_rel` is the **rel-path** produced by `discover_skills()` (`skill_md.parent.relative_to(root).as_posix()`, line 100-101). **Confirmed: the scanner joins on rel-path, not basename.** Output rows are re-keyed to `short_name` via `derive_short_name()` (line 105-128) before emission.
- Found: `scripts/skills/skill-usage-report.py:355-388` `apply_invocation_demotion()` demotes a skill one tier iff `coverage_days >= 14 AND session_count == 0` (`MIN_COVERAGE_DAYS = 14`, line 331; `should_demote` mirror in scanner line 180-186). This is the gate the backfill must satisfy.

### Standards
Not applicable (harness/infrastructure issue).

### LLM Wiki pages consulted
No relevant wiki pages (harness-internal tooling; not wiki content). Client: N/A.

### Documents consulted
- `docs/plans/2026-06-15-issue-3112-skill-invocation-instrumentation.md` — the parent plan; established the verified Read-of-SKILL.md emit signal and the scanner/report/demotion chain this plan feeds.
- `docs/plans/2026-04-17-issue-2320-skill-usage-audit.md` — origin of the scanner/demotion design.
- Issue #3112 body — defines the backfill task ("Backfill what's recoverable... document the limitation that pre-instrumentation usage is unknowable").
- Issue #3139 — universe/short_name-parity reconciliation (dependency, see Risks).
- Issue #3137 — Skill-tool capture (relation, see Risks).

### Gaps identified
- **No backfill tool exists.** `ls scripts/skills/*backfill*` → no matching skill-invocation backfill script (`scripts/hermes/backfill-skills-to-repo.sh` is unrelated — it syncs skill *files*, not invocation events).
- **`_extract_skill_name_from_path` returns the WRONG granularity for the scanner.** It returns basename; the scanner and the live logger both key on **rel-path**. The plan must NOT call that function's return value directly for the emitted `skill_name`; it reuses the module's `SKILL_PATH_RE` regex and emits the rel-path `m.group(1)`. (This is a real reuse trap — flag for reviewers.)
- **No `skill_name` exists in any historical log.** Confirmed empirically: 0 of ~93k existing session-log events carry a populated `skill_name` (it shipped after they were written).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-15 via `gh issue view`):
- `#3138` — OPEN — "Skill-invocation: backfill historical events from transcripts — follow-on to #3112"
- `#3112` — OPEN (status:plan-approved, status:completeness-verified) — parent instrumentation issue
- `#3139` — OPEN — "reconcile scanner-vs-report skill universe (3,180 vs 833)"
- `#3137` — OPEN — "capture Skill-tool calls (id→short_name resolution)"

**File existence** (`ls` / Read 2026-06-15):
- EXISTS: `scripts/skills/skill_execution_tracker.py` (the reuse target)
- EXISTS: `scripts/skills/skill-invocation-scanner.py`, `scripts/skills/skill-usage-report.py`
- EXISTS: `.claude/hooks/session-logger.sh`
- MISSING (new — this plan creates): `scripts/skills/skill_invocation_backfill.py`, `tests/skills/test_skill_invocation_backfill.py`

**Line excerpt — the regex to reuse** (`scripts/skills/skill_execution_tracker.py:17`):
```
SKILL_PATH_RE = re.compile(r"/\.claude/skills/([^/]+/[^/]+)/SKILL\.md$")
```
Note `_extract_skill_name_from_path` (line 37-43) returns `m.group(1).split("/")[-1]` (basename). The backfill reuses `m.group(1)` (rel-path) — i.e. the regex, not the basename-reducing return value.

**Line excerpt — live emit shape to match** (`.claude/hooks/session-logger.sh:36-38`):
```
  */.claude/skills/*/SKILL.md)
    SKILL_NAME="${FILE##*/.claude/skills/}"   # -> email/gmail-triage/SKILL.md
    SKILL_NAME="${SKILL_NAME%/SKILL.md}"       # -> email/gmail-triage
```

**Recoverable-data census** (ran probe scripts over live data 2026-06-15):

| Source | Read-of-SKILL.md events | distinct skills (rel-path) | distinct sessions | date span | span (days) |
|---|---|---|---|---|---|
| `~/.claude/projects/**/*.jsonl` (Claude transcripts, 4,750 files) | 358 | 101 | 109 | 2026-03-17 .. 2026-06-15 | 90 |
| `.claude/state/sessions/session_*.jsonl` (58 files) | 343 | 48 | 72 | 2026-03-25 .. 2026-05-23 | 59 |
| `logs/orchestrator/claude/session_*.jsonl` | 2,278 | 264 | 72 | 2026-03-02 .. 2026-05-23 | 82 |

Plus **1,080 `Skill` tool_use events** in transcripts (deferred to #3137 — plugin-id resolution).

Transcript record shape (verified): top-level keys `['content', 'operation', 'sessionId', 'timestamp', 'type']`; tool calls live in `message.content[]` blocks with `type == "tool_use"`, `name == "Read"`, `input.file_path` carrying the SKILL.md path. Sample:
```
{"path":"/mnt/local-analysis/reconcile-main-20260427/.claude/skills/coordination/issue-planning-mode/SKILL.md",
 "ts":"2026-04-27T15:50:03.776Z","sid":"93a4a205-...","rel":"coordination/issue-planning-mode"}
```
Note paths appear under **worktrees** (`reconcile-main-20260427/...`) as well as the main checkout — the regex anchors on `/.claude/skills/.../SKILL.md` so it matches regardless of the checkout root. Good.

**Reproduction proof — why backfill is needed** (the blind spot, `/tmp/inspect_session_format.py` over `.claude/state/sessions`):
```
session files: 58
events with skill_name set: 0
common key-sets: ['epoch','file','hook','project','repo','session_id','tool','ts'] (27,166 events have `file` but no `skill_name`)
```
- Reproduced at: 2026-06-15
- Failure mode observed matches issue claim: YES — the forward-looking emit cannot demote until 14 days accrue because **zero** `skill_name` events exist historically; the `file` field is present but `skill_name` was never derived for pre-#3112 records.

**Source count: 5** (issue body + skill_execution_tracker.py + scanner + session-logger.sh + #3112 plan).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-06-15-issue-3138-skill-invocation-backfill.md |
| Implementation | `scripts/skills/skill_invocation_backfill.py` |
| Tests | `tests/skills/test_skill_invocation_backfill.py` |
| Output (data, not committed) | `.claude/state/sessions/session_<YYYYMMDD>.backfill.jsonl` (per source-day) |
| Plan review — Claude | scripts/review/results/2026-06-15-plan-3138-claude.md |
| Plan review — Codex | scripts/review/results/2026-06-15-plan-3138-codex.md |
| Plan review — Gemini | scripts/review/results/2026-06-15-plan-3138-gemini.md |
| Docs updates | docs/plans/README.md (index entry) |

---

## Deliverable

A `scripts/skills/skill_invocation_backfill.py` tool that reconstructs historical
`{skill_name (rel-path), ts, session_id}` Read-of-SKILL.md events from Claude
transcripts and existing session logs, writes them in the scanner-consumable
`session_*.jsonl` envelope, is **idempotent** (re-runs add no duplicates), and
**streams** per-file/per-day so it never loads thousands of transcripts into
memory — populating ≥14d coverage so `apply_invocation_demotion` can act immediately.

---

## Pseudocode

```
# skill_invocation_backfill.py
from skill_execution_tracker import SKILL_PATH_RE   # REUSE the regex (not the basename fn)

def rel_path_from(file_path):                 # mirrors session-logger.sh semantics
    m = SKILL_PATH_RE.search(file_path)
    return m.group(1) if m else None          # rel-path, e.g. "coordination/issue-planning-mode"
    # NOTE: NOT _extract_skill_name_from_path() — that returns basename, wrong key.

def iter_transcript_events(projects_root):    # stream; never hold all files
    for jsonl in projects_root.rglob("*.jsonl"):
        for line in open(jsonl):              # line-by-line, not read_text()
            rec = safe_json(line); skip if None
            for block in rec.message.content where type=="tool_use" and name=="Read":
                rel = rel_path_from(block.input.file_path)
                if rel:
                    yield {ts: rec.timestamp, session_id: rec.sessionId,
                           skill_name: rel, tool: "Read", hook: "backfill",
                           source: "transcript"}

def iter_sessionlog_events(sessions_dir):     # existing logs already have `file` + session_id
    for ev in stream_session_lines(sessions_dir):
        if ev.tool == "Read" and (rel := rel_path_from(ev.get("file",""))):
            yield {ts: ev.ts, session_id: ev.session_id, skill_name: rel,
                   tool:"Read", hook:"backfill", source:"sessionlog"}

def backfill(sources, out_dir, since=None, until=None):
    seen = load_existing_dedup_index(out_dir)         # (session_id, ts, skill_name) tuples
    for ev in chain(selected sources):
        day = ev.ts[:10]
        if since and day < since: continue
        if until and day > until: continue
        key = (ev.session_id, ev.ts, ev.skill_name)
        if key in seen: continue                      # IDEMPOTENT
        seen.add(key)
        append ev to out_dir / f"session_{day.replace('-','')}.backfill.jsonl"
    print counts per day + coverage span
```

Idempotency contract: the dedup key is `(session_id, ts, skill_name)`. On every run
the tool first reads back any rows it previously wrote into the `*.backfill.jsonl`
files (and optionally the real `session_*.jsonl` for cross-source overlap) to seed
`seen`, so a second run is a no-op. Output goes to a **distinct `.backfill.jsonl`
filename** per day so it never clobbers or races the live logger writing
`session_<today>.jsonl`.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/skills/skill_invocation_backfill.py` | streaming, idempotent backfill tool |
| Create | `tests/skills/test_skill_invocation_backfill.py` | TDD suite |
| Update | docs/plans/README.md | index this plan |

No edits to `skill_execution_tracker.py`, the scanner, the report, or the logger —
the backfill is additive. (If reviewers prefer, the rel-path helper could be
*added* to `skill_execution_tracker.py` next to `_extract_skill_name_from_path`
so both consumers share it; that is an optional refactor flagged for review, not
required for this issue.)

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_rel_path_from_main_checkout | rel-path extraction from a main-checkout path | `/x/.claude/skills/coordination/issue-planning-mode/SKILL.md` | `coordination/issue-planning-mode` |
| test_rel_path_from_worktree | matches under a worktree root too | `/mnt/.../reconcile-main-20260427/.claude/skills/a/b/SKILL.md` | `a/b` |
| test_rel_path_none_for_non_skill | non-SKILL paths yield None | `/x/src/foo.py` | `None` |
| test_rel_path_uses_shared_regex | the tool imports `SKILL_PATH_RE` from skill_execution_tracker, not a copy | (import assertion) | same compiled pattern object |
| test_emit_format_matches_scanner | emitted row has `skill_name` (rel-path) + `ts` + `session_id` + `tool` | one transcript Read block | dict consumable by `scan_sessions` |
| test_transcript_parse_tool_use | extracts Read tool_use from `message.content[]` | minimal transcript record | one event |
| test_transcript_skips_skill_tool | `Skill` tool_use is NOT emitted (deferred #3137) | record with name=="Skill" | zero events |
| test_sessionlog_parse_file_field | recovers SKILL.md Read from existing session log `file` field | session-log line w/ `file`, no `skill_name` | one event w/ derived `skill_name` |
| test_idempotent_rerun | second run over same input adds zero rows | run twice | output line count unchanged |
| test_dedup_key_across_sources | same (session_id,ts,skill_name) from transcript + sessionlog dedups | overlapping events | one row |
| test_date_window_since_until | `--since`/`--until` bound the output | events across 3 days, window=1 day | only in-window rows |
| test_streaming_no_full_load | malformed line skipped without aborting file; large input handled line-wise | file w/ bad line | good rows emitted, bad skipped |
| test_scanner_reads_backfill_output | end-to-end: scanner over backfill output reports coverage_days>=14 and nonzero sessions for a used skill | synthetic 20-day backfill | `coverage_days>=14`, `session_count>0` |
| test_coverage_gate_satisfied | `should_demote(session_count=0, coverage_days)` flips True once span>=14 | backfill spanning 20d | demotion enabled for zero-session skills |

---

## Acceptance Criteria

- [ ] All new tests pass: `uv run --no-project pytest tests/skills/test_skill_invocation_backfill.py -v`
- [ ] Running the backfill then the scanner over the backfilled dir yields `coverage_days >= 14` (target: full ~90d transcript span).
- [ ] Re-running the backfill produces byte-identical output (idempotent; verified by diff/line-count).
- [ ] The emitted `skill_name` is the **rel-path** (matches `session-logger.sh` and the scanner's `discover_skills` join key), confirmed by a row spot-check.
- [ ] `--since`/`--until` date-windowing works; default streams all sources without loading all files into memory.
- [ ] The pre-instrumentation blind spot is documented in the script docstring + a one-line note in the scanner output context (per #3112 task: "document the limitation that pre-instrumentation usage is unknowable").
- [ ] Review artifacts posted to scripts/review/results/.

---

## Adversarial Review Summary

<!-- Filled in after Step 4. Not yet run. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | (pending) | |
| Codex | (pending) | |
| Gemini | (pending) | |

**Overall result:** (pending)

---

## Risks and Open Questions

- **Risk (reuse trap — highest):** `_extract_skill_name_from_path` returns the **basename**, but the scanner + live logger key on the **rel-path**. Naively "reusing" that function (as the issue text literally says) would emit the wrong key and the demotion join would silently miss every backfilled skill. Mitigation: reuse the `SKILL_PATH_RE` regex and emit `m.group(1)`; add `test_rel_path_*` to lock the rel-path contract. **This must be called out to the user at approval.**
- **Risk (short_name universe — depends on #3139):** the scanner re-keys rel-path → `short_name` via `derive_short_name`, and #3139 documents that the scanner (3,180 skills, no exclusions) and report (833, excludes `_archive/_core/_internal`) iterate **different universes** with `_archived`-vs-`_archive` collisions. Backfill events for skills that only exist under excluded dirs, or whose rel-path no longer resolves to a current SKILL.md, will be discovered-but-unclassified or collide. Mitigation: backfill emits raw rel-path events (the scanner's responsibility to key/classify); we do NOT pre-resolve short_name. If #3139 lands first, parity improves; if not, document that backfilled rows for excluded/renamed skills won't demote. **Soft dependency on #3139** — not blocking, but parity defects surface in both.
- **Risk (Skill-tool out of scope — relation to #3137):** 1,080 `Skill` tool_use events are recoverable but use plugin-namespaced ids (`superpowers:test-driven-development`) that need id→short_name resolution, explicitly deferred to #3137. This plan emits **only** Read-of-SKILL.md events; `test_transcript_skips_skill_tool` enforces the boundary. When #3137 lands, a follow-on can backfill Skill-tool events through the same tool.
- **Risk (stale/diverged sources):** `logs/orchestrator/claude` and `.claude/state/sessions` stop at 2026-05-23 for SKILL.md reads, while transcripts run to 2026-06-15. Using transcripts as the primary source gives the widest span; session logs are a secondary cross-check that mostly overlaps. Dedup across sources prevents double-counting.
- **Risk (timestamp/session_id fidelity):** transcript `timestamp` is ISO-8601 with `Z`; the scanner's `_parse_ts` handles `Z` and naive forms — verified compatible. `sessionId` (camelCase) in transcripts vs `session_id` (snake) in session logs — the backfill normalizes to `session_id` on emit.
- **Risk (volume):** 4,750 transcripts. Mitigation: stream line-by-line, never `read_text()` whole files; `--since` lets a first run scope to the last ~30 days if a full pass is slow.
- **Open:** Should backfilled events write into the real `session_<day>.jsonl` (so a single scanner pass over `.claude/state/sessions` sees everything) or stay in separate `*.backfill.jsonl` files (cleaner provenance, but the scanner globs `session_*.jsonl` — would need `--sessions-dir` pointed at a merged dir or a glob that includes both)? Recommend separate files + run the scanner with `--sessions-dir` over a dir containing both, to avoid mutating live logs the logger is actively appending to. Flag for user.
- **Open:** Retention — should backfill output be committed (durable coverage) or treated as regenerable local state under `.claude/state/`? Recommend local/regenerable (consistent with the rest of `.claude/state/sessions`, which is not committed).

---

## Dependencies

- **Parent:** #3112 (epic #3058) — shipped the emit signal + scanner/report/demotion chain this backfill feeds. `status:plan-approved`.
- **Soft dep:** #3139 — scanner/report universe + short_name parity. Not blocking (backfill emits raw rel-path), but parity defects affect whether backfilled rows classify cleanly.
- **Relation (not a dep):** #3137 — Skill-tool capture. Explicitly out of scope here; the 1,080 Skill-tool events are deferred to it.

---

## Complexity: T2

**T2** — one new streaming module + one test file, reusing an existing regex; multi-source
parsing with idempotency and date-windowing; no changes to shared harness files. Not T3
(no cross-provider or systemic change), not T1 (non-trivial dedup/streaming/format-match logic).
