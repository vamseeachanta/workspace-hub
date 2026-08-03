#!/usr/bin/env bash
# ABOUTME: Daily log section — AI agent usage summary (usage remaining, tool versions, sessions, models)
# Usage: bash ai-usage-summary.sh <WORKSPACE_ROOT>

set -euo pipefail
WORKSPACE_ROOT="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"
STATUS_FILE="$WORKSPACE_ROOT/config/ai_agents/ai-tools-status.yaml"
PIPELINE_FILE="$WORKSPACE_ROOT/.claude/work-queue/pipeline-state.yaml"
USER_QUOTA_CACHE="$HOME/.cache/agent-quota.json"
WORKSPACE_QUOTA="$WORKSPACE_ROOT/config/ai-tools/agent-quota-latest.json"

echo "## AI Agent Usage Summary"
echo ""

# ── Weekly Usage Remaining (top) ──────────────────────────────────────────────
echo "### Weekly Usage Remaining"
echo ""

# Pick freshest available file (user cache preferred, up to 2h old)
quota_file=""
if [[ -f "$USER_QUOTA_CACHE" ]]; then
    age=$(( $(date +%s) - $(stat -c %Y "$USER_QUOTA_CACHE" 2>/dev/null || echo 0) ))
    (( age < 7200 )) && quota_file="$USER_QUOTA_CACHE"
fi
[[ -z "$quota_file" && -f "$WORKSPACE_QUOTA" ]] && quota_file="$WORKSPACE_QUOTA"

if [[ -n "$quota_file" ]]; then
    uv run --no-project python - "$quota_file" <<'PYEOF'
import json, sys, os, time

with open(sys.argv[1]) as f:
    data = json.load(f)

ts        = data.get("timestamp", "")
src       = os.path.basename(sys.argv[1])
# Use JSON timestamp for age (file mtime can be refreshed by git without data changing)
from datetime import datetime, timezone
try:
    ts_dt = datetime.fromisoformat(ts)
    age = int((datetime.now(timezone.utc) - ts_dt.astimezone(timezone.utc)).total_seconds())
except (ValueError, TypeError):
    age = int(time.time() - os.path.getmtime(sys.argv[1]))
age_label = f"{age//60}m ago" if age < 3600 else f"{age//3600}h ago"
stale     = age > 48 * 3600  # >48 hours = stale
stale_days = age // 86400
if stale:
    age_label = f"⚠ stale ({stale_days}d old)"
print(f"_Source: {src}  |  Updated: {ts} ({age_label})_")
if stale:
    print("")
    print(f"> **⚠ Quota data is {stale_days} days old.** Run `bash scripts/ai/assessment/query-quota.sh` to refresh.")
print("")
print("| Agent | % Used | % Remaining | Bar | Resets In | Notes |")
print("|-------|--------|-------------|-----|-----------|-------|")

BARS  = "▓▓▓▓▓▓▓▓▓▓"
EMPTY = "░░░░░░░░░░"

def bar(pct_used):
    filled = min(10, round(float(pct_used) / 10))
    return BARS[:filled] + EMPTY[filled:]

def hrs_label(entry):
    h = entry.get("hours_to_reset")
    if h is not None:
        return f"{h}h"
    resets = entry.get("resets_at", "")
    return resets[:10] if resets else "—"

def warn(pct_used):
    if pct_used >= 80: return "⚠ high"
    if pct_used >= 50: return "⬆ moderate"
    return ""

for agent in data.get("agents", []):
    prov = agent.get("provider", "?")
    if "week_pct" in agent:
        pct_used  = float(agent["week_pct"] or 0)
        remaining = 100 - pct_used
    else:
        remaining = float(agent.get("pct_remaining") or 0)
        pct_used  = 100 - remaining

    notes = warn(pct_used)
    if stale:
        notes = "⚠ stale" + (f" {notes}" if notes else "")
    if prov == "claude":
        s = agent.get("sonnet_pct")
        if s is not None:
            notes += f" sonnet {s:.0f}% used"
        reqs = agent.get("approx_requests")
        if reqs:
            notes += f" ~{reqs} reqs"

    print(f"| {prov} | {pct_used:.0f}% | {remaining:.0f}% | {bar(pct_used)} | {hrs_label(agent)} | {notes} |")
PYEOF
else
    QUERY_SCRIPT="$WORKSPACE_ROOT/scripts/ai/assessment/query-quota.sh"
    if [[ -x "$QUERY_SCRIPT" ]]; then
        echo "_No cached quota — running query-quota.sh_"
        echo ""
        bash "$QUERY_SCRIPT" 2>/dev/null || echo "_query-quota.sh failed_"
    else
        echo "_No quota data — run: bash scripts/ai/assessment/query-quota.sh_"
    fi
fi
echo ""

# ── Tool Versions ─────────────────────────────────────────────────────────────
echo "### Tool Versions"
echo ""
if [[ -f "$STATUS_FILE" ]]; then
    updated=$(grep "^last_updated:" "$STATUS_FILE" | awk '{print $2}' | tr -d '"')
    echo "_Last checked: ${updated}_"
    echo ""
    echo "| Machine | Node | Claude | Codex | Gemini | gh | Status |"
    echo "|---------|------|--------|-------|--------|----|--------|"
    for host in dev-primary dev-secondary licensed-win-1; do
        hfile="$WORKSPACE_ROOT/config/ai_agents/status/$host.yaml"
        [[ ! -f "$hfile" ]] && continue
        status=$(grep "^status:" "$hfile" | awk '{print $2}')
        node=$(awk   '/^versions:/{f=1} f && /  node:/{   print $2; exit}' "$hfile" | tr -d '"')
        claude=$(awk '/^versions:/{f=1} f && /  claude:/{ print $2; exit}' "$hfile" | tr -d '"')
        codex=$(awk  '/^versions:/{f=1} f && /  codex:/{  print $2; exit}' "$hfile" | tr -d '"')
        gemini=$(awk '/^versions:/{f=1} f && /  gemini:/{ print $2; exit}' "$hfile" | tr -d '"')
        gh=$(awk     '/^versions:/{f=1} f && /  gh:/{     print $2; exit}' "$hfile" | tr -d '"')
        icon="✓"; [[ "$status" == "needs-update" ]] && icon="⚠"; [[ "$status" == "manual-check-required" ]] && icon="?"
        echo "| $host | ${node:----} | ${claude:----} | ${codex:----} | ${gemini:----} | ${gh:----} | $icon $status |"
    done
