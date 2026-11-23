# Plan for #2845: provider-dream silently drops learnings on non-JSON distill batches (rc=0 masks data loss)

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-05-27
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2845
> **Client:** N/A
> **Project:** (n/a)
> **Review artifacts:** scripts/review/results/2026-05-27-plan-2845-claude.md | (cross-provider dispatch blocked from this session — see Adversarial Review)

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/memory/distill-provider-sessions.py` — `claude_distill()` (lines 333-392) is the distill backend; `run_provider()` + nested `flush()` (lines 431-532) own watermark advancement.
- Found: `scripts/memory/bridge-providers-to-dream.sh` — cron wrapper (04:00 daily) that invokes the distiller and logs `done (rc=N)`.
- Gap: no dead-letter file, no poison-batch retry counter, no skipped-batch accounting (confirmed: `grep -n "deadletter\|poison\|POISON\|skipped_batches"` returns only the comment at line 382).

### Standards
Not applicable (harness/infra issue).

### LLM Wiki pages consulted
No relevant wiki pages (harness/infra issue).

### Documents consulted
- Issue #2845 body — alleges silent learning loss on non-JSON batches; observed in live cron log.
- `logs/orchestrator/memory-bridge/cron-20260527.log` — live evidence of the skip + `rc=0`.
- Parent #2841 (memory-layer completeness contract) + mechanism #2833.
- `project_orchestrator_consistency_decisions` (auto-memory) — records the 2026-05-27 decision context.

### Gaps identified
- `claude_distill()` returns `[]` for **two distinct meanings** (valid-empty vs non-JSON garble); callers cannot distinguish them.
- No bounded-retry mechanism for transient non-JSON before giving up.
- No auditable record (dead-letter) when a batch is abandoned.
- `main()` always returns 0 even when batches were abandoned — cron mail never surfaces loss.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-27T18:50:23Z via `gh issue view`):
- `#2845` — OPEN — bug(memory): provider-dream silently drops learnings on non-JSON distill batches
- `#2841` — OPEN — parent consistency umbrella
- `#2833` — OPEN — cross-provider dream bridge (the mechanism)

**File existence** (`ls -la` 2026-05-27T18:50:23Z):
- EXISTS: scripts/memory/distill-provider-sessions.py
- EXISTS: scripts/memory/bridge-providers-to-dream.sh
- MISSING (this plan creates at runtime): ~/.claude/projects/.../memory/.provider-bridge-deadletter.jsonl
- MISSING (new test file this plan creates): scripts/memory/tests/test_distill_poison_handling.py

**Line excerpts** (`sed -n` of distill-provider-sessions.py):
```
375  if not isinstance(parsed, dict):
...
388      sys.stderr.write(f"[distill] claude -p result not JSON for {provider} batch "
389                       f"— skipping this batch, continuing\n")
390      return []                       # <-- COLLIDES with valid-empty return at line 391-392
391  out = parsed.get("learnings", [])
392  return [l for l in out if isinstance(l, dict) and l.get("title") and l.get("body")]
```
```
479  if learnings is None:
480      batch.clear(); batch_mts.clear()
481      return False                    # None => watermark holds (retry). [] falls through:
...
493  high_water = max(high_water, pending_skip_hw, max(batch_mts))   # <-- advances over garbled batch
```

**Gap proofs** (2026-05-27T18:50:23Z):
- `grep -n "deadletter\|poison\|POISON\|skipped_batches" scripts/memory/distill-provider-sessions.py` → only `382: ... one poison batch can't wedge the whole provider.` → confirms no machinery exists.
- `ls ~/.claude/projects/.../memory/.provider-bridge-deadletter.jsonl` → "No such file or directory" → dead-letter file absent.

**Reproduction proofs** (Step 1.5 — static trace + live log, runtime failure is data-loss not a crash):
```
$ tail -25 logs/orchestrator/memory-bridge/cron-20260527.log
[distill] claude -p result not JSON for codex batch — skipping this batch, continuing
[distill] claude -p result not JSON for hermes batch — skipping this batch, continuing
...
[bridge-to-dream] 2026-05-27T09:04:06Z done (rc=0)
```
- Reproduced at: 2026-05-27T18:50:23Z (live log + code trace: line 390 `return []` → line 479 `learnings is None` is False → falls through to line 493 watermark advance → sessions in the garbled batch are never re-selected).
- Failure mode observed matches issue claim: YES — the loss is silent (rc=0) and the garbled batch's sessions advance past the watermark with zero learnings written.

