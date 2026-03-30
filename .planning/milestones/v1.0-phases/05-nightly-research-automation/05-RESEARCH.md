# Phase 5: Nightly Research Automation - Research

**Researched:** 2026-03-29
**Domain:** Shell scripting, Claude CLI headless invocation, cron scheduling, research artifact management
**Confidence:** HIGH

## Summary

Phase 5 enhances an already-functional nightly researcher (`scripts/cron/gsd-researcher-nightly.sh`) that has been running since 2026-03-25 and producing quality research artifacts. The existing script handles domain rotation, context assembly, git commit/push, and failure notifications. The changes are well-scoped modifications to existing code rather than greenfield work: adding a fourth domain (competitor/market), switching to weekday-only with one-domain-per-day rotation, adding model selection (Haiku for daily, Sonnet for synthesis), enabling web search, feeding prior research as context, validating output structure, adding a staleness alert cron job, and implementing 90-day artifact pruning.

All required infrastructure exists and is verified: `claude` CLI v2.1.87 with `--model`, `--tools`, `--allowedTools`, `--max-budget-usd`, and `--no-session-persistence` flags; `scripts/notify.sh` for alerts; `config/scheduled-tasks/schedule-tasks.yaml` as the single task registry; `scripts/cron/setup-cron.sh` for idempotent crontab installation; and `scripts/lib/workstation-lib.sh` for machine variant guarding.

