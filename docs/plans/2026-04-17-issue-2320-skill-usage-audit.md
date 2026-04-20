# Plan for #2320: Mine session logs for dead-skill candidates — usage-signal input to #2280 weekly audit

> **Status:** revised 2026-04-17 — 6 deltas vs v1 (one load-bearing window reduction confirmed by user); see "Execution-time revisions"
> **Complexity:** T2
> **Date:** 2026-04-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2320
> **Review artifacts:** scripts/review/results/2026-04-17-plan-2320-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/skills/skill-usage-report.py` (#1559) — tier-classifies skills (HOT/WARM/COLD/DEAD) using static cross-references + git-log mentions (last 90 days). Does **not** parse session invocation logs.
- Found: `scripts/skills/skill-health-dashboard.sh` (#1562) — composes multiple audits into `.claude/state/skill-health/YYYY-MM-DD.json`; already wired for nightly cron (non-blocking).
- Found: `scripts/analysis/claude_session_ecosystem_audit.py` and `provider_session_ecosystem_audit.py` — session-ecosystem audits, confirm session-jsonl parsing is an established pattern.
- Gap: no existing code parses Skill-tool invocations out of `logs/orchestrator/hermes/session_YYYYMMDD.jsonl`.

### Standards
| Standard | Status | Source |
|---|---|---|
| n/a — harness/skills hygiene, not engineering | n/a | — |

### LLM Wiki pages consulted
- Not applicable (harness-infra issue).

### Documents consulted
- `docs/plans/2026-04-14-issue-2280-weekly-skill-ecosystem-audit-and-consolidation-maintenance-loop.md` — parent governance plan defining the weekly audit rules and child implementation split.
- `docs/plans/2026-04-14-issue-2282-lock-classification-and-ranking-policy-for-weekly-skills-audit.md` — ranking policy that this usage-signal will feed into.
- `logs/orchestrator/hermes/session_20260415.jsonl` (4.4MB) sampled — Skill-tool invocations are present as JSON events; parsing is straightforward.
- `.claude/state/skill-scores.yaml` — existing state format the new signal must integrate with.

### Gaps identified
- No script parses session jsonl for Skill-tool invocations.
- `skill-usage-report.py` tier assignment is driven by static references — a skill with 5 incoming `related_skills` but zero real invocations gets HOT despite being dead in practice.
- Weekly audit output (`.claude/state/skill-health/`) lacks an "invocations_30d" column.

<!-- 5 distinct sources: 3 existing scripts, 2 prior plans, session jsonl file directly sampled, skill-scores.yaml → ≥3 satisfied. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-17-issue-2320-skill-usage-audit.md` |
| New script | `scripts/skills/skill-invocation-scanner.py` |
| Tests | `tests/skills/test_skill_invocation_scanner.py` |
| Fixture | `tests/skills/fixtures/sample_session.jsonl` |
| State integration | `scripts/skills/skill-usage-report.py` (modify) |
| Report dir | `.claude/state/skill-invocations/YYYY-MM-DD.json` (created) |
| Plan review — Claude | `scripts/review/results/2026-04-17-plan-2320-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-17-plan-2320-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-17-plan-2320-gemini.md` |

---

## Deliverable

A `scripts/skills/skill-invocation-scanner.py` script that parses session jsonl files for Skill-tool invocations and emits a per-skill CSV/JSON with 30-day and 90-day counts, then feeds into the existing `skill-usage-report.py` tier classification as a fourth data source.

---

## Pseudocode

> **Revised** after empirical schema probe of `logs/orchestrator/hermes/session_YYYYMMDD.jsonl`:
> - Real event shape is a FLAT envelope: `{ts, hook, tool, hermes_tool, project, repo, model, session_id, file, skill_name}`. Top-level `skill_name` is populated on events that fire while a skill is active — this IS the signal.
> - There is no "Skill tool" sibling of Read/Bash/Grep; the plan's alias list (`Skill / activate_skill / skill`) was invented. Filtering is: "does the event have `skill_name`?", not "does the tool name match an alias list".
> - Retention is ~17 days, not 90. Output uses `coverage_days` (literal) instead of a hardcoded 90d window. Decision recorded in "Execution-time revisions".

