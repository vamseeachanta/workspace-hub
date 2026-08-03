# Plan for #3784: tmux persistence is attach-gated and unwired — no reboot survival on any box, no SSH auto-attach

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-08-02
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3784
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-08-02-plan-3784-claude.md | ...-codex.md
> **Provider count:** 2 (T2 scope — agy not dispatched; `...-agy.md` is intentionally absent, not UNAVAILABLE)
> **Canonical artifact:** this file. r2 reviewed an inline copy predating the r1 patch wave and flagged
> the divergence (r2-1) — correct observation; the file is authoritative and the divergence is resolved here.

> **Artifact-format note:** this plan stays Markdown rather than defaulting to HTML per the
> HTML-artifact rule (#2663). It governs harness files, and `docs/plans/` carries enforcement
> tooling (`attest-plan-claims`, plan-index checks) that parses Markdown plans.

---

## Resource Intelligence Summary

Issue class: **Harness/Infrastructure** (`cat:harness`, `domain:workstations`).

### Existing repo code

- Found: `config/tmux/tmux.conf` — **71 lines** at both HEAD and `origin/main`. Carries
  `history-limit 50000` at **line 52** and a resurrect/continuum block guarded by
  `if-shell "[ -r ... ]"`. The guard's own comment reads *"Machines without the plugins skip this block
  silently."*

  > **Corrected after r2b-2.** An earlier revision of this plan asserted "65 lines / line 46" — inferred,
  > never measured. `wc -l` says 71 and `grep -n history-limit` says 52. The 65-line figure was actually
  > measured on **gpu-claw's clone**, which makes it evidence of a *different* defect (below), not of
  > this file's shape.

- **Found (new, promoted from the corrected measurement): gpu-claw's clone is stale.**
  `~/ws/workspace-hub/config/tmux/tmux.conf` is **65 lines** while `origin/main` is **71**. R5 therefore
  cannot simply run the deploy script from that clone — it would symlink `~/.tmux.conf` to a
  six-lines-behind config and report success. **R5 must `git pull` first**, and the acceptance check must
  assert against the origin/main line count, not a hardcoded number.
- Found: `scripts/setup/deploy-tmux.sh` (28 lines) — symlinks `config/tmux/tmux.conf` → `~/.tmux.conf`
  and reloads a running server. **Gap: it never installs the resurrect/continuum plugins**, which is the
  root cause of the per-machine drift.
- Found: `config/tmux/start-session.sh` (50 lines) — 6-window launcher, `SESSION="${1:-work}"`, hostname
  `case` resolving workspace roots. **Gap: no `gpu-claw` case; stale `vamsee-linux1` case; default name
  `work` conflicts with the `main` used by the deployed alias.**
- Found: `scripts/setup/new-machine-setup.sh:234-244` — Step 8b invokes `deploy-tmux.sh`, with a
  `DRY_RUN` branch. Extending `deploy-tmux.sh` therefore reaches onboarding with no new call site.
- Found: `config/fleet-ssh-hosts.yml` — `ssh_hosts: [ace-linux-2, gpu-claw]`, `fallbacks: {gpu-claw: gpu-claw-ts}`.
- Gap: **no test covers any tmux surface.** `find tests -iname '*tmux*'` returns empty.

### Standards

Not applicable — harness/infrastructure issue, no engineering standard involved.

### LLM Wiki pages consulted

No relevant wiki pages — this is harness tooling, not domain knowledge.

### Documents consulted

- Issue #3784 body + the 2026-08-02 correction comment — defect set D1–D5 and the owner-selected
  auto-attach guard contract.
- Issue #1462 — original tmux install issue. Its acceptance criteria date from 2026-03, predate
  gpu-claw's enrolment, and contain no reboot-survival or auto-attach criteria. This plan does not
  re-open its scope; #3784 is the remediation successor.
- Issue #88 — Zellij evaluation, CLOSED 2026-08-02 `NOT_PLANNED` with tmux recorded as settled. The
  dependency #1462 declared (*"gates on #88"*) is therefore discharged.
- Issue #3549 (`status:plan-approved`) — registry-driven Linux connection helpers. **Boundary:** it owns
  `scripts/operations/connection/` (how ace-linux-1 connects *out*). This plan will not modify any file
  under that directory.
- Issue #3696 — stranded secondary working copies on ace-linux-2; explains the dual workspace roots
  observed there.
- Issue #3507 — records gpu-claw's `workspace_root=/home/undi/ws/workspace-hub`, which corrected this
  plan's initial wrong path assumption.
- PR #3597 (merged, squash `aa7fca3`) — added history-limit 50k + the guarded resurrect/continuum block
  this plan extends.
- Prior art `tests/enforcement/test_check_no_conflict_markers.py` — pytest + `subprocess` against
  hermetic `tmp_path` fixtures, tests derived from a plan doc. This plan will follow that shape.
- Drive-file index: no relevant drive files — this is repo-internal harness tooling with no document
  provenance.

### Gaps identified

- No scheduled, attach-independent autosave mechanism exists.
- `deploy-tmux.sh` has no plugin-installation step.
- No visible signal when the plugin block is skipped.
- No test coverage for any tmux surface.
- No auto-attach on SSH login on any machine.
- No canonical session name; three names compete.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-08-03T03:29:04Z via `gh issue view`):

