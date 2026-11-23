# Plan for #3057: cron cutover env and repo hygiene live-probe hardening

> **Status:** plan-approved
> **Complexity:** T2
> **Date:** 2026-06-13
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3057
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** failing r1/r2/r3/r4/r6/r7/r8/r9/r10/r11/r12/r13/r14/r15/r16 artifacts, superseded no-MAJOR r5 artifacts, and final no-MAJOR r17 artifacts under `scripts/review/results/2026-06-13-plan-3057-*`.

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/cron/cron_apply.py:145-157` loads raw catalog tasks, calls `cron_transaction.select_tasks(...)`, then sends those task dicts directly into `cron_transaction.plan_cutover(...)`. `select_tasks` already supports exact legacy `machines:` pins and conflict reporting, but `cron_apply.py:213-216` resolves the live host to the canonical registry key `dev-primary`; catalog tasks pinned only to `ace-linux-1` therefore miss the exact legacy match. This diverges from `setup-cron.sh`, which selects cron rows by hostname/alias machine tokens.
- Found: `rg -n 'scheduler' scripts/cron/cron_transaction.py scripts/cron/cron_apply.py scripts/cron/cron-audit.py` returns no matches today; Linux-cron scheduler filtering is net-new for the transactional/audit path. Current Windows catalog tasks avoid selection only incidentally through `machines: [ace-win-1, ace-win-2]` legacy exclusion, and they appear in the current conflict report instead of being skipped as non-cron scheduler entries.
- Found: `scripts/cron/cron_transaction.py:28-29` classifies bare uppercase `VAR=value` lines as env/header lines, and `scripts/cron/cron_transaction.py:191-192` returns them as `ignore`; this is why the live dry-run lists `WORKSPACE_HUB=` and `LOG=` under `preserved` rather than aborting as uncataloged.
- Found: `scripts/cron/cron_transaction.py:269-279` renders managed crontab lines as `"{schedule} {task['command']}"`; it has no machine-aware `$WORKSPACE_HUB` or `$LOG` expansion.
- Found: `scripts/cron/setup-cron.sh:106-140` contains separate expansion logic for `$WORKSPACE_HUB` and `$LOG`, so the legacy installer and transactional installer currently diverge.
- Found: `scripts/cron/cron_apply.py:119-130` prefers a `scripts/*.sh|*.py` token and otherwise truncates fallback catalog command keys with `cmd.strip()[:60]`; placeholder commands such as `notification-purge` therefore need full raw+rendered fallback keys rather than the existing 60-character prefix.
- Found: `scripts/cron/cron_apply.py:133-138` and `scripts/cron/cron-audit.py:101-116` currently return bare fingerprint dicts and discard sibling metadata; `scripts/cron/cron_apply.py:188-199` separately rolls back if any line classified as `preserved_external` or `ignore` is missing after apply. Catalog-owned dedupe therefore must preserve `catalog_task_id` metadata and use the same selected-task-aware classifier in both `plan_cutover` and the post-apply preservation guard.
- Found: `rg -n 'def catalog_commands|catalog_commands\\(' scripts/cron tests/cron` shows `cron_apply.catalog_commands` is used by `scripts/cron/cron_apply.py` and `tests/cron/test_a1_preserved.py`; `cron-audit.py` has a separate `load_catalog_commands`; `cron_transaction.py` currently receives catalog commands as parameters. The shared builder move must update the test import and preserve existing parameter-call fixtures.
- Found: `tests/cron/test_cron_transaction.py:147-150` exercises `classify_line` with a bare fingerprint dict, so any metadata-entry extension must normalize both shapes and keep the public string-returning API backward compatible.
- Found: `setup-cron.sh` currently emits schedule/command lines with two spaces while `cron_transaction.py:278` uses one; the shared renderer must pin one canonical separator so byte-parity tests compare a real contract.
- Found: `scripts/cron/repo-ecosystem-hygiene-audit.sh:37-39` defaults probe/repo/total timeouts to `10`, `45`, and `480` seconds.
- Found: `scripts/cron/repo-ecosystem-hygiene-audit.sh:144-175` maps fixed read-only git operations, including `status-short` at `scripts/cron/repo-ecosystem-hygiene-audit.sh:147`.
- Found: `scripts/monitoring/cron-health-check.sh:83-92` scans generic log error tokens only; it does not interpret the hygiene evidence line `task=repo-ecosystem-hygiene status=ERROR`.
- Found: `scripts/monitoring/cron-health-check.sh:28-35` supports live cron invocation without `--workspace` by using `WORKSPACE_HUB` when set and otherwise falling back to the script-relative repo root; `--workspace` is only the hermetic test override.
- Found: `tests/cron/test_cron_apply.py:78-153`, `tests/cron/test_cron_transaction.py:158-236`, `scripts/cron/tests/test_repo_ecosystem_hygiene_audit.py:184-215`, and `scripts/monitoring/tests/test_cron_health_check.sh:390-440` provide focused test surfaces for the three defects.

### Standards
| Standard | Status | Source |
|---|---|---|
| Scheduled task source of truth | active | `config/scheduled-tasks/schedule-tasks.yaml:1-5` says all cron/task-scheduler entries must be declared there and not added directly to crontab. |
| Control-plane contract | active | `docs/standards/CONTROL_PLANE_CONTRACT.md:1-11` makes `AGENTS.md` and repo docs the discovery contract; this issue stays in `workspace-hub` control-plane automation. |
| Hard-stop policy | active | `docs/standards/HARD-STOP-POLICY.md:1-35` does not classify this as engineering-critical, but repo AGENTS instructions still require issue planning, TDD, review, and user approval before implementation. |

### LLM Wiki pages consulted
- N/A - this plan does not touch `llm-wiki` or client wiki content.

### Documents consulted
- GitHub issue `#3057` - open bug with `status:needs-plan` and `lane:claude`; defines the three live defects and five acceptance criteria.
- GitHub issue `#3041` - closed parent delivery for the daily read-only repo ecosystem hygiene audit.
- GitHub issue `#2969` - closed transactional cron cutover issue; current cutover path comes from this work.
- GitHub issue `#2291` - open cron-health hardening issue; #3057 will make the narrower hygiene evidence-line fix without consuming the broader issue.
- `docs/plans/2026-06-12-issue-3041-repo-ecosystem-hygiene-audit.md:596-621` - prior plan deliberately kept ordinary hygiene `WARN/ERROR` in audit artifacts/evidence lines while reserving nonzero cron failure for execution failures; #3057 refines how cron-health interprets a hygiene `status=ERROR` evidence line.
- `config/scheduled-tasks/schedule-tasks.yaml:500-531` - current hygiene and cron-health task definitions; hygiene runs at `35 5 * * *`, cron-health at `45 5 * * *`.

### Gaps identified
- No shared rendering helper exists for the transactional cutover path to expand `$WORKSPACE_HUB` and `$LOG` the way `setup-cron.sh` does.
- `cron_apply.py --json` does not expose rendered crontab text or a required-env contract, so dry-run output cannot currently prove executability.
- `cron_apply.py` catalog matching is script-token-stable for most tasks, but at least one placeholder command (`notification-purge`) lacks a `scripts/*.sh|*.py` token and falls back to the first 60 raw command characters. After render-time placeholder expansion, that raw fallback key would no longer match an expanded out-of-managed-block legacy line; the 60-character fallback is also too collision-prone once the absolute workspace path consumes most of the key.
- Hygiene status probes use `git status --porcelain=v1 --untracked-files=all` with a 10-second default, which is too close to observed live repo timings on this host.
- Cron-health does not treat `task=repo-ecosystem-hygiene status=ERROR` as a task problem, while it must continue treating `status=WARN` as an audit finding rather than an execution failure.

### Evidence

**Issue statuses** (verified 2026-06-13 via `gh issue view`):
- `#3057` - OPEN - `bug(automation): harden cron cutover env and repo hygiene live probes` - labels include `status:needs-plan`, `cat:harness`, `domain:automation`, `domain:repo-health`, `lane:claude`.
- `#3041` - CLOSED - `feat(automation): daily read-only repo ecosystem hygiene audit`.
- `#2969` - CLOSED - `feat(workstations): declarative workflow/cron catalog - role-tagged, materialize per-role subset [#2967 F2]`.
- `#2291` - OPEN - `fix(cron-health): harden failure detection and align task evidence contracts`.

**File existence** (`rg --files` 2026-06-13):
- EXISTS: `scripts/cron/cron_apply.py`
- EXISTS: `scripts/cron/cron_transaction.py`
- EXISTS: `scripts/cron/cron-audit.py`
- EXISTS: `scripts/cron/setup-cron.sh`
- EXISTS: `scripts/cron/repo-ecosystem-hygiene-audit.sh`
- EXISTS: `scripts/monitoring/cron-health-check.sh`
- EXISTS: `config/workstations/harness-state-classes.yaml`
- EXISTS: `config/workstations/registry.yaml`
- EXISTS: `tests/cron/test_cron_apply.py`
- EXISTS: `tests/cron/test_cron_transaction.py`
- EXISTS: `tests/cron/test_cron_audit.py`
- EXISTS: `tests/cron/test_a1_preserved.py`
- EXISTS: `scripts/cron/tests/test_validate_schedule.py`
- EXISTS: `scripts/cron/tests/test_repo_ecosystem_hygiene_audit.py`
- EXISTS: `scripts/monitoring/tests/test_cron_health_check.sh`

**Line excerpts**:
```
$ nl -ba scripts/cron/cron_transaction.py | sed -n '28,29p;191,192p;269,279p'
28  # An env/header line such as MAILTO=, SHELL=, PATH= at the start of the line.
29  _ENV_LINE_RE = re.compile(r"^[A-Z_]+=")
191     if _is_ignore_line(line):
192         return "ignore"
269 def render_block(tasks: list[dict], roles: list[str]) -> list[str]:
275     sorted_tasks = sorted(tasks or [], key=lambda t: t.get("id"))
276     lines = [marker_begin(roles)]
277     for task in sorted_tasks:
278         lines.append(f"{task['schedule']} {task['command']}")
279     lines.append(MARKER_END)

$ nl -ba scripts/cron/setup-cron.sh | sed -n '106,140p'
106 hub = '${WORKSPACE_HUB}'
107 log_full = hub + '/logs/quality/cron-wrapper.log'
135     # Expand \$WORKSPACE_HUB and \$LOG variables
136     command = command.replace('\$WORKSPACE_HUB', hub)
137     if '${CRON_VARIANT}' == 'full':
138         command = command.replace('\$LOG', log_full)
140         command = command.replace('\$LOG', log_contrib)

$ nl -ba scripts/cron/setup-cron.sh | sed -n '21,25p;43,63p;95,96p'
21  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
22  WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
45    CRON_VARIANT=$(uv run --no-project python -c "
54          print(m.get('schedule_variant', 'contribute'))
60      echo "INFO: hostname '${HOSTNAME_SHORT}' not in registry - defaulting to 'contribute'"
62      CRON_VARIANT="contribute"
95  done < <(
96    uv run --no-project python -c "

$ nl -ba scripts/cron/repo-ecosystem-hygiene-audit.sh | sed -n '37,39p;144,148p;458,468p'
37  PROBE_TIMEOUT_SEC = int(os.environ.get("REPO_ECOSYSTEM_HYGIENE_PROBE_TIMEOUT_SEC", "10"))
38  REPO_TIMEOUT_SEC = int(os.environ.get("REPO_ECOSYSTEM_HYGIENE_REPO_TIMEOUT_SEC", "45"))
39  TOTAL_TIMEOUT_SEC = int(os.environ.get("REPO_ECOSYSTEM_HYGIENE_TOTAL_TIMEOUT_SEC", "480"))
144 def git_readonly(operation: str, repo: Path, arg: str | None = None, timeout_sec: float | None = None) -> dict[str, Any]:
147     "status-short": ["git", "status", "--porcelain=v1", "--untracked-files=all"],
458 status_short = git_readonly("status-short", path, timeout_sec=remaining_repo_timeout())
463                 "code": "git_probe_timeout" if status_short["code"] == 124 else "git_probe_failed",

$ nl -ba scripts/monitoring/cron-health-check.sh | sed -n '83,92p;226,255p'
28  if [[ -z "$WS_HUB" ]]; then
30      if [[ -n "${WORKSPACE_HUB:-}" ]]; then
31          WS_HUB="$WORKSPACE_HUB"
33          WS_HUB="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
84  ERROR_PATTERNS=(
85      "(^|[[:space:]])ERROR:"
86      "fatal:"
87      "ModuleNotFoundError"
88      "Permission denied"
89      "Traceback"
90      "command not found"
91      "No such file or directory"
92  )
226 # Scan for errors in the most recent log (last 100 lines).
236 for pattern in "${ERROR_PATTERNS[@]}"; do
244 if [[ $ERRORS_FOUND -gt 0 ]]; then
247     STATUS="ERROR"
```

**Reproduction proofs** (verify-against-repo-state, 2026-06-13):
```
$ crontab -l | rg -n '^(WORKSPACE_HUB|LOG|REPO_ECOSYSTEM_HYGIENE_)|repo-ecosystem-hygiene|cron-health'
1:WORKSPACE_HUB=/mnt/local-analysis/workspace-hub
2:LOG=/mnt/local-analysis/workspace-hub/logs/quality/cron-wrapper.log
3:REPO_ECOSYSTEM_HYGIENE_PROBE_TIMEOUT_SEC=30
4:REPO_ECOSYSTEM_HYGIENE_REPO_TIMEOUT_SEC=120
24:45 5 * * * cd $WORKSPACE_HUB && bash scripts/monitoring/cron-health-check.sh >> $WORKSPACE_HUB/logs/quality/cron-health-$(date +\%Y\%m\%d).log 2>&1
43:35 5 * * * PATH=$HOME/.local/bin:$HOME/.npm-global/bin:$PATH; cd $WORKSPACE_HUB && bash scripts/cron/repo-ecosystem-hygiene-audit.sh >> $WORKSPACE_HUB/logs/quality/repo-ecosystem-hygiene-$(date +\%Y\%m\%d).log 2>&1
```

```
$ crontab -l | rg -n 'notification|logs/notifications|find logs/notifications'
38:30 4 * * * cd $WORKSPACE_HUB && find logs/notifications/ -name "*.jsonl" -mtime +7 -delete 2>/dev/null || true
```

```
$ UV_CACHE_DIR=.claude/state/uv-cache uv run --no-project python - <<'PY'
import json, os, subprocess
env = {**os.environ, "UV_CACHE_DIR": ".claude/state/uv-cache"}
res = subprocess.run(
    ["uv", "run", "--script", "scripts/cron/cron_apply.py", "--json"],
    text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, check=True,
)
data = json.loads(res.stdout)
print("status", data.get("status"))
print("has_new_text", "new_text" in data)
preserved = data.get("preserved") or []
print("preserved_env_lines", [line for line in preserved if line.startswith(("WORKSPACE_HUB=", "LOG=", "REPO_ECOSYSTEM_HYGIENE_"))])
selected = data.get("selected") or []
print("selected_count", len(selected))
print("selected_contains", {name: (name in selected) for name in ["repo-ecosystem-hygiene", "cron-health", "repository-sync", "solver-watch-results", "solver-dashboard"]})
print("conflicts_count", len(data.get("conflicts") or []))
PY
status dry-run
has_new_text False
preserved_env_lines ['WORKSPACE_HUB=/mnt/local-analysis/workspace-hub', 'LOG=/mnt/local-analysis/workspace-hub/logs/quality/cron-wrapper.log', 'REPO_ECOSYSTEM_HYGIENE_PROBE_TIMEOUT_SEC=30', 'REPO_ECOSYSTEM_HYGIENE_REPO_TIMEOUT_SEC=120']
selected_count 40
selected_contains {'repo-ecosystem-hygiene': True, 'cron-health': True, 'repository-sync': True, 'solver-watch-results': False, 'solver-dashboard': False}
conflicts_count 5
```

```
$ UV_CACHE_DIR=.claude/state/uv-cache uv run --no-project python - <<'PY'
import importlib.util
from pathlib import Path
repo=Path.cwd()
spec=importlib.util.spec_from_file_location('cron_transaction', repo/'scripts/cron/cron_transaction.py')
ct=importlib.util.module_from_spec(spec); spec.loader.exec_module(ct)
tasks=[{'id':'repo-ecosystem-hygiene','schedule':'35 5 * * *','command':'PATH=$HOME/.local/bin:$HOME/.npm-global/bin:$PATH; cd $WORKSPACE_HUB && bash scripts/cron/repo-ecosystem-hygiene-audit.sh >> $WORKSPACE_HUB/logs/quality/repo-ecosystem-hygiene-$(date +\\\\%Y\\\\%m\\\\%d).log 2>&1'}]
print('\n'.join(ct.render_block(tasks, ['daily-maintenance'])))
PY
# >>> workspace-hub managed (role: daily-maintenance) - generated by setup-cron.sh, do not edit >>>
35 5 * * * PATH=$HOME/.local/bin:$HOME/.npm-global/bin:$PATH; cd $WORKSPACE_HUB && bash scripts/cron/repo-ecosystem-hygiene-audit.sh >> $WORKSPACE_HUB/logs/quality/repo-ecosystem-hygiene-$(date +\%Y\%m\%d).log 2>&1
# <<< workspace-hub managed <<<
```

```
$ tmp=$(mktemp -d /tmp/cron-health-3057.XXXXXX)
$ # temp schedule contains one fresh repo-ecosystem-hygiene log with:
$ # task=repo-ecosystem-hygiene status=ERROR summary=git_probe_timeout
$ bash scripts/monitoring/cron-health-check.sh --workspace "$tmp"
[OK     ] repo-ecosystem-hygiene    last-run: 1h ago, errors: 0
[cron-health] 2026-06-13 | host: ace-linux-1 | tasks: 1 | healthy: 1 | problems: 0
rc=0
```

```
$ /usr/bin/time -f 'workspace-hub elapsed=%e rc=%x' timeout 20 git -C /mnt/local-analysis/workspace-hub status --porcelain=v1 --untracked-files=all >/tmp/issue3057-workspace-status.out
workspace-hub elapsed=11.81 rc=0

$ /usr/bin/time -f 'digitalmodel elapsed=%e rc=%x' timeout 20 git -C /mnt/local-analysis/digitalmodel status --porcelain=v1 --untracked-files=all >/tmp/issue3057-digitalmodel-status.out
digitalmodel elapsed=10.41 rc=0
```

```
$ UV_CACHE_DIR=.claude/state/uv-cache uv run --no-project python - <<'PY'
import yaml
from pathlib import Path
data = yaml.safe_load(Path('config/scheduled-tasks/schedule-tasks.yaml').read_text())
for task in data.get('tasks', []):
    cmd = task.get('command', '') or ''
    has_script = any(tok.startswith('scripts/') and (tok.endswith('.sh') or tok.endswith('.py')) for tok in cmd.split())
    has_placeholder = '$WORKSPACE_HUB' in cmd or '$LOG' in cmd
    if has_placeholder and not has_script:
        print(f"{task.get('id')}\t{cmd}")
PY
notification-purge    cd $WORKSPACE_HUB && find logs/notifications/ -name "*.jsonl" -mtime +7 -delete 2>/dev/null || true
```

```
$ UV_CACHE_DIR=.claude/state/uv-cache uv run --no-project python - <<'PY'
import json, os, subprocess
res = subprocess.run(
    ["uv", "run", "--script", "scripts/cron/cron_apply.py", "--json"],
    text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    env={**os.environ, "UV_CACHE_DIR": ".claude/state/uv-cache"}, check=True,
)
data = json.loads(res.stdout)
selected = set(data.get("selected") or [])
matches = [
    line for key in ("uncataloged", "preserved", "conflicts")
    for line in (data.get(key) or [])
    if isinstance(line, str) and ("notifications" in line or "notification" in line)
]
print("selected_has_notification_purge", "notification-purge" in selected)
print("out_of_block_notification_matches", len(matches))
PY
selected_has_notification_purge True
out_of_block_notification_matches 0
```

This host's current live crontab does not reproduce an out-of-block notification purge duplicate; the duplicate/re-add risk remains covered through the harness preserved-local variant in `config/workstations/harness-state-classes.yaml` and the apply-path shim tests below.

```
$ /usr/bin/time -f 'elapsed=%e rc=%x' env \
  REPO_ECOSYSTEM_HYGIENE_PROBE_TIMEOUT_SEC=30 \
  REPO_ECOSYSTEM_HYGIENE_REPO_TIMEOUT_SEC=120 \
  REPO_ECOSYSTEM_HYGIENE_TOTAL_TIMEOUT_SEC=480 \
  UV_CACHE_DIR=.claude/state/uv-cache \
  bash scripts/cron/repo-ecosystem-hygiene-audit.sh
task=repo-ecosystem-hygiene status=WARN artifact=/mnt/local-analysis/workspace-hub/.claude/state/repo-ecosystem-hygiene/latest.md state=/mnt/local-analysis/workspace-hub/.claude/state/repo-ecosystem-hygiene/latest.json ts=2026-06-13T22:12:34Z
elapsed=16.13 rc=0

$ UV_CACHE_DIR=.claude/state/uv-cache uv run --no-project python - <<'PY'
import json
data = json.load(open('.claude/state/repo-ecosystem-hygiene/latest.json'))
timeout_codes = [
    (repo.get('name'), finding.get('code'))
    for repo in data.get('repos', [])
    for finding in repo.get('findings', [])
    if finding.get('code') in {'git_probe_timeout', 'incomplete_due_to_deadline'}
]
print('generated_at', data.get('generated_at'))
print('status', data.get('status'))
print('repo_count', data.get('repo_count'), len(data.get('repos', [])))
print('incomplete_due_to_deadline', data.get('incomplete_due_to_deadline'))
print('timeout_codes', timeout_codes)
PY
generated_at 2026-06-13T22:12:34Z
status WARN
repo_count 17 17
incomplete_due_to_deadline False
timeout_codes []
```

Timing note: the 16.13s full-set run occurred after the standalone `git status` probes and may have benefited from warmed filesystem cache. It proves the 30/120/480 settings can complete on this host in a warm-cache state; it is not worst-case proof. Implementation closeout must capture one cold-cache or dropped-cache full-set timing. The two standalone probes total 22.2s for two repos, so a rough cold-cache expectation for the 17-repo governed set is around 170s if all repos behave like the two slowest sampled repos; that remains below the 480s total deadline but must be verified live.

```
$ tail -40 logs/quality/repo-ecosystem-hygiene-20260613.log
task=repo-ecosystem-hygiene status=ERROR artifact=... ts=2026-06-13T13:23:09Z
task=repo-ecosystem-hygiene status=WARN artifact=... ts=2026-06-13T13:27:54Z
task=repo-ecosystem-hygiene status=WARN artifact=... ts=2026-06-13T13:33:28Z

$ UV_CACHE_DIR=.claude/state/uv-cache uv run --no-project python - <<'PY'
import json
data=json.load(open('.claude/state/cron-health/2026-06-13.json'))
for task in data.get('tasks', []):
    if task.get('id') == 'repo-ecosystem-hygiene':
        print(task.get('id'), task.get('status'), task.get('details'), task.get('errors_found'))
PY
repo-ecosystem-hygiene OK last-run: 0h ago, errors: 0 0
```

Current distinct source count: 10+ (issue body, related issues, prior plan, scheduled-task registry, cron transaction, cron apply, setup-cron, hygiene audit, cron-health, tests).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-06-13-issue-3057-cron-hygiene-hardening.md` |
| Plan index | `docs/plans/README.md` |
| Shared cron renderer | `scripts/cron/cron_render.py` |
| Transactional cron apply | `scripts/cron/cron_apply.py` |
| Pure crontab core | `scripts/cron/cron_transaction.py` |
| Legacy cron installer parity reference | `scripts/cron/setup-cron.sh` |
| Schedule catalog | `config/scheduled-tasks/schedule-tasks.yaml` |
| Repo hygiene audit | `scripts/cron/repo-ecosystem-hygiene-audit.sh` |
| Cron health monitor | `scripts/monitoring/cron-health-check.sh` |
| Cron apply tests | `tests/cron/test_cron_apply.py` |
| Cron render tests | `tests/cron/test_cron_render.py` |
| Cron transaction tests | `tests/cron/test_cron_transaction.py` |
| Schedule tests | `scripts/cron/tests/test_validate_schedule.py` |
| Hygiene tests | `scripts/cron/tests/test_repo_ecosystem_hygiene_audit.py` |
| Cron-health tests | `scripts/monitoring/tests/test_cron_health_check.sh` |
| Failed plan reviews | `scripts/review/results/2026-06-13-plan-3057-r1-*`, `scripts/review/results/2026-06-13-plan-3057-r2-*`, `scripts/review/results/2026-06-13-plan-3057-r3/`, `scripts/review/results/2026-06-13-plan-3057-r4/`, `scripts/review/results/2026-06-13-plan-3057-r6/`, `scripts/review/results/2026-06-13-plan-3057-r7/`, `scripts/review/results/2026-06-13-plan-3057-r8/`, `scripts/review/results/2026-06-13-plan-3057-r9/`, `scripts/review/results/2026-06-13-plan-3057-r10/`, `scripts/review/results/2026-06-13-plan-3057-r11/`, `scripts/review/results/2026-06-13-plan-3057-r12/`, `scripts/review/results/2026-06-13-plan-3057-r13/`, `scripts/review/results/2026-06-13-plan-3057-r14/`, `scripts/review/results/2026-06-13-plan-3057-r15/`, `scripts/review/results/2026-06-13-plan-3057-r16/` |
| Superseded no-MAJOR plan reviews | `scripts/review/results/2026-06-13-plan-3057-r5/` |
| Final no-MAJOR plan reviews | `scripts/review/results/2026-06-13-plan-3057-r17/` |

---

## Deliverable

The daily repo-hygiene cron path will be self-sufficient from the catalog-rendered crontab, with one shared cron renderer used by both `setup-cron.sh` and `cron_apply.py`, expanded executable managed command lines in the applied/dry-run `new_text`, alias-aware effective schedules for `schedule_by_machine` tasks, raw-and-rendered catalog matching for placeholder fallback tasks, durable tracked hygiene probe timeout defaults, and cron-health detection based on the latest hygiene-specific marker so a newer successful audit clears older hygiene errors.

This issue will also align `cron_apply.py` legacy machine-pin matching with setup-cron's physical-machine targeting: transactional selection will preserve existing role semantics and additionally treat `machines:` entries matching the canonical machine id, hostname, or aliases as legacy matches. `setup-cron.sh` selection will remain machine-token-only; shared behavior between setup-cron and cron_apply is limited to rendering selected task schedule/command text.

---

## Pseudocode

```
function resolve_machine(registry, machine_id_or_hostname):
    wanted = lower(machine_id_or_hostname)
    for name, machine in registry.machines:
        candidates = [name, machine.hostname] + machine.hostname_aliases
        if wanted in lower(candidates):
            return name, machine
    return machine_id_or_hostname, {}

function cron_context_for_machine(repo_root, registry, machine_id_or_hostname):
    # Match setup-cron.sh semantics: WORKSPACE_HUB is the actual checkout path
    # (or live env override), not registry.workspace_root. Also share
    # setup-cron's alias-aware machine resolution before reading schedule_variant.
    machine_name, machine = resolve_machine(registry, machine_id_or_hostname)
    workspace_hub = env.WORKSPACE_HUB or str(repo_root)
    variant = machine.schedule_variant or "contribute"
    if variant == "full":
        log = workspace_hub + "/logs/quality/cron-wrapper.log"
    else:
        log = "/tmp/workspace-hub-cron.log"
    machine_tokens = lower([machine_name, machine.hostname] + machine.hostname_aliases)
    if requested machine tokens match the live host's machine tokens:
        hostname_short = live hostname
    else:
        hostname_short = machine.hostname
    schedule_tokens = lower([hostname_short] + sorted(machine_tokens))
    return {"machine": machine_name, "machine_tokens": machine_tokens, "schedule_tokens": schedule_tokens, "WORKSPACE_HUB": workspace_hub, "LOG": log, "variant": variant}

function machine_roles(registry, machine_id_or_hostname):
    machine_name, machine = resolve_machine(registry, machine_id_or_hostname)
    roles = machine.harness_profile.roles or []
    return machine_name, roles

function render_catalog_task_for_cron(task, context):
    clone task
    # Match setup-cron.sh's current schedule_by_machine precedence:
    # hostname first, then sorted token set.
    schedule = first task.schedule_by_machine[token] where token in context["schedule_tokens"], else task.schedule
    clone.schedule = schedule
    command = task.command
    replace "$WORKSPACE_HUB" with context["WORKSPACE_HUB"]
    replace "$LOG" with context["LOG"]
    return clone with rendered schedule and rendered command

function render_cron_line(rendered_task):
    # Canonical line separator for both setup-cron and cron_transaction render_block:
    # exactly one ASCII space between the effective schedule string and command.
    return rendered_task.schedule + " " + rendered_task.command

function setup_cron_install(...):
    context = cron_context_for_machine(repo_root, registry, machine_id)
    selected_by_hostname = select_machine_pinned_cron_tasks(catalog.tasks, context.machine_tokens)
    for task in selected_by_hostname:
        rendered = render_catalog_task_for_cron(task, context)
        print render_cron_line(rendered)

function select_machine_pinned_cron_tasks(tasks, machine_tokens):
    # Preserve setup-cron.sh selection semantics: cron scheduler only, and
    # machines must intersect the current physical-machine token set.
    for task in tasks:
        if task.scheduler exists and task.scheduler != "cron":
            continue
        if lower(task.machines) intersects machine_tokens:
            include task

function select_tasks(tasks, roles, machine_id_or_tokens):
    # Backward-compatible extension of cron_transaction.select_tasks:
    # existing string callers are normalized to a one-item token set.
    machine_tokens = normalize_machine_tokens(machine_id_or_tokens)
    conflicts = []
    for task in tasks:
        if task.scheduler exists and task.scheduler != "cron":
            continue
        role_match = task.roles intersects roles
        has_machines = task.machines is a non-empty list
        legacy_match = lower(task.machines) intersects machine_tokens
        legacy_excludes = has_machines and not legacy_match
        if role_match and legacy_excludes:
            if task.roles_authoritative is true:
                include task
                append conflict "role-match vs legacy machines exclusion; roles_authoritative=True -> roles win"
            else:
                append conflict "role-match vs legacy machines exclusion; roles_authoritative not set -> legacy wins"
            continue
        if role_match or legacy_match:
            include task
    return selected tasks, conflicts

function preserved_fingerprint_entries(state_classes):
    # Backward-compatible loader for preserved_external + preserved_local.
    # Keep each entry's fingerprint plus sibling metadata such as owner,
    # note, and optional catalog_task_id; do not return bare fingerprints only.
    for entry in preserved_external + preserved_local:
        include {
          "fingerprint": entry.fingerprint,
          "owner": entry.owner,
          "catalog_task_id": entry.catalog_task_id or null,
        }

function normalize_preserved_entry(entry):
    if entry has key "fingerprint":
        return {"fingerprint": entry.fingerprint, "owner": entry.owner or null, "catalog_task_id": entry.catalog_task_id or null}
    # Backward compatibility for existing classify_line callers/tests that pass
    # bare fingerprint dicts such as {"cwd_contains": ..., "script_basename": ...}.
    return {"fingerprint": entry, "owner": null, "catalog_task_id": null}

function classify_line_detail(line, catalog_keys, preserved_entries, catalog_owned_task_ids):
    if line is blank/comment/env:
        return {"kind": "ignore"}
    for raw_entry in preserved_entries:
        entry = normalize_preserved_entry(raw_entry)
        if match_fingerprint(line, entry.fingerprint):
            if entry.catalog_task_id in catalog_owned_task_ids:
                return {"kind": "cataloged", "reason": "catalog_owned_duplicate", "catalog_task_id": entry.catalog_task_id}
            return {"kind": "preserved_external", "entry": entry}
    if any catalog key is substring of line:
        return {"kind": "cataloged"}
    return {"kind": "uncataloged"}

function classify_line(line, catalog_keys, preserved_entries):
    # Preserve the current string-returning public API for existing callers by
    # delegating to classify_line_detail with an empty catalog-owned task set.
    return classify_line_detail(line, catalog_keys, preserved_entries, catalog_owned_task_ids=set()).kind

function catalog_command_keys(tasks, fallback_mode="full-command"):
    # New shared builder replacing cron_apply.catalog_commands and
    # cron-audit.load_catalog_commands. Prefer scripts/*.sh|*.py tokens;
    # fallback_mode="full-command" uses the full normalized command, not [:60].
    for task in tasks:
        include script token if present, else normalized full command

function plan_cutover(current_crontab, selected_tasks, roles, catalog_keys, preserved_entries, selected_task_ids=set()):
    # Backward-compatible signature widening: existing five-argument callers
    # behave exactly as before because selected_task_ids defaults to empty.
    classify non-managed lines with classify_line_detail(..., selected_task_ids)
    preserve ignore/preserved_external lines; drop cataloged/catalog_owned_duplicate lines; fail closed on uncataloged lines
    render managed block with render_cron_line for each selected task

function run_cutover(...):
    load catalog, registry, state classes
    canonical_machine_id, roles = machine_roles(registry, machine_id)
    context = cron_context_for_machine(REPO, registry, canonical_machine_id)
    select tasks and conflicts with select_tasks(tasks, roles, context.machine_tokens)
    rendered_selected = map(render_catalog_task_for_cron, selected, context)
    raw_catalog_keys = catalog_command_keys(catalog.tasks, fallback_mode="full-command")
    rendered_catalog = map(render_catalog_task_for_cron, catalog.tasks, context)
    rendered_catalog_keys = catalog_command_keys(rendered_catalog, fallback_mode="full-command")
    catalog_keys = stable_dedupe(raw_catalog_keys + rendered_catalog_keys)
    preserved_entries = preserved_fingerprint_entries(state_classes)
    selected_task_ids = set(task.id for task in rendered_selected)
    plan = plan_cutover(current_crontab, rendered_selected, roles, catalog_keys, preserved_entries, selected_task_ids=selected_task_ids)
    include actual plan["new_text"] in --json dry-run result
    include conflicts from select_tasks in --json dry-run/apply result
    use canonical_machine_id for result metadata and backup filename
    assert managed command lines contain no unresolved "$WORKSPACE_HUB" or "$LOG"
    assert selected schedule_by_machine tasks use the alias-aware effective schedule
    preserve existing external/ignore lines exactly, except preserved_local entries explicitly annotated with catalog_task_id and selected in the managed block classify as cataloged/catalog_owned_duplicate and are deduped from out-of-block preserved lines
    compute the post-apply preservation guard with classify_line_detail(..., catalog_owned_task_ids=selected_task_ids), so deliberately deduped catalog-owned selected lines are not counted in the "must remain byte-identical" Counter
    keep notification-purge fingerprint but annotate it catalog_task_id=notification-purge so loose live variants remain safe, the selected managed output is not duplicated, and --apply returns status=applied rather than rolled-back
    assert expanded and unexpanded legacy/out-of-block catalog lines for notification-purge classify as catalog-owned duplicate, are dropped from preserved out-of-block lines, are excluded from the post-apply preservation need counter, and result in exactly one managed notification-purge line

function cron_audit(...):
    read live crontab with the same fail-closed semantics as cron_apply:
      if crontab -l exits nonzero with stderr and no stdout, return ok=false / nonzero instead of treating it as empty crontab
    resolve target machine with the same alias-aware context as cron_apply
    select target-machine tasks with select_tasks(tasks, roles, context.machine_tokens)
    selected_task_ids = set(task.id for task in selected)
    use the same shared raw+rendered catalog key builder as cron_apply
    load the same metadata-preserving fingerprint entries as cron_apply
    classify current crontab with classify_line_detail using selected_task_ids as catalog_owned_task_ids, so audit/apply agree: selected catalog-owned duplicates classify cataloged, unselected catalog-owned preserved_local lines stay preserved_external

function hygiene_status_defaults():
    set tracked source defaults:
      PROBE_TIMEOUT_SEC = 30
      REPO_TIMEOUT_SEC = 120
      TOTAL_TIMEOUT_SEC = 480 and assert it is below the schedule-derived hygiene->cron-health gap
    acceptance requires the live governed repo set to finish inside TOTAL_TIMEOUT_SEC

function cron_health_check_task_log(task_id, recent_tail):
    if task_id == "repo-ecosystem-hygiene":
        latest_hygiene_marker = empty
        for each line in recent_tail:
            if bash [[ line =~ ^task=repo-ecosystem-hygiene[[:space:]]+status=(OK|WARN|ERROR)([[:space:]]|$) ]]:
                latest_hygiene_marker = BASH_REMATCH[1]
            if bash [[ line =~ ^ERROR:[[:space:]]+repo-ecosystem-hygiene[[:space:]]+execution_failed([[:space:]]|$) ]]:
                latest_hygiene_marker = "ERROR"
        filter recognized hygiene-specific marker lines before generic ERROR_PATTERNS scan
        if latest_hygiene_marker == "ERROR" and current task status is OK:
            mark task ERROR
        if latest_hygiene_marker == "ERROR" and current task status is already STALE or MISSING:
            keep existing status and do not double-count; include marker detail
        if latest_hygiene_marker is "WARN" or "OK":
            do not mark execution failure
    generic non-hygiene ERROR_PATTERNS tokens still mark ERROR
    merge with stale/missing status as existing code does
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/cron/cron_render.py` | Shared pure cron renderer for machine context, hostname-first effective `schedule_by_machine` selection, `$WORKSPACE_HUB`, `$LOG`, `full`/`contribute` log target selection, canonical one-ASCII-space cron-line rendering, and optional CLI use by shell scripts. It is a leaf module: it imports no `cron_transaction.py` helpers, while `cron_transaction.py` may import render helpers from it. |
| Modify | `scripts/cron/cron_apply.py` | Replace `main()` hostname-only resolution with alias-aware canonical resolution before `machine_roles`, call the backward-compatible extended selector with machine tokens, use the shared renderer before transactional cutover, use the canonical machine id for metadata/backups, use shared catalog keys for `plan_cutover` and the post-cutover preservation recheck, retain `catalog_task_id` metadata from preserved fingerprints, pass selected task ids into cutover/classification, exclude selected catalog-owned duplicates from the post-apply preservation Counter, and expose actual rendered `plan["new_text"]` in JSON dry-run. |
| Modify | `scripts/cron/cron_transaction.py` | Extend `select_tasks` in place to accept string or token-set machine identity while preserving existing string-call behavior; add net-new `scheduler != cron` filtering before selection/conflict reporting for the Linux cron path; preserve `roles_authoritative` conflict semantics and conflict reporting for cron-scheduler tasks; add canonical shared raw+rendered `catalog_command_keys(tasks, fallback_mode="full-command")` builder imported by both `cron_apply.py` and `cron-audit.py`, replacing `cron_apply.catalog_commands` / `cron-audit.load_catalog_commands` call sites; add a backward-compatible detail classifier that accepts both existing bare fingerprint dicts and metadata entries, retains preserved-fingerprint metadata, and treats selected `catalog_task_id` duplicates as cataloged/catalog-owned rather than preserved_external; widen `plan_cutover` with optional/defaulted `selected_task_ids=set()` so existing five-argument callers keep working; use the shared one-space cron-line renderer while preserving top-level env lines verbatim and making rendered managed commands self-sufficient. |
| Modify | `scripts/cron/cron-audit.py` | Resolve the same target-machine context as transactional cutover, select the target-machine task ids, and use the same shared raw+rendered catalog-key builder plus metadata-preserving fingerprint loader/detail classifier so pre-cutover audit and apply classify placeholder fallback lines identically; keep a `--json` script-entry smoke gate. |
| Modify | `config/workstations/harness-state-classes.yaml` | Keep the loose `notification-purge` preserved-local fingerprint for live variants, correct its stale dedupe comment, and annotate/narrow it as catalog-owned (`catalog_task_id: notification-purge`) so cutover can dedupe the preserved copy when a selected managed task is rendered. |
| Modify | `scripts/cron/setup-cron.sh` | Keep setup-cron's selection machine-token-only, but consume the shared renderer for effective schedule and command expansion while preserving current hostname-first schedule semantics. |
| Modify | `scripts/cron/repo-ecosystem-hygiene-audit.sh` | Make timeout policy durable with tracked defaults of 30s probe and 120s repo budget while preserving dirty-worktree visibility. |
| Modify | `scripts/monitoring/cron-health-check.sh` | Detect only the latest hygiene-specific marker for `status=ERROR`; allow newer `status=WARN`/`status=OK` to clear older hygiene-specific failures while preserving generic error detection; replace hardcoded `/home/vamsee/.local/bin/uv` calls with PATH-based `uv` after the script's existing PATH setup. |
| Modify | `tests/cron/test_cron_apply.py` | Add tests for rendered applied `new_text`, JSON dry-run evidence, clean/no-env crontabs, and second-cutover idempotency. |
| Create | `tests/cron/test_cron_render.py` | Unit tests for shared renderer context, placeholder expansion, variant fallback, and parity fixture used by both setup-cron and cron_apply. |
| Modify | `tests/cron/test_cron_transaction.py` | Add tests for preserving `WORKSPACE_HUB=` and `LOG=` env lines verbatim, string-call backward compatibility, token-set selection, and conflict reporting. |
| Modify | `tests/cron/test_a1_preserved.py` | Extend the existing ace-linux-1 preservation regression so both expanded and unexpanded `notification-purge` fallback forms remain non-uncataloged after raw+rendered catalog keys. |
| Modify | `tests/cron/test_cron_audit.py` | Add audit/apply parity coverage for raw+rendered catalog keys and placeholder fallback lines. |
| Modify | `scripts/cron/tests/test_validate_schedule.py` | Assert setup dry-run goes through the shared renderer for both `$WORKSPACE_HUB` and `$LOG`, and preserve existing hygiene ordering/log/staleness contract. |
| Modify | `scripts/cron/tests/test_repo_ecosystem_hygiene_audit.py` | Add tests for 30/120 timeout defaults and status probe behavior. |
| Modify | `scripts/monitoring/tests/test_cron_health_check.sh` | Add latest-evidence-line positive/negative tests, including older ERROR followed by newer WARN/OK. |
| Update | `docs/plans/README.md` | Maintain this plan's index row and status. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_cron_render_matches_setup_cron_context_semantics` | Shared renderer matches setup-cron's context, resolution, and effective-schedule rules. | Registry fixture with `schedule_variant=full`, hostname aliases, `schedule_by_machine`, missing-variant machine, and env/no-env workspace path cases. | `WORKSPACE_HUB` uses actual checkout/env override; aliases resolve to the registered machine before variant lookup; `schedule_by_machine` precedence is hostname first, then sorted machine tokens; missing variant falls back to `contribute`; `$LOG` maps to `cron-wrapper.log` for `full` and `/tmp/workspace-hub-cron.log` otherwise. |
| `test_cron_render_schedule_precedence_uses_live_hostname_first` | Schedule precedence matches setup-cron's `hostname -s` behavior, not only registry hostname. | Fixture where live hostname is an alias with a distinct `schedule_by_machine` value from canonical/registry hostname. | Renderer chooses the live hostname value first, then sorted machine-token fallback. |
| `test_cron_render_non_live_machine_uses_registry_hostname_for_schedule_precedence` | Cross-machine preview does not accidentally use the current host's schedule stagger. | Run renderer from an ace-linux-1/live-host context while requesting `--machine dev-secondary`, with a fixture where `provider-dream-bridge` has distinct `schedule_by_machine` values for `ace-linux-1`, `dev-primary`, and `dev-secondary`. | Renderer uses dev-secondary's resolved registry hostname/token precedence, not the live ace-linux-1 hostname value. |
| `test_cron_render_uses_current_ace_linux_1_schedule_golden_values` | Effective-schedule tests anchor to pre-refactor behavior, not tautological shared-module parity. | Real `provider-dream-bridge` and `hermes-claude-bridge` entries with context for `dev-primary` / `ace-linux-1`. | Renderer returns `5 4 * * *` and `25 4 * * *`, matching setup-cron's current hostname-first behavior on ace-linux-1. |
| `test_cron_render_line_separator_is_canonical` | Full cron-line byte parity has an explicit separator contract. | Rendered task with five-field schedule and command, plus source/static checks for setup-cron and cron_transaction. | Shared renderer returns `"<schedule> <command>"` with exactly one ASCII space between schedule and command; both setup-cron dry-run and `cron_transaction.render_block` use the shared line renderer. |
| `test_cron_render_is_leaf_module_no_cron_transaction_import` | Shared rendering helpers do not introduce an import cycle. | Source/import inspection of `scripts/cron/cron_render.py`, `scripts/cron/cron_transaction.py`, and `scripts/cron/cron-audit.py --json`. | `cron_render.py` imports no `cron_transaction.py`; `cron_transaction.py` can import render helpers; `cron-audit.py --json` smoke catches import-cycle regressions. |
| `test_cron_apply_resolves_hostname_alias_before_role_selection` | Alias resolution happens before role lookup, task selection, and backup naming in `cron_apply.py`. | `--machine vamsee-linux1` against a fixture matching registry alias `dev-primary`. | Selected role-managed tasks are planned; result is not `status=skip`; metadata/backups use canonical `dev-primary`. |
| `test_cron_apply_selects_machine_pinned_tasks_for_hostname_tokens` | Transactional cutover does not drop tasks selected by setup-cron's physical-machine path. | ace-linux-1/dev-primary context and real `solver-watch-results` / `solver-dashboard` task shapes pinned to `machines: [ace-linux-1]`. | `cron_apply.py --json` selected/new_text includes those tasks even though their roles are not `control-plane`. |
| `test_cron_apply_does_not_select_machine_excluded_role_matches` | Token-aware selection preserves existing legacy exclusion semantics. | dev-secondary/ace-linux-2 context plus `notification-purge`, `solver-watch-results`, and `solver-dashboard` shapes whose roles match dev-secondary but whose `machines:` exclude it. | Tasks are not selected; conflicts remain reported unless `roles_authoritative=True`. |
| `test_cron_apply_filters_non_cron_schedulers_before_role_selection` | Linux cron rendering does not pull in Windows Task Scheduler entries through role matches or conflict reporting. | ace-linux-1/dev-primary context plus `provider-dream-bridge-win`, `hermes-claude-bridge-win`, `win-repository-sync`, and `win-session-state-commit`, with a current-baseline fixture showing these tasks previously appeared as machine-exclusion conflicts. | These tasks are excluded from selected/new_text and from conflict entries; existing conflict reporting remains covered by separate cron-scheduler role/machine-exclusion fixtures. |
| `test_select_tasks_accepts_existing_string_machine_id_callers` | Extending selector identity is backward-compatible for existing callers and the module self-check. | Existing string `machine_id` fixtures from `tests/cron/test_cron_transaction.py` and the `cron_transaction.py` self-check shape. | String callers preserve current behavior; focused verification also runs `UV_CACHE_DIR=.claude/state/uv-cache uv run --no-project python scripts/cron/cron_transaction.py`. |
| `test_classify_line_accepts_existing_bare_fingerprint_dicts_after_metadata_extension` | Extending fingerprint classification to metadata entries does not break existing callers. | Existing `tests/cron/test_cron_transaction.py` deckhand fixture that passes `fps = [{"cwd_contains": "/deckhand", "script_basename": "member-audit-cron.py"}]` directly to `classify_line`. | The line still classifies `preserved_external`; metadata-entry fixtures also classify correctly; `plan_cutover` does not abort on genuine external lines. |
| `test_plan_cutover_accepts_existing_five_argument_callers_after_selected_task_ids_extension` | Extending cutover classification with selected task ids does not break existing direct callers. | Existing `tests/cron/test_cron_transaction.py` five-argument `plan_cutover(current, selected, roles, catalog_keys, fingerprints)` fixtures plus a metadata-entry fixture using the optional `selected_task_ids` keyword. | Five-argument calls produce the same result as before; keyword-selected catalog-owned duplicates dedupe as intended. |
| `test_setup_cron_and_cron_apply_use_shared_renderer_for_same_task` | The original rendering divergence and schedule drift classes are covered cross-path without changing setup-cron selection semantics. | Fixtures selected by both setup-cron's machine-token path and cron_apply's role/legacy path, including a `schedule_by_machine` override. | Full rendered cron lines are byte-identical for common selected tasks with the canonical one-space separator; setup-cron remains machine-token-only and does not gain role selection. |
| `test_setup_cron_delegates_placeholder_rendering_to_shared_renderer` | Shared-renderer usage is structural, not only black-box parity. | Source inspection of `scripts/cron/setup-cron.sh` and `scripts/cron/cron_render.py`. | `setup-cron.sh` invokes the shared renderer/CLI and no longer carries independent `command.replace('$WORKSPACE_HUB', ...)` or `command.replace('$LOG', ...)` expansion logic. |
| `test_run_cutover_renders_applied_new_text_without_unresolved_workspace_placeholders` | Transactional cutover renders selected catalog commands into executable crontab lines. | Clean/no-env crontab and catalog command with `$WORKSPACE_HUB` and `$LOG`. | Applied `new_text` managed command lines contain concrete workspace/log paths; no unresolved `$WORKSPACE_HUB`/`$LOG` remains in managed command lines. |
| `test_plan_cutover_preserves_workspace_hub_and_log_env_lines_verbatim` | Existing live env lines remain preserved by transactional apply. | Current crontab containing `WORKSPACE_HUB=...` and `LOG=...` outside managed block. | Plan/apply keeps exact env lines and does not duplicate/drop them. |
| `test_run_cutover_second_pass_is_idempotent_after_expansion` | Expanded managed block does not break second transactional cutover. | First cutover output fed into a second dry-run/apply plan, including `notification-purge` and the canonical one-space cron-line separator. | Second plan does not abort as uncataloged, does not duplicate managed lines, and raw/rendered fallback command keys remain stable despite schedule-command separator normalization. |
| `test_preserved_fingerprint_entries_retain_catalog_task_id_metadata` | Catalog-owned dedupe metadata is available to both cutover and audit, not discarded by YAML loaders. | `preserved_local` fixture with `fingerprint`, `owner`, `note`, and `catalog_task_id: notification-purge`. | `cron_apply.py` and `cron-audit.py` loaders preserve `catalog_task_id`; bare-fingerprint legacy callers still work through normalization. |
| `test_notification_purge_catalog_owned_line_is_deduped_without_apply_rollback` | Catalog-owned preserved-local fallback lines do not survive as duplicate out-of-block lines and do not trip the post-apply preservation guard. | `run_cutover(..., apply=True, _read/_write shims, _daemons=[], allow_live_reload=True)` with current ace-linux-1 `$WORKSPACE_HUB` line and absolute-path fixture variants, loose fingerprint annotated with `catalog_task_id: notification-purge`, plus selected catalog `notification-purge` task. | Result status is `applied`, not `rolled-back`; the original out-of-block line is absent from the final crontab; exactly one managed `notification-purge` line remains; the post-apply preservation Counter still protects unrelated preserved/ignore lines. |
| `test_cron_audit_and_cron_apply_share_rendered_catalog_keys_and_fingerprint_metadata` | Pre-cutover audit and transactional apply classify placeholder fallback lines consistently for the target machine. | Raw and rendered `notification-purge` forms plus another fallback-keyed command, a catalog-owned preserved fingerprint, and dev-primary/dev-secondary target contexts. | `cron-audit.py` and `cron_apply.py` use the same shared raw+rendered key builder, preserve `catalog_task_id`, selected dev-primary notification-purge forms classify cataloged/catalog-owned in both paths, and unselected dev-secondary forms remain preserved_external in both paths. |
| `test_cron_audit_json_cli_smoke_uses_shared_classifier` | The fail-closed script entrypoint still imports and runs after moving shared helpers. | `UV_CACHE_DIR=.claude/state/uv-cache uv run --script scripts/cron/cron-audit.py --json` on an implementing host with readable crontab plus a fixture-supported monkeypatch for restricted CI. | Live-host command exits `0` for recognized lines and emits JSON using the shared classifier; restricted-context fixture verifies import/script metadata without requiring live crontab access. |
| `test_cron_audit_fails_closed_on_unreadable_crontab` | Audit does not silently pass on permission-denied or otherwise unreadable crontab. | Monkeypatched `crontab -l` result with nonzero return code, empty stdout, and stderr containing `Permission denied`; compare `cron_apply.py`'s `CronReadError` behavior. | `cron-audit.py --json` emits `ok=false` (or exits nonzero per chosen CLI contract) and surfaces stderr/reason instead of auditing an empty crontab as OK. |
| `test_all_fallback_catalog_keys_are_unique_nonempty_and_full_command_based` | The `[:60]` to full-command fallback change is safe beyond `notification-purge`. | All catalog tasks lacking a `scripts/*.sh|*.py` token, raw and rendered. | Raw/rendered fallback keys are non-empty, full-command based, and do not collide within the current catalog. |
| `test_setup_cron_dry_run_expands_workspace_hub_and_log` | Legacy installer remains semantic parity reference. | Hostname alias fixture for `vamsee-linux1`. | Dry-run output expands both `$WORKSPACE_HUB` and `$LOG` in task command lines where those placeholders are expected to be concrete. |
| `test_json_dry_run_includes_actual_rendered_new_text` | `cron_apply.py --json` can prove executability from the actual transactional plan output. | Dry-run with hygiene and repository-sync selected. | JSON includes rendered `new_text` from `plan_cutover`; command lines have no unresolved `$WORKSPACE_HUB`/`$LOG`. |
| `test_repo_hygiene_timeout_defaults_are_production_safe` | Timeout policy is durable in tracked source and derives its schedule margin from the catalog. | Source/default inspection plus parsing `repo-ecosystem-hygiene` and `cron-health` schedules. | Probe/repo defaults are exactly `30`/`120`, total timeout remains `480`, the actual hygiene-to-cron-health gap is computed from `schedule-tasks.yaml`, and total timeout is less than that gap. |
| `test_governed_repo_names_includes_required_optional_and_non_tier1` | Full governed repo-set coverage is pinned by automated tests, not only live closeout proof. | Registry fixture with required, optional, and `non_tier1_machine_access_current` buckets. | Hygiene audit repo enumeration includes all three buckets, not only `tier1_baseline.required`. |
| `test_status_short_probe_uses_default_timeout_budget` | Status probe behavior uses the documented default budget. | Shimmed slow `git status` that finishes inside 30s but after 10s. | No `git_probe_timeout` under default env; a deliberately lower override still reports `git_probe_timeout`. |
| `test_cron_health_detects_latest_repo_hygiene_status_error` | Latest hygiene evidence line with `status=ERROR` fails cron-health. | Temp schedule/log where the latest matching line is `task=repo-ecosystem-hygiene status=ERROR`. | Output reports `[ERROR] repo-ecosystem-hygiene`; exit code `1`; JSON task status `ERROR`. |
| `test_cron_health_latest_warn_clears_older_status_error` | Older hygiene `status=ERROR` does not keep cron-health red after a newer non-error run. | Temp schedule/log with older `status=ERROR` followed by newer `status=WARN` or `status=OK`. | Output remains `[OK]` for the task when no generic errors/staleness exist; exit code `0`. |
| `test_cron_health_latest_status_clears_older_execution_failed_marker` | Older hygiene execution failure marker does not keep cron-health red after a newer successful audit. | Temp schedule/log with older `ERROR: repo-ecosystem-hygiene execution_failed ...` followed by newer `task=repo-ecosystem-hygiene status=WARN` or `status=OK`. | Output remains `[OK]` for the task when no newer generic non-hygiene errors/staleness exist; exit code `0`. |
| `test_cron_health_latest_execution_failed_marker_still_fails` | A latest execution failure remains a cron-health failure. | Temp schedule/log whose latest hygiene-specific marker is `ERROR: repo-ecosystem-hygiene execution_failed ...`. | Output reports `[ERROR] repo-ecosystem-hygiene`; exit code `1`. |
| `test_cron_health_hygiene_error_respects_existing_stale_or_missing_status` | Hygiene-marker escalation does not double-count or clobber existing STALE/MISSING status. | Temp schedule/log where repo-hygiene is already stale or missing and also has an older/newer hygiene `status=ERROR` marker. | Problem count increments once; existing STALE/MISSING precedence remains explicit. |
| `test_cron_health_marker_filter_preserves_unrelated_generic_errors` | Hygiene-specific marker filtering is line-exact and does not hide unrelated failures. | Temp hygiene log with an older recognized `execution_failed` marker, newer `status=OK`, and a separate non-marker `Traceback` or `ERROR:` line. | Task remains `[ERROR]`; only recognized marker lines are filtered before generic scan. |
| `test_cron_health_generic_error_patterns_still_work` | Existing generic error detection is not regressed. | Existing cron-health fixture with `ERROR:`/`Traceback`. | Task still reports `ERROR` and exits nonzero. |
| `test_cron_health_uses_path_uv_not_user_absolute_path` | Cron-health remains portable across cron users/machines. | Source inspection and shell fixture with `uv` available on PATH but no `/home/vamsee/.local/bin/uv`. | Script invokes `uv` from PATH and contains no hardcoded `/home/vamsee/.local/bin/uv`. |
| `test_validate_schedule_repo_hygiene_contract` | Schedule catalog still carries required ordering/log/staleness fields. | `config/scheduled-tasks/schedule-tasks.yaml`. | Hygiene remains before cron-health, log glob matches redirect, stale threshold remains `23`. |

---

## Acceptance Criteria

- [ ] On the implementing host with readable crontab access, `UV_CACHE_DIR=.claude/state/uv-cache uv run --script scripts/cron/cron_apply.py --json` includes the actual rendered `new_text` from `plan_cutover`, proving generated managed command lines can run without manual `WORKSPACE_HUB` / `LOG` edits, use alias-aware hostname-first `schedule_by_machine` values where defined, and include tasks selected by role or machine-token pins. Restricted CI/Codex contexts must use a hermetic `run_cutover` fixture with `_read`/`_write` shims for the same assertions rather than treating live `crontab -l` permission failure as a plan failure.
- [ ] Existing external/preserved crontab lines remain preserved by transactional apply, including existing top-level env lines, except for selected catalog-owned `preserved_local` duplicates explicitly annotated with `catalog_task_id` and replaced by the managed block.
- [ ] A clean/no-env crontab fixture receives expanded managed command lines and a second transactional run remains idempotent.
- [ ] Placeholder commands without a `scripts/*.sh|*.py` catalog token, including `notification-purge`, classify both expanded and unexpanded legacy/out-of-managed-block lines consistently across `cron-audit.py` and `cron_apply.py`; selected target-machine cases dedupe as catalog-owned, and unselected target-machine cases remain preserved_external in both paths.
- [ ] `notification-purge` is not duplicated: the loose preserved-local fingerprint is annotated/narrowed as catalog-owned, `catalog_task_id` metadata is retained by both apply and audit loaders, absolute-path and `$WORKSPACE_HUB` legacy forms are deduped from out-of-block preserved lines only when the catalog task is selected, exactly one managed `notification-purge` line appears in `plan["new_text"]`, and an apply-path shim returns `status=applied` rather than `status=rolled-back`.
- [ ] `cron_apply.py --machine vamsee-linux1 --json` resolves the registry hostname alias before role lookup, does not return `status=skip`, and uses canonical `dev-primary` for result metadata and backup naming.
- [ ] `provider-dream-bridge` and `hermes-claude-bridge` keep their ace-linux-1 `schedule_by_machine` values (`5 4 * * *` and `25 4 * * *`) in `cron_apply.py --json` / rendered `new_text`, preventing silent 5-minute retiming.
- [ ] Cross-machine preview uses the requested machine's registry hostname/token precedence rather than the current host's live hostname; e.g. `--machine dev-secondary` run from ace-linux-1 does not emit ace-linux-1's `provider-dream-bridge` stagger.
- [ ] Machine-pinned tasks selected by setup-cron on ace-linux-1, including `solver-watch-results` and `solver-dashboard`, remain selected/rendered by `cron_apply.py` and are not dropped as stale cataloged lines during transactional cutover.
- [ ] Token-aware selection preserves current `select_tasks` safety semantics for cron-scheduler tasks: role matches whose `machines:` exclude the current machine remain unselected unless `roles_authoritative=True`, and conflicts continue to appear in JSON dry-run/apply results. Non-cron scheduler entries are a net-new filter in the Linux cron path and are skipped before selection and conflict reporting.
- [ ] Implementation closeout records current pre/post scheduler-filter conflict ids/counts: non-cron scheduler tasks are removed from conflicts by design, and at least one cron-scheduler role/machine-exclusion fixture proves the conflict branch still works even if the real catalog's conflict count drops to zero.
- [ ] Existing string-argument `select_tasks` call sites remain backward compatible, including `scripts/cron/cron_transaction.py`'s `__main__` self-check and existing `tests/cron/test_cron_transaction.py` fixtures.
- [ ] Existing bare-fingerprint `classify_line` call sites remain backward compatible after metadata-entry support; the deckhand preserved-external fixture still classifies `preserved_external`, while metadata entries retain `catalog_task_id` for selected catalog-owned dedupe.
- [ ] Existing five-argument `plan_cutover` call sites remain backward compatible after adding the optional/defaulted `selected_task_ids` keyword; metadata-aware selected dedupe uses the keyword path only.
- [ ] Negative selection tests prove Windows scheduler tasks (`provider-dream-bridge-win`, `hermes-claude-bridge-win`, `win-repository-sync`, `win-session-state-commit`) are not rendered into the Linux crontab and dev-secondary does not inherit ace-linux-1-only machine-pinned tasks through role matches.
- [ ] `setup-cron.sh` and `cron_apply.py` use one shared renderer module for effective schedule, command text, and full cron-line rendering with exactly one ASCII space between schedule and command; setup-cron selection remains machine-token-only, `cron_apply.py` keeps role/legacy selection with tokenized legacy matching, a static/source test proves the shell script no longer has duplicate placeholder `command.replace(...)` logic, and cross-path parity covers full rendered lines only for tasks selected by both paths.
- [ ] `cron_render.py` remains a leaf module and imports no `cron_transaction.py`; `cron_transaction.py` may depend on render helpers, and `cron-audit.py --json` smoke covers import-cycle regressions.
- [ ] On the implementing host, `repo-ecosystem-hygiene-audit.sh` completes across that host's live governed repo set from `config/workstations/registry.yaml` (required, optional, and `non_tier1_machine_access_current`) with zero `git_probe_timeout` and `incomplete_due_to_deadline=false` under tracked 30/120/480 defaults; `status=OK` or `status=WARN` with rc=0 satisfies completion because ordinary hygiene findings remain audit output, not execution failure. The implementation closeout must include the host-local live audit invocation, parsed `.claude/state/repo-ecosystem-hygiene/latest.json` proof, and one cold-cache or dropped-cache full-set timing; cross-machine coverage is not implied by one host's run.
- [ ] Automated hygiene tests prove repo enumeration includes `required`, `optional`, and `non_tier1_machine_access_current`; the timeout-vs-schedule test computes the hygiene-to-cron-health gap from `schedule-tasks.yaml` instead of hardcoding `600`.
- [ ] `cron-health-check.sh` flags a hygiene log whose latest hygiene-specific marker is `status=ERROR` or `ERROR: repo-ecosystem-hygiene execution_failed`.
- [ ] `cron-health-check.sh` does not flag an older hygiene-specific `status=ERROR` or `execution_failed` if a newer hygiene evidence line has `status=WARN` or `status=OK`.
- [ ] `cron-health-check.sh` filters recognized hygiene marker lines exactly and still flags unrelated generic `ERROR:` / `Traceback` lines in the same task log.
- [ ] `cron-health-check.sh` handles hygiene `status=ERROR` on an already stale/missing task without double-counting or clobbering existing STALE/MISSING precedence.
- [ ] `cron-health-check.sh` uses PATH-based `uv` resolution and contains no hardcoded `/home/vamsee/.local/bin/uv` path.
- [ ] Focused tests pass: `UV_CACHE_DIR=.claude/state/uv-cache uv run --no-project pytest tests/cron/test_cron_render.py tests/cron/test_cron_apply.py tests/cron/test_cron_transaction.py tests/cron/test_a1_preserved.py tests/cron/test_cron_audit.py scripts/cron/tests/test_validate_schedule.py scripts/cron/tests/test_repo_ecosystem_hygiene_audit.py -q`.
- [ ] Selector self-check passes: `UV_CACHE_DIR=.claude/state/uv-cache uv run --no-project python scripts/cron/cron_transaction.py`.
- [ ] Cron-audit CLI smoke passes on the implementing host with readable crontab: `UV_CACHE_DIR=.claude/state/uv-cache uv run --script scripts/cron/cron-audit.py --json`; restricted contexts must run the fixture-backed smoke instead.
- [ ] Cron-audit fails closed on unreadable crontab: permission-denied `crontab -l` fixture returns `ok=false` or nonzero and surfaces the stderr/reason, rather than passing an empty-crontab audit.
- [ ] Focused shell tests pass: `bash scripts/monitoring/tests/test_cron_health_check.sh`.
- [ ] Before legal/absolute-path scans, all new and modified implementation files are staged or at least `git add --intent-to-add` so `git diff --name-only HEAD` and `git ls-files` include newly created files such as `scripts/cron/cron_render.py` and `tests/cron/test_cron_render.py`.
- [ ] Legal/security scan passes after staging/tracking new files: `bash scripts/legal/legal-sanity-scan.sh --diff-only`.
- [ ] Absolute-path enforcement passes in pathspec mode for this issue's changed production shell/Python files, with the existing baseline explicitly enabled to avoid unrelated repo-wide drift: `bash scripts/enforcement/check-no-abs-paths.sh --baseline=config/quality/no-abs-paths-baseline.txt scripts/cron/cron_render.py scripts/cron/cron_apply.py scripts/cron/cron_transaction.py scripts/cron/cron-audit.py scripts/cron/setup-cron.sh scripts/cron/repo-ecosystem-hygiene-audit.sh scripts/monitoring/cron-health-check.sh`. Test files that intentionally use absolute-path fixtures remain covered by focused tests/legal scan; any new non-fixture absolute path in tests must use a line-level `# abs-path-allowed` sentinel or be refactored.
- [ ] Plan-review promotion gate: after final no-MAJOR review and before moving the GitHub issue to `status:plan-review`, update this plan header/status and review summary so they no longer say `FAIL` or "fresh review required"; commit and push this plan, `docs/plans/README.md`, and final no-MAJOR review artifacts; verify `git rev-parse HEAD` equals `git ls-remote origin refs/heads/main`; post a GitHub issue comment citing the commit SHA, plan path, final review artifact paths/verdicts, and the fact that implementation remains blocked pending user approval.
- [ ] Read-only boundary from #3041 is preserved: no repo mutation, branch cleanup, stash mutation, worktree pruning, or remote writes are added to the hygiene audit.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude r1 | MAJOR | Latest evidence-line semantics, OR-shaped executability contract, setup-cron parity source mismatch, unfalsifiable timeout test, missing second-cutover test, and too-narrow live repo acceptance. |
| Codex r1 | MAJOR | Latest evidence-line semantics, OR-shaped executability contract, setup-cron `$WORKSPACE_HUB` test gap, and too-narrow live repo acceptance. |
| Gemini r1 | MAJOR | Mixed false positives from shell heredoc/path reading plus a valid regex portability concern and missing file-existence citation. |
| Claude r2 | MAJOR | Unresolved shared renderer/cross-parity decision remained a blocker; also requested tighter timeout, generic marker precedence, classifier citation, and explicit Bash regex engine. |
| Codex r2 | MAJOR | `new_text`/preview OR remained, older `ERROR:` execution marker semantics were unspecified, timeout total budget conflicted with full governed set, and parity tests missed selection/rendering divergence. |
| Gemini r2 | MAJOR | Stale `/tmp/wf0/repo` file-existence false positives plus a valid greedy-regex concern. |
| Claude r3 | MAJOR | Full governed-set timeout evidence still missing and fallback-key catalog matching could break expanded placeholder tasks. |
| Codex r3 | MINOR | Required explicit live governed-set verification command/output and separation of failed vs fresh no-MAJOR review artifacts. |
| Claude r4 | MAJOR | Rendered-only catalog keys would regress unexpanded `$WORKSPACE_HUB` fallback lines; schedule-field parity was overstated; WARN completion wording needed tightening. |
| Codex r4 | MAJOR | Alias resolution happened after role lookup; shared-renderer usage was not structurally falsifiable; existing `test_a1_preserved.py` regression was omitted from the focused gate. |
| Claude r5 | MINOR | No blockers; requested schedule-by-machine drift guard, canonical backup naming, stronger `notification-purge` retained-output assertion, and line-exact marker-filter coverage. |
| Codex r5 | MINOR | No blockers; requested README row wording cleanup, `uv run` evidence commands, and fresh artifact header state. |
| Claude r6 | MAJOR | Renderer schedule precedence contradicted setup-cron hostname-first behavior; parity test was tautological; cron-health stale/error and schedule-gap tests needed tightening. |
| Codex r6 | MAJOR | `cron_apply.py` selection could drop setup-cron machine-pinned tasks; parity test missed machine-token-only selection; governed repo buckets lacked automated regression coverage. |
| Claude r7 | MAJOR | Selector over-selected Windows/non-cron tasks and dropped conflict reporting; resource-intel root cause was misstated; literal dry-run evidence and live-hostname schedule precedence needed tightening. |
| Codex r7 | MAJOR | Selector failed to preserve current legacy exclusion and `roles_authoritative` semantics; physical-machine parity claim was false without negative role-match/machine-exclusion tests. |
| Claude r8 | MINOR | No blockers; requested call-site/self-check migration clarity, selector strategy consistency, broader fallback-key coverage, host-local live evidence wording, and `main()` alias-resolution locus. |
| Codex r8 | MAJOR | `notification-purge` could be preserved and re-added; `cron-audit.py` would diverge from shared raw/rendered catalog-key behavior. |
| Claude r9 | MAJOR | Notification-purge dedupe needed live-safe proof or catalog-owned loose fingerprint; shared catalog-key builder had no canonical module; cron-audit/apply status quo was misframed. |
| Codex r9 | MAJOR | Setup-cron selection contract remained ambiguous; notification-purge dedupe needed catalog-owned verification; cron-health hardcoded user-local `uv` path remained unaddressed. |
| Claude r10 | MAJOR | Catalog-owned notification-purge dedupe lacked metadata plumbing into cutover and would trip the post-apply preservation guard. |
| Codex r10 | MAJOR | Same metadata/classification blocker plus missing `cron-audit.py --json` smoke for the fail-closed CLI. |
| Claude r11 | MAJOR | Metadata-entry classifier could break existing bare-fingerprint callers; cron-line byte parity needed a separator contract. |
| Codex r11 | MINOR | Header/artifact state needed R11 freshness and the superseded R4 schedule-parity note needed clarification. |
| Claude r12 | MINOR | Requested defaulted `plan_cutover` compatibility, cold/cache timing evidence, and cited fallback-constant verification. |
| Codex r12 | MAJOR | Preserved-local acceptance wording conflicted with selected catalog-owned dedupe; absolute-path enforcement gate was missing. |
| Claude r13 | MINOR | Requested import-direction constraint, cross-machine schedule preview coverage, env-override disclosure, and catalog-command caller inventory. |
| Codex r13 | MAJOR | `cron-audit.py` used all catalog task ids instead of target-machine selected ids; verification gates could miss untracked new files. |
| Claude r14 | MINOR | Recommended T3/split packaging consideration and stronger cold-cache timing proof; no correctness blockers. |
| Codex r14 | MAJOR | Absolute-path check in no-arg mode failed on unrelated tracked files; plan/review artifacts must be tracked before promotion. |
| Claude r15 | MAJOR | Scheduler filtering was net-new but described as existing; non-cron scheduler conflict delta lacked a test; file evidence/shared builder naming needed tightening. |
| Codex r15 | MAJOR | Pathspec absolute-path gate self-blocked on existing test fixture literals without explicit baseline or scoped production-file pathspec. |
| Claude r16 | MINOR | Requested timing-evidence reconciliation, structural cold-cache expectation, real-catalog conflict-count statement, and T3 governance note. |
| Codex r16 | MAJOR | `cron-audit.py` passed on unreadable crontab, plan promotion did not require clearing failed-review header/summary state, and live `cron_apply.py --json` gate needed implementing-host scope. |
| Claude r17 | MINOR | No blockers; requested notification-purge live-risk clarification, stale harness comment cleanup, hygiene cold-cache closeout discipline, and artifact-map labeling cleanup. |
| Codex r17 | MINOR | No blockers; requested duplicate failed-review artifact-map row cleanup and commit/push before label promotion. |

**Overall result:** PASS - r17 returned no MAJOR findings. User approved implementation on 2026-06-14 and the GitHub issue carries `status:plan-approved`.

Revisions made based on review:
- Changed cron-health semantics from "any `status=ERROR` in tail" to "latest matching hygiene evidence line wins".
- Removed OR-shaped crontab executability paths; plan now chooses expanded managed command lines and tests applied/rendered `new_text`.
- Aligned transactional rendering semantics with `setup-cron.sh`: actual checkout path for `WORKSPACE_HUB`, registry `schedule_variant` if present, and `contribute` fallback.
- Pinned timeout mitigation to tracked script defaults of 30s probe and 120s per-repo budget.
- Added second-cutover idempotency coverage.
- Expanded live acceptance from two named repos to the governed registry repo set.
- Added `scripts/cron/tests/test_validate_schedule.py` to file-existence evidence and clarified that `.sh` files contain intentional Python heredocs invoked through `uv`.
- R2: changed the implementation design from per-path renderers to a shared `scripts/cron/cron_render.py` renderer consumed by both setup-cron and cron_apply.
- R2: removed `managed_preview` as an acceptable dry-run substitute; JSON must expose actual rendered `plan["new_text"]`.
- R2: defined hygiene-specific marker precedence across both `task=... status=...` and `ERROR: repo-ecosystem-hygiene execution_failed` markers.
- R2: pinned timeout defaults to 30/120/480 and required total timeout to remain below the 600s hygiene-to-cron-health schedule gap.
- R2: added classifier evidence for `VAR=value` env-line preservation.
- R3: added live 17-repo audit evidence under 30/120/480 defaults: elapsed 16.13s, `repo_count=17`, `incomplete_due_to_deadline=False`, and no `git_probe_timeout`.
- R3: added rendered-catalog classification for fallback-keyed placeholder commands and a test using the live `notification-purge` shape.
- R3: changed machine context resolution to match setup-cron's alias-aware machine lookup before schedule-variant selection.
- R3: clarified that the header's existing artifacts are failed historical review rounds until a fresh no-MAJOR round lands.
- R4: changed fallback-key catalog matching from rendered-only to raw+rendered union and required both expanded and unexpanded `notification-purge` line coverage.
- R4: moved alias resolution before `cron_apply.py` role lookup and added an alias-mode dry-run acceptance check.
- R4: added a structural source test that `setup-cron.sh` delegates placeholder rendering to the shared renderer instead of retaining duplicate shell heredoc replacement logic.
- R4: added `tests/cron/test_a1_preserved.py` to the focused verification gate.
- R4: temporarily scoped schedule-field parity out of that revision because `setup-cron.sh` honored `schedule_by_machine` while `cron_apply.py` still rendered `task["schedule"]`; R5 superseded this by moving effective schedule selection into the shared renderer contract.
- R4: clarified that hygiene `status=WARN rc=0` satisfies completion when deadline/timeout findings are absent.
- R5: moved effective `schedule_by_machine` selection into the shared renderer contract so `cron_apply.py` will not silently retime ace-linux-1 tasks.
- R5: specified single canonical machine resolution for role lookup, result metadata, and backup naming.
- R5: strengthened `notification-purge` fallback tests to assert the selected command appears in `plan["new_text"]`.
- R5: added line-exact marker-filter coverage so stale hygiene markers can be ignored without hiding unrelated `Traceback` or `ERROR:` lines.
- R5: replaced bare `python3` evidence commands with `UV_CACHE_DIR=.claude/state/uv-cache uv run --no-project python`.
- R5: changed the README artifact action from add-only to maintaining the existing row/status.
- R6: changed task selection to include role matches and machine-token matches so transactional cutover does not drop setup-cron-selected machine-pinned tasks.
- R6: changed effective `schedule_by_machine` precedence to match setup-cron: hostname first, then sorted machine-token set.
- R6: added golden schedule tests for the live ace-linux-1 `provider-dream-bridge` and `hermes-claude-bridge` values.
- R6: added regression coverage for `solver-watch-results` and `solver-dashboard` machine-pinned selection.
- R6: changed fallback catalog keys for non-script tasks from truncated 60-character prefixes to full raw/rendered command keys and added distinctness coverage.
- R6: added automated governed-repo bucket coverage for required, optional, and `non_tier1_machine_access_current`.
- R6: added schedule-derived timeout-gap coverage and cron-health combined STALE/MISSING plus hygiene-error precedence coverage.
- R7: changed the selector plan from broad OR matching to extending existing `select_tasks` with scheduler filtering, tokenized legacy matching, `roles_authoritative` conflict semantics, and conflict reporting.
- R7: added negative tests for Windows Task Scheduler entries and dev-secondary role-match/machine-exclusion cases.
- R7: corrected resource intelligence to identify the exact `dev-primary` vs `ace-linux-1` machine-pin mismatch.
- R7: replaced the abridged dry-run JSON illustration with literal summarized command output.
- R7: added live-hostname-first schedule precedence and explicit cron-health STALE/MISSING plus hygiene-error precedence.
- R8: kept `select_tasks` as the single selector, made the machine identity argument backward-compatible, and added self-check/call-site coverage.
- R8: added `cron-audit.py` to the shared raw+rendered catalog-key change so audit/apply classification stays consistent.
- R8: added a plan change to remove or narrow the obsolete `notification-purge` preserved-local exception and test that only one managed notification-purge line remains after cutover.
- R8: added all-fallback-key uniqueness/non-empty/full-command coverage and made live repo-hygiene evidence explicitly host-local.
- R9: changed notification-purge dedupe from fingerprint removal to catalog-owned fingerprint annotation plus explicit dedupe, avoiding byte-exact live-crontab assumptions.
- R9: named `cron_transaction.py` as the canonical shared raw+rendered catalog-key builder module and required both `cron_apply.py` and `cron-audit.py` to import it.
- R9: clarified setup-cron selection stays machine-token-only while cron_apply keeps role/legacy selection with tokenized legacy matching.
- R9: added cron-health hardcoded `/home/vamsee/.local/bin/uv` cleanup and PATH-based `uv` tests.
- R10: made catalog-owned preserved fingerprints metadata-preserving end to end, with a detail classifier that treats selected catalog-owned duplicates as cataloged rather than preserved.
- R10: required the post-apply preservation guard to use the same detail classifier so deliberate selected catalog-owned dedupe does not roll back as a lost preserved line.
- R10: added apply-path notification-purge coverage and a `cron-audit.py --json` smoke gate.
- R11: added bare-fingerprint normalization and backward-compat tests for `classify_line` after the metadata-entry extension.
- R11: pinned cron line rendering to one ASCII space between effective schedule and command so setup-cron and cron_apply byte-parity tests have a concrete separator contract.
- R12: made `plan_cutover`'s selected-task-id argument optional/defaulted and added five-argument caller regression coverage.
- R12: clarified the preserved-local acceptance exception for selected catalog-owned duplicates, added cold/cache timing disclosure to live hygiene evidence, and added the absolute-path enforcement check.
- R13: changed `cron-audit.py` classification to use target-machine selected task ids instead of all catalog task ids and added selected/unselected audit/apply parity coverage.
- R13: required staging/tracking newly created files before diff-only legal and absolute-path scans so `cron_render.py` and `test_cron_render.py` cannot be missed.
- R13: pinned `cron_render.py` as a leaf module, added non-live `--machine` schedule-precedence coverage, inventoried catalog-command callers, and documented preserved env override precedence.
- R14: changed absolute-path verification to pathspec mode scoped to this issue's changed shell/Python files, required cold/dropped-cache full-set timing, and added the commit/push/comment gate before `status:plan-review`.
- R15: corrected scheduler filtering to net-new Linux-cron behavior, pinned non-cron scheduler conflict-delta tests, completed file-existence evidence, named the shared `catalog_command_keys` API, and changed absolute-path enforcement to production-file pathspec with explicit baseline.
- R16: added unreadable-crontab fail-closed audit behavior, scoped live crontab checks to implementing-host closeout with hermetic restricted-runner fixtures, required clearing failed-review header/summary state before promotion, and reconciled warm-cache timing evidence.
- R17: collapsed duplicate failed-review artifact-map rows, recorded final no-MAJOR r17 artifacts, clarified current-host notification-purge evidence versus fixture-covered preserved-local variants, and made stale harness-comment cleanup explicit.

---

## Risks and Open Questions

- **Risk:** Expanding `$WORKSPACE_HUB` and `$LOG` inside transactional cutover could diverge from `setup-cron.sh` if two independent implementations remain. Mitigation: match setup-cron's actual checkout path and `contribute` fallback semantics, and add parity tests for both placeholders.
- **Risk:** A shared renderer can still leave setup-cron and cron_apply task-selection semantics intentionally different. This plan mitigates that by keeping setup-cron's machine-token-only selector explicit, extending cron_apply's role/legacy selector with the same physical-machine token set, and testing both role-selected and machine-pinned task shapes.
- **Risk:** Rendering placeholders before cutover can break catalog matching for fallback-keyed tasks that do not contain a stable script token. Mitigation: compute catalog keys from full raw and rendered commands, then test both expanded and unexpanded `notification-purge` fallback shapes and key distinctness.
- **Risk:** Preserving existing top-level env lines while expanding managed command lines leaves redundant live env state, and existing `REPO_ECOSYSTEM_HYGIENE_*` crontab env lines still override tracked script defaults at runtime. This is acceptable for zero-removal safety because current live values match the planned defaults; if future tracked defaults change, cleanup of those preserved env overrides must be a separate explicit crontab disposition.
- **Risk:** Changing `status-short` to `--untracked-files=no` would hide untracked residue that #3041 currently reports as dirty worktree. This plan chooses tracked 30/120 timeout defaults instead of changing the probe shape.
- **Risk:** `TOTAL_TIMEOUT_SEC=480` is below the 600s hygiene-to-cron-health schedule gap but leaves only a 120s buffer for cron dispatch/log-flush jitter. The observed 16.13s full-set run is warm-cache evidence, not worst-case proof; the sampled standalone probes suggest a rough cold-cache full-set expectation near 170s if all 17 repos behave like the two slowest sampled repos. Implementation closeout must include a cold/dropped-cache full-set timing and fail if it reports `incomplete_due_to_deadline=true`.
- **Risk:** Cron-health must not relitigate all repo hygiene findings or keep stale failures red. It should parse only the latest hygiene-specific marker, filter recognized older hygiene-specific markers before generic scanning, and leave detailed findings in `.claude/state/repo-ecosystem-hygiene/`.
- **Risk:** The live crontab currently contains manual env workarounds. Tests must cover a clean/no-env crontab so the fix is not accidentally dependent on those current live lines.
- **Open:** No user decision is required before review. The plan recommends expanding command placeholders instead of relying on top-level env definitions.

---

## Complexity: T2

**T2** - This touches multiple automation scripts and tests, but the behavioral surface is bounded to scheduled-task rendering, read-only hygiene audit timeout behavior, and cron-health log interpretation. It does not change the mutability boundary of repo hygiene and does not touch engineering/client code.
