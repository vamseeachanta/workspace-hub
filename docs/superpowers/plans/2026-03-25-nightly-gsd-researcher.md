# Nightly GSD Researcher Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Set up a nightly cron job that runs domain-specific research via Claude CLI and surfaces findings in the morning summary.

**Architecture:** A single bash script (`gsd-researcher-nightly.sh`) rotates through 3 research domains by day-of-week, pipes PROJECT.md + ROADMAP.md as context to `claude -p`, writes structured output to `.planning/research/`, and commits. A new daily_today section script reads yesterday's research for the morning digest.

**Tech Stack:** Bash, Claude CLI (`claude -p` via stdin pipe), YAML schedule config, git

**Spec:** `docs/superpowers/specs/2026-03-25-nightly-gsd-researcher-design.md`

---

### Task 1: Create directory structure and .gitkeep files

**Files:**
- Create: `.planning/research/.gitkeep`
- Create: `logs/research/.gitkeep`

- [ ] **Step 1: Create research output directory**

```bash
mkdir -p .planning/research
touch .planning/research/.gitkeep
```

- [ ] **Step 2: Create research log directory**

```bash
mkdir -p logs/research
touch logs/research/.gitkeep
```

- [ ] **Step 3: Commit**

```bash
git add .planning/research/.gitkeep logs/research/.gitkeep
git commit -m "chore(1434): create research and log directories"
```

---

### Task 2: Write the researcher script

**Files:**
- Create: `scripts/cron/gsd-researcher-nightly.sh`

- [ ] **Step 1: Create the script**

Write `scripts/cron/gsd-researcher-nightly.sh`:

