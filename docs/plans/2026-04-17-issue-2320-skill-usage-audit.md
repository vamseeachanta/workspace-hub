# Plan for #2320: Mine session logs for dead-skill candidates — usage-signal input to #2280 weekly audit

> **Status:** draft
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

```
function scan_sessions(sessions_dir, window_days):
    invocations = defaultdict(list)  # skill_name -> [timestamp, ...]
    for each session_YYYYMMDD.jsonl in sessions_dir:
        for each line in file:
            event = json.loads(line)
            if event.tool_name in ("Skill", "activate_skill", "skill"):
                skill_name = event.tool_input.get("skill") or event.tool_input.get("skill_name")
                if skill_name:
                    invocations[skill_name].append(event.ts)
    return invocations

function classify(invocations, now, skills_root):
    all_skills = discover_skills(skills_root)  # walk .claude/skills for SKILL.md
    rows = []
    for skill in all_skills:
        ts_list = invocations.get(skill, [])
        rows.append({
            "skill": skill,
            "invocations_30d": count_within(ts_list, now, 30),
            "invocations_90d": count_within(ts_list, now, 90),
            "last_used": max(ts_list) if ts_list else None,
            "days_since_last_use": (now - max(ts_list)).days if ts_list else None,
        })
    return rows

function main():
    args = parse_args()
    invocations = scan_sessions(args.sessions_dir, args.window_days)
    rows = classify(invocations, utcnow(), args.skills_root)
    write_json(rows, f".claude/state/skill-invocations/{today}.json")
    write_csv(rows, f"data/reports/skill-usage-{today}.csv") if args.csv
```

Integration with `skill-usage-report.py`: add a "data source 5" step that reads today's `skill-invocations/YYYY-MM-DD.json` and demotes tier when `invocations_90d == 0` regardless of static references.

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

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_scan_counts_invocation | counts a single Skill event | fixture with 1 event | `{"skill-a": 1}` |
| test_scan_ignores_non_skill_tools | Read/Bash tool events not counted | fixture with mixed events | zero for those skills |
| test_scan_handles_multiple_aliases | Skill/activate_skill/skill all counted | fixture with all three | combined count |
| test_window_30d_excludes_older | 31-day-old event excluded from 30d count | fixture with old+new | 30d==1, 90d==2 |
| test_classify_zero_invocations_flags_dead | skill never invoked gets `days_since_last_use==None` | fixture missing skill | None |
| test_integration_with_tier_demotion | `invocations_90d==0` demotes HOT→COLD | fixture + mocked cross-refs | COLD tier |
| test_malformed_jsonl_line_skipped | bad JSON line does not abort | fixture with 1 bad line | valid lines parsed |

---

## Acceptance Criteria

- [ ] `uv run --no-project python scripts/skills/skill-invocation-scanner.py --sessions-dir logs/orchestrator/hermes --skills-root .claude/skills` exits 0 and writes `.claude/state/skill-invocations/YYYY-MM-DD.json`.
- [ ] Scan of 15 days (~35 MB) completes in <30 seconds on dev-secondary.
- [ ] Every `.claude/skills/**/SKILL.md` appears in output (zero-invocation rows present).
- [ ] `uv run pytest tests/skills/test_skill_invocation_scanner.py -v` passes all 7 tests.
- [ ] `scripts/skills/skill-usage-report.py` demotes tier when `invocations_90d==0`; verified via unit test.
- [ ] `scripts/skills/skill-health-dashboard.sh` runs end-to-end and includes the new audit.
- [ ] `docs/reports/skill-invocation-baseline-2026-04-17.md` records: total skills, dead (0 invocations 90d), demoted count.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MINOR | 30s perf target unmeasured; 90d vs 15d retention unresolved; tier-demotion rule conflicts with HOT criterion; PII not addressed |
| Codex | MAJOR | 90d promised but only 15d retained (underspecified/false); provider-schema not validated; tier rule doesn't distinguish COLD vs DEAD; no dashboard integration test |
| Gemini | MAJOR | 90d vs 15d causes false-positive demotions; flat event-schema assumption oversimplifies; skill discovery path hardcoded; output dir rotation not addressed |

**Overall result:** FAIL — MAJOR from Codex+Gemini. Plan requires revision before user approval.

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
