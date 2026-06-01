#!/usr/bin/env bash
# Deckhand — repository protection + token verification (config-driven, reusable)
#
# Single source of truth: config/deckhand/scopes.yml. This script derives the repo
# list and per-scope PAT env-var mapping from that file, so onboarding a new client
# or machine is a YAML edit — NOT a script edit. Do not hardcode repos here.
#
# Subcommands:
#   protect      Create a ruleset on each scope repo's default branch that blocks
#                force-push (non_fast_forward) + branch/tag deletion. Idempotent.
#   verify       List the rulesets present on each scope repo.
#   verify-pat   Confirm each scope's fine-grained PAT reaches ONLY its own repos.
#                Reads DECKHAND_PAT_* from env or ~/.hermes/.env. Never prints secrets.
#   unprotect    Remove the deckhand ruleset from each scope repo (reversal).
#   deploy-detective [--apply]
#                Install the destructive-event alarm workflow in each scope repo.
#                Dry-run by default; mutates only when --apply is passed.
#   verify-detective
#                Check whether each scope repo has the destructive-event workflow.
#
# Requires: gh (authenticated), python3 with pyyaml.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SCOPES_YML="${DECKHAND_SCOPES_YML:-$REPO_ROOT/config/deckhand/scopes.yml}"
RULESET_NAME="deckhand-protect-default"
DETECTIVE_TEMPLATE="$REPO_ROOT/scripts/deckhand/templates/deckhand-destructive-alarm.yml"
DETECTIVE_WORKFLOW_PATH=".github/workflows/deckhand-destructive-alarm.yml"

[ -f "$SCOPES_YML" ] || { echo "scopes.yml not found: $SCOPES_YML" >&2; exit 1; }
command -v gh >/dev/null || { echo "gh not found" >&2; exit 1; }

# --- config extractors (derive from scopes.yml) ----------------------------
_py() {
python3 - "$SCOPES_YML" "$1" <<'PY'
import sys, yaml
cfg = yaml.safe_load(open(sys.argv[1])) or {}
scopes = cfg.get("scopes", {}) or {}
mode = sys.argv[2]
def concrete(repos):
    if not isinstance(repos, list):   # skip globs like "owner:vamseeachanta/*"
        return []
    return [r for r in repos if isinstance(r, str) and "/" in r and not r.startswith("owner:")]
if mode == "repos":
    seen = []
    for s in scopes.values():
        for r in concrete(s.get("repositories")):
            if r not in seen:
                seen.append(r)
    print("\n".join(seen))
elif mode == "pat-map":
    for name, s in scopes.items():
        env = s.get("pat_env")
        repos = concrete(s.get("repositories"))
        if env and repos:
            print("%s\t%s\t%s" % (name, env, ",".join(repos)))
PY
}

ruleset_body() {
cat <<'JSON'
{"name":"deckhand-protect-default","target":"branch","enforcement":"active",
 "conditions":{"ref_name":{"include":["~DEFAULT_BRANCH"],"exclude":[]}},
 "rules":[{"type":"deletion"},{"type":"non_fast_forward"}]}
JSON
}

# Echoes the rulesets JSON array, or the literal UNAVAILABLE / ERROR:<msg>.
_rulesets_json() {
  local out rc
  out="$(gh api "repos/$1/rulesets" 2>&1)"; rc=$?
  if [ "$rc" -ne 0 ]; then
    if printf '%s' "$out" | grep -qi 'Upgrade to GitHub Pro\|make this repository public'; then echo UNAVAILABLE
    else echo "ERROR:$out"; fi
    return 0
  fi
  printf '%s' "$out"
}

_ruleset_id_from() { printf '%s' "$1" | python3 -c "import sys,json;a=json.load(sys.stdin);print(next((str(x['id']) for x in a if x.get('name')=='$RULESET_NAME'),''))" 2>/dev/null; }

_detective_existing_sha() {
  gh api "repos/$1/contents/$DETECTIVE_WORKFLOW_PATH" -q '.sha' 2>/dev/null || true
}

_detective_content_b64() {
  python3 - "$DETECTIVE_TEMPLATE" <<'PY'
import base64, sys
print(base64.b64encode(open(sys.argv[1], "rb").read()).decode("ascii"))
PY
}

_detective_put() {
  local repo="$1" sha="$2" content="$3"
  python3 - "$sha" "$content" <<'PY' | gh api -X PUT "repos/$repo/contents/$DETECTIVE_WORKFLOW_PATH" --input - >/dev/null
import json, sys
sha, content = sys.argv[1], sys.argv[2]
payload = {
    "message": "chore(deckhand): install destructive event alarm",
    "content": content,
}
if sha:
    payload["sha"] = sha
print(json.dumps(payload))
PY
}

protect() {
  while IFS= read -r r; do [ -n "$r" ] || continue
    json="$(_rulesets_json "$r")"
    case "$json" in
      UNAVAILABLE) echo "unavailable: $r  (rulesets need GitHub Pro/Team for private repos)"; continue;;
      ERROR:*)     echo "error:       $r: ${json#ERROR:}"; continue;;
    esac
    if [ -n "$(_ruleset_id_from "$json")" ]; then echo "exists:      $r"
    else ruleset_body | gh api -X POST "repos/$r/rulesets" --input - >/dev/null 2>&1 && echo "protected:   $r" || echo "post-failed:  $r"; fi
  done < <(_py repos)
}

