# Enhanced Model Selection with Usage Awareness

> **Version:** 2.0.0
> **Status:** Production-ready
> **Last Updated:** 2025-01-11

## Overview

The enhanced model selection system recommends Claude models (Opus, Sonnet, Haiku) based on **task complexity AND real-time usage constraints**. It prevents bottlenecks by:

1. **Checking current usage** (combination cache + on-demand)
2. **Hard blocking at 80%+** usage (no recommendations for blocked models)
3. **Falling back to lowest-usage** model if ideal is blocked
4. **Estimating time to reset** if all models are blocked
5. **Logging all decisions** for audit trail and tracking

## Architecture

```
scripts/monitoring/
├── suggest_model.sh              # Main orchestrator (enhanced)
├── lib/
│   ├── usage_tracker.sh          # Manage tracking JSON + recommendations log
│   ├── usage_checker.sh          # Get current usage (cache + on-demand)
│   ├── model_filter.sh           # Hard block at 80% enforcement
│   └── recommender.sh            # Find best available or fallback
├── logs/
│   └── recommendations.jsonl     # Audit trail of all recommendations
└── MODEL_SELECTION_ENHANCED.md   # This file
```

## Configuration

### Usage Tracking File

Location: `/mnt/github/workspace-hub/config/model_usage.json`

Format:
```json
{
  "timestamp": "2025-01-11T10:30:00Z",
  "opus": 45,
  "sonnet": 78,
  "haiku": 32,
  "session_started": "2025-01-11T08:00:00Z"
}
```

### Cache Management

- **Cache max age:** 1 hour (configurable via `CACHE_MAX_AGE`)
- **Cache strategy:** Use cached data if <1 hour old, otherwise prompt for manual refresh
- **Manual refresh:** User prompted when cache is stale
- **Data source:** https://claude.ai/settings/usage

### Hard Block Threshold

- **Threshold:** 80% usage
- **Behavior:** Models at ≥80% are completely blocked from recommendation
- **Fallback:** Automatically recommends lowest-usage available model
- **All blocked:** Recommends lowest-usage model overall + time to reset

## Usage

### Basic Usage

```bash
./scripts/monitoring/suggest_model.sh <repository> "<task description>"
```

**Examples:**

```bash
# Interactive mode
./scripts/monitoring/suggest_model.sh

# Direct mode with arguments
./scripts/monitoring/suggest_model.sh digitalmodel "Implement user authentication system"
./scripts/monitoring/suggest_model.sh energy "Fix bug in data loader"
./scripts/monitoring/suggest_model.sh hobbies "Quick status check"
```

### Minimal Output Format

The script outputs minimal format (as requested):

```
═══════════════════════════════════════
  Model Recommendation
═══════════════════════════════════════

Repository: digitalmodel (Work Tier 1 (Production))
Task: Implement user authentication system
Complexity: 3

Recommended: OPUS

Current Usage Status:
  Opus:   45% ✅ Available
  Sonnet: 78% ⚠️  Limited availability
  Haiku:  32% ✅ Available

Capacity Status (Hard Block at 80%):
  Opus:   45% ✅ Available
  Sonnet: 78% ✅ Available
  Haiku:  32% ✅ Available

═══════════════════════════════════════

Use this recommendation? (y/n):
```

### With Fallback Warning

If ideal model is blocked:

```
Recommended: HAIKU
⚠️  Ideal blocked, using lowest available
```

If all models blocked:

```
Recommended: OPUS
⚠️  All models at capacity (>80%)
Reset in: 2h 15m (Tuesday 4 PM ET)
```

## Modular Components

### 1. Usage Tracker (`lib/usage_tracker.sh`)

Manages persistent usage data and recommendation logging.

**Commands:**

```bash
# Initialize tracking file
bash lib/usage_tracker.sh init

# Get cached usage
bash lib/usage_tracker.sh get

# Check if cache is valid
bash lib/usage_tracker.sh is-valid

# Update usage percentages
bash lib/usage_tracker.sh update 45 78 32

# Log a recommendation decision
bash lib/usage_tracker.sh log-recommendation "digitalmodel" "auth task" 3 "opus" '{"opus":45,...}'

# Get today's stats
bash lib/usage_tracker.sh today-stats
```

**Output examples:**

```bash
$ bash lib/usage_tracker.sh get
{
  "timestamp": "2025-01-11T10:30:00Z",
  "opus": 45,
  "sonnet": 78,
  "haiku": 32,
  "session_started": "2025-01-11T08:00:00Z"
}
```

### 2. Usage Checker (`lib/usage_checker.sh`)

Gets current usage with combination cache + on-demand strategy.

**Commands:**