```bash
#!/usr/bin/env bash
# ABOUTME: Nightly GSD researcher — rotates domains by day-of-week, writes to .planning/research/
# ABOUTME: Pipes PROJECT.md + ROADMAP.md as context to claude CLI
# Issue: #1434
#
# Domain rotation:
#   Mon/Thu = standards (offshore/subsea)
#   Tue/Fri = python-ecosystem
#   Wed/Sat = ai-tooling (Claude, GSD, MCP)
#   Sun     = synthesis (week review)
#
# Usage: bash scripts/cron/gsd-researcher-nightly.sh [--dry-run]

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_HUB="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DATE=$(date -u +%Y-%m-%d)
DAY_NUM=$(date +%u)  # 1=Mon, 7=Sun
TIME_BUDGET=180
DRY_RUN=false
LOG_DIR="${WS_HUB}/logs/research"
OUTPUT_DIR="${WS_HUB}/.planning/research"

for arg in "$@"; do
    [[ "$arg" == "--dry-run" ]] && DRY_RUN=true
done

mkdir -p "$LOG_DIR" "$OUTPUT_DIR"
LOG_FILE="${LOG_DIR}/${DATE}.log"

log() { echo "[gsd-researcher] $(date -u +%H:%M:%S) $*" | tee -a "$LOG_FILE"; }

# ── Hostname guard ───────────────────────────────────────────────────────────
HOSTNAME_SHORT=$(hostname -s 2>/dev/null || hostname | cut -d. -f1)
HOSTNAME_SHORT=$(printf '%s' "$HOSTNAME_SHORT" | tr '[:upper:]' '[:lower:]')
case "$HOSTNAME_SHORT" in
    dev-primary|ace-linux-1) ;;
    *)
        log "SKIP: not dev-primary (hostname=$HOSTNAME_SHORT)"
        exit 0
        ;;
esac

# ── Git pull ─────────────────────────────────────────────────────────────────
log "Starting nightly research"
cd "$WS_HUB"
git pull --rebase --quiet 2>>"$LOG_FILE" || {
    log "WARNING: git pull failed — continuing with local state"
}

# ── Domain selection ─────────────────────────────────────────────────────────
case "$DAY_NUM" in
    1|4) DOMAIN="standards" ;;
    2|5) DOMAIN="python-ecosystem" ;;
    3|6) DOMAIN="ai-tooling" ;;
    7)   DOMAIN="synthesis" ;;
    *)   DOMAIN="standards" ;;
esac

log "Domain: ${DOMAIN} (day=${DAY_NUM})"

# ── Context assembly ─────────────────────────────────────────────────────────
CONTEXT=""
for f in .planning/PROJECT.md .planning/ROADMAP.md; do
    if [[ -f "$f" ]]; then
        CONTEXT+="--- $(basename "$f") ---"$'\n'
        CONTEXT+="$(cat "$f")"$'\n\n'
    fi
done

# ── Domain prompts ───────────────────────────────────────────────────────────
OUTPUT_FORMAT='Use this exact output format:

# Research: DOMAIN — DATE

## Key Findings
- Finding with source/reference (one bullet per finding, 3-5 findings)

## Relevance to Project
- How each finding affects a specific package or workflow in this project

## Recommended Actions
- [ ] Actionable item (one of: promote to PROJECT.md, create GitHub issue, or ignore with reason)'

case "$DOMAIN" in
    standards)
        PROMPT="You are a research assistant for an offshore/subsea engineering team. Given the project context below, search your knowledge for recent developments in engineering standards relevant to this project. Focus on:
- API (American Petroleum Institute) standards updates
- DNV (Det Norske Veritas) recommended practices and rules
- ABS (American Bureau of Shipping) guides
- ISO standards for offshore/marine structures
- Any regulatory changes affecting cathodic protection, VIV, fitness-for-service, or structural analysis

Report only findings from the past 6 months that are relevant to the packages and domains described in the project context.

${OUTPUT_FORMAT}"
        ;;
    python-ecosystem)
        PROMPT="You are a research assistant tracking the Python packaging ecosystem. Given the project context below, search your knowledge for recent developments relevant to this project. Focus on:
- uv package manager changes, new features, or breaking changes
- Dependencies used by tier-1 packages (numpy, pandas, pyyaml, etc.) — new versions, deprecations, security advisories
- Python packaging standards (PEP updates, pyproject.toml changes)
- Testing ecosystem changes (pytest, coverage tools)
- Any CVEs or security advisories affecting common scientific Python packages

Report only findings from the past 3 months that are relevant to the packages described in the project context.

${OUTPUT_FORMAT}"
        ;;
    ai-tooling)
        PROMPT="You are a research assistant tracking AI developer tooling. Given the project context below, search your knowledge for recent developments relevant to this project. Focus on:
- Claude Code CLI updates, new features, or behavior changes
- GSD framework (get-shit-done) updates and new patterns
- Codex CLI and Gemini CLI changes
- MCP (Model Context Protocol) ecosystem updates — new servers, protocol changes
- Agent SDK developments (Anthropic, OpenAI)
- Multi-agent orchestration patterns

Report only findings from the past 3 months that are relevant to the AI tooling stack described in the project context.

${OUTPUT_FORMAT}"
        ;;
    synthesis)
        # For synthesis, add this week's research files as context
        WEEK_FILES=""
        for f in "${OUTPUT_DIR}/${DATE%%-*}"*.md; do
            [[ -f "$f" ]] || continue
            # Only include files from the past 7 days
            file_date=$(basename "$f" | grep -oP '^\d{4}-\d{2}-\d{2}' || echo "")
            if [[ -n "$file_date" ]]; then
                days_old=$(( ($(date -d "$DATE" +%s) - $(date -d "$file_date" +%s)) / 86400 )) 2>/dev/null || days_old=99
                if [[ "$days_old" -le 7 ]]; then
                    WEEK_FILES+="--- $(basename "$f") ---"$'\n'
                    WEEK_FILES+="$(cat "$f")"$'\n\n'
                fi
            fi
        done
        CONTEXT+="${WEEK_FILES}"

        PROMPT="You are synthesizing this week's research findings for an engineering team. Review all research reports from this week (provided below) and produce a weekly synthesis. Focus on:
- Rank findings by impact to the project (high/medium/low)
- Identify cross-domain connections (e.g., a Python CVE affecting an engineering package)
- Flag the top 3 insights that should be promoted to PROJECT.md
- Note any findings that warrant a GitHub issue

Output format:

# Weekly Research Synthesis — DATE

## Top 3 Insights for PROJECT.md
1. Insight with rationale for promotion
2. ...
3. ...

## Cross-Domain Connections
- Connection between domains

## Action Items
- [ ] Promote: specific insight → PROJECT.md section
- [ ] Issue: specific finding → GitHub issue title
- [ ] Monitor: finding to watch next week"
        ;;
esac

# ── Replace placeholders in prompts ──────────────────────────────────────────
PROMPT="${PROMPT//DOMAIN/$DOMAIN}"
PROMPT="${PROMPT//DATE/$DATE}"

OUTPUT_FILE="${OUTPUT_DIR}/${DATE}-${DOMAIN}.md"

# ── Dry run ──────────────────────────────────────────────────────────────────
if [[ "$DRY_RUN" == true ]]; then
    log "DRY RUN — would call claude with domain=${DOMAIN}"
    log "Context length: ${#CONTEXT} chars"
    log "Output would go to: ${OUTPUT_FILE}"
    exit 0
fi

# ── Research call ────────────────────────────────────────────────────────────
if ! command -v claude >/dev/null 2>&1; then
    log "ERROR: claude CLI not found in PATH"
    bash "${WS_HUB}/scripts/notify.sh" cron gsd-researcher fail "claude CLI not found" || true
    exit 1
fi

log "Calling claude (timeout=${TIME_BUDGET}s)..."
RESULT=$(echo "$CONTEXT" | timeout "$TIME_BUDGET" claude -p "$PROMPT" 2>>"$LOG_FILE") || {
    log "ERROR: claude call failed or timed out"
    bash "${WS_HUB}/scripts/notify.sh" cron gsd-researcher fail "claude timeout or error" || true
    exit 1
}

# ── Write output ─────────────────────────────────────────────────────────────
echo "$RESULT" > "$OUTPUT_FILE"
log "Research written to: ${OUTPUT_FILE} ($(wc -l < "$OUTPUT_FILE") lines)"

# ── Git commit (best-effort) ─────────────────────────────────────────────────
git add "$OUTPUT_FILE" 2>>"$LOG_FILE" || true
if ! git diff --staged --quiet 2>/dev/null; then
    git commit -m "docs(research): ${DOMAIN} research ${DATE}" --quiet 2>>"$LOG_FILE" || {
        log "WARNING: git commit failed"
    }
    git push --quiet 2>>"$LOG_FILE" || {
        log "WARNING: git push failed — will sync on next repo-sync"
    }
fi

# ── Notify ───────────────────────────────────────────────────────────────────
bash "${WS_HUB}/scripts/notify.sh" cron gsd-researcher pass "domain=${DOMAIN}" || true
log "Done"
```

