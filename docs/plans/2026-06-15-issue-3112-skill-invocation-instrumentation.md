# Plan for #3112: Instrument true skill/command invocation

> **Status:** blocked-draft (adversarial review MAJOR — proposed building tools that already exist; corrected scope = the emit step only; see review summary)
> **Complexity:** T3
> **Date:** 2026-06-15
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3112
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-15-plan-3112-{claude,codex,gemini}.md

---

## Resource Intelligence Summary

### Existing repo code
- `scripts/skills/skill-usage-report.py:427-428` — the defect: `baseline_usage_rate = effective_refs/max_refs` (cross-ref ratio); `calls_in_period = existing.get("calls_in_period", effective_refs)` → "calls" defaults to cross-ref count. **No real invocation is ever recorded.**
- `.claude/settings.json` — **PostToolUse already matches `Read` (line ~184) and `.*` (line ~196)**, and PreToolUse matches `Read` (line ~62). So hook plumbing to observe Read/Skill events exists; nothing logs skill usage.
- `.claude/hooks/skill-content-pretooluse.sh` — prior art for a skill-path-aware hook (parses tool input, acts on `.claude/skills/` paths). Reuse its path-detection pattern.
- No skill *loader* exists: workspace-hub skills enter context by the model **Reading `SKILL.md`**; plugin/invocable skills go through the `Skill` tool (logged as plugin-namespaced IDs).

### Documents / issues consulted
- `analysis/2026-06-15-skill-sprawl-refresh-3062.md`; parked plans #3062, #3106 (both blocked on this signal).
- #3061 (continuous parity instrumentation), #1742 (gsd-aware usage tracking) — sibling measurement work; reuse the JSONL-signal + nightly-aggregation pattern.
- Memory: `project_skill_retirement_blocked_on_invocation_signal`.

### Evidence (embedded verification)
**File/line** (verified 2026-06-15):
- `skill-usage-report.py:428` → `"calls_in_period": existing.get("calls_in_period", effective_refs)` — confirms the fallback.
- `settings.json` PostToolUse `Read` matcher present (line ~184).
- Transcripts contain `Read` tool calls of SKILL.md paths (greppable) → historical signal is **backfillable**.
- `Skill` tool records `"skill":"<plugin>:<name>"` — invocable signal exists but is namespaced.

### Gaps
- No event log of skill loads/invocations; `calls_in_period` is synthetic.
- Retrieval-skill "use" is unobservable except via SKILL.md Read events (a *load* proxy, not an *applied* proxy — state this honestly).

---

## Deliverable
A model-agnostic skill-invocation signal: a PostToolUse hook logs real skill load/invoke events to `.claude/state/skill-invocations.jsonl`, a backfill reconstructs history from transcripts, and `skill-usage-report.py` consumes real counts into `calls_in_period` — so HOT/DEAD tiers and `check_retirement_candidates.py` reflect usage, not centrality.

## Pseudocode
```
# .claude/hooks/log-skill-invocation.sh  (PostToolUse: matcher "Read|Skill")
read tool_json from stdin
if tool == "Read" and path =~ \.claude/skills/.*/SKILL\.md:
    skill = derive_skill_name_from_path(path)         # dir name under skills/
    emit {ts, session, skill, kind:"load"} >> skill-invocations.jsonl
elif tool == "Skill":
    emit {ts, session, skill: tool.input.skill, kind:"invoke"} >> skill-invocations.jsonl
# fast-exit otherwise; must be cheap (fires on every Read)

# scripts/skills/backfill_skill_invocations.py
for jsonl in ~/.claude/projects/**/*.jsonl:
    for rec where tool_use Read of SKILL.md or Skill tool:
        emit load/invoke event       # reconstruct history (document: pre-instrumentation gaps)

# skill-usage-report.py change
calls_in_period = count(skill-invocations.jsonl within period) for skill   # REPLACE effective_refs fallback
keep effective_refs as a SEPARATE discoverability metric (don't conflate)
```

