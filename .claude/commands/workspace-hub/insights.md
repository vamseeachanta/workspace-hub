# /insights - Claude-Native Session Analysis

Generate comprehensive reports analyzing your Claude Code sessions. This skill uses Claude's native capabilities to analyze session data, corrections, and patterns.

## Usage

```bash
/insights                    # Analyze today's sessions
/insights --day YYYY-MM-DD   # Analyze specific day
/insights --week             # Weekly summary (last 7 days)
/insights --session <id>     # Analyze specific session
```

## Instructions

You are a session analysis expert. Your job is to analyze Claude Code session data and produce actionable insights.

### Step 1: Gather Session Data

Read the relevant session data based on the command:

**For today's sessions:**
```bash
# List today's session reports
ls -la "$WORKSPACE_ROOT/.claude/state/session-reports/session_$(date +%Y%m%d)_*.md" 2>/dev/null

# Read today's corrections
cat "$WORKSPACE_ROOT/.claude/state/corrections/session_$(date +%Y%m%d).jsonl" 2>/dev/null

# Get recent sessions from state
cat "$WORKSPACE_ROOT/.claude/state/sessions/"*.json 2>/dev/null | tail -5000
```

**For specific day (--day YYYY-MM-DD):**
```bash
DATE_STAMP=$(echo "YYYY-MM-DD" | tr -d '-')
ls -la "$WORKSPACE_ROOT/.claude/state/session-reports/session_${DATE_STAMP}_*.md"
cat "$WORKSPACE_ROOT/.claude/state/corrections/session_${DATE_STAMP}.jsonl"
```

**For weekly (--week):**
```bash
# Last 7 days of daily summaries
ls -la "$WORKSPACE_ROOT/.claude/state/daily-summaries/daily_summary_*.md" | tail -7
```

### Step 2: Analyze Patterns

Look for these key patterns in the data:

1. **Delegation Score**: Percentage of Task tool usage vs direct execution
   - High (>60%): Good orchestrator pattern compliance
   - Medium (30-60%): Improvement opportunity
   - Low (<30%): Needs coaching on delegation

2. **Correction Patterns**: Rapid re-edits to same file
   - Gap <60s: Quick fix (typos, syntax)
   - Gap 60-300s: Iterative refinement
   - Gap >300s: Delayed realization

3. **Tool Distribution**: Which tools are used most
   - Read/Grep/Glob: Research-heavy session
   - Edit/Write: Implementation session
   - Bash: Operations/testing session
   - Task: Well-delegated session

4. **Error Patterns**: Common mistakes
   - Syntax errors in specific file types
   - Missing imports
   - Path issues

5. **Engineering Audit**: Scan for keywords like `wall_thickness`, `fatigue`, `metocean`, `design_code`, `sn_curve`.
   - If detected, extract inputs (e.g., `wt=0.05`), results, and design code.
   - Generate a YAML audit record in `.claude/state/engineering-audit/audit_<SESSION_ID>.yaml`.

6. **Data Provenance**: Scan for data file operations (Read/Write to CSV, XLSX, etc.).
   - Record data source, processing steps, and destination in `.claude/state/provenance/prov_<SESSION_ID>.yaml`.

### Step 3: Generate Report

Produce a markdown report with these sections:

```markdown
# Insights Report: [Date Range]

## Executive Summary
[2-3 sentence overview of session activity and quality]

## Quick Stats

| Metric | Value | Trend |
|--------|-------|-------|
| Sessions | N | ↑/↓/→ |
| Total Duration | Xh Ym | |
| Tool Calls | N | |
| Corrections | N | |
| Delegation Score | X% | |

## Session Timeline

| Time | Duration | Focus | Delegation |
|------|----------|-------|------------|
| HH:MM | Xm | activity | X% |

## Correction Analysis

**Total Corrections:** N
**Most Corrected File Types:** .ext (N)
**Average Gap:** Xs

### Patterns Detected
- Pattern 1: description
- Pattern 2: description

## Tool Usage Distribution

```
Read:   ████████████ 45%
Edit:   ██████████   35%
Bash:   ████         15%
Task:   ██           5%
```

## Recommendations

1. **[Priority]** Specific actionable recommendation
2. **[Priority]** Another recommendation

## Tomorrow's Focus

Based on today's patterns, consider:
- Focus area 1
- Focus area 2
```

### Step 4: Save Report

Save the generated report:

```bash
# For session report
REPORT_PATH="$WORKSPACE_ROOT/.claude/state/session-reports/session_$(date +%Y%m%d_%H%M%S).md"

# For daily summary
REPORT_PATH="$WORKSPACE_ROOT/.claude/state/daily-summaries/daily_summary_$(date +%Y-%m-%d).md"
```

### Integration with /reflect

The `/insights` skill feeds into the larger reflection system:

```
/insights (Claude-native analysis)
    ↓
Session Reports (.claude/state/session-reports/)
    ↓
Daily Summaries (.claude/state/daily-summaries/)
    ↓
Weekly Digest (via /reflect and generate-report.sh)
```

## Environment Variables

- `WORKSPACE_ROOT`: Base directory (default: /mnt/github/workspace-hub)
- `WORKSPACE_STATE_DIR`: State directory (default: $WORKSPACE_ROOT/.claude/state)

## Examples

**Basic usage:**
```
/insights
```
Output: Analysis of today's sessions with patterns and recommendations.

**Specific day:**
```
/insights --day 2026-02-04
```
Output: Analysis of all sessions from February 4th.

**Weekly summary:**
```
/insights --week
```
Output: Aggregated analysis of the last 7 days with trends.
