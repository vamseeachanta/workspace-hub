## Recommended Approach

Recommend **Approach A: PATH shim**, with one minimal Hermes core PATH prepend if service-level PATH cannot be changed safely.

Why: Deckhand policy already declares `path_shim: true` and `scoped_pat: true` as intended enforcement layers in [config/deckhand/policy.yml](/mnt/local-analysis/workspace-hub/config/deckhand/policy.yml:73). The existing hook allows/denies only and explicitly says it cannot inject PATs in [scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py](/mnt/local-analysis/workspace-hub/scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:1). A shim keeps Hermes core edits minimal, applies to foreground and background terminal commands, and reuses the hook’s active-scope state/binding logic.

Approach B is viable but worse: core env injection in `_make_run_env()` would make all subprocesses carry git credential machinery, even when no `git`/`gh` command runs. It also couples workspace-specific Deckhand logic into Hermes core.

UNVERIFIED: the requested artifact `scripts/review/results/2026-06-01-deckhand-wiring-recon-codex.md` does not exist. Closest match `scripts/review/results/2026-06-01-deckhand-b2-plan-codex.md` exists but is zero bytes.

## Exact Patch Points

Recommended A:

1. Add tracked shim files in workspace-hub, for example:
   - `/mnt/local-analysis/workspace-hub/scripts/deckhand/shims/git`
   - `/mnt/local-analysis/workspace-hub/scripts/deckhand/shims/gh`
   - `/mnt/local-analysis/workspace-hub/scripts/deckhand/shims/hub`

2. Install them into a Hermes-owned shim dir, for example:
   - `/home/vamsee/.hermes/deckhand/shims/git`
   - `/home/vamsee/.hermes/deckhand/shims/gh`
   - `/home/vamsee/.hermes/deckhand/shims/hub`

3. Get shim dir onto terminal PATH:
   - Non-core possibility: change the Hermes gateway service/process environment PATH before gateway startup. Hermes local terminal inherits process env into `_make_run_env()` at [local.py](/home/vamsee/.hermes/hermes-agent/tools/environments/local.py:309), then passes it to `subprocess.Popen()` at [local.py](/home/vamsee/.hermes/hermes-agent/tools/environments/local.py:544).
   - I did **not** find a supported local terminal config knob equivalent to `_HERMES_FORCE_PATH`. Existing `_HERMES_FORCE_` only maps `_HERMES_FORCE_FOO` to `FOO` during env construction at [local.py](/home/vamsee/.hermes/hermes-agent/tools/environments/local.py:311).
   - If service-env PATH is not acceptable, make a one-line core touch after `existing_path = run_env.get("PATH", "")` in [local.py](/home/vamsee/.hermes/hermes-agent/tools/environments/local.py:317): prepend `/home/vamsee/.hermes/deckhand/shims` when present.

4. No patch needed at terminal call sites if PATH shim is used:
   - Background local commands pass `env.env` to `spawn_local()` at [terminal_tool.py](/home/vamsee/.hermes/hermes-agent/tools/terminal_tool.py:2040).
   - Foreground commands call `env.execute()` at [terminal_tool.py](/home/vamsee/.hermes/hermes-agent/tools/terminal_tool.py:2253).
   - Local execution builds env once in `_run_bash()` at [local.py](/home/vamsee/.hermes/hermes-agent/tools/environments/local.py:513).

Approach B insertion point if chosen:
- Patch `_make_run_env()` after session env bridge, before `return run_env`, at [local.py](/home/vamsee/.hermes/hermes-agent/tools/environments/local.py:339). It already bridges `HERMES_SESSION_*` into subprocess env at [local.py](/home/vamsee/.hermes/hermes-agent/tools/environments/local.py:341).
- Read active scope from the same session identity/state/binding logic as the plugin: `_identity()` at [plugin __init__.py](/mnt/local-analysis/workspace-hub/scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:195), `_active_scope_name()` at [plugin __init__.py](/mnt/local-analysis/workspace-hub/scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:253), state file at [plugin __init__.py](/mnt/local-analysis/workspace-hub/scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:221), and DM binding fallback at [plugin __init__.py](/mnt/local-analysis/workspace-hub/scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:280).

## Credential Injection Design

Dynamic per-scope PAT lookup:
- Load `/mnt/local-analysis/workspace-hub/config/deckhand/scopes.yml`.
- Resolve active scope from:
  1. `/home/vamsee/.hermes/deckhand/active-scope/<platform>/<chat_id>/<operator_id>.json`
  2. `channel_repo_bindings` fallback
- Get `pat_env` from the selected scope, e.g. `DECKHAND_PAT_ACMA` at [scopes.yml](/mnt/local-analysis/workspace-hub/config/deckhand/scopes.yml:17).
- Read that env var at command time, not install time.

GitHub CLI:
- Export `GH_TOKEN=$PAT`.
- Also export `GITHUB_TOKEN=$PAT` for tools that prefer it.
- This bypasses ambient `gh auth` state without needing to mutate `~/.config/gh`.

