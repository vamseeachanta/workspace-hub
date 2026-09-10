#!/usr/bin/env bash
# run.sh — durable job dispatch for a Linux fleet host. workspace-hub#3740 slice 4.
#
# WHY THIS EXISTS
# 867 issues sit at `dispatch:ready` because the queue is drained by per-machine
# sessions and a session that finishes leaves no trace. Asking operators to
# remember to report back has already failed 867 times. This wrapper makes the
# completion record a SIDE EFFECT of running the work: you cannot run a job
# through it without the exit code, the timings, and the issue it belongs to
# being written down.
#
# WHY setsid AND A PIDFILE
# A dispatched run must outlive the session that submitted it. `cmd &` alone does
# not: the shell's job stays in the submitting session's process group, and a
# session teardown (SSH close, `tmux kill-session`, terminal hangup) delivers
# SIGHUP to that group. `setsid` puts the runner in a NEW session with no
# controlling terminal, so the teardown has nothing to signal; `nohup` and
# `</dev/null` close the remaining paths back to the dead terminal. The pidfile
# is what makes the detached process addressable afterwards — a detached job with
# no recorded pid is uncancellable and indistinguishable from one that never
# started.
#
# This is the Linux counterpart of `scripts/windows/dispatch-run.ps1` (wh#3729)
# and MUST stay interchangeable with it: same verbs, same one-JSON-object-per-
# invocation output. Windows needed a Scheduled Task for the same durability
# because Windows OpenSSH kills the whole descendant process tree at session
# close and neither `start /b` nor `Start-Process -WindowStyle Hidden` survives.
# Different mechanism, identical contract.
#
# ---------------------------------------------------------------------------
# CONSTRAINT — DO NOT "SIMPLIFY" THIS INTO `ssh host '<cmd>'`
# ---------------------------------------------------------------------------
# Per .claude/rules/licensed-solver-dispatch.md: Orcina products (OrcaFlex,
# OrcaWave) CANNOT complete a FlexNet license checkout under an SSH public-key
# logon token. The token an SSH key logon produces lacks the credentials FlexNet
# needs to reach the license service, so the solver fails the checkout — and it
# fails at solve time, long after the dispatch looked successful, which is why
# this keeps getting rediscovered. Licensed solver work is
# **Windows-Scheduled-Task-only**; it goes through `dispatch-run.ps1` on a
# licensed host, never through this script and never through a bare `ssh host
# '<cmd>'` one-liner.
#
# This script is for unlicensed compute (analysis, codegen, data work, test
# runs). If you are here to "unify the two platforms behind ssh", the answer is
# no, and the reason is a license token, not an aesthetic preference.
# ---------------------------------------------------------------------------
#
# VERBS (each emits exactly ONE JSON object on stdout)
#   run.sh submit  --command <cmd> --issue-ref owner/repo#123
#                  [--job-id <id>] [--work-dir <dir>] [--shell bash|sh]
#                  [--foreground]
#   run.sh status  --job-id <id>
#   run.sh logs    --job-id <id> [--tail <n>]
#   run.sh list
#   run.sh cancel  --job-id <id>
#   run.sh cleanup --job-id <id>
#
# EXIT CODES OF THIS SCRIPT (not of the dispatched job)
#   0   the verb succeeded
#   2   no such job
#   64  usage error (unknown verb, missing/invalid argument)
# A successful `submit` exits 0 even for a job that will fail. The child's real
# exit code round-trips through the job's own state, read back by a LATER
# `status` invocation. The submitting shell never sees it and must not try to:
# the submitting shell is usually gone by the time the job finishes.
#
# STATE DIR LAYOUT  ($WH_DISPATCH_STATE_DIR, default $XDG_STATE_HOME/workspace-hub/dispatch)
#   <root>/<job_id>/
#     job.kv       immutable submit-time facts (issue_ref, shell, work_dir)
#     command.txt  the payload, executed as a file so no quoting is re-parsed
#     runner.sh    generated wrapper; records the exit code AFTER the payload ends
#     status.kv    mutable state, replaced atomically (tmp + mv)
#     heartbeat    one ISO-8601 line, refreshed OUT-OF-BAND by a sibling process
#     runner.pid   pid of the detached wrapper
#     child.pid    pid of the payload
#     stdout.log / stderr.log
#
# WHY .kv AND NOT status.json ON DISK: a POSIX shell has no JSON parser it can
# rely on (jq is not installable on every fleet host). Writing JSON that this
# script then re-parses with sed would make the on-disk format load-bearing for
# regex, which breaks the first time a work_dir contains a quote. Tab-separated
# key/value is trivially parseable, and JSON is rendered in exactly ONE place —
# the emitters below — so the two can never drift.

