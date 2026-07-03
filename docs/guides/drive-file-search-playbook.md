# Drive-File-Search Usage Playbook (#3340, epic #3333)

How and when to use the drive-file index layer — the `drive-file-search` skill
(`.claude/skills/data/drive-file-search/SKILL.md`, #3338) and the CLI it wraps
(`scripts/data/drive-index-search/search.py`, #3335) — plus the de-identification
rules for a PUBLIC repo, the metrics that measure whether any of this is worth
keeping, and the decision framework for the long-term unified cross-drive index.

Related surfaces: registry `config/drive-index-registry.yml` (#3334 builders),
prompt nudge `.claude/hooks/drive-file-nudge.sh` (#3339), catalog-level sibling
skill `.claude/skills/data/ecosystem-data-sources/SKILL.md`.

## 1. Integration points — when to invoke

Three documented integration points. Each passes its own `--caller` value so the
30-day review can see which point actually fires (unknown values are accepted
and logged verbatim; the enum below is the documented set).

| Integration point | When | `--caller` |
|---|---|---|
| Issue-planning Resource Intel | MANDATORY for every plan, per the RETRIEVAL CONTRACT ALL-issues bundle in `docs/plans/_template-issue-plan.md` and Step 2 of `docs/plans/README.md`. Run the drive-file-search skill or the CLI; cite hits under "Documents consulted" using canonical `/mnt/<drive>` paths (de-identified, section 3); state "no relevant drive files" if empty. | `plan-resource-intel` |
| Pre-calculation search | Before implementing any digitalmodel / worldenergydata calculation, search for prior spreadsheets, calc notebooks, and reports — feeds the "small calcs into domain modules" practice instead of rebuilding from scratch. | `pre-calc` |
| Data-flywheel feed | A hit that reveals a latent DATASET (not just a file) gets routed onward: record it via the `ecosystem-data-sources` skill into the data-source catalog / "Establish the domain database" issue family. | (whichever caller surfaced it) |
| Ad-hoc human/agent query | Anything else. | `manual` (default) |

Canonical invocation (read-only):

```
uv run python scripts/data/drive-index-search/search.py "<terms>" --json --limit 20 --caller <point>
```

(`python3` works when uv is broken; add `--session <id>` on non-Claude runtimes —
Claude Code sessions inherit the id from the environment automatically.)

## 2. Reading results — scores, coverage, freshness

- `score` is a merged [0,1] rank (bm25/token-match blend + filename/all-tokens
  bonuses) — a relative ordering, NOT a probability of relevance.
- ALWAYS read `coverage_gaps`: it lists what was NOT searched (unreachable or
  missing indexes — an unmounted drive is coverage pain, not staleness). Quote
  each gap `reason` verbatim when presenting results.
- Freshness AUTHORITY: the CLI's dynamic staleness warnings on stderr and the
  `index_status` array in the `--json` envelope (#3336) are authoritative when
  present. The hardcoded dates below are FALLBACK-ONLY, for when `index_status`
  is absent:
  - master file index frozen 2026-04-17;
  - dde JSONL coverage stale until the #3334 rebuild lands;
  - `.ace-knowledge` catalog built 2026-03-26.
- Canonical paths only: every result path must start with a canonical drive root
  (`/mnt/ace` or `/mnt/dde`). A transport-alias path (slash-mnt-remote form) in
  output is a bug — report it against #3335 rather than quoting it anywhere.
- Exit code `2` = registry error or zero reachable indexes: name the down
  drives, point at `scripts/setup/canonical-drive-links.sh`, fall back to
  `ecosystem-data-sources`.

## 3. De-identification rules for PUBLIC artifacts

workspace-hub plans, issues, PRs, and commits are PUBLIC. Drive paths embed
client names and project codes. "Public repo ≠ safe to publish" — every issue
carries the exclude-list + leak-grep posture (same governance as
`.claude/skills/data/ecosystem-data-sources/SKILL.md`).

Before persisting any surfaced path into a public artifact:

1. Leak-grep it for known client/project tokens (`grep -iE '<client-token-list>'`
   over the text you are about to commit; the token list is judgment + local
   knowledge — it cannot live in this public repo).
2. If identifying: use the metadata-only form ("a past mooring deliverable on
   /mnt/ace, path recorded locally") or redact the identifying segment.
3. Showing full paths in-session to the local user is fine — PERSISTING them
   into public artifacts is the gated act.
4. De-identification judgment stays on `lane:claude`.

## 4. What NOT to do

- NO ad-hoc drive crawls (`find`/`grep` over `/mnt/ace` or `/mnt/dde`) when the
  index can answer — bounded reads of specific surfaced files only.
- Never write to the drives; never mount, never sudo (unreachable dde is normal).
- Never commit raw metrics logs (`*.jsonl` under the metrics dir is gitignored
  by design — do not `git add -f` it).
- Never log raw queries without the documented opt-in (section 5) — queries
  embed client identifiers exactly like paths do.
- Never hand-copy index keywords into skills/docs — they go stale; query live.

## 5. Metrics — what is logged, where, opt-out

Every CLI run appends ONE line to the local, gitignored
`invocations.jsonl` under `data/drive-index-search/metrics/`
(emission: `scripts/data/drive-index-search/metrics.py`; fail-open — a metrics
bug never breaks a search). The #3339 nudge hook appends `{ts, session}` lines
to `nudges.jsonl` in the same dir so nudge→invocation conversion is measurable.

| Field | Meaning |
|---|---|
| `ts` | UTC ISO-8601 emission time |
| `session` | `--session` flag > `CLAUDE_CODE_SESSION_ID` env > `"unknown"` |
| `caller` | integration point (section 1) |
| `query_hash` | first 12 hex of sha256(query) — raw query NEVER logged by default |
| `n_tokens` | query token count |
| `n_results` / `top_score` | result count / best merged score (null when empty) |
| `json_flag` | `--json` used (programmatic-consumption proxy) |
| `indexes_queried` / `coverage_gaps` | counts only |
| `n_stale_indexes` | count of `index_status[].stale == true` (#3336); 0 when the key is absent |
| `exit_code` / `duration_ms` | CLI outcome / wall time |

Controls: `DRIVE_SEARCH_NO_METRICS=1` disables emission entirely;
`DRIVE_SEARCH_LOG_RAW_QUERY=1` additionally logs the raw query — LOCAL TUNING
ONLY, never leave it set (raw queries can embed client identifiers);
`DRIVE_SEARCH_METRICS_DIR=<dir>` redirects the log (tests/tuning).

Weekly aggregate (counts-only, privacy-safe by construction — no hashes, no
session ids, no paths) is COMMITTED per host:

```
python3 scripts/data/drive-index-search/aggregate_metrics.py --week <ISO-week>
# -> data/drive-index-search/metrics/weekly/<ISO-week>-<hostname>.json
```

The aggregate reports `nudges_log_absent` distinctly from "0 nudges" so a lost
denominator is visible, and counts `plans_citing_drive_paths` as the
used-in-plan proxy (undercounts when de-id redaction removes the path string —
accepted v1 caveat).

## 6. 30-day review + unified-index decision framework

At implementation close a follow-up issue is created ("review after" date in
the title) that merges the per-host weekly files and applies these criteria
(initial thresholds; the review may tune them with justification):

- **Volume**: median ≥ 10 invocations/week (excluding `caller=manual` noise).
- **Hit-rate**: fraction of invocations with `n_results ≥ 1` AND `top_score ≥`
  the `HIT_SCORE_MIN` constant in
  `scripts/data/drive-index-search/aggregate_metrics.py` (the constant is the
  only place that literal lives). Healthy ≥ 60%; < 40% = relevance problem.
- **Staleness pressure**: fraction of invocations with `n_stale_indexes ≥ 1`
  (> 25% = freshness pain). Derived from `index_status`, NOT coverage_gaps.
- **Coverage pain** (separate signal — unreachable ≠ stale): fraction with
  `coverage_gaps ≥ 1`; argues for mount/coverage work, not the unified DB.
- **Latency**: median `duration_ms` > 5000 warm = adapter ceiling reached.
- **Nudge conversion**: tunes the nudge/skill (and #3339's auto-invocation
  question) — not a DB criterion directly.

Decision matrix: **BUILD** the unified cross-drive DB (SQLite/DuckDB,
content-hash dedup, per epic #3333) iff volume passes AND at least one of
{hit-rate < 40%, stale-index-rate > 25%, latency breach}. **STAY** on the
adapter layer if volume passes and all three are healthy. **DEPRIORITIZE**
(defer the DB) if volume < 2/week regardless of quality.

## Appendix: 30-day review issue template

```
Title: Drive-file-search 30-day usage review (review after <YYYY-MM-DD>) — apply #3340 decision framework
Labels: cat:data, lane:claude
Body:
  Merge per-host aggregates in data/drive-index-search/metrics/weekly/ and apply
  the decision framework in docs/guides/drive-file-search-playbook.md section 6:
  - volume / hit-rate (HIT_SCORE_MIN in aggregate_metrics.py) / staleness
    pressure / coverage pain / latency / nudge conversion
  - Decide: BUILD unified cross-drive DB | STAY on adapters | DEPRIORITIZE
  - Also decide: #3339 nudge auto-invocation escalation (same metrics window)
  - Re-derive HIT_SCORE_MIN from the observed score distribution if needed
  Link the outcome from epic #3333.
```
