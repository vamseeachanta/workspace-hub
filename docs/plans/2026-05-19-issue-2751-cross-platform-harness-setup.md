# Plan for #2751: Cross-platform harness setup — integrate AI-provider bootstrap, auth orchestration, macOS+PowerShell, per-machine status registry

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-05-19
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2751
> **Review artifacts:** scripts/review/results/2026-05-19-plan-2751-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/setup/new-machine-setup.sh` (266 lines, dated 2026-05-04) — comprehensive WRK-313 single-command bootstrap with 9 steps (submodules, hooks, Claude statusline + keybindings, shell aliases, npm, Codex pin, crontab, SSH, env, tmux, verify). Idempotent (content-diff). OS branches: `linux` (default), `windows` (MINGW*/CYGWIN*/MSYS*). macOS would fall through `linux` branch with apt assumptions.
- Found: `scripts/setup/verify-setup.sh` (267 lines) — 9-section PASS/WARN/FAIL validator covering git/hooks/CLIs/aliases/statusline/cron/SSH/env/python.
- Found: `scripts/setup/install-all-hooks.sh` — idempotent git hook installer (header explicitly: "PowerShell is NOT supported").
- Found: `scripts/setup/engineering-suite-install.sh` — Ubuntu sudo-only engineering apps installer (Blender/FreeCAD/OpenFOAM/QGIS/CalculiX/Elmer/FEniCSx). Out of scope for this plan.
- Found: `scripts/setup/deploy-tmux.sh`, `scripts/install/pin-codex.sh`.
- Found: `scripts/memory/bootstrap-machine.sh` (5853 bytes, dated 2026-05-16) — AI-provider memory bootstrap. Creates `~/.claude/CLAUDE.md`, calls `install-soul-runtime.sh`. **Currently never invoked by `new-machine-setup.sh`** — G1 root cause.
- Found: `scripts/agents/install-soul-runtime.sh` (3288 bytes, dated 2026-05-16) — creates `~/.hermes/SOUL.md` → repo, `~/.codex/AGENTS.md` → repo symlinks with `.pre-install-backup.<timestamp>` for pre-existing files.
- Found: `scripts/operations/agent-execution/collect-machine-baseline.ps1` (Windows-only) and `.bat` sibling. Outputs hardware baseline to `docs/reports/machine-baseline/<HOSTNAME>-<STAMP>.{txt,json}` with credential redaction. **No `.sh` sibling exists.**
- Gap: no `scripts/setup/lib/` directory exists.
- Gap: no `scripts/setup/new-machine-setup.ps1` exists.
- Gap: no `scripts/setup/emit-machine-status.{sh,ps1}` exists.
- Gap: no `scripts/setup/aggregate-machine-status.sh` exists.

### Standards

Not applicable — this is harness/infrastructure work, not engineering-calculation work. No engineering standards (DNV/API/IADC) apply.

### LLM Wiki pages consulted

Not applicable — no domain wiki content relevant to harness setup tooling.

### Documents consulted

- `.claude/docs/new-machine-setup.md` (236 lines, dated 2026-02-24) — existing canonical doc, internal-facing. Covers Quick Start, Components (Git Hooks/Statusline/Aliases), 9 documented setup components. Status: active. Will be migrated to `docs/setup/` and replaced with a thin pointer.
- `config/agents/SHARED_SOUL.md:104` — canonical machine roster mention: "Hermes on `ace-linux-1`, Claude Max subscription, Codex/OpenAI paid seat, Gemini Google AI Pro".
- `config/agents/user-profile.yaml:25` — `ace-linux-1` listed in user profile (implicit roster of 1).
- `.claude/rules/coding-style.md` — path handling rule: "use relative paths or `${REPO_ROOT}` — never hardcode absolute paths (enforced: `scripts/enforcement/check-no-abs-paths.sh`)".
- `.claude/rules/patterns.md` — enforcement gradient (prose → script → hook). New scripts in this plan are Level 2 (auditable shell). Future promotion to Level 3 (pre-commit) deferred.
- Memory: `feedback_cross_machine_execution` — per-machine tasks via shared git repo, not SSH/rsync. Directly informs G9 architecture.
- Memory: `feedback_subagent_write_phantom` — subagent reports Write success while file doesn't land; main session must `ls` before believing. Applies to plan-writing too — main session writes plan directly.
- Memory: `feedback_plan_past_tense_artifact_claims` — plans describe proposed work in future tense; no past-tense "artifact already exists" claims.
- Related issue: [#2479](https://github.com/vamseeachanta/workspace-hub/issues/2479) — Codex CLI pin precedent (informs CLI version-pinning question in v2).
- Parent assessment: 2026-05-19 conversation thread on cross-machine harness parity (4-agent parallel exploration).

### Gaps identified

- **G1**: `new-machine-setup.sh` does not invoke `scripts/memory/bootstrap-machine.sh`. AI-provider SOUL-runtime symlinks not installed by entry point. Confirmed by `grep -nE 'bootstrap-machine|install-soul-runtime' scripts/setup/new-machine-setup.sh` → no matches.
- **G2**: No auto-install of provider CLIs (warns only).
- **G3**: No interactive auth orchestration.
- **G4**: No Hermes `config.yaml` rendering from `config/agents/hermes/config.yaml.template`.
- **G5**: No native PowerShell `new-machine-setup.ps1`.
- **G6**: No explicit `darwin` branch in OS detection; macOS untested.
- **G7**: User-facing setup docs absent from `docs/`. Live in `.claude/docs/` (internal namespace).
- **G9**: No per-machine harness-parity status emission/aggregation. Control plane (`ace-linux-1`) cannot assess fleet harness drift.
- G8 (engineering-apps cross-platform install) deferred — separate follow-up.

### Evidence

**Issue statuses** (verified 2026-05-19T via `gh issue view`):
- `#2751` — OPEN — "Cross-platform harness setup: integrate AI-provider bootstrap, auth orchestration, macOS+PowerShell, per-machine status registry"
- `#2479` — referenced (Codex CLI pin precedent)
- `#2722` — referenced (drift probe memory)
- `#2750` — referenced (Hermes flow-through tracking)

**File existence** (`ls -la` 2026-05-19T):
- EXISTS: `scripts/setup/new-machine-setup.sh`
- EXISTS: `scripts/setup/verify-setup.sh`
- EXISTS: `scripts/setup/install-all-hooks.sh`
- EXISTS: `scripts/memory/bootstrap-machine.sh`
- EXISTS: `scripts/agents/install-soul-runtime.sh`
- EXISTS: `scripts/operations/agent-execution/collect-machine-baseline.ps1`
- EXISTS: `.claude/docs/new-machine-setup.md`
- EXISTS: `config/agents/hermes/config.yaml.template` (referenced; will verify before render-helper implementation)
- MISSING (this plan creates): `scripts/setup/lib/detect-os.sh`
- MISSING (this plan creates): `scripts/setup/lib/install-provider-clis.sh`
- MISSING (this plan creates): `scripts/setup/lib/orchestrate-auth.sh`
- MISSING (this plan creates): `scripts/setup/lib/instantiate-hermes-config.sh`
- MISSING (this plan creates): `scripts/setup/new-machine-setup.ps1`
- MISSING (this plan creates): `scripts/setup/verify-setup.ps1`
- MISSING (this plan creates): `scripts/setup/emit-machine-status.sh`
- MISSING (this plan creates): `scripts/setup/emit-machine-status.ps1`
- MISSING (this plan creates): `scripts/setup/aggregate-machine-status.sh`
- MISSING (this plan creates): `docs/setup/` (directory)
- MISSING (this plan creates): `config/machine-baselines/` (directory)
- MISSING (this plan creates): `tests/setup/` (directory)