set -uo pipefail

STATE_ROOT="${WH_DISPATCH_STATE_DIR:-${XDG_STATE_HOME:-$HOME/.local/state}/workspace-hub/dispatch}"
HEARTBEAT_SECONDS="${WH_DISPATCH_HEARTBEAT_SECONDS:-30}"

EX_USAGE=64
EX_NOJOB=2

# ---------------------------------------------------------------------------
# JSON emission — the only place JSON is produced
# ---------------------------------------------------------------------------

# Escape a value into a JSON string literal. Order matters: backslashes first,
# or the escapes added for quotes and newlines get escaped a second time.
json_str() {
    local s=${1-}
    s=${s//\\/\\\\}
    s=${s//\"/\\\"}
    s=${s//$'\n'/\\n}
    s=${s//$'\r'/\\r}
    s=${s//$'\t'/\\t}
    printf '"%s"' "$s"
}

# A number, or the literal null for an empty value. Callers must not quote these
# — an exit code arriving as "7" instead of 7 turns every consumer's numeric
# comparison into a silent false.
json_num() {
    local v=${1-}
    if [ -z "$v" ]; then printf 'null'; else printf '%s' "$v"; fi
}

# Usage and argument failures are JSON too. A caller parsing stdout should never
# have to switch to reading prose to find out it passed a bad flag.
#
# FAIL_JOB_ID is echoed back when it is known, matching the Windows side's
# `{ok:false, job_id, error}` for a missing job. A caller polling several jobs
# needs to know WHICH one it just asked about.
FAIL_JOB_ID=''
fail() {
    local action=$1 message=$2 code=${3:-$EX_USAGE}
    printf '{"ok":false,"action":%s,"job_id":%s,"error":%s}\n' \
        "$(json_str "$action")" "$(json_str "$FAIL_JOB_ID")" "$(json_str "$message")"
    exit "$code"
}

# ---------------------------------------------------------------------------
# validation
# ---------------------------------------------------------------------------

# Job ids become directory names. Anything outside this set could escape the
# state root (`../..`) or collide with the tmp files used for atomic replace.
# Same character class as the Windows side, so an id minted on one platform is
# valid on the other.
valid_job_id() {
    [[ ${1-} =~ ^[A-Za-z0-9._-]{1,64}$ ]]
}

# `owner/repo#123`. The point of the wrapper is that a run is tied to a record;
# an unvalidated ref would tie it to a typo, which is the same as not tying it.
valid_issue_ref() {
    [[ ${1-} =~ ^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+#[0-9]+$ ]]
}

# A flag whose value is missing must abort, not consume the next flag and not
# spin. `shift 2` on a one-element list fails silently, leaves the list intact,
# and the parse loop then runs forever — a hang is a worse bug report than an
# error message.
need_value() {
    local action=$1 flag=$2
    [ $# -ge 3 ] || fail "$action" "option '$flag' requires a value"
}

new_job_id() {
    # Timestamp for sortability plus randomness for collision resistance when two
    # submits land in the same second. $RANDOM rather than /dev/urandom piped
    # through head: the pipe SIGPIPEs under pipefail and the "random" id becomes
    # a submit failure.
    printf '%s-%04x%04x' "$(date -u +%Y%m%dT%H%M%SZ)" "$RANDOM" "$RANDOM"
}

now_iso() { date -u +%Y-%m-%dT%H:%M:%SZ; }

job_dir() { printf '%s/%s' "$STATE_ROOT" "$1"; }

# ---------------------------------------------------------------------------
# key/value state files
# ---------------------------------------------------------------------------

kv_get() {
    local file=$1 key=$2
    [ -f "$file" ] || return 0
    awk -v k="$key" 'index($0, k "\t") == 1 { print substr($0, length(k) + 2) }' \
        "$file" | tail -n 1
}

alive() {
    local pid=${1-}
    [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null
}

read_pid() {
    local f=$1
    [ -f "$f" ] && tr -dc '0-9' < "$f"
}

# ---------------------------------------------------------------------------
# the generated runner
# ---------------------------------------------------------------------------
#
# Written per job rather than sourced from a shared path so a job's wrapper
# cannot change under it mid-run: two agents editing one shared runner while
# jobs are in flight is a documented hazard in this repo
# (`feedback_parallel_agents_shared_mutable_tool_path`). The template is static
# — every job fact is read from job.kv — so there is no substitution to get
# wrong and the file is byte-identical across jobs.
write_runner() {
    cat > "$1/runner.sh" <<'RUNNER'
#!/usr/bin/env bash
# Generated by scripts/dispatch/run.sh. Do not edit — edit the generator.
#
# Deliberately NOT `set -e`. Recording the payload's exit code after it finishes
# is this wrapper's entire purpose; an errexit abort somewhere in the bookkeeping
# would leave a finished job looking like a vanished one, which is exactly the
# failure mode #3740 exists to close.
set -uo pipefail

dir=$1

kv() { awk -v k="$1" 'index($0, k "\t") == 1 { print substr($0, length(k) + 2) }' "$dir/job.kv" | tail -n 1; }

job_id=$(kv job_id)
issue_ref=$(kv issue_ref)
shell_bin=$(kv shell)
work_dir=$(kv work_dir)
hb=$(kv heartbeat_seconds)
submitted_at=$(kv submitted_at)

now() { date -u +%Y-%m-%dT%H:%M:%SZ; }

# Atomic replace. A reader that catches a half-written heartbeat would see a
# blank timestamp and conclude the job is dead.
beat() {
    now > "$dir/heartbeat.tmp" 2>/dev/null && mv -f "$dir/heartbeat.tmp" "$dir/heartbeat"
}

write_status() {
    local state=$1 exit_code=$2 started=$3 finished=$4
    {
        printf 'job_id\t%s\n'       "$job_id"
        printf 'issue_ref\t%s\n'    "$issue_ref"
        printf 'state\t%s\n'        "$state"
        printf 'shell\t%s\n'        "$shell_bin"
        printf 'work_dir\t%s\n'     "$work_dir"
        printf 'submitted_at\t%s\n' "$submitted_at"
        printf 'started_at\t%s\n'   "$started"
        printf 'finished_at\t%s\n'  "$finished"
        printf 'exit_code\t%s\n'    "$exit_code"
    } > "$dir/status.kv.tmp" && mv -f "$dir/status.kv.tmp" "$dir/status.kv"
}

echo "$$" > "$dir/runner.pid"

started_at=$(now)
beat

if ! cd "$work_dir" 2>/dev/null; then
    # A missing work dir is a dispatch error, not a solver error, and must be
    # distinguishable from one. 66 = EX_NOINPUT.
    printf 'dispatch: work dir does not exist: %s\n' "$work_dir" > "$dir/stderr.log"
    write_status finished 66 "$started_at" "$(now)"
    exit 66
fi

"$shell_bin" "$dir/command.txt" > "$dir/stdout.log" 2> "$dir/stderr.log" &
child=$!
echo "$child" > "$dir/child.pid"
write_status running "" "$started_at" ""

# The heartbeat is refreshed by a SIBLING of the payload, never by the payload.
# A job blocked inside a solver cannot beat for itself, and requiring it to would
# make every long run look dead to the reaper — which would then requeue work
# that was fine, the worst possible interruption.
( while kill -0 "$child" 2>/dev/null; do beat; sleep "$hb"; done ) &
beater=$!

# `cancel` signals the child, not this wrapper, so this wrapper survives to
# record the outcome. This trap covers the other direction: a signal aimed at
# the wrapper is forwarded down rather than orphaning the payload.
trap 'kill -TERM "$child" 2>/dev/null' TERM INT

wait "$child"
rc=$?

kill "$beater" 2>/dev/null
beat

# Signal deaths (128+n) are reported as `cancelled`, because "ran to completion
# with a nonzero code" and "was killed" call for different follow-up. The code
# is preserved either way — the state names the shape of the ending, the exit
# code carries the detail.
if [ "$rc" -gt 128 ]; then state=cancelled; else state=finished; fi
write_status "$state" "$rc" "$started_at" "$(now)"
exit "$rc"
RUNNER
    chmod +x "$1/runner.sh"
}

# ---------------------------------------------------------------------------
# verbs
# ---------------------------------------------------------------------------

cmd_submit() {
    local command='' job_id='' work_dir='' shell_bin='bash' issue_ref='' foreground=0
    while [ $# -gt 0 ]; do
        case $1 in
            --command)   need_value submit "$@"; command=$2;   shift 2 ;;
            --job-id)    need_value submit "$@"; job_id=$2;    shift 2 ;;
            --work-dir)  need_value submit "$@"; work_dir=$2;  shift 2 ;;
            --shell)     need_value submit "$@"; shell_bin=$2; shift 2 ;;
            --issue-ref) need_value submit "$@"; issue_ref=$2; shift 2 ;;
            --foreground) foreground=1;   shift ;;
            *) fail submit "unknown option '$1' for submit" ;;
        esac
    done

    [ -n "$command" ] || fail submit "--command is required for submit"

    # Required, not optional. A run with no issue ref is precisely the 867-issue
    # failure: work happens, nothing can be joined back to the queue item, and
    # the record has nowhere to land. Refusing here is cheaper than reconciling
    # an orphan run later.
    [ -n "$issue_ref" ] || fail submit \
        "--issue-ref owner/repo#123 is required for submit (a run with no record is unreportable)"
    valid_issue_ref "$issue_ref" || fail submit \
        "invalid --issue-ref '$issue_ref' (expected owner/repo#123)"

    case $shell_bin in
        bash|sh) ;;
        *) fail submit "invalid --shell '$shell_bin' (allowed: bash, sh)" ;;
    esac

    if [ -n "$job_id" ]; then
        valid_job_id "$job_id" || fail submit \
            "invalid --job-id '$job_id' (allowed: letters, digits, dot, underscore, hyphen; max 64)"
    else
        job_id=$(new_job_id)
    fi

    local dir; dir=$(job_dir "$job_id")
    # Refuse rather than reuse: a second submit into a live job dir would
    # overwrite the first job's logs and exit code while it is still running.
    [ -e "$dir" ] && fail submit "job '$job_id' already exists at $dir"
    mkdir -p "$dir" || fail submit "cannot create job dir $dir"

    [ -n "$work_dir" ] || work_dir=$dir

    printf '%s\n' "$command" > "$dir/command.txt"

    local submitted_at; submitted_at=$(now_iso)
    {
        printf 'job_id\t%s\n'            "$job_id"
        printf 'issue_ref\t%s\n'         "$issue_ref"
        printf 'shell\t%s\n'             "$shell_bin"
        printf 'work_dir\t%s\n'          "$work_dir"
        printf 'heartbeat_seconds\t%s\n' "$HEARTBEAT_SECONDS"
        printf 'submitted_at\t%s\n'      "$submitted_at"
    } > "$dir/job.kv"

    # Seed a status before launching so a poll landing between mkdir and the
    # runner's first write reads `submitted`, not a void it would have to
    # interpret.
    {
        printf 'job_id\t%s\n'        "$job_id"
        printf 'issue_ref\t%s\n'     "$issue_ref"
        printf 'state\t%s\n'         "submitted"
        printf 'shell\t%s\n'         "$shell_bin"
        printf 'work_dir\t%s\n'      "$work_dir"
        printf 'submitted_at\t%s\n'  "$submitted_at"
        printf 'started_at\t%s\n'    ""
        printf 'finished_at\t%s\n'   ""
        printf 'exit_code\t%s\n'     ""
    } > "$dir/status.kv"

    write_runner "$dir"

    local mode
    if [ "$foreground" -eq 1 ]; then
        # Attached mode. Not the dispatch path — it is for debugging a job under
        # a terminal, and for verifying the exit-code round-trip without racing
        # a detached process. The recorded state is identical either way, which
        # is what makes it a usable check of the real thing.
        mode=foreground
        bash "$dir/runner.sh" "$dir" >/dev/null 2>&1
    elif command -v setsid >/dev/null 2>&1; then
        mode=setsid
        setsid nohup bash "$dir/runner.sh" "$dir" >/dev/null 2>&1 </dev/null &
    else
        # util-linux is absent on a stripped image. nohup alone still detaches
        # from the terminal, but the runner stays in the submitting shell's
        # process group, so a group-wide kill can still reach it. Degraded, and
        # named as such in the output so a caller can tell.
        mode=nohup
        nohup bash "$dir/runner.sh" "$dir" >/dev/null 2>&1 </dev/null &
    fi

    printf '{"ok":true,"action":"submit","job_id":%s,"issue_ref":%s,"task":%s,"mode":%s,"dir":%s,"stdout":%s,"stderr":%s,"shell":%s}\n' \
        "$(json_str "$job_id")" "$(json_str "$issue_ref")" \
        "$(json_str "$mode:$job_id")" "$(json_str "$mode")" \
        "$(json_str "$dir")" "$(json_str "$dir/stdout.log")" \
        "$(json_str "$dir/stderr.log")" "$(json_str "$shell_bin")"
    # Exit 0 for a successful SUBMISSION. The child's code is not knowable here
    # and must not be guessed at; the caller reads it from a later `status`.
    exit 0
}

# Shared flag parsing for the verbs that address an existing job.
parse_job_flags() {
    ARG_JOB_ID=''
    ARG_TAIL=50
    local action=$1; shift
    while [ $# -gt 0 ]; do
        case $1 in
            --job-id) need_value "$action" "$@"; ARG_JOB_ID=$2; shift 2 ;;
            --tail)   need_value "$action" "$@"; ARG_TAIL=$2;   shift 2 ;;
            *) fail "$action" "unknown option '$1' for $action" ;;
        esac
    done
    [ -n "$ARG_JOB_ID" ] || fail "$action" "--job-id is required for $action"
    valid_job_id "$ARG_JOB_ID" || fail "$action" \
        "invalid --job-id '$ARG_JOB_ID' (allowed: letters, digits, dot, underscore, hyphen; max 64)"
    # Only echoed back once the id is known safe — an unvalidated id must not be
    # reflected into the caller's output.
    FAIL_JOB_ID=$ARG_JOB_ID
}

