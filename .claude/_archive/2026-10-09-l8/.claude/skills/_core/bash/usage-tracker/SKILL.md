---
name: usage-tracker
version: 1.0.0
description: Track and analyze usage metrics with timestamped logging, reporting,
  and trend detection
author: workspace-hub
category: _core
tags:
- bash
- metrics
- logging
- analytics
- tracking
- reporting
platforms:
- linux
- macos
see_also:
- usage-tracker-1-basic-usage-logging
- usage-tracker-3-usage-summary-reports
- usage-tracker-5-trend-analysis
- usage-tracker-best-practices
---

# Usage Tracker

## When to Use This Skill

✅ **Use when:**
- Need to track tool/resource usage over time
- Generating usage reports (daily, weekly, monthly)
- Monitoring quotas or limits
- Analyzing usage patterns
- Building dashboards

❌ **Avoid when:**
- Real-time metrics (use proper monitoring tools)
- High-frequency events (>100/second)
- Sensitive data without encryption

## Summary

$(generate_summary "$period" | sed 's/\x1b\[[0-9;]*m//g')

## Daily Breakdown

| Date | Opus | Sonnet | Haiku | Total |
|------|------|--------|-------|-------|
EOF

    for i in $(seq 6 -1 0); do
        local date=$(date -d "$i days ago" +%Y-%m-%d)
        local opus=$(grep "$date" "$USAGE_LOG" | grep "|opus|" | wc -l)
        local sonnet=$(grep "$date" "$USAGE_LOG" | grep "|sonnet|" | wc -l)
        local haiku=$(grep "$date" "$USAGE_LOG" | grep "|haiku|" | wc -l)
        local total=$((opus + sonnet + haiku))

        echo "| $date | $opus | $sonnet | $haiku | $total |" >> "$output"
    done

    cat >> "$output" << EOF

## Recommendations

Based on current usage patterns:
$(generate_recommendations)

---
Generated: $(date)
EOF

    echo "Report generated: $output"
}
```

## Complete Example: Usage Monitor CLI

```bash
#!/bin/bash
# ABOUTME: Complete usage monitoring CLI tool
# ABOUTME: Track, analyze, and report on usage metrics

set -e

# ─────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────

SCRIPT_NAME="usage-monitor"
USAGE_DIR="${HOME}/.${SCRIPT_NAME}"
USAGE_LOG="$USAGE_DIR/usage.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# ─────────────────────────────────────────────────────────────────
# Core Functions

*See sub-skills for full details.*

## Resources

- [awk One-Liners](https://catonmat.net/awk-one-liners-explained-part-one)
- [sed/awk Tutorial](https://www.grymoire.com/Unix/Awk.html)
- [Date Manipulation in Bash](https://www.cyberciti.biz/faq/linux-unix-formatting-dates-for-display/)

---

## Version History

- **1.0.0** (2026-01-14): Initial release - extracted from workspace-hub check_claude_usage.sh

## Sub-Skills

- [1. Basic Usage Logging (+1)](1-basic-usage-logging/SKILL.md)
- [3. Usage Summary Reports (+1)](3-usage-summary-reports/SKILL.md)
- [5. Trend Analysis (+1)](5-trend-analysis/SKILL.md)
- [Best Practices](best-practices/SKILL.md)