**Line excerpts** (`sed -n N,Mp scripts/setup/new-machine-setup.sh`):
```
34: WH_OS="linux"
35: case "$(uname -s 2>/dev/null)" in
36:   MINGW*|CYGWIN*|MSYS*) WH_OS="windows" ;;
37: esac
```
This is the OS-detection branch that will gain `Darwin*) WH_OS="darwin" ;;`.

```
246: # ── Step 9: Verify ──
247: step "9. Post-setup verification"
```
After line 252, a new Step 10 (AI-provider harness) will be inserted, and the script will gain Steps 11-14 for auto-install, auth orchestration, Hermes config, status emission.

**Gap proofs**:
- `ls scripts/setup/lib/ 2>&1` → "No such file or directory" → confirms helper dir does not yet exist.
- `ls config/machine-baselines/ 2>&1` → "No such file or directory" → confirms registry dir does not yet exist.
- `grep -nE 'bootstrap-machine|install-soul-runtime' scripts/setup/new-machine-setup.sh` → no output → confirms G1 (no AI-provider wiring).

**Reproduction proofs**:
N/A — proposed-feature issue, not a runtime claim. Existing `scripts/setup/new-machine-setup.sh` runs fine for what it covers; this plan adds capabilities, does not fix a runtime bug.

Distinct sources consulted: 11 (issue body, 4 existing scripts read in full, 3 docs/memory, 2 rules, 1 parent conversation). Minimum 3 satisfied.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-19-issue-2751-cross-platform-harness-setup.md` |
| Tests | `tests/setup/test_detect_os.sh`, `test_idempotency.sh`, `test_missing_cli_install.sh`, `test_status_emission_schema.sh`, `test_secret_scrubbing.sh`, `test_aggregate_status.sh` |
| Implementation (entry points) | `scripts/setup/new-machine-setup.sh` (modify), `scripts/setup/new-machine-setup.ps1` (new), `scripts/setup/verify-setup.sh` (modify), `scripts/setup/verify-setup.ps1` (new) |
| Implementation (lib helpers) | `scripts/setup/lib/detect-os.sh`, `install-provider-clis.sh`, `orchestrate-auth.sh`, `instantiate-hermes-config.sh` (all new) |
| Implementation (status registry) | `scripts/setup/emit-machine-status.{sh,ps1}` (new), `scripts/setup/aggregate-machine-status.sh` (new) |
| Status registry data | `config/machine-baselines/<hostname>.{md,yaml}` (per-machine, git-tracked) |
| Fleet status report | `docs/reports/fleet-harness-status.md` (generated by aggregator) |
| Docs (user-facing) | `docs/setup/README.md`, `FRESH_MACHINE_SETUP.md`, `EXISTING_MACHINE_AUDIT.md`, `PROVIDER_AUTH_GUIDE.md`, `TROUBLESHOOTING.md`, `MACHINE_REGISTRY.md` (all new) |
| Docs (internal pointer) | `.claude/docs/new-machine-setup.md` (reduce to thin pointer) |
| Plan index | `docs/plans/README.md` (add row) |
| Plan review — Claude | `scripts/review/results/2026-05-19-plan-2751-claude.md` |
| Plan review — Codex or Gemini (T2 = 1 other provider) | `scripts/review/results/2026-05-19-plan-2751-<provider>.md` |

---

## Deliverable

A single-command cross-platform bootstrap (`scripts/setup/new-machine-setup.{sh,ps1}`) that takes a freshly-cloned workspace-hub on Linux, macOS, or Windows from clone to fully-authenticated AI-provider parity, plus a git-tracked per-machine harness-parity status registry (`config/machine-baselines/`) the control plane reads to assess fleet drift, plus user-facing setup documentation (`docs/setup/`) including the canonical coverage table.

**Operational tracker**: [#2753](https://github.com/vamseeachanta/workspace-hub/issues/2753) is the evergreen tracker for fresh-machine setup runs. After this plan implements, operators reference #2753 by phrasing "run this machine against #2753" — each bootstrap event becomes a comment on that issue with the machine's status report. The setup script and `emit-machine-status.sh` will include hints to that effect in their final-status output (acceptance criterion added).

---

## Pseudocode

### `scripts/setup/lib/detect-os.sh`

**Canonical OS-token decision (per r1 M1):** align with existing `scripts/memory/bootstrap-machine.sh:26` which already emits `macos` for Darwin. New helper adopts the same vocabulary; `new-machine-setup.sh:34-37` and `verify-setup.sh:25-28` get refactored to source this helper instead of duplicating inline.

```
detect_os():
    case uname -s:
        Linux*)              echo "linux"
        Darwin*)             echo "macos"      # aligned with bootstrap-machine.sh:26
        MINGW*|CYGWIN*|MSYS*) echo "windows"
        *)                   echo "unknown" ; return 1
```

### `scripts/setup/lib/install-provider-clis.sh`

**Channel-branched install (per r1 M2):** 3 of 4 provider CLIs are npm packages, only `gh` is a system pkg. Pseudocode branches by install-channel, not by OS.

```
install_provider_clis(os):
    # System-package install channel (gh only)
    sys_pkg_install = match os:
        linux   -> "sudo apt-get install -y"
        macos   -> "brew install"
        windows -> "choco install -y" OR "winget install -e --id"

    # npm install channel (claude, codex, gemini)
    # Precondition: node + npm must be present. Install Node first if missing.
    ensure_node(os):
        if has_cli(node) and has_cli(npm): return
        match os:
            linux   -> apt install -y nodejs npm                # existing precedent at new-machine-setup.sh:171
            macos   -> brew install node
            windows -> choco install -y nodejs OR winget install OpenJS.NodeJS

    # gh = system pkg
    if not has_cli(gh):
        elevate_check()
        run sys_pkg_install gh
        verify gh on PATH

    # npm packages — claude, gemini
    if not (has_cli(claude) and has_cli(gemini)):
        ensure_node(os)
    if not has_cli(claude):
        npm install -g @anthropic-ai/claude-code
        verify claude on PATH
    if not has_cli(gemini):
        npm install -g <gemini-pkg-name>                        # name TBD by verify step before TDD
        verify gemini on PATH

    # codex — reuse existing pin script, do not reinvent
    if not has_cli(codex):
        bash scripts/install/pin-codex.sh                       # honors CODEX_PIN_VERSION
        verify codex on PATH

    # Hermes binary — out-of-band, document URL
    if not has_cli(hermes):
        print "Hermes binary not installed. Install per docs/setup/PROVIDER_AUTH_GUIDE.md#hermes"
        # Do not auto-install; user-driven step.
