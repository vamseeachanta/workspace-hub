#!/usr/bin/env bash
# Issue #1308: read PR state, checks and reviewers in at most two human lines.
# Usage: gh-pr-status.sh [PR#] [--json]
# Requires bash, gh and jq; uses the repository and current branch from gh.
# Bash exit conventions: success=0, failure=1, incorrect usage=2.
set -euo pipefail

source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/_common.sh"

usage() {
    printf 'Usage: gh-pr-status.sh [PR#] [--json]\n' >&2
    exit 2
}

json_mode=false
selection=()
for argument in "$@"; do
    case "$argument" in
        --json)
            [[ "$json_mode" == false ]] || usage
            json_mode=true
            ;;
        *)
            [[ "$argument" =~ ^[1-9][0-9]*$ && ${#selection[@]} == 0 ]] || usage
            selection=("$argument")
            ;;
    esac
done

github_require_tool jq || exit 1
payload=$(github_read_pr "${selection[@]}") || exit 1

# gh JSON uses CheckRun status/conclusion or StatusContext state. A successful
# read exits successfully even when checks fail or are pending; it is no gate.
# jq's zero is the additive identity for the hand-counted check categories.
if ! output=$(jq -ers --argjson machine "$json_mode" '
    def clean: tostring | gsub("[[:cntrl:]\u0085\u2028\u2029]"; " ");
    def names: if length == 0 then "none" else map(clean) | join(", ") end;
    def bucket:
        if .__typename == "CheckRun" then
            if .status == "COMPLETED" then
                if .conclusion == "SUCCESS" then "passed"
                elif (.conclusion == "SKIPPED" or .conclusion == "NEUTRAL") then "skipped"
                elif (.conclusion as $conclusion
                      | ["FAILURE", "ERROR", "CANCELLED", "TIMED_OUT", "ACTION_REQUIRED",
                         "STALE", "STARTUP_FAILURE"] | index($conclusion)) != null then "failed"
                else "unknown" end
            elif (["QUEUED", "IN_PROGRESS", "WAITING", "PENDING", "REQUESTED"] as $pending
                  | .status as $status | $pending | index($status)) != null then "pending"
            else "unknown" end
        elif .__typename == "StatusContext" then
            if .state == "SUCCESS" then "passed"
            elif .state == "PENDING" or .state == "EXPECTED" then "pending"
            elif .state == "FAILURE" or .state == "ERROR" then "failed"
            else "unknown" end
        else "unknown" end;
    if length != 1 then error("expected one JSON object") else .[0] end
    | if type != "object" then error("expected object") else . end
    | if ((.number | type) != "number" or .number <= 0 or .number != (.number | floor)) then
          error("invalid PR metadata") else . end
    | if (.state != "OPEN" and .state != "CLOSED" and .state != "MERGED") then
          error("invalid state") else . end
    | if ((.statusCheckRollup != null and (.statusCheckRollup | type) != "array")
          or (.reviewRequests != null and (.reviewRequests | type) != "array")
          or (.reviews != null and (.reviews | type) != "array")) then
          error("invalid collections") else . end
    | if $machine then tojson else
        . as $pr
        | reduce (($pr.statusCheckRollup // [])[]) as $check
            ({passed:0,pending:0,failed:0,skipped:0,unknown:0}; .[$check | bucket] += 1)
        | "PR #\($pr.number) \($pr.state) | checks: \(.passed) passed, \(.pending) pending, \(.failed) failed, \(.skipped) skipped, \(.unknown) unknown",
          "Review decision: \(if ($pr.reviewDecision // "") == "" then "none" else $pr.reviewDecision | clean end) | requested: \(($pr.reviewRequests // []) | map(.login // .name // .slug // "unknown") | names) | reviews: \(($pr.reviews // []) | map((.author.login // "unknown") + "=" + (.state // "unknown")) | names)"
      end
' <<< "$payload" 2>/dev/null); then
    github_error 'Invalid PR JSON returned by gh; check the gh version and retry.'
    exit 1
fi
printf '%s\n' "$output"
