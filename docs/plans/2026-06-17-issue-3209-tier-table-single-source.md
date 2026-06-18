# Plan for #3209: Reconcile tier-table routing into one cost-aligned source

> **Status:** adversarial-reviewed (r1 Claude MAJOR → revised; r2 Codex pending)
> **Complexity:** T2
> **Date:** 2026-06-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3209
> **Client:** N/A
> **Project:** (none)
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-17-plan-3209-claude.md | ...-codex.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `config/agents/routing-config.yaml` `tiers.*` — **all primary=claude**, fallbacks include `hermes` (SIMPLE `[hermes,codex,gemini]`, STANDARD `[codex,hermes,gemini]`, COMPLEX/REASONING `[gemini,codex]`).
- Found: `scripts/coordination/routing/lib/tier_router.sh:26-58` — the **executed** table is hardcoded bash arrays `TIER_PRIMARY/FALLBACK1/FALLBACK2`: SIMPLE/STANDARD primary=**codex** (fb gemini/claude), COMPLEX/REASONING primary=claude (fb gemini,codex). **No hermes** (the bash `check_provider_available` only knows claude/codex/gemini — line ~52). This is the cost-aligned reality.
- Found: `scripts/ai/task-dispatcher.py:63-68` — `TIER_AGENT_PREFERENCE` dict, **claude-first for every tier** (`simple:[claude,hermes,codex,gemini]`, …). Advisory CLI; position-based scoring in `score_agents` (`tier_score = (len-index)/len`).
- Found (**r1-F3 — a FOURTH copy, missed in draft**): `scripts/coordination/routing/route.sh:216-220` — the `--config` display prints a hardcoded "Routing Table:" string (`SIMPLE -> codex (fallback: gemini, claude)` …). Matches the cost-aligned table today but is a 4th hand-maintained drift surface. Must be reconciled/guarded.
- Found (just landed, #3205): `scripts/ai/routing_resolver.py` — single resolver owning `execution_contexts`. This plan **extends** it to also own `tiers` (`tier_chain`/`--tier`), so one module is the source for both context AND tier routing.
- Found: `scripts/dispatch/route.py` (#3030) — lane-quota, does not read `tiers`. Out of scope.

### Standards
Not applicable (harness/infrastructure).

### LLM Wiki pages consulted
None (Client: N/A).

### Documents consulted
- `docs/governance/2026-06-17-cost-ceiling-policy.md` — "Claude is the interactive-dev lane only"; the executed bash (codex on cheap tiers) is already consistent with this, the YAML is the stale outlier.
- `docs/plans/2026-06-17-issue-3205-executed-router-consolidation.md` §Gaps/§Risks — this is the deferred tier half of #3205; the resolver substrate + `_resolver` bash helper already exist.
- Memory `routing-config-is-advisory` (updated 2026-06-17) — confirms tier maps still advisory after #3205; this plan closes that.
- Issue #3209 (body) — acceptance; operator decision recorded: cost-aligned codex-cheap.

### Gaps identified
- No `tier_chain`/`--tier` in the resolver yet (only execution_contexts).
- Three tier copies (YAML, bash arrays, python dict) must collapse to the resolver-as-source.
- `test_routing_config_observed_behavior.py::test_simple_and_standard_route_to_claude` pins the stale claude-everywhere YAML and must be updated.

### Evidence (embedded verification)
**Issue statuses** (verified 2026-06-17 via `gh issue view`): `#3209` OPEN (domain:harness, lane:claude); `#3205` CLOSED (merged PR #3210); `#3058` OPEN (epic).

**File existence** (`ls` 2026-06-17): EXISTS `routing_resolver.py`, `tier_router.sh`, `task-dispatcher.py`, `tests/config/test_routing_config_observed_behavior.py`. MISSING (new): `tests/ai/test_tier_chain.py` (or extend `test_routing_resolver.py`), `tests/coordination/test_tier_router_cost_aligned.py`.

**Line excerpts** — `tier_router.sh` bash arrays (SIMPLE/STANDARD primary=codex) vs `routing-config.yaml` tiers (primary=claude): the divergence table in this plan's header is taken verbatim from those two files.

**Reproduction proof** (issue alleges "editing YAML doesn't change runtime tier routing"):
```
$ grep -n "TIER_PRIMARY\|ROUTING_CONFIG" scripts/coordination/routing/lib/tier_router.sh
# arrays are hardcoded; YAML tiers.* is never read for routing.
```
Matches the claim: **YES**.

<!-- distinct sources: issue + routing-config.yaml + tier_router.sh + task-dispatcher.py + cost-policy doc + #3205 plan + memory = 7 -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-06-17-issue-3209-tier-table-single-source.md |
| Resolver (extend) | `scripts/ai/routing_resolver.py` |
| Resolver tests (extend) | `tests/ai/test_routing_resolver.py` |
| Tier-router cost-aligned test (new) | `tests/coordination/test_tier_router_cost_aligned.py` |
| Modify | `scripts/coordination/routing/lib/tier_router.sh` (load table from resolver) |
| Modify | `scripts/ai/task-dispatcher.py` (derive tier preference from resolver) |
| Reconcile | `config/agents/routing-config.yaml` (`tiers.*` → cost-aligned) |
| Update | `tests/config/test_routing_config_observed_behavior.py` (SIMPLE/STANDARD → codex) |
| Update | docs/plans/README.md (index) |
| Update (memory) | `routing-config-is-advisory.md` (tier maps now enforced too) |

---

## Deliverable

`scripts/ai/routing_resolver.py` becomes the single source for **both** context and tier routing; `tier_router.sh` and `task-dispatcher.py` derive their tier chains from it (no hardcoded tier copies); `routing-config.yaml` `tiers.*` is reconciled to the cost-aligned table (SIMPLE/STANDARD primary=codex), with a test that drives the real router proving no Claude on cheap tiers.

---

## Canonical cost-aligned table (proposed — matches the executed bash)

| Tier | primary | fallbacks |
|---|---|---|
| SIMPLE | codex | [gemini, claude] |
| STANDARD | codex | [claude, gemini] |
| COMPLEX | claude | [gemini, codex] |
| REASONING | claude | [gemini, codex] |

**hermes is dropped from tier chains** (recommended): the executed bash never had it, and `check_provider_available` can't dispatch it; hermes routing lives in `dimensions` (research/data → hermes) and `execution_contexts` (hermes_batch), which are unchanged. This keeps runtime tier behavior identical to today's executed bash — the change is *single-sourcing*, not re-routing. (Decision flagged for approval; alternative = keep hermes in cheap-tier fallbacks.)

---

## Design — YAML is the single source; bash is GENERATED, not read at runtime (post-r1)

r1-MAJOR-1: making `route_by_tier` read the YAML at runtime costs ~2s per `uv run` (measured 2.07s) × 4 tiers, on every `route.sh`/`orchestrate.sh` source. **Rejected.** Instead:

- **YAML `tiers.*` is the single source of truth.**
- **`tier_router.sh` bash arrays are GENERATED from the YAML** (resolver `--emit-bash-table`), committed, and a **CI drift-guard test** fails if they diverge. → zero runtime resolver calls on the hot path; the no-context interactive route stays as fast as today. (The #3205 cost-ceiling `_resolver --filter` call still runs only when `ROUTE_CONTEXT` is set — unchanged.)
- **`route.sh --config` display (the 4th copy, r1-F3) is rendered live** from the resolver — `--config` is a rare human-inspection command, so one resolver call there is fine, and it removes the copy entirely rather than guarding it.
- **`task-dispatcher.py` imports the resolver in-process** (no subprocess, fast) and derives its tier preference from `tier_chain`.

This gives genuine single-source ("copies generated from it") with zero hot-path latency. The cost: editing the YAML table requires regenerating the bash arrays (one command); CI catches a forgotten regen.

## Pseudocode

Resolver additions (CLI-normalized, same `cli()` map as #3205; `ROUTING_CONFIG_PATH` env override for tests — r1-F2):
```
ROUTING_CONFIG = env ROUTING_CONFIG_PATH or <repo>/config/agents/routing-config.yaml
KNOWN_TIERS = {SIMPLE, STANDARD, COMPLEX, REASONING}
class UnknownTierError(ValueError)
tier_chain(tier, cfg=None) -> list[str]:
    t = (cfg or load()).tiers.get(tier.upper())
    if t is None: raise UnknownTierError(tier)            # fail closed
    return cli-normalized, dedup, order-preserving [t.primary, *t.fallbacks]
emit_bash_table(cfg=None) -> str:                          # generator for tier_router.sh
    # prints the exact `declare -A TIER_PRIMARY/FALLBACK1/FALLBACK2(...)` blocks
CLI (top-level mutually-exclusive: --context | --tier | --all-tiers | --emit-bash-table) — r1-F4:
    --tier NAME           -> chain, exit 3 on unknown tier
    --all-tiers           -> JSON {tier: chain}            # one-call, used by --config render
    --emit-bash-table     -> the declare -A blocks         # used by the generator/drift-guard
```

`tier_router.sh` — arrays GENERATED from YAML (committed), with a header marker so the drift-guard + regen target them:
```
# >>> GENERATED FROM routing-config.yaml tiers.* via routing_resolver.py --emit-bash-table — do not hand-edit
declare -A TIER_PRIMARY=( [SIMPLE]="codex" [STANDARD]="codex" [COMPLEX]="claude" [REASONING]="claude" )
declare -A TIER_FALLBACK1=( [SIMPLE]="gemini" [STANDARD]="claude" [COMPLEX]="gemini" [REASONING]="gemini" )
declare -A TIER_FALLBACK2=( [SIMPLE]="claude" [STANDARD]="gemini" [COMPLEX]="codex" [REASONING]="codex" )
# <<< END GENERATED
```
(No runtime resolver call added here. route_by_tier logic + the #3205 context filter unchanged.)

`route.sh --config` — replace the hardcoded lines 217-220 with a live render:
```
echo "Routing Table:"
_resolver --all-tiers | jq -r 'to_entries[] | "  \(.key): \(.value|join(" -> "))"'
```

`task-dispatcher.py` — in-process import, no subprocess:
```
def tier_preference(tier):
    chain = routing_resolver.tier_chain(tier)                       # cost-aligned, cli tokens
    return chain + [a for a in KNOWN_AGENTS if a not in chain]      # append hermes (dimension/keyword can still surface it)
# replaces the hardcoded TIER_AGENT_PREFERENCE dict
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/ai/routing_resolver.py` | `tier_chain`/`--tier`/`--all-tiers`/`--emit-bash-table`/`UnknownTierError`; `ROUTING_CONFIG_PATH` env override (r1-F2/F4) |
| Modify | `scripts/coordination/routing/lib/tier_router.sh` | arrays GENERATED-from-YAML (committed) with marker block; no runtime resolver call (r1-F1) |
| Modify | `scripts/coordination/routing/route.sh` | `--config` renders table live from resolver (removes 4th copy, r1-F3) |
| Modify | `scripts/ai/task-dispatcher.py` | `tier_preference()` imports resolver; drop hardcoded dict |
| Reconcile | `config/agents/routing-config.yaml` | `tiers.*` → cost-aligned table above (single source) |
| Update | `tests/config/test_routing_config_observed_behavior.py` | SIMPLE/STANDARD primary now codex |
| Create | `tests/coordination/test_tier_router_cost_aligned.py` | real route_by_tier: SIMPLE/STANDARD→codex, COMPLEX/REASONING→claude |
| Create | `tests/coordination/test_tier_table_no_drift.py` | drift-guard: committed bash arrays == `--emit-bash-table`; route.sh display has no hardcoded tiers |
| Modify | `tests/ai/test_routing_resolver.py` | tier_chain + --tier + --all-tiers + unknown-tier fail-closed + `ROUTING_CONFIG_PATH` proof |
| Update | docs/plans/README.md | index |

---

## TDD Test List

| Test | Verifies | Input | Expected |
|---|---|---|---|
| test_tier_chain_simple_cost_aligned | resolver tier chain | "SIMPLE" | ["codex","gemini","claude"] |
| test_tier_chain_complex | | "COMPLEX" | ["claude","gemini","codex"] |
| test_tier_chain_cli_normalized | no provider tokens | any | no "openai-codex" |
| test_tier_unknown_fails_closed | unknown tier errors | "BOGUS" | UnknownTierError / CLI exit 3 |
| test_cli_tier_mode | CLI `--tier SIMPLE` | — | "codex\ngemini\nclaude" |
| test_cli_all_tiers_json | `--all-tiers` one-call | — | JSON, 4 tiers, cost-aligned |
| test_config_path_override (r1-F2) | `ROUTING_CONFIG_PATH` points at a temp YAML | temp SIMPLE primary=gemini | tier_chain("SIMPLE")[0]=="gemini" |
| test_router_simple_selects_codex (real) | route_by_tier SIMPLE, all avail, no context | — | provider=="codex" (not claude) |
| test_router_standard_selects_codex (real) | route_by_tier STANDARD | — | provider=="codex" |
| test_router_complex_selects_claude (real) | route_by_tier COMPLEX | — | provider=="claude" (unchanged) |
| test_tier_table_no_drift (r1-F1/F3) | committed bash arrays == resolver `--emit-bash-table`; route.sh has no hardcoded SIMPLE/STANDARD lines | — | match; no drift |
| test_simple_under_ceiling_still_codex (#3205 compose) | route_by_tier SIMPLE + ROUTE_CONTEXT=hermes_batch | — | provider=="codex", never claude |
| test_dispatcher_simple_not_claude_first | advisory prefers cost-aligned | --tier simple, neutral task | recommended_agent != "claude" |
| test_dispatcher_no_context_can_pick_claude (existing, must stay green) | reasoning+architecture | — | claude (verified survives codex-first preference) |
| test_observed_behavior_simple_standard_codex (updated) | YAML reconciled | — | tiers.SIMPLE/STANDARD.primary=="codex" |

`test_config_path_override` proves the resolver (python single-source) reads YAML at runtime; `test_tier_table_no_drift` proves the bash arrays are a CI-enforced generation of that same source (not reconciled-by-coincidence). Together they satisfy "single source; copies generated from it" without the rejected runtime-read latency.

---

## Acceptance Criteria

- [ ] `routing-config.yaml` `tiers.*` is the single source (cost-aligned: SIMPLE/STANDARD primary=codex); `task-dispatcher.py` dict removed (imports resolver); `tier_router.sh` arrays generated from it + CI drift-guarded; `route.sh --config` renders live (4th copy removed)
- [ ] Real router selects codex (not claude) for SIMPLE/STANDARD; claude for COMPLEX/REASONING — proven by a test driving `route_by_tier`
- [ ] `ROUTING_CONFIG_PATH` override proves the resolver reads YAML at runtime; `test_tier_table_no_drift` proves bash is a CI-enforced generation (no hot-path latency added — r1-MAJOR-1)
- [ ] `test_routing_config_observed_behavior.py` updated + green
- [ ] #3205 cost-ceiling tests still green; SIMPLE+hermes_batch still selects codex (compose test)
- [ ] No regression: `uv run pytest tests/config/ tests/ai/ tests/coordination/` (pre-existing unrelated `test_agents_and_review_policy...` failure excepted); `bash -n` clean
- [ ] Review artifacts posted

---

## Adversarial Review Summary

**r1 — Claude (adversarial subagent), 2026-06-17:** verdict **MAJOR**. All findings verified against the live tree and incorporated:

| # | Sev | Finding | Resolution |
|---|---|---|---|
| F1 | MAJOR | Source-time resolver loading = ~8s (4× `uv run` @ 2.07s) on every route.sh/orchestrate.sh | Rejected runtime-read; bash arrays now GENERATED from YAML + committed + CI drift-guard → zero hot-path latency |
| F2 | MAJOR | No config-path override → the single-source proof test can't reach the bash/python path against a temp YAML | Added `ROUTING_CONFIG_PATH` env override + `test_config_path_override` |
| F3 | MAJOR | A **4th** hardcoded tier copy at `route.sh:216-220` (the `--config` display), unaccounted | `--config` now renders live from `--all-tiers`; drift-guard asserts no hardcoded tier lines remain |
| F4 | MINOR | argparse: `--context required=True` blocks adding `--tier` | top-level mutually-exclusive `--context|--tier|--all-tiers|--emit-bash-table` |
| — | note | dispatcher codex-first preference must not break `test_dispatcher_no_context_can_pick_claude` | r1 traced the scoring: reasoning+architecture still yields claude (1.45 vs 0.75); kept as an explicit regression test |
| — | note | hermes drop from tier chains verified safe (no reader depends on it; dimensions/contexts unchanged) | proceed |

**r2 — Codex (fanout):** **UNAVAILABLE** — `codex exec` timed out at the 600s limit (stuck in sandbox PreToolUse hooks; SIGTERM/exit 143, empty output). Per SHARED_SOUL "Cross-Review Routing", provider outage degrades T2→T1 documented; r1 (MAJOR, verified) carries the review. Artifact: `scripts/review/results/2026-06-17-plan-3209-codex.md`.

**Overall result after r1 revisions:** PASS (T1, r2 documented UNAVAILABLE).

**Code-stage r3 — Claude (adversarial subagent), 2026-06-17:** verdict **MINOR** (no blockers). Verified across all vectors: cost-ceiling does not regress (claude impossible under hermes_batch on every tier incl. emergency), drift-guard fails correctly when YAML changes, fail-closed holds, live `--config` render works. Cleanliness fixes applied: removed dead `ROUTING_CONFIG` constant + `context_mode` var; `--tier`+`--context` now rejected (contract consistency); `task-dispatcher` honors `ROUTING_CONFIG_PATH` (no split-config); drift-guard test pins the repo config; strengthened the SIMPLE-dispatcher assertion to `==codex`.

---

## Risks and Open Questions

- **Open (approval — only real fork left):** hermes dropped from tier chains (recommended — matches executed reality; check_provider_available can't dispatch hermes; it routes via `dimensions`/`execution_contexts`). Alternative: keep hermes in SIMPLE/STANDARD fallbacks. r1 verified dropping is safe (no reader depends on tier-hermes).
- **Risk — `task-dispatcher` advisory behavior change:** today claude-first; after, codex-first on cheap tiers. Dimension/keyword boosts still let claude/hermes win on matching tasks. r1 traced + this plan pins `test_dispatcher_no_context_can_pick_claude` (reasoning+architecture → claude, 1.45 vs 0.75) as a regression guard; the #3205 hermes_batch dispatcher test stays valid.
- **Risk — generated-array staleness:** if someone edits YAML `tiers.*` without regenerating the bash block, the executed router would lag the source. Mitigation: `test_tier_table_no_drift` fails CI on divergence; the GENERATED marker block + a one-command regen make the workflow explicit.
- **Risk — cost-ceiling composition (#3205):** the filter runs on top of the (now-generated) tier chain; SIMPLE under hermes_batch = codex (primary already codex; claude filtered from fallback) — pinned by `test_simple_under_ceiling_still_codex`.
- **Risk — `test_simple_and_standard_route_to_claude` update:** required, not optional; in Files to Change so it isn't missed.
- **Resolved (r1):** hot-path latency (no runtime resolver call in bash); proof-test reachability (`ROUTING_CONFIG_PATH`); the 4th copy (route.sh `--config` rendered live).

---

## Complexity: T2

**T2** — multi-file (resolver + bash + python + YAML + tests), TDD, cross-language, but built on the #3205 substrate. Plan review = 2 providers.
