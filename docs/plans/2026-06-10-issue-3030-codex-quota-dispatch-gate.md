# Plan for #3030: Dispatch-time codex weekly-quota gate — suspend lane:codex routing when available <10%

> **Status:** adversarial-reviewed
> **Complexity:** T2
> **Date:** 2026-06-10
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3030
> **Client:** N/A
> **Project:** (none)
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-10-plan-3030-claude.md | ...-codex.md

---

## Resource Intelligence Summary

Sources consulted:

1. **`scripts/ai/assessment/query-codex-usage.sh`** — Found the canonical codex weekly-quota source: `--json` emits `{week_pct, pct_remaining, resets_at_epoch, source, updated_at}`; live app-server RPC first, falls back to `~/.codex/sessions` token_count rate_limits. Verified live 2026-06-10: `pct_remaining: 29, source: local-session-rate-limits`.
2. **`config/ai-tools/agent-quota-latest.json` (cache; statusline `quota_primary`, statusline-command.sh:60)** — Found `pct_remaining: 79` for codex at the same moment the live source reported **29%** — the cache (refreshed by `scripts/cron/provider-utilization-refresh.sh`) lags real burn by hours. **Finding: the gate must call the live-first script, not trust the cache**; a stale cache would silently keep routing to a drained codex lane.
3. **`scripts/dispatch/route.py:resolve_provider` (landed in #3029, commit `fc4d866a7`)** — Confirmed the single provider-resolution choke point. Currently returns `(provider, provider_explicit)`; the gate needs to know *why* codex was chosen (only the lane-derived choice is suspendable), so the function must also expose a provider source.
4. **`tests/dispatch/test_route_lane.py`** — 7 tests unpack the 2-tuple; extending the return shape requires updating their unpacking in the same commit (enumerated in Step 1).
5. **`.claude/memory/kanban/routing-rules.yaml:30-66`** — Confirmed hermes shares `codex_pool` but is routed only by rules/`ai:hermes`, never by lane; the gate therefore cannot affect hermes. `ai:codex` (human) and rule-assigned codex (e.g. `needs:cross-review`) carry human/rule authority and must NOT be demoted.
6. **`.claude/memory/agents.md` "Compute lane assignment" rule (`5ce951be2`)** — The governing gate text: "if codex weekly usage available drops below 10% … suspend the codex lane for the rest of that week". Strictly `< 10`; suspension scope is the *lane*, not codex generally.

Gaps (to build from scratch):
- A quota-read helper with timeout + fail-open semantics in route.py.
- A pure, testable gate decision function.
- Proposal annotation + operator-visible marker for demoted cards.

## Proposed Changes

### Step 1 — Tests first (TDD, red)

Extend `tests/dispatch/test_route_lane.py` (update existing unpacking to the new 3-tuple) and add `tests/dispatch/test_route_quota_gate.py`:

1. `resolve_provider` returns `(provider, provider_explicit, source)` with `source` in `{"ai", "rule", "lane", "default"}` — each path pinned.
2. Pure gate: `lane_quota_demotion(provider, source, remaining_pct, defaults)` →
   - codex + lane + `remaining=9.9` → demoted to `defaults.provider`, flagged;
   - codex + lane + `remaining=10.0` → NOT demoted (strict `<10`);
   - codex + `source="ai"` or `"rule"` + `remaining=2` → NOT demoted (human/rule authority stands);
   - codex + lane + `remaining=None` → NOT demoted (**fail-open**: unknown quota never blocks dispatch);
   - claude + lane → untouched at any quota.
3. Quota helper: `codex_weekly_remaining()` returns `None` on subprocess timeout/failure/malformed JSON (monkeypatched subprocess in tests; no live calls in CI).
   **Window-validity guard (r2 MAJOR-1):** a quota snapshot may drive demotion ONLY if it provably belongs to the current weekly window — `source == "app-server-live"`, OR fallback source with `resets_at_epoch > now`. A fallback snapshot with `resets_at_epoch <= now` is cross-reset stale and returns `None` (fail open, stderr warning naming the source). Within a current window, fallback staleness can only understate usage (usage is monotone within a window), so it errs toward fail-open — pinned by tests: (a) fallback + future reset + remaining 9 → demote; (b) fallback + past reset + remaining 9 → None/no demotion; (c) app-server-live + remaining 9 → demote.
4. `propose()` integration: quota helper invoked at most once per run (memoized), demoted proposals carry `"quota_demoted": True`.
5. **No sticky residue from demotion (r1 M2):** a demoted card keeps `provider_explicit=False`, so `labels_for()` emits no `ai:` label — quota flapping near the boundary between runs is cosmetic, never persisted.
6. **Pool accounting follows the demoted provider (r1 M3):** through `apply_wip`, a demoted card counts against claude per-provider/machine caps and does NOT consume `codex_pool` slots.

### Step 2 — Implementation (green)

- `resolve_provider` → 3-tuple with `source`; call sites updated.
- `codex_weekly_remaining()`: script path anchored at `ROOT / "scripts/ai/assessment/query-codex-usage.sh"` (route.py's existing repo-root constant — survives cron cwd; r1 M1); `subprocess.run([...], timeout=QUOTA_TIMEOUT_S)` (default 10s, env-overridable `DISPATCH_QUOTA_TIMEOUT`), parse `pct_remaining`; any exception → `None` + one stderr warning. **No env override in production (r2 MAJOR-2):** tests monkeypatch `codex_weekly_remaining` directly; the operator escape hatch is an explicit CLI flag `--codex-remaining=<pct>` that prints a loud stderr notice when used — it cannot be inherited silently by cron the way an env var could.
- In `propose()`: after resolution, `if provider == "codex" and source == "lane"`, fetch memoized remaining; if `remaining is not None and remaining < 10`: provider := `defaults.get("provider")`, annotate `quota_demoted: True`. `print_detail` renders a `Q!` marker on demoted cards; summary line counts demotions.
- Doc sync (r2 MINOR): one sentence appended to the compute-lane rule in BOTH `.claude/memory/templates/agents-template.md` (bridge-canonical) and the generated `.claude/memory/agents.md` (live until the 4am bridge run), stating the gate is enforced at dispatch (route.py, #3030), demotion requires a current-window quota snapshot, and unknown/stale quota fails open.

### Step 3 — Verification

- `uv run --with pyyaml pytest tests/dispatch/` — all suites green (glob + lane + new quota tests).
- `route.py` dry-run executes; with `--codex-remaining=5`, dry-run shows lane-codex cards demoted with markers and the loud override notice; with `--codex-remaining=50`, no demotions.
- `legal-sanity-scan.sh --diff-only` PASS.

## Acceptance Criteria

1. A lane-derived codex card is routed to the default provider when live codex weekly remaining `< 10%`, with `quota_demoted: True` and a visible marker; at `>= 10%` or unknown quota, behavior is identical to #3029.
2. `ai:codex`, rule-assigned codex, and hermes routing are never altered by the gate (pinned by tests).
3. Quota is read from `query-codex-usage.sh --json` (live-first), never solely from the stale-prone `agent-quota-latest.json` cache; demotion requires a current-window snapshot (`app-server-live`, or fallback with future `resets_at_epoch`); subprocess failure or cross-reset-stale data fails open with a warning naming the source.
5. No environment variable can alter gate behavior; the only override is the loud `--codex-remaining` CLI flag (pinned by a test that sets a tempting env var and asserts no effect).
4. Existing dispatch suites pass unmodified in behavior (only tuple-shape updates in test_route_lane.py).

## Adversarial Review Resolution (r3, inline)

- **r1 (Claude, inline): MINOR** — `scripts/review/results/2026-06-10-plan-3030-claude.md`; M1-M3 folded before r2 returned.
- **r2 (Codex, dispatched): MAJOR** — `scripts/review/results/2026-06-10-plan-3030-codex.md`. Both MAJORs verified and resolved: (1) window-validity guard — non-live fallback snapshots may suspend the lane only when `resets_at_epoch > now` proves the current window; cross-reset stale data fails open (this also answers codex's author question: fallback may demote only with a provably-current window, otherwise informational); (2) `DISPATCH_CODEX_REMAINING` env override removed — tests monkeypatch, operators get a loud `--codex-remaining` CLI flag. MINOR resolved: doc sync covers both the template and the generated live `agents.md`. Per the r3 inline-loop-break pattern, no re-dispatch; the r2 artifact records the pre-revision verdict.

## Risks / Notes

- **Latency**: one subprocess (≤10s timeout) per `propose()` run; route.py runs interactively/cron, not per-card — acceptable. Memoization prevents N-card amplification.
- **Stale-cache trap (found in intel)**: cache said 79% while live said 29% the same minute; design explicitly bypasses the cache. If the live script itself degrades to old session logs, its own `source`/`updated_at` fields surface that; gate still fails open on hard failure.
- **Fail-open choice**: an unreachable quota source must not strand heavy work — the gate is an optimization on top of #3029 routing, and the statusline keeps the human informed. Documented in the helper docstring.
- **"Rest of the week" semantics**: implemented as evaluate-at-dispatch-time (each run re-checks). Within a verified current window, remaining% is monotone non-increasing, so `<10%` stays true until reset — equivalent to suspension-for-the-week without persisting state. The cross-reset stale-snapshot case that would break this equivalence is excluded by the window-validity guard (r2 MAJOR-1); a snapshot that cannot be tied to the current window never demotes.

## Out of Scope

- Claude/gemini quota gates; hermes budget accounting (codex_pool concurrency already governs).
- Refreshing or fixing `agent-quota-latest.json` staleness (cron-owned, separate concern).
- Backfilling `ai:` labels or any relabeling.