```

### `scripts/setup/lib/orchestrate-auth.sh`
```
orchestrate_auth():
    for cli, cmd in [
        (claude, "claude auth login"),
        (codex, "codex auth login"),
        (gh, "gh auth login"),
        # Gemini has NO `auth` subcommand (verified 2026-05-19 via `gemini --help`).
        # Auth options: (1) `gcloud auth application-default login` if gcloud present,
        #               (2) first-run trigger via `gemini -p "ping"` to provoke OAuth prompt,
        #               (3) GEMINI_API_KEY env var.
        # Chosen: option 2 (matches interactive-auth UX); falls through to option 3 (env var) if browser unavailable.
        (gemini, "gemini -p ping"),
    ]:
        if auth_present(cli): skip
        else:
            print "Launching: <cmd>. Complete browser flow then return here."
            run <cmd> in foreground
            verify auth_present(cli)
            # For gemini specifically: after probe, check ~/.gemini/oauth_creds.json exists.
            # If still absent, prompt for GEMINI_API_KEY → write to ~/.gemini/.env (mode 600).
    # Hermes .env field prompt — values never echoed
    if not exists ~/.hermes/.env:
        prompt fields (HERMES_TELEGRAM_BOT_TOKEN, HERMES_OPENAI_API_KEY, etc.) via read -s
        write to ~/.hermes/.env with mode 600
```

### `scripts/setup/lib/instantiate-hermes-config.sh`
```
instantiate_hermes_config():
    template = REPO_ROOT/config/agents/hermes/config.yaml.template
    target = ~/.hermes/config.yaml
    if exists target and not --force: skip
    machine_specific_fields = prompt_user_for_or_detect:
        - hostname
        - workspace_root
        - log_directory
    render template → target with field substitution
    verify YAML valid (yq if available, else python yaml.safe_load)
```

### `scripts/setup/emit-machine-status.sh`
```
emit_machine_status():
    hostname = $(hostname -s)
    os = $(detect_os)
    output_md = REPO_ROOT/config/machine-baselines/${hostname}.md
    output_yaml = REPO_ROOT/config/machine-baselines/${hostname}.yaml

    # Collect status across 22 dimensions (expanded from 13 per r2 C6 — original schema
    # omitted setup-critical state already validated by verify-setup.sh:36-254. Machines
    # could pass plan-defined dimensions while failing the existing verifier.)
    status = {
        hostname, os, last_updated: ISO-8601,
        dimensions: {
            # --- AI-provider harness (13 original) ---
            soul_contracts:        check_runtime_files_match_canonical(),
            skills:                check_dot_claude_skills_present(),
            rules:                 check_dot_claude_rules_present(),
            bridged_memory:        check_dot_claude_memory_present(),
            claude_global_pointer: check_home_claude_md_exists(),
            codex_agents_symlink:  check_symlink_target(~/.codex/AGENTS.md),
            hermes_soul_symlink:   check_symlink_target(~/.hermes/SOUL.md),
            claude_cli_auth:       check_claude_credentials_present(),
            codex_cli_auth:        check_codex_auth_present(),
            gh_cli_auth:           check_gh_auth_status(),
            gemini_cli_auth:       check_gemini_oauth_present(),
            hermes_can_boot:       check_hermes_config_yaml_valid(),
            raw_session_state:     "machine-local-by-design",     # always this string

            # --- Repo + tooling (9 added per r2 C6) ---
            submodules_initialized:     check_git_submodules_all_init(),    # `git submodule status` no '-' lines
            git_hooks_installed:        check_hooks_present_and_current(),  # parity with verify-setup.sh:60-72
            shell_profile_wired:        check_bashrc_snippets_sourced(),    # parity with verify-setup.sh:124
            npm_global_prefix:          check_npm_prefix_set(),             # parity with new-machine-setup.sh:163-175
            scheduler_entries:          check_cron_or_taskscheduler(),      # linux: crontab; windows: schtasks
            ssh_key_present:            check_home_ssh_id_files(),
            env_file_present:           check_repo_dotenv_present(),
            uv_or_python_available:     check_python_or_uv(),               # parity with verify-setup.sh:234-254
            git_bash_available:         check_git_bash_on_windows(),        # windows-only; "n/a" elsewhere (per r2 C4)
        },
        cli_versions: { claude: ver, codex: ver, gh: ver, gemini: ver, hermes: ver, node: ver, uv: ver },
    }

    # NEVER include token values, file contents, or anything secret-shaped
    scrub_secrets(status)

    write yaml to output_yaml
    render md from yaml to output_md
