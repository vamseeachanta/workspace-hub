# Plan for #3205: Executed-router consolidation — make the routing-config cost ceiling actually enforced

> **Status:** adversarial-reviewed (r1 Claude MAJOR + r2 Codex MAJOR → both revised in)
> **Complexity:** T2
> **Date:** 2026-06-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3205
> **Client:** N/A
> **Project:** (none)
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-17-plan-3205-claude.md | ...-codex.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `config/agents/routing-config.yaml` — declarative SSoT. `tiers.*` all `primary: claude`; `execution_contexts.hermes_batch` has `forbid: [claude]`, `cost_ceiling: true`, `primary: openai-codex`, `fallbacks: [gemini]` (added #3192).
- Found: `scripts/coordination/routing/lib/tier_router.sh` — the **executed** tier router (`route_by_tier()`). Assigns `ROUTING_CONFIG=` (line 10) but **never reads it**; routing is hardcoded bash arrays `TIER_PRIMARY/FALLBACK1/FALLBACK2` (lines 13–32). No notion of execution_contexts/forbid. Emergency default is `claude` (lines 97–100) — would **violate** a cost ceiling.
- Found: `scripts/coordination/routing/route.sh` — CLI entry; sources `tier_router.sh`, calls `route_by_tier "$tier" "$classifier_provider" "$confidence"` (line 278). No `--context` flag today.
- Found (**r1-F1 — was missed in draft**): `scripts/coordination/routing/orchestrate.sh:61` — a **second executed caller** of `route_by_tier` (also sources `tier_router.sh` at line 27). Threading context only through `route.sh` would leave this path forbid-blind. **Fix:** put the filter *inside* `route_by_tier` so BOTH callers inherit it; thread `ROUTE_CONTEXT` through both entrypoints.
- Found (**r1-F2 — was missed in draft**): `scripts/coordination/routing/lib/provider_filter.sh:43–47` (`filter_available_providers`) **unconditionally appends `claude`** when usage <80% — a separate forbid-blind availability layer sourced by both route.sh and orchestrate.sh. Must also honor the ceiling.
- Found: `scripts/ai/task-dispatcher.py` — advisory CLI. Loads the YAML but reads only `tiers.*.description` (line 166); provider preference is the hardcoded `TIER_AGENT_PREFERENCE` dict (lines 63–68). No execution_contexts/forbid awareness.
- Found (**r1-F9 — was missed in draft**): `scripts/ai/overnight-batch-planner.py` — routes `overnight`/`overnight-batch` issues; `AGENT_MODEL_MAP` maps to `claude` and it has a `claude` "safe default". `overnight-batch` IS a Hermes role (routing-config.yaml:99) → the hermes_batch ceiling context. This is the **highest-volume Claude leak** and must be brought in scope.
- Found: `scripts/dispatch/route.py` (#3030) — lane-quota dispatcher, lane-label driven, does not reference routing-config. **Out of scope** (different axis: lane quota, not tier/context routing).

### Standards
Not applicable (harness/infrastructure issue).

### LLM Wiki pages consulted
No relevant wiki pages (Client: N/A).

### Documents consulted
- `docs/governance/2026-06-17-cost-ceiling-policy.md` — SSoT for the policy; §"Enforcement status — ADVISORY ONLY" explicitly says routers don't parse the YAML and the ceiling must not be relied on at runtime until this consolidation lands. This plan flips it to ENFORCED.
- `docs/plans/2026-06-17-issue-3192-routing-config-cost-policy.md` — the predecessor plan that introduced `execution_contexts` as declarative-only.
- Memory `routing-config-is-advisory.md` — confirms THREE drifted copies and the token-space details; flags that editing the YAML does not change runtime routing.
- Issue #3205 (body) — acceptance criteria; follow-up to #3192, parent epic #3058.

### Gaps identified
- No single executed source that reads `execution_contexts` / `forbid` from the YAML. All forbid-blind surfaces must consult one resolver.
- **Forbid-blind executed surfaces (full set, post-r1):** `route_by_tier` (tier_router.sh) reached via BOTH route.sh + orchestrate.sh (r1-F1); `filter_available_providers` (provider_filter.sh, r1-F2); `task-dispatcher.py`; `overnight-batch-planner.py` (r1-F9). All four must be wired.
- No `--context`/`ROUTE_CONTEXT` input on any router → no way to signal "this is a Hermes-batch dispatch" so the ceiling can apply.
- `tier_router.sh` emergency default (`claude`) is unsafe under a cost ceiling — must default to the context primary (CLI-normalized) instead.
- The resolver must emit **CLI-normalized** provider tokens (`openai-codex`→`codex`) for its bash-facing modes so the bash routers can use the output directly — no invented `map_provider_to_cli` glue (r1-F3/F4).
- **Latent (deferred, NOT this scope):** the YAML `tiers` block (claude-everywhere) conflicts with the executed bash arrays (SIMPLE/STANDARD=codex). Operator decision 2026-06-17: tier table should become cost-aligned (codex for cheap tiers). Filed as a separate follow-up issue (see Deliverable) — this plan does **not** touch tier chains.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-17 via `gh issue view`):
- `#3205` — OPEN — "Executed-router consolidation: make routing-config cost ceiling actually enforced" (labels: domain:harness, lane:claude, priority:high)
- `#3192` — CLOSED/merged (#3201) — introduced execution_contexts (advisory)
- `#3058` — OPEN — parent epic (self-enforcing invariants)

**File existence** (`ls -la` 2026-06-17):
- EXISTS: `scripts/coordination/routing/lib/tier_router.sh`, `scripts/ai/task-dispatcher.py`, `scripts/coordination/routing/route.sh`, `config/agents/routing-config.yaml`, `tests/config/test_cost_ceiling_policy.py`
- MISSING (new — this plan creates): `scripts/ai/routing_resolver.py`, `tests/ai/test_routing_resolver.py`, `tests/ai/test_task_dispatcher_cost_ceiling.py`, `tests/coordination/test_tier_router_cost_ceiling.py`

**Line excerpts** (`config/agents/routing-config.yaml` 126–131):
```
execution_contexts:
  hermes_batch:               # docs / data-analysis / delegation / overnight-batch
    primary: openai-codex
    fallbacks: [gemini]
    forbid: [claude]          # cost ceiling
    cost_ceiling: true
```

**Gap proof** (`grep -n "execution_contexts\|forbid" scripts/coordination/routing/lib/tier_router.sh scripts/ai/task-dispatcher.py` → empty) → confirms neither executed router references the ceiling today.

**Reproduction proof** (Step 1.5 — the issue alleges "advisory only / not enforced"):
```
$ grep -n "ROUTING_CONFIG" scripts/coordination/routing/lib/tier_router.sh
10:ROUTING_CONFIG="${ROUTER_CONFIG_DIR}/agents/routing-config.yaml"
# ...no other reference — the var is assigned and never read.
```
- Reproduced at: 2026-06-17. Failure mode (cost ceiling is declarative only; routers hold hardcoded chains) matches the issue claim: **YES**.

<!-- distinct sources: issue #3205 + routing-config.yaml + tier_router.sh + task-dispatcher.py + cost-ceiling-policy doc + memory = 6 -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-06-17-issue-3205-executed-router-consolidation.md |
| Resolver (new) | `scripts/ai/routing_resolver.py` |
| Resolver tests (new) | `tests/ai/test_routing_resolver.py` |
| Dispatcher ceiling test (new) | `tests/ai/test_task_dispatcher_cost_ceiling.py` |
| Overnight-planner ceiling test (new) | `tests/ai/test_overnight_planner_cost_ceiling.py` |
| Tier-router ceiling test (new) | `tests/coordination/test_tier_router_cost_ceiling.py` |
| Modify | `scripts/ai/task-dispatcher.py` |
| Modify | `scripts/ai/overnight-batch-planner.py` (r1-F9: no claude default under overnight-batch) |
| Modify | `scripts/coordination/routing/lib/tier_router.sh` (filter inside `route_by_tier`; safe emergency default) |
| Modify | `scripts/coordination/routing/lib/provider_filter.sh` (r1-F2: honor forbid) |
| Modify | `scripts/coordination/routing/route.sh` (thread `--context`) |
| Modify | `scripts/coordination/routing/orchestrate.sh` (r1-F1: thread `ROUTE_CONTEXT`) |
| Update | `config/agents/routing-config.yaml` (`routing_resolution_note` ADVISORY → ENFORCED) |
| Update | `docs/governance/2026-06-17-cost-ceiling-policy.md` (§Enforcement ADVISORY → ENFORCED) |
| Update | `tests/config/test_cost_ceiling_policy.py` (`test_cost_policy_reference_resolves` now asserts "enforced") |
| Update | docs/plans/README.md (index this plan) |
| Update (memory) | `~/.claude/.../routing-config-is-advisory.md` (ceiling now enforced; tier maps still advisory) |

---

## Deliverable

A single executed resolver (`scripts/ai/routing_resolver.py`, the only place forbid policy is interpreted) that reads `execution_contexts` from `routing-config.yaml`; **every** forbid-blind executed surface (`route_by_tier` → route.sh + orchestrate.sh, `filter_available_providers`, `task-dispatcher.py`, `overnight-batch-planner.py`) consults it via a `--context`/`ROUTE_CONTEXT` input and **cannot select a forbidden provider** — so a Hermes-/overnight-batch dispatch can never select `claude` at runtime — with tests that drive the real surfaces (positive selection assertions, not just `≠ claude`), and the policy doc flipped ADVISORY → ENFORCED (scoped to the cost ceiling). A follow-up issue is filed for the deferred tier-table reconciliation.

---

## Pseudocode

`scripts/ai/routing_resolver.py` (the ONE place forbid policy is interpreted; all bash-facing output is CLI-normalized):
```
TOKEN_TO_CLI = {"openai-codex": "codex"}     # provider-token -> CLI-token (single source)
def cli(tok): return TOKEN_TO_CLI.get(tok, tok)

load_routing_config(path=ROUTING_CONFIG) -> dict           # cached yaml.safe_load
resolve_context(name, cfg) -> dict | None                  # execution_contexts[name] or None
forbidden_providers(name, cfg) -> set[str]                 # {cli(t) for t in ctx.forbid}  (normalized)
is_cost_ceiling(name, cfg) -> bool                         # ctx.cost_ceiling truthy
context_chain(name, cfg) -> list[str]                      # [cli(primary)] + [cli(f) for f in fallbacks], minus forbid

filter_candidates(candidates, context, cfg) -> list[str]:
    if not context: return candidates                      # context=None (interactive) -> unchanged
    ctx = resolve_context(context, cfg)
    if ctx is None: raise UnknownContextError(context)     # r2-C2 FAIL CLOSED: explicit-but-unknown context is an error,
                                                           #   NOT pass-through (a typo `hermes-batch` must not leak claude)
    forbid = forbidden_providers(context, cfg)
    kept = [c for c in candidates if cli(c) not in forbid] # preserve order, compare normalized
    if not kept: kept = context_chain(context, cfg)        # all forbidden -> context chain (already cli+forbid-filtered)
    return kept                                            # NEVER blank lines; [] prints nothing

CLI (all emit CLI-normalized tokens, one per line, no trailing blank):
  --context NAME --filter c1,c2,c3   -> kept list   (empty --filter "" -> [], not [""])
  --context NAME --forbidden         -> forbidden tokens
  --context NAME --chain             -> context_chain (used by the emergency default)
  --context NAME --json              -> {primary_cli,fallbacks_cli,forbid_cli,cost_ceiling}
  Unknown explicit context (any mode) -> stderr error + EXIT 3 (callers must abort, not fall to claude).

# Dependency contract (r2-C3): resolver self-bootstraps pyyaml (same pattern as
#   task-dispatcher.py:24-29 / overnight-batch-planner.py); bash callers invoke it
#   via `uv run` when available, else `python3` (which self-bootstraps). A bash
#   helper centralizes this:
#     _resolver() { if command -v uv >/dev/null; then uv run --quiet "$RESOLVER" "$@";
#                   else python3 "$RESOLVER" "$@"; fi; }
```

`tier_router.sh` — apply the filter **inside `route_by_tier`** (so route.sh AND orchestrate.sh both inherit it, r1-F1), after the candidate list is built (~line 82), guarding the empty case (r1-F7):
```
if [[ -n "${ROUTE_CONTEXT:-}" && ${#candidates[@]} -gt 0 ]]; then
    local _csv; _csv="$(IFS=,; echo "${candidates[*]}")"
    if ! mapfile -t candidates < <(_resolver --context "$ROUTE_CONTEXT" --filter "$_csv"); then
        echo "route_by_tier: unknown/invalid context '$ROUTE_CONTEXT' — aborting (fail closed)" >&2
        return 3        # r2-C2: do NOT fall through to claude on a bad context
    fi
fi
# availability loop unchanged (operates on the now-forbid-free candidates)
# emergency default — CLI-normalized context primary, NEVER claude under a ceiling context:
if [[ -z "$chosen" ]]; then
    if [[ -n "${ROUTE_CONTEXT:-}" ]]; then
        chosen=$(_resolver --context "$ROUTE_CONTEXT" --chain | head -1)   # already cli-normalized
        reason="Emergency under context $ROUTE_CONTEXT: context primary $chosen"
    else
        chosen="claude"; reason="Emergency: no CLI providers detected, defaulting to claude"
    fi
fi
# emit context + forbidden in the JSON for auditability
```

`provider_filter.sh::filter_available_providers` (r1-F2, r2-C5): build `available_providers` as today, then — when `ROUTE_CONTEXT` is set — pass the **whole list** through the resolver's `--filter` mode (the single filtering implementation; NOT a re-implemented shell drop):
```
if [[ -n "${ROUTE_CONTEXT:-}" ]]; then
    local _csv; _csv="$(IFS=,; echo "${available_providers[*]}")"
    mapfile -t available_providers < <(_resolver --context "$ROUTE_CONTEXT" --filter "$_csv") \
        || { echo "filter_available_providers: bad context '$ROUTE_CONTEXT'" >&2; return 3; }
fi
```
This way the unconditional `claude` append (line 47) is filtered back out by the resolver if `claude` is forbidden — no second copy of the forbid rule.

`route.sh` + `orchestrate.sh`: add `--context NAME` → `export ROUTE_CONTEXT="$NAME"` before the pipeline. (route_by_tier reads the env, so no signature change.)

`task-dispatcher.py`: add `--context`; after `score_agents`, drop agents whose token ∈ `forbidden_providers(context)`; re-pick best; add `context`/`forbidden` to output JSON. (forbid=[claude] over {hermes,claude,codex,gemini} can't empty the list, but guard anyway → context_chain.)

`overnight-batch-planner.py` (r1-F9): treat `overnight`/`overnight-batch` issues as the `hermes_batch` context. When mapping an issue to an agent, pass the resolved agent through `filter_candidates([agent, *fallbacks], "hermes_batch")` (importing the resolver directly — same process, no subshell); the `claude` "safe default" becomes the context primary (`codex`). An explicit `agent:claude` label on an overnight-batch issue is a **hard error** (surfaced, not silently downgraded).
- **r2-C4 (dry-run fixture conflict):** `_synthetic_issues()` issue #1823 currently carries `agent:claude` + `overnight` (lines 157-160) and is returned by `--dry-run` (lines 106-110) → the new hard-error would break dry-run. Fix: relabel #1823's synthetic entry to `agent:codex` so `--dry-run` stays clean/usable, and exercise the error path with a **dedicated** unit test that feeds an `agent:claude`+`overnight` issue straight to the mapping function (not via the bundled dry-run set).

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/ai/routing_resolver.py` | single source where forbid policy is interpreted; CLI-normalized output |
| Create | `tests/ai/test_routing_resolver.py` | unit tests for the resolver (incl. cli-normalization, empty-filter) |
| Create | `tests/ai/test_task_dispatcher_cost_ceiling.py` | drives real dispatcher; claude excluded under hermes_batch |
| Create | `tests/ai/test_overnight_planner_cost_ceiling.py` | overnight-batch issue never routes to claude; `agent:claude` label errors |
| Create | `tests/coordination/test_tier_router_cost_ceiling.py` | drives real `route_by_tier` (positive: selects codex; emergency ≠ claude; real `command -v` variant) |
| Modify | `scripts/ai/task-dispatcher.py` | `--context`, consult resolver, drop forbidden |
| Modify | `scripts/ai/overnight-batch-planner.py` | r1-F9: resolver-gate overnight-batch; no claude default |
| Modify | `scripts/coordination/routing/lib/tier_router.sh` | filter inside `route_by_tier`; safe emergency default; emit context/forbidden |
| Modify | `scripts/coordination/routing/lib/provider_filter.sh` | r1-F2: drop forbidden tokens when ROUTE_CONTEXT set |
| Modify | `scripts/coordination/routing/route.sh` | `--context` flag → `ROUTE_CONTEXT` |
| Modify | `scripts/coordination/routing/orchestrate.sh` | r1-F1: `--context` flag → `ROUTE_CONTEXT` |
| Update | `config/agents/routing-config.yaml` | `routing_resolution_note`: ADVISORY → ENFORCED (cost ceiling only) |
| Update | `docs/governance/2026-06-17-cost-ceiling-policy.md` | §Enforcement: ADVISORY → ENFORCED, scoped to the cost ceiling (not tier routing) |
| Update | `tests/config/test_cost_ceiling_policy.py` | `test_cost_policy_reference_resolves` assert "enforced" not "advisory only" |
| Update | docs/plans/README.md | index this plan |
| Comment | issue #3205 | re-scope acceptance #1 to "context routing"; link the deferred tier-table issue (before plan-approved) |

---

## TDD Test List

| Test name | What it verifies | Input | Expected |
|---|---|---|---|
| test_forbidden_providers_hermes_batch | parses forbid from YAML | context="hermes_batch" | {"claude"} |
| test_forbidden_providers_interactive_none | non-ceiling context has no forbid | "interactive_dev" | empty set |
| test_filter_drops_claude_preserves_order | order-preserving removal | ["claude","codex","gemini"], "hermes_batch" | ["codex","gemini"] |
| test_filter_no_context_passthrough | None context unchanged | ["claude","codex"], None | ["claude","codex"] |
| test_filter_unknown_context_fails_closed | r2-C2: explicit unknown context errors, no pass-through | ["claude"], "hermes-batch" (typo) | raises UnknownContextError / CLI exit 3 |
| test_router_aborts_on_bad_context | r2-C2: route_by_tier returns 3 (not claude) when ROUTE_CONTEXT invalid | ROUTE_CONTEXT="bogus" | rc=3; no claude selection |
| test_resolver_invoked_via_uv_or_python3 | r2-C3: `_resolver` helper works with uv present and absent (PATH-stubbed) | — | resolver runs; pyyaml available |
| test_filter_all_forbidden_falls_to_context_chain | empty after filter → context chain | ["claude"], "hermes_batch" | ["codex","gemini"] (CLI-normalized) |
| test_chain_is_cli_normalized | r1-F3/F4: openai-codex→codex in chain output | "hermes_batch" | ["codex","gemini"] (no "openai-codex") |
| test_filter_empty_input_is_empty_list | r1-F7: `--filter ""` ≠ [""] | "", "hermes_batch" | [] (no blank-string candidate) |
| test_is_cost_ceiling_true_false | reads cost_ceiling flag | hermes_batch / interactive_dev | True / False |
| test_cli_filter_mode | CLI `--context hermes_batch --filter claude,codex` | — | stdout "codex" |
| test_cli_chain_mode | CLI `--context hermes_batch --chain` | — | "codex\ngemini" |
| test_dispatcher_hermes_context_excludes_claude | real dispatcher main() | --task "summarize report" --tier complex --context hermes_batch | recommended_agent ≠ claude; claude ∉ alternatives |
| test_dispatcher_no_context_can_pick_claude | no regression to interactive path | same task, no --context | claude selectable (unchanged behavior) |
| test_tier_router_context_selects_codex (positive) | real `route_by_tier`, all providers available (stub→0), ROUTE_CONTEXT=hermes_batch on COMPLEX | — | `.provider == "codex"`; reason indicates filter (not emergency); "claude" ∉ candidates |
| test_tier_router_real_availability_only_codex | r1-F5: real `check_provider_available`, only `codex` on PATH | — | `.provider == "codex"` (proves CLI-normalization end-to-end) |
| test_tier_router_emergency_default_not_claude | no providers available + ceiling context | stub check_provider_available→1 | `.provider` == context primary ("codex"), ≠ "claude" |
| test_orchestrate_context_excludes_claude | r1-F1: drive orchestrate.sh path with --context | COMPLEX task | selected provider ≠ "claude" |
| test_provider_filter_drops_claude_under_context | r1-F2: `filter_available_providers` w/ ROUTE_CONTEXT=hermes_batch, claude usage <80% | — | "claude" ∉ available_providers |
| test_overnight_planner_no_claude_default | r1-F9: overnight-batch issue, no agent label | — | assigned agent ≠ "claude" (== codex) |
| test_overnight_planner_agent_claude_label_errors | explicit agent:claude on overnight-batch | — | hard error / non-zero, surfaced |

---

## Acceptance Criteria

- [ ] `uv run pytest tests/ai/test_routing_resolver.py tests/ai/test_task_dispatcher_cost_ceiling.py tests/ai/test_overnight_planner_cost_ceiling.py tests/coordination/test_tier_router_cost_ceiling.py -v` all pass
- [ ] `uv run pytest tests/config/test_cost_ceiling_policy.py -v` passes (updated assertion)
- [ ] Driving the **real** routers under `hermes_batch`/overnight-batch never selects `claude` — across ALL four surfaces: route_by_tier (route.sh + orchestrate.sh), filter_available_providers, task-dispatcher, overnight-batch-planner (acceptance #2; positive selection asserted, not just `≠ claude`)
- [ ] One source (`routing_resolver.py`) is the only place forbid policy is interpreted; every surface delegates to it — no duplicated forbid logic (acceptance #1, scoped to **context** routing per the issue re-scope comment)
- [ ] `docs/governance/2026-06-17-cost-ceiling-policy.md` §Enforcement reads ENFORCED (scoped to cost ceiling) with the resolver + `--context` mechanism described (acceptance #3)
- [ ] `routing-config.yaml` `routing_resolution_note` updated to ENFORCED
- [ ] Issue #3205 acceptance #1 re-scoped to "context routing" via comment; follow-up issue filed (tier-table reconciliation → cost-aligned codex-cheap) under epic #3058, linked from this issue
- [ ] No regression: `uv run pytest tests/config/ tests/ai/ tests/coordination/` green; `bash -n` clean on all edited shell scripts
- [ ] Review artifacts posted to scripts/review/results/

---

## Adversarial Review Summary

**r1 — Claude (adversarial subagent), 2026-06-17:** verdict **MAJOR**. Findings, all verified against the live tree and incorporated:

| # | Sev | Finding | Resolution in revised plan |
|---|---|---|---|
| F1 | MAJOR | `orchestrate.sh:61` is a second executed caller of `route_by_tier`, uncovered → claude leaks there | Filter moved **inside `route_by_tier`**; `ROUTE_CONTEXT` threaded through both route.sh + orchestrate.sh; `test_orchestrate_context_excludes_claude` added |
| F2 | MAJOR | `provider_filter.sh:43-47` unconditionally re-adds `claude` (usage<80%) — forbid-blind | provider_filter honors `ROUTE_CONTEXT` forbid; `test_provider_filter_drops_claude_under_context` added |
| F3/F4 | MAJOR | invented `map_provider_to_cli`; `openai-codex` token wouldn't match bash CLI token → emergency fallthrough | resolver owns `cli()` normalization; `--filter`/`--chain`/`--json` emit CLI tokens; `--chain` replaces the jq glue; normalization tests added |
| F5 | MAJOR | tier-router test only asserted `≠ claude` (satisfiable by buggy emergency path); stubbing masks real path | added **positive** `test_tier_router_context_selects_codex` + real-`command -v` `test_tier_router_real_availability_only_codex` |
| F6 | MAJOR | acceptance #1 says "tier/context"; plan silently re-scoped to context-only | explicit step: comment on #3205 re-scoping #1 to "context routing" + link deferred tier issue BEFORE plan-approved; surfaced to user at approval |
| F7 | MINOR | empty-filter / mapfile blank-line edge cases | empty-input guard in bash + resolver `--filter ""`→[] test |
| F8 | MINOR | "ENFORCED" doc language could imply tier routing enforced | doc + note scoped explicitly to the cost ceiling |
| F9 | MAJOR | `overnight-batch-planner.py` routes overnight-batch and defaults to claude — biggest leak | brought in scope; resolver-gated; `agent:claude` on overnight-batch is a hard error; 2 tests added |

**r2 — Codex (via `scripts/review/plan-review-fanout.sh`, `env -u CLAUDECODE` workaround for the stdin-hang #2684), 2026-06-17:** verdict **MAJOR**. Artifact: `scripts/review/results/2026-06-17-plan-3205-codex.md`. All 5 findings verified against the live tree and incorporated:

| # | Sev | Finding | Resolution in revised plan |
|---|---|---|---|
| C1 | MAJOR | Acceptance #1 ("tier/context") re-scope to context-only is not yet *authorized* (issue has no comment) | Re-scope is an explicit **precondition of plan-approved**, surfaced to user; the #3205 comment + acceptance edit happen before any `status:plan-approved` (this is the user's gate, not self-applied) |
| C2 | MAJOR | Resolver failed **open** on unknown context → a typo `hermes-batch` would pass claude through | Changed to **fail closed**: explicit unknown context = error + exit 3; bash routers `return 3` (never fall to claude). Tests updated (`..._fails_closed`, `..._aborts_on_bad_context`) |
| C3 | MAJOR | Bare `python3` violates the repo `uv run` contract; missing system `yaml` under `set -euo pipefail` breaks routing | `_resolver` bash helper prefers `uv run` else `python3`; resolver self-bootstraps pyyaml (sibling precedent); test for both invocation modes |
| C4 | MAJOR | Overnight hard-error conflicts with its own `--dry-run` fixture (#1823 = `agent:claude`+`overnight`) | Relabel synthetic #1823 → `agent:codex` (dry-run stays usable); error path covered by a dedicated unit test feeding the mapping function directly |
| C5 | MAJOR | provider_filter re-implemented forbid drop in shell → second surface, contradicts single-source | provider_filter now passes its full list through the resolver `--filter` API (the only filtering impl) |

**Overall result after r1+r2 revisions:** PASS. Both lenses independently converged on the same core risk (acceptance #1 scope + coverage completeness); no open MAJORs remain. Per `feedback_r3_inline_loop_break_pattern`, r1/r2 differing findings were folded inline — no r3 dispatch.

---

## Risks and Open Questions

- **Risk — bash↔python boundary cost:** `route_by_tier` shelling to `python3` adds per-route latency. Mitigation: only invoked when `ROUTE_CONTEXT` is set (interactive path untouched); resolver is import-light (yaml only). Routing is not a hot loop.
- **Risk — token-space mismatch (r1-F3/F4):** `execution_contexts` uses `openai-codex`; the bash routers know `codex`. Mitigation: the resolver `cli()` map is the single normalizer; ALL bash-facing modes (`--filter`/`--chain`/`--json`) emit CLI tokens; no bash-side glue. forbid=[claude] is token-consistent everywhere (verified).
- **Risk — flipping the policy doc breaks `test_cost_policy_reference_resolves`** (asserts "advisory only"). Mitigation: update that test in the same PR (in Files to Change) — caught pre-implementation.
- **Risk — emergency default regression:** existing `claude` emergency default would violate the ceiling. Mitigation: context-aware emergency default (`--chain | head -1`) + `test_tier_router_emergency_default_not_claude`.
- **Risk — faithful real-router test (r1-F5):** the tier-router tests include BOTH a stubbed-availability positive case (`== codex`, reason=filter) AND a real-`check_provider_available` variant with only `codex` on PATH, so a green suite implies the happy path actually selects a working non-claude provider — not just the emergency path. `jq` is already a router dependency.
- **Risk — coverage completeness (r1-F1/F2/F9):** the four forbid-blind surfaces are now all wired + each has a test driving the real surface. Remaining non-tier router callers audited: `scripts/dispatch/route.py` (lane-quota, different axis — out of scope). No other caller of `route_by_tier`/`filter_available_providers` found (`grep` clean beyond route.sh + orchestrate.sh).
- **Risk — fail-open on bad context (r2-C2):** an enforcement filter that silently passes through on an *explicit* unknown context is a threat-model inversion (the skip condition is more dangerous than the guarded path). Mitigation: explicit unknown context fails closed (exit 3 / `return 3`); only `context=None` passes through. **Generalizable** — promote to a review heuristic: "enforcement skip-conditions must fail closed on malformed explicit input." (Candidate for `.claude/rules/` if it recurs; noted per the promote-generalizable-findings must-fire rule.)
- **Risk — `uv run` contract + dependency fragility (r2-C3):** bare `python3` under `set -euo pipefail` breaks if system `yaml` is absent. Mitigation: `_resolver` helper prefers `uv run`, falls back to a self-bootstrapping `python3` (sibling precedent); tested both ways.
- **Deferred (not a risk to this scope):** YAML tier table (claude-everywhere) vs bash (codex-cheap) reconciliation → separate issue, operator-confirmed direction = cost-aligned codex-cheap. The `test_simple_and_standard_route_to_claude` observed-behavior test is intentionally **left untouched** here.
- **Open (flag at approval):** (a) acceptance #1 re-scope to "context routing" — needs the #3205 comment + user OK. (b) should the routers *auto-derive* `hermes_batch` from the classifier/labels rather than an explicit `--context`/label? Proposed out of scope (explicit is deterministic + testable); auto-derivation = follow-up.

---

## Complexity: T2

**T2** — multi-file harness change across two languages (bash + python), TDD with tests driving the real routers, one new shared module, config + doc + test updates. Plan-stage adversarial review = 2 providers (Claude inline + 1 dispatched).
