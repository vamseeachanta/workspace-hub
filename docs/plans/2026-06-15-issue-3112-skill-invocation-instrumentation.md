# Plan for #3112: Instrument true skill invocation (FINALIZED — verified design)

> **Status:** plan-review
> **Complexity:** T3
> **Date:** 2026-06-15
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3112
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-15-plan-3112-claude.md (empirical proof + adversarial)

---

## Why this supersedes the earlier draft
Earlier scope ("build instrumentation") was wrong — the scanner/report/demotion chain already exists. **Empirical verification** (running the real functions, no edits) found the actual two defects and the exact fix. The premise is therefore *proven*, not asserted.

## VERIFIED FINDINGS (reproduction — Step 1.5 satisfied empirically)
- **Emit contract:** `skill-invocation-scanner.py` consumes session-log records `{"skill_name": <key>, "ts": <iso8601>, "session_id": <id>}`. `apply_invocation_demotion` (`skill-usage-report.py:355`) demotes ONE tier only when `coverage_days >= 14 AND session_count == 0` (conservative; never promotes).
- **BUG 1:** no producer emits `skill_name` events → 0 invocations / 0-day coverage over 57 live sessions. **NOTE:** `.claude/hooks/session-logger.sh:27` is ALREADY the PostToolUse producer (captures `file_path`+`session_id`) — **extend it with a `skill_name` field; do NOT create a parallel hook** (avoids double-emit race).
- **BUG 2 (proven):** join-key mismatch. Scanner keys rows by **rel-path** (`skill-invocation-scanner.py:100`); report keys tiers by **short_name** (`skill-usage-report.py:12,26`, frontmatter `name`). The `.get(entry["skill"])` join (`:371`) never matches → silent no-op even with data.
  ```
  # /tmp/proof_3112_join.py (importlib, real functions, identical 0-session/20d data):
  rel-path key   -> demotions=0  (account-research stays HOT)
  short_name key -> demotions=1  (account-research -> WARM)
  ```
- **BUG 3 (verified):** the chain is not wired end-to-end. `skill-health-dashboard.sh:130` runs the scanner but **never passes `--invocation-data`** to `skill-usage-report.py` (`:139` uses a separate USAGE_DIR). So demotion never runs in production even with BUG 1+2 fixed. Wiring the dashboard is a required deliverable.
- **Universe mismatch:** scanner `discover_skills` walks all 3,180 SKILL.md; report `scan_skills` excludes `_archive/_core/_internal` → 833. Must reconcile the exclusion sets or the join silently carries/misses skills.

## Reconciliation decision (locked): canonical short_name end-to-end
Every downstream consumer (`skill-scores.yaml`, tier_lookup, retirement gate) keys on `short_name`. **Correct derivation (verified):** `short_name = frontmatter "name" lowercased, else dir basename` (`skill-usage-report.py:92,150-153`) — do NOT use `_skill_name_from_path` (it returns rel-path; that was the BUG-2 source). Centralize in one `derive_short_name(skill_md_path)` helper used by emit + scanner.
**Collision handling (required):** 75/833 skills have frontmatter `name` ≠ basename; 2 confirmed short_name collisions (`session-corpus-audit`, `gmail-data-extraction` — the latter because the report excludes `_archive` but NOT `_archived`). The helper must detect collisions and the exclusion sets must be reconciled so a collision can't merge two skills' signals.

## Deliverable
A skill-invocation signal feeding the existing chain: a PostToolUse hook emits `{skill_name: short_name, ts, session_id}` for Skill-tool calls + Reads of `.claude/skills/**/SKILL.md`; the scanner keys on short_name (BUG 2 fix); a backfill reconstructs history from transcripts; the retirement threshold is re-tuned for the new metric scale.

