# Adversarial Review Results — April 2, 2026

Reviewer: **Codex (gpt-5.4)** via `codex exec`
Date: 2026-04-02T132222Z
Scope: Retroactive review of 4 work streams pushed without review

---

## Stream 1: Solver Queue (#1648, #1650, #1654, #1586, #1595)

**Verdict: MAJOR**

| # | Severity | Finding |
|---|----------|---------|
| S1 | HIGH | Manifest validation schema mismatch — submit-batch.sh requires `solver`/`input_file` but validate_manifest.py defines `name`/`solver_type`/`model_file`. Contract bug. |
| S2 | HIGH | Shell injection via `python3 -c` path interpolation in submit-batch.sh and queue-health.sh. Manifest path embedded unsanitized in Python source. |
| S3 | HIGH | watch-results.sh has race condition — no inter-process locking, two watchers can duplicate-process the same result. |
| S4 | HIGH | `git pull 2>/dev/null || true` silently masks sync failures in watcher — can operate on stale queue state indefinitely. |
| S5 | MEDIUM | queue-health.sh counts corrupt result.yaml as completed (increments before verifying parseable). |
| S6 | MEDIUM | results_dashboard.py silently discards malformed JSONL lines — quiet data loss. |
| S7 | MEDIUM | Retry classifier too coarse — treats all `license` and `not found` messages as permanent failures. |
| S8 | MEDIUM | submit-batch.sh violates `uv run` convention — uses bare `python3`. |

---

## Stream 2: GTM Job Market Scanner (#1669, #1671)

**Verdict: MAJOR**

| # | Severity | Finding |
|---|----------|---------|
| G1 | HIGH | No credible rate-limit or ToS compliance — 2s fixed delay plus forged User-Agent. No per-site policy, no robots check, no Retry-After handling. |
| G2 | HIGH | Deduplication too weak — `job_id()` hashes only title|company|location. Collapses distinct openings, misses reposts. Trend/new-this-week claims unreliable. |
| G3 | HIGH | Partial network failure can silently produce bad data that gets auto-committed to main. `git pull` and `pip install` failures masked with `|| true`. |
| G4 | MEDIUM | Unbounded JSON growth — cumulative-index.json grows forever with no retention/compaction/pruning. |
| G5 | MEDIUM | Priority scoring too naive for business use — no recency, contract/FTE distinction, geography fit, or service line mapping. |
| G6 | MEDIUM | weekly-scan-refresh.sh violates `uv run` convention — uses arbitrary Python interpreters and opportunistic `pip install`. |

---

## Stream 3: Pre-Push Review Gate + Daily Audit (#1668)

**Verdict: MAJOR**

| # | Severity | Finding |
|---|----------|---------|
| E1 | CRITICAL | WARN-by-default is not enforcement — in a 40+ commit/day workflow, exit 0 warnings will be ignored. |
| E2 | CRITICAL | Trivially bypassable — `--no-verify`, hook removal, another clone, `SKIP_REVIEW_GATE=1`. Local JSON log is not a reliable audit trail. |
| E3 | HIGH | Commit-subject classification is weak proxy — misses unprefixed commits, can be gamed by labeling as `chore:` or `docs:`. |
| E4 | HIGH | Inverse false-positive: `test:`, `docs:`, `ci:`, `chore:` can contain production-significant changes but are skipped wholesale. |
| E5 | HIGH | `git log keywords` evidence source is spoofable — commit message "reviewed with Codex" satisfies gate without actual review. |
| E6 | HIGH | Duplicate issue creation risk — no idempotency check for existing open review-backlog issues. |
| E7 | HIGH | `gh` auth failure in cron causes silent audit degradation — no explicit failure handling. |
| E8 | MEDIUM | Timezone handling — git log dates vs file mtime vs cron server time may create boundary mismatches. |
| E9 | MEDIUM | Bootstrap problem — this enforcement commit itself was not reviewed. |
| E10 | MEDIUM | Hook symlink only activates one clone — uneven enforcement across agents/machines. |
| E11 | MEDIUM | Hook latency not measured — scanning multiple dirs + git log per push adds friction. |
| E12 | LOW | Compliance score misleading if many meaningful commits classified out of scope. |
| E13 | LOW | Local bypass logs not tamper-resistant. |

---

## Summary

| Stream | Verdict | Critical | High | Medium | Low |
|--------|---------|----------|------|--------|-----|
| Solver Queue | MAJOR | 0 | 4 | 4 | 0 |
| GTM Scanner | MAJOR | 0 | 3 | 3 | 0 |
| Review Enforcement | MAJOR | 2 | 5 | 4 | 2 |
| **TOTAL** | **MAJOR** | **2** | **12** | **11** | **2** |

## Recommended Follow-Up Issues

1. **Solver: Fix manifest schema contract mismatch** (S1) — align submit-batch.sh and validate_manifest.py schemas
2. **Solver: Fix shell injection in python3 -c** (S2) — use proper quoting or standalone scripts
3. **Solver: Add watcher locking** (S3) — flock or atomic marker rename
4. **Solver: Surface git pull failures** (S4) — fail loudly instead of masking
5. **GTM: Add rate limiting and ToS compliance** (G1) — per-site config, robots check, backoff
6. **GTM: Improve deduplication** (G2) — add source URL, posting date, requisition ID to key
7. **GTM: Add data retention policy** (G4) — cap cumulative index, prune old raw results
8. **Enforcement: Add idempotent issue creation** (E6) — check for existing open backlog issue
9. **Enforcement: Handle gh auth failure** (E7) — explicit error path
10. **Enforcement: Measure hook latency** (E11) — benchmark and optimize