- [ ] **Step 2: Make executable**

```bash
chmod +x scripts/cron/gsd-researcher-nightly.sh
```

- [ ] **Step 3: Verify dry-run works**

Run: `bash scripts/cron/gsd-researcher-nightly.sh --dry-run`

Expected: Output showing domain selection, context length, output path — no claude call made.

- [ ] **Step 4: Commit**

```bash
git add scripts/cron/gsd-researcher-nightly.sh
git commit -m "feat(1434): add nightly GSD researcher script"
```

---

### Task 3: Add schedule entry to YAML

**Files:**
- Modify: `config/scheduled-tasks/schedule-tasks.yaml`

- [ ] **Step 1: Add the gsd-researcher entry**

Insert after the `benchmark-regression` entry (which also runs at 1:30 AM but is not a claude task — this keeps claude tasks visually grouped near `skills-curation`). Actually, insert before the `comprehensive-learning` entry to maintain chronological order:

Add this block after the `benchmark-regression` entry (line 20) and before `dep-health`:

Wait — `benchmark-regression` is at `30 1 * * *` which conflicts with our `30 1 * * *`. Since benchmark is not a claude task and researcher is, they can run in parallel. But to be safe, offset by 5 minutes.

Actually, re-reading the crontab: `benchmark-regression` is already at `30 1`. Let's use `35 1` for the researcher to avoid simultaneous startup.

Add after the `benchmark-regression` entry:

```yaml
  - id: gsd-researcher
    label: Nightly GSD domain researcher
    schedule: "35 1 * * *"
    machines: [dev-primary, ace-linux-1]
    command: >-
      PATH=$HOME/.local/bin:$PATH;
      cd $WORKSPACE_HUB &&
      bash scripts/cron/gsd-researcher-nightly.sh
      >> $WORKSPACE_HUB/logs/research/$(date +\%Y-\%m-\%d).log 2>&1
    log: logs/research/*.log
    is_claude_task: true
    description: Nightly domain research rotating standards/python-ecosystem/ai-tooling; Sunday synthesis.
```

- [ ] **Step 2: Validate schedule YAML**

Run: `uv run --no-project python config/scheduled-tasks/validate-schedule.py`

Expected: No errors.

- [ ] **Step 3: Commit**

```bash
git add config/scheduled-tasks/schedule-tasks.yaml
git commit -m "feat(1434): add gsd-researcher to schedule YAML"
```

---

### Task 4: Create morning summary section script

**Files:**
- Create: `scripts/productivity/sections/research-highlights.sh`
- Modify: `scripts/productivity/daily_today.sh`

- [ ] **Step 1: Create the section script**