- `#3784` — OPEN — bug(workstations): tmux persistence is attach-gated and unwired
- `#1462` — OPEN — Install and configure tmux (or chosen multiplexer) across all workstation machines
- `#88` — CLOSED (`NOT_PLANNED`) — WRK-1284: Evaluate Zellij terminal multiplexer
- `#3549` — OPEN, `status:plan-approved` — feat(ops): registry-driven Linux connection helpers with TDD

**File existence** (`ls`/`wc -l`, 2026-08-02):

- EXISTS: `config/tmux/tmux.conf` (65 lines)
- EXISTS: `scripts/setup/deploy-tmux.sh` (28 lines)
- EXISTS: `config/tmux/start-session.sh` (50 lines)
- EXISTS: `scripts/setup/new-machine-setup.sh` (325 lines)
- EXISTS: `config/fleet-ssh-hosts.yml`
- MISSING (new — this plan creates): `scripts/tmux/tmux-autosave.sh`
- MISSING (new — this plan creates): `config/tmux/autoattach.sh`
- MISSING (new — this plan creates): `config/tmux/tmux-autosave.service`, `config/tmux/tmux-autosave.timer`
- MISSING (new — this plan creates): `tests/tmux/test_tmux_autoattach.py`, `tests/tmux/test_deploy_tmux.py`, `tests/tmux/test_tmux_autosave.py`

**Line excerpts** (`sed -n` on `config/tmux/tmux.conf`):

```
# Machines without the plugins skip this block silently.
set -g @resurrect-capture-pane-contents 'on'
set -g @continuum-save-interval '15'
set -g @continuum-restore 'on'
if-shell "[ -r ~/.tmux/plugins/tmux-resurrect/resurrect.tmux ]" \
  "run-shell ~/.tmux/plugins/tmux-resurrect/resurrect.tmux"
if-shell "[ -r ~/.tmux/plugins/tmux-continuum/continuum.tmux ]" \
  "run-shell ~/.tmux/plugins/tmux-continuum/continuum.tmux"
```

**Gap proofs**:

- `find tests -maxdepth 2 -iname '*tmux*'` → empty → confirms no tmux test coverage exists.
- `ssh ace-linux-2 'ls -d ~/.tmux/plugins/*'` → `No such file or directory` → confirms plugins absent.
- `ssh gpu-claw-ts 'ls -d ~/.tmux/plugins/*'` → `No such file or directory` → confirms plugins absent.

**Reproduction proofs** (verify-against-repo-state):

D1 — autosave stalled while detached:

```
$ tmux show-options -g | grep continuum-save-last-timestamp
@continuum-save-last-timestamp 1785451976
$ date -d @1785451976
Thu Jul 30 05:52:56 PM CDT 2026
$ date
Sun Aug  2 09:38:25 PM CDT 2026
$ tmux list-clients
(empty)
$ ps -eo pid,etimes,cmd | grep '[t]mux'
2756537  981071 tmux new -s overnight
```

Gap = ~75.8 h against a declared 15-minute interval, with zero attached clients and exactly one
tmux server process (so the multi-server guard is excluded as a cause).

D3 — gpu-claw deployment step never ran:

```
$ ssh gpu-claw-ts 'wc -l ~/ws/workspace-hub/config/tmux/tmux.conf ~/.tmux.conf'
  65 /home/undi/ws/workspace-hub/config/tmux/tmux.conf
  26 /home/undi/.tmux.conf
$ ssh gpu-claw-ts 'grep -c continuum ~/ws/workspace-hub/config/tmux/tmux.conf ~/.tmux.conf'
/home/undi/ws/workspace-hub/config/tmux/tmux.conf:7
/home/undi/.tmux.conf:0
```

D4 — three competing session names:

```
$ tmux ls                                          # ace-linux-1
overnight: 1 windows (created Wed Jul 22 13:04:03 2026)
$ grep -n "alias w=" ~/.bashrc
147:alias w='tmux new -A -s main'
$ grep -n 'SESSION=' config/tmux/start-session.sh
SESSION="${1:-work}"
```

- Reproduced at: 2026-08-02T21:31Z–21:38Z CDT / 2026-08-03T03:29Z UTC
- Failure mode observed matches issue claim: **YES** for D1, D2, D4, D5. **NO for D3 as originally
  filed** — the clone exists at `~/ws/workspace-hub`, not the `~/workspace-hub` first checked; the
  actual failure is an undeployed symlink, not a missing clone. Corrected on the issue before planning,
  and this plan addresses the actual failure mode.

**Design-precedent proofs**:

