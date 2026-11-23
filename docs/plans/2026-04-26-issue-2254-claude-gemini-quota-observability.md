# Plan for #2254: fix(provider-telemetry): improve Claude and Gemini quota observability for exact weekly targeting

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-26
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2254
> **Review artifacts:** scripts/review/results/2026-04-26-plan-2254-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/ai/assessment/query-quota.sh` — main entry point. Calls `query_claude`, `query_codex`, `query_gemini` from `lib/providers.sh` and writes `config/ai-tools/agent-quota-latest.json`.
- Found: `scripts/ai/assessment/lib/providers.sh` — implements all three provider probes. `query_claude()` (lines 138-175) returns `source: "unavailable"` whenever `get_claude_oauth_entry()` finds no validated `oauth-api` entry; the OAuth path is the only authoritative branch and currently never populates. `query_gemini()` (lines 220-247) hardcodes `source: "estimated"` and counts files in `~/.config/gemini/tmp` against a `GEMINI_DAILY_REQUESTS=1000` ceiling; it never reads any authoritative usage signal even though `~/.config/gemini/state.json` is consulted but typically empty for `dailyRequestCount`.
- Found: `scripts/cron/provider-utilization-refresh.sh` — orchestrates `query-quota.sh --refresh --log`, then `credit-utilization-tracker.py`, scorecard, work-queue, and autolabel scripts. This is the only refresh path that writes the latest snapshot.
- Found: `scripts/ai/credit-utilization-tracker.py` (referenced by refresh cron) — generates `provider-utilization-weekly.json` and the markdown report; already includes `quota_basis`, `quota_source`, `utilization_basis` fields per provider per week. It is the surface where confidence semantics will be widened.
- Found: `scripts/ai/provider-routing-scorecard.py` — generates `provider-routing-scorecard.json` and surfaces `quota_basis: unavailable | estimated_daily_quota | quota`. Recommendations include the warning "Telemetry is weak; treat utilization as directional, not exact weekly headroom" — that warning will be driven by a new explicit confidence flag rather than inferred from `quota_source`.
- Found: `scripts/ai/assessment/lib/providers.sh::get_ccusage_weekly()` — pulls token/cost from `npx ccusage weekly --json` against Claude session JSONL. Currently used only as auxiliary enrichment when an authoritative OAuth entry exists; never used as a primary signal because the OAuth gate keeps it out.
- Found: `scripts/operations/monitoring/check_claude_usage.sh` — separate, log-file-based per-call ledger at `~/.workspace-hub/claude_usage.log`. Not wired into the routing pipeline; an alternative local-history source.
- Found: `scripts/readiness/provider-cost-tracker.sh` — model-registry-priced cost estimator from `.claude/state/session-signals/*.jsonl`. Best-effort and produces `cost-tracking.jsonl`; an alternative bottom-up estimator usable when first-party telemetry is unavailable.

### Standards

Not applicable — telemetry/observability work, no engineering-standards bundle.

### LLM Wiki pages consulted

No relevant wiki pages — this is harness/observability scope, not domain knowledge.

### Documents consulted

- `docs/plans/2026-04-22-issue-2332-provider-audit-python3-runtime-cleanup.md` — prior provider-audit plan; established the `provider_session_ecosystem_audit.py` artifact path used as a secondary input by the routing scorecard.
- `docs/plans/2026-04-22-issue-2333-provider-audit-drift-classification-expansion.md` — prior plan that expanded the audit drift classes; demonstrates the audit/scorecard input contract this plan will preserve.
- `docs/plans/2026-04-25-provider-usage-inventory-readiness-exit-handoff.md` — exit handoff for the provider-usage inventory pass, includes the "telemetry is directional only" caveat that #2254 directly targets.
- Issue body for #2254 — explicit acceptance: Claude stronger than `unavailable`, Gemini stronger than `estimated`, reports distinguish exact vs heuristic confidence, fallback remains safe.
- Parent #1838 — strategy issue; horses-for-courses routing requires precise quota signals to hit `<25%` Gemini target and `<15%` underutilization floor.
- Context #2089 — weekly Hermes + AI provider review; this work feeds the weekly review's "exact-vs-heuristic" delta.
- Context #2108 — cron scrub for stale `exhausted_*` cache entries; constrains how the new Claude/Gemini probes write into `~/.cache/agent-quota.json` so they participate in the same staleness contract.
- Context #2109 — codex_quota tests; pattern reference for the test matrix proposed below (telemetry-available, telemetry-unavailable, mixed-confidence aggregation).

### Gaps identified

- No live Anthropic-side usage probe. `query_claude()` only knows how to read `~/.claude/stats-cache.json` (an internal CLI tracker) and an `oauth-api`-tagged entry that is never produced today. There is no script that calls `https://api.anthropic.com/v1/organizations/{org_id}/usage_report/messages` (Admin API).
- No live Gemini quota probe. `query_gemini()` infers from filesystem mtime. There is no script that exercises Gemini CLI's quota subcommand or calls Google AI Studio quota endpoints.
- No explicit confidence-level field in any artifact. Reports overload `quota_source` (`unavailable | estimated | history.jsonl | oauth-api`) to mean both *origin* and *trustworthiness*. Downstream consumers cannot programmatically partition exact vs heuristic.
- No fallback hierarchy contract. The current implementation is single-source per provider with hard-coded fallback inside one function; new sources cannot be added without editing the function body and there is no priority order recorded in artifacts.
- No tests covering telemetry-available, telemetry-unavailable, and mixed-confidence aggregation paths.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-26 via `gh issue view`):
- `#2254` — OPEN — fix(provider-telemetry): improve Claude and Gemini quota observability for exact weekly targeting
- `#1838` — OPEN — AI credit utilization governance — horses-for-courses routing with Gemini as first-class provider
- `#2089` — OPEN — feat(harness): weekly Hermes + AI provider settings review for repo ecosystem
- `#2108` — OPEN — chore(harness): add cron job to scrub stale quota cache entries
- `#2109` — OPEN — test(hermes): add test coverage for codex_quota reset-time recovery and stale cache handling

**File existence** (`ls` 2026-04-26):
- EXISTS: `scripts/ai/assessment/query-quota.sh`
- EXISTS: `scripts/ai/assessment/lib/providers.sh`
- EXISTS: `scripts/ai/assessment/lib/utils.sh`
- EXISTS: `scripts/ai/assessment/lib/display.sh`
- EXISTS: `scripts/cron/provider-utilization-refresh.sh`
- EXISTS: `scripts/ai/credit-utilization-tracker.py`
- EXISTS: `scripts/ai/provider-routing-scorecard.py`
- EXISTS: `scripts/ai/provider-work-queue.py`
- EXISTS: `scripts/ai/provider-autolabel.py`
- EXISTS: `config/ai-tools/agent-quota-latest.json`
- EXISTS: `config/ai-tools/provider-utilization-weekly.json`
- EXISTS: `config/ai-tools/provider-routing-scorecard.json`
- EXISTS: `docs/reports/provider-utilization-weekly.md`
- EXISTS: `~/.claude/stats-cache.json`, `~/.claude/.credentials.json`
- EXISTS: `~/.config/gemini/state.json`, `~/.config/gemini/oauth_creds.json`
- MISSING (new — this plan creates): `scripts/ai/assessment/lib/claude_quota_probes.sh`
- MISSING (new — this plan creates): `scripts/ai/assessment/lib/gemini_quota_probes.sh`
- MISSING (new — this plan creates): `scripts/ai/assessment/tests/test_quota_probes.sh`
- MISSING (new — this plan creates): `tests/ai/test_credit_utilization_confidence.py`

**Line excerpts** (`scripts/ai/assessment/lib/providers.sh` lines 138-175 — current Claude probe):
```
query_claude() {
    local oauth
    oauth=$(get_claude_oauth_entry)
    if [[ -n "$oauth" ]]; then
        _enrich_with_ccusage "$oauth"
        return
    fi
    ...
    jq -n ... '{ provider:"claude", ..., source:"unavailable" }'
}
```

**Gap proofs**:
- `grep -n 'anthropic\|admin.*api\|usage_report' scripts/ai/assessment/lib/providers.sh` → no matches → confirms no Admin-API probe today.
- `grep -rn 'gemini.*usage\|generativelanguage.*usage' scripts/ai/` → no matches → confirms no live Gemini usage probe.
- `grep -n 'confidence' config/ai-tools/provider-utilization-weekly.json` → no matches → confirms no confidence field exists.

Distinct-source count: 9 (issue body + 4 prior plans/issues + 4 source files). Meets ≥3 contract.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-26-issue-2254-provider-telemetry-quota-observability.md |
| Probe lib (Claude) | scripts/ai/assessment/lib/claude_quota_probes.sh |
| Probe lib (Gemini) | scripts/ai/assessment/lib/gemini_quota_probes.sh |
| Probe shell tests | scripts/ai/assessment/tests/test_quota_probes.sh |
| Aggregation tests | tests/ai/test_credit_utilization_confidence.py |
| Modified probe entry | scripts/ai/assessment/lib/providers.sh |
| Modified aggregator | scripts/ai/credit-utilization-tracker.py |
| Modified scorecard | scripts/ai/provider-routing-scorecard.py |
| Modified report writer | scripts/ai/credit-utilization-tracker.py (md emission) |
| Plan review — Claude | scripts/review/results/2026-04-26-plan-2254-claude.md |
| Plan review — Codex | scripts/review/results/2026-04-26-plan-2254-codex.md |
| Plan review — Gemini | scripts/review/results/2026-04-26-plan-2254-gemini.md |

---

## Deliverable

A provider-telemetry layer that will (a) attempt stronger live data sources for Claude and Gemini quota with documented fallback hierarchies, (b) emit a new `confidence_level` field in `agent-quota-latest.json`, `provider-utilization-weekly.json`, and `provider-routing-scorecard.json`, and (c) preserve existing fallback semantics so reports remain produced even when live telemetry is unavailable.

---

## Pseudocode

```
# scripts/ai/assessment/lib/claude_quota_probes.sh

probe_claude_admin_api():
    if ANTHROPIC_ADMIN_KEY env var unset OR ANTHROPIC_ORG_ID unset:
        return "" (signal: not-configured)
    response = curl GET https://api.anthropic.com/v1/organizations/{ORG_ID}/usage_report/messages
                with Authorization: Bearer $ANTHROPIC_ADMIN_KEY,
                anthropic-version header,
                starting_at = monday_iso(),
                bucket_width = 1d
                with --max-time 10
    if HTTP != 200: log non-fatal warning, return ""
    parse JSON, sum input+output messages this ISO week
    return JSON entry { source: "anthropic-admin-api", confidence_level: "exact",
                        week_messages, weekly_limit, pct_remaining, ... }

probe_claude_stats_cache():
    # existing query_claude_stats() body, retagged confidence_level: "heuristic"
    # because CLI-side stats-cache.json under-counts subagent traffic and lags
    return JSON entry { source: "stats-cache.json", confidence_level: "heuristic", ... }

probe_claude_ccusage():
    # bottom-up token-cost estimate from session JSONL via npx ccusage
    # confidence_level: "heuristic" (cost-driven, not message-quota-driven)
    return JSON entry { source: "ccusage", confidence_level: "heuristic", ... } or ""

probe_claude_oauth_cache():
    # existing get_claude_oauth_entry() — only fires if some upstream
    # process previously wrote an oauth-api entry into the cache.
    # confidence_level: "exact"
    return JSON entry { source: "oauth-api", confidence_level: "exact", ... } or ""

resolve_claude():
    for probe in [probe_claude_admin_api,
                  probe_claude_oauth_cache,
                  probe_claude_stats_cache,
                  probe_claude_ccusage]:
        result = probe()
        if non-empty: return result
    return { source: "unavailable", confidence_level: "absent",
             pct_remaining: null, ... }   # preserve current shape


# scripts/ai/assessment/lib/gemini_quota_probes.sh

probe_gemini_cli_quota():
    if `gemini` not on PATH OR `gemini quota --json` unsupported: return ""
    response = run with timeout 5s
    if exit != 0: return ""
    parse, return JSON entry { source: "gemini-cli-quota",
                               confidence_level: "exact", today_messages, daily_limit, ... }

probe_gemini_state_json():
    # read ~/.config/gemini/state.json's dailyRequestCount when populated
    # confidence_level: "heuristic" (CLI-internal counter, may reset late)
    return JSON entry { source: "gemini-state-json",
                         confidence_level: "heuristic", ... } or ""

probe_gemini_tmp_filecount():
    # existing logic — confidence_level: "estimated"
    return JSON entry { source: "estimated", confidence_level: "estimated", ... }

resolve_gemini():
    for probe in [probe_gemini_cli_quota,
                  probe_gemini_state_json,
                  probe_gemini_tmp_filecount]:
        result = probe()
        if non-empty: return result
    return { source: "unavailable", confidence_level: "absent", ... }


# scripts/ai/credit-utilization-tracker.py — new aggregation rules

derive_confidence_level(provider_entries_for_week):
    confidences = set(entry.confidence_level for entry in entries)
    if confidences == {"exact"}:        return "exact"
    if "exact" in confidences:           return "mixed"   # at least one exact source
    if "heuristic" in confidences:       return "heuristic"
    if "estimated" in confidences:       return "estimated"
    return "absent"

routing_confidence(weekly_payload):
    # exposed in provider-routing-scorecard.json:
    # confidence per provider + overall_targeting_confidence:
    #   "exact"  if all of {claude, codex, gemini} are exact
    #   "mixed"  if any one is exact and others are heuristic/estimated
    #   "heuristic" if none are exact but at least one is heuristic
    #   "estimated" if all are estimated
    #   "absent" if none have data
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | scripts/ai/assessment/lib/claude_quota_probes.sh | Encapsulate Claude probe ladder (Admin API → OAuth cache → stats-cache → ccusage) |
| Create | scripts/ai/assessment/lib/gemini_quota_probes.sh | Encapsulate Gemini probe ladder (CLI quota → state.json → tmp filecount) |
| Modify | scripts/ai/assessment/lib/providers.sh | Replace `query_claude()` and `query_gemini()` bodies with calls into the new probe libs; preserve external JSON shape and add `confidence_level` |
| Modify | scripts/ai/credit-utilization-tracker.py | Read `confidence_level` from `agent-quota-latest.json` and propagate to weekly artifacts; add `confidence_level` and `targeting_confidence` to each weekly provider record; emit confidence column in markdown |
| Modify | scripts/ai/provider-routing-scorecard.py | Surface per-provider `confidence_level` and a top-level `overall_targeting_confidence`; replace the hardcoded "Telemetry is weak" string with confidence-driven recommendation text |
| Create | scripts/ai/assessment/tests/test_quota_probes.sh | Bash test fixtures for probe ladder (mock curl, mock gemini CLI, missing-config path, timeout path) |
| Create | tests/ai/test_credit_utilization_confidence.py | Pytest coverage for confidence derivation and mixed-aggregation logic |
| Modify | docs/plans/README.md | Add this plan to the index |
| Modify | config/ai-tools/agent-quota-latest.json | Schema update — confidence_level field per agent (auto-emitted by query-quota refresh) |
| Modify | config/ai-tools/provider-utilization-weekly.json | Schema update — confidence_level + targeting_confidence per week per provider |
| Modify | docs/reports/provider-utilization-weekly.md | Add Confidence column, add overall targeting-confidence callout |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_claude_admin_api_path_returns_exact | When `ANTHROPIC_ADMIN_KEY` set and mock 200 response, probe returns `confidence_level: exact`, `source: anthropic-admin-api` | Mock curl returns valid usage_report JSON, env keys set | source==anthropic-admin-api, confidence_level==exact |
| test_claude_admin_api_404_falls_through | Mock curl returns 404 — probe returns empty so resolver tries next probe | Mock curl: 404 | resolve_claude() returns next probe's source (oauth-api or stats-cache) |
| test_claude_admin_api_timeout_falls_through | curl --max-time triggers; resolver does not block beyond budget | Slow mock that exceeds 10s | Probe returns empty within budget, resolver falls through |
| test_claude_admin_api_missing_creds_skips | Env vars unset → probe returns empty without making any HTTP call | Unset env | Probe returns "", no curl invocation |
| test_claude_stats_cache_tagged_heuristic | Stats-cache path returns heuristic confidence | Populated `~/.claude/stats-cache.json` fixture | source==stats-cache.json, confidence_level==heuristic |
| test_claude_full_unavailable | All probes empty → unavailable + confidence_level: absent | All probes mocked empty | source==unavailable, confidence_level==absent, pct_remaining==null |
| test_gemini_cli_quota_path_returns_exact | Mock `gemini quota --json` with valid output | Mock CLI binary on PATH returning `{used: 12, limit: 1000}` | source==gemini-cli-quota, confidence_level==exact |
| test_gemini_cli_missing_falls_through | `gemini` not on PATH → next probe runs | PATH stripped | resolve_gemini() returns state-json or estimated |
| test_gemini_state_json_populated | `state.json` has non-zero `dailyRequestCount` | Fixture file with `{dailyRequestCount: 47}` | source==gemini-state-json, confidence_level==heuristic |
| test_gemini_tmp_filecount_fallback | Both CLI and state.json fail; tmp directory has N files | Fixture tmp dir | source==estimated, confidence_level==estimated, today_messages==N |
| test_confidence_derive_all_exact | Aggregation produces "exact" when all entries exact | Three exact entries | weekly confidence_level==exact |
| test_confidence_derive_mixed | One exact + two heuristic produces "mixed" | Mixed entries | weekly confidence_level==mixed |
| test_confidence_derive_all_estimated | All estimated → "estimated" | Three estimated | weekly confidence_level==estimated |
| test_confidence_derive_absent | All entries absent → "absent" | Three absent | weekly confidence_level==absent |
| test_routing_scorecard_overall_targeting_confidence | Scorecard top-level summarizes per-provider | Synthetic weekly payload | overall_targeting_confidence reflects worst-case downgrade |
| test_report_md_includes_confidence_column | Markdown report renders Confidence column | Synthetic weekly JSON | markdown contains `Confidence` header and per-row value |
| test_existing_codex_path_unchanged | Codex probe behavior preserved (regression guard) | Existing history.jsonl fixture | source==history.jsonl, confidence_level==exact |
| test_artifact_schema_round_trip | Writing agent-quota-latest.json + reading via tracker preserves confidence_level | End-to-end fixture | Field survives JSON round-trip, no key dropped |
| test_rate_limit_self_throttle | Admin-API probe respects a 15-min cache TTL (does not hammer endpoint on every call) | Two consecutive probe calls within 15 min | Second call returns cached entry, no second curl invocation |

---

## Acceptance Criteria

- [ ] All new tests pass: `bash scripts/ai/assessment/tests/test_quota_probes.sh` and `uv run pytest tests/ai/test_credit_utilization_confidence.py -v`
- [ ] No regression: `uv run pytest tests/` passes
- [ ] `query-quota.sh --refresh --json` on a configured machine emits `confidence_level: "exact"` for Claude when `ANTHROPIC_ADMIN_KEY` is set; emits `"heuristic"` when only `stats-cache` is available; emits `"absent"` when nothing is configured. All three paths preserve the existing JSON shape (no key removed).
- [ ] `query-quota.sh --refresh --json` emits `confidence_level: "exact"` for Gemini when `gemini quota --json` is supported; degrades to `"heuristic"` then `"estimated"` then `"absent"` as the ladder fails.
- [ ] `provider-utilization-weekly.json` per-week per-provider records carry `confidence_level`, and the top-level payload carries `overall_targeting_confidence` for the current week.
- [ ] `provider-routing-scorecard.json` carries `confidence_level` per provider, and the recommendation text is driven by that field rather than by a hardcoded string.
- [ ] `docs/reports/provider-utilization-weekly.md` renders a Confidence column and a current-week targeting-confidence summary line.
- [ ] Fallback safety: forcibly disabling all probes (env vars unset, no `gemini` CLI, no stats-cache) results in `source: "unavailable"` / `confidence_level: "absent"` for both providers and the cron refresh exits 0.
- [ ] Probe self-throttling: Claude Admin-API probe is cached 15 min (matches existing `CACHE_TTL_SEC`) and never fires more than once per `query-quota.sh` invocation.
- [ ] Review artifacts posted to scripts/review/results/

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | — |
| Codex | PENDING | — |
| Gemini | PENDING | — |

**Overall result:** PENDING

Revisions made based on review:
- (none yet — pending review wave)

---

## Risks and Open Questions

- **Risk: Anthropic may not expose org-level message-count usage via Admin API** — the public Admin API surfaces token usage and cost, not message-count quota. Mitigation: the probe will translate token usage into a derived `pct_remaining` against the message-quota-equivalent budget where the API supports it, and will tag confidence as `exact` only for fields the endpoint actually returns. If the endpoint returns only token totals (not weekly message ceiling), the probe will tag `confidence_level: heuristic` and the resolver will continue to the OAuth/stats-cache rung. This means "exact" is conditional on the API's actual coverage; the schema will not falsely label a heuristic value as exact.
- **Risk: Console scraping fragility** — explicitly out of scope. No DOM scraping of `console.anthropic.com` or `aistudio.google.com`. The ladder is API-first or local-state-first only. If neither lands, we surface `absent` rather than scrape.
- **Risk: Rate-limit cost on the telemetry call itself** — the Admin-API probe will be wrapped by the existing 15-minute cache (`CACHE_TTL_SEC=900` in `query-quota.sh`) and will not be invoked on subagent paths (the `CLAUDE_SUBAGENT=1` skip already exists). Worst case: 96 calls/day per machine, well under any plausible Admin-API rate ceiling.
- **Risk: Gemini CLI may not ship a stable `quota` subcommand** — verified as of 2026-04-26 the CLI surface is unstable. Mitigation: probe is feature-detected (try `gemini quota --json` with `--help` first; fall through silently on unsupported); we never depend on a single command shape.
- **Risk: `confidence_level` field is consumer-breaking for downstream readers** — mitigation: addition-only schema change. Existing keys remain. New consumers opt in. Migration documented in the report header.
- **Risk: Auto-sync collisions on dirty working tree** — the issue mentions current artifacts are dirty in working tree. Implementation will land on a feature branch, regenerate artifacts last so they reflect post-merge state.
- **Risk: Mixed-confidence aggregation may surprise weekly reviewers** — mitigation: the markdown report will explicitly call out which provider drove a downgrade (e.g., "Targeting confidence: mixed — gemini estimated"). No silent rollups.
- **Open:** Should `confidence_level: absent` block the routing scorecard from emitting a recommendation, or only annotate it? Default in this plan: annotate only — preserve current behavior of producing directional recommendations.
- **Open:** Should the Admin API key live in `~/.claude/.credentials.json` (existing OAuth cred file), in `config/ai-tools/secrets.env` (new), or in env-only? Default in this plan: env-only with a documented `~/.config/workspace-hub/ai-secrets.env` autoload pattern; flag for user during approval.

---

## Complexity: T2

**T2** — bounded harness/observability change: two new shell libs, three modified scripts, schema-additive artifact changes, full TDD coverage, no engineering-standards or wiki touches.