Write `scripts/productivity/sections/research-highlights.sh`:

```bash
#!/usr/bin/env bash
# ABOUTME: Daily log section — surfaces overnight research findings from .planning/research/
# Usage: bash research-highlights.sh <WORKSPACE_ROOT>

set -euo pipefail
WORKSPACE_ROOT="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"
RESEARCH_DIR="$WORKSPACE_ROOT/.planning/research"

echo "## Research Highlights"
echo ""

if [[ ! -d "$RESEARCH_DIR" ]]; then
    echo "_No research directory found._"
    echo ""
    return 0 2>/dev/null || exit 0
fi

# Find research files modified in the last 24 hours
RECENT=$(find "$RESEARCH_DIR" -name "*.md" -not -name ".gitkeep" -mtime -1 2>/dev/null | sort)

if [[ -z "$RECENT" ]]; then
    echo "_No new research from last night._"
    echo ""
    return 0 2>/dev/null || exit 0
fi

for f in $RECENT; do
    filename=$(basename "$f" .md)
    echo "### ${filename}"
    echo ""

    # Extract Key Findings section
    findings=$(sed -n '/^## Key Findings/,/^## /{ /^## Key Findings/d; /^## /d; p; }' "$f" 2>/dev/null)
    if [[ -n "$findings" ]]; then
        echo "$findings"
    else
        echo "_(could not extract findings)_"
    fi
    echo ""

    # Extract Recommended Actions section
    actions=$(sed -n '/^## Recommended Actions/,/^## \|^$/{ /^## Recommended Actions/d; /^## /d; p; }' "$f" 2>/dev/null)
    if [[ -n "$actions" ]]; then
        echo "**Actions:**"
        echo "$actions"
        echo ""
    fi
done
```

- [ ] **Step 2: Make executable**

```bash
chmod +x scripts/productivity/sections/research-highlights.sh
```

- [ ] **Step 3: Add section call to daily_today.sh**

In `scripts/productivity/daily_today.sh`, in the `generate_daily()` function, add the research highlights call after the `learning-outcomes.sh` line (line 61):

Find this block:
```bash
        run_section learning-outcomes.sh   "$WORKSPACE_ROOT"
        run_section data-health.sh        "$WORKSPACE_ROOT"
```

Replace with:
```bash
        run_section learning-outcomes.sh   "$WORKSPACE_ROOT"
        run_section research-highlights.sh "$WORKSPACE_ROOT"
        run_section data-health.sh        "$WORKSPACE_ROOT"
```

- [ ] **Step 4: Test section script standalone**

Run: `bash scripts/productivity/sections/research-highlights.sh /mnt/local-analysis/workspace-hub`

Expected: Output showing "No new research from last night." (since no research files exist yet).

- [ ] **Step 5: Commit**

```bash
git add scripts/productivity/sections/research-highlights.sh scripts/productivity/daily_today.sh
git commit -m "feat(1434): add research highlights to morning summary"
```

---

### Task 5: Install crontab entry and end-to-end test

**Files:**
- No new files — uses existing `setup-cron.sh`

- [ ] **Step 1: Dry-run the crontab installer**

Run: `bash scripts/cron/setup-cron.sh --dry-run`

Expected: Output includes the new `gsd-researcher` entry at `35 1 * * *`.

- [ ] **Step 2: Install crontab**

Run: `bash scripts/cron/setup-cron.sh`

Expected: New entry installed. Verify with `crontab -l | grep gsd-researcher`.

- [ ] **Step 3: End-to-end dry-run test**

Run: `bash scripts/cron/gsd-researcher-nightly.sh --dry-run`

Expected output:
```
[gsd-researcher] HH:MM:SS Starting nightly research
[gsd-researcher] HH:MM:SS Domain: <domain> (day=N)
[gsd-researcher] HH:MM:SS DRY RUN — would call claude with domain=<domain>
[gsd-researcher] HH:MM:SS Context length: NNNN chars
[gsd-researcher] HH:MM:SS Output would go to: .planning/research/YYYY-MM-DD-<domain>.md
```

- [ ] **Step 4: Manual live test (optional — costs tokens)**

Run: `bash scripts/cron/gsd-researcher-nightly.sh`

Expected: Creates `.planning/research/2026-03-25-<domain>.md` with structured findings, commits and pushes.

- [ ] **Step 5: Close the GitHub issue**

Run: `gh issue comment 1434 --body "Implementation complete. Nightly researcher running at 1:35 AM, morning summary integration added. First research will appear tomorrow."`
