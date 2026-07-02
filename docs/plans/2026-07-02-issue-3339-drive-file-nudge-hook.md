# Plan for #3339: Proactive invocation — drive-file nudge via UserPromptSubmit hook (extends #801 pattern)

> **Status:** adversarial-reviewed
> **Complexity:** T2
> **Date:** 2026-07-02
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3339
> **Client:** N/A
> **Project:** (none — repo-internal harness infrastructure)
> **Lane:** lane:claude   <!-- matches the issue's lane:claude label; hook/skill authoring stays on Claude per epic #3333 provider routing -->
> **Review artifacts:** scripts/review/results/2026-07-02-plan-3339-claude.md | scripts/review/results/2026-07-02-plan-3339-codex.md | scripts/review/results/2026-07-02-plan-3339-gemini.md

---

## Resource Intelligence Summary

<!-- Issue class: Harness/Infrastructure. Consulted: issue body, epic body, the #801
     hook + its map + its tests + its settings.json wiring + its activation PR (#3330),
     sibling plan #3335 (registry/CLI this nudge composes with), propagation scripts,
     .claude/rules/, docs/standards/CONTROL_PLANE_CONTRACT.md location,
     docs/document-intelligence/README.md (intelligence entry point). -->

### Existing repo code

- Found: `.claude/hooks/ecosystem-data-nudge.sh` — THE pattern to extend (#801). Contract verified by reading the script: hook JSON on stdin (`.prompt`, `.session_id`), one context line on stdout, `exit 0` always, fail-open (no `jq` or no map → silent exit 0), once-per-**domain**-per-session via state file `${ECOSYSTEM_NUDGE_STATE_DIR:-/tmp}/claude-<sid>-ecodomains`, keyword word-boundary matching (`(^|[^a-z0-9])kw([^a-z0-9]|$)`, ERE specials escaped) against `.claude/hooks/ecosystem-domain-map.json`, exits after the FIRST domain hit (one line per prompt). `WORKSPACE_HUB` env with `BASH_SOURCE`-relative fallback resolves the repo root.
- Found: `.claude/hooks/ecosystem-domain-map.json` — 12 domains, 84 keywords total; header `_generated_from: llm-wiki/data/domain-database-index.yml` — it is a **generated** artifact (by `scripts/data-sources/gen_domain_pointers.py`), so extending its schema couples this issue to that generator.
- Found: `.claude/settings.json` lines 273–282 — the `UserPromptSubmit` wiring for #801 (excerpt in Evidence). settings.json is config-protected; wiring changes are owner-merged (PR #3330 precedent).
- Found: `tests/data_sources/test_ecosystem_data_sources_801.py` — the existing hook test harness to mirror: runs the hook via `subprocess.run(["bash", HOOK], input=json_payload, env=...)`, isolates once-per-session state by pointing `ECOSYSTEM_NUDGE_STATE_DIR` at the pytest `tmp_path`, fakes the workspace root via `WORKSPACE_HUB=tmp_path` with the map copied under `<tmp>/.claude/hooks/`, and derives unique session ids from `tmp_path.name`. Covers: fires-on-domain, silent-on-irrelevant, idempotent-per-session, word-boundary, fail-open-without-map.
- Found: `tests/hooks/test_state_size_settings_wiring.py` (#2070) — repo precedent for a settings-wiring test: loads `.claude/settings.json` as JSON and asserts the hook command string is present in the right event array.
- Found: `scripts/propagate-hooks.sh` — EXISTS but is a 6-line **deprecated** wrapper that `exec`s `scripts/propagate-ecosystem.sh --hooks-only`. `propagate-ecosystem.sh` (22 KB) currently only knows how to add the **Stop-event consume-signals hook** to sibling repos (line 166: `"already has consume-signals hook"`); it has no generic UserPromptSubmit propagation. → propagation of this nudge is a follow-on, not v1.
- Gap: no drive-file nudge exists — `.claude/hooks/` has no `drive-file-nudge.sh` and no `drive-file-map.json` (gap proof below).

### Standards

Not applicable — harness/hook infrastructure; no engineering standard governs it.

| Standard | Status | Source |
|---|---|---|
| — | not applicable | `data/document-index/standards-transfer-ledger.yaml` not relevant to hook tooling |

### LLM Wiki pages consulted

No relevant wiki pages — this is Claude-harness plumbing, not domain engineering knowledge. (The domain knowledge angle is already mediated by `ecosystem-domain-map.json`, generated from llm-wiki's `data/domain-database-index.yml`.)

### Documents consulted

- Issue #3339 body — scope: sibling of #801 firing on file-seeking intent OR domain+artifact co-occurrence; same contract; nudge names the `drive-file-search` skill + coverage fact ("1.2M ace + 0.5M dde files indexed"); settings.json wiring owner-merged; evaluate propagation; plan-stage decision on nudge-only vs auto-invocation. Acceptance: "set up a fatigue analysis like we did before" nudges exactly once per session; irrelevant prompts silent; <50 ms added; fail-open verified.
- Epic #3333 body — Layer 3 of the architecture; the skill this nudge points at is Layer 2 at `.claude/skills/data/drive-file-search/` (#3338, planned in parallel — referenced by issue number only, per lane instruction); Layer 0 registry `config/drive-index-registry.yml` comes from #3335. Coverage numbers source: epic inventory table (1,188,891 ace assets; registry `dde_project: 495487`).
- Sibling plan `docs/plans/2026-07-02-issue-3335-drive-index-query-cli.md` (read via `git show origin/feat/plans-drive-index-3334-3335:...`) — #3335 creates `config/drive-index-registry.yml` as the single source of truth for index coverage/freshness (Layer 0). CORRECTION (review F1): the registry schema carries NO row counts — each entry has only `id, adapter, path, coverage{drives,subtree}, domains, freshness{built_at,staleness_days}, builder, adapter_params` — so this nudge does NOT read coverage numbers from it in v1 (see D3 revision; schema ask filed as a follow-on).
- PR #3330 (MERGED) — "chore(#801): activate ecosystem data-source auto-suggestion hook" — the owner-merge precedent for config-protected settings.json wiring.
- `.claude/rules/` (README, patterns, goal-invocation, coding-style, …) — no rule constrains UserPromptSubmit hooks specifically; `docs/standards/CONTROL_PLANE_CONTRACT.md` exists (harness-class bundle checked); `docs/document-intelligence/README.md` exists (intelligence entry point checked; catalog-level, not hook-relevant).
- Repo rule (user memory `feedback_externalize_all_config_to_yaml.md`): all work config (keyword lists, coverage fallbacks, thresholds) lives in reviewable YAML/JSON, never hardcoded — hence the new keyword map file.

### Gaps identified

- No `.claude/hooks/drive-file-nudge.sh` — hook built from scratch (sibling of #801, different matching engine — see Decision 4: #801's per-domain loop measured 270–460 ms, over this issue's 50 ms budget, so the loop must NOT be copied).
- No `.claude/hooks/drive-file-map.json` — intent-phrase / artifact-noun keyword map built from scratch.
- No `config/drive-index-registry.yml` on this branch — and, per review F1, the registry is NOT a coverage-number source anyway (its schema carries no row counts): in v1 the coverage line comes ONLY from the dated `coverage_fallback` in `drive-file-map.json`.
- No tests for a drive-file nudge — new `tests/hooks/test_drive_file_nudge_3339.py`, mirroring the #801 harness.
- `propagate-ecosystem.sh` cannot propagate UserPromptSubmit hooks — v1 is workspace-hub only; propagation is a named follow-on.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-07-02T10:53Z via `gh issue view` / `gh pr list`):
- `#3339` — OPEN — "Proactive invocation: drive-file nudge via UserPromptSubmit hook (extends #801 pattern)" (labels: cat:harness, enhancement, lane:claude, priority:medium, status:needs-plan)
- `#3333` — OPEN — "EPIC: Context-aware drive-file search — skill + unified query layer over /mnt/ace + /mnt/dde file indexes"
- `#3338` — OPEN — "Skill: drive-file-search — context-aware related-file surfacing from work context" (planned in parallel; this plan references it by number only)
- PR `#3330` — MERGED — "chore(#801): activate ecosystem data-source auto-suggestion hook" (owner-merge precedent for settings.json wiring)
- Caveat: workspace-hub issue `#801` itself is CLOSED with title "WRK-1012: chore(plugins): install and verify official Claude Code plugins…" — the "#801" in the hook header/PR title is legacy numbering that does not match today's issue #801; the authoritative artifacts are the hook file and PR #3330.

**File existence** (`ls` 2026-07-02T10:53Z, worktree `feat/plans-drive-search-3338-3339`):
- EXISTS: `.claude/hooks/ecosystem-data-nudge.sh`, `.claude/hooks/ecosystem-domain-map.json`, `tests/data_sources/test_ecosystem_data_sources_801.py`, `scripts/propagate-hooks.sh`, `scripts/propagate-ecosystem.sh`, `docs/standards/CONTROL_PLANE_CONTRACT.md`, `docs/document-intelligence/README.md`
- MISSING (new — this plan creates): `.claude/hooks/drive-file-nudge.sh`, `.claude/hooks/drive-file-map.json`, `tests/hooks/test_drive_file_nudge_3339.py`
- MISSING (created by #3335, read-if-present here): `config/drive-index-registry.yml` → `ls: cannot access 'config/drive-index-registry.yml': No such file or directory`

**Line excerpts** — settings.json wiring for #801 (`sed -n 273,282p .claude/settings.json`, 2026-07-02T10:53Z):
```
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash \"${WORKSPACE_HUB:-$(git rev-parse --show-toplevel)}/.claude/hooks/ecosystem-data-nudge.sh\" 2>/dev/null || true",
            "timeout": 5
          }
        ]
      }
    ],
```

**Line excerpts** — #801 test harness state isolation (`tests/data_sources/test_ecosystem_data_sources_801.py` lines 51–60):
```python
def _run_hook(prompt, session_id, map_path_dir):
    env = dict(os.environ)
    env["WORKSPACE_HUB"] = map_path_dir
    # Isolate hook session-state inside this test's unique tmp dir (pytest gives a
    # fresh empty dir per run), so once-per-session state never leaks across runs.
    env["ECOSYSTEM_NUDGE_STATE_DIR"] = map_path_dir
    payload = json.dumps({"prompt": prompt, "session_id": session_id})
    p = subprocess.run(["bash", HOOK], input=payload, env=env,
                       capture_output=True, text=True, timeout=15)
    return p
```

**Line excerpts** — `scripts/propagate-hooks.sh` (entire file body, 2026-07-02T10:53Z):
```bash
# DEPRECATED: Use propagate-ecosystem.sh instead.
# This wrapper redirects to the unified propagation script.
echo "NOTE: propagate-hooks.sh is deprecated. Use propagate-ecosystem.sh instead."
exec bash "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/propagate-ecosystem.sh" --hooks-only "$@"
```

**Gap proofs** (2026-07-02T10:53Z):
- `ls .claude/hooks/ | grep drive` → no output → no drive-file hook or map exists.
- `ls docs/plans/ | grep -E "333[0-9]"` → no output → no prior plan for #3339 in this worktree (sibling plans live on other branches).
- `grep -n "consume-signals" scripts/propagate-ecosystem.sh` → line 166 `"already has consume-signals hook"` → propagation script is Stop-hook-specific, cannot propagate UserPromptSubmit hooks today.

**Reproduction proofs** (performance ground truth for Decision 4, per Step 1.5 — the issue's <50 ms acceptance is a runtime claim, so measured):

#801 hook as-is (2026-07-02T10:53:06Z, ace-linux-1, temp state dir, fresh session ids, `/usr/bin/time -f "%e s"`):
```
$ echo '{"prompt":"mooring analysis for the project","session_id":"perf-…"}' \
    | ECOSYSTEM_NUDGE_STATE_DIR=$TD bash .claude/hooks/ecosystem-data-nudge.sh
[ecosystem-data] This looks like **mooring** work (home: digitalmodel). …
0.28 s / 0.27 s / 0.27 s        # match path (3 runs)
$ … prompt "what time is it" …
0.47 s / 0.46 s / 0.46 s        # NON-match path (worst case: 12 domains × per-keyword grep spawns)
```
→ **#801's loop design is 5–9× OVER the 50 ms budget.** The new hook must not copy it.

Single-pass prototype of the proposed design (2026-07-02T10:54:39Z; 1 jq stdin-parse + 3 jq map-reads + ≤3 grep alternation passes; scratch script, not committed):
```
== intent match ==            → "[drive-file] nudge line …" emitted
== domain+artifact match ==   → emitted
== irrelevant ==              → silent, exit 0
== once per session ==        → second prompt same sid: silent
== timing x5 (worst case, non-match path) ==
0.02 s / 0.02 s / 0.02 s / 0.02 s / 0.02 s
== timing (intent-match, first fire) ==
0.02 s   (subsequent same-sid runs short-circuit on the state file: ≤0.01 s)
```
- Reproduced at: 2026-07-02T10:53:06Z (#801 baseline) and 2026-07-02T10:54:39Z (prototype)
- HONESTY CORRECTION (review F3): independent adversarial re-measurement of a faithful prototype on the same box timed **0.03–0.05 s non-match ×5 and 0.03–0.04 s first-fire ×3** — the honest measured range is **30–50 ms**, with one sample AT the 50 ms budget (`/usr/bin/time` resolution is 10 ms; the 0.02 s figures above reflect a flattering min). The design remains feasible; the headroom comes from the D4 spawn-count mitigation (ONE jq config read, or zero runtime joins via precomputed alternation strings), and all latency evidence must report median-of-5 alongside min-of-5.
- Failure mode observed matches issue claim: YES for feasibility (<50 ms is achievable — measured 30–50 ms before mitigation, headroom after), with the added finding that the *pattern being extended* currently violates the budget — this plan's design diverges from #801's inner loop deliberately.

<!-- Verification: distinct sources consulted: issue #3339, epic #3333, ecosystem-data-nudge.sh,
     ecosystem-domain-map.json, .claude/settings.json, test_ecosystem_data_sources_801.py,
     test_state_size_settings_wiring.py, propagate-hooks.sh + propagate-ecosystem.sh,
     sibling plan #3335 (origin branch), PR #3330, .claude/rules/, live latency measurements.
     Current count: 12 (≥3 required). -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-07-02-issue-3339-drive-file-nudge-hook.md |
| Hook | `.claude/hooks/drive-file-nudge.sh` |
| Keyword/config map | `.claude/hooks/drive-file-map.json` |
| Tests | `tests/hooks/test_drive_file_nudge_3339.py` |
| Settings wiring (owner-merged) | `.claude/settings.json` — `hooks.UserPromptSubmit[]` new entry |
| Plan review — Claude | scripts/review/results/2026-07-02-plan-3339-claude.md |
| Plan review — Codex | scripts/review/results/2026-07-02-plan-3339-codex.md |
| Plan review — Gemini | scripts/review/results/2026-07-02-plan-3339-gemini.md |
| Wiki updates | none (harness infrastructure) |
| Docs updates | docs/plans/README.md index row (at PR assembly — see Files to Change) |

---

## Deliverable

A `drive-file-nudge.sh` UserPromptSubmit hook (plus externalized `drive-file-map.json` keyword config and TDD suite) that, at most once per session and in <50 ms, emits one context line pointing file-seeking prompts at the `drive-file-search` skill (#3338) with the DATED drive-index coverage fact (as_of + dde staleness softener) — same fail-open contract as #801, but with a single-pass matcher that actually fits the latency budget.

---

## Design Decisions (recommended, with alternatives weighed)

**D1 — Separate sibling script, not a second emission from `ecosystem-data-nudge.sh`. → RECOMMEND separate `.claude/hooks/drive-file-nudge.sh`.**
- #801 `exit 0`s after its FIRST domain hit — a second concern inside it would restructure its control flow and complicate its once-per-*domain* state keying (this nudge needs a single once-per-*session* key, a different granularity).
- Measured: #801 is already 5–9× over this issue's 50 ms budget; bolting the new matcher into it inherits that debt, while a sibling gets a clean single-pass engine.
- Separate script = independent state key (`claude-<sid>-drivefile`), independent test env var (`DRIVE_NUDGE_STATE_DIR`), independent 5 s timeout, and zero regression risk to #801.
- Cost accepted: one more entry in the config-protected `UserPromptSubmit` array — but both wirings ride the same owner-merged PR anyway (#3330 precedent), so the marginal owner cost is one JSON block.

**D2 — Trigger logic + keyword externalization (REVISED per review F2/F5/F7). → RECOMMEND two-tier trigger with Tier 1 restricted to strong multiword phrases; new `.claude/hooks/drive-file-map.json`; domain keywords reused from `ecosystem-domain-map.json` at runtime.**
- Tier 1 (fires alone): ONLY strong, unambiguous MULTIWORD file-seeking phrases — `similar past work`, `search the drives`, `prior project files`, `like we did before`, `we did before`, `previous project`, `past project`, `have we done this before` (and similar unambiguous multiword forms). This deliberately includes #3338's canonical skill triggers `similar past work` and `search the drives` (review F5 — reconciled with the skill's `triggers:` list; the shared cross-artifact alignment pytest described in #3338's plan pins this once both artifacts land, skip-guarded until then — single shared test file is fine). (The acceptance prompt "…like we did before" matches `like we did before` / `we did before`.)
- DEMOTED to Tier 2 (review F2 — these fired on everyday coding prompts in the reviewer's faithful prototype): `do we have`, `reuse`, `precedent`, `similar work` now REQUIRE eco-domain keyword co-occurrence. The three demonstrated false positives — "do we have unit tests for this module", "reuse this helper function in the CI pipeline", "this sets a bad precedent for the API design" — are REQUIRED silent negative tests in the TDD list. `example` and `template` remain Tier-2 artifact nouns (never fire alone).
- Tier 2 (co-occurrence): engineering-domain keyword (from `ecosystem-domain-map.json`) AND (a demoted intent phrase OR an *artifact noun* — `drawing(s)`, `report(s)`, `spec(s)`, `template`, `example`, `model(s)`, `calc(s)`, `deck`, `dataset`, `document(s)`, `file(s)`). Bare artifact nouns ("write a report") do NOT fire alone — this is the false-positive guard; the issue's looser singleton keywords (`drawing`, `report`, `spec`, `example`, `template`) are deliberately demoted to Tier 2.
- KNOWN LIMITATION (review F7 — named, accepted): Tier-2 vocabulary collision class — eco-map keywords double as software vocabulary (`pipeline`, `anchor`) and artifact nouns double as artifact-of-software nouns (`template`, `model`, `deck`, `files`), so a prompt like "fix the anchor tag in the template" DOES fire Tier 2. Partial mitigation: a small `software_context_exclusions` list in the map discounts domain-keyword hits inside software compounds (`ci pipeline`, `build pipeline`, `data pipeline`, `deployment pipeline`) — required to keep the "reuse this helper function in the CI pipeline" negative test silent. Residual collisions are ACCEPTED with rationale: once-per-session bounds the cost at one line per session, and tuning is a config-only change; one known-limitation probe test documents the accepted false positive.
- Externalization: Tier-1 phrases + demoted Tier-2 phrases + artifact nouns + exclusion lists + nudge-template + coverage fallback live in a NEW `.claude/hooks/drive-file-map.json` (repo YAML/JSON-config rule). NOT an extension of `ecosystem-domain-map.json`, because that file is generated (`_generated_from: llm-wiki/...` by `gen_domain_pointers.py`) — extending its schema couples this issue to the generator and risks the generator clobbering hand-curated keys. Domain keywords are NOT duplicated: the hook reads them from `ecosystem-domain-map.json` at runtime (single jq spawn per D4, `[.domains[].keywords[]] | unique`, ERE-escaped); if that map is absent, Tier 2 silently degrades to off (fail-open, Tier 1 still works).

**D3 — Nudge line content and coverage-number source (REVISED per review F1/F6). → RECOMMEND: the dated `coverage_fallback` in `drive-file-map.json` is the ONLY v1 source; the registry-read tier is DROPPED from v1.**
- Line names the skill and the coverage fact, one line, e.g.:
  `[drive-file] This prompt suggests prior work may exist on the shared drives (~1.2M /mnt/ace + ~0.5M /mnt/dde files indexed as of 2026-07-02 — dde coverage may be stale, see #3334). Invoke the drive-file-search skill (#3338 / .claude/skills/data/drive-file-search) to surface related files before building from scratch.`
- REQUIREMENT (not example wording — review F6): the emitted coverage string MUST carry the `as_of` date from `coverage_fallback` AND a staleness softener for dde ("dde coverage may be stale — see #3334"), because dde rows in the master index sit under stale aliases, dde coverage is frozen (that is #3334's purpose), and `/mnt/dde` is not even mounted on this box today.
- Registry-read DROPPED (review F1): an earlier draft claimed #3335's `config/drive-index-registry.yml` is "a YAML registry of every index with row counts" — VERIFIED FALSE. The schema gives each entry only `id, adapter, path, coverage{drives,subtree}, domains, freshness{built_at,staleness_days}, builder, adapter_params`; there are no counts and no summary block, so a "tolerant grep/sed extraction of two summary counts" would silently fall back forever (dead code with a permanently-green fixture test). The 1,188,891 ace / 495,487 dde numbers actually come from `data/document-index/registry.yaml` + the live `index.db` — different artifacts, themselves flagged divergent in #3335's evidence, hence the `~` and the date.
- Numbers live in `coverage_fallback` in `drive-file-map.json` (`{"ace": "~1.2M", "dde": "~0.5M", "as_of": "2026-07-02"}` — externalized, dated, one-line update when stale). Hardcoding in the script is rejected (stale-risk + config rule).
- Follow-on (filed as a schema ask on #3335/#3336): add an OPTIONAL per-index `row_count`/`as_of` field to the registry schema; the registry-read tier becomes a follow-on change once that field actually exists — not before.

**D4 — Performance budget (REVISED per review F3). → RECOMMEND single-pass matcher: 1 jq stdin-parse, ONE jq config read (or zero), ≤3 grep alternation passes, one state-file stat.**
- Measured (evidence above): #801's per-domain jq + per-keyword grep loop costs 270–460 ms — the pattern's *contract* is extended, its *inner loop* is not (this claim independently VERIFIED by review).
- Honest prototype range (review F3): a faithful prototype of the earlier "3 jq config reads" design measures **30–50 ms** worst case on this box (one sample AT the 50 ms budget), not the ~20 ms first logged — the margin was overstated. Mitigation that buys the headroom: fold the 3 config jq reads into ONE `jq` invocation spanning both JSON files (emit all alternation strings in a single spawn), or better, precompute the joined, ERE-escaped alternation strings INTO `drive-file-map.json` at authoring time so the hook does zero runtime joins. Cutting 2+ process spawns puts the non-match path clearly under budget.
- Keyword lists become alternation EREs (`(^|[^a-z0-9])(kw1|kw2|…)([^a-z0-9]|$)`) so match cost is O(≤3 grep spawns), independent of keyword count. ERE specials escaped at join time.
- Latency evidence REQUIREMENT (review F3): all measurements — acceptance run and `test_latency_budget` — report **median-of-5 alongside min-of-5** (`/usr/bin/time` resolution is 10 ms; min-of-5 alone reports the flattering tail).
- The once-per-session check runs BEFORE any map parsing (a single `[[ -f $STATE ]]`), so every prompt after the first fire pays only stdin-parse cost.

**D5 — Propagation scope. → RECOMMEND workspace-hub only in v1; propagation is a named follow-on.**
- `scripts/propagate-hooks.sh` exists but is a deprecated wrapper around `propagate-ecosystem.sh --hooks-only`, whose hook-add logic is hardcoded to the Stop-event consume-signals hook (evidence above) — it cannot wire a UserPromptSubmit hook into sibling repos today. Extending it is real (jq-insert into each sibling's settings.json + hook file copy) but is its own reviewable change touching N config-protected files. v1 lands + proves the nudge here; a follow-on issue (filed at PR time, referenced from #3333) extends propagation.

**D6 — Nudge-only vs skill auto-invocation (issue scope item 5). → RECOMMEND nudge-only in v1.**
- Auto-invocation from a UserPromptSubmit hook would inject imperative instructions on every match — higher blast radius, no conversion data. Ship nudge-only, measure nudge→invocation conversion under #3340 (usage playbook + metrics child of the epic), escalate only with evidence.

**D7 — Coexistence with #801 (`ecosystem-data-nudge.sh`) on the same prompt (ADDED per review F4). → DECIDE: dual emission is ACCEPTED, with a DATA-ask carve-out.**
- Both hooks CAN fire on one prompt (verified live: "pull together the mooring analysis report" fires #801's mooring nudge AND this hook's Tier 2). This dual emission is ACCEPTED by design: two one-line nudges, each once-per-session, at complementary levels — #801 answers at the DATA/domain-catalog level, this hook at the FILE level. Asserted, not just tolerated: `test_dual_emission_with_801_accepted` runs the mooring-report prompt through both hooks and asserts each emits its line.
- EXCEPTION (the carve-out): prompts shaped as DATA-level asks — matching a regex like `do we have data|data for|data on` (case-insensitive) — are EXCLUDED from BOTH Tier 1 and Tier 2 firing and route to #801's DATA-level nudge only. Without this, the demoted `do we have` + a domain keyword would nudge a pure DATA ask ("do we have data for metocean") toward the FILE-level skill — exactly the FILE-vs-DATA discrimination #3338 pins with its disjointness/alignment tests. `test_data_ask_routes_to_801_only` asserts this hook stays silent on the metocean-data prompt while #801's concern still fires.

---

## Pseudocode

```
# .claude/hooks/drive-file-nudge.sh  (UserPromptSubmit; sibling of ecosystem-data-nudge.sh)
set -uo pipefail                      # NEVER set -e; every exit path is exit 0
WS   = ${WORKSPACE_HUB:-<BASH_SOURCE>/../..}          # same resolution as #801
MAP  = $WS/.claude/hooks/drive-file-map.json
ECO  = $WS/.claude/hooks/ecosystem-domain-map.json     # optional (Tier 2 only)
# NOTE: config/drive-index-registry.yml is NOT read — registry carries no counts (D3/F1)

fail-open guards: no jq → exit 0 ; no MAP → exit 0
INPUT = cat stdin (|| true)
one jq pass: SID = .session_id // "nosession" ; PROMPT_LC = (.prompt // "") | ascii_downcase
empty prompt or jq parse failure → exit 0

STATE = ${DRIVE_NUDGE_STATE_DIR:-/tmp}/claude-$SID-drivefile
[[ -f STATE ]] → exit 0                                # once per session, checked FIRST

# ONE jq spawn for ALL config (D4/F3) — a single invocation spanning MAP (+ ECO via
# --slurpfile when present) emits every needed string on separate lines:
#   TIER1_RE, TIER2_RE, ARTIFACT_RE, DATA_ASK_RE, SW_EXCL_RE, DOMAIN_RE, ace, dde, as_of
# (alternatively: the joined, ERE-escaped alternation strings are precomputed and stored
#  in MAP at authoring time, so the hook does zero runtime joins — preferred)
# DOMAIN_RE = "" if ECO missing (Tier 2 degrades to off)

B='(^|[^a-z0-9])' ; E='([^a-z0-9]|$)'
grep -qiE "do we have data|data for|data on" PROMPT_LC → exit 0   # DATA-ask carve-out (D7):
                                                                  # route to #801 only
fire = grep -qiE B(TIER1_RE)E on PROMPT_LC                        # Tier 1: strong multiword only
    OR ( DOMAIN_RE != ""                                          # Tier 2: domain co-occurrence
         AND grep -qiE B(DOMAIN_RE)E                              #   (software compounds like
             on PROMPT_LC with SW_EXCL matches discounted        #    "ci pipeline" discounted — D2)
         AND ( grep -qiE B(TIER2_RE)E OR grep -qiE B(ARTIFACT_RE)E ) )
not fire → exit 0

# coverage fact: dated map fallback ONLY (v1 — D3/F1); as_of + staleness softener REQUIRED
echo "[drive-file] This prompt suggests prior work may exist on the shared drives"
     " (${ace} /mnt/ace + ${dde} /mnt/dde files indexed as of ${as_of}"
     " — dde coverage may be stale, see #3334)."
     " Invoke the drive-file-search skill (#3338) to surface related files"
     " before building from scratch."
touch STATE (|| true)
exit 0
```

```
# .claude/hooks/drive-file-map.json  (hand-curated; NOT generated — unlike ecosystem-domain-map.json)
{
  "_note": "config for drive-file-nudge.sh (#3339); domain keywords come from ecosystem-domain-map.json at runtime",
  "tier1_intent_phrases": ["similar past work","search the drives","prior project files","like we did before",
                           "we did before","previous project","past project","have we done this before"],
  "tier2_intent_phrases": ["do we have","reuse","precedent","similar work"],
  "artifact_nouns": ["drawing","drawings","report","reports","spec","specs","template","example",
                     "model","models","calc","calcs","deck","dataset","document","documents","file","files"],
  "data_ask_exclusions": ["do we have data","data for","data on"],
  "software_context_exclusions": ["ci pipeline","build pipeline","data pipeline","deployment pipeline"],
  "coverage_fallback": {"ace": "~1.2M", "dde": "~0.5M", "as_of": "2026-07-02"},
  "skill_ref": "drive-file-search (#3338)"
}
```

```
# settings.json wiring (owner-merged; exact block, appended to hooks.UserPromptSubmit[]):
{ "hooks": [ { "type": "command",
    "command": "bash \"${WORKSPACE_HUB:-$(git rev-parse --show-toplevel)}/.claude/hooks/drive-file-nudge.sh\" 2>/dev/null || true",
    "timeout": 5 } ] }
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `.claude/hooks/drive-file-nudge.sh` | the hook (single-pass matcher, fail-open, once-per-session) |
| Create | `.claude/hooks/drive-file-map.json` | externalized intent/artifact keywords + coverage fallback + skill ref |
| Create | `tests/hooks/test_drive_file_nudge_3339.py` | TDD suite, mirrors `test_ecosystem_data_sources_801.py` harness (subprocess + `WORKSPACE_HUB`/`DRIVE_NUDGE_STATE_DIR` tmp isolation) |
| Modify | `.claude/settings.json` | append UserPromptSubmit entry — **config-protected; owner merges** (PR #3330 precedent); exact JSON block above |
| Update | `docs/plans/README.md` | add this plan to the index — deferred to PR assembly (not edited in this authoring pass, per worktree instruction) |

Not changed: `.claude/hooks/ecosystem-data-nudge.sh` (D1 — untouched; its own >50 ms latency is noted as a follow-on optimization candidate, out of scope here); `scripts/propagate-ecosystem.sh` (D5 — follow-on issue).

---

## TDD Test List

Harness: mirror `tests/data_sources/test_ecosystem_data_sources_801.py` — `_run_hook(prompt, sid, ws)` runs `subprocess.run(["bash", HOOK], input=json, env={WORKSPACE_HUB: ws, DRIVE_NUDGE_STATE_DIR: ws})`; `ws` fixture = `tmp_path` with `.claude/hooks/{drive-file-nudge.sh, drive-file-map.json, ecosystem-domain-map.json(fixture)}` copied in; session ids derived from `tmp_path.name`.

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_fires_on_intent_phrase | Tier 1; the issue's acceptance prompt | "set up a fatigue analysis like we did before" | rc 0; stdout contains `[drive-file]` and `drive-file-search` |
| test_fires_on_domain_plus_artifact | Tier 2 co-occurrence | "pull together the mooring analysis report" (fixture eco-map has `mooring`) | rc 0; nudge emitted |
| test_silent_on_domain_only | Tier 2 needs BOTH halves | "run a mooring analysis" (no artifact noun, no intent) | rc 0; stdout empty |
| test_silent_on_artifact_only | bare artifact noun never fires alone | "write a report on the meeting" | rc 0; stdout empty |
| test_silent_on_irrelevant_prompt | issue acceptance (negative) | "what time is it" / "refactor this python function" | rc 0; stdout empty |
| test_silent_on_demoted_intent_phrases | REQUIRED negatives (review F2): the three demonstrated false positives stay silent under the revised tiers | "do we have unit tests for this module" (no domain kw); "this sets a bad precedent for the API design" (no domain kw); "reuse this helper function in the CI pipeline" (`pipeline` discounted by `software_context_exclusions`) | rc 0; stdout empty for all three |
| test_data_ask_routes_to_801_only | D7 carve-out: DATA-shaped asks never fire this hook | "do we have data for metocean" (would otherwise be Tier 2: demoted `do we have` + `metocean`) | rc 0; stdout empty — #801's DATA-level nudge owns this prompt |
| test_dual_emission_with_801_accepted | D7: dual emission is the accepted, asserted design | "pull together the mooring analysis report" run through BOTH `drive-file-nudge.sh` and `ecosystem-data-nudge.sh` (each with tmp state) | each hook emits exactly one line (`[drive-file]` and `[ecosystem-data]`) — complementary FILE vs DATA levels |
| test_known_limitation_collision_probe | documents the ACCEPTED Tier-2 collision class (review F7): eco-map keywords (`anchor`) × artifact nouns (`template`); rationale: once-per-session bounds the cost at one line, tuning is config-only | "fix the anchor tag in the template" | rc 0; nudge EMITTED — asserted as a known, accepted false positive |
| test_once_per_session | second match same sid suppressed | fire, then "search the drives for mooring examples" same sid | 1st: nudge; 2nd: empty; state file exists in tmp dir |
| test_new_session_fires_again | state keyed on sid | same prompt, different sid | nudge emitted |
| test_word_boundary_no_false_fire | `(^|[^a-z0-9])…` boundary | "the reporting pipeline is precedented" (substrings only) | rc 0; stdout empty |
| test_failopen_without_map | no `drive-file-map.json` | intent prompt | rc 0; stdout empty |
| test_failopen_without_eco_map | Tier 2 degrades, Tier 1 survives | eco-map absent: domain+artifact prompt → empty; intent prompt → nudge | rc 0 both |
| test_failopen_without_jq | no-jq guard | run with `PATH=<stub-dir>` where the stub dir's EXPLICIT contents are symlinks to `bash`, `cat`, `grep`, `sed`, `touch`, `mkdir` — everything the hook spawns EXCEPT `jq`. NOTE (review F8): `grep` and `sed` are NOT coreutils — they must be linked into the stub explicitly, or the test proves less than intended (it would exercise missing-grep, not missing-jq) | rc 0; stdout empty |
| test_malformed_stdin | garbage / empty / non-JSON stdin | `"not json"`, `""`, `"{"` | rc 0; stdout empty; no state file |
| test_coverage_fallback_dated | coverage line comes ONLY from the dated map fallback (review F1 — replaces the dropped `test_coverage_from_registry`, which tested a registry feature that does not exist) | Tier-1 prompt; map fixture with known `coverage_fallback` | nudge contains `~1.2M`, `~0.5M`, the `as_of` date (`2026-07-02`), and the dde staleness softener referencing #3334 |
| test_latency_budget | <50 ms acceptance | intent prompt, fresh sid ×5, wall-time | min-of-5 AND median-of-5 subprocess wall time < 0.05 s (review F3; budget overridable via `DRIVE_NUDGE_LATENCY_BUDGET_MS` for slow CI; re-measured prototype range 30–50 ms — the D4 single-spawn mitigation provides the headroom) |
| test_settings_wiring | wiring present after owner merge | parse `.claude/settings.json`, find `drive-file-nudge.sh` in `hooks.UserPromptSubmit` (pattern: `tests/hooks/test_state_size_settings_wiring.py`) | passes on the PR branch that carries the wiring; `pytest.mark.skipif` when wiring absent so pre-merge suites stay green |
| test_hook_skill_trigger_alignment | cross-artifact reconciliation (review F5 — the SAME shared test #3338's plan F2 describes; single shared test file is fine, skip-guarded until both this map and `.claude/skills/data/drive-file-search/SKILL.md` land) | #3338's SKILL.md `triggers:` + `drive-file-map.json` | every canonical skill trigger fires this hook's Tier-1 matcher; DATA-level phrasings route to neither |

---

## Acceptance Criteria

- [ ] All new tests pass: `python3 -m pytest tests/hooks/test_drive_file_nudge_3339.py -v` (repo pytest convention per #801 test header; `uv run pytest` equivalent)
- [ ] No regression: `python3 -m pytest tests/data_sources/test_ecosystem_data_sources_801.py tests/hooks/ -v` passes (proves #801 untouched)
- [ ] Issue acceptance 1: `echo '{"prompt":"set up a fatigue analysis like we did before","session_id":"acc1"}' | bash .claude/hooks/drive-file-nudge.sh` emits exactly one `[drive-file]` line naming `drive-file-search` + the dated coverage fact (numbers + `as_of` + dde staleness softener — D3 requirement); re-running with the same sid emits nothing
- [ ] Issue acceptance 2: irrelevant prompts ("what time is it") emit nothing, exit 0 — INCLUDING the review-pinned negatives: "do we have unit tests for this module", "reuse this helper function in the CI pipeline", "this sets a bad precedent for the API design" (F2), and the DATA-ask "do we have data for metocean" (D7 carve-out)
- [ ] Issue acceptance 3: measured added latency < 50 ms — min-of-5 AND median-of-5 reported (`/usr/bin/time`; review F3), match and non-match paths
- [ ] Issue acceptance 4: fail-open verified — missing map, missing jq, malformed stdin all exit 0 silently
- [ ] Keyword lists + coverage fallback live in `.claude/hooks/drive-file-map.json`, not in the script (config-externalization rule)
- [ ] settings.json wiring block delivered in the PR for owner merge (agent does not self-merge; #3330 precedent); wiring test skip-guarded until merged
- [ ] Review artifacts posted to `scripts/review/results/2026-07-02-plan-3339-{claude,codex,gemini}.md`

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | **MAJOR** | Registry-read coverage tier was built against a fabricated #3335 schema feature — the registry carries NO row counts (F1); Tier-1 bare intent phrases (`do we have`, `reuse`, `precedent`) empirically fire on everyday coding prompts (F2); prototype latency honestly 30–50 ms, not ~20 ms (F3); double-nudge with #801 undesigned, incl. DATA-ask misrouting (F4); hook misses #3338's own canonical triggers (F5); dde coverage overstated without date/softener (F6); Tier-2 software-vocabulary collision class unnamed (F7); no-jq stub must still provide grep/sed (F8). #801 baseline + infra claims verified (F9). Full artifact: scripts/review/results/2026-07-02-plan-3339-claude.md |
| Codex | PENDING — dispatch deferred (codex runtime CPU-constrained on this host; see epic #3333 routing note) | — |
| Gemini | PENDING — dispatch deferred (codex runtime CPU-constrained on this host; see epic #3333 routing note) | — |

**Overall result:** PASS after revisions (Claude r1)

Revisions made based on review:
- **F1 (MAJOR)** → registry-read coverage tier DROPPED from v1 (D3 rewritten; Resource Intelligence + Gaps corrected; pseudocode REG read removed): the coverage line comes ONLY from the dated `coverage_fallback` in `drive-file-map.json`; `test_coverage_from_registry` (and the now-redundant `test_coverage_fallback_without_registry`) replaced by `test_coverage_fallback_dated`; Risks/Open now files a schema ask on #3335/#3336 for an optional per-index `row_count`/`as_of` registry field, with registry-read as a follow-on once it exists; the false "registry with row counts" claim removed (schema = id/adapter/path/coverage/domains/freshness/builder/adapter_params only).
- **F2 (MAJOR)** → trigger tiers reworked (D2, map JSON, pseudocode): Tier 1 restricted to strong multiword phrases (`similar past work`, `search the drives`, `prior project files`, `like we did before`, `we did before`, `previous project`, `past project`, `have we done this before`); `do we have`, `reuse`, `precedent`, `similar work` demoted to Tier 2 (domain co-occurrence required; `example`/`template` stay Tier-2 artifact nouns); the three demonstrated false-positive prompts added as REQUIRED silent tests (`test_silent_on_demoted_intent_phrases`).
- **F3 (MEDIUM)** → D4 + Reproduction proofs restated honestly (30–50 ms measured range, one sample AT budget); mitigation: fold the 3 config jq reads into ONE jq call or precompute joined alternation strings in the map at authoring time; all latency evidence (acceptance + `test_latency_budget`) now reports median-of-5 alongside min-of-5.
- **F4 (MEDIUM)** → new D7: dual emission with #801 on the same prompt is ACCEPTED (two one-line nudges, each once-per-session, complementary DATA vs FILE levels) EXCEPT DATA-shaped asks (`do we have data|data for|data on`) which are excluded from Tier 1/Tier 2 and routed to #801 only; tests added: `test_dual_emission_with_801_accepted` (mooring-report prompt fires both, asserted) + `test_data_ask_routes_to_801_only` (metocean-data prompt: this hook silent).
- **F5 (LOW)** → intent phrases reconciled with #3338's canonical skill triggers (`similar past work`, `search the drives` are Tier-1); skip-guarded cross-artifact alignment pytest added (`test_hook_skill_trigger_alignment` — the same shared test #3338's plan describes, single shared test file).
- **F6 (LOW)** → coverage string REQUIREMENT (D3, acceptance 1, `test_coverage_fallback_dated`): carries the `as_of` date + dde staleness softener ("dde coverage may be stale — see #3334").
- **F7 (LOW)** → Tier-2 vocabulary collision class named as a KNOWN LIMITATION in D2 (eco-map `pipeline`/`anchor` × artifact nouns `template`/`model`/`deck`/`files`), with `software_context_exclusions` as partial mitigation and `test_known_limitation_collision_probe` documenting the accepted false positive ("fix the anchor tag in the template" fires; once-per-session bounds the cost).
- **F8 (NIT)** → `test_failopen_without_jq` now states the stub dir's explicit contents (symlinks to bash, cat, grep, sed, touch, mkdir — everything except jq; grep/sed are not coreutils so must be linked explicitly).

---

## Risks and Open Questions

- **Open — schema ask to #3335/#3336 (filed at PR time; replaces the dropped registry-read tier per review F1):** request an OPTIONAL per-index `row_count`/`as_of` field in the `config/drive-index-registry.yml` schema (today's schema carries only `id, adapter, path, coverage{drives,subtree}, domains, freshness{built_at,staleness_days}, builder, adapter_params` — no counts). The registry-read coverage tier becomes a follow-on change once that field exists; until then the dated map `coverage_fallback` is the only source, and staleness is managed by the `as_of` date + softener in the emitted line.
- **Risk — #3338 skill name/path drift:** the nudge names `drive-file-search` / `.claude/skills/data/drive-file-search/` per epic #3333 Layer 2. Trigger vocabularies are now RECONCILED via adversarial review r1 (Tier 1 carries the skill's canonical triggers `similar past work` / `search the drives`; the shared skip-guarded `test_hook_skill_trigger_alignment` pins hook↔skill alignment once both land — review F5). If the skill slug changes, the fix is a one-string edit in `drive-file-map.json` (`skill_ref` is externalized for exactly this reason).
- **Risk — wiring is owner-gated:** until the owner merges the settings.json entry, the hook is inert in live sessions. Tests exercise the hook directly (subprocess), so CI validity does not depend on the wiring; the wiring test is skip-guarded.
- **Risk — nudge fatigue / false positives:** Tier-1 restriction to strong multiword phrases + demotion of `do we have`/`reuse`/`precedent`/`similar work` to Tier 2 (review F2) + single global once-per-session key (stricter than #801's per-domain key) bound the worst case at one line per session. The Tier-2 vocabulary collision class (D2 known limitation, review F7) is accepted with a documenting probe test; keyword/exclusion tuning is a config-only change.
- **Risk — combined UserPromptSubmit latency:** #801 already adds 270–460 ms per prompt (measured); this hook adds ~20 ms more. Total is dominated by #801 — flagged as a follow-on optimization (port #801 to the single-pass matcher), explicitly out of scope here to keep this change zero-risk to #801.
- **Risk — latency test flake on loaded CI:** wall-clock assertion at 50 ms can flake under load. Mitigation: min-of-5 sampling + `DRIVE_NUDGE_LATENCY_BUDGET_MS` env override; acceptance measurement is the manual `/usr/bin/time` run.
- **Open — propagation follow-on:** extend `propagate-ecosystem.sh` to UserPromptSubmit hooks and roll to sibling repos? Recommend filing at PR time as an epic #3333 child (D5); needs owner appetite since it touches N config-protected settings files.
- **Open — nudge→invocation conversion measurement:** metric collection lands with #3340 (usage playbook); v1 emits no telemetry. Flag for user during approval if telemetry-in-v1 is preferred.
- **Note — "#801" numbering caveat:** workspace-hub issue #801 is an unrelated closed plugins chore; "#801 pattern" refers to the hook file + PR #3330. Plan cites file paths, not the stale number, for anything load-bearing.

---

## Complexity: T2

**T2** — one new hook script + one new config map + a 20-test TDD suite mirroring an existing harness, one config-protected file touched via owner merge; no new subsystem, but real design decisions (trigger tiers, latency engine, #801 coexistence, coverage-fact sourcing) and a measured performance constraint rule out T1.