```
function scan_sessions(sessions_dir):
    event_ts   = defaultdict(list)  # skill_name -> [event_timestamp, ...]
    session_ts = defaultdict(set)   # skill_name -> {(session_id, date), ...}
    oldest = None; newest = None
    for each session_YYYYMMDD.jsonl in sessions_dir:
        for each line in file:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue                    # malformed line — skip per AC
            sn = event.get("skill_name")
            if not sn:
                continue                    # event is not "inside a skill"
            ts = event.get("ts"); sid = event.get("session_id")
            if ts is None:
                continue
            event_ts[sn].append(ts)
            if sid:
                session_ts[sn].add((sid, date_of(ts)))
            oldest = min(oldest, ts); newest = max(newest, ts)
    coverage_days = days_between(oldest, newest) if oldest else 0
    return event_ts, session_ts, coverage_days

function classify(event_ts, session_ts, coverage_days, skills_root):
    all_skills = discover_skills(skills_root)  # walk .claude/skills/**/SKILL.md
    rows = []
    for skill in all_skills:
        ts_list   = event_ts.get(skill, [])
        sess_set  = session_ts.get(skill, set())
        rows.append({
            "skill": skill,
            "invocations_available_days": len(ts_list),
            "session_count_available_days": len(sess_set),
            "coverage_days": coverage_days,
            "last_used": max(ts_list) if ts_list else None,
            "days_since_last_use": days_between(max(ts_list), now()) if ts_list else None,
        })
    return rows

function main():
    args = parse_args()
    event_ts, session_ts, coverage = scan_sessions(args.sessions_dir)
    rows = classify(event_ts, session_ts, coverage, args.skills_root)
    write_json({"coverage_days": coverage, "generated_at": now(), "rows": rows},
               f".claude/state/skill-invocations/{today}.json")
    if args.csv: write_csv(rows, f"data/reports/skill-usage-{today}.csv")
```

Integration with `skill-usage-report.py`: add a data source that reads today's `skill-invocations/YYYY-MM-DD.json`. Demotion rule: when `session_count_available_days == 0` AND `coverage_days >= MIN_COVERAGE_DAYS` (default 14), demote one tier regardless of static references. If `coverage_days < MIN_COVERAGE_DAYS`, signal is treated as "insufficient data" and does NOT demote — prevents false-dead from short-window starts.

