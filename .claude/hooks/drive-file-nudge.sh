#!/usr/bin/env bash
# drive-file-nudge.sh — UserPromptSubmit hook (#3339, epic #3333)
# Sibling of ecosystem-data-nudge.sh (the "#801 pattern": same contract,
# different matching engine). When a prompt shows file-seeking intent
# (Tier 1: strong multiword phrases) or an engineering-domain + artifact
# co-occurrence (Tier 2), emit ONE context line pointing at the
# drive-file-search skill (#3338) with the dated drive-index coverage fact,
# so prior project files get surfaced before the session rebuilds from
# scratch.
#
# Contract (identical to ecosystem-data-nudge.sh): hook JSON on stdin
# (.prompt / .session_id), ONE line on stdout, exit 0 ALWAYS, fail-open
# (no jq / no map -> silent exit 0). Fires at most ONCE per session:
# state key claude-<sid>-drivefile in ${DRIVE_NUDGE_STATE_DIR:-/tmp}.
#
# Latency (plan D4/F3, budget <50 ms): SINGLE-PASS matcher — exactly ONE jq
# spawn per prompt: stdin parse + config read ride the same invocation
# (drive-file-map.json + ecosystem-domain-map.json via --slurpfile; the
# alternation strings are precomputed in the map at authoring time). The
# alternation passes themselves run as bash builtin [[ =~ ]] ERE matches
# (zero extra process spawns — the same regexes the plan's grep passes would
# use, hardened for loaded hosts). Total per prompt: bash + 1 jq.
# Deliberately NOT #801's per-domain/per-keyword grep loop (measured
# 270-460 ms there — over budget; do not copy it back in).
#
# Trigger tiers (plan D2, adversarial review F2/F5/F7):
#   Tier 1 fires alone: strong multiword file-seeking phrases only.
#   Tier 2 requires eco-domain keyword co-occurrence (domains reused at
#     runtime from ecosystem-domain-map.json; Tier 2 degrades OFF if that
#     map is absent) AND (demoted intent phrase OR artifact noun), with
#     software compounds ("ci pipeline", ...) discounted from domain hits.
#   DATA-shaped asks (do we have data|data for|data on) are carved out of
#     BOTH tiers and left to #801's DATA-level nudge (plan D7).
set -uo pipefail

WS="${WORKSPACE_HUB:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." 2>/dev/null && pwd)}"
MAP="${WS}/.claude/hooks/drive-file-map.json"
ECO="${WS}/.claude/hooks/ecosystem-domain-map.json"   # optional: Tier 2 only

# Fail-open: no jq or no map -> silently do nothing.
command -v jq >/dev/null 2>&1 || exit 0
[[ -f "$MAP" ]] || exit 0

INPUT=""
IFS= read -r -d '' INPUT || true   # builtin stdin slurp (no cat spawn)