```
$ grep -n 'quiet\|SCRIPT_OUTPUT' ~/.tmux/plugins/tmux-resurrect/scripts/save.sh | head -3
13:# if "quiet" script produces no output
14:SCRIPT_OUTPUT="$1"
$ ls ~/.config/systemd/user/*.timer | wc -l
10
```

`save.sh quiet` is a supported invocation, and systemd **user** timers are the established
persistence primitive on this box (10 `claude-routine-*.timer` units), so the chosen mechanism
follows existing convention rather than introducing a new one.

**Login-shell chain verification** (added after r1-F3 challenged the `~/.bashrc` placement, 2026-08-02):

```
$ ls ~/.bash_profile ~/.bash_login          # all three boxes
No such file or directory                    # ace-linux-1 (vamsee)
No such file or directory                    # ace-linux-2 (vamsee)
No such file or directory                    # gpu-claw    (undi)
$ grep -n bashrc ~/.profile                  # identical on all three
13:    # include .bashrc if it exists
14:    if [ -f "$HOME/.bashrc" ]; then
15:	. "$HOME/.bashrc"
```

No `~/.bash_profile` or `~/.bash_login` exists on any of the three boxes, so bash falls through to
`~/.profile`, which sources `~/.bashrc` at line 15. The chain is **intact today on all three**. It is
not guaranteed to stay that way — creating a `~/.bash_profile` later would shadow `~/.profile` and
silently kill the auto-attach — so the deploy script will detect and warn rather than assume.

Distinct sources consulted: **11** (issue body + 10 others) — exceeds the 3-source minimum.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-08-02-issue-3784-tmux-persistence-and-ssh-autoattach.md` |
| Auto-attach guard (new) | `config/tmux/autoattach.sh` |
| Autosave wrapper (new) | `scripts/tmux/tmux-autosave.sh` |
| systemd user unit (new) | `config/tmux/tmux-autosave.service` |
| systemd user timer (new) | `config/tmux/tmux-autosave.timer` |
| Deploy script (modify) | `scripts/setup/deploy-tmux.sh` |
| Shared config (modify) | `config/tmux/tmux.conf` |
| Session launcher (modify) | `config/tmux/start-session.sh` |
| Tests (new) | `tests/tmux/test_tmux_autoattach.py`, `tests/tmux/test_deploy_tmux.py`, `tests/tmux/test_tmux_autosave.py` |
| Plan review — Claude | `scripts/review/results/2026-08-02-plan-3784-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-08-02-plan-3784-codex.md` |

---

## Deliverable

A tmux persistence stack in which detached sessions are autosaved on a schedule independent of any
attached client, the resurrect/continuum plugins are installed by the deploy script rather than by
hand, plugin absence is announced rather than silent, all three Linux boxes converge on a single
session name `main`, and an interactive SSH login lands directly in that session without affecting
any non-interactive path — with pytest coverage for every guard condition.

---

## Pseudocode

**`config/tmux/autoattach.sh`** — sourced from `~/.bashrc`; kept as a separate file so tests can
exercise it without mutating a real `~/.bashrc`.

```
# Every condition must hold, else return silently and leave the shell alone.
if shell is not interactive        -> return
if SSH_CONNECTION is unset         -> return   # local console, not an SSH login
if TMUX is set                     -> return   # already inside tmux
if SSH_ORIGINAL_COMMAND is set     -> return   # ssh host '<cmd>', scp, rsync
if NO_TMUX_AUTOATTACH is set       -> return   # operator escape hatch
if tmux binary not on PATH         -> return

session = "${WH_TMUX_SESSION:-main}"    # r2b-6: must carry a literal default.
                                        # An undefined bare "$WH_TMUX_SESSION"
                                        # passes an EMPTY session name and fails
                                        # every interactive login.
if tmux new -A -s "$session" succeeds:
    exit          # detaching from tmux ends the login, matching exec semantics
else:
    warn to stderr and return   # never strand the operator without a shell