else
    echo "_Not found — run: bash scripts/maintenance/ai-tools-status.sh_"
fi
echo ""

# ── Active Sessions & Workload ────────────────────────────────────────────────
echo "### Active Sessions & Workload"
echo ""
if [[ -f "$PIPELINE_FILE" ]]; then
    session_count=$(grep -c "session_id:" "$PIPELINE_FILE" 2>/dev/null || echo 0)
    active_wrk=$(grep "active_wrk:" "$PIPELINE_FILE" | awk '{print $2}' | tr -d '"' | grep -v '^$\|null' || true)
    echo "- Registered sessions: $session_count"
    echo "- Active WRK: ${active_wrk:-none}"
else
    echo "_No pipeline state_"
fi
echo ""

# ── Active Provider Config ─────────────────────────────────────────────────────
echo "### Active Provider Config"
echo ""
uv run --no-project python - "$WORKSPACE_ROOT" <<'PYEOF'
import json, sys, re
from pathlib import Path

ws = Path(sys.argv[1])
home = Path.home()

def read_json(p):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}

def read_toml_key(p, key):
    """Extract bare 'key = "value"' from a TOML file (no dependency on tomllib)."""
    try:
        for line in p.read_text(encoding="utf-8").splitlines():
            m = re.match(rf'^\s*{re.escape(key)}\s*=\s*["\']?([^"\'#\n]+)["\']?', line)
            if m:
                return m.group(1).strip().strip('"\'')
    except Exception:
        pass
    return None

# Context windows from config/agents/model-registry.yaml context_windows_k (#3038)
ALIAS_MAP = {
    "fable": "claude-fable-5",
    "opus": "claude-opus-4-8",
    "sonnet": "claude-sonnet-4-6",
    "haiku": "claude-haiku-4-5",
    "gemini 3.1 pro (high)": "gemini-3.1-pro-preview",
    "gemini 3.1 pro": "gemini-3.1-pro-preview",
}

def _load_registry_ctx():
    fallback = {"claude-fable-5": 1000, "claude-sonnet-4-6": 200,
                "claude-opus-4-8": 200, "claude-haiku-4-5": 200,
                "gpt-5.5": 128, "gemini-2.5-pro": 1000}
    try:
        text = (ws / "config/agents/model-registry.yaml").read_text(encoding="utf-8")
    except Exception:
        return fallback
    block = re.search(r"^context_windows_k:\n((?:[ \t]+\S+:[ \t]*\d+.*\n)+)", text, re.MULTILINE)
    if not block:
        return fallback
    out = {m.group(1).lower(): int(m.group(2))
           for m in re.finditer(r"^[ \t]+(\S+):[ \t]*(\d+)", block.group(1), re.MULTILINE)}
    return out or fallback

CTX_MAP = _load_registry_ctx()

def ctx_label(model_alias):
    key = (model_alias or "").lower()
    suffix = re.search(r"\[(\d+)(k|m)\]$", key)
    key = re.sub(r"\[[^\]]*\]$", "", key)
    if suffix:
        return f"{int(suffix.group(1)) * (1000 if suffix.group(2) == 'm' else 1)}K"
    key = ALIAS_MAP.get(key, key)
    return f"{CTX_MAP[key]}K" if key in CTX_MAP else "?"

rows = []

# ── Claude ────────────────────────────────────────────────────────────────────
claude_cfg   = read_json(home / ".claude/settings.json")
claude_alias = claude_cfg.get("model") or "not set"
# Check for extended thinking in repo settings
repo_cfg      = read_json(ws / ".claude/settings.json")
thinking_on   = repo_cfg.get("thinking") or claude_cfg.get("thinking")
claude_effort = "thinking=on" if thinking_on else "thinking=off"
rows.append(("claude", claude_alias, ctx_label(claude_alias), claude_effort, "~/.claude/settings.json"))

# ── Codex — repo-local overrides user config ──────────────────────────────────
codex_user  = home / ".codex/config.toml"
codex_repo  = ws / ".codex/config.toml"
codex_src   = codex_repo if codex_repo.exists() else codex_user
codex_model  = read_toml_key(codex_src, "model") or "not set"
codex_effort = read_toml_key(codex_src, "model_reasoning_effort") or "—"
rows.append(("codex", codex_model, ctx_label(codex_model), f"effort={codex_effort}", codex_src.name))

# ── Agy (Antigravity, Gemini-backed — routed third lane since #3573) ─────────
agy_cfg   = read_json(home / ".gemini/antigravity-cli/settings.json")
agy_model = (agy_cfg.get("model") or {}).get("name") or str(agy_cfg.get("model") or "not set")
rows.append(("agy", agy_model, ctx_label(agy_model), "—", "~/.gemini/antigravity-cli/settings.json"))

print("| Provider | Model | Context | Effort/Thinking | Config Source |")
print("|----------|-------|---------|-----------------|---------------|")
for provider, model, ctx, effort, src in rows:
    print(f"| {provider} | {model} | {ctx} | {effort} | {src} |")
PYEOF