```bash
# Get current usage (cache if valid, prompt if stale)
bash lib/usage_checker.sh get

# Display usage with status indicators
bash lib/usage_checker.sh display

# Get available models (not at 80%+)
bash lib/usage_checker.sh available-models

# Get lowest usage model
bash lib/usage_checker.sh lowest-available

# Minutes until weekly reset
bash lib/usage_checker.sh time-to-reset

# All stats
bash lib/usage_checker.sh all
```

**Output examples:**

```bash
$ bash lib/usage_checker.sh display

Current Claude Usage Status:
  Opus:   45% ✅ Available
  Sonnet: 78% ⚠️  Limited availability
  Haiku:  32% ✅ Available

$ bash lib/usage_checker.sh available-models
opus
haiku

$ bash lib/usage_checker.sh time-to-reset
135
```

### 3. Model Filter (`lib/model_filter.sh`)

Enforces hard block at 80% and filters available models.

**Commands:**

```bash
# Filter available models (those not at 80%+)
bash lib/model_filter.sh filter [preferred_model]

# Get status of specific model
bash lib/model_filter.sh status <model>

# Get all model statuses
bash lib/model_filter.sh all-status

# Display capacity status
bash lib/model_filter.sh display

# Check if all models are blocked
bash lib/model_filter.sh check-blocked

# Count available models
bash lib/model_filter.sh count-available
```

**Output examples:**

```bash
$ bash lib/model_filter.sh filter
opus
haiku

$ bash lib/model_filter.sh all-status
{"opus": "available", "sonnet": "blocked", "haiku": "available"}

$ bash lib/model_filter.sh display

Capacity Status (Hard Block at 80%):
  Opus:   45% ✅ Available
  Sonnet: 78% ✅ Available
  Haiku:  32% ✅ Available
```

### 4. Recommender (`lib/recommender.sh`)

Recommends best available model or lowest-usage fallback.

**Commands:**

```bash
# Get recommendation as JSON
bash lib/recommender.sh get <complexity> <repo> <task>

# Display minimal recommendation
bash lib/recommender.sh display-minimal <complexity> <repo> <task>

# Display detailed recommendation
bash lib/recommender.sh display-detailed <complexity> <repo> <task>

# Get specific field from recommendation
bash lib/recommender.sh field <complexity> <repo> <task> <field>
```

**Output examples:**

```bash
$ bash lib/recommender.sh get 3 "digitalmodel" "Design auth system"
{
  "recommended_model": "opus",
  "ideal_model": "opus",
  "complexity_score": 3,
  "ideal_available": true,
  "fallback_reason": "none",
  "time_to_reset_minutes": 0
}

$ bash lib/recommender.sh display-minimal 3 "digitalmodel" "Design auth system"
OPUS

$ bash lib/recommender.sh field 3 "digitalmodel" "Design auth system" "recommended_model"
opus
```

## Decision Logic

### Complexity Scoring

| Factor | Score | Examples |
|--------|-------|----------|
| **Keywords** | +3 to -2 | architecture, refactor, design (Opus); implement, feature, bug (Sonnet); check, quick, status (Haiku) |
| **Word Count** | +1 to -1 | >15 words (+1); <5 words (-1) |
| **Repository Tier** | +1 to -1 | Work Tier 1 (+1); Personal Experimental (-1) |

### Model Selection

**Priority order:**
1. Check if ideal model is available (<80%)
2. If blocked, use lowest-usage available model
3. If all blocked (≥80%), recommend lowest-usage model overall + show time to reset

### Examples

| Complexity | Usage | Ideal | Available | Decision |
|-----------|-------|-------|-----------|----------|
| 3 (Opus) | O:45%, S:78%, H:32% | Opus | ✅ Yes | **OPUS** ✅ |
| 3 (Opus) | O:82%, S:78%, H:32% | Opus | ❌ No | **HAIKU** ⚠️ (lowest) |
| 3 (Opus) | O:82%, S:85%, H:92% | Opus | ❌ All blocked | **OPUS** 🔴 (lowest of blocked) |
| 1 (Sonnet) | O:45%, S:78%, H:32% | Sonnet | ✅ Yes | **SONNET** ✅ |
| 1 (Sonnet) | O:45%, S:82%, H:32% | Sonnet | ❌ No | **OPUS** ⚠️ (lowest available) |
| -2 (Haiku) | O:45%, S:78%, H:92% | Haiku | ❌ No | **OPUS** ⚠️ (lowest available) |

## Data Files

### Tracking File
- **Path:** `/mnt/github/workspace-hub/config/model_usage.json`
- **Format:** JSON with timestamp, usage %, session info
- **Updated:** On-demand when cache is stale
- **Retention:** Persistent (not auto-cleared)