cmd_status() {
    parse_job_flags status "$@"
    local dir; dir=$(job_dir "$ARG_JOB_ID")
    [ -d "$dir" ] || fail status "no such job" "$EX_NOJOB"

    local state exit_code issue_ref heartbeat child_pid task_state
    state=$(kv_get "$dir/status.kv" state)
    exit_code=$(kv_get "$dir/status.kv" exit_code)
    issue_ref=$(kv_get "$dir/status.kv" issue_ref)
    heartbeat=''
    [ -f "$dir/heartbeat" ] && heartbeat=$(cat "$dir/heartbeat")
    child_pid=$(read_pid "$dir/child.pid")
    [ -n "$state" ] || state=unknown

    if alive "$child_pid"; then task_state=running; else task_state=absent; fi

    local out_bytes='' err_bytes=''
    [ -f "$dir/stdout.log" ] && out_bytes=$(wc -c < "$dir/stdout.log" | tr -dc '0-9')
    [ -f "$dir/stderr.log" ] && err_bytes=$(wc -c < "$dir/stderr.log" | tr -dc '0-9')

    # `task_last_result` exists for shape parity with the Windows verb. There it
    # is the Scheduled Task's own launch result, which is 0 for a started job
    # whose payload later failed. Here the wrapper exits with the payload's code,
    # so the two coincide — and the runner-recorded exit_code stays authoritative
    # on both platforms.
    printf '{"ok":true,"action":"status","job_id":%s,"issue_ref":%s,"state":%s,"exit_code":%s,"task_state":%s,"task_last_result":%s,"pid":%s,"heartbeat_at":%s,"stdout_bytes":%s,"stderr_bytes":%s,"dir":%s}\n' \
        "$(json_str "$ARG_JOB_ID")" "$(json_str "$issue_ref")" "$(json_str "$state")" \
        "$(json_num "$exit_code")" "$(json_str "$task_state")" "$(json_num "$exit_code")" \
        "$(json_num "$child_pid")" "$(json_str "$heartbeat")" \
        "$(json_num "$out_bytes")" "$(json_num "$err_bytes")" "$(json_str "$dir")"
    exit 0
}

