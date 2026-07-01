#!/usr/bin/env bash
# ecosystem-data-nudge.sh — UserPromptSubmit hook (#801)
# When a prompt mentions an engineering domain, emit ONE line pointing to the
# ecosystem data-source catalog + the ecosystem-data-sources skill, so a session
# proactively surfaces available data instead of the user re-prompting.
#
# Contract (verified against skill-nudge-start.sh): read hook JSON on stdin,
# echo context to STDOUT, exit 0. NEVER block the prompt. Fail-open.
# Fires at most once per domain per session (keyed on session_id).
set -uo pipefail

WS="${WORKSPACE_HUB:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." 2>/dev/null && pwd)}"
MAP="${WS}/.claude/hooks/ecosystem-domain-map.json"

# Fail-open: no map or no jq -> silently do nothing.
command -v jq >/dev/null 2>&1 || exit 0
[[ -f "$MAP" ]] || exit 0

INPUT="$(cat 2>/dev/null || true)"
PROMPT="$(printf '%s' "$INPUT" | jq -r '.prompt // empty' 2>/dev/null)"
SID="$(printf '%s' "$INPUT" | jq -r '.session_id // "nosession"' 2>/dev/null)"
[[ -n "$PROMPT" ]] || exit 0

# lower-case the prompt for matching
PROMPT_LC="$(printf '%s' "$PROMPT" | tr '[:upper:]' '[:lower:]')"
# State dir is injectable for test isolation; production defaults to /tmp
# (session_id is globally unique per session, so the once-per-session key is safe).
STATE_DIR="${ECOSYSTEM_NUDGE_STATE_DIR:-/tmp}"
STATE="${STATE_DIR}/claude-${SID}-ecodomains"
touch "$STATE" 2>/dev/null || true

# Iterate domains; on first keyword hit not yet fired this session, emit + record.
while IFS= read -r domain; do
    # already surfaced this domain this session?
    grep -qxF "$domain" "$STATE" 2>/dev/null && continue
    # collect this domain's keywords, match on word boundary
    matched=""
    while IFS= read -r kw; do
        [[ -z "$kw" ]] && continue
        if printf '%s' "$PROMPT_LC" | grep -qiE "(^|[^a-z0-9])$(printf '%s' "$kw" | sed 's/[.[\*^$()+?{|]/\\&/g')([^a-z0-9]|$)" 2>/dev/null; then
            matched="$kw"; break
        fi
    done < <(jq -r --arg d "$domain" '.domains[$d].keywords[]?' "$MAP" 2>/dev/null)

    if [[ -n "$matched" ]]; then
        repo="$(jq -r --arg d "$domain" '.domains[$d].repo_home // ""' "$MAP" 2>/dev/null)"
        prec="$(jq -r --arg d "$domain" '.domains[$d].has_ace_share_precedent' "$MAP" 2>/dev/null)"
        extra=""
        [[ "$prec" == "true" ]] && extra=" Latent ACE_SHARE precedent exists (metadata-only)."
        echo "[ecosystem-data] This looks like **${domain}** work (home: ${repo:-?}). We likely already have data — see llm-wiki \`data/domain-database-index.yml\` and invoke the \`ecosystem-data-sources\` skill for sources + the domain-database issue.${extra}"
        echo "$domain" >> "$STATE" 2>/dev/null || true
        exit 0
    fi
done < <(jq -r '.domains | keys[]' "$MAP" 2>/dev/null)

exit 0