## Files to Change
| Action | Path | Reason |
|---|---|---|
| Create | .claude/hooks/log-skill-invocation.sh | PostToolUse Read/Skill → events |
| Create | scripts/skills/backfill_skill_invocations.py | reconstruct history from transcripts |
| Create | scripts/skills/tests/test_log_skill_invocation.sh + test_backfill_*.py | TDD |
| Modify | .claude/settings.json | wire the hook (PostToolUse matcher "Read\|Skill") |
| Modify | scripts/skills/skill-usage-report.py | calls_in_period from real events; keep refs separate |
| Update | docs/plans/README.md | index row |

## TDD Test List
| Test | Verifies |
|---|---|
| test_read_skillmd_logged | Read of `.claude/skills/x/SKILL.md` → one load event |
| test_non_skill_read_ignored | Read of a non-skill file → no event (and cheap fast-exit) |
| test_skill_tool_logged | Skill tool call → invoke event w/ correct id |
| test_skill_name_derivation | nested path → correct skill name (handles references/ subdirs) |
| test_backfill_reconstructs | sample transcript → expected events; idempotent on re-run |
| test_calls_from_events | usage-report calls_in_period = event count, not effective_refs |
| test_refs_metric_preserved | discoverability/refs still reported separately (no conflation) |

## Acceptance Criteria
- [ ] Hook logs load/invoke events; verified cheap (no measurable latency on ordinary Reads).
- [ ] Backfill reconstructs historical usage; documents the pre-instrumentation blind spot.
- [ ] `skill-usage-report.py` `calls_in_period` comes from real events; `effective_refs` retained as a distinct discoverability metric.
- [ ] **Signal-works proof:** after backfill, ≥1 currently-"DEAD" domain skill reclassifies HOT/WARM (usage ≠ centrality), and ≥1 high-centrality-but-unused skill drops — demonstrating the tiers now mean something different.
- [ ] Tests pass; existing hook/skill tests unaffected.

## Adversarial Review Summary
| Provider | Verdict | Findings |
|---|---|---|
| Claude (adversarial subagent) | **MAJOR** | The subsystem already exists and was missed (discovery-first failure): `skill-invocation-scanner.py` (#2320), `skill_execution_tracker.py` (WRK-5086), and `skill-usage-report.py:328-388` already have `load_invocation_data()`/`apply_invocation_demotion()`/`--invocation-data`. Read-of-SKILL.md is a minority/biased signal (23/3180; @-include + progressive-disclosure invisible). Changing `calls_in_period` breaks the `check_retirement_candidates.py:91` threshold. Skill-tool namespace (`superpowers:x`) ≠ disk `short_name`. Single-file JSONL append = concurrency hazard. |

**Overall result:** FAIL — re-draft NOT as "build instrumentation". **Empirically verified corrected scope:** the scanner consumes records with a `skill_name` field; live `session_*.jsonl` carry only `{context_k, effort, event, model, provider, ts}` — **no producer emits `skill_name` events**, so the scanner returns 0 invocations / 0-day coverage across 57 sessions. The ONLY missing link is the **emit step**, and its design hinges on defining "invocation" across Skill-tool / Read / @-include paths. Everything downstream already exists.

## Risks and Open Questions
- **Risk — load ≠ apply.** A SKILL.md Read means loaded-into-context, not necessarily acted on. Honest framing: it's a vastly better usage proxy than cross-refs, but still a proxy. Document it; don't overclaim.
- **Risk — hook cost / noise.** PostToolUse fires on every Read; the hook must fast-exit on non-skill paths. Measure overhead in a test.
- **Risk — session-id / privacy.** Log skill name + timestamp + session id only; no content. Stays local (`.claude/state/`), not committed beyond aggregates.
- **Risk — backfill volume.** ace-linux-1 has thousands of transcripts; backfill must stream, not load all. Cap/window by date.
- **Open — count Skill-tool plugin invocations separately** from wh-skill loads? (Different semantics.) Recommend: yes, tag `kind`. **User confirm at approval.**
- **Open — promote to cross-machine?** This is `machine:multi`; initial landing single-box, aggregate later (per #3061 pattern). **User confirm.**

## Complexity: T3
Touches the hook layer + scoring substrate that retirement/quality decisions depend on; model-agnostic signal consumed ecosystem-wide. 3-provider review warranted.