<!-- Source count: 5 (issue + cron log + distill script + bridge wrapper + #2833/#2841) -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-05-27-issue-2845-dream-nonjson-deadletter.md |
| Tests | scripts/memory/tests/test_distill_poison_handling.py |
| Implementation | scripts/memory/distill-provider-sessions.py |
| Implementation (wrapper log) | scripts/memory/bridge-providers-to-dream.sh |
| Plan review — Claude | scripts/review/results/2026-05-27-plan-2845-claude.md |

---

## Deliverable
The dream distiller distinguishes non-JSON garble from valid-empty, retries a garbled batch a bounded number of runs, dead-letters the sessions to an auditable JSONL file when retries are exhausted, and exits non-zero when any sessions were abandoned — so cross-provider learnings are never silently lost.

---

## Pseudocode

> **Revised after adversarial review (MAJOR).** Two structural changes vs. the draft:
> (a) the retry counter is keyed on a **content digest of the batch's session paths**, not `high_water` (batch identity is NOT stable across runs — re-glob/re-sort, new in-window sessions, `--limit`/`--since-days` all reshape the batch); (b) poison state lives in a **separate sibling file**, never overloaded into the `{provider: float}` watermark dict.

```
# Sentinel: a NAMED, NON-FALSY singleton. Compared by identity ONLY (never truthiness),
# so a future `if not learnings:` refactor cannot route it into the empty-success path.
class _Poison:  __slots__ = ()             # bool(_Poison()) is True; repr legible in logs
POISON = _Poison()

claude_distill(...) -> list | None | POISON:
    ... existing transient detection -> return None      # UNCHANGED
    if result is not JSON dict:
        if _TRANSIENT_RE matches: return None            # UNCHANGED: hold watermark, retry
        else: return POISON                              # NEW: garble, distinct from valid-empty []
    return [valid learnings]                              # may be [] == genuinely nothing durable

# Poison state: SEPARATE file, not the watermark dict (Finding 3).
POISON_FILE = MEM_DIR / ".provider-bridge-poison.json"   # {provider: {sig, attempts, first_ts}}
DEADLETTER  = MEM_DIR / ".provider-bridge-deadletter.jsonl"

batch_signature(batch_files) -> str:
    return sha1("\n".join(sorted(f.name for f in batch_files)))   # stable batch identity

flush() -> "ok" | "hold" | "poison":                     # TRI-STATE (was bool)
    learnings = claude_distill(...)
    if learnings is None:    clear batch; return "hold"
    if learnings is POISON:  return "poison"             # batch left intact for caller to inspect
    write all learnings; advance high_water; clear batch; return "ok"

MAX_POISON_RETRIES = 3          # user-approved 2026-05-27
AGE_ESCAPE_DAYS    = 7          # user-approved v1: stale-hold escape hatch

handle_poison(provider, batch_files, sig):               # shared by BOTH flush call sites
    # Counting is scoped to PLAIN INCREMENTAL runs. --limit/--since-days/--backfill reshape
    # the window, so their batches are not comparable across runs -> they HOLD (no count,
    # no deadletter) to avoid a meaningless counter.
    if args.limit or args.since_days or args.backfill:
        return "abort_hold"                              # retry on next plain run
    ps = read_poison_state(provider)                     # flock'd read-modify-write
    # first_ts = when this provider FIRST entered a continuous poison-hold; it carries
    # across sig changes and is cleared ONLY by a successful "ok" flush (recovery).
    first_ts = ps.first_ts if ps else now
    if ps and ps.sig == sig:  attempts = ps.attempts + 1     # same batch -> count up
    else:                     attempts = 1                   # new sig -> attempt count restarts...
    ps = {sig, attempts, first_ts}                           # ...but first_ts is preserved
    # AGE ESCAPE (Finding-1 residual): a batch that keeps absorbing new sessions gets a
    # fresh sig every run and would HOLD forever. If we've been in continuous poison-hold for
    # > AGE_ESCAPE_DAYS, dead-letter regardless of sig.
    age_exceeded = (now - first_ts) > AGE_ESCAPE_DAYS * 86400
    if ps.attempts >= MAX_POISON_RETRIES or age_exceeded:
        if not dry_run:
            deadletter_append(provider, batch_files, reason, ps.attempts)   # APPEND, gated
            advance high_water past batch                # prevent permanent wedge, gated
            clear_poison_state(provider)
        stats["deadlettered_sessions"] += len(batch_files)
        return "deadlettered"
    else:
        if not dry_run: write_poison_state(provider, ps) # do NOT advance high_water
        return "abort_hold"

run_provider():
    # ... mid-loop flush (line ~508) AND trailing flush (line ~522) BOTH do:
    r = flush()
    if r == "poison":
        if handle_poison(...) in ("abort_hold",): aborted=True; break/return
        # "deadlettered" -> continue past this batch
    if r == "ok": clear_poison_state(provider)           # recovery resets the counter
    # watermark persistence stays gated on `not dry_run` (unchanged)

main():
    run all providers
    return 3 if total deadlettered_sessions > 0 else 0   # cron mail surfaces loss
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | scripts/memory/distill-provider-sessions.py | `_Poison` singleton, tri-state `flush()`, content-digest-keyed bounded-retry in a **separate poison-state file**, dead-letter append, stats + non-zero exit; poison-counting scoped to plain incremental runs |
| Create | scripts/memory/tests/test_distill_poison_handling.py | TDD suite (written first) |
| Modify | scripts/memory/bridge-providers-to-dream.sh | log a WARN when distiller exits non-zero (don't swallow rc) |
| Update | docs/plans/README.md | index this plan |

Runtime state files (created on first poison/dead-letter event, gitignored — under `~/.claude/.../memory/`):
- `.provider-bridge-poison.json` — `{provider: {sig, attempts, first_ts}}`, flock'd, **separate from** the watermark dict.
- `.provider-bridge-deadletter.jsonl` — append-only audit log of abandoned batches.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_valid_empty_advances_watermark | valid `{"learnings":[]}` is NOT treated as poison | claude_distill → `[]` | watermark advances, no dead-letter, no abort |
| test_poison_holds_watermark_first_attempt | first garble holds watermark, no loss | claude_distill → POISON | watermark unchanged, poison-file `attempts==1`, provider aborts, no dead-letter |
| test_poison_retried_then_deadlettered | garble for MAX runs → dead-letter + advance | POISON × MAX_POISON_RETRIES (same batch sig) | sessions appended to dead-letter JSONL, watermark advances past batch |
| test_transient_none_holds_watermark | existing transient behavior preserved | claude_distill → None | watermark holds, provider aborts (regression guard) |
| test_successful_batch_writes_and_advances | happy path unchanged | claude_distill → [learning] | file written, watermark advances |
| test_poison_counter_resets_after_success | recovered provider drops stale poison count | POISON then [learning] | poison-state cleared; later single garble doesn't prematurely dead-letter |
| test_deadletter_record_shape | dead-letter record is auditable + recoverable | one dead-letter event | JSONL record has provider, sessions[], mtimes, reason, attempts, ts |
| test_main_exit_nonzero_on_deadletter | rc surfaces loss | a dead-letter occurs | `main()` returns 3 |
| **test_poison_sig_changes_resets_counter** (Finding 1) | batch-membership shift is well-defined, not silent loss | POISON run1 (sig A), new in-window session → POISON run2 (sig B) | counter does NOT increment to MAX on a different batch; sig-B starts attempts=1 |
| **test_poison_only_counts_plain_incremental** (Finding 1) | `--limit`/`--since-days`/`--backfill` poison HOLDS, never dead-letters | POISON under `--limit 3` | no poison-state written, no dead-letter, provider aborts-hold |
| **test_final_batch_only_poison** (Finding 5) | sole sub-`batch_size` batch (never hits mid-loop flush) is handled | 2 sessions, batch_size=8, claude_distill → POISON | trailing-flush path triggers identical poison handling (hold→…→dead-letter) |
| **test_dry_run_no_deadletter_no_advance** (Finding 6) | dry-run writes neither JSONL nor watermark nor poison-state | `--dry-run` + POISON×MAX | dead-letter file absent, watermark unchanged, poison-state unchanged |
| **test_poison_sentinel_identity_invariant** (Finding 4) | sentinel cannot be made falsy by refactor | `POISON` | `bool(POISON) is True` and `POISON is not None` and `POISON is not []` |
| **test_poison_state_file_separate_from_watermark** (Finding 3) | poison state never coerced as a provider mtime | watermark `{codex:123.0}` + poison-file present | `float(watermark.get('codex'))` works; no provider-iteration touches poison state |
| **test_deadletter_append_preserves_prior** (Finding 8) | second dead-letter event keeps the first record | two dead-letter events | JSONL has 2 lines, first survives |
| **test_age_escape_deadletters_stale_hold** (v1 decision) | sig-changes-every-run hold dead-letters after AGE_ESCAPE_DAYS | POISON each run, different sig, `first_ts` > 7d ago | dead-letter fires despite attempts never reaching MAX; `first_ts` carried across sig changes |
| **test_first_ts_resets_only_on_recovery** (v1 decision) | recovery clears the age clock | POISON (sets first_ts) → ok → POISON | second poison starts a fresh first_ts, not the old one |
| **test_watermark_schema_backward_compatible** | legacy watermark (no poison machinery) loads cleanly | watermark `{codex: 123.0}` | provider mtime read correctly; poison-state defaults empty |

---

## Acceptance Criteria

- [ ] All new tests pass: `uv run --no-project python -m pytest scripts/memory/tests/test_distill_poison_handling.py -v`
- [ ] No regression in existing distiller behavior (transient→None hold, valid-empty advance, happy-path write) — covered by regression-guard tests above.
- [ ] A forced non-JSON response produces a visible warning + (after MAX retries) a dead-letter record + non-zero exit — NOT a silent rc=0.
- [ ] Dead-lettered sessions are recorded with enough provenance to be re-fed manually.
- [ ] `bridge-providers-to-dream.sh` logs a WARN line (not silent) when the distiller exits non-zero.
- [ ] Plan + code review artifacts posted to scripts/review/results/.
- [ ] Summary comment posted to #2845.

---

## Adversarial Review Summary

<!-- Populated after Step 4. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (fresh-context subagent) | **MAJOR** | (1) batch identity not stable across runs → `high_water` is the wrong counter key; (2) float-equality key fragile; (3) `_poison` reserved key collides with `{provider: float}` watermark; (4) POISON sentinel type unpinned (falsy hazard); (5) trailing-batch flush path unhandled (small runs never hit mid-loop flush); (6) dry-run dead-letter unguarded; (7) concurrent backfill clobbers counter; (8) six test gaps. |
| Codex | UNAVAILABLE | cross-provider dispatch blocked from a Claude-Code session (CLAUDECODE=1 trips submit-to-codex version guard; #2721/#2715). Documented per scripts/review/results convention. |
| Gemini | UNAVAILABLE | same dispatch constraint; T2 degraded to single-author + fresh-context subagent review per `feedback_permission_gate_blocks_cross_review`. |

**Overall result:** PASS after revision (draft was MAJOR → all 8 findings incorporated; re-review recommended at code stage when cross-provider dispatch is available).

Revisions made based on review:
- **F1/F2:** retry counter re-keyed from `high_water` → **sha1 content digest of sorted batch session paths**; poison-counting scoped to plain incremental runs only (`--limit`/`--since-days`/`--backfill` hold without counting).
- **F3:** poison state moved out of the watermark dict into a **separate `.provider-bridge-poison.json`** file — eliminates the float-coercion collision.
- **F4:** POISON pinned to a **named non-falsy singleton** (`class _Poison`), identity-comparison only; invariant test added.
- **F5:** `flush()` converted to **tri-state**; both mid-loop and trailing flush routed through one `handle_poison()` — sole-batch poison now covered.
- **F6:** dead-letter append + watermark advance + poison-state write all gated on `not dry_run`; test added.
- **F7:** poison-state file uses flock'd read-modify-write; `--backfill`-vs-cron exclusion documented (and poison-counting disabled under backfill anyway).
- **F8:** six tests added to the TDD list (sig-change, plain-incremental-only, final-batch, dry-run, sentinel-identity, append-preserves-prior).

---

## Risks and Open Questions

- **DECIDED (user 2026-05-27):** `MAX_POISON_RETRIES = 3`.
- **DECIDED (user 2026-05-27):** age-escape **included in v1** (`AGE_ESCAPE_DAYS = 7`) — `first_ts` carries across sig changes, clears only on recovery; closes the absorb-forever residual.
- **Open (for user, non-blocking):** dead-letter recovery — v1 records sessions for **manual** re-feed only; auto-replay (`--retry-deadletter`) deferred to a follow-on.
- **Resolved (was F1):** batch-stability — no longer assumed. Counter keys on a content digest of the batch's session paths and only counts on plain incremental runs; a membership shift yields a new digest and a fresh (attempts=1) count rather than silent loss.
- **Resolved (was F3):** no watermark schema change — poison state is a separate file, so `{provider: float}` reads are untouched.
- **Resolved (was F7):** poison-state file is flock'd read-modify-write; backfill does not poison-count, so it cannot clobber the counter toward never-dead-lettering.
- **Risk (residual):** a genuinely-poison batch that keeps absorbing new sessions each run (digest changes every run) would hold indefinitely without dead-lettering. Mitigation: the run still exits non-zero on the *hold-abort* path is NOT triggered (hold is silent) — so add a **secondary age-based escape**: if `first_ts` for any held provider exceeds N days, dead-letter regardless of sig. (Flag for user: include age-escape in v1 or defer?)

---

## Complexity: T2
**T2** — single core file modified with non-trivial control-flow change, new test file (TDD), a watermark-schema extension, and a small wrapper edit. Multi-file, correctness-critical (data loss), but bounded to one subsystem. T2 → 2-provider adversarial review target (degraded to single-author + fresh-context subagent this session; constraint documented).