```

**`scripts/tmux/tmux-autosave.sh`** — invoked by the systemd user timer.

```
exit 0 quietly if tmux binary absent               # nothing to save, not an error
exit 0 quietly if no tmux server is running        # idle machine, not an error
exit 0 quietly if continuum_save.sh missing        # plugins not installed on this box
exec continuum_save.sh                             # NOT resurrect's save.sh directly
```

**The wrapper calls `continuum_save.sh`, not resurrect's `save.sh`** — this is the whole design, and it
replaces the "restore-in-progress marker" approach that an earlier draft of this plan proposed.

r2 correctly refuted that earlier approach: **there is no durable restore-in-progress marker.**
Verified against the installed plugin code —
`~/.tmux/plugins/tmux-resurrect/scripts/restore.sh:19` is `RESTORING_FROM_SCRATCH="false"`, a
process-local shell variable invisible to any other process, and
`~/.tmux/plugins/tmux-continuum/scripts/continuum_restore.sh:13-19` simply sleeps 1 s and invokes
resurrect's restore script. A wrapper testing for a marker would have been testing for something the
plugins never create, and its test would have passed against a synthetic fixture while protecting
nothing in production.

`continuum_save.sh` already provides what is actually needed (`main()`, lines 55-60):

| Guard | Line | What it gives us |
|---|---|---|
| `supported_tmux_version_ok` | 9-11 | version floor |
| `auto_save_not_disabled` | 17-19 | honours `@continuum-save-interval` being 0 |
| `enough_time_since_last_run_passed` | 21-27 | self-throttles against `@continuum-save-last-timestamp` |
| `acquire_lock` | 37-53 | auto-expiring `mkdir` lock keyed to the tmux server PID, commented *"otherwise we can get corrupted saved state"* |

Calling it from the timer therefore yields behaviour **identical to the attached-mode status-line hook,
minus the attach dependency** — which is precisely the defect. It also keeps
`@continuum-save-last-timestamp` coherent (`set_last_save_timestamp`, line 33), and that option is the
very signal D1's evidence was measured from. The self-throttle means the timer interval need not match
the tmux interval; a shorter timer simply no-ops until the interval elapses.

**The boot race is handled by the timer, not the wrapper.** At a fresh server start
`@continuum-save-last-timestamp` defaults to `0`, so `enough_time_since_last_run_passed` returns true
immediately and a boot-time save *would* fire while continuum is still restoring. The timer therefore
carries `OnBootSec=5min`, which puts the first tick well clear of a restore that begins ~1 s after
server start.

**`scripts/setup/deploy-tmux.sh`** — extended; existing symlink behaviour preserved.

```
if ~/.tmux.conf exists and is NOT already the correct symlink:
    back it up to ~/.tmux.conf.bak-<timestamp>     # r1-F6: never clobber silently
    report the backup path
symlink config/tmux/tmux.conf -> ~/.tmux.conf         (existing behaviour)
verify the login-shell chain reaches ~/.bashrc:        # r1-F3
    if ~/.bash_profile or ~/.bash_login exists and does not source ~/.bashrc:
        WARN loudly — the autoattach block would never execute on this box
for each of tmux-resurrect, tmux-continuum:
    if plugin dir absent:
        git clone --depth 1 into ~/.tmux/plugins/
        on clone failure: WARN loudly, continue, mark degraded
    else:
        report already present            # idempotent, no network needed
install autoattach block into ~/.bashrc between sentinel markers,
    replacing any existing block so re-runs never duplicate it
install + enable the systemd user timer when systemd --user is available,
    else WARN that autosave is unavailable on this machine
reload config in a running tmux server    (existing behaviour)
report a final status line: linked / plugins / autoattach / timer
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `config/tmux/autoattach.sh` | guarded auto-attach logic, sourced from `~/.bashrc`, unit-testable in isolation |
| Create | `scripts/tmux/tmux-autosave.sh` | attach-independent save wrapper that fails soft on every absent precondition |
| Create | `config/tmux/tmux-autosave.service` | systemd user unit invoking the wrapper |
| Create | `config/tmux/tmux-autosave.timer` | `OnBootSec=5min`, `OnUnitActiveSec=15min`, monotonic — matching the `setup-kanban-loader-timer.sh` precedent. **`Persistent=` is not used, and the earlier rationale for excluding it was wrong** (r2b-5): `systemd.timer(5)` defines `Persistent=` as affecting `OnCalendar=` only, so it is *inert* on a monotonic timer — it was never the boot-race trigger. The real mitigation is `OnBootSec=5min`, because `@continuum-save-last-timestamp` defaults to `0` at a fresh server start and an early tick would save over an in-flight restore. The unit must also specify `ExecStart`, `Type=oneshot`, a timeout, and a non-alerting failure policy — all of which an earlier revision left unspecified. |
| Create | `tests/tmux/test_tmux_autoattach.py` | TDD coverage of all seven guard conditions + failure path |
| Create | `tests/tmux/test_deploy_tmux.py` | TDD coverage of plugin install, idempotency, degraded-mode warnings |
| Create | `tests/tmux/test_tmux_autosave.py` | TDD coverage of the fail-soft preconditions |
| Modify | `scripts/setup/deploy-tmux.sh` | install plugins, install autoattach block, install timer, report status |
| Modify | `config/tmux/tmux.conf` | replace the silent `if-shell` skip with a visible warning when plugins are absent |
| Modify | `config/tmux/start-session.sh` | default session `work` → `main`; add `gpu-claw` case; drop stale `vamsee-linux1` case |
| Update | `docs/plans/README.md` | add this plan to the index |