## Files to Change
| Action | Path | Reason |
|---|---|---|
| **Modify** | .claude/hooks/session-logger.sh | add `skill_name` (short_name) when tool=Read of SKILL.md or tool=Skill — EXTEND existing producer, not a new hook |
| Verify+Modify | .claude/settings.json | confirm Skill tool fires PostToolUse + exposes an id field (EMPIRICALLY UNVERIFIED — gate item); add `Skill` to the matcher if so |
| Modify | scripts/skills/skill-invocation-scanner.py | key classify()/discover on short_name (BUG 2) via shared derive_short_name; reconcile exclusion set with the report |
| **Modify** | scripts/skills/skill-health-dashboard.sh | wire `--invocation-data <scanner output>` into the usage-report call (BUG 3 — the end-to-end gap) |
| Reuse | scripts/skills/skill_execution_tracker.py | backfill should REUSE `_extract_skill_name_from_path` (already extracts skill from session logs) — don't duplicate |
| Modify | scripts/skills/check_retirement_candidates.py | consume session_count / re-tune so working demotion doesn't mass-flag |
| **Modify** | tests/skills/test_skill_invocation_scanner.py, test_usage_report_invocation_demotion.py | existing tests assert rel-path keys — update for short_name (drop the false "unaffected" AC) |
| Create | scripts/skills/tests/test_skill_invocation_join.py | promoted BUG-2 regression proof |

## TDD Test List (write first)
| Test | Verifies |
|---|---|
| test_join_shortname_matches (from /tmp/proof) | scanner output key joins report tier key (BUG 2 regression) |
| test_emit_read_skillmd | PostToolUse Read of SKILL.md → one event w/ correct short_name |
| test_emit_skill_tool | Skill tool call → event; plugin id `superpowers:x`→`x` normalized |
| test_emit_non_skill_read_ignored | Read of non-skill file → no event, fast-exit |
| test_short_name_from_frontmatter | derive_short_name uses frontmatter `name`, falls back to basename |
| test_scanner_keys_shortname | classify() rows keyed by short_name, not rel-path |
| test_demotion_fires_end_to_end | emit→scan→report demotes a zero-session HOT skill (coverage≥14) |
| test_backfill_idempotent | re-run produces no duplicate events |

## Acceptance Criteria
- [ ] Tests above pass; existing scanner/report/retirement tests unaffected.
- [ ] Hook emits short_name events; verified cheap (no measurable latency on ordinary Reads; fast-exit proven).
- [ ] Scanner + emit + report all key on short_name; **a zero-session skill with ≥14d coverage actually demotes** (BUG 2 closed end-to-end).
- [ ] Backfill reconstructs historical events; documents the pre-instrumentation blind spot.
- [ ] `check_retirement_candidates.py` threshold re-tuned; show it does NOT mass-flag under real counts.
- [ ] @-include/progressive-disclosure remains an explicit documented blind spot (out of v1 scope).

## Adversarial Review Summary
| Provider | Verdict | Findings (all incorporated above) |
|---|---|---|
| Claude empirical proof | PASS | BUG 2 join mismatch proven via real functions (`/tmp/proof_3112_join.py`). Premise not in doubt. |
| Claude adversarial (impl surface) | **MAJOR → incorporated** | Found BUG 3 (dashboard not wired); `derive_short_name` must NOT use `_skill_name_from_path`; 2 short_name collisions + `_archived` exclusion gap; 3,180-vs-833 universe mismatch; existing scanner/demotion tests assert rel-path (false "unaffected" AC); reuse `session-logger.sh` + `skill_execution_tracker.py` instead of new files; Skill-tool PostToolUse contract empirically unverified. All folded into Files-to-Change + Risks. |
| Codex / Gemini | NOT RUN | T3 escalation available at implementation start |

**Overall result:** MAJOR findings incorporated → spec is now accurate. **Recommend a confirmatory re-review at implementation start.** Then USER approval required before any code write (gate-blocked; agent cannot self-approve). Empirical verification before coding turned a "quick emit-step add" into a correctly-scoped 3-bug change — six adversarial passes this session, each caught real defects pre-code.

## Risks
- **short_name collisions:** two skills with the same frontmatter `name` in different dirs collide on the key. Mitigation: detect + warn at derive time; the report already keys this way, so collisions are pre-existing, not introduced.
- **Hook cost:** PostToolUse fires on every Read — fast-exit on non-`/skills/.../SKILL.md` paths is mandatory; benchmark in test.
- **Concurrent append:** parallel sessions appending one file → use per-day file (`skill-invocations/YYYY-MM-DD` dir, matching #2320 convention) not a single JSONL, to avoid interleave corruption.
- **Threshold scale:** real counts are small (0–few); `check_retirement_candidates.py:91` was tuned to cross-ref magnitudes → MUST re-tune or it mass-flags. (Caught in prior review; carried here.)

## Complexity: T3
Touches hook layer + scoring substrate consumed ecosystem-wide. Focused adversarial review on implementation surface, then user approval before any write (gated).
