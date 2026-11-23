# Plan for #3340: Drive-file-search usage playbook — planning Resource-Intel integration, metrics, long-term unified-index decision

> **Status:** adversarial-reviewed
> **Complexity:** T2
> **Date:** 2026-07-02
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3340
> **Client:** N/A
> **Project:** (none — repo-internal workflow/metrics infrastructure)
> **Lane:** lane:claude   <!-- matches the issue's lane:claude label; playbook/workflow authoring + light metrics code per epic #3333 provider routing -->
> **Review artifacts:** scripts/review/results/2026-07-02-plan-3340-claude.md | scripts/review/results/2026-07-02-plan-3340-codex.md | scripts/review/results/2026-07-02-plan-3340-gemini.md

---

## Resource Intelligence Summary

<!-- Issue class: Documentation / Harness-Infrastructure union (playbook doc + workflow-template
     edits + light instrumentation). Consulted: issue body, epic body, ALL FOUR sibling plans on
     main, the planning-workflow artifacts this issue modifies (template RETRIEVAL CONTRACT,
     issue-planning-mode SKILL.md, docs/plans/README.md), de-id governance precedent
     (ecosystem-data-sources SKILL.md), .gitignore, live env probes. -->

### Existing repo code
- Found: `docs/plans/_template-issue-plan.md` — the RETRIEVAL CONTRACT comment block (lines 22–42) defines issue-class source bundles ("ALL issues: prior plans, existing code, recent related issues, intelligence entry points"). This is the exact insertion point for the mandated drive-index query: one line added to the ALL-issues bundle. The template lives under `docs/plans/` — protection in this repo lives in PreToolUse **hook scripts**, not settings.json literals (review r1 correction), and hook-level analysis shows `plan-approval-gate.sh` includes `docs/plans/` in its safe paths — so the template edit is a **normal PR change, not owner-merge-gated** (unlike settings.json wiring, PR #3330 precedent).
- Found: `.claude/skills/coordination/issue-planning-mode/SKILL.md` — Step 1 item 3 ("Search existing code, standards, documents, and prior plans before writing") and Step 2 are where the drive-index query becomes a named, mandatory Resource-Intel source. Protection status (hook-level, review r1 correction): `skill-content-pretooluse.sh` DOES match `.claude/skills/*.md` but intercepts **Read** only and is advisory (content-threat scan, exit 0); `plan-approval-gate.sh` safe-paths `.claude/` — so the SKILL.md edit is a normal PR change (sibling #3338 creates skill files without owner-merge).
- Found: `docs/plans/README.md` Step 2 "Universal minimum (ALL issues)" list — the third surface documenting the retrieval contract; must receive the same bundle line at implementation time (plus this plan's index row). NOT edited in this authoring pass (worktree instruction).
- Found: `.claude/skills/data/ecosystem-data-sources/SKILL.md` "Governance (never violate)" — the in-repo de-identification precedent the playbook codifies for drive paths: ACE_SHARE holds client data, "never reproduce raw content or client names in any repo; surface as metadata only", bounded reads only, de-id stays `lane:claude`.
- Found: `.gitignore` — many local-data JSONL patterns exist (e.g., line 471 `data/document-index/index.jsonl`, line 457 `.planning/cost-events.jsonl`) but **no** `data/drive-index-search/` entries — the metrics-log gitignore lines are new.
- Gap: no playbook, no metrics emission, no aggregate script, no nudge-conversion join exists anywhere (gap proofs below).

### Standards
Not applicable — documentation/workflow/metrics issue; no engineering standard governs it.

| Standard | Status | Source |
|---|---|---|
| — | not applicable | `data/document-index/standards-transfer-ledger.yaml` not relevant to workflow tooling |

### LLM Wiki pages consulted
No relevant wiki pages — harness/workflow infrastructure, not domain engineering knowledge. (The data-flywheel integration point the playbook documents *points at* llm-wiki's `data/data-source-catalog.yml` + `domain-database-index.yml` via the ecosystem-data-sources skill; it does not modify them.)

### Documents consulted
- Issue #3340 body — scope: (1) integration points (issue-planning-mode Resource Intel step, pre-calculation search, data-flywheel feed), (2) usage playbook (trust, freshness, de-id), (3) effectiveness metrics (JSONL log from the CLI, ~30-day review: hit-rate, integration-point mix, nudge conversion), (4) long-term unified-DB recommendation. Acceptance: playbook committed; Resource Intel step references the skill; metrics logging live; 30-day review issue scheduled.
- Epic #3333 body — this is the capstone child ("usage review", last in the suggested order); the long-term candidate is "single cross-drive incremental index (SQLite/DuckDB, content-hash dedup) replacing the heterogeneous layer". This plan defines the decision criteria; it does NOT build the unified DB.
- Sibling plan `docs/plans/2026-07-02-issue-3335-drive-index-query-cli.md` (ON MAIN, adversarial-reviewed) — the CLI this issue instruments: `search.py` orchestrator `main()` with `--json` envelope `{query, generated_at, indexes_queried[], coverage_gaps[], results[{canonical_path, score, rank_basis, ...}]}`, exit codes 0/2, package layout `scripts/data/drive-index-search/{search.py, registry.py, pathnorm.py, merge.py, adapters/}`, test tree `tests/data/drive_index_search/` with fixture registry. Its Risks section explicitly forwards the shards-registry question to "#3336/#3340". The emission point this plan adds is a new `metrics.py` module in that package, called once from `main()` before return.
- Sibling plan `docs/plans/2026-07-02-issue-3338-drive-file-search-skill.md` (ON MAIN, adversarial-reviewed) — the skill's Step 4 next-action 2 ("record chosen paths as a 'Documents consulted' entry in the active plan's Resource Intelligence section — the #3340 playbook formalizes this loop") and its Risks ("#3340's playbook should add the leak-grep check to the Resource-Intel recording loop"; "fetched 20/shown 10 are initial guesses; #3340's metrics should tune them") are direct asks this plan answers. The skill's ONE CLI command is where `--caller skill` gets added.
- Sibling plan `docs/plans/2026-07-02-issue-3339-drive-file-nudge-hook.md` (ON MAIN, adversarial-reviewed) — D6: "Ship nudge-only, measure nudge→invocation conversion under #3340"; its Open list: "metric collection lands with #3340 … v1 emits no telemetry". Nudge state file is `${DRIVE_NUDGE_STATE_DIR:-/tmp}/claude-<sid>-drivefile`, keyed on the hook-stdin `session_id` — the join-key design below builds on this.
- Sibling plan `docs/plans/2026-07-02-issue-3334-dde-drive-index.md` (ON MAIN, adversarial-reviewed) — dde index/freshness context for the playbook's freshness-caveat section (dde JSONL coverage frozen 2026-04-17; deprecation decision; `/mnt/dde` not mounted on ace-linux-1 today).
- User-memory precedent — "public repo ≠ safe to publish — every issue has exclude-list + leak-grep guard" (ecosystem Pages epic): workspace-hub plans/issues are PUBLIC; the playbook's de-id rules + the leak-grep check operationalize this for drive paths.

### Gaps identified
- No usage playbook exists — `docs/guides/drive-file-search-playbook.md` built from scratch (docs/guides/ exists and is the natural home; evidence below). Note (review r1): `docs/guides/` is NOT in `plan-approval-gate.sh`'s safe-path list — the playbook file is created under the approved-plan marker, like any implementation file (normal post-approval flow, no extra gate).
- No drive-index line in the RETRIEVAL CONTRACT bundles (template), issue-planning-mode SKILL.md, or docs/plans/README.md Step 2 — three coordinated one-block edits, from scratch.
- No metrics emission anywhere: `scripts/data/drive-index-search/metrics.py`, the `--session`/`--caller` CLI flags, and the `main()` emission call do not exist (the whole #3335 package is itself not yet implemented — dependency, see Risks).
- No aggregate script: `scripts/data/drive-index-search/aggregate_metrics.py` built from scratch.
- No nudge firing log: #3339's hook only `touch`es an ephemeral `/tmp` state file — conversion measurement needs one appended JSONL line (small coordinated addition to #3339's hook; its plan explicitly deferred telemetry here).
- No `.gitignore` entries for `data/drive-index-search/metrics/*.jsonl`.
- No 30-day review mechanism — no `gh issue create` precedent in `scripts/cron/` (proof below), so the simple convention (follow-up issue created at implementation time, review-after date in title) is defined here.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-07-02T14:42Z via `gh issue view --repo vamseeachanta/workspace-hub`):
- `#3340` — OPEN — "Drive-file-search usage playbook: planning Resource-Intel integration, metrics, long-term unified-index decision" (labels: cat:data, enhancement, lane:claude, priority:medium, status:needs-plan)
- `#3333` — OPEN — "EPIC: Context-aware drive-file search — skill + unified query layer over /mnt/ace + /mnt/dde file indexes"
- `#3334`/`#3335`/`#3338`/`#3339` — OPEN (states as recorded in their merged plans' evidence blocks, 2026-07-02; re-verify at implementation start per repo rule)

**File existence** (`ls`, 2026-07-02T14:47Z, worktree `feat/plans-drive-index-3336-3337-3340`):
- EXISTS: `docs/plans/2026-07-02-issue-333{4,5,8,9}-*.md` (all four sibling plans, on main via PRs #3345/#3348 per `git log`)
- EXISTS: `docs/guides/` (review-transport.md, SECURITY.md, SPECIFY_INITIALIZATION_GUIDE.md, test-skill-learning.md), `docs/plans/_template-issue-plan.md`, `.claude/skills/coordination/issue-planning-mode/SKILL.md`, `.claude/skills/data/ecosystem-data-sources/SKILL.md`, `scripts/review/plan-review-fanout.sh`
- MISSING (new — this plan creates): `docs/guides/drive-file-search-playbook.md`, `data/drive-index-search/` (whole tree), `scripts/data/drive-index-search/metrics.py`, `scripts/data/drive-index-search/aggregate_metrics.py`
- MISSING (dependency — created by siblings, modified here): `scripts/data/drive-index-search/search.py` (#3335), `.claude/hooks/drive-file-nudge.sh` (#3339), `.claude/skills/data/drive-file-search/SKILL.md` (#3338)

**Line excerpts** — the template insertion point (`sed -n '31,34p' docs/plans/_template-issue-plan.md`, 2026-07-02T14:40Z):
```
     Issue-class bundles — consult at minimum:
     - ALL issues: prior plans (docs/plans/), existing code in affected paths, recent related issues,
       intelligence entry points (docs/document-intelligence/README.md or data-intelligence-map.md)
     - Engineering: + standards-transfer-ledger.yaml, code-registry.yaml, relevant domain wiki, online-resource-registry.yaml
```

**Session join-key probe** (load-bearing for the metrics design; `env | grep -iE "claude_|session"`, 2026-07-02T14:47Z, live Claude Code Bash tool on ace-linux-1):
```
CLAUDE_CODE_SESSION_ID=d6f7970c-5b34-4865-817f-017ab6ce8d21
CLAUDE_CODE_CHILD_SESSION=1
```
→ Claude Code DOES export the session id to Bash-tool subprocesses as `CLAUDE_CODE_SESSION_ID` — the CLI can default its `--session` value from this env var. (#3339's hook receives `session_id` on stdin JSON; equality of the two values is expected but pinned by an implementation-time probe — see Risks.)

**Gap proofs** (2026-07-02T14:44–14:47Z):
- `ls data/drive-index-search docs/guides/drive-file-search-playbook.md` → "No such file or directory" (both) → metrics tree and playbook do not exist.
- `grep -nE "^data|\.jsonl|metrics" .gitignore` → hits for `data/document-index/*.jsonl.backup-*`, `.planning/cost-events.jsonl`, etc.; **nothing** for `data/drive-index-search/` → gitignore lines are new.
- Protection-surface analysis (review r1 — HOOKS, not settings.json literals, are this repo's protection mechanism; the earlier settings.json grep was the wrong probe): `skill-content-pretooluse.sh` matches `.claude/skills/*.md` but intercepts **Read only** and is advisory (content-threat scan, exit 0); `plan-approval-gate.sh` safe paths include `docs/plans/` and `.claude/` → template + SKILL.md edits are normal PR changes. `docs/guides/` is NOT safe-pathed → playbook creation requires the plan-approval marker (normal post-approval implementation flow). settings.json itself remains the only owner-merge surface in this epic, and this issue does not touch it.
- `grep -rln "gh issue create" scripts/cron/` → no output → no cron-created-issue convention exists; 30-day review uses the simple follow-up-issue convention defined below.

**Reproduction proofs**: N/A — documentation/metrics-design issue; no runtime failure alleged. The load-bearing runtime claim (session-id availability in the CLI's environment) is proven live above.

<!-- Source count: issue #3340, epic #3333, sibling plans #3334/#3335/#3338/#3339, template
     RETRIEVAL CONTRACT, issue-planning-mode SKILL.md, docs/plans/README.md, ecosystem-data-sources
     SKILL.md governance, .gitignore, .claude/settings.json probe, scripts/cron probe, live env
     probe = 13 distinct sources ≥ 3 required. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-07-02-issue-3340-drive-search-usage-playbook.md |
| Playbook (main deliverable) | docs/guides/drive-file-search-playbook.md |
| Metrics emission module | scripts/data/drive-index-search/metrics.py (inside #3335's package) |
| Aggregate script | scripts/data/drive-index-search/aggregate_metrics.py |
| Local metrics logs (gitignored) | data/drive-index-search/metrics/invocations.jsonl, data/drive-index-search/metrics/nudges.jsonl |
| Committed weekly aggregates | data/drive-index-search/metrics/weekly/&lt;ISO-week&gt;-&lt;hostname&gt;.json (per-host — review r1 F3) |
| Tests | tests/data/drive_index_search/test_metrics_3340.py, tests/docs/test_drive_search_playbook_3340.py |
| Workflow-integration edits | docs/plans/_template-issue-plan.md, .claude/skills/coordination/issue-planning-mode/SKILL.md, docs/plans/README.md (Step 2 + index row) |
| Sibling-artifact edits (coordinated) | scripts/data/drive-index-search/search.py (#3335), .claude/hooks/drive-file-nudge.sh (#3339), .claude/skills/data/drive-file-search/SKILL.md (#3338) |
| 30-day review issue | created via `gh issue create` at implementation close (template text in playbook appendix) |
| Plan review — Claude / Codex / Gemini | scripts/review/results/2026-07-02-plan-3340-{claude,codex,gemini}.md |
| Wiki updates | none |

---

## Deliverable

A committed usage playbook (`docs/guides/drive-file-search-playbook.md`) plus three coordinated workflow-surface edits making the drive-index query a mandated Resource-Intel source, a fail-open JSONL invocation-metrics pipeline (CLI emission + nudge-firing log + weekly aggregate script) with a session-id join for nudge→invocation conversion, and a written decision framework + scheduled 30-day review issue that will decide the unified cross-drive DB investment on evidence instead of appetite.

---

## Design Decisions (recommended, with alternatives weighed)

**D1 — Instrument INSIDE the #3335 CLI, not a wrapper. → RECOMMEND a `metrics.py` module in `scripts/data/drive-index-search/`, called once from `search.py main()` just before return.**
- A wrapper script would be bypassed by every consumer that calls `search.py` directly — which is exactly how #3338's skill and the playbook instruct invocation. One in-process emission point captures ALL callers.
- Emission is fail-open: wrapped in `try/except Exception: pass`, disabled by `DRIVE_SEARCH_NO_METRICS=1`; a metrics bug must never break a search (mirrors the hook fail-open discipline of #801/#3339).
- Sequencing: #3335 is `lane:codex` and not yet implemented. If #3335 lands first, this issue adds `metrics.py` + two flags + one call site as a small follow-on PR; if this issue's PR is ready first, the emission piece waits (playbook/template/aggregate pieces are independent). Filed as a comment on #3335 at implementation start so the codex lane knows the call site is coming.

**D2 — What gets logged (privacy weighed). → RECOMMEND hashed query, never raw.**
- Queries frequently embed client/project identifiers (the whole de-id posture of this epic). The local log is gitignored, but "gitignored + raw client strings" is one `git add -f` from a public leak. Log `query_hash` = first 12 hex of sha256(query) + `n_tokens`; raw text never touches disk by default. Debug escape hatch: `DRIVE_SEARCH_LOG_RAW_QUERY=1` opt-in for a local tuning session (documented in the playbook with a warning).
- Fields per line: `ts` (iso8601 UTC), `session` (see D3), `caller` (see D4), `query_hash`, `n_tokens`, `n_results`, `top_score` (null when empty), `json_flag` (bool — proxy for programmatic/skill consumption), `indexes_queried` (count), `coverage_gaps` (count), `n_stale_indexes` (count of `index_status[].stale == true` from #3336's envelope key; **0 when the key is absent** — forward-compatible before #3336 lands; review r1 F2), `exit_code`, `duration_ms`. Counts only — no paths, no scores-per-result, no index ids beyond counts — so even an accidental commit of the local log leaks nothing client-identifying.
- Committed weekly aggregates carry only counts/rates/medians (never hashes, never session ids) — safe for the public repo by construction.

**D3 — Nudge→invocation join key: session id, CLI-side sourced `--session` flag > `CLAUDE_CODE_SESSION_ID` env > `"unknown"`. → RECOMMEND env-default with flag override.**
- Verified live (Evidence): Claude Code exports `CLAUDE_CODE_SESSION_ID` to Bash subprocesses, and #3339's hook receives `session_id` on stdin — both sides of the join exist without any propagation machinery. The `--session` flag exists for non-Claude runtimes (Codex/Gemini set no such env var; #3338's skill text tells those runtimes to pass `--session <id>` if one is known, else omit → `"unknown"`, which simply drops out of conversion joins without corrupting them).
- Nudge side: #3339's `/tmp` state files are ephemeral (reboots, tmp cleaners) and carry no timestamp beyond mtime — unusable as the durable record. RECOMMENDED coordinated one-line addition to `drive-file-nudge.sh` (after its `touch STATE`): append `{"ts":...,"session":"<sid>"}` to `data/drive-index-search/metrics/nudges.jsonl` (`>> ... 2>/dev/null || true` — fail-open, adds one redirect to a measured 30–50 ms budget). The emission block `mkdir -p`s the metrics dir first (review r1 F5) — the dir's existence must not hang solely on the `weekly/.gitkeep` parent; and `aggregate_metrics.py` reports "nudges.jsonl absent" distinctly from "0 nudges", so a silently-discarded denominator is visible at review time. #3339's plan explicitly deferred conversion telemetry to this issue; the addition rides whichever of the two implementation PRs lands second, with a coordination comment on #3339.
- Conversion metric: `sessions(nudges.jsonl) ∩ sessions(invocations.jsonl) / sessions(nudges.jsonl)` per aggregation window. Scanning `/tmp` state files instead was REJECTED (ephemeral, no history); logging conversion from the hook was REJECTED (the hook cannot see later CLI calls).

**D4 — Integration-point attribution: a `--caller` enum flag on the CLI. → RECOMMEND `--caller {skill|plan-resource-intel|pre-calc|manual}`, default `manual`.**
- The issue's 30-day question "which integration point fires most" needs attribution at emission time. Each documented integration point passes its own value: #3338's SKILL.md command gains `--caller skill`; the template/SKILL.md Resource-Intel line specifies `--caller plan-resource-intel`; the playbook's pre-calculation section specifies `--caller pre-calc`. Unknown values are accepted and logged verbatim (forward-compatible), documented values enumerated in the playbook.
- "Whether results were used" (issue scope 3) cannot be instrumented mechanically at the CLI. Proxy pair: (a) `json_flag` + `caller` distinguish programmatic consumption from casual queries; (b) the aggregate script counts plans under `docs/plans/` whose Resource-Intel sections cite `/mnt/ace` or `/mnt/dde` paths that week ("used-in-plan" count) — cheap, grep-based, and directly tied to the loop the playbook formalizes.

**D5 — Log residency: LOCAL gitignored JSONL + committed weekly aggregate. → RECOMMEND exactly that split.**
- Raw invocation lines are per-machine, high-churn, and carry session ids + query hashes → gitignored (`data/drive-index-search/metrics/*.jsonl`). Weekly aggregates are small, counts-only, reviewable → committed to `data/drive-index-search/metrics/weekly/<ISO-week>-<hostname>.json` — per-HOST files (review r1 F3), because multiple machines run searches and a single global `<week>.json` would clobber/conflict across machines and let one machine's traffic masquerade as the ecosystem's; the 30-day review step MERGES the per-host files (aggregate-of-aggregates). This way the review reads history from the repo, not from one machine's /tmp-adjacent state. Alternatives rejected: fully-committed raw log (privacy + merge churn); fully-local everything (30-day review would depend on a single machine surviving 30 days).
- Aggregation is manual-or-cron: `uv run python scripts/data/drive-index-search/aggregate_metrics.py --week <ISO-week>` is idempotent; wiring it into `scripts/cron/` is OPTIONAL and deferred to the 30-day review (no new cron surface before value is proven).

**D6 — 30-day review mechanism. → RECOMMEND a follow-up issue created at implementation close, review-after date in the title.**
- Verified: no `gh issue create` cron precedent exists — inventing scheduled-issue automation for one reminder is over-build. At implementation close: `gh issue create --title "Drive-file-search 30-day usage review (review after YYYY-MM-DD) — apply #3340 decision framework" --label cat:data,lane:claude` with body = the decision framework section of the playbook + pointers to `metrics/weekly/`. The epic (#3333) gets a comment linking it.

**D7 — Long-term unified-index decision framework (defined NOW, applied at the review — the unified DB is NOT built in this issue).**
Criteria over the ~30-day window (initial thresholds; the review may tune them but must justify changes):
- **Volume:** median ≥ 10 invocations/week (excluding `caller=manual` test noise) → real demand exists.
- **Hit-rate:** fraction of invocations with `n_results ≥ 1` AND `top_score ≥ HIT_SCORE_MIN` (named constant in `aggregate_metrics.py`, initially 0.3 — the constant is the only place the literal lives; the #3335 merge score is normalized to [0,1]). Healthy ≥ 60%; < 40% = relevance/index-quality problem.
- **Staleness pressure (review r1 F2 — derived from #3336's `index_status`, NOT from coverage_gaps):** fraction of invocations with `n_stale_indexes ≥ 1` (stale-index-rate), plus staleness complaints recorded in the playbook's feedback section / issue comments. > 25% stale-index-rate = freshness pain.
- **Coverage pain (SEPARATE signal — unreachable ≠ stale):** fraction of invocations with `coverage_gaps ≥ 1`. Per #3335's contract, `coverage_gaps` records unreachable/missing indexes (unmounted drive, nonexistent path) — it feeds mount/coverage decisions, not the freshness criterion; an unmounted `/mnt/dde` on a laptop is coverage pain with zero staleness signal.
- **Latency:** median `duration_ms` > 5000 warm = adapter-layer performance ceiling reached.
- **Nudge conversion:** informs the nudge/skill tuning (and #3339's D6 auto-invocation question), not the DB decision directly.
Decision matrix: BUILD the unified cross-drive DB (epic long-term architecture) iff volume passes AND ≥ 1 of {hit-rate < 40%, stale-index-rate > 25%, latency breach} — i.e., demand is real and the adapter layer is the bottleneck (high coverage-pain rate argues for mounts/coverage work, not necessarily the DB). STAY on the adapter layer if volume passes and all three are healthy. DEPRIORITIZE (defer the DB, keep adapters) if volume < 2/week regardless of quality — no investment case either way.

---

## Pseudocode

### `scripts/data/drive-index-search/metrics.py` (the metrics logging — emission point)

```
LOG_PATH = <repo_root>/data/drive-index-search/metrics/invocations.jsonl

function emit_invocation(args, envelope_or_none, exit_code, t_start):
    if env DRIVE_SEARCH_NO_METRICS == "1": return
    try:
        session = args.session or env CLAUDE_CODE_SESSION_ID or "unknown"
        q = args.query
        line = {
            ts: utcnow iso8601,
            session: session,
            caller: args.caller,                     # skill | plan-resource-intel | pre-calc | manual
            query_hash: sha256(q).hexdigest()[:12],  # raw query ONLY if DRIVE_SEARCH_LOG_RAW_QUERY=1
            n_tokens: len(tokens(q)),
            n_results: len(envelope.results) if envelope else 0,
            top_score: envelope.results[0].score if results else null,
            json_flag: args.json,
            indexes_queried: len(envelope.indexes_queried) if envelope else 0,
            coverage_gaps: len(envelope.coverage_gaps) if envelope else 0,
            n_stale_indexes: count(s for s in envelope.get("index_status", []) if s.stale),
                # #3336's envelope key; 0 when absent — forward-compatible (review r1 F2)
            exit_code: exit_code,
            duration_ms: int((now - t_start) * 1000),
        }
        makedirs(dirname(LOG_PATH)); append json.dumps(line) + "\n" to LOG_PATH   # O_APPEND single write
    except Exception:
        pass                                          # fail-open: metrics never break a search

# call site (one line each in #3335's search.py main(), both return paths):
#   emit_invocation(args, envelope, rc, t_start)
# new argparse flags in search.py:
#   --session <id>   (default: None → env fallback in emit)
#   --caller <str>   (default: "manual")
```

### `.claude/hooks/drive-file-nudge.sh` addition (coordinated with #3339 — one appended block after `touch STATE`)

```
mkdir -p "$WS/data/drive-index-search/metrics" 2>/dev/null || true   # pin dir existence (review r1 F5):
  # never depend solely on the weekly/.gitkeep parent surviving sparse checkouts / gitignore churn
printf '{"ts":"%s","session":"%s"}\n' "$(date -u +%FT%TZ)" "$SID" \
  >> "$WS/data/drive-index-search/metrics/nudges.jsonl" 2>/dev/null || true
```

### `scripts/data/drive-index-search/aggregate_metrics.py`

```
HIT_SCORE_MIN = 0.3   # named constant — the ONLY place this literal lives (review r1 F7);
                      # playbook prose and D7 cite the constant, never the number

function main(--week ISO-week = current, --metrics-dir override for tests):
    inv    = parse invocations.jsonl lines whose ts falls in week (skip malformed lines, count them)
    nudges = parse nudges.jsonl lines in week (same tolerance)
    nudges_log_absent = not exists(nudges.jsonl)   # review r1 F5: report "nudges.jsonl absent"
                                                   # DISTINCTLY from "0 nudges" — silent loss visible
    agg = {
        week, generated_at, host: hostname(),
        invocations: len(inv),
        by_caller: counter(inv.caller),
        hit_rate: frac(inv where n_results>=1 and top_score>=HIT_SCORE_MIN),
        empty_rate: frac(inv where n_results==0),
        gap_rate: frac(inv where coverage_gaps>=1),          # coverage pain (unreachability)
        stale_rate: frac(inv where n_stale_indexes>=1),      # staleness pressure (r1 F2 — separate)
        median_duration_ms, json_flag_rate,
        distinct_sessions: len(set(inv.session) - {"unknown"}),
        nudges_log_absent: bool,
        nudge_firings: len(nudges),
        nudge_conversion: |sessions(nudges) ∩ sessions(inv)| / |sessions(nudges)|
                          (null if 0 nudges OR nudges_log_absent),
        plans_citing_drive_paths: count files in docs/plans/ modified this week (git log --since/--until)
                                  containing /mnt/ace or /mnt/dde,               # "used-in-plan" proxy
        malformed_lines: count,
    }
    write data/drive-index-search/metrics/weekly/<week>-<hostname>.json (idempotent overwrite, sorted keys)
        # per-host filename (review r1 F3): avoids cross-machine clobber/merge conflicts;
        # the 30-day review MERGES per-host files (aggregate-of-aggregates)
    print human one-screen summary
    # NOTE: aggregates contain ONLY counts/rates — no hashes, sessions, paths, or queries
```

### Playbook outline (`docs/guides/drive-file-search-playbook.md` — prose, ~150 lines)

```
1. When to invoke — the three integration points (+ --caller value each):
   a. issue-planning Resource Intel (MANDATORY per the updated RETRIEVAL CONTRACT): run the
      drive-file-search skill (#3338) or the CLI directly with --caller plan-resource-intel;
      cite hits in "Documents consulted" using CANONICAL /mnt/<drive> paths only
   b. pre-calculation: before implementing any digitalmodel/worldenergydata calc, search for
      prior spreadsheets/reports (--caller pre-calc) — feeds the "small calcs into domain
      modules" practice
   c. data-flywheel: hits that reveal a latent dataset get routed to the data-source catalog /
      "Establish the <domain> database" issues via the ecosystem-data-sources skill
2. How to read results: score is [0,1] merged rank (bm25 + token match — not a probability);
   ALWAYS read coverage_gaps (what was NOT searched — unreachability, not staleness) AND the
   freshness AUTHORITY: #3336's dynamic CLI stderr staleness warnings + `index_status` in
   --json (review r1 F2); the hardcoded dates (master index frozen 2026-04-17; dde coverage
   stale until #3334; .ace-knowledge built 2026-03-26) are fallback-only when `index_status`
   is absent; canonical paths only — a transport-alias path (slash-mnt-remote form) in
   output is a bug, report it   # worded so the playbook itself carries zero literal
                                # /mnt/remote/ occurrences (review r1 F4)
3. De-identification rules for PUBLIC artifacts (plans/issues/PRs/commits in workspace-hub):
   drive paths embed client names/project codes; before quoting a path → leak-grep it
   (grep -iE '<client-token-list>' — same posture as ecosystem-data-sources governance +
   the exclude-list/leak-grep precedent); if identifying → metadata-only form ("a past
   <domain> deliverable on /mnt/ace, path recorded locally") or redact the segment;
   showing paths in-session to the local user is fine — PERSISTING them publicly is gated;
   de-id judgment stays lane:claude
4. What NOT to do: no ad-hoc drive crawls (find/grep over /mnt/ace|/mnt/dde) when the index
   can answer — bounded reads of specific surfaced files only; never mount/sudo; never
   commit raw metrics logs; never log raw queries without the documented opt-in
5. Metrics: what is logged (field table), where (local gitignored JSONL), weekly aggregate
   command, DRIVE_SEARCH_NO_METRICS opt-out
6. 30-day review + unified-index decision framework (D7 criteria + matrix; the hit-score
   threshold is cited as the `HIT_SCORE_MIN` constant in aggregate_metrics.py — no
   hardcoded score literal in playbook prose, review r1 F7)
7. Appendix: 30-day review issue template text
```

### Workflow-surface edits (exact insertion, template shown; SKILL.md + README get the equivalent line)

```
docs/plans/_template-issue-plan.md, RETRIEVAL CONTRACT block, ALL-issues bundle gains:
     - ALL issues: ... intelligence entry points (...),
+      drive-file index (run the drive-file-search skill or
+      `scripts/data/drive-index-search/search.py "<terms>" --json --caller plan-resource-intel`;
+      cite hits under "Documents consulted" with canonical /mnt/<drive> paths, de-id per
+      docs/guides/drive-file-search-playbook.md; state "no relevant drive files" if empty)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | docs/guides/drive-file-search-playbook.md | the playbook (main deliverable; outline above) — created under the plan-approval marker; docs/guides/ is not plan-gate safe-pathed (review r1) |
| Create | scripts/data/drive-index-search/metrics.py | fail-open invocation-log emission (D1/D2) — lands inside #3335's package |
| Modify | scripts/data/drive-index-search/search.py | add `--session`/`--caller` flags + one `emit_invocation()` call site (DEPENDS #3335; coordination comment filed on #3335) |
| Create | scripts/data/drive-index-search/aggregate_metrics.py | weekly aggregate + nudge-conversion join + used-in-plan proxy (D4/D5) |
| Modify | .claude/hooks/drive-file-nudge.sh | append one fail-open nudge-firing JSONL line (DEPENDS #3339; its plan defers telemetry here; rides whichever PR lands second) |
| Modify | .claude/skills/data/drive-file-search/SKILL.md | add `--caller skill` to the skill's ONE CLI command; link the playbook from guardrails (DEPENDS #3338) |
| Modify | docs/plans/_template-issue-plan.md | RETRIEVAL CONTRACT ALL-issues bundle gains the drive-index line (normal PR — docs/plans/ is a plan-gate safe path per hook-level analysis, review r1) |
| Modify | .claude/skills/coordination/issue-planning-mode/SKILL.md | Step 1/Step 2 Resource Intel names the drive-index query as a mandated universal source (normal PR — `.claude/` is plan-gate safe-pathed; skill-content hook is Read-only/advisory) |
| Modify | docs/plans/README.md | Step 2 "Universal minimum" gains the same line + this plan's index row (at PR time — NOT edited in this authoring pass) |
| Modify | .gitignore | add `data/drive-index-search/metrics/*.jsonl` (weekly/ stays tracked) |
| Create | data/drive-index-search/metrics/weekly/.gitkeep | anchor the committed aggregate dir |
| Create | tests/data/drive_index_search/test_metrics_3340.py | metrics emission + aggregate TDD (below) |
| Create | tests/docs/test_drive_search_playbook_3340.py | playbook lint (links resolve, canonical paths only, required sections) |

Not changed: `.claude/settings.json` (nothing here needs owner-merged wiring); no unified DB, no index builders, no cron entries (deferred per D5/D6).

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_emit_writes_schema_line | emission schema | fake args (query="mooring fatigue", caller="skill", json=True) + fixture envelope, tmp LOG_PATH | 1 JSONL line with exactly the D2 keys; `query_hash` = 12 hex; `n_tokens`=2; `top_score` float |
| test_emit_hashes_never_raw_query | privacy default | query containing "clientCo-proj42" | raw string ABSENT from log file bytes; hash present |
| test_emit_raw_query_optin | debug escape hatch | same + env DRIVE_SEARCH_LOG_RAW_QUERY=1 | raw query present (documented opt-in) |
| test_emit_session_precedence | D3 join key | (a) --session X + env Y → X; (b) env only → env value; (c) neither → "unknown" | per-case `session` field |
| test_emit_disabled_by_env | opt-out | DRIVE_SEARCH_NO_METRICS=1 | no file created |
| test_emit_fail_open | metrics never break search | LOG_PATH dir unwritable (chmod 0) | no exception raised; search result unaffected |
| test_emit_empty_results | null handling | envelope with 0 results | `n_results`=0, `top_score`=null |
| test_cli_fixture_run_emits_line (skipif until #3335 `search.py` exists) | end-to-end emission point | subprocess `search.py "riser" --registry <#3335 fixture registry> --json --caller pre-calc --session t1` with metrics dir → tmp | exit 0; stdout envelope unchanged vs no-metrics run; exactly 1 new JSONL line, caller="pre-calc", session="t1" |
| test_aggregate_counts_and_rates | aggregate math | fixture invocations.jsonl: 10 lines, 6 with n_results≥1∧top_score≥0.3, 3 with gaps, callers mixed | weekly JSON: invocations=10, hit_rate=0.6, gap_rate=0.3, by_caller matches |
| test_aggregate_nudge_conversion | the join | nudges.jsonl sessions {a,b,c}; invocations sessions {b,c,d} | nudge_conversion = 2/3; "unknown" sessions excluded from the join |
| test_aggregate_zero_nudges | division guard | empty nudges.jsonl | nudge_conversion = null, no crash |
| test_aggregate_skips_malformed | robustness | 1 garbage line in each file | counted in malformed_lines; rest aggregated |
| test_aggregate_no_privacy_leak | D5 committed-artifact safety | fixture logs with hashes+sessions | weekly JSON contains NO `query_hash`, NO session id values, NO /mnt/ paths |
| test_aggregate_idempotent | re-run safety | run twice same week | byte-identical output file |
| test_playbook_links_resolve | playbook lint | every relative link / repo path cited in the playbook | all `ls`-resolvable in repo (skill/CLI paths skipif-gated until siblings land) |
| test_playbook_canonical_paths_only | canonical-path rule eats its own cooking | playbook body (its own negative example is worded descriptively — "a transport-alias path (slash-mnt-remote form)" — so the zero-literal-match assertion holds; review r1 F4) | zero `/mnt/remote/` occurrences; every drive example starts `/mnt/ace` or `/mnt/dde` |
| test_playbook_required_sections | structure | playbook body | headings for: integration points, reading results/freshness, de-identification, what NOT to do, metrics, decision framework |
| test_template_and_skill_carry_drive_intel_line | workflow integration landed | `_template-issue-plan.md` + issue-planning-mode `SKILL.md` + `docs/plans/README.md` | each contains `drive-index-search` (or the skill name) in its Resource-Intel/RETRIEVAL-CONTRACT text |
| test_gitignore_covers_metrics_jsonl | residency split | `git check-ignore data/drive-index-search/metrics/invocations.jsonl` and `.../weekly/2026-W30-hostx.json` (per-host name — r1 F3) | first ignored; second NOT ignored |

---

## Acceptance Criteria

- [ ] All new tests pass: `uv run pytest tests/data/drive_index_search/test_metrics_3340.py tests/docs/test_drive_search_playbook_3340.py -v` (#3335-dependent tests SKIP cleanly while the CLI is absent, PASS once it lands)
- [ ] No regression: `uv run pytest tests/` passes (or matches pre-change failure baseline recorded at branch time)
- [ ] Playbook committed at `docs/guides/drive-file-search-playbook.md` with all six sections + the 30-day issue template appendix
- [ ] Resource Intel step references the skill/CLI in ALL THREE workflow surfaces (template RETRIEVAL CONTRACT, issue-planning-mode SKILL.md, docs/plans/README.md Step 2) — issue acceptance "Resource Intel step references the skill"
- [ ] Metrics logging live (once #3335 is merged): a live fixture-registry run appends exactly one schema-valid line to `data/drive-index-search/metrics/invocations.jsonl`; `git status` shows the log untracked/ignored
- [ ] Weekly aggregate: `uv run python scripts/data/drive-index-search/aggregate_metrics.py --week <current>` writes `metrics/weekly/<week>-<hostname>.json` (per-host, review r1 F3) containing counts/rates only (privacy check passes); "nudges.jsonl absent" reported distinctly from "0 nudges"
- [ ] Nudge-conversion join demonstrated on fixtures (test_aggregate_nudge_conversion) and the one-line hook addition delivered on whichever of this/#3339's implementation PRs lands second
- [ ] 30-day review issue created at implementation close with review-after date in title, decision framework in body, linked from epic #3333 — issue acceptance "30-day review issue scheduled"
- [ ] Explicitly NOT delivered (scope guard): no unified cross-drive DB, no cron wiring, no settings.json change
- [ ] Docs: plan indexed in docs/plans/README.md at PR time
- [ ] Review artifacts posted to scripts/review/results/ (3 providers)

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | **MINOR** | Sibling contracts + session-join evidence verified genuine; 3 MEDIUM defects (protection claim rested on the wrong probe — hooks, not settings.json; staleness conflated with coverage_gaps while ignoring #3336's `index_status`; weekly-aggregate filename clobbers across machines) + 4 smaller nits — all addressed in r1 revisions below |
| Codex | PENDING — dispatch deferred (codex runtime CPU-constrained on this host; see epic #3333 routing note) | — |
| Gemini | PENDING — dispatch deferred (codex runtime CPU-constrained on this host; see epic #3333 routing note) | — |

**Overall result:** PASS after revisions (Claude r1)

Revisions made based on review:
- **F1** — settings.json-grep "unprotected" evidence replaced with hook-level analysis: `skill-content-pretooluse.sh` intercepts Read only (advisory); `plan-approval-gate.sh` safe paths include `docs/plans/` and `.claude/`; `docs/guides/` is NOT safe-pathed → playbook creation happens under the plan-approval marker; "verified unprotected" phrasing softened throughout (Resource Intel, Gaps, Evidence, Files to Change).
- **F2** — staleness/coverage separated: D2 field list + metrics.py gain `n_stale_indexes` derived from #3336's `index_status` (0 when key absent); D7 staleness pressure redefined on stale-index-rate with coverage_gaps-rate kept as a SEPARATE "coverage pain" signal (unreachable ≠ stale); playbook §2 cites #3336's dynamic CLI warnings/`index_status` as the freshness authority, hardcoded dates fallback-only (D2, D7, Pseudocode, Playbook outline, aggregate schema).
- **F3** — committed weekly aggregate renamed to per-host `weekly/<ISO-week>-<hostname>.json` to avoid cross-machine clobber; the 30-day review merges per-host files (aggregate-of-aggregates) (Artifact Map, D5, Pseudocode, Acceptance, TDD).
- **F4** — playbook's negative-example line reworded to "a transport-alias path (slash-mnt-remote form) in output is a bug" so `test_playbook_canonical_paths_only`'s zero-literal-match assertion holds against the playbook's own body (Playbook outline §2, TDD).
- **F5** — nudge-log dir existence pinned: the hook emission `mkdir -p`s the metrics dir (never relies solely on `weekly/.gitkeep` parent); `aggregate_metrics.py` reports "nudges.jsonl absent" distinctly from "0 nudges" via `nudges_log_absent` (D3, Pseudocode, Acceptance).
- **F6** — `plans_citing_drive_paths` proxy gains the undercount-via-redaction caveat beside the existing citations-≠-usefulness one (Risks/Open).
- **F7** — 0.3 hit threshold lives ONLY as the `HIT_SCORE_MIN` named constant in `aggregate_metrics.py`; D7 and the playbook prose cite the constant, not the literal (D7, Pseudocode, Playbook outline §6).

---

## Risks and Open Questions

- **Risk — three sibling dependencies, none implemented:** #3335 (CLI — emission call site), #3339 (hook — nudge log line), #3338 (skill — `--caller skill` edit) all exist only as adversarial-reviewed plans on main. Mitigation: every dependent piece is skipif-gated or rides-second-PR; the playbook, workflow-surface edits, aggregate script, gitignore, and decision framework are dependency-free and land regardless. Implementation step 1: `gh issue view 3335 3338 3339` + re-read merged contracts (check-issue-state-before-implementing rule).
- **Risk — hook-stdin `session_id` ≠ `CLAUDE_CODE_SESSION_ID` env value would break the conversion join.** Both are believed to be the same session UUID (env value verified live; hook contract per #3339 evidence). Pinned at implementation with a one-off probe (hook logs its sid, same session runs `echo $CLAUDE_CODE_SESSION_ID`, compare). If they diverge, the join degrades to null — the aggregate reports it, nothing silently lies. Also note `CLAUDE_CODE_CHILD_SESSION=1` exists: subagent/child sessions may carry their own ids, which slightly undercounts conversion (nudge in parent, invocation in child) — accepted for v1, documented in the playbook.
- **Risk — template/SKILL.md edits raise every future plan's floor:** adding a mandatory retrieval source costs every planner one CLI/skill run. Bounded: the line permits "state 'no relevant drive files' if empty", the CLI degrades gracefully when drives are unmounted (exit 0 + coverage_gaps per #3335), and on machines without the indexes the correct citation is the gap itself. Reviewers should challenge whether the line should be ALL-issues or class-scoped (engineering/data only) — plan recommends ALL-issues because the epic's premise is precedent-blindness across all work; flag for user during approval.
- **Risk — metrics gaming / noise:** `caller` is self-reported and `manual` test queries pollute volume. Mitigated: D7 volume criterion excludes `caller=manual`; the aggregate is transparent about by_caller mix; thresholds are review-time tunable with justification.
- **Risk — 0.3 top_score hit threshold is a guess** layered on #3335's own guessed ranking constants (0.25/0.25 bonuses). Accepted: it is a measurement threshold, not behavior; stored only in `aggregate_metrics.py` as a named constant; the 30-day review re-derives it from the observed score distribution if needed.
- **Risk — de-id rules remain judgment, not mechanics:** the playbook's leak-grep is a checklist step, not an enforced hook. A pre-commit leak-grep over `docs/plans/*.md` for a client-token list is a candidate follow-on — deliberately NOT in scope (client-token list itself is sensitive config; needs its own design). Flag for user.
- **Open — where does the client-token list for leak-grep live?** The playbook v1 says "grep for known client/project tokens" generically; a maintained private list would make it mechanical but cannot live in this public repo. Options: private sibling repo config, or local-only `~/.config` list. Flag for user during approval.
- **Open — should the 30-day review also decide the nudge auto-invocation escalation (#3339 D6)?** Recommend YES (same metrics window, one review issue covers both) — the review-issue template includes the nudge-conversion question alongside the DB decision.
- **Open — `plans_citing_drive_paths` proxy counts citations, not usefulness — and UNDERCOUNTS via redaction (review r1 F6).** The playbook's own de-id rules instruct redacting identifying paths to metadata-only form; a fully-redacted citation (no `/mnt/` string at all) escapes the grep, so the proxy undercounts exactly when the de-id discipline is followed best. Both caveats accepted as v1; the review can spot-check the cited plans qualitatively.

---

## Complexity: T2

**T2** — one substantial playbook doc + one small emission module + one aggregate script + a ~19-test TDD suite + three coordinated one-block edits to existing workflow surfaces and three small sibling-artifact touch-points; no new subsystem, no owner-gated config, but real cross-issue sequencing and privacy/measurement design decisions rule out T1.
