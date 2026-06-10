# Plan for #3034: Quota cache staleness — statusline freshness-aware sourcing + local slim refresh

> **Status:** adversarial-reviewed
> **Complexity:** T2
> **Date:** 2026-06-10
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3034
> **Client:** N/A
> **Project:** (none)
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-10-plan-3034-claude.md | ...-codex.md

---

## Resource Intelligence Summary

Sources consulted:

1. **`scripts/ai/assessment/query-quota.sh:78-90`** — The writer already stamps a top-level `timestamp` (`date -Iseconds`) and writes BOTH `~/.cache/agent-quota.json` (`write_cache`) and the git-tracked `config/ai-tools/agent-quota-latest.json` (`write_repo_quota`). Issue body's "no timestamp field" claim was wrong (corrected on the issue).
2. **`config/scheduled-tasks/schedule-tasks.yaml:243-256` (codex r2 MAJOR-1)** — A canonical `provider-utilization-refresh` task ALREADY runs every 4h (`20 */4 * * *`) — but `machines: [dev-primary, ace-linux-1]` only. ace-linux-2 is excluded by design.
3. **`git log -- config/ai-tools/agent-quota-latest.json`** — Repo-file freshness on ace-linux-2 depends on ace-linux-1 committing its refreshed copy (sporadic: 06-07, 06-04, 06-01 …) and this box pulling (3am cron). **Root cause: on ace-linux-2 the tracked cache is a structurally stale git-propagated snapshot** (currently `timestamp: 2026-06-07T09:15:04`, vs live codex 29% the same day the cache said 79%).
4. **`.claude/statusline-command.sh:63-78, 120-131, 163-197` (codex r2 MAJOR-2, MINOR-1)** — `extract_pct` prefers `quota_primary` (`.week_pct`) and falls back to `quota_cache` (`.pct_remaining`); `reset_days` scans both files; Claude's `c_days` countdown can be file-sourced even when its percentage is live (`statusline-command.sh:196-197`). One global freshness boolean cannot label values correctly — and a fresh HOME cache would today be shadowed by a stale-but-populated repo file. Test seams exist: `STATUSLINE_QUOTA_PRIMARY`/`STATUSLINE_QUOTA_CACHE`.
5. **`tests/statusline/test_weekly_reset.bats:26-33`, `test_combined_wrapper.bats:12-18` (codex r2 MAJOR-3)** — Existing fixtures carry NO top-level `timestamp`; "missing timestamp = stale" therefore requires updating those fixtures with fresh timestamps in the same commit (assertions unchanged).
6. **`scripts/cron/provider-utilization-refresh.sh:18-32` + `scripts/ai/provider-work-queue.py:38-44`, `provider-kanban.py:454-462` (codex r2 MAJOR-4)** — The full refresher runs five uv generators, two with live GitHub issue-list calls, and has no flock guard. Unfit to add to ace-linux-2 at 4h; the slim quota query is the only payload needed here.
7. **`scripts/cron/setup-cron.sh:21-24, 66, 94-120`** — Reads schedule-tasks.yaml (crontab-template.sh is legacy/read-only); ace-linux-2 maps to variant `contribute`; per-machine apply (#2920).
8. **#3030 (closed)** — The dispatch quota gate bypasses this cache entirely (window-validity guard); this issue is human-facing statusline truth only.

Gaps (to build from scratch):
- Per-value freshness-aware source selection + staleness marker in statusline-command.sh.
- `--cache-only` mode in query-quota.sh (local refresh must NOT dirty the git-tracked file).
- A slim `quota-snapshot-refresh` YAML task for ace-linux-2.
- bats coverage for staleness, fresher-file preference, threshold validation.

## Proposed Changes

### Step 1 — Tests first (TDD, red): `tests/statusline/test_quota_staleness.bats` (+ fixture updates)

Following the env-seam fixture pattern; existing `test_weekly_reset.bats`/`test_combined_wrapper.bats` fixtures gain a fresh `timestamp` field (assertions untouched — resolves the fixture/semantics conflict, codex r2 MAJOR-3):

1. Stale primary (timestamp > threshold), no cache → codex/gemini segments carry the `?` marker.
2. Fresh primary → no `?`; rendering otherwise identical to pre-change output for the same fixture (regression pin).
3. Missing/unparseable `timestamp` in the file a value came from → that value renders `?` (undatable = stale; fail toward visible doubt).
4. **Fresher-cache-wins (new semantic, from root cause):** stale primary + fresh HOME cache with values → values come from the cache, no `?`. Tie/equal or cache missing → primary (today's behavior).
5. Per-value sourcing (codex r2 MAJOR-2): stale primary missing codex value + fresh cache carrying it → codex unmarked, gemini (from stale primary) marked.
6. Claude mixed-source (codex r2 MINOR-1): live `rate_limits.seven_day` percentage + file-sourced `c_days` from a stale file → the countdown suffix carries the marker, the live percentage does not; fully live Claude → no marker.
7. `STATUSLINE_QUOTA_MAX_AGE_HOURS` validation (codex r2 MINOR-2): unset → 6; empty/non-numeric/zero/negative/>168 → fall back to 6 (a local env cannot silently disable the warning by huge threshold); valid small value honored.

### Step 2 — Statusline implementation (green)

In `.claude/statusline-command.sh`:
- Read each quota file's `.timestamp` once into `primary_age_h`/`cache_age_h` (python3 `fromisoformat` per the existing `days_until_iso` pattern; parse failure → "undatable").
- Threshold: validate `STATUSLINE_QUOTA_MAX_AGE_HOURS` numeric in (0, 168], else 6.
- `extract_pct` (and `reset_days`) return value + which file supplied it; selection order becomes: fresh primary > fresh cache > stale primary > stale cache (preserves today's behavior whenever ages are equal or cache absent).
- Marker: any displayed component (percentage or reset-countdown suffix) whose source file is stale/undatable gets `?` appended to that component. Claude's live `rate_limits` path is never marked; its file-sourced countdown follows the file's age.

### Step 3 — Local slim refresh (no dirty tree)

- `query-quota.sh`: add `--cache-only` flag — calls `write_cache` only, skipping `write_repo_quota`, so a local cron never dirties the git-tracked file (the repo copy remains ace-linux-1's canonical commit artifact).
- `config/scheduled-tasks/schedule-tasks.yaml`: new entry `id: quota-snapshot-refresh`, `schedule: "10 */4 * * *"` (offset from the canonical 20-past task), `machines: [dev-secondary, ace-linux-2]`, command `bash scripts/ai/assessment/query-quota.sh --refresh --cache-only --log` with a `logs/` redirect per file conventions. The existing dev-primary task is untouched.
- Apply: `bash scripts/cron/setup-cron.sh --dry-run`, then live; run the slim command once by hand and verify `~/.cache/agent-quota.json` `.timestamp` is current, codex `pct_remaining` ≈ live (29% on 2026-06-10), and the statusline `O:` segment shows the fresh unmarked value while the tracked repo file stays clean (`git status`).

### Step 4 — Verification

- `bats tests/statusline/` — new suite + updated existing suites green.
- Real-state before/after: stale repo file alone → `O:…?`; after one slim refresh → unmarked fresh value from the HOME cache.
- `legal-sanity-scan.sh --diff-only` PASS.

## Acceptance Criteria

1. Every displayed quota component is sourced from the freshest available file and carries `?` iff its source is older than the validated threshold or undatable — verified per-provider, including the Claude mixed-source case.
2. Existing statusline test suites pass with fixtures updated to carry timestamps; behavior for fresh files is unchanged versus today.
3. ace-linux-2 gets a 4h slim quota refresh that writes only `~/.cache/agent-quota.json`; the git-tracked file is never dirtied by cron on this box; the dev-primary full-refresh task is unmodified.
4. Threshold env is bounds-validated; no env value can disable staleness marking beyond the 168h cap.

## Adversarial Review Resolution (r3, inline)

- **r1 (Claude, inline): MINOR ×2** — legacy crontab-template target and full-refresher payload, folded pre-r2 (`scripts/review/results/2026-06-10-plan-3034-claude.md`).
- **r2 (Codex, dispatched): MAJOR ×4 + MINOR ×2** — `scripts/review/results/2026-06-10-plan-3034-codex.md`. Codex reviewed the as-dispatched snapshot (its closing question is answered: the local file had r1 folds mid-review; this r3 revision supersedes both). All findings adopted: existing canonical task discovered (root cause re-diagnosed as machine-targeting + git-propagation, not "no owner"); per-value source tracking replaces the global freshness boolean; fixture/semantics conflict resolved by timestamping existing fixtures; slim `--cache-only` local refresh replaces any full-refresher scheduling (also keeps the tracked file clean — new constraint found in r3 discovery); Claude mixed-source suffix marking; threshold bounds-validation with a 168h cap.
- Per the r3 inline-loop-break pattern, no re-dispatch; the r2 artifact records the pre-revision verdict.

## Risks / Notes

- **Two-file divergence is now a feature**: HOME cache = this box's live view; repo file = fleet-shared committed snapshot. The statusline prefers whichever is fresher, which is the honest per-box signal. Cross-machine quota reconciliation stays out of scope.
- **`extract_pct` return-shape change** is internal to statusline-command.sh (single consumer file); bats suites pin the rendered output, not the helper signature.
- **Statusline latency**: two `.timestamp` reads + one python3 parse per render, same cost class as existing `days_until_iso` calls.
- **`--cache-only` writer change** reverses the earlier "no writer change needed" RIS claim — driven by the dirty-tree constraint discovered in r3; the flag is additive and default behavior is unchanged.

## Out of Scope

- Auto-committing refreshed quota files; modifying the dev-primary full-refresh task or its gh-API generators (pre-existing); dispatch-gate changes (#3030 closed); cross-machine quota truth reconciliation; flock guard for the full refresher (pre-existing, separate issue if wanted).