PII note: output contains only `skill_name`, `session_id`, `ts`, and counts. No file paths, prompts, tool args, or stdout are propagated. Output is PII-safe by construction.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/skills/skill-invocation-scanner.py` | main implementation |
| Create | `tests/skills/test_skill_invocation_scanner.py` | TDD tests |
| Create | `tests/skills/fixtures/sample_session.jsonl` | fixture: 2 skills invoked, 1 never |
| Modify | `scripts/skills/skill-usage-report.py` | add invocation-data source + tier demotion rule |
| Modify | `scripts/skills/skill-health-dashboard.sh` | call new scanner as additional audit |
| Update | `docs/plans/README.md` | add row for this plan |
| Create | `docs/reports/skill-invocation-baseline-2026-04-17.md` | one-time baseline snapshot |

---

## TDD Test List

Test convention: pytest under `tests/skills/`, fixtures under `tests/skills/fixtures/`. Fixture event shape mirrors the real flat envelope (`ts`, `session_id`, `tool`, `skill_name`).

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_scan_counts_event_when_skill_name_present | events with `skill_name` are counted | fixture with 1 event, `skill_name="foo/bar"` | `invocations_available_days == 1` for foo/bar |
| test_scan_ignores_events_without_skill_name | bare Bash/Read events are ignored | fixture with mixed events | zero count for any "skill" not present |
| test_scan_counts_distinct_sessions | 5 events across 2 sessions → session_count=2, invocations=5 | fixture with 2 sessions | both counts as described |
| test_classify_zero_invocations_flags_dead | skill never invoked gets `days_since_last_use==None` | fixture missing skill | None |
| test_classify_reports_coverage_days | coverage_days = days between oldest and newest event seen | fixture spanning 5 calendar days | `coverage_days == 5` |
| test_malformed_jsonl_line_skipped | bad JSON line does not abort | fixture with 1 bad line | valid lines parsed, malformed silently ignored |
| test_output_contains_no_file_paths | PII-safe: output has no `file`, `prompt`, `cwd`, or similar leak | run scanner, load json | assert no such keys present at any level |
| test_integration_tier_demotion_requires_coverage | tier demotion guarded by MIN_COVERAGE_DAYS | fixture with coverage=5 (< 14) | no demotion; with coverage=20 → demotion |

---

## Acceptance Criteria

- [ ] `uv run --no-project python scripts/skills/skill-invocation-scanner.py --sessions-dir logs/orchestrator/hermes --skills-root .claude/skills` exits 0 and writes `.claude/state/skill-invocations/YYYY-MM-DD.json`.
- [ ] Scan of all available session files (~17 days at time of writing) completes in <30 seconds.
- [ ] Every `.claude/skills/**/SKILL.md` appears in output (zero-invocation rows present).
- [ ] Output JSON's top-level contains `coverage_days` reflecting actual span of session data found; consumers depend on this.
- [ ] Output fields per skill: `invocations_available_days`, `session_count_available_days`, `coverage_days`, `last_used`, `days_since_last_use`. No `invocations_90d` key — the 90d window is not available.
- [ ] `uv run pytest tests/skills/test_skill_invocation_scanner.py -v` passes all 8 tests.
- [ ] `scripts/skills/skill-usage-report.py` demotes tier when `session_count_available_days == 0` AND `coverage_days >= MIN_COVERAGE_DAYS` (default 14); verified via unit test.
- [ ] `scripts/skills/skill-health-dashboard.sh` runs end-to-end and includes the new audit.
- [ ] `docs/reports/skill-invocation-baseline-2026-04-17.md` records: total skills, dead (zero sessions), demoted count, and explicit `coverage_days` value for the audit.
- [ ] Output JSON contains no file paths, prompts, tool args, or cwds — PII-safe by construction; asserted by a regression test.

## Execution-time revisions (2026-04-17)

Pre-execution scan against `.planning/plan-approved/2320.md` + empirical schema probe surfaced six deltas:

1. **Flat schema, not nested.** v1 pseudocode used `event.tool_name` + `event.tool_input.get("skill")` (Claude Code API shape). Real hermes jsonl schema is flat: `{ts, hook, tool, hermes_tool, project, repo, model, session_id, file, skill_name}`. Resolution: read `event["skill_name"]` directly.
2. **Retention 17d, not 90d — LOAD-BEARING.** Available data spans Apr 01 → Apr 17 (17 days). v1 AC hardcoded `invocations_90d`, uncomputable. User confirmed option 2a (narrow scope honestly): output becomes `invocations_available_days` + `coverage_days`. Downstream classifier uses MIN_COVERAGE_DAYS gate (14d default) to avoid false-dead verdicts on short windows.
3. **Signal semantics — dual counts.** `skill_name` is populated while a skill is active, so one skill activation can produce many events. For dead-skill detection, `session_count` is the honest signal. v1 implicitly counted events. Resolution: emit both `invocations_available_days` (raw) and `session_count_available_days` (distinct-session) per skill.
4. **Alias list is invented.** There is no "Skill tool" in the event stream — filtering is by `skill_name` presence, not tool-name match. Resolution: drop the alias concept.
5. **PII risk resolved by construction.** Output propagates only `skill_name`, `session_id`, `ts`, counts. No file paths, prompts, args. Regression-test asserts.
6. **Archive dir noted.** `.claude/state/session-signals/archive/` exists; scanner does NOT ingest it in v1 — another "widen later" opportunity for a future PR alongside any log-rotation changes.

Deltas 1, 3, 4, 5, 6 applied unilaterally per standing preferences. Delta 2 confirmed by user (option 2a — honest narrow window).

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
**Wave v2 (2026-04-17, stance-contract applied):**

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR | Pseudocode uses flat `event.tool_name` that doesn't match real Claude Code nested-content schema; 90d promise impossible against 15d retention; tier-demotion merge rule unspecified; zero-invocation acceptance not satisfied by pseudocode; PII not addressed; MCP tools vs Skill tools conflated |
| Codex | MAJOR | (see scripts/review/results/2026-04-17-plan-2320-codex.md) |
| Gemini | MAJOR | (see scripts/review/results/2026-04-17-plan-2320-gemini.md) |

**Overall result:** FAIL — MAJOR from all three. Plan requires revision before user approval.

**Blockers to resolve before approval:**
- Reconcile 90-day signal with 15-day log retention (either narrow to 15d, add archive ingestion, or label as best-available with explicit semantics).
- Document concrete JSON schema for Skill-tool invocations per provider (Claude Code, Codex, Gemini), with fixtures; or narrow v1 to Hermes/Claude only.
- Specify tier transition distinguishing COLD vs DEAD with tests.
- Parameterize the skills discovery path; add `skill-health-dashboard.sh` integration test.

---

## Risks and Open Questions

- **Risk:** Different Skill-tool invocation event formats across `claude-code`, `codex`, and `gemini` session logs — parser must handle all three aliases.
- **Risk:** Session logs rotate (15-day retention); 90-day window cannot be computed in-full without archived logs. Mitigation: treat older windows as "best-available signal", document caveat in report.
- **Risk:** The skill-patches.jsonl log (40 entries, create/modify events only) might be mistaken for invocation log — clearly document the distinction in script docstring.
- **Open:** Should demotion threshold be `invocations_90d==0` or `<N`? Recommend: `0` for v1, tune later based on data.
- **Open:** Should we aggregate across machines? #2320 body says per-machine v1 — confirming that holds.

---

## Complexity: T2

**T2** — one new script, one modified script, new test suite, fixture, report artifact. No cross-machine coordination. Depends on #2280/#2282 policy but does not block them.