# THE single jq spawn (plan D4/F3): parses stdin (sanitized session id +
# lower-cased prompt with control chars -- incl. newlines -- flattened to
# spaces, so the line-based splitting below is safe) AND emits all config in
# the same invocation: precomputed alternation strings from MAP
# (authoring-time joins; list fallback kept for robustness) plus the eco-map
# domain-keyword alternation ($eco is [] when that map is absent ->
# DOMAIN_RE empty -> Tier 2 degrades off). Malformed or empty stdin -> jq
# emits nothing -> exit 0 (and no state file is written).
ECO_ARGS=(--argjson eco '[]')
[[ -f "$ECO" ]] && ECO_ARGS=(--slurpfile eco "$ECO")
CFG="$(printf '%s' "$INPUT" | jq -r --slurpfile m "$MAP" "${ECO_ARGS[@]}" '
    def esc: gsub("(?<c>[.\\[\\\\*^$()+?{|])"; "\\" + .c);
    $m[0] as $map |
    ((.session_id // "nosession") | tostring | gsub("[^a-zA-Z0-9._-]"; "-")),
    ((.prompt // "") | tostring | ascii_downcase | gsub("[[:cntrl:]]"; " ")),
    ($map.precomputed.tier1_re // (($map.tier1_intent_phrases // []) | map(esc) | join("|"))),
    ($map.precomputed.tier2_re // (($map.tier2_intent_phrases // []) | map(esc) | join("|"))),
    ($map.precomputed.artifact_re // (($map.artifact_nouns // []) | map(esc) | join("|"))),
    ($map.precomputed.data_ask_re // (($map.data_ask_exclusions // []) | map(esc) | join("|"))),
    ($map.precomputed.software_context_exclusions_re // (($map.software_context_exclusions // []) | map(esc) | join("|"))),
    ([$eco[0].domains[]?.keywords[]?] | unique | map(esc) | join("|")),
    ($map.coverage_fallback.ace // "?"),
    ($map.coverage_fallback.dde // "?"),
    ($map.coverage_fallback.as_of // "unknown"),
    ($map.skill_ref // "drive-file-search (#3338)")
  ' 2>/dev/null)" || true
[[ -n "$CFG" ]] || exit 0
mapfile -t C <<< "$CFG"
(( ${#C[@]} >= 12 )) || exit 0
SID="${C[0]}"; PROMPT_LC="${C[1]}"
TIER1_RE="${C[2]}"; TIER2_RE="${C[3]}"; ARTIFACT_RE="${C[4]}"
DATA_ASK_RE="${C[5]}"; SW_EXCL_RE="${C[6]}"; DOMAIN_RE="${C[7]}"
ACE="${C[8]}"; DDE="${C[9]}"; AS_OF="${C[10]}"; SKILL_REF="${C[11]}"
[[ -n "$PROMPT_LC" ]] || exit 0
[[ -n "$SID" ]] || SID="nosession"

# Once per session: a single builtin stat -- every prompt after the first
# fire exits here (post-fire cost stays bash + 1 jq, like any other prompt).
STATE_DIR="${DRIVE_NUDGE_STATE_DIR:-/tmp}"
STATE="${STATE_DIR}/claude-${SID}-drivefile"
[[ -f "$STATE" ]] && exit 0

B='(^|[^a-z0-9])'
E='([^a-z0-9]|$)'

# All alternation matches below are bash builtin [[ =~ ]] ERE (prompt and
# patterns are already lower-cased) — zero process spawns on the match path.

# DATA-ask carve-out (plan D7): DATA-shaped asks are excluded from BOTH tiers
# and route to #801's DATA-level nudge only.
RE="${B}(${DATA_ASK_RE})${E}"
if [[ -n "$DATA_ASK_RE" ]] && [[ "$PROMPT_LC" =~ $RE ]]; then
    exit 0
fi

FIRE=0
RE="${B}(${TIER1_RE})${E}"
if [[ -n "$TIER1_RE" ]] && [[ "$PROMPT_LC" =~ $RE ]]; then
    # Tier 1: strong multiword file-seeking phrase fires alone.
    FIRE=1
elif [[ -n "$DOMAIN_RE" ]]; then
    # Tier 2: eco-domain keyword AND (demoted intent phrase OR artifact noun).
    # Domain hits inside software compounds are discounted first (plan D2/F7:
    # "ci pipeline" etc. must not count as a pipeline-domain hit).
    PROMPT_DOM="$PROMPT_LC"
    if [[ -n "$SW_EXCL_RE" ]]; then
        RE="(${SW_EXCL_RE})"
        n=0
        while (( n < 20 )) && [[ "$PROMPT_DOM" =~ $RE ]]; do
            PROMPT_DOM="${PROMPT_DOM/"${BASH_REMATCH[0]}"/ }"
            n=$(( n + 1 ))
        done
    fi
    T2A="${TIER2_RE}"
    [[ -n "$TIER2_RE" && -n "$ARTIFACT_RE" ]] && T2A="${TIER2_RE}|${ARTIFACT_RE}"
    [[ -z "$TIER2_RE" ]] && T2A="${ARTIFACT_RE}"
    DRE="${B}(${DOMAIN_RE})${E}"
    TRE="${B}(${T2A})${E}"
    if [[ -n "$T2A" ]] && [[ "$PROMPT_DOM" =~ $DRE ]] && [[ "$PROMPT_LC" =~ $TRE ]]; then
        FIRE=1
    fi
fi
[[ "$FIRE" == "1" ]] || exit 0

# Coverage fact comes ONLY from the dated map fallback in v1 (plan D3/F1 —
# the #3335 registry schema carries no row counts). as_of date + dde
# staleness softener are REQUIRED content (plan F6).
echo "[drive-file] This prompt suggests prior work may exist on the shared drives (${ACE} /mnt/ace + ${DDE} /mnt/dde files indexed as of ${AS_OF} - dde coverage may be stale, see #3334). Invoke the ${SKILL_REF} skill (.claude/skills/data/drive-file-search) to surface related files before building from scratch." # abs-path-allowed
# Record the once-per-session state via builtin redirect (no touch spawn on
# the common path); fall back to mkdir -p for a not-yet-created state dir.
{ : > "$STATE"; } 2>/dev/null \
    || { mkdir -p "$STATE_DIR" && : > "$STATE"; } 2>/dev/null \
    || true
exit 0