**Explicitly not changed:** anything under `scripts/operations/connection/` (owned by #3549), `sshd`
configuration, and the Windows hosts.

### Scheduler-mutation scope (added after r2b-3 — SCOPE EXPANSION, flagged for the approval decision)

Installing and enabling a systemd **user** timer makes the installer a scheduler mutation surface, which
`.claude/rules/scheduler-mutation-safety.md` governs as a **hard rule**. An earlier revision of this plan
omitted it entirely; implementing the file list as it then stood would have violated repository policy.

Verified precedent — the registry already carries an exactly analogous entry:

```
$ grep -n -A6 'setup-kanban-loader-timer' config/scheduled-tasks/mutation-surfaces.yaml
83:  - path: scripts/install/setup-kanban-loader-timer.sh
87:      - id: install:systemd-unit-write
88:        primitive: systemd-user-unit-write
89:        target_kind: systemd-user
90:        scheduler_identity: local-user-systemd-kanban-loader-sync
```

**Design consequence — the timer install will be split out of `deploy-tmux.sh`.** Folding a governed
mutation surface into the general onboarding script would drag `deploy-tmux.sh` (invoked from
`new-machine-setup.sh` Step 8b) into the scheduler contract wholesale. Instead:

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/install/setup-tmux-autosave-timer.sh` | the **only** scheduler mutation surface; modelled on `setup-kanban-loader-timer.sh` |
| Update | `config/scheduled-tasks/mutation-surfaces.yaml` | register it: `primitive: systemd-user-unit-write`, `target_kind: systemd-user`, `scheduler_identity: local-user-systemd-tmux-autosave`, `execution_host_binding: physical-local` |
| Create | `tests/tmux/test_setup_tmux_autosave_timer.py` | baseline snapshot, durable backup, compare-and-swap, exact post-write verification, CAS rollback |
| Update | `docs/reports/` scheduler audit HTML | required by `--check-html`; note the audit staleness interaction in `feedback_scheduler_audit_digest_covers_ci_workflows` |

`deploy-tmux.sh` will *call* that installer rather than embedding it, and will treat its absence or
failure as a warning, keeping the onboarding path non-governed.

**This is the largest single change from the original scope and is the main thing to weigh at approval.**
The alternative — drop the timer and accept that autosave only runs while attached — leaves D1 unfixed,
which is the defect that motivated the issue.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_autoattach_fires_on_interactive_ssh` | nominal case attaches | interactive, `SSH_CONNECTION` set, no `TMUX` | stub tmux invoked with `new -A -s main` |
| `test_autoattach_skips_non_interactive` | dispatch lane unaffected | non-interactive shell | stub tmux **not** invoked |
| `test_autoattach_skips_local_console` | console login unaffected | `SSH_CONNECTION` unset | stub tmux **not** invoked |
| `test_autoattach_skips_when_already_in_tmux` | no nesting | `TMUX` set | stub tmux **not** invoked |
| `test_autoattach_skips_ssh_remote_command_shape` | **the real** `ssh host '<cmd>'` shape (r1-F4) | non-interactive shell **with** `SSH_CONNECTION` set | stub tmux **not** invoked |
| `test_autoattach_skips_forcecommand_shape` | defence-in-depth only — `SSH_ORIGINAL_COMMAND` is set by sshd *only* under `ForceCommand`/`authorized_keys command=`, neither of which this plan uses | `SSH_ORIGINAL_COMMAND` set | stub tmux **not** invoked |
| `test_autoattach_emits_nothing_when_non_interactive` | **scp/sftp safety** (r1-F5) — any byte on stdout corrupts file transfer | non-interactive shell | stdout **and** stderr both empty |
| `test_autoattach_skips_with_escape_hatch` | operator override works | `NO_TMUX_AUTOATTACH=1` | stub tmux **not** invoked |
| `test_autoattach_skips_when_tmux_absent` | no error on a tmux-less box | empty `PATH` | returns 0, no output |
| `test_autoattach_survives_tmux_failure` | **no lockout** | stub tmux exits 1 | returns non-fatally, warning on stderr, shell continues |
| `test_autoattach_session_name_is_main` | name convergence | default env | session name `main` |
| `test_deploy_installs_missing_plugins` | plugin gap closed | fake `HOME` without plugins | both plugin dirs created |
| `test_deploy_is_idempotent` | re-run safe | run twice | exactly one autoattach block in `~/.bashrc` |
| `test_deploy_warns_when_clone_fails` | degraded mode visible | git clone forced to fail | non-empty warning, exit 0 |
| `test_deploy_preserves_existing_bashrc` | no data loss | `~/.bashrc` with prior content | prior content intact, block appended |
| `test_deploy_replaces_stale_block` | drift repaired | `~/.bashrc` with an old block | old block replaced, not duplicated |
| `test_autosave_noop_without_server` | idle box quiet | no tmux server | exit 0, no output |
| `test_autosave_noop_without_plugin` | unplugged box quiet | no `continuum_save.sh` | exit 0, no output |
| `test_autosave_delegates_to_continuum_save` | **the core design** (r2-2) — the wrapper must call `continuum_save.sh`, never resurrect's `save.sh` directly, so it inherits the lock and interval throttle | stub `continuum_save.sh` | stub invoked; resurrect `save.sh` **not** invoked directly |
| `test_autosave_respects_continuum_lock` | concurrent-save corruption prevented | lock dir already held | second invocation performs no save |
| `test_timer_unit_has_no_persistent_and_delays_boot` | **boot race closed** (r1-F2 + r2-2) | the shipped `.timer` file | no `Persistent=true`; `OnBootSec` ≥ 5 min |
| `test_deploy_backs_up_regular_tmux_conf` | **no silent clobber** (r1-F6) | `~/.tmux.conf` is a regular file | backup file exists with original content |
| `test_deploy_warns_on_broken_login_chain` | dead-block detection (r1-F3) | `~/.bash_profile` present, no bashrc source | non-empty warning |
| `test_start_session_default_is_main` | launcher converges | no argument | session name `main` |
| `test_start_session_has_gpu_claw_case` | gpu-claw resolved (r2b-11: `start-session.sh:11` does `HOST="$(hostname)"`, so an injected `HOST` env var is **overwritten** — the script must take an injectable hostname, or the test must stub `hostname` on `PATH`) | stubbed `hostname` returning `gpu-claw` | workspace root `~/ws/workspace-hub` |
| `test_autoattach_defaults_session_when_var_unset` | **empty-name login failure** (r2b-6) | `WH_TMUX_SESSION` unset | tmux invoked with `main`, never an empty string |
| `test_plugin_clone_is_pinned` | **cross-machine convergence** (r2b-13) | clone step | a pinned ref/commit is requested, not bare remote HEAD |
| `test_plugin_dir_validated_not_just_present` | partial-clone recovery (r2b-13) | plugin dir exists but `resurrect.tmux` missing | treated as invalid, repaired or warned — not accepted |
| `test_tmux_conf_warns_visibly_at_attach` | the acceptance criterion is real (r2b-10) | plugins absent | warning reaches an attaching client — verified as an **attach-time** hook, since config-load `display-message` fires before any client exists |
| `test_timer_unit_fields_complete` | unit is fully specified (r2b-5) | shipped `.service`/`.timer` | `ExecStart`, `Type=oneshot`, timeout and failure policy all present |

---

## Rollout (per-machine, after tests pass)

**Order corrected after r2b-12.** An earlier revision stated in Risks that ace-linux-2 would be validated
before ace-linux-1 "so the dispatch surface is never the first test subject", then sequenced ace-linux-1
first anyway — the mitigation and the sequence contradicted each other. ace-linux-2 now genuinely goes first.

| Step | Machine | Action | Verification |
|---|---|---|---|
| R1 | ace-linux-2 | pull + run `deploy-tmux.sh` | plugins created for the first time; block in `~/.bashrc` |
| R2 | ace-linux-2 | `tmux rename-session -t overnight main`, **then force an immediate save** (r1-F7) | `tmux ls` shows `main`; window contents intact; the saved state file names `main`, not `overnight` |
| R2b | ace-linux-2 | **interactive SSH + BatchMode + scp smoke** | auto-attach works AND non-interactive paths are clean — **gate: do not proceed to ace-linux-1 until green** |
| R3 | ace-linux-1 | run `deploy-tmux.sh` | plugins present, timer active, block in `~/.bashrc` |
| R4 | ace-linux-1 | rename `overnight` → `main` + force save | as R2 |
| R5 | gpu-claw | **`git pull` first** (clone is 6 lines behind), then run `deploy-tmux.sh` from `~/ws/workspace-hub` | clone matches `origin/main`; `~/.tmux.conf` becomes a symlink; line count equals `git show origin/main:config/tmux/tmux.conf \| wc -l`, not a hardcoded number |
| R6 | all three | wait one timer interval with **zero** clients attached | `@continuum-save-last-timestamp` advances |
| R7 | all three | interactive SSH login | lands in `main` |
| R8 | ace-linux-1 | `ssh -o BatchMode=yes ace-linux-1 'echo ok'` and an `scp` | both succeed, no tmux involvement |

R2/R4 are non-destructive renames; they will be guarded to abort if a session named `main` already
exists, so no session is ever clobbered.

---

## Acceptance Criteria

- [ ] All new tests pass: `uv run pytest tests/tmux/ -v`
- [ ] Tests were committed failing first, then made to pass (red → green evidenced in commit order)
- [ ] No regression: repository test suite applicable to changed files passes
- [ ] Autosave timestamp advances across one interval with **zero** attached clients on all three boxes
- [ ] `deploy-tmux.sh` run twice produces exactly one autoattach block
- [ ] Plugin absence produces a visible warning at tmux attach time
- [ ] gpu-claw's clone is pulled current, and `~/.tmux.conf` there is a symlink whose line count equals `git show origin/main:config/tmux/tmux.conf | wc -l` (**not** a hardcoded number — r2b-2)
- [ ] `scripts/install/setup-tmux-autosave-timer.sh` is registered in `config/scheduled-tasks/mutation-surfaces.yaml` and `uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py` passes (r2b-3)
- [ ] Interactive SSH login lands in `main` on all three Linux boxes
- [ ] BatchMode SSH, `ssh host '<cmd>'`, `scp`, `rsync`, and `NO_TMUX_AUTOATTACH=1` each provably do **not** auto-attach
- [ ] Exactly one session name (`main`) across launcher, alias, and live sessions on all three boxes
- [ ] No file under `scripts/operations/connection/` is modified (boundary with #3549 held)
- [ ] `scripts/legal/legal-sanity-scan.sh` passes; no client identifiers, no hardcoded secrets, no tailnet addresses added to tracked files
- [ ] Review artifacts posted to `scripts/review/results/`
- [ ] Summary comment posted to #3784 before closeout

---

## Adversarial Review Summary

<!-- Filled in after adversarial review completes. Not posted to GitHub until populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (r1, inline) | **MAJOR** | F1 autosave races continuum's restore; F2 `Persistent=true` fires that race at every boot; F3 `~/.bashrc` may not be read by a login shell; F4 `SSH_ORIGINAL_COMMAND` is the wrong guard for `ssh host '<cmd>'`; F5 no test pins non-interactive silence (scp safety); F6 deploy clobbers gpu-claw's config with no backup; F7 rename not durable until next save; F8 `return`/`exit` test-harness constraint |
| Codex (r2a, fanout) | **MAJOR** | 1 inline-vs-file plan drift; **2 the restore-in-progress marker does not exist** (verified against plugin source); 3 review-artifact set incomplete; 4 plan not yet at the `status:plan-review` gate; 5 plan-index row absent |
| Codex (r2b, direct invocation) | **MAJOR** | 13 findings, 7 of them new. Blocking: **2 stale evidence** (tmux.conf is 71 lines / line 52, not 65 / line 46 — and the 65 was really gpu-claw's *stale clone*); **3 the systemd-timer installer is an unregistered scheduler mutation surface**, violating `.claude/rules/scheduler-mutation-safety.md`; **12 rollout order contradicts its own stated lockout mitigation**. Also: 5 `Persistent=` is inert on monotonic timers (my r1-F2 rationale was wrong); 6 `WH_TMUX_SESSION` undefined → empty session name; 11 `start-session.sh:11` overwrites injected `HOST`; 13 plugin clones unpinned, defeating the convergence claim; 10 attach-time warning is untested and may fire before any client exists |

**Overall result:** both providers returned MAJOR. All findings are resolved in this revision; the plan
is now presented for user approval. Per the cross-review routing contract, r3 was applied as
main-session inline patches rather than dispatched.

Revisions made based on review:

- **r2-2 (the most consequential).** The r1-F1 mitigation depended on a restore-in-progress marker that
  **does not exist**. Verified independently: `restore.sh:19` `RESTORING_FROM_SCRATCH="false"` is a
  process-local variable, and `continuum_restore.sh:13-19` invokes restore directly. The design changed
  from "guard on a marker" to "**delegate to `continuum_save.sh`**", which already carries an
  auto-expiring PID-keyed lock (lines 37-53), an interval self-throttle (21-27), and timestamp
  bookkeeping (33). Simpler and strictly more correct than the r1 design. The boot race moved to the
  timer (`OnBootSec=5min`) since `@continuum-save-last-timestamp` defaults to `0` on a fresh server.
- **r1-F2 / r2-2.** `Persistent=true` dropped; `OnBootSec=5min` added; both pinned by a test.
- **r1-F3.** Login-shell chain verified empirically on all three boxes (no `~/.bash_profile` shadowing;
  `~/.profile:15` sources `~/.bashrc`). Downgraded from blocking to a deploy-time warn-if-broken check.
- **r1-F4.** Test re-specified: `ssh host '<cmd>'` is protected by the **interactivity** check, not by
  `SSH_ORIGINAL_COMMAND` (which sshd sets only under `ForceCommand`/`command=`). Both cases now tested,
  correctly labelled.
- **r1-F5.** Added `test_autoattach_emits_nothing_when_non_interactive` — scp/sftp corruption guard.
- **r1-F6.** Deploy script now backs up a non-symlink `~/.tmux.conf` before linking.
- **r1-F7.** R2/R4 now force an immediate save after the rename.
- **r1-F8 / r2-1 / r2-3 / r2-5.** Test-harness constraint stated; this file declared canonical; header
  no longer promises an agy artifact at T2 scope; plan-index row added to `docs/plans/README.md`.
- **r2-4** is not a defect — it describes the gate this revision is now entering.
- **r2b-2.** Line-count evidence corrected (71 / line 52) and the 65-line figure re-attributed to gpu-claw's
  **stale clone** — a new defect the wrong number was masking. R5 gains a `git pull`; the acceptance check
  now compares against `origin/main` rather than a literal.
- **r2b-3 (scope expansion).** The timer installer is split into
  `scripts/install/setup-tmux-autosave-timer.sh`, registered in `config/scheduled-tasks/mutation-surfaces.yaml`
  per the `setup-kanban-loader-timer.sh` precedent, with CAS/rollback tests and the scheduler enforcement
  check added to acceptance. **This is the item most worth the owner's attention at approval.**
- **r2b-5.** `Persistent=` corrected as inert for monotonic timers; the real guard is `OnBootSec=5min`.
  Unit field completeness (`ExecStart`, `Type`, timeout, failure policy) now specified and tested.
- **r2b-6 / 11 / 13 / 10.** Session-name literal default; `hostname` made stubbable; plugin clones pinned
  and validated beyond directory existence; attach-time warning given a real test.
- **r2b-12.** Rollout reordered — ace-linux-2 is now genuinely first, with an explicit R2b gate before the
  dispatch surface is touched.

**Not carried:** r2b-1 (canonical-artifact drift) is the same process artifact as r2-1 — both Codex passes
reviewed inline copies predating the patch waves. Resolved by declaring this file canonical in the header.
r2b-4/7/8/9 duplicate r1-F1/F3/F4/F6, already fixed.

---

## Risks and Open Questions

- **Risk — lockout (highest).** A defective auto-attach block can make interactive SSH unusable. Mitigated
  four ways: the block never uses `exec`, so a tmux failure returns to a normal shell; `NO_TMUX_AUTOATTACH=1`
  is an inline escape hatch; the block lives in `~/.bashrc` (user-owned, no root needed to revert); and
  `sshd` is untouched, so a `ForceCommand`-class lockout is structurally impossible. Rollout will validate
  on ace-linux-2 before ace-linux-1 so the dispatch surface is never the first test subject.
- **Deliberate divergence from the approved snippet — needs owner acknowledgement.** The option preview
  approved on 2026-08-02 used `exec tmux new -A -s main`. This plan proposes `if tmux new -A -s main; then
  exit; fi` plus a warning instead. User-visible behaviour is identical (detach ends the login), but a tmux
  failure yields a working shell rather than an immediately-closed connection. Flagging rather than silently
  substituting.
- **Risk — dispatch breakage.** ace-linux-1 is the dispatch surface. Test cases for BatchMode, remote-command,
  `scp` and `rsync` are acceptance-blocking, not optional, and R8 re-verifies on the live box.
- **Risk — gpu-claw availability.** The box flaps on the tailnet and its LAN route is dead. If it is
  unreachable during rollout, R5 will be recorded as deferred with evidence rather than silently skipped,
  and the issue will stay open for that step.
- **Risk — ace-linux-2 dual workspace roots.** Both `/mnt/workspace-hub` and `/mnt/local-analysis/workspace-hub`
  exist there while `start-session.sh` hardcodes the former and the live symlink uses the latter. This plan
  will make the launcher consistent with the deployed symlink; the deeper stranded-copy problem stays with #3696.
- **Risk — systemd user timer requires linger.** `Linger=yes` is confirmed on all three boxes today. The
  deploy script will verify rather than assume, and warn if absent.
- **Open — timer interval.** The plan uses 15 minutes to match the existing `@continuum-save-interval`.
  A shorter interval bounds worst-case loss more tightly at a small I/O cost. Flagged for the approval decision.
- **Open — `overnight` session contents.** Both live sessions have run 11.3 days. The rename is
  non-destructive, but if either holds an active long-running process the owner may prefer to schedule
  R2/R4 rather than run them inline.
- **Implementation constraint (r1-F8).** The guard uses `return` (valid only when sourced) and `exit`
  (terminates the sourcing shell — the intended login behaviour). Tests must therefore invoke it via
  `subprocess` against hermetic fixtures, as the cited prior art does. An in-process `source` from
  pytest would terminate the test runner. Stated explicitly so no implementer reaches for the simpler
  in-process form.
- **Checked, not a risk — pytest collection viability.** A concurrent session is investigating pytest
  *collection* hangs in sibling repos (assetutilities, worldenergydata, digitalmodel) on this NTFS-FUSE
  filesystem. Since this plan's acceptance gate is `uv run pytest tests/tmux/`, that was verified against
  workspace-hub directly rather than assumed: `uv run pytest tests/enforcement/test_check_gh_auth.py
  --collect-only -q` → **6 tests collected in 2.77 s** (14.9 s wall incl. uv resolution). Targeted
  collection in this repo is unaffected. The plan will keep test invocations path-scoped rather than
  whole-suite so it stays clear of whatever that investigation finds.
- **Risk — new failure introduced by the fix (r1-F1).** The autosave timer, done naively, is capable of
  destroying restore points that the current broken-but-idle system never touches. The restore-in-progress
  guard and the omission of `Persistent=true` are the two mitigations; both carry blocking tests. This is
  the single most important thing for a reviewer to check, because the failure is silent and only
  observable after a reboot.

---

## Complexity: T2