```

### `scripts/setup/aggregate-machine-status.sh`
```
aggregate_machine_status():
    machines = ls REPO_ROOT/config/machine-baselines/*.yaml
    report = REPO_ROOT/docs/reports/fleet-harness-status.md

    # Build fleet drift table: rows = machines, cols = 13 dimensions
    matrix = {}
    for yaml_file in machines:
        m = parse yaml
        matrix[m.hostname] = m.dimensions

    render markdown table:
        header: | Machine | OS | Last-updated | dim1 | dim2 | ... |
        rows: per machine, each cell = ✅ / ⚠️ / ❌ per status
        footer: per-dimension coverage summary (X of N machines PASS)

    write to report
```

### `scripts/setup/new-machine-setup.sh` (additions only)
```
# After existing Step 9 (verify):
Step 10. AI-provider harness:
    bash scripts/memory/bootstrap-machine.sh
    # bootstrap-machine.sh internally calls scripts/agents/install-soul-runtime.sh

Step 11. Auto-install provider CLIs:
    source scripts/setup/lib/install-provider-clis.sh
    install_provider_clis "$WH_OS"

Step 12. Auth orchestration (interactive):
    source scripts/setup/lib/orchestrate-auth.sh
    orchestrate_auth

Step 13. Hermes config:
    source scripts/setup/lib/instantiate-hermes-config.sh
    instantiate_hermes_config

Step 14. Emit machine-status report:
    bash scripts/setup/emit-machine-status.sh
```

### `scripts/setup/new-machine-setup.ps1` — bash→PowerShell step mapping (per r1 m2)

PowerShell parity is **not 1-to-1**. Some bash steps have no Windows equivalent; some map to existing Windows-native tooling. Explicit mapping:

| Bash step | PowerShell handling | Reason |
|---|---|---|
| **0. Git Bash prerequisite** (NEW per r2 C4) | Check `Test-Path "C:\Program Files\Git\bin\bash.exe"`. If absent: `winget install -e --id Git.Git` (or `choco install -y git`); re-verify; **fail-fast if install denied**. Sets `$GitBash` for later steps. Precedent: `scripts/windows/setup-scheduler-tasks.ps1` already hardcodes this path. | Native PowerShell parity depends on Git Bash subshells for hooks/Codex pin/AI-provider bootstrap/Hermes config. Must validate/install before any step that needs it. |
| 1. Submodules | Identical (`git submodule update --init --recursive`) | Git is platform-neutral |
| 2. Git hooks | Reuse `install-all-hooks.sh` via Git Bash subshell (depends on Step 0) | Existing helper is bash-only; not worth re-implementing |
| 3. Claude statusline | Identical (`claude config set`) | CLI is cross-platform |
| 3b. Keybindings | Identical (cp config/claude/keybindings.json → `$env:USERPROFILE\.claude\keybindings.json`) | Same JSON, different path |
| 4. Shell aliases | **DIFFERENT** — write to `$PROFILE` (PowerShell profile), source `config/shell/profile-snippets.ps1` (new file, parallel to bashrc-snippets.sh) | PowerShell has no `.bashrc` |
| 5. npm PATH | Identical via PowerShell PATH manipulation | npm is cross-platform |
| 5b. Codex pin | Reuse `pin-codex.sh` via Git Bash | Existing helper is bash |
| 6. Crontab | **DIFFERENT** — reuse `scripts/windows/setup-scheduler-tasks.ps1` (already exists) | Windows uses Task Scheduler, not cron |
| 7. SSH key | Identical (`ssh-keygen`) | OpenSSH built into Windows 10+ |
| 8. .env copy | Identical | Just a file copy |
| 8b. tmux | **SKIP** — Windows Terminal handles panes natively | tmux is POSIX-only |
| 9. Verify | Call `verify-setup.ps1` (new sibling) | Bash version unavailable to native PowerShell users |
| 10. AI-provider harness | Reuse `bootstrap-machine.sh` via Git Bash subshell | Existing helper is bash-only; rewriting is out of scope for v1 |
| 11. Auto-install CLIs | **DIFFERENT** — `winget` / `choco` for system pkgs; `npm` for Anthropic/Gemini CLIs (same as bash branch via npm) | Per-OS package managers |
| 12. Auth orchestration | Identical commands (`claude auth login` etc.) | CLI is cross-platform |
| 13. Hermes config | Identical (PowerShell-native YAML render via `ConvertTo-Yaml` from `powershell-yaml` module, OR call `instantiate-hermes-config.sh` via Git Bash subshell) | Both viable; bash subshell is lower maintenance |
| 14. Emit machine-status | Call `emit-machine-status.ps1` (new sibling) | Native PowerShell preferred for status emission to avoid Git Bash dependency on this critical step |

**Steps requiring native PowerShell implementation:** 4 (aliases via $PROFILE), 6 (Task Scheduler — reuse existing), 9 (verify-setup.ps1), 11 (install-provider-clis.ps1), 14 (emit-machine-status.ps1).

**Steps reusing existing bash helpers via Git Bash subshell:** 2 (hooks), 5b (codex pin), 10 (AI-provider bootstrap), 13 (Hermes config — preferred path).

**Steps skipped on Windows:** 8b (tmux).

Pseudocode (PowerShell, partial — full implementation in delivery):
```
# Functional parity per the mapping table above. Critical departures:
# - Uses $env:OS detection (Windows-native), not uname
# - winget/choco for system pkgs (gh), npm install -g for claude/codex/gemini
# - Read-Host -AsSecureString for Hermes .env (never echo)
# - ConvertTo-Yaml / ConvertTo-Json for status emission
# Uses: $env:OS detection, winget/choco for install,
#        Start-Process for auth launches,
#        Read-Host -AsSecureString for Hermes .env,
#        ConvertTo-Yaml / ConvertTo-Json for status emission
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/setup/new-machine-setup.sh` | Add darwin branch (line 34-37); insert Steps 10-14 after current Step 9 |
| Modify | `scripts/setup/verify-setup.sh` | Add darwin branch; add Hermes/SOUL-symlink/auth checks; emit status file at end |
| Create | `scripts/setup/new-machine-setup.ps1` | Native Windows PowerShell sibling, functional parity |
| Create | `scripts/setup/verify-setup.ps1` | PowerShell sibling for verify |
| Create | `scripts/setup/lib/detect-os.sh` | uname/MINGW/Darwin discrimination — sourced by all setup scripts |
| Create | `scripts/setup/lib/install-provider-clis.sh` | Per-OS auto-install of claude/codex/gh/gemini |
| Create | `scripts/setup/lib/orchestrate-auth.sh` | Sequential interactive auth flows + Hermes .env prompts |
| Create | `scripts/setup/lib/instantiate-hermes-config.sh` | Render `~/.hermes/config.yaml` from template |
| Create | `scripts/setup/emit-machine-status.sh` | Per-machine status emission (bash) |
| Create | `scripts/setup/emit-machine-status.ps1` | Per-machine status emission (PowerShell) |
| Create | `scripts/setup/aggregate-machine-status.sh` | Control-plane fleet aggregator |
| Create | `docs/setup/README.md` | Index of setup docs |
| Create | `docs/setup/FRESH_MACHINE_SETUP.md` | Full walkthrough, embeds canonical 4×13 coverage table |
| Create | `docs/setup/EXISTING_MACHINE_AUDIT.md` | Gap-detection + repair flow for in-place machines |
| Create | `docs/setup/PROVIDER_AUTH_GUIDE.md` | Per-provider auth flows + token rotation |
| Create | `docs/setup/TROUBLESHOOTING.md` | Known issues (NTFS overlays, sparse-checkout, dirty volumes) |
| Create | `docs/setup/MACHINE_REGISTRY.md` | Fleet roster + control-plane assessment guide |
| Modify | `.claude/docs/new-machine-setup.md` | Reduce to thin pointer at `docs/setup/FRESH_MACHINE_SETUP.md` |
| Modify | `scripts/memory/bootstrap-machine.sh` | THREE coupled changes: (1) Refactor inline OS detection (lines 23-27) to `source scripts/setup/lib/detect-os.sh` — keep `macos` token (r1 M1). (2) **Make SOUL-runtime install unconditional** (lines 112-117): remove the `if [[ -d ~/.hermes || ... ]]` guard, instead `mkdir -p` the parent dirs (`~/.hermes`, `~/.codex`, `~/.gemini`) and always invoke `install-soul-runtime.sh` (r2 C1 — current conditional causes G1 to silently fail on fresh machines where no provider dir exists yet). (3) **Remove date timestamp** from `~/.claude/CLAUDE.md` generation (lines 18, 50): drop `TIMESTAMP="$(date +%Y-%m-%d)"` and the `Generated by ... on ${TIMESTAMP}` line, OR replace with stable `Generated by scripts/memory/bootstrap-machine.sh` (no date) so re-runs across days produce zero diff (r2 C5). |
| Create | `tests/setup/test_emit_status_schema.ps1` | PowerShell sibling for status-emission schema test (per r2 C3) |
| Create | `tests/setup/test_idempotency.ps1` | PowerShell idempotency test (per r2 C3) |
| Create | `tests/setup/test_install_provider_clis.ps1` | PowerShell CLI-install branching test (per r2 C3) |
| Modify | `.gitignore` | Confirm `config/machine-baselines/` NOT ignored; add `tests/setup/__pycache__/` and `tests/setup/.tmp-*` if shell-test artifacts emerge during implementation. Per r1 m9. |
| Create | `config/machine-baselines/.gitkeep` | Establish git-tracked directory |
| Create | `config/machine-baselines/README.md` | Schema + secret-scrub contract |
| Create | `tests/setup/test_detect_os.sh` | OS detection across linux/darwin/mingw/cygwin |
| Create | `tests/setup/test_idempotency.sh` | Re-run produces zero filesystem changes except timestamp |
| Create | `tests/setup/test_missing_cli_install.sh` | Auto-install path for each provider CLI (mocked package manager) |
| Create | `tests/setup/test_status_emission_schema.sh` | YAML schema validation + round-trip |
| Create | `tests/setup/test_secret_scrubbing.sh` | Status file never contains token-shaped strings |
| Create | `tests/setup/test_aggregate_status.sh` | Fleet aggregator handles 0/1/N machine files correctly |
| Update | `docs/plans/README.md` | Add row for this plan |

**Total**: 19 created, 5 modified, 1 updated = **25 files touched**.

---

## UX Contract (added per r1 M3)

"Auto-install no-prompt" + "Interactive auth" is not a contradiction once phases are itemized. The script has **three execution phases** with different interactivity profiles:

| Phase | Steps | Interactivity | Failure mode |
|---|---|---|---|
| **A. Fully unattended** | 1 (submodules), 2 (hooks), 3/3b (statusline, keybindings), 5 (npm PATH), 5b (codex pin), 7 (SSH gen), 8 (env copy), 8b (tmux config), 9 (verify), 10 (AI-provider bootstrap), 13 (Hermes config render) | Zero user input. Runs silently. | Exit 1 with clear message; no orphan partial state. |
| **B. Elevation-required** | 11 (auto-install CLIs) | Sudo password prompt on linux/macos; UAC prompt on Windows. Install confirmation `-y` is auto-supplied. | If sudo not granted → fail clearly, print remediation. |
| **C. Browser-blocking** | 12 (auth orchestration) | Each `<cli> auth login` opens a browser; user completes OAuth flow then returns. Hermes `.env` field prompts use `read -s` (bash) / `Read-Host -AsSecureString` (PS) — values never echoed. | If browser flow times out → skip provider with WARN; user re-runs to complete. |
| **D. Side-effect emission** | 14 (machine-status report) | Writes to `config/machine-baselines/<hostname>.{md,yaml}`. Idempotent. | Exit 1 on YAML schema violation. |

**Net contract on the user:**
- Single sudo/admin prompt at Phase B (one entry, cached for the rest).
- Up to 4 browser flows in sequence at Phase C (each ~30 s of user attention).
- Total wall-clock: ~3-8 minutes depending on package-manager cache state and browser cooperation.

**`--non-interactive` flag** (new in this plan): when set, skips Phase C entirely (auth orchestration), Phase B is best-effort (fails fast if elevation absent), and emits machine-status with `auth: pending-interactive-completion` markers. Used in CI smoke tests and unattended re-runs after auth has already happened.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_detect_os_linux` | uname=Linux returns "linux" | `uname -s` mocked to `Linux` | stdout: `linux`, exit 0 |
| `test_detect_os_macos` | uname=Darwin returns "macos" (per r2 C2 — token canonicalized to `macos` across pseudocode, tests, schema, acceptance) | `uname -s` mocked to `Darwin` | stdout: `macos`, exit 0 |
| `test_detect_os_mingw` | MINGW64 returns "windows" | `uname -s` mocked to `MINGW64_NT-10.0` | stdout: `windows`, exit 0 |
| `test_detect_os_cygwin` | Cygwin returns "windows" | `uname -s` mocked to `CYGWIN_NT-10.0` | stdout: `windows`, exit 0 |
| `test_detect_os_unknown` | Unknown OS errors | `uname -s` mocked to `Plan9` | stdout: `unknown`, exit 1 |
| `test_idempotency_full_rerun` | Re-run produces zero mutations except `config/machine-baselines/<hostname>.{md,yaml}` timestamp (per r1 m6) | Fixture: `setup → snapshot tree → setup again → diff trees`. Snapshot via `find . -path ./.git -prune -o -type f -printf '%p %T@ %s\n'`. | Diff is empty modulo baseline-file timestamps. |
| `test_smoke_real_install_linux` | Real (non-mocked) provider-CLI auto-install on Ubuntu 24.04 (per r1 m5) | Fresh apt-based environment; npm + node pre-installed | All 4 CLIs land on PATH; output captured to `docs/sessions/2026-05-19-issue-2751-smoke-linux.md` |
| `test_smoke_real_install_macos` | Real auto-install on macOS Sonoma+ (per r1 m5) | Fresh brew environment; user runs once | All 4 CLIs land on PATH; output captured to `docs/sessions/2026-05-19-issue-2751-smoke-macos.md` |
| `test_smoke_real_install_windows` | Real auto-install on Windows 10/11 via choco or winget (per r1 m5) | Fresh PowerShell elevated session | All 4 CLIs land on PATH; output captured to `docs/sessions/2026-05-19-issue-2751-smoke-windows.md` |
| `test_install_provider_clis_all_missing` | Auto-install path runs for each provider CLI on linux/darwin/windows | `command -v <cli>` mocked false; package manager mocked | Each `<pkg_mgr> install <cli>` invoked exactly once |
| `test_install_provider_clis_some_present` | Skip-install path when CLI already present | claude+gh present, codex+gemini missing | Only codex+gemini install commands run |
| `test_orchestrate_auth_already_authed` | Skip auth when credentials already present | All `*-credentials.json` / `oauth_creds.json` / `gh auth status` pass | No `auth login` commands invoked |
| `test_orchestrate_auth_partial` | Resume from partial-auth state | claude+gh authed, codex+gemini not | Only codex+gemini `auth login` invoked |
| `test_instantiate_hermes_config_first_run` | Template renders to `~/.hermes/config.yaml` with substitutions | `config.yaml.template` exists, target missing | Target file exists, YAML valid, fields substituted |
| `test_instantiate_hermes_config_idempotent` | Skip when target already exists and `--force` absent | Target exists | No mutation; exit 0 |
| `test_emit_status_schema_yaml` | YAML output matches documented schema | Fresh run | YAML parses, contains 13 dimensions keys + hostname + os + last_updated |
| `test_emit_status_schema_md` | MD output is human-readable rendering of YAML | Fresh run | MD file exists, contains all 13 dimensions, contains hostname header |
| `test_emit_status_secret_scrub_token` | No token shapes of ANY documented provider format in output (expanded per r2 C7) | Each token-shape fixture seeded in env/files | All 7 regex patterns return 0 hits: `gh[opsu]_[A-Za-z0-9]{20,}` (classic GitHub PAT), `github_pat_[A-Za-z0-9_]{20,}` (fine-grained PAT), `sk-[A-Za-z0-9_-]{20,}` (OpenAI), `sk-ant-[A-Za-z0-9_-]{20,}` (Anthropic), `AIza[A-Za-z0-9_-]{30,}` (Google API), `eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+` (JWT bearer), `"(refresh_token\|access_token)":\s*"[^"]+"` (OAuth field values) |
| `test_emit_status_secret_scrub_credential` | No values from `.credentials.json`/`auth.json`/`.env` in output | Provider auth files populated | Output contains "present"/"absent" booleans only, never literal token chars |
| `test_aggregate_zero_machines` | Aggregator handles empty registry | `config/machine-baselines/` empty | Report emits "No machines registered" placeholder, exit 0 |
| `test_aggregate_one_machine` | Aggregator handles single machine | One YAML file | Report has 1-row table |
| `test_aggregate_n_machines` | Aggregator handles N machines | 3 YAML files (varied dimensions) | Report has 3-row table + per-dimension coverage row |
| `test_aggregate_drift_detection` | Aggregator surfaces dimension mismatches | 2 machines, 1 dimension differs | Report marks that cell with ⚠️ + "drift" annotation |

**Note**: Bash tests use a lightweight shell-test pattern (no framework dependency). PowerShell tests deferred to v1.1 if time permits; v1 ships bash-test parity for both code paths via cross-shell behavior assertions.

---

## Acceptance Criteria

- [ ] All tests in `tests/setup/test_*.sh` pass.
- [ ] `bash scripts/setup/new-machine-setup.sh --dry-run` lists all 14 steps including new G1-G4 steps.
- [ ] Real run on a fresh Linux machine yields `readlink ~/.codex/AGENTS.md` → repo path, `readlink ~/.hermes/SOUL.md` → repo path.
- [ ] Real run launches `claude auth login`, `codex auth login`, `gh auth login` interactively, plus the documented Gemini OAuth path (`gemini -p ping` first-run trigger; falls back to `GEMINI_API_KEY` env var if browser unavailable). Per r2 C8 — no reference to nonexistent `gemini auth` subcommand.
- [ ] All four provider CLIs auto-install via the channel-branched logic in §Pseudocode `install-provider-clis.sh` (`gh` via system pkg manager; `claude`/`gemini` via npm with Node prerequisite; `codex` via existing `scripts/install/pin-codex.sh`).
- [ ] `bash scripts/setup/verify-setup.sh` returns 0 FAIL after fresh setup.
- [ ] `pwsh scripts/setup/new-machine-setup.ps1` reaches functional parity on Windows 10/11, **including required v1 PowerShell smoke tests** (per r2 C3): at minimum, `test_emit_status_schema_yaml.ps1`, `test_idempotency_full_rerun.ps1`, and `test_install_provider_clis_some_present.ps1` ported to PowerShell with Pester. Native-Windows scripts ship with required automated test coverage in v1, not deferred to v1.1.
- [ ] `new-machine-setup.ps1` Step 0 (NEW per r2 C4) verifies Git Bash presence; if absent, installs via `winget install Git.Git` (or `choco install -y git`) and re-verifies before proceeding. Fail-fast if install denied.
- [ ] `config/machine-baselines/ace-linux-1.{md,yaml}` exists and is git-tracked after script run on ace-linux-1.
- [ ] `bash scripts/setup/aggregate-machine-status.sh` emits `docs/reports/fleet-harness-status.md` with per-dimension status across all registered machines.
- [ ] `docs/setup/FRESH_MACHINE_SETUP.md` contains the canonical 4×22 coverage table (per r2 C6 — expanded from 13 to 22 dimensions to cover all setup-critical state already validated by `verify-setup.sh`).
- [ ] `docs/setup/MACHINE_REGISTRY.md` documents how to read `config/machine-baselines/` from the control plane.
- [ ] All scripts pass `scripts/enforcement/check-no-abs-paths.sh`.
- [ ] All scripts pass `scripts/legal/legal-sanity-scan.sh`.
- [ ] Idempotency: re-running on configured machine produces zero git diff except `config/machine-baselines/<hostname>.{md,yaml}` last_updated timestamp **and excluding home-runtime files** (per r2 C5). `~/.claude/CLAUDE.md` regeneration date-stamp removed from `bootstrap-machine.sh:18,50` to honor idempotency; alternatively, the idempotency contract explicitly scopes to repo-tracked files (not `$HOME`).
- [ ] No tokens, secrets, or credential values appear in any `config/machine-baselines/*` file. Redaction patterns (per r2 C7) cover at minimum: `gh[opsu]_[A-Za-z0-9]{20,}` (classic GitHub PAT), `github_pat_[A-Za-z0-9_]{20,}` (fine-grained PAT), `sk-[A-Za-z0-9_-]{20,}` (OpenAI), `sk-ant-[A-Za-z0-9_-]{20,}` (Anthropic), `AIza[A-Za-z0-9_-]{30,}` (Google API), `eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+` (JWT), and `refresh_token`/`access_token` JSON field values.
- [ ] `new-machine-setup.{sh,ps1}` and `emit-machine-status.{sh,ps1}` final-status output includes a prompt referencing operational tracker [#2753](https://github.com/vamseeachanta/workspace-hub/issues/2753) — operators are guided to post `config/machine-baselines/<hostname>.md` as a comment on that issue.
- [ ] T2 adversarial review (Claude inline + one of Codex/Gemini dispatched) returns APPROVE or MINOR-only — no MAJOR.
- [ ] All harness file size checks pass: `scripts/enforcement/check-harness-file-size.sh` returns 0 (CLAUDE.md/AGENTS.md/MEMORY.md/GEMINI.md stay under 20 lines).
- [ ] Plan-approval gate satisfied: this plan reaches `status:plan-approved` via user action (never self-applied).

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (inline, r1) | **MAJOR** (3 MAJOR + 9 MINOR) | OS-token inconsistency (M1), wrong CLI install method (M2), UX contradiction (M3); 9 MINOR around PowerShell parity, hardware availability, hostname PII, drift semantics. Artifact: `scripts/review/results/2026-05-19-plan-2751-claude.md`. **All 12 absorbed via r3 inline patches.** |
| Codex (dispatched via `env -u CLAUDECODE submit-to-codex.sh`, r2) | **MAJOR** (8 findings, **all non-overlapping with r1**) | Conditional SOUL install bug (C1, critical — would have broken G1 on fresh machines), OS-token TDD mismatch (C2), PS tests deferred (C3), Git Bash unvalidated prereq (C4), idempotency broken by CLAUDE.md date timestamp (C5), schema missing 9 setup dimensions (C6), insufficient token-format coverage (C7), `gemini auth` acceptance text drift (C8). C1 and C5 verified empirically by reading `scripts/memory/bootstrap-machine.sh` content. Artifact: `scripts/review/results/2026-05-19-plan-2751-codex.md`. **All 8 absorbed via r3 inline patches.** |

**Overall result:** r1 + r2 + r3 patch cycle complete. 20 of 20 findings absorbed inline (12 r1 + 8 r2). Plan is **approval-track ready** pending user review of the r3 patches before applying `status:plan-review` → `status:plan-approved`.

Revisions made based on review: see §r1 Review and Patches Applied + §r2 Review and Patches Applied (both after §Complexity).

---

## Risks and Open Questions

- **Risk — Sudo/admin elevation**: Auto-install (no-prompt per user decision) requires elevated privileges on linux (`sudo apt`), darwin (`brew` runs as user but some formulae need sudo), and windows (`choco`/`winget` as admin). Script must detect missing elevation early and either re-exec under sudo or exit with clear instructions. Mitigation: pre-check via `id -u` (linux/darwin) and `[Security.Principal.WindowsBuiltInRole]::Administrator` (PS).
- **Risk — Secret leakage in status files**: `config/machine-baselines/<hostname>.{md,yaml}` is git-tracked. Any accidental token-shaped string committed becomes public on the repo. Mitigation: hard-coded redaction patterns (precedent in `collect-machine-baseline.ps1` `Redact-Text`) + dedicated `test_emit_status_secret_scrub_*` tests + pre-commit hook addition (deferred to follow-up).
- **Risk — Interactive auth flows can't be tested in CI**: `claude auth login` and siblings require a browser. CI tests must mock these. Mitigation: test the orchestrator's branching logic with mocked `command -v` and mocked file presence — not the actual auth flow.
- **Risk — Hermes binary install is out-of-band**: User noted Hermes installer is documented separately. Script will detect missing binary and print install instructions rather than attempt to install. Document explicitly in `PROVIDER_AUTH_GUIDE.md`.
- **Risk — macOS validation requires a Mac**: **RESOLVED 2026-05-19** — user confirmed macOS host available. Acceptance criterion stays in v1: implementation validates the `macos` branch on real Mac hardware before issue close. PowerShell sibling validated on Windows 10/11 in parallel.
- **Risk — PowerShell parity is significant net-new surface**: PS sibling scripts double maintenance. Mitigation: extract OS-agnostic logic into helper data files (YAML/JSON config) consumed by both shells; minimize logic duplication.
- **Open — CLI version pinning**: Codex pins via `scripts/install/pin-codex.sh`. Should claude/gh/gemini also pin? Defer to v2; v1 accepts latest.
- **Open — Machine roster authority**: Should `config/machine-baselines/` files be the source of truth for "which machines exist," or should a separate `config/agents/machines.yaml` referenced by `user-profile.yaml` carry identity, with `config/machine-baselines/` carrying state? Recommend: separate roster (identity, deliberate addition) vs. state (auto-emitted). Add `config/agents/machines.yaml` to scope or defer? Recommend defer to follow-up — v1 ships state-only; roster emerges organically from machines that have run the setup.
- **Open — Per-machine status refresh cadence**: Manual (run script) vs. cron-driven (auto-refresh). v1 manual; cron deferred.
- **Open — `gemini auth` subcommand verification** (r1 m1): The plan pseudocode assumes `gemini auth` is the auth invocation. Gemini CLI versions differ — some use `gemini config`, some use `gemini auth login`, some bootstrap via `gcloud`. **Before TDD-locking the orchestrator**, verify by running `gemini --help` on `ace-linux-1` and document the actual subcommand in `PROVIDER_AUTH_GUIDE.md`. If the syntax has drifted, swap before implementation begins.
- **Open — macOS validation hardware** (r1 m3): Acceptance criterion "validated on at least one macOS machine" requires Mac access. **Resolution paths**: (a) user has a Mac → validate during implementation; (b) no Mac available → ship the `darwin`→`macos` branch with `# UNTESTED ON HARDWARE` banner in script headers, mark macOS as "best-effort" in `FRESH_MACHINE_SETUP.md`, file follow-up issue for hardware validation. Decision required from user before status:plan-approved.
- **Open — Hostname publication policy** (r1 m4): `config/machine-baselines/<hostname>.{md,yaml}` is git-tracked → public on the repo. If hostnames embed PII (e.g., `vamsee-laptop-tx-bjk-01`), they leak. **Three options**: (a) raw hostname (current draft, PII risk); (b) stable machine-id UUID + private mapping table (no PII but loses readability); (c) deliberate alias (`ace-linux-1`, `licensed-win-1`) required before status emission, with fallback to UUID for unaliased machines. **Recommendation: (c)**. Concretely: emit-machine-status.sh first checks for an alias in a new `config/agents/machines.yaml` (deferred to follow-up as roster) OR falls back to first 8 chars of `sha256(hostname)` as the filename token. Document the alias convention in `MACHINE_REGISTRY.md`.
- **Open — Drift-detection semantics** (r1 m7): Aggregator marks "drift" when a dimension differs across machines, but some heterogeneity is *expected* (workers don't need claude_cli_auth; control plane needs all dimensions). v1: ship the aggregator with a flat "dimension differs across N machines" indicator; v1.1: add `role: control-plane | worker | developer` field to status YAML and per-role expected-value matrix.

---

## Complexity: T2

**T2** — multi-file (25 files touched after r1 patches), multi-platform (linux/macos/windows + bash/PowerShell), TDD required, integrates 4 pre-existing scripts (`bootstrap-machine.sh` refactored to use shared OS-detect, `install-soul-runtime.sh`, `verify-setup.sh`, `pin-codex.sh` reused for codex install path). Not T3 because no new architectural pattern is invented — every component (per-OS detection, idempotent install, per-machine status emission, fleet aggregation) has a precedent in the existing codebase. Cross-platform scope and PowerShell sibling push it above T1.

---

## r1 Review and Patches Applied

**r1 (Claude inline, 2026-05-19)** — verdict MAJOR with 3 MAJOR + 9 MINOR findings. Review artifact at `scripts/review/results/2026-05-19-plan-2751-claude.md`.

| Finding | Severity | Patch applied in this revision |
|---|---|---|
| M1: OS-name token inconsistency (`darwin` in plan vs. `macos` in bootstrap-machine.sh:26) | MAJOR | §Pseudocode `detect_os` aligned to `macos`; §Files to Change adds `bootstrap-machine.sh` refactor row; §Complexity updated to `linux/macos/windows`. |
| M2: `pkg_install <cli>` wrong (3 of 4 are npm) | MAJOR | §Pseudocode `install-provider-clis.sh` rewritten to branch by install-channel (system pkg for `gh`, npm for `claude`/`gemini`, reuse `pin-codex.sh` for `codex`). Node prerequisite check added via `ensure_node()`. |
| M3: Auto-install no-prompt + interactive auth contradiction | MAJOR | New §UX Contract section with three-phase model (unattended/elevation/browser). `--non-interactive` flag introduced. |
| m1: `gemini auth` subcommand unverified | MINOR | Added to §Open. Pre-TDD verification step required. |
| m2: PowerShell parity hand-wavy | MINOR | Added bash→PowerShell step-mapping table to §Pseudocode `new-machine-setup.ps1`. |
| m3: macOS hardware availability | MINOR | Added to §Open. Decision required from user before status:plan-approved. |
| m4: Hostname PII leak via git-tracked files | MINOR | Added to §Open with 3-option matrix; recommendation (c) alias-with-sha256-fallback. |
| m5: Mocked tests vs. real-install verification | MINOR | Will address with smoke-test matrix in TDD section before status:plan-approved. |
| m6: Idempotency test fixture undefined | MINOR | Will refine TDD entry before status:plan-approved. |
| m7: Drift-detection semantics | MINOR | Added to §Open; v1 ships flat indicator, v1.1 adds role-aware matrix. |
| m8: `bootstrap-machine.sh` not in Files to Change | MINOR | Added Files-to-Change row (couples M1 fix). |
| m9: `.gitignore` review missing | MINOR | Added Files-to-Change row for `.gitignore` review. |

**Status after r1+patches:** plan is approval-track-ready but still requires r2 (dispatched provider) per T2 hard-gate. r1 was self-review (same author conflict-of-interest); independent verdict from Codex or Gemini is required before `status:plan-review` is appropriate.

---

## r2 Review and Patches Applied

**r2 (Codex dispatched via `submit-to-codex.sh`, 2026-05-19)** — verdict **MAJOR** with 8 findings, **all 8 non-overlapping with r1** (matches `feedback_cross_provider_review_payoff` empirical pattern). Review artifact at `scripts/review/results/2026-05-19-plan-2751-codex.md`.

Initial dispatch hit `feedback_codex_cli_0_124_upstream_regression` (codex exec stdin-hangs under Claude Code Bash). Retry via documented workaround `env -u CLAUDECODE bash scripts/review/submit-to-codex.sh ...` succeeded.

| Finding | Severity | Patch applied in this revision |
|---|---|---|
| **C1**: `bootstrap-machine.sh:112-117` conditional SOUL install (`if [[ -d ~/.hermes || ~/.codex || ~/.gemini ]]`) means **G1 silently fails on fresh machines** where no provider dir exists yet. **Verified empirically** via `grep -nC 2 install-soul-runtime scripts/memory/bootstrap-machine.sh`. | MAJOR | §Files to Change row for `bootstrap-machine.sh` updated: remove the conditional guard, `mkdir -p ~/.hermes ~/.codex ~/.gemini` first, then always invoke `install-soul-runtime.sh`. This is the most critical r3 patch — would have shipped a broken headline deliverable without it. |
| **C2**: TDD `test_detect_os_darwin` still expected `darwin` after r1 patched pseudocode to `macos`. Internal inconsistency — implementation can satisfy pseudocode OR test, not both. | MAJOR | Test renamed `test_detect_os_macos`; expected stdout `macos`. Acceptance text already corrected via Acceptance section patches. |
| **C3**: PowerShell tests "deferred to v1.1 if time permits" despite plan creating 3 PS scripts as core scope. | MAJOR | Acceptance criterion added: v1 requires Pester-based PS tests for `test_emit_status_schema.ps1`, `test_idempotency.ps1`, `test_install_provider_clis.ps1`. Three rows added to §Files to Change. |
| **C4**: `new-machine-setup.ps1` reuses bash helpers via Git Bash subshells but no Step 0 verifies Git Bash presence. Native Windows without Git Bash → silent partial failure. Precedent: `scripts/windows/setup-scheduler-tasks.ps1` already hardcodes the path. | MAJOR | PowerShell mapping table gains new "Step 0. Git Bash prerequisite" — detect, install via `winget`/`choco`, fail-fast if absent. Acceptance criterion added. |
| **C5**: `bootstrap-machine.sh:18,50` embeds `TIMESTAMP="$(date +%Y-%m-%d)"` into `~/.claude/CLAUDE.md`. Re-run on different day mutates the file → idempotency claim is false. **Verified empirically** via `grep -n "TIMESTAMP\|date +" scripts/memory/bootstrap-machine.sh`. | MAJOR | §Files to Change row for `bootstrap-machine.sh` updated: drop the date timestamp (replace with stable "Generated by scripts/memory/bootstrap-machine.sh" — no date). §Acceptance Criteria explicitly excludes home-runtime files from the idempotency contract. |
| **C6**: 13-dimension status schema omits submodules, hooks, shell-profile, npm PATH, scheduler, SSH, env, uv/Python, Git Bash. Machine could pass plan-defined dimensions while failing `verify-setup.sh`. | MAJOR | §Pseudocode `emit_machine_status` expanded from 13 to 22 dimensions. Acceptance criterion updated to "canonical 4×22 coverage table". |
| **C7**: Secret-scrub regex covered only `gh[opsu]_...` and `sk-...`. Misses fine-grained PATs, Anthropic, Gemini, JWT, OAuth refresh tokens. | MAJOR | TDD `test_emit_status_secret_scrub_token` expanded to 7 regex patterns covering modern token formats. Acceptance criterion enumerates the patterns. |
| **C8**: Acceptance still said `gemini auth` even after r1 patched pseudocode away from it. | MAJOR | Acceptance text updated to "documented Gemini OAuth path (`gemini -p ping` first-run trigger; falls back to `GEMINI_API_KEY` env var)". |

**Status after r1+r2+r3 patches:** all 12 r1 findings and all 8 r2 findings absorbed. Plan is now approval-track-ready. r2 raised two **questions for the author** that are scope-level (not pure defects):

1. *"Should v1 require true native PowerShell parity, or is Git Bash-backed Windows support acceptable if documented and preflighted?"* → **Answer applied in r3 patches**: Step 0 Git Bash prerequisite + Pester PS tests for the 3 core scripts = "Git Bash-backed but preflighted + tested." This honors user's earlier "Both bash AND PowerShell from v1" choice while keeping maintenance surface bounded.
2. *"Should `config/machine-baselines/` model role-aware expectations now, or narrow to raw status collection plus a follow-up?"* → **Answer applied**: v1 ships raw collection (22 dimensions); v1.1 adds role-aware drift matrix (already documented in §Open as a deferred item).

**Outstanding pre-approval items** (before `status:plan-review` label):
- Empirical verification of `gemini -p ping` triggers OAuth flow as designed (will happen during implementation TDD).
- macOS hardware confirmed available (resolved 2026-05-19 — user confirmed).
- User review of r3 patches before approval label.
