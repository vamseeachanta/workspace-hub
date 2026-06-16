# Plan for [#2893](https://github.com/vamseeachanta/workspace-hub/issues/2893): Statusline Provider Coverage

> **Status:** plan-approved
> **Complexity:** T3
> **Date:** 2026-06-16
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2893
> **Client:** N/A
> **Lane:** lane:claude
> **Latest review evidence:** scripts/review/results/2026-06-16-plan-2893-r14-claude.md | scripts/review/results/2026-06-16-plan-2893-r14-codex.md | scripts/review/results/2026-06-16-plan-2893-r14-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `.claude/statusline-command.sh` already owns the Claude Code quota tail and renders `C:|O:|G:` in both full and `--usage-tail` modes. It reads `config/ai-tools/agent-quota-latest.json` plus `~/.cache/agent-quota.json`, marks stale quota files with `?`, and appends weekly reset countdowns.
- Found: `.claude/statusline-combined.sh` composes the vendored GSD statusline with `.claude/statusline-command.sh --usage-tail`, so workspace-hub already has one repo-owned Claude Code statusline wrapper.
- Found: `config/ai-tools/agent-quota-latest.json` currently includes Codex `week_pct`, `five_hour_pct`, `pct_remaining`, `hours_to_reset`, `resets_at`, and `source`, but the rendered `O:` segment still omits the Codex 5-hour window.
- Found: live Claude `C:` rendering from session input already works when `rate_limits.seven_day.used_percentage` is present. The actual remaining [#2843](https://github.com/vamseeachanta/workspace-hub/issues/2843) gap for this plan is narrower: when live `rate_limits` are absent and the quota collector has no authoritative Claude OAuth entry, the statusline currently falls to `C:-%` instead of a cheap, explicitly marked local estimate or explicit unknown.
- Found: `scripts/ai/assessment/lib/providers.sh` already has `query_claude_stats()` and then deliberately does not use it in `query_claude()`: comments state "Main claude query: authoritative OAuth snapshot only" and "If unavailable, surface N/A rather than an estimated quota." This plan will preserve that shared authoritative collector policy and keep any estimate fallback local to `.claude/statusline-command.sh`.
- Found: the live `~/.cache/agent-quota.json` Codex entry on this workstation includes `five_hour_pct`, `pct_remaining`, `hours_to_reset`, `resets_at`, and `source`, so the `codex_five_hour_remaining()` cache path is observed on this machine rather than fixture-only. Tests will still cover missing `five_hour_pct` as a safe-missing branch.
- Found: `scripts/ai/assessment/query-quota.sh` and `scripts/ai/assessment/lib/providers.sh` emit Claude, Codex, and Gemini quota entries only. Hermes has no independent quota entry in this collector.
- Found: `docs/session-handoffs/2026-05-25-domain-dispatch-phase-a-b.md` and `docs/session-handoffs/2026-06-11-provider-skills-rework.md` document Hermes as using/sharing the OpenAI/Codex provider rather than a separate subscription pool. The plan will treat Hermes as an explicit `H=O` alias, not a fabricated fourth quota.
- Found: `config/agents/codex/config.toml` currently uses a legacy `[status_line]` table with usage-related items. Current official OpenAI Codex docs describe `tui.status_line`, but local review proved `codex --strict-config ... --help` does not validate config keys/items and no clean noninteractive validator is known. This plan will not migrate Codex managed config or sync logic in [#2893](https://github.com/vamseeachanta/workspace-hub/issues/2893); it will document the blocker and keep config files unchanged.
- Found: `scripts/_core/sync-agent-configs.sh` manages Codex config sync and already delegates parts of config surgery to Python. The blocker for [#2893](https://github.com/vamseeachanta/workspace-hub/issues/2893) is not "bash cannot edit TOML"; it is that no reliable Codex CLI/item validator exists for the proposed native statusline migration. This plan will not modify that script.
- Found: `scripts/readiness/build-equality-matrix.py` renders equality-matrix rows from collected machine reports. It has no repo-level `statusline:provider-coverage` row yet and no `COMPLETE`/`PARTIAL` CSS classes.
- Found: `tests/readiness/test_build_equality_matrix.py` already has end-to-end row-render coverage through `test_solvers_renders_row_in_html`, plus provider-harness verdict-unit tests; this is the right file to extend with a dedicated repo-level row render test.

### Standards

Not applicable. This is tooling/statusline work, not engineering calculation work.

### LLM Wiki pages consulted

No relevant wiki pages.

### Documents consulted

- Issue [#2893](https://github.com/vamseeachanta/workspace-hub/issues/2893) — defines R6 scope: one statusline, provider-pool coverage, and a single matrix row `statusline:provider-coverage` graded `COMPLETE/PARTIAL`.
- Issue [#2844](https://github.com/vamseeachanta/workspace-hub/issues/2844) — defines the Codex-specific gap: show the 5-hour burst window and visibly distinguish stale/estimated `O:` readings.
- Issue [#2843](https://github.com/vamseeachanta/workspace-hub/issues/2843) — defines the Claude `C:` visibility gap. Current local reproduction still shows `C:-%`; implementation must close or explicitly mark the Claude estimate/unknown path, not merely verify it.
- Issue [#2887](https://github.com/vamseeachanta/workspace-hub/issues/2887) — records the epic-level design that R6 is not a machine x provider parity grid.
- Issue [#2894](https://github.com/vamseeachanta/workspace-hub/issues/2894) — remains open and still blocks R6 closeout/unattended fleet evidence. This plan may prepare local code/tests for the row, but [#2893](https://github.com/vamseeachanta/workspace-hub/issues/2893) cannot be closed as R6-complete until [#2894](https://github.com/vamseeachanta/workspace-hub/issues/2894) is resolved or the blocker is explicitly lifted.
- `docs/session-handoffs/2026-06-14-agy-gemini-statusline-rollout.md` — documents current Gemini `G:` behavior: genuine usage-left plus binding-window reset from the agy usage snapshot or newer live 429.
- OpenAI Codex config reference, `https://developers.openai.com/codex/config-reference` — verified 2026-06-16; documents `tui.status_line` as the Codex footer configuration key.
- OpenAI Codex slash-command reference, `https://developers.openai.com/codex/cli/slash-commands` — verified 2026-06-16; documents `/statusline` persisting footer items to `tui.status_line`, with available item classes such as model, context, limits, git, tokens, session, and version.

### Gaps identified

- No canonical `docs/plans/` artifact existed for issue [#2893](https://github.com/vamseeachanta/workspace-hub/issues/2893) before this planning wave.
- The issue had contradictory labels (`status:plan-approved` and `status:needs-plan`) during earlier review rounds. After fresh r13 Codex MAJOR evidence, rollback was performed per the issue-planning workflow. R14 then reached no-MAJOR available-provider review, and the user explicitly approved implementation on 2026-06-16; live labels now carry `status:plan-approved`.
- Live-input `C:` already renders correctly. Estimate-fallback `C:` still renders unavailable when live rate-limit input is absent and no authoritative Claude quota file entry exists; the plan must include concrete fallback/unknown behavior tied to [#2843](https://github.com/vamseeachanta/workspace-hub/issues/2843) without rebuilding the live path.
- `O:` does not show Codex 5-hour remaining headroom despite `five_hour_pct` being available in the quota JSON.
- Fresh-file `history.jsonl-estimate` Codex data is not visibly distinguished from live app-server/session telemetry.
- The provider-pool statusline contract is not documented in a durable repo artifact.
- Hermes is not represented in the statusline contract even though the issue asks for Claude/Codex/Gemini/Hermes coverage; current evidence supports an alias to the Codex/OpenAI pool, not an independent quota.
- Codex native statusline config is still in the older `[status_line]` table shape; no reliable local validator exists for `tui.status_line` key/item semantics, so managed config migration is explicitly out of scope for this issue.
- The equality matrix has no repo-level `statusline:provider-coverage` row, no helper-owned repo-level evidence source for that row, and no `COMPLETE`/`PARTIAL` rendering class. Deterministic statusline fixture checks must not be injected into per-machine telemetry.

### Evidence

**Issue statuses** (verified 2026-06-16T05:40:42-05:00 via `gh issue view`):
- [#2893](https://github.com/vamseeachanta/workspace-hub/issues/2893) — OPEN — cross-provider statusline parity issue; R14 reached no-MAJOR available-provider review and the user explicitly approved implementation on 2026-06-16. The issue now carries `status:plan-approved`.
- [#2843](https://github.com/vamseeachanta/workspace-hub/issues/2843) — OPEN — Claude `C:` usage visibility issue.
- [#2844](https://github.com/vamseeachanta/workspace-hub/issues/2844) — OPEN — Codex 5-hour burst-window plus stale/estimate marker issue.
- [#2887](https://github.com/vamseeachanta/workspace-hub/issues/2887) — OPEN — epic-level machine/provider equivalence issue extending [#2801](https://github.com/vamseeachanta/workspace-hub/issues/2801).
- [#2894](https://github.com/vamseeachanta/workspace-hub/issues/2894) — OPEN — equality-matrix substrate blocker for R6 closeout.

**File existence** (`ls -la` verified 2026-06-16T04:37:22-05:00):
- EXISTS: `.claude/statusline-command.sh`
- EXISTS: `.claude/statusline-combined.sh`
- EXISTS: `tests/statusline/test_weekly_reset.bats`
- EXISTS: `tests/statusline/test_quota_staleness.bats`
- EXISTS: `tests/statusline/test_combined_wrapper.bats`
- EXISTS: `~/.cache/agent-quota.json` on this workstation with Codex `five_hour_pct`
- EXISTS: `config/agents/codex/config.toml`
- EXISTS: `scripts/_core/sync-agent-configs.sh`
- EXISTS: `scripts/_core/tests/test_sync_agent_configs.sh`
- EXISTS: `scripts/readiness/collect-equality.sh`
- EXISTS: `scripts/readiness/build-equality-matrix.py`
- EXISTS: `tests/readiness/test_build_equality_matrix.py`
- MISSING (new - this plan will create): `docs/standards/statusline-provider-coverage.md`
- EXISTS: `docs/plans/2026-06-16-issue-2893-statusline-provider-coverage.html`
- MISSING (new - this plan will create): `tests/statusline/test_claude_usage_visibility.bats`
- MISSING (new - this plan will create): `tests/statusline/test_codex_burst_and_provider_coverage.bats`
- MISSING (new - this plan will create): `scripts/readiness/statusline_provider_coverage.py`
- MISSING (new - this plan will create): `tests/readiness/test_statusline_provider_coverage.py`
- EXISTS: `scripts/review/results/2026-06-16-plan-2893-r14-claude.md`
- EXISTS: `scripts/review/results/2026-06-16-plan-2893-r14-codex.md`
- EXISTS: `scripts/review/results/2026-06-16-plan-2893-r14-gemini.md`

**Line excerpts**:

`.claude/statusline-command.sh` currently builds only `C|O|G` and appends only weekly reset days to `O:`:

```bash
read -r o_pct o_state <<< "$(extract_pct "codex")"
...
read -r o_days o_days_state <<< "$(reset_days codex)"
o_days_mark=""; [[ "${o_days_state:-}" == stale && -n "${o_days:-}" ]] && o_days_mark="?"
o_suffix="$o_mark"
[[ -n "${o_days:-}" ]] && o_suffix="${o_mark}·${o_days}d${o_days_mark}"

ai_usage="$(color_pct C "$c_rem" "$c_suffix")|$(color_pct O "$o_pct" "$o_suffix")|$(color_pct G "$g_pct" "${g_mark}${g_suffix}")"
```

`config/agents/codex/config.toml` currently uses the older table:

```toml
[status_line]
enabled = true
items = [
  "model",
  "project_root",
  "git_branch",
  "cwd",
  "context_window_used_percentage",
  "limit_5h_remaining_percentage",
  "limit_weekly_remaining_percentage",
  "token_count"
]
```

`scripts/readiness/build-equality-matrix.py` currently has no R6 row:

```python
BASE_DISPLAY_DIMS = ["compute", "data_access", "solvers", "harness", "python_cmd", "skills",
                     "kanban", "memory", "behavior", "scheduler"]
DISPLAY_DIMS = BASE_DISPLAY_DIMS + provider_rows()
```

```bash
$ jq '.timestamp, (.agents[] | select(.provider=="codex"))' config/ai-tools/agent-quota-latest.json
"2026-06-15T16:36:49-05:00"
{
  "provider": "codex",
  "tier": "subscription",
  "weekly_limit": 1400,
  "week_messages": 209,
  "week_pct": 65,
  "five_hour_pct": 1,
  "pct_remaining": 35,
  "hours_to_reset": 80,
  "resets_at": "2026-06-19T01:32:54-0500",
  "source": "app-server-live"
}
```

`~/.cache/agent-quota.json` also carries live Codex 5-hour schema fields on this workstation:

```bash
$ jq '.timestamp, (.agents[] | select(.provider=="codex"))' ~/.cache/agent-quota.json
"2026-06-16T04:20:04-05:00"
{
  "provider": "codex",
  "tier": "subscription",
  "weekly_limit": 1400,
  "week_messages": 209,
  "week_pct": 73,
  "five_hour_pct": 0,
  "pct_remaining": 27,
  "hours_to_reset": 69,
  "resets_at": "2026-06-19T01:32:54-0500",
  "source": "app-server-live"
}
```

**Reproduction proofs** (verify-against-repo-state):

Live Claude `C:` path works when session input includes `rate_limits.seven_day.used_percentage`. Only the `C:` segment is load-bearing in this proof; the `O:` reset-day text and stale markers are freshness-sensitive and are not test or acceptance oracles.

```bash
$ printf '%s' '{"model":{"display_name":"Opus"},"workspace":{"current_dir":"/tmp/wt-2893-statusline-plan"},"cost":{"total_cost_usd":0.42},"context_window":{"used_percentage":15},"rate_limits":{"seven_day":{"used_percentage":68}}}' \
  | STATUSLINE_QUOTA_PRIMARY=config/ai-tools/agent-quota-latest.json \
    STATUSLINE_QUOTA_CACHE=/tmp/no-agent-quota.json \
    STATUSLINE_GEMINI_SNAPSHOT=/tmp/no-agy-snapshot.json \
    bash .claude/statusline-command.sh --usage-tail \
  | perl -pe 's/\e\[[0-9;]*m//g' \
  | cut -d'|' -f1
C:32%
```

This proof intentionally extracts only the `C:` segment. The `O:` reset-day and stale-marker text is freshness-sensitive and is not a verifier here.

Estimate/unknown fallback gap appears when that live input is absent. Only the `C:-%` segment is load-bearing in this proof; the `O:` text is freshness-sensitive.

```bash
$ printf '%s' '{"model":{"display_name":"Opus"},"workspace":{"current_dir":"/tmp/wt-2893-statusline-plan"},"cost":{"total_cost_usd":0.42},"context_window":{"used_percentage":15}}' \
  | STATUSLINE_QUOTA_PRIMARY=config/ai-tools/agent-quota-latest.json \
    STATUSLINE_QUOTA_CACHE=/tmp/no-agent-quota.json \
    STATUSLINE_GEMINI_SNAPSHOT=/tmp/no-agy-snapshot.json \
    bash .claude/statusline-command.sh --usage-tail \
  | perl -pe 's/\e\[[0-9;]*m//g' \
  | cut -d'|' -f1
C:-%
```

This proof intentionally extracts only the `C:` segment. The `O:` reset-day and stale-marker text is freshness-sensitive and is not a verifier here.

- Reproduced at: 2026-06-16T02:16:40Z
- Failure modes observed match the narrowed issue family: YES. The live `C:` path works, but the fallback path remains unavailable. The input quota file carries `five_hour_pct: 1`, but the rendered `O:` segment shows only weekly remaining plus weekly reset. The exact `O:` reset-day value and stale markers are wall-clock-sensitive because statusline freshness is computed from the JSON timestamp; implementation tests will use freshness-controlled fixtures rather than pinning literal captured reset-day text.

Current distinct source count: 16.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-06-16-issue-2893-statusline-provider-coverage.md` |
| Human-facing HTML plan companion | `docs/plans/2026-06-16-issue-2893-statusline-provider-coverage.html` |
| Provider-pool contract | `docs/standards/statusline-provider-coverage.md` |
| Claude Code statusline implementation | `.claude/statusline-command.sh` |
| Combined workspace-hub wrapper | `.claude/statusline-combined.sh` |
| Statusline tests | `tests/statusline/test_weekly_reset.bats`; `tests/statusline/test_quota_staleness.bats`; new focused Codex/Hermes coverage tests |
| Codex native config blocker note | `docs/standards/statusline-provider-coverage.md` |
| Equality matrix implementation | `scripts/readiness/build-equality-matrix.py` |
| Equality matrix tests | `tests/readiness/test_build_equality_matrix.py` |
| Latest review - Claude r14 | `scripts/review/results/2026-06-16-plan-2893-r14-claude.md` |
| Latest review - Codex r14 | `scripts/review/results/2026-06-16-plan-2893-r14-codex.md` |
| Latest review - Gemini r14 | `scripts/review/results/2026-06-16-plan-2893-r14-gemini.md` |

---

## Deliverable

The implementation will produce preparatory local code/tests for the shared workspace-hub Claude Code statusline and matrix reporting. The statusline will expose provider usage in a compact, source-aware form: Claude live `C:` remains intact, Claude fallback becomes cheap estimate-or-unknown, Codex displays its 5-hour burst window, Gemini behavior stays source-aware, and Hermes is documented/rendered as a Codex/OpenAI pool alias. Codex native footer migration is documented as blocked until a real validator exists. The equality matrix gains a repo-level `statusline:provider-coverage` row driven by a dirty-guarded helper rather than per-machine fixture telemetry. [#2893](https://github.com/vamseeachanta/workspace-hub/issues/2893) stays open pending [#2894](https://github.com/vamseeachanta/workspace-hub/issues/2894) live substrate evidence.

---

## Pseudocode

```text
define statusline provider contract:
    C = Claude weekly remaining %, optional weekly reset, explicit estimate/unknown marker when live data is unavailable
    O = Codex weekly remaining %, weekly reset, 5-hour remaining %, stale/estimate marker
    G = Gemini binding-window remaining %, reset, stale marker from agy snapshot state
    H = Hermes alias to O while Hermes uses OpenAI/Codex provider; no fabricated independent quota

shared quota collectors:
    do not modify query_claude() authoritative-only behavior in scripts/ai/assessment/lib/providers.sh
    do not write estimate values into config/ai-tools/agent-quota-latest.json
    keep fallback Claude estimates local to the statusline renderer only

statusline-command.sh:
    preserve current C/O/G compact shape and color thresholds
    update extract_pct or add an equivalent source-aware helper so returned state can distinguish fresh, stale, estimate, and missing
    classify source values equal to "estimated", ending in "-estimate", or equal to "stats-cache.json-estimate" as estimate even when the quota file timestamp is fresh
    preserve the current live rate_limits.seven_day branch unchanged
    render Claude estimate or stale state visibly, e.g. C:32%? when only fallback data is available
    obtain Claude estimate from a lightweight statusline-local helper over a cache file, not by calling query_claude_stats() or uv
    do not add new bare python3 call sites in .claude/statusline-command.sh; current workspace policy prefers uv run for new Python invocations, and this issue avoids new Python in the prompt-render path entirely
    do not call uv in the prompt-render hot path
    implement the 7-day Claude estimate cutoff with jq only: convert dailyActivity[].date from YYYY-MM-DD to (.date + "T00:00:00Z") before fromdateiso8601, compare to (now - 7*86400), and avoid GNU date -d / BSD date -v / awk mktime
    require a runtime jq capability probe for the estimate path because jq now and fromdateiso8601 are used: `jq -n '"1970-01-01T00:00:00Z"|fromdateiso8601'`; jq absence, old/minimal builds, probe failure, parser errors, and type errors must redirect stderr to /dev/null and fail safe to C:-% rather than crash or fabricate usage
    keep cutoff tests deterministic by generating dates well inside/outside the 7-day boundary, e.g. today and today-30d; the shell estimate window need not be bit-identical to the legacy query_claude_stats() Python lexical cutoff
    in scripts/ai/assessment/lib/providers.sh, change only CLAUDE_MESSAGE_RATIO validation; do not modify the existing query_gemini() python3 call in this issue
    add fixture seams such as STATUSLINE_CLAUDE_STATS_CACHE and STATUSLINE_CLAUDE_CREDS for tests
    use the same schema query_claude_stats() reads:
        stats cache: dailyActivity[].date, dailyActivity[].messageCount, dailyActivity[].sessionCount, dailyActivity[].toolCallCount
        credentials: claudeAiOauth.subscriptionType and claudeAiOauth.rateLimitTier
        tier limits: pro=2000, max=10000, default_claude_max_20x=20000, team=3500, fallback=10000
        ratio default: start with ${CLAUDE_MESSAGE_RATIO:-15}; if empty, non-numeric, or <= 0, reset to 15
        estimate formula: sum last-7-days messageCount / ratio to approximate requests, then pct_remaining=max(0, min(100, 100-floor(approx_requests/weekly_limit*100)))
    harden query_claude_stats() ratio parsing with the same positive-ratio guard, but do not change its authoritative-only query_claude() policy or persist its estimates into shared quota caches
    mark this source as statusline-stats-cache-estimate, never stats-cache.json live
    skip the estimate and render C:-% if the cache is missing, unreadable, or malformed
    never feed that estimate back into the shared quota collector/cache
    add helper codex_five_hour_remaining(provider="codex"):
        read freshest quota source using same precedence as extract_pct/reset_days
        tolerate cache files that lack five_hour_pct by returning missing rather than failing jq or borrowing weekly values
        convert five_hour_pct used to remaining = 100 - five_hour_pct
        classify file/source as fresh, stale, estimate, missing
        return "<remaining> <state>" or "- missing"
    extend Codex suffix:
        preserve existing O:<weekly>%·<weekly_days>d shape
        append compact 5-hour suffix, e.g. O:35%·<days>d·5h99%
        apply independent threshold coloring to the 5-hour percentage in terminal output; ANSI-stripped tests assert the plain text contract
        mark stale or estimated components with "?"
    add Hermes suffix/segment:
        render H=O or H:<same binding pool> per contract, not an invented independent value
        bypass color_pct for H=O alias output because color_pct expects an integer percentage and appends "%"
        keep unknown/alias state visually explicit
    keep --usage-tail nonblank even when quota helpers fail

codex native config:
    make no changes to config/agents/codex/config.toml in this issue
    make no changes to scripts/_core/sync-agent-configs.sh in this issue
    document in docs/standards/statusline-provider-coverage.md that native Codex footer migration is blocked until a command or upstream spec validates exact status_line item identifiers
    optionally file a follow-on issue for a TOML-safe Codex config migration once validation exists

repo-level statusline coverage helper:
    add a small repo-local helper that evaluates the statusline contract from freshness-controlled deterministic fixtures
    helper creates temporary quota, Gemini, and Claude fixture files at runtime instead of reusing aging committed quota snapshots
    helper seeds Claude with either live-rate-limit stdin or STATUSLINE_CLAUDE_STATS_CACHE plus STATUSLINE_CLAUDE_CREDS fixture seams so the local contract_verdict COMPLETE path is reachable independent of live user telemetry
    helper fixture timestamps use the same freshness-control idea as tests/statusline/test_quota_staleness.bats iso_at_age_hours: generate a top-level timestamp inside STATUSLINE_QUOTA_MAX_AGE_HOURS for fresh-contract samples and explicit old timestamps for stale-path samples
    helper runs .claude/statusline-command.sh --usage-tail against those temporary fixtures and strips ANSI
    helper refuses COMPLETE when measured paths have any untracked, modified, deleted, staged, unstaged, or missing required changes:
        first verify each required file/directory exists after implementation; missing required artifacts return MISSING-EVIDENCE before git cleanliness is evaluated
        for paths that should be tracked after implementation, verify git ls-files --error-unmatch succeeds or report MISSING-EVIDENCE
        run git status --porcelain --untracked-files=all -- <measured paths>
        treat any output as dirty and include the path/status entries in the helper JSON
        .claude/statusline-command.sh
        .claude/statusline-combined.sh
        tests/statusline/
        scripts/ai/assessment/query-quota.sh
        scripts/ai/assessment/lib/providers.sh
        scripts/ai/assessment/gemini-usage.py
        config/ai-tools/agent-quota-latest.json
        scripts/readiness/build-equality-matrix.py
        scripts/readiness/statusline_provider_coverage.py
        tests/readiness/test_build_equality_matrix.py
        tests/readiness/test_statusline_provider_coverage.py
        docs/standards/statusline-provider-coverage.md
        docs/plans/2026-06-16-issue-2893-statusline-provider-coverage.md
        docs/plans/2026-06-16-issue-2893-statusline-provider-coverage.html
        docs/plans/README.md
    helper emits repo-level JSON schema:
        schema_version: 1
        generated_by: scripts/readiness/statusline_provider_coverage.py
        checkout_sha: <sha>
        dirty: true|false
        missing_paths: [path, ...]
        r6_closeout_blocker: issue_2894_open|issue_2894_unknown|none
        issue_state_evidence: {issue: 2894, state: OPEN|CLOSED|UNKNOWN, source: env|cache|unavailable, error: string}
        contract_verdict: COMPLETE|PARTIAL|MISSING-EVIDENCE|STALE-CHECKOUT
        output_sample: stripped fixture statusline
        providers:
          claude: {state: complete|partial|missing, evidence: observed_output, notes: string}
          codex:  {state: complete|partial|missing, evidence: observed_output, notes: string}
          gemini: {state: complete|partial|missing, evidence: observed_output, notes: string}
          hermes: {state: alias|partial|missing, evidence: observed_output, bound_to: codex, observed_codex_segment: string, notes: string}
    complete means the provider segment is parsed from stripped statusline output generated from fresh-controlled fixtures, required artifacts exist, tracked-path checks pass, and measured paths are clean; named tests verify the helper but do not substitute for observed output
    stale-marked readings in the fresh-contract sample downgrade that provider to partial; stale rendering remains covered by explicit stale tests, not by COMPLETE
    hermes.state == alias satisfies the complete condition only when H=O is present and the helper also parsed a non-missing observed Codex/OpenAI `O:` segment with its source/stale/window semantics
    partial means the provider is documented but lacks observed output coverage
    missing means no segment/alias evidence exists
    tests own the contract assertions; renderer only consumes the collected report
    determine r6_closeout_blocker fail-closed without live network in normal matrix rendering:
        first honor STATUSLINE_R6_BLOCKER_STATE=open|closed|unknown for tests
        otherwise read an optional precomputed local cache file path from STATUSLINE_R6_BLOCKER_CACHE if present
        do not call gh issue view from build-equality-matrix.py or its default helper path
        absent/unparseable cache => issue_2894_unknown
        open => issue_2894_open; closed => none; unknown/unavailable/absent/parse failure => issue_2894_unknown
        issue_2894_open and issue_2894_unknown both prevent final COMPLETE rendering
    while issue 2894 is open or unknown, helper may report contract_verdict COMPLETE but matrix row verdict must remain PARTIAL with detail "local contract complete; live equality substrate pending issue 2894" or "issue 2894 state unavailable"

matrix:
    do not add statusline providers to DISPLAY_DIMS or any global matrix provider list
    do not modify scripts/readiness/collect-equality.sh
    add a repo-level statusline row path separate from per-machine telemetry rows
    expose collect_statusline_provider_coverage(repo_root: Path) from scripts/readiness/statusline_provider_coverage.py
    import and call that helper once from scripts/readiness/build-equality-matrix.py main()
    add render_repo_level_row(dim, verdict, detail, colspan=len(roster)):
        emit <tr><th>statusline:provider-coverage</th><td class="..." colspan="<machine-count>"><strong>{verdict}</strong><span class="detail">{escaped detail}</span></td></tr>
    insertion point:
        in main(), after rows = [] and before the existing for dim in DISPLAY_DIMS loop, append the repo-level row
        do not include statusline:provider-coverage in DISPLAY_DIMS
        do not call verdict_for(dim, m, ...) for this row
    add statusline_provider_coverage_verdict():
        read the helper dict returned in-process from the current repo checkout
        return (COMPLETE, detail) only when Claude/Codex/Gemini are complete from observed output, Hermes is bound to the observed Codex/OpenAI segment, required artifacts exist, measured paths are clean, and no live R6 closeout blocker is active
        return (PARTIAL, detail) when the local statusline contract is complete but issue 2894 is open or issue-state evidence is unavailable
        return (PARTIAL, detail) when at least one provider is missing/unknown
        return (STALE-CHECKOUT, detail) or (MISSING-EVIDENCE, detail) when helper reports dirty/missing data
        return (MISSING-EVIDENCE, detail) when the helper schema is absent
    in docs/standards/statusline-provider-coverage.md, state that contract_verdict COMPLETE is renderer-contract evidence from seeded fixtures, not proof of live provider telemetry availability
    in docs/standards/statusline-provider-coverage.md, state that statusline 5-hour `O:` uses remaining polarity (`100 - five_hour_pct`) even though scripts/ai/assessment/lib/display.sh currently prints raw five_hour_pct used polarity
    H=O alias rendering bypasses color_pct only for percent formatting; it must inherit the observed O segment's state: missing/unavailable O dims or marks H=O as unknown, while stale O gives H=O the stale `?` marker without forcing dim if O itself is threshold-colored rather than dimmed
    render `statusline:provider-coverage` before or after machine rows as a single repo-level row, not one per machine
    add CSS/docstring vocabulary and tests for new COMPLETE, PARTIAL, and .detail styling; verify existing MISSING-EVIDENCE and STALE-CHECKOUT classes are reused rather than duplicated
    explicitly state that the row does not measure machine parity and carries no per-machine signal
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/standards/statusline-provider-coverage.md` | Define the durable provider-pool display contract, including source/staleness rules and Hermes alias semantics |
| Update/Preserve | `docs/plans/2026-06-16-issue-2893-statusline-provider-coverage.html` | Keep the human-facing HTML companion aligned with the Markdown workflow artifact required by `docs/plans/README.md` |
| Modify | `.claude/statusline-command.sh` | Display Codex 5-hour remaining headroom and source-state markers; render Hermes as an explicit Codex/OpenAI alias; keep existing `C:`/`G:` behavior intact |
| Modify | `scripts/ai/assessment/lib/providers.sh` | Guard existing `CLAUDE_MESSAGE_RATIO` math against empty/non-numeric/zero values without changing authoritative-only collector policy |
| Modify/Create | `tests/statusline/test_claude_usage_visibility.bats` | Add focused TDD tests for real/estimated/unknown Claude `C:` rendering |
| Modify | `tests/statusline/test_weekly_reset.bats` | Extend existing reset tests to cover the new Codex 5-hour suffix without regressing weekly reset behavior |
| Modify | `tests/statusline/test_quota_staleness.bats` | Extend existing stale/estimate assertions so Codex 5-hour and Claude estimate markers cannot look live |
| Modify | `tests/statusline/test_combined_wrapper.bats` | Update existing combined-wrapper assertions for the new `O:` suffix and `H=O` alias while preserving wrapper fail-soft behavior |
| Modify/Create | `tests/statusline/test_codex_burst_and_provider_coverage.bats` | Add focused TDD tests for Codex 5-hour, estimate/stale markers, Hermes alias rendering, and nonblank `--usage-tail` fallback |
| Create | `scripts/readiness/statusline_provider_coverage.py` | Produce a small, dirty-guarded repo-level statusline coverage self-report |
| Create | `tests/readiness/test_statusline_provider_coverage.py` | Pin the coverage helper schema, fixture execution, and non-circular provider-state derivation |
| Modify | `scripts/readiness/build-equality-matrix.py` | Add the single repo-level `statusline:provider-coverage` row and `COMPLETE`/`PARTIAL`/`MISSING-EVIDENCE`/`STALE-CHECKOUT` verdict rendering without per-machine telemetry |
| Modify | `tests/readiness/test_build_equality_matrix.py` | Pin R6 row rendering and verdict behavior |
| Update | `docs/plans/README.md` | Index this plan |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `claude_live_or_estimate_is_visible` | Existing live `C:` stays intact and fallback estimates are marked cheaply | live Claude rate-limit fixture plus estimate-only fixtures via `STATUSLINE_CLAUDE_STATS_CACHE` and `STATUSLINE_CLAUDE_CREDS` | live fixture renders unmarked `C:<pct>%`; estimate fixture renders marked `C:<pct>%?`; no data remains `C:-%`; malformed/missing cache remains `C:-%` |
| `claude_estimate_ratio_defaults_safely` | Missing, non-numeric, or zero `CLAUDE_MESSAGE_RATIO` cannot crash the statusline or adjacent stats helper | estimate fixture with unset/empty/non-numeric/zero ratio | helper and `query_claude_stats()` guard fall back to 15 or render unknown without division by zero |
| `claude_estimate_cutoff_uses_portable_jq_iso_math` | Seven-day Claude estimate avoids GNU/BSD date portability traps and new Python calls | stats-cache fixture with date-only `YYYY-MM-DD` entries generated far from the boundary, e.g. today and today-30d; simulated missing/old/minimal jq | jq capability probe for `fromdateiso8601` succeeds before use; jq errors redirect stderr to `/dev/null` and intentionally render `C:-%`; added-lines-only diff check for `.claude/statusline-command.sh` finds no new Python entrypoint in prompt code: `git diff -- .claude/statusline-command.sh | grep -E '^\\+' | grep -v '^+++' | grep -E '\\b(python3|python)\\b|uv run python'` is empty |
| `codex_shows_weekly_reset_and_5h_remaining` | Codex `O:` preserves weekly shape and adds 5-hour remaining using freshness-controlled fixtures | quota with `week_pct=65`, `five_hour_pct=1`, `hours_to_reset=80`, live source and fresh timestamp via the existing `iso_at_age_hours` pattern | output contains `O:35%·...d·5h99%` or the exact contract string chosen in implementation |
| `codex_5h_suffix_has_independent_threshold_color` | Burst-window pressure is visible even when weekly quota is healthy | quota with healthy weekly remaining and low 5-hour remaining | terminal output includes a 5h-specific ANSI SGR sequence distinct from the weekly segment's threshold color; ANSI-stripped output still matches the plain contract |
| `codex_estimate_source_is_marked` | Fresh estimated Codex sources do not look live | quota fixtures with `source=history.jsonl-estimate` and exact `source=estimated` | `O:` includes a visible `?`/estimate marker for both source spellings |
| `codex_stale_file_marks_pct_reset_and_5h_components` | Existing stale-file marker behavior extends to 5-hour data | stale primary with Codex weekly/reset/5h values | `O:` includes stale markers on affected components |
| `codex_fresh_cache_wins_for_5h_window` | Home cache precedence applies to 5-hour values too | stale primary + fresh cache with different `five_hour_pct` | rendered 5-hour remaining comes from cache and is unmarked |
| `hermes_renders_as_codex_alias` | Hermes is represented honestly without fake quota and bound to the observed Codex/OpenAI pool | Codex live quota available; no Hermes provider entry | output includes `H=O`; coverage helper records Hermes as alias only if the observed `O:` segment is non-missing |
| `hermes_alias_inherits_unknown_visual_state` | Hermes alias cannot look live when the Codex/OpenAI pool it aliases is missing or stale | missing, unavailable, and stale Codex quota fixtures | missing/unavailable `O:` makes `H=O` dim or otherwise unknown-marked; stale `O:` gives `H=O?` without forcing dim when `O:` itself remains threshold-colored |
| `usage_tail_never_blanks_on_missing_quota_helpers` | Wrapper remains fail-soft | missing quota files and missing Gemini snapshot | nonempty statusline tail with dim/unknown segments |
| `codex_config_scope_guard` | Speculative Codex config migration and shared estimate persistence stay out of this issue | git diff after implementation | `config/agents/codex/config.toml`, `scripts/_core/sync-agent-configs.sh`, `scripts/_core/tests/test_sync_agent_configs.sh`, `scripts/ai/assessment/query-quota.sh`, and `config/ai-tools/agent-quota-latest.json` are unchanged |
| `statusline_provider_coverage_helper_reports_four_providers` | Repo-level helper evidence is produced outside per-machine telemetry | freshness-controlled fixture/statusline helper run with runtime-generated timestamps | JSON has schema_version, dirty flag, output_sample, and claude/codex/gemini/hermes states derived only from parsed output |
| `statusline_provider_coverage_helper_fails_closed_on_dirty_measured_paths` | Helper cannot report COMPLETE from uncommitted or missing statusline evidence | temp repo/worktree with untracked, modified, deleted, staged, unstaged, missing, and untracked-required measured paths, including `scripts/ai/assessment/lib/providers.sh` | verdict is not COMPLETE and dirty or missing path/status is named |
| `matrix_renders_statusline_provider_coverage_repo_row` | R6 row exists in generated matrix without pretending to be per-machine telemetry | monkeypatched `collect_statusline_provider_coverage()` and monkeypatched `bem.REPORTS` to `tmp_path` before invoking `bem.main()` | temp HTML contains `<th>statusline:provider-coverage</th>` and one `td colspan=<machine-count>`; repo `docs/reports/` remains untouched |
| `matrix_preserves_existing_row_counts_and_order` | Adding the repo-level row does not break existing equality matrix rows | generated HTML with the new row plus existing dimensions/provider rows | one new statusline row appears before existing rows; ten base dimensions and nine provider capability rows remain present and ordered as before |
| `statusline_provider_coverage_complete_requires_four_contract_cases` | Contract verdict only becomes `COMPLETE` when C/O/G/H contract cases are parsed from stripped output | simulated provider coverage states derived from fixture output | partial coverage -> `PARTIAL`; Claude/Codex/Gemini complete plus Hermes alias bound to observed Codex segment -> contract `COMPLETE` |
| `statusline_provider_coverage_helper_fixtures_are_freshness_controlled` | Helper fixture output does not decay as wall-clock time passes | helper run with generated fresh fixture timestamps and a separate stale fixture | fresh sample lacks stale `?` markers; stale sample includes markers and does not satisfy provider COMPLETE |
| `r6_closeout_blocker_probe_fails_closed` | Issue 2894 state cannot fail open to COMPLETE without adding network calls to matrix rendering | fixture seam/cache for open, closed, unknown, absent, and unparseable states | open/unknown/absent/unparseable -> matrix `PARTIAL`; closed plus local contract complete -> matrix `COMPLETE`; no `gh issue view` is called by `bem.main()` |
| `matrix_downgrades_local_complete_while_2894_blocks_live_substrate` | The matrix row does not advertise R6 COMPLETE while live substrate evidence is blocked | helper reports contract `COMPLETE` plus `r6_closeout_blocker=issue_2894_open` | rendered row verdict is `PARTIAL` with detail naming [#2894](https://github.com/vamseeachanta/workspace-hub/issues/2894) |
| `matrix_has_verdict_and_detail_css_classes` | New verdicts and detail text are styled intentionally without duplicating existing classes | generated HTML/CSS string | `.complete`, `.partial`, and `.detail` classes are added; existing `.missing-evidence` and `.stale-checkout` classes are still applied |

---

## Acceptance Criteria

- [ ] `docs/standards/statusline-provider-coverage.md` documents the provider segment contract for Claude, Codex, Gemini, and Hermes, including source/staleness markers and Hermes-as-Codex-alias semantics.
- [ ] `docs/plans/2026-06-16-issue-2893-statusline-provider-coverage.html` exists as the human-facing plan companion and links to the Markdown workflow artifact.
- [ ] Existing live Claude `C:` rendering from `rate_limits.seven_day` remains unchanged; fallback `C:` renders an explicitly marked cheap estimate when fixtureable local cache evidence exists and `-%` only when no usable evidence exists.
- [ ] Claude Code statusline output remains compact and includes Codex 5-hour headroom plus stale/estimate markers; a representative plain output matches the contract shape, e.g. `C:<pct>%|O:<pct>%·<days>d·5h<pct>%|G:<pct>%·<days>d|H=O` where data exists.
- [ ] Shared quota collectors remain authoritative-only: `scripts/ai/assessment/query-quota.sh` and `config/ai-tools/agent-quota-latest.json` are not changed to persist Claude estimates; any `scripts/ai/assessment/lib/providers.sh` change is limited to guarding the existing `CLAUDE_MESSAGE_RATIO` math.
- [ ] Codex native managed config and sync remain unchanged; `docs/standards/statusline-provider-coverage.md` records that native Codex footer migration is blocked until exact `status_line` item identifiers can be validated by a real command or upstream spec.
- [ ] `scripts/readiness/statusline_provider_coverage.py` emits dirty-guarded repo-level provider coverage JSON; it refuses COMPLETE when required artifacts are missing or measured statusline paths are dirty.
- [ ] The coverage helper uses runtime-generated freshness-controlled fixtures for the default contract sample; committed quota snapshots are not used as literal fresh-output fixtures.
- [ ] The coverage helper derives `COMPLETE` only from parsed stripped statusline output and clean measured paths; test names, contract prose, or fixture existence alone cannot satisfy provider coverage.
- [ ] The issue-state probe for [#2894](https://github.com/vamseeachanta/workspace-hub/issues/2894) is fail-closed: open, unknown, unavailable, timeout, auth failure, or parse failure all prevent final `COMPLETE`.
- [ ] Matrix rendering remains offline by default: `scripts/readiness/build-equality-matrix.py` and its in-process helper do not call `gh`; issue-state evidence is injected by env/cache and defaults to unknown/partial when absent.
- [ ] Matrix row tests write only to `tmp_path` by monkeypatching `bem.REPORTS`; they do not create files under repo `docs/reports/`.
- [ ] `scripts/readiness/build-equality-matrix.py` renders `statusline:provider-coverage` through a concrete repo-level/colspan path with `COMPLETE`, `PARTIAL`, `MISSING-EVIDENCE`, or `STALE-CHECKOUT`, not as per-machine telemetry.
- [ ] While [#2894](https://github.com/vamseeachanta/workspace-hub/issues/2894) remains open, the matrix row does not render final `COMPLETE`; it renders `PARTIAL` with detail that local contract coverage is complete but live equality-substrate evidence is still blocked.
- [ ] The `statusline:provider-coverage` row may be locally implemented and tested, but [#2893](https://github.com/vamseeachanta/workspace-hub/issues/2893) remains blocked from final closeout until [#2894](https://github.com/vamseeachanta/workspace-hub/issues/2894) resolves the live equality-substrate/fleet evidence blocker.
- [ ] Focused statusline tests pass: `bats tests/statusline/test_claude_usage_visibility.bats tests/statusline/test_weekly_reset.bats tests/statusline/test_quota_staleness.bats tests/statusline/test_codex_burst_and_provider_coverage.bats tests/statusline/test_combined_wrapper.bats`.
- [ ] Focused matrix/collector tests pass: `uv run pytest tests/readiness/test_statusline_provider_coverage.py tests/readiness/test_build_equality_matrix.py -q`.
- [ ] Legal/security scan passes: `bash scripts/legal/legal-sanity-scan.sh`.
- [ ] Completeness score is computed before closure per gate label `gate:completeness`.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MINOR | r14 found no blockers. Remaining minors were explicit `five_hour_pct:null` handling, prominent display-polarity divergence documentation, implementation sequencing for dirty-guarded files, directory pathspec wording, and estimate-source 5-hour fixture coverage. |
| Codex | MINOR | r14 found no blockers. Remaining minors were that the live issue was already in `status:plan-review` before r14 artifacts were tracked and the completeness closeout artifact list was underspecified. |
| Gemini | UNAVAILABLE | r14 Gemini CLI failed before returning usable review signal (`rc=124`); per cross-review routing, this degrades T3 to the two available no-MAJOR providers and is documented rather than blocking indefinitely. |

**Overall result:** r14 returned no MAJOR from available providers: Claude MINOR, Codex MINOR, Gemini UNAVAILABLE. The user explicitly approved implementation on 2026-06-16.

Revisions made based on review:
- Added concrete Claude `C:` visibility work and tests tied to [#2843](https://github.com/vamseeachanta/workspace-hub/issues/2843), now scoped around existing `query_claude_stats()` and the deliberate authoritative-only policy in `scripts/ai/assessment/lib/providers.sh`.
- Moved statusline coverage evidence generation to a collector/helper path; the matrix renderer will consume collected evidence only.
- Defined the repo-level helper JSON schema and required observed stripped statusline output evidence.
- Removed the dead matrix provider tuple and required a concrete repo-level render path outside `DISPLAY_DIMS` and per-machine `verdict_for()` routing.
- Deferred Codex native config migration and `scripts/_core/sync-agent-configs.sh` TOML editing because current local validation cannot prove exact Codex key/item semantics.
- Recorded live governance drift that previously put [#2893](https://github.com/vamseeachanta/workspace-hub/issues/2893) in both `status:plan-approved` and `status:needs-plan`; after r13 rollback and r14 no-MAJOR available-provider review, explicit user approval restored `status:plan-approved`.
- Added [#2894](https://github.com/vamseeachanta/workspace-hub/issues/2894) non-closing scope: local code/tests may be prepared, but [#2893](https://github.com/vamseeachanta/workspace-hub/issues/2893) cannot be closed as R6-complete while [#2894](https://github.com/vamseeachanta/workspace-hub/issues/2894) remains a live blocker.
- Archived r3, r4, and r5 review artifacts under stable `*-rN-*.md` names because the fixed current-output paths are truncated during the next fanout run.
- Added source-aware statusline extraction, Codex 5-hour cache schema handling, `H=O` alias rendering outside `color_pct`, and explicit Hermes alias-to-`COMPLETE` mapping.
- Removed Codex managed config migration and `scripts/_core/sync-agent-configs.sh` TOML editing from [#2893](https://github.com/vamseeachanta/workspace-hub/issues/2893) scope because no reliable validator exists and this issue should not modify native Codex managed config.
- Kept Claude estimate fallback local to `.claude/statusline-command.sh`; the shared provider quota library remains authoritative-only.
- Replaced per-machine collector fixture injection with a dirty-guarded repo-level helper and repo-level matrix row.
- Re-scoped Claude work to the fallback-only gap, added a live-C positive reproduction, removed stale pre-plan gap proof text, and required a lightweight local cache reader with env fixture seams instead of calling `query_claude_stats()` or `uv`.
- Specified the exact matrix integration: import/call the helper once in `scripts/readiness/build-equality-matrix.py` and render a single colspan repo-level row.
- Added `scripts/ai/assessment/gemini-usage.py` to the helper dirty guard.
- Reframed reset-day reproduction text as time-sensitive evidence and required freshness-controlled fixtures for literal statusline assertions.
- Added exact Claude stats-cache/credentials schema and estimate formula.
- Added `.claude/statusline-combined.sh`, `scripts/readiness/build-equality-matrix.py`, and `tests/readiness/test_build_equality_matrix.py` to the dirty guard.
- Named the precise repo-level row insertion point: after `rows = []`, before the existing `DISPLAY_DIMS` loop, never through `verdict_for()` per machine.
- Added the HTML companion plan artifact required for human-facing rich artifacts while preserving the Markdown workflow artifact required by `docs/plans/README.md`.
- Added live `~/.cache/agent-quota.json` Codex 5-hour schema evidence.
- Required dirty-guard evaluation via `git status --porcelain --untracked-files=all -- <measured paths>`.
- Bound Hermes COMPLETE semantics to an observed non-missing `O:` segment and visible `H=O` output.
- Added `tests/statusline/test_quota_staleness.bats` to Files to Change, guarded `CLAUDE_MESSAGE_RATIO` default/zero handling, and made `render_repo_level_row(..., detail, ...)` consume escaped detail text.
- Archived r8 review artifacts under stable `*-r8-*.md` names before the next fanout.
- Removed the earlier draft permission for an inline bare `python3` statusline-local cache reader; seven-day Claude fallback filtering must use portable `jq` ISO conversion and no new Python calls in the prompt-render hot path.
- Added required-path existence and tracked-path checks before `git status --porcelain --untracked-files=all` so missing artifacts cannot appear clean.
- Added helper schema fields for `missing_paths`, `contract_verdict`, and `r6_closeout_blocker`.
- Required matrix row support for `MISSING-EVIDENCE`, `STALE-CHECKOUT`, and `.detail` styling in addition to `COMPLETE`/`PARTIAL`.
- Required the matrix row to render `PARTIAL` rather than final `COMPLETE` while [#2894](https://github.com/vamseeachanta/workspace-hub/issues/2894) remains a live equality-substrate blocker.
- Added independent 5-hour suffix threshold coloring and clamped Claude estimate percentages to `0..100`.
- Corrected the resource-intel precedent for matrix row tests.
- Archived r9 review artifacts under stable `*-r9-*.md` names before the next fanout.
- Required runtime-generated freshness-controlled fixtures for `scripts/readiness/statusline_provider_coverage.py`; committed quota snapshots are not fresh-output oracles.
- Specified that stale-marked fresh-contract samples downgrade provider coverage instead of satisfying provider COMPLETE.
- Added a fail-closed issue-state probe for issue 2894: open, unknown, unavailable, timeout, auth failure, and parse failure all block final `COMPLETE`.
- Removed permission to add new bare `python3` call sites in `.claude/statusline-command.sh`; the implementation must use the planned `jq` cutoff path and leave pre-existing statusline `python3` callsites unchanged unless a separate approved scope changes them.
- Clarified that only `.complete`, `.partial`, and `.detail` CSS are new; existing `.missing-evidence` and `.stale-checkout` classes should be reused.
- Narrowed the Python policy for `scripts/ai/assessment/lib/providers.sh`: [#2893](https://github.com/vamseeachanta/workspace-hub/issues/2893) may only guard `CLAUDE_MESSAGE_RATIO`; the existing `query_gemini()` bare-`python3` helper call is pre-existing and out of scope for this issue.
- Replaced the impossible shell cutoff ambiguity with explicit `jq` math: append `T00:00:00Z` to `dailyActivity[].date`, run `fromdateiso8601`, and compare to `now - 7*86400`.
- Required matrix tests invoking `bem.main()` to monkeypatch `bem.REPORTS` to `tmp_path`, and added a row-count/order regression guard for the existing matrix rows.
- Clarified that matrix rendering remains offline by default; issue [#2894](https://github.com/vamseeachanta/workspace-hub/issues/2894) state is injected from env/cache and absent/unparseable state fails closed to `PARTIAL`.
- Archived r11 review artifacts under stable `*-r11-*.md` names before the next fanout.
- Added `scripts/ai/assessment/lib/providers.sh` to the dirty-guard measured path set because this issue modifies its `CLAUDE_MESSAGE_RATIO` logic.
- Made the no-new-bare-`python3` proof diff-scoped so pre-existing statusline `python3` callsites do not make the test impossible.
- Added the `jq >= 1.6` estimate-path floor and safe fallback behavior for missing/old jq.
- Required the coverage helper to seed Claude fixtures via live-rate-limit stdin or the new stats-cache/creds seams so local `contract_verdict: COMPLETE` remains reachable when [#2894](https://github.com/vamseeachanta/workspace-hub/issues/2894) is no longer blocking.
- Archived r12 review artifacts under stable `*-r12-*.md` names before the next fanout.
- Added `scripts/ai/assessment/query-quota.sh` and `config/ai-tools/agent-quota-latest.json` to both dirty-guard coverage and the scope-guard test so Claude estimates cannot be persisted into the shared quota collector unnoticed.
- Reworked the reproduction commands to extract only the `C:` segment, eliminating stale literal `O:` reset/staleness text from the verbatim proof blocks.
- Added plan/index/HTML artifacts to the dirty-guard measured path set.
- Required `H=O` alias rendering to inherit the dim/unknown visual state of the observed `O:` segment.
- Required the contract doc to spell out 5-hour remaining polarity and the renderer-contract meaning of `contract_verdict: COMPLETE`.
- Archived r13 review artifacts under stable `*-r13-*.md` names before the next fanout.
- Performed workflow rollback after fresh r13 MAJOR evidence: posted [GitHub comment](https://github.com/vamseeachanta/workspace-hub/issues/2893#issuecomment-4717803644), removed `status:plan-approved` and `status:needs-plan`, and applied `status:plan-review`.
- Extended the estimate-source classifier and test matrix to cover exact `source=estimated` in addition to `*-estimate` source values.
- Archived r14 review artifacts under stable `*-r14-*.md` names.

---

## Risks and Open Questions

- **Risk:** Earlier label drift incorrectly left the issue in both `status:plan-approved` and `status:needs-plan` while fresh review waves returned `MAJOR`. That drift was rolled back after r13; R14 reached no-MAJOR available-provider review and the user explicitly approved implementation on 2026-06-16.
- **Risk:** [#2894](https://github.com/vamseeachanta/workspace-hub/issues/2894) is a live blocker for R6 closeout. This plan can produce preparatory local code/tests for the row, but closing [#2893](https://github.com/vamseeachanta/workspace-hub/issues/2893) as complete requires [#2894](https://github.com/vamseeachanta/workspace-hub/issues/2894) to be resolved or the blocker to be explicitly lifted.
- **Risk:** Codex native statusline cannot render the exact Claude Code shell-formatted `C:|O:|G:` string unless upstream adds arbitrary formatter support. Native footer migration is out of scope until exact item identifiers and safe config mutation can be validated.
- **Risk:** Hermes has no independent quota telemetry in the current collector. The contract must render Hermes as an explicit OpenAI/Codex alias (`H=O`) or `unknown`, not as a fake separate percentage.
- **Risk:** Adding a provider-coverage row to a machine-shaped matrix can accidentally look like machine parity. The row must use an explicit repo-level colspan render path and not call `verdict_for()` per machine.
- **Open:** Whether the final `O:` suffix should be `·5h99%`, `/5h99%`, or the shorter `·99h`. Recommendation: use `·5h99%` because it is explicit while preserving the existing `O:<weekly>%·<days>d` prefix the user already recognizes.

---

## Complexity: T3

**T3** - The work crosses statusline rendering, local estimate policy, a new repo-level readiness helper, and matrix rendering. It still has a narrow user-facing surface, but the code spans multiple subsystems and requires 3-provider adversarial plan/code review.