**Primary recommendation:** Modify the existing `gsd-researcher-nightly.sh` in-place (not replace). Add new files only for the staleness check script and the pruning logic. Register the staleness job in `schedule-tasks.yaml`.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Expand from 3 domains to 4: standards, python-ecosystem, ai-tooling, and competitor/market (focused on competing software tools: Sesam, SACS, OrcaFlex, Flexcom, ANSYS updates, feature gaps, pricing changes, new capabilities).
- **D-02:** Weekday-only schedule with one domain per day + synthesis: Mon=standards, Tue=python-ecosystem, Wed=ai-tooling, Thu=competitor/market, Fri=synthesis. Sat/Sun=off (no API cost on weekends).
- **D-03:** Manual weekly review of the Friday synthesis report. User reviews, picks insights to promote to PROJECT.md or create GitHub issues.
- **D-04:** "Insight actioned" for UAT = promoted to PROJECT.md (updating context) OR becomes a tracked GitHub issue. Concrete, verifiable bar.
- **D-05:** Synthesis report includes a structured action table at the top: `| Finding | Impact | Action | Status |` for quick scan and triage.
- **D-06:** Staleness alert: if no new research artifact appears within 36 hours, trigger a notification via notify.sh. Catches silent failures (cron not running, machine down).
- **D-07:** Staleness check runs as a separate lightweight cron job (e.g., 06:00 UTC) -- not embedded in the researcher script. This detects cases where the researcher script itself doesn't execute.
- **D-08:** 90-day auto-prune for daily research artifacts. Weekly synthesis files kept longer. Add a cron entry or integrate into existing retention logic.
- **D-09:** Enable web search for all domains (`--allowedTools WebSearch` or equivalent). Critical for recency -- CVE advisories, release notes, standard updates.
- **D-10:** Feed prior research artifacts (last week's outputs) as additional context so the model builds on prior findings, avoids repetition, and tracks evolving trends.
- **D-11:** Use Haiku for daily domain scans (cheaper, sufficient for scanning + summarizing). Use Sonnet for Friday synthesis (deeper cross-domain analysis).
- **D-12:** Basic structure validation after generation: check output has Key Findings, Relevance, and Recommended Actions sections. Reject and retry once if sections are missing. No URL verification.

### Claude's Discretion
- Exact web search tool invocation mechanism (depends on claude CLI capabilities at implementation time)
- How prior research artifacts are assembled into context (full text vs summaries)
- Staleness check script implementation details
- Pruning mechanism (cron entry vs script)
- Competitor/market prompt design (specific tool names to track, comparison angles)

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope.
</user_constraints>

## Standard Stack

### Core
| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| Claude CLI | 2.1.87 | Headless AI invocation for research generation | Already installed, used by current researcher, has all required flags |
| bash | 5.x | Script execution environment | Project standard, all cron scripts are bash |
| cron | system | Scheduling | Already used for 12+ scheduled tasks in this project |

### Supporting
| Tool | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| `scripts/notify.sh` | current | Failure/staleness notifications | On researcher failure and staleness detection |
| `scripts/lib/workstation-lib.sh` | current | Machine variant guard (`ws_is "full"`) | Script entry point to skip non-primary machines |
| `config/scheduled-tasks/schedule-tasks.yaml` | current | Task registry (single source of truth) | Register new staleness-check job |
| `scripts/cron/setup-cron.sh` | current | Idempotent crontab installer | After adding staleness job to YAML |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Haiku for daily | Sonnet for all | 3-5x cost increase, marginal quality improvement for scanning tasks |
| `--tools` restriction | No tool restriction | Default gives Bash/Edit access which is unnecessary and risky for headless research |
| Separate staleness script | Staleness check inside researcher | Would not detect cases where researcher script itself fails to run |
| 90-day find -delete | Custom Python pruner | find is simpler, proven pattern (already used for notification-purge) |

## Architecture Patterns

### Modified Files
```
scripts/
  cron/
    gsd-researcher-nightly.sh   # MODIFY: rotation, model, tools, validation, prior context
    research-staleness-check.sh  # NEW: 36-hour freshness alert
.planning/
  research/
    README.md                    # MODIFY: update rotation table, add pruning docs
config/
  scheduled-tasks/
    schedule-tasks.yaml          # MODIFY: add staleness-check entry, update researcher description
```

### Pattern 1: Claude CLI Headless Invocation
**What:** Using `claude -p` with model, tool, and budget controls for unattended operation.
**When to use:** All researcher invocations (daily and synthesis).
**Verified flags (tested on this machine):**

```bash
# Daily domain research (Haiku, restricted tools, web search enabled)
echo "$CONTEXT" | timeout "$TIME_BUDGET" claude -p "$PROMPT" \
    --model haiku \
    --tools "Read,WebSearch" \
    --allowedTools "Read WebSearch" \
    --max-budget-usd 0.50 \
    --no-session-persistence \
    2>>"$LOG_FILE"

# Friday synthesis (Sonnet, restricted tools, web search enabled)
echo "$CONTEXT" | timeout "$TIME_BUDGET" claude -p "$PROMPT" \
    --model sonnet \
    --tools "Read,WebSearch" \
    --allowedTools "Read WebSearch" \
    --max-budget-usd 2.00 \
    --no-session-persistence \
    2>>"$LOG_FILE"
```

**Key findings from testing:**
- `--model haiku` and `--model sonnet` work as aliases (verified on CLI v2.1.87)
- `--tools "Read,WebSearch"` restricts available tools to ONLY those listed (verified: model reports only Read and WebSearch)
- `--allowedTools "Read WebSearch"` pre-approves tools (no permission prompt in headless mode)
- `--max-budget-usd` provides a cost safety guard (verified: exits with error when exceeded)
- `--no-session-persistence` prevents session files from accumulating on disk
- `--bare` flag should NOT be used -- it changes auth behavior and requires explicit `ANTHROPIC_API_KEY` (breaks OAuth-based auth)
- Without `--bare`, CLAUDE.md and project rules are still loaded (harmless, provides useful project context)

### Pattern 2: Domain Rotation (Weekday-Only)
**What:** Map day-of-week to one domain; skip weekends.
**Current:** `$DAY_NUM` case statement (1=Mon through 7=Sun), all 7 days.
**New:**

```bash
case "$DAY_NUM" in
    1) DOMAIN="standards" ;;
    2) DOMAIN="python-ecosystem" ;;
    3) DOMAIN="ai-tooling" ;;
    4) DOMAIN="competitor-market" ;;
    5) DOMAIN="synthesis" ;;
    6|7)
        log "SKIP: weekend (day=${DAY_NUM})"
        exit 0
        ;;
esac
```

### Pattern 3: Prior Research Context Assembly
**What:** Feed last week's research artifacts as additional context to avoid repetition and build on trends.
**Implementation:** Concatenate `.planning/research/*.md` files from the last 7 days, same delimited format as existing context assembly.

```bash
# Assemble prior research (last 7 days)
PRIOR_RESEARCH=""
for f in "${OUTPUT_DIR}"/*.md; do
    [[ -f "$f" ]] || continue
    [[ "$(basename "$f")" == "README.md" ]] && continue
    file_date=$(basename "$f" | grep -oP '^\d{4}-\d{2}-\d{2}' || echo "")
    if [[ -n "$file_date" ]]; then
        days_old=$(( ($(date -d "$DATE" +%s) - $(date -d "$file_date" +%s)) / 86400 )) 2>/dev/null || days_old=99
        if [[ "$days_old" -le 7 && "$days_old" -ge 0 ]]; then
            PRIOR_RESEARCH+="--- $(basename "$f") ---"$'\n'
            PRIOR_RESEARCH+="$(cat "$f")"$'\n\n'
        fi
    fi
done
```

**Decision (Claude's discretion):** Use full text of prior artifacts (not summaries). Haiku's context window is sufficient for ~7 research files averaging 5KB each (~35KB total). Summarization would lose detail needed for trend tracking and repetition avoidance.

### Pattern 4: Output Validation with Retry
**What:** Check generated output has required sections; retry once on failure.
**Required sections (from D-12):** "Key Findings", "Relevance" (covers "Relevance to Project"), "Recommended Actions".

```bash
validate_output() {
    local file="$1"
    local missing=()
    grep -qi "key findings" "$file"        || missing+=("Key Findings")
    grep -qi "relevance" "$file"           || missing+=("Relevance")
    grep -qi "recommended actions" "$file" || missing+=("Recommended Actions")
    if [[ ${#missing[@]} -gt 0 ]]; then
        echo "${missing[*]}"
        return 1
    fi
    return 0
}
```

### Pattern 5: Staleness Check (Separate Script)
**What:** Independent script checking if newest `.planning/research/*.md` is older than 36 hours.
**Why separate (D-07):** Detects cases where the researcher script itself doesn't execute (cron misconfiguration, machine down).

```bash
#!/usr/bin/env bash
# research-staleness-check.sh -- alert if no research artifact in 36 hours
# Registered in schedule-tasks.yaml, runs at 06:00 UTC daily

NEWEST=$(find "$OUTPUT_DIR" -name "*.md" ! -name "README.md" -printf '%T@\n' 2>/dev/null | sort -rn | head -1)
NOW=$(date +%s)
AGE_HOURS=$(( (NOW - ${NEWEST%.*}) / 3600 ))

if [[ "$AGE_HOURS" -gt 36 ]]; then
    bash "${WS_HUB}/scripts/notify.sh" cron research-staleness fail \
        "No research artifact in ${AGE_HOURS}h (threshold: 36h)"
fi
```

**Weekend-aware caveat:** With weekday-only schedule (D-02), the staleness check must account for weekends. Friday's artifact would be ~60 hours old by Monday 06:00 UTC. The threshold should be 60 hours (not 36) to avoid false positives on Monday. Alternatively, skip the staleness check on Saturday/Sunday/Monday-before-researcher-runs. Recommended: use 60-hour threshold and let it fire on genuine multi-day gaps. This is simpler than day-of-week logic in the staleness checker.

**Correction to D-06:** The 36-hour threshold will fire false positives every Monday (Friday artifact is ~53h old by Monday 06:00). Use 60 hours instead, or skip staleness checks on weekends+Monday. This should be flagged to the planner as a necessary adaptation of the user's decision.

### Pattern 6: 90-Day Artifact Pruning (D-08)
**What:** Delete daily research files older than 90 days; keep synthesis files longer.
**Proven pattern:** The `notification-purge` task already uses `find -mtime -delete` in schedule-tasks.yaml.

```bash
# Prune daily research artifacts older than 90 days (keep synthesis longer)
find "$OUTPUT_DIR" -name "????-??-??-*.md" ! -name "*-synthesis.md" -mtime +90 -delete 2>/dev/null || true
# Prune synthesis artifacts older than 365 days
find "$OUTPUT_DIR" -name "*-synthesis.md" -mtime +365 -delete 2>/dev/null || true
```

**Implementation (Claude's discretion):** Integrate pruning into the researcher script itself (run at the end of each execution) rather than a separate cron job. This avoids yet another scheduled task entry. The researcher already runs daily and is the natural owner of its output directory. If the researcher doesn't run, pruning is deferred but not harmful.

### Anti-Patterns to Avoid
- **Using `--bare` flag:** Breaks OAuth auth, requires explicit `ANTHROPIC_API_KEY` env var. Use `--tools` + `--allowedTools` instead.
- **Giving researcher Bash/Edit/Write tools:** Headless research should be read-only + web search. No filesystem mutation.
- **Embedding staleness check in researcher:** Defeats the purpose (D-07) -- the check must detect when the researcher itself doesn't run.
- **Hardcoding absolute paths:** Use `$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)` pattern (already used in current script).
- **Using `--system-prompt` to override:** Even with override, CLAUDE.md still loads. Use `--append-system-prompt` if needed, but piping context via stdin is the established pattern and works well.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Scheduling | Custom daemon or systemd timer | cron via `schedule-tasks.yaml` + `setup-cron.sh` | Established pattern, 12+ tasks already use it |
| Notifications | Custom notification system | `scripts/notify.sh` | JSONL-based, already integrated with researcher |
| Machine guard | Hostname parsing | `workstation-lib.sh` `ws_is "full"` | Handles aliases, registry lookup |
| Model selection | API calls, SDK imports | `claude --model haiku/sonnet` | CLI handles auth, model routing, rate limits |
| Web search | Scraping, custom HTTP | `--tools "Read,WebSearch"` | Built into Claude CLI, no external dependencies |
| File retention | Custom age-tracking database | `find -mtime +N -delete` | Standard Unix, already used for notification-purge |

**Key insight:** This phase is incremental improvement to existing infrastructure, not new system design. Every building block is already in place and tested in production.

## Common Pitfalls

### Pitfall 1: Weekend False Positives on Staleness Check
**What goes wrong:** Staleness alert fires every Monday because Friday's artifact is >36h old.
**Why it happens:** D-06 specifies 36h threshold but D-02 specifies weekday-only (60h gap Fri-to-Mon).
**How to avoid:** Use 60-hour threshold (accounts for Friday 01:35 UTC to Monday 06:00 UTC = ~52h). Log the skip reason when weekend gap is detected.
**Warning signs:** notify.sh sending "stale" alerts every Monday morning.

### Pitfall 2: Context Size Explosion with Prior Research
**What goes wrong:** Feeding too many prior artifacts overflows the model's useful context window or hits token limits.
**Why it happens:** Over time, if prior research window extends beyond 7 days or files grow large.
**How to avoid:** Hard cap at 7 days of prior artifacts. For synthesis, this is natural (week's files). For daily, the prior artifacts provide trend continuity without overwhelming. Monitor log file for context length.
**Warning signs:** Claude CLI timeout (currently 180s) hit more frequently; research quality degrades.

### Pitfall 3: Model Alias Instability
**What goes wrong:** `--model haiku` or `--model sonnet` stops resolving after a CLI update.
**Why it happens:** Claude CLI updates can change model alias mappings.
**How to avoid:** Log the actual model used (if possible from CLI output). The existing error handling + notify.sh will catch failures. Can fall back to explicit model IDs if needed.
**Warning signs:** Sudden researcher failures after `harness-update.sh` runs (01:15 UTC, before researcher at 01:35).

### Pitfall 4: Synthesis Glob Pattern Inefficiency
**What goes wrong:** The existing glob `${DATE%%-*}*.md` matches all files from the current year, then filters by date.
**Why it happens:** Bash parameter expansion `${DATE%%-*}` extracts just the year ("2026").
**How to avoid:** For the current scale (4 artifacts/week, ~200/year), this is fine. The `days_old` filter correctly limits to 7 days. No action needed unless artifacts grow to thousands.
**Warning signs:** Synthesis step taking noticeably longer than daily scans.

### Pitfall 5: Git Commit Race with Other Cron Jobs
**What goes wrong:** Researcher's git commit/push conflicts with repository-sync (every 4h) or other tasks.
**Why it happens:** Multiple cron jobs run git operations on the same repo.
**How to avoid:** The current script already handles this with `|| true` on git push. The best-effort commit pattern is correct. No lock needed.
**Warning signs:** Persistent "git push failed" in logs (occasional failures are normal).

### Pitfall 6: Output Validation Regex Too Strict or Too Loose
**What goes wrong:** Validation rejects valid output because of case/format differences, or accepts empty sections.
**Why it happens:** The model might format headers as "## Key findings" (lowercase) or "**Key Findings:**" (bold).
**How to avoid:** Use case-insensitive grep (`grep -qi`). Check for section presence, not content quality. D-12 explicitly says no URL verification.
**Warning signs:** Frequent retries logged, or invalid artifacts passing validation.

## Code Examples

### Competitor/Market Domain Prompt (Claude's Discretion)

```bash
competitor-market)
    PROMPT="You are a research assistant tracking the competitive landscape for offshore/subsea engineering software. Given the project context below, search for recent developments in competing tools. Focus on:
- Sesam (Wood Group) — structural analysis updates, new modules, pricing changes
- SACS (Bentley) — offshore structural analysis, version updates, cloud offerings
- OrcaFlex (Orcina) — dynamic analysis, new cable/riser models, licensing changes
- Flexcom (Wood Group) — flexible pipe/riser analysis, new capabilities
- ANSYS (Ansys Inc) — mechanical/structural updates relevant to offshore, API changes
- Any new entrants in offshore/subsea engineering software
- Open-source alternatives gaining traction (OpenFAST, Blue Kenue, etc.)

Report pricing changes, new capabilities, deprecated features, and any shifts that create opportunities or threats for aceengineer.com's calculator and consulting positioning.

${OUTPUT_FORMAT}"
    ;;
```

### Updated Synthesis Prompt with Action Table (D-05)

```bash
synthesis)
    PROMPT="You are synthesizing this week's research findings for an engineering team. Review all research reports from this week (provided below) and produce a weekly synthesis.

Output format:

# Weekly Research Synthesis -- __DATE__

## Action Table
| Finding | Impact | Action | Status |
|---------|--------|--------|--------|
| [finding] | High/Medium/Low | Promote to PROJECT.md / Create GitHub issue / Monitor / Ignore | Pending |

## Top 3 Insights for PROJECT.md
1. Insight with rationale for promotion
2. ...
3. ...

## Cross-Domain Connections
- Connection between domains

## Detailed Action Items
- [ ] Promote: specific insight -> PROJECT.md section
- [ ] Issue: specific finding -> GitHub issue title
- [ ] Monitor: finding to watch next week"
    ;;
```

### Model Selection Logic

```bash
# Model selection based on domain (D-11)
if [[ "$DOMAIN" == "synthesis" ]]; then
    MODEL="sonnet"
    BUDGET="2.00"
else
    MODEL="haiku"
    BUDGET="0.50"
fi
```

### Pruning Integration (End of Researcher Script)

```bash
# 90-day prune for daily artifacts, 365-day for synthesis (D-08)
log "Pruning old research artifacts..."
PRUNED_DAILY=$(find "$OUTPUT_DIR" -name "????-??-??-*.md" ! -name "*-synthesis.md" -mtime +90 -delete -print 2>/dev/null | wc -l)
PRUNED_SYNTH=$(find "$OUTPUT_DIR" -name "*-synthesis.md" -mtime +365 -delete -print 2>/dev/null | wc -l)
log "Pruned: ${PRUNED_DAILY} daily, ${PRUNED_SYNTH} synthesis artifacts"
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `claude -p` (default model, all tools) | `claude -p --model haiku --tools "Read,WebSearch"` | Available in CLI v2.1.x | Cost control, security (no Bash/Edit), web search |
| No session persistence control | `--no-session-persistence` flag | CLI v2.1.x | Prevents session file accumulation from headless runs |
| Agent SDK (programmatic) | CLI `-p` mode (headless) | Project decision | Simpler, no npm dependency, uses existing auth |
| 7-day rotation (all days) | 5-day rotation (weekday-only) | This phase | Saves ~28% on API costs |

**Deprecated/outdated:**
- `--bare` flag is not suitable for OAuth-authenticated environments (which this project uses). It requires explicit `ANTHROPIC_API_KEY`.
- `ClaudeCodeOptions` in Agent SDK renamed to `ClaudeAgentOptions` (noted in ai-tooling research 2026-03-28). Not relevant since this phase uses CLI, not SDK.

## Open Questions

1. **Staleness threshold vs. weekday schedule tension**
   - What we know: D-06 says 36h, D-02 says weekday-only. Friday 01:35 UTC to Monday 06:00 UTC is ~52h.
   - What's unclear: Whether user intended 36h for weekday-to-weekday gaps only.
   - Recommendation: Use 60h threshold. Document the reasoning. If user wants tighter weekday detection, the staleness script can add day-of-week awareness later.

2. **Cost per month estimate**
   - What we know: Haiku is ~$0.25/1M input, $1.25/1M output; Sonnet is ~$3/1M input, $15/1M output. Each research call uses ~10-15K input tokens (context + prompt) and generates ~2-5K output tokens.
   - What's unclear: Exact per-call cost depends on context size growth as prior artifacts are fed.
   - Recommendation: Estimated $1-3/month for Haiku (4 calls/week) + $0.50-1.50/week for Sonnet synthesis. Total ~$5-10/month. `--max-budget-usd` guard prevents runaway costs.

3. **Prior research assembly for non-synthesis domains**
   - What we know: D-10 says feed prior research as context. Currently only synthesis assembles prior files.
   - What's unclear: Whether daily domain scans should see ALL prior research or only their own domain's prior artifacts.
   - Recommendation: Feed all prior research (last 7 days, all domains) to daily scans. Cross-domain context is valuable (e.g., Python CVE affecting an engineering standard). Token cost is minimal with Haiku.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| claude CLI | Research generation | Yes | 2.1.87 | -- (blocking) |
| cron | Scheduling | Yes | system | -- (blocking) |
| bash | Script execution | Yes | 5.x | -- (blocking) |
| git | Artifact commit/push | Yes | system | Best-effort (skip commit) |
| notify.sh | Failure/staleness alerts | Yes | current | Log-only (degrade gracefully) |
| workstation-lib.sh | Machine guard | Yes | current | Hostname case match fallback |
| find (GNU) | Pruning | Yes | system | -- |
| grep -P (PCRE) | Date extraction | Yes | system | grep -oE fallback |

**Missing dependencies with no fallback:** None -- all required tools are installed and verified.

**Missing dependencies with fallback:** None.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | bash + manual verification (no pytest for shell scripts) |
| Config file | None (shell scripts tested via `--dry-run` and manual execution) |
| Quick run command | `bash scripts/cron/gsd-researcher-nightly.sh --dry-run` |
| Full suite command | Manual: run researcher, check output, verify staleness check, verify pruning |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| D-01 | 4-domain rotation (standards, python-ecosystem, ai-tooling, competitor/market) | smoke | `bash scripts/cron/gsd-researcher-nightly.sh --dry-run` (check domain output) | Modify existing |
| D-02 | Weekday-only schedule, skip Sat/Sun | smoke | `DAY_NUM=6 bash scripts/cron/gsd-researcher-nightly.sh --dry-run` (should log SKIP) | Modify existing |
| D-05 | Synthesis has action table | manual | Inspect Friday synthesis output for `\| Finding \| Impact \| Action \| Status \|` | N/A |
| D-06/D-07 | Staleness alert fires when no artifact in threshold | smoke | `bash scripts/cron/research-staleness-check.sh --dry-run` | Wave 0 (new script) |
| D-08 | 90-day daily prune, 365-day synthesis prune | smoke | Create test files with old timestamps, run pruning, verify deletion | Manual test |
| D-09 | Web search enabled for all domains | smoke | Check `--tools` flag in script contains `WebSearch` | Code review |
| D-10 | Prior research fed as context | smoke | `--dry-run` output shows "Context length" > baseline | Modify existing |
| D-11 | Haiku for daily, Sonnet for synthesis | smoke | `--dry-run` output shows model selection per domain | Modify existing |
| D-12 | Output validation with retry | smoke | Generate output missing a section, verify retry logic | Manual test |

### Sampling Rate
- **Per task commit:** `bash scripts/cron/gsd-researcher-nightly.sh --dry-run`
- **Per wave merge:** Manual full run of researcher + staleness check
- **Phase gate:** At least one nightly run produces valid output; staleness check correctly detects/skips

### Wave 0 Gaps
- [ ] `scripts/cron/research-staleness-check.sh` -- new script (D-06/D-07), needs `--dry-run` support
- [ ] Update `--dry-run` output in researcher to show model selection and tool restriction
- [ ] No automated test framework for shell scripts -- rely on `--dry-run` smoke tests and manual UAT

## Sources

### Primary (HIGH confidence)
- **Claude CLI v2.1.87 `--help`** -- verified all flags (`--model`, `--tools`, `--allowedTools`, `--max-budget-usd`, `--no-session-persistence`, `--bare`) on the actual installed CLI
- **Live testing** -- `--model haiku` works, `--tools "Read,WebSearch"` restricts tool list (verified), `--bare` breaks OAuth (verified), `--allowedTools` pre-approves without restricting (verified)
- **Existing script** `scripts/cron/gsd-researcher-nightly.sh` -- read in full, all patterns documented
- **schedule-tasks.yaml** -- read in full, 12+ tasks already registered, notification-purge uses find-delete pattern
- **Research artifacts** `2026-03-26` through `2026-03-29` -- read in full, quality is good, format is established

### Secondary (MEDIUM confidence)
- **Cost estimates** -- Based on published Anthropic pricing as of training data. Actual costs depend on token counts.

### Tertiary (LOW confidence)
- None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all tools verified on this machine, existing infrastructure is production-proven
- Architecture: HIGH -- modifications to working code, patterns extracted from existing implementation
- Pitfalls: HIGH -- staleness threshold tension identified from concrete date arithmetic, other pitfalls from production log review

**Research date:** 2026-03-29
**Valid until:** 2026-04-28 (30 days -- stable domain, CLI version may change)