### Recommendations Log
- **Path:** `/mnt/github/workspace-hub/scripts/monitoring/logs/recommendations.jsonl`
- **Format:** JSONL (one JSON object per line)
- **Contents:** Timestamp, repo, task, complexity, recommendation, usage at time
- **Purpose:** Audit trail and historical tracking
- **Retention:** Indefinite (for analysis)

### Example Recommendation Log Entry

```json
{
  "timestamp": "2025-01-11T10:30:00Z",
  "repository": "digitalmodel",
  "task": "Implement user authentication system...",
  "complexity_score": 3,
  "recommended_model": "opus",
  "usage_at_time": {"opus": 45, "sonnet": 78, "haiku": 32}
}
```

## Integration Points

### With Existing Tools

1. **check_claude_usage.sh:** Logs recommendations to existing usage tracking
2. **CLAUDE.md:** Reference model selection flow in project config
3. **AI_USAGE_GUIDELINES.md:** Document recommends using this tool

### Workflow Integration

**Ideal workflow:**

```bash
# 1. Before starting work, get model recommendation
./scripts/monitoring/suggest_model.sh digitalmodel "Implement authentication"

# 2. Tool shows: OPUS (available)
# 3. Use the recommended model for your task
# 4. After using Claude, optionally log tokens

# Later, if you check again:
./scripts/monitoring/suggest_model.sh digitalmodel "Quick fix"

# 2. Tool shows: HAIKU (Sonnet blocked at 82%)
# 3. Use HAIKU instead to balance usage
```

## Customization

### Change Cache Age

```bash
export CACHE_MAX_AGE=7200  # 2 hours instead of 1
./scripts/monitoring/suggest_model.sh ...
```

### Change Block Threshold

Edit `lib/model_filter.sh`:
```bash
CAPACITY_THRESHOLD=85  # Block at 85% instead of 80%
```

### Change Repository Tiers

Edit `suggest_model.sh`:
```bash
WORK_TIER1="your-prod-repos"
PERSONAL_ACTIVE="your-personal"
# ...
```

## Troubleshooting

### "Usage cache is stale" Prompt

- **Cause:** Tracking file is >1 hour old
- **Action:** Enter current usage from https://claude.ai/settings/usage
- **Alternative:** Manually update file: `bash lib/usage_tracker.sh update 45 78 32`

### Empty Usage JSON

- **Cause:** Tracking file not initialized
- **Fix:** `bash lib/usage_tracker.sh init`

### Models showing as "blocked" incorrectly

- **Cause:** Stale data in tracking file
- **Fix:** Get fresh usage: `bash lib/usage_checker.sh get` (will prompt for manual entry)

### Script permission errors

- **Cause:** Scripts not executable
- **Fix:** `chmod +x /mnt/github/workspace-hub/scripts/monitoring/lib/*.sh`

## Performance

- **Speed:** <1 second for recommendation (cache hit)
- **Cache update:** ~5 seconds if manual entry required
- **Logging:** ~0.1 seconds per recommendation

## Security Notes

- ✅ No passwords/secrets stored
- ✅ Usage percentages only (not raw token counts)
- ✅ JSONL format safe for git (add `logs/` to `.gitignore` if needed)
- ✅ No external API calls (offline-capable once cached)

## Testing

### Manual Testing

```bash
# Test 1: Normal recommendation
./scripts/monitoring/suggest_model.sh digitalmodel "Design complex system"

# Test 2: Interactive mode
./scripts/monitoring/suggest_model.sh

# Test 3: Direct helper usage
bash scripts/monitoring/lib/usage_checker.sh all
bash scripts/monitoring/lib/model_filter.sh display

# Test 4: Simulate all models blocked (edit JSON manually for testing)
```

### Automated Testing (Future)

Add to CI/CD pipeline:
```bash
# Verify all scripts are executable
for script in scripts/monitoring/lib/*.sh; do
    [ -x "$script" ] || echo "Not executable: $script"
done

# Run basic commands
bash scripts/monitoring/lib/usage_tracker.sh init
bash scripts/monitoring/lib/usage_checker.sh get > /dev/null
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2025-01-11 | Complete modular rewrite with usage awareness |
| 1.0.0 | 2025-01-09 | Original complexity-based recommendation |

## Next Steps

1. **Initialize tracking:** `bash lib/usage_tracker.sh init`
2. **Test basic flow:** `./suggest_model.sh digitalmodel "test task"`
3. **Integrate into workflow:** Add to CLAUDE.md and documentation
4. **Monitor usage:** Check `/logs/recommendations.jsonl` for patterns
5. **Iterate:** Adjust thresholds and keywords based on experience

---

**Questions?** See the inline script documentation:
```bash
bash lib/usage_tracker.sh          # See usage options
bash lib/usage_checker.sh all      # Display full status
```