Git over HTTPS:
- Use **GIT_ASKPASS**, not URL tokens and not global credential helpers.
- Wrapper creates a temp askpass script under `XDG_RUNTIME_DIR` or `/tmp/deckhand-askpass-$UID/`.
- Set:
  - `GIT_ASKPASS=/path/to/temp/askpass`
  - `GIT_TERMINAL_PROMPT=0`
  - `GIT_CONFIG_COUNT=2`
  - `GIT_CONFIG_KEY_0=credential.helper`
  - `GIT_CONFIG_VALUE_0=`
  - `GIT_CONFIG_KEY_1=credential.useHttpPath`
  - `GIT_CONFIG_VALUE_1=true`
- Askpass returns `x-access-token` for username prompts and the PAT for password prompts.
- Avoid URL token injection because it leaks into process args, remotes, logs, and audit output.

Neutralize ambient creds:
- Unset `GH_TOKEN`, `GITHUB_TOKEN` before setting scoped values.
- Set empty in-process git credential helper via `GIT_CONFIG_*` rather than editing repo/global config.
- Set `GIT_TERMINAL_PROMPT=0` so failure is explicit if the PAT is absent/wrong.
- Optional: set `GH_CONFIG_DIR` to a temp read-only/empty dir for `gh`, but only after validating it does not break `gh api` with `GH_TOKEN`.

Shim bypass:
- Hook already treats absolute-path or basename-path invocations suspicious: `_is_suspicious_tool_token()` returns suspicious when basename is `git`, `gh`, or `hub` but token is not the trusted bare executable at [hook.py](/mnt/local-analysis/workspace-hub/src/deckhand/hook.py:415). That blocks `/usr/bin/git` and `./git` style bypasses when the hook sees the command.

## /scope Identity Fix

Problem: plugin commands dispatch before session vars are set. Plugin dispatch happens at [gateway/run.py](/home/vamsee/.hermes/hermes-agent/gateway/run.py:8078), but `_set_session_env(context)` currently runs later at [gateway/run.py](/home/vamsee/.hermes/hermes-agent/gateway/run.py:8647). The plugin’s `/scope` reads identity through `gateway.session_context.get_session_env()` at [plugin __init__.py](/mnt/local-analysis/workspace-hub/scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:195), so it sees empty values.

Minimal core patch:
- Build `context = build_session_context(source, self.config, session_entry)` and call `_set_session_env(context)` before plugin command dispatch.
- Ensure the existing `finally` still calls `_clear_session_env(_session_env_tokens)` at [gateway/run.py](/home/vamsee/.hermes/hermes-agent/gateway/run.py:9619).
- Remove or guard the later duplicate `_set_session_env()` call around [gateway/run.py](/home/vamsee/.hermes/hermes-agent/gateway/run.py:8651).

Risk:
- Low but real: earlier session context may affect quick commands and skill command resolution. It should be desirable because session context is task-local via contextvars, documented in [session_context.py](/home/vamsee/.hermes/hermes-agent/gateway/session_context.py:20).
- Must avoid clearing vars before normal agent execution.

## Re-Apply / Maintenance Strategy

Keep Hermes edits as generated patches under workspace-hub:
- `patches/hermes/deckhand-path-shim-path-prepend.patch`
- `patches/hermes/deckhand-plugin-command-session-env.patch`

Add install/verify scripts:
- `scripts/deckhand/install-hermes-b2.sh`
  - copies/symlinks shims into `/home/vamsee/.hermes/deckhand/shims`
  - applies Hermes patches with `git apply --check` then `git apply`
  - refuses if target hunks drift
- `scripts/deckhand/verify-hermes-b2.sh`
  - verifies PATH order inside a Hermes terminal command
  - verifies `command -v git/gh/hub` resolves to Deckhand shims
  - verifies `/scope` can see `HERMES_SESSION_USER_ID`
  - verifies `GH_TOKEN` is absent unless scoped command path injects it

Do not hand-edit secrets into tracked files. `pat_env` remains config metadata only.

## Risks + Smallest Safe Validation Sequence

Risks:
- PATH shim does not protect direct non-terminal Python subprocesses unless they run through `PATH` and the hook blocks absolute-path bypasses.
- SSH remotes will not use HTTPS PAT. Validation should either require HTTPS remotes for scoped repos or make the shim rewrite GitHub SSH remotes to HTTPS for command execution only. Prefer requiring HTTPS for B2.
- `gh` may still read ambient config for host/user display; `GH_TOKEN` should control API auth, but validate with `gh auth status` and a token-scoped API call.
- Temp askpass script must be mode `0700` dir and `0700` file, cleaned after exec.

Validation sequence:
1. Read-only identity:
   - In scoped Hermes DM: `/scope`
   - Then terminal: `gh api user -q .login`
   - Confirm it returns the scoped PAT identity, not ambient owner.
2. Read-only repo containment:
   - `gh repo view vamseeachanta/llm-wiki-acma --json nameWithOwner`
   - `git ls-remote https://github.com/vamseeachanta/llm-wiki-acma.git HEAD`
3. Negative read:
   - Attempt `gh repo view` on a repo outside the fine-grained PAT. Expect insufficient scope/access.
4. Sandbox write:
   - Use a throwaway branch/file in the scoped repo, e.g. `deckhand-b2-smoke-<timestamp>`.
   - Push branch over HTTPS with `git push origin HEAD:refs/heads/...`.
   - Delete only if destructive policy/test setup explicitly authorizes it; otherwise leave branch for manual cleanup.
5. Real write:
   - Only after audit log shows ALLOW, scoped identity is verified, and outside-scope negative test fails as expected.