verify() {
  while IFS= read -r r; do [ -n "$r" ] || continue
    json="$(_rulesets_json "$r")"
    case "$json" in
      UNAVAILABLE) echo "$r: UNAVAILABLE (needs GitHub Pro/Team for private repo)"; continue;;
      ERROR:*)     echo "$r: error ${json#ERROR:}"; continue;;
    esac
    echo "$r:"; printf '%s' "$json" | python3 -c "import sys,json
a=json.load(sys.stdin)
[print('  - '+x.get('name','?')+' ('+x.get('enforcement','?')+')') for x in a] or print('  (none)')" 2>/dev/null
  done < <(_py repos)
}

unprotect() {
  while IFS= read -r r; do [ -n "$r" ] || continue
    json="$(_rulesets_json "$r")"
    case "$json" in UNAVAILABLE|ERROR:*) echo "skip:    $r"; continue;; esac
    id="$(_ruleset_id_from "$json")"
    if [ -n "$id" ]; then gh api -X DELETE "repos/$r/rulesets/$id" >/dev/null && echo "removed: $r"; else echo "absent:  $r"; fi
  done < <(_py repos)
}

verify_pat() {
  # Load PATs from ~/.hermes/.env if not already in the environment.
  if [ -f "$HOME/.hermes/.env" ]; then set -a; . "$HOME/.hermes/.env"; set +a; fi
  all_repos="$(_py repos)"
  while IFS=$'\t' read -r scope env repos; do [ -n "$env" ] || continue
    tok="${!env:-}"
    if [ -z "$tok" ]; then echo "$scope ($env): NOT SET — skip"; continue; fi
    IFS=',' read -ra owned <<< "$repos"
    for r in "${owned[@]}"; do
      if GH_TOKEN="$tok" gh api "repos/$r" -q '.full_name' >/dev/null 2>&1; then echo "$scope: reaches $r  OK"
      else echo "$scope: CANNOT reach own repo $r  FAIL"; fi
    done
    # negative: token must NOT reach repos outside its scope
    while IFS= read -r other; do [ -n "$other" ] || continue
      case ",$repos," in *",$other,"*) continue;; esac
      if GH_TOKEN="$tok" gh api "repos/$other" -q '.full_name' >/dev/null 2>&1; then
        echo "$scope: WARN token over-broad — reaches out-of-scope $other"; fi
    done <<< "$all_repos"
  done < <(_py pat-map)
}

deploy_detective() {
  local apply=0
  [ "$#" -le 1 ] || { echo "usage: $0 deploy-detective [--apply]" >&2; exit 2; }
  case "${1:-}" in
    "") ;;
    --apply) apply=1 ;;
    *) echo "usage: $0 deploy-detective [--apply]" >&2; exit 2 ;;
  esac

  [ -f "$DETECTIVE_TEMPLATE" ] || { echo "template not found: $DETECTIVE_TEMPLATE" >&2; exit 1; }

  if [ "$apply" -eq 0 ]; then
    echo "dry-run: would install $DETECTIVE_TEMPLATE as $DETECTIVE_WORKFLOW_PATH"
  else
    echo "apply: installing $DETECTIVE_TEMPLATE as $DETECTIVE_WORKFLOW_PATH"
  fi

  local content sha
  content="$(_detective_content_b64)"
  while IFS= read -r r; do [ -n "$r" ] || continue
    if [ "$apply" -eq 0 ]; then
      echo "would-put:  $r:$DETECTIVE_WORKFLOW_PATH"
      continue
    fi
    sha="$(_detective_existing_sha "$r")"
    if _detective_put "$r" "$sha" "$content"; then
      if [ -n "$sha" ]; then echo "updated:    $r:$DETECTIVE_WORKFLOW_PATH"; else echo "created:    $r:$DETECTIVE_WORKFLOW_PATH"; fi
    else
      echo "put-failed: $r:$DETECTIVE_WORKFLOW_PATH"
    fi
  done < <(_py repos)
}

verify_detective() {
  while IFS= read -r r; do [ -n "$r" ] || continue
    if gh api "repos/$r/contents/$DETECTIVE_WORKFLOW_PATH" -q '.path' >/dev/null 2>&1; then
      echo "$r: present"
    else
      echo "$r: absent"
    fi
  done < <(_py repos)
}

case "${1:-}" in
  protect) protect ;;
  verify) verify ;;
  unprotect) unprotect ;;
  verify-pat) verify_pat ;;
  deploy-detective) shift; deploy_detective "$@" ;;
  verify-detective) shift; [ "$#" -eq 0 ] || { echo "usage: $0 verify-detective" >&2; exit 2; }; verify_detective ;;
  *) echo "usage: $0 {protect|verify|unprotect|verify-pat|deploy-detective [--apply]|verify-detective}" >&2; exit 2 ;;
esac