cmd_logs() {
    parse_job_flags logs "$@"
    [[ $ARG_TAIL =~ ^[0-9]+$ ]] || fail logs "invalid --tail '$ARG_TAIL' (expected a non-negative integer)"
    local dir; dir=$(job_dir "$ARG_JOB_ID")
    [ -d "$dir" ] || fail logs "no such job" "$EX_NOJOB"

    # Control characters other than the ones json_str escapes are stripped: a raw
    # 0x07 from a progress bar inside a JSON string is invalid JSON, and the
    # caller would lose the whole payload over a decoration.
    local out='' err=''
    [ -f "$dir/stdout.log" ] && out=$(tail -n "$ARG_TAIL" "$dir/stdout.log" | tr -d '\000-\010\013\014\016-\037')
    [ -f "$dir/stderr.log" ] && err=$(tail -n "$ARG_TAIL" "$dir/stderr.log" | tr -d '\000-\010\013\014\016-\037')

    printf '{"ok":true,"action":"logs","job_id":%s,"stdout":%s,"stderr":%s}\n' \
        "$(json_str "$ARG_JOB_ID")" "$(json_str "$out")" "$(json_str "$err")"
    exit 0
}

cmd_list() {
    [ $# -eq 0 ] || fail list "list takes no options (got '$1')"
    local jobs='' count=0 d id state exit_code issue_ref
    if [ -d "$STATE_ROOT" ]; then
        for d in "$STATE_ROOT"/*/; do
            [ -d "$d" ] || continue
            id=$(basename "$d")
            state=$(kv_get "$d/status.kv" state)
            exit_code=$(kv_get "$d/status.kv" exit_code)
            issue_ref=$(kv_get "$d/status.kv" issue_ref)
            [ -n "$state" ] || state=unknown
            [ -z "$jobs" ] || jobs="$jobs,"
            jobs="$jobs{\"job_id\":$(json_str "$id"),\"issue_ref\":$(json_str "$issue_ref"),\"state\":$(json_str "$state"),\"exit_code\":$(json_num "$exit_code")}"
            count=$((count + 1))
        done
    fi
    printf '{"ok":true,"action":"list","count":%d,"jobs":[%s]}\n' "$count" "$jobs"
    exit 0
}

cmd_cancel() {
    parse_job_flags cancel "$@"
    local dir; dir=$(job_dir "$ARG_JOB_ID")
    [ -d "$dir" ] || fail cancel "no such job" "$EX_NOJOB"

    # Signal the PAYLOAD, not the wrapper. Killing the wrapper (or its whole
    # process group) would stop the one process whose job is to record the
    # outcome, turning a cancellation into an unexplained disappearance.
    local child_pid signalled=false note
    child_pid=$(read_pid "$dir/child.pid")
    if alive "$child_pid"; then
        kill -TERM "$child_pid" 2>/dev/null && signalled=true
    fi
    if [ "$signalled" = true ]; then
        note="SIGTERM sent to the payload; the runner records the final state and exit code"
    else
        # Not an error: cancelling an already-finished job is the normal outcome
        # of a race between a reaper and a job that completed. The recorded state
        # is left exactly as it was — cancel never rewrites history.
        note="payload was not running; status.kv keeps its last recorded state"
    fi

    printf '{"ok":true,"action":"cancel","job_id":%s,"pid":%s,"signalled":%s,"note":%s}\n' \
        "$(json_str "$ARG_JOB_ID")" "$(json_num "$child_pid")" "$signalled" "$(json_str "$note")"
    exit 0
}

cmd_cleanup() {
    parse_job_flags cleanup "$@"
    local dir; dir=$(job_dir "$ARG_JOB_ID")
    [ -d "$dir" ] || fail cleanup "no such job" "$EX_NOJOB"
    # Logs go with the job. Fetch them BEFORE cleanup if you need them — same
    # contract as the Windows verb.
    rm -rf "$dir"
    printf '{"ok":true,"action":"cleanup","job_id":%s,"removed_dir":%s}\n' \
        "$(json_str "$ARG_JOB_ID")" "$(json_str "$dir")"
    exit 0
}

cmd_help() {
    printf '{"ok":true,"action":"help","verbs":["submit","status","logs","list","cancel","cleanup"],"state_root":%s}\n' \
        "$(json_str "$STATE_ROOT")"
    exit 0
}

# ---------------------------------------------------------------------------
# dispatch
# ---------------------------------------------------------------------------

main() {
    [ $# -gt 0 ] || fail "" "no verb given (expected one of: submit status logs list cancel cleanup)"
    local verb=$1; shift
    case $verb in
        submit)  cmd_submit  "$@" ;;
        status)  cmd_status  "$@" ;;
        logs)    cmd_logs    "$@" ;;
        list)    cmd_list    "$@" ;;
        cancel)  cmd_cancel  "$@" ;;
        cleanup) cmd_cleanup "$@" ;;
        help|--help|-h) cmd_help ;;
        # No default verb, ever. A typo that silently ran `list` would report a
        # clean-looking result for work that was never dispatched — the exact
        # class of quiet false success this whole slice exists to remove.
        *) fail "$verb" "unknown verb '$verb' (expected one of: submit status logs list cancel cleanup)" ;;
    esac
}

main "$@"
