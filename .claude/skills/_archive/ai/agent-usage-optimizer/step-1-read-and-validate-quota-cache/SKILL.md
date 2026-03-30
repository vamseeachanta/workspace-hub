---
name: agent-usage-optimizer-step-1-read-and-validate-quota-cache
description: "Sub-skill of agent-usage-optimizer: Step 1 \u2014 Read and Validate\
  \ Quota Cache."
version: 1.0.0
category: ai
type: reference
scripts_exempt: true
---

# Step 1 — Read and Validate Quota Cache

## Step 1 — Read and Validate Quota Cache


```bash
QUOTA_FILE="$HOME/.cache/agent-quota.json"

# Check cache exists and is fresh (< 1 hour old)
if [[ ! -f "$QUOTA_FILE" ]]; then
  echo "WARN: quota cache not found at $QUOTA_FILE"
  echo "Run: bash scripts/monitoring/query-quota.sh"
  echo "Falling back to default routing rules."
  CACHE_FRESH=false
else
  CACHE_AGE_SECS=$(( $(date +%s) - $(date -r "$QUOTA_FILE" +%s) ))
  if [[ $CACHE_AGE_SECS -gt 3600 ]]; then
    echo "WARN: quota cache is $(( CACHE_AGE_SECS / 60 ))m old — consider refreshing"
    CACHE_FRESH=false
  else
    CACHE_FRESH=true
  fi
fi

# Parse quota values (requires jq)
CLAUDE_PCT=$(jq -r '.agents[] | select(.provider=="claude") | .pct_remaining' "$QUOTA_FILE" 2>/dev/null || echo 100)
CODEX_PCT=$(jq  -r '.agents[] | select(.provider=="codex")  | .pct_remaining' "$QUOTA_FILE" 2>/dev/null || echo 100)
GEMINI_PCT=$(jq -r '.agents[] | select(.provider=="gemini") | .pct_remaining' "$QUOTA_FILE" 2>/dev/null || echo 100)
CACHE_TS=$(jq  -r '.timestamp' "$QUOTA_FILE" 2>/dev/null || echo "unknown")
```
