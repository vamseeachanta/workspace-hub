# 2026-07-09 Codex YOLO Default Exit Handoff

## Active Task

Make the plain `codex` command start with approvals and sandboxing disabled from every repository on this machine.

This was a machine-local configuration task. No product implementation or GitHub issue lifecycle was involved.

## Security Warning and Safe Escape

`--yolo` runs commands without approval prompts or sandboxing. OpenAI recommends it only in an externally hardened or isolated environment. This risk was explicitly accepted for this machine-local default.

For one safer session without changing the default, bypass the wrapper and override the global config:

```bash
$HOME/.npm-global/bin/codex --sandbox workspace-write --ask-for-approval on-request
```

If the user requests a permanent rollback, restore `approval_policy = "on-request"` and `sandbox_mode = "workspace-write"` in `$HOME/.codex/config.toml`, move or remove `$HOME/.local/bin/codex`, then run `hash -r`. Do not roll back silently.

## Suggested Skills

- `openai-docs` -- revalidate current Codex configuration and CLI behavior.
- `coordination/pre-completion-cleanup-audit` -- required before a future closeout.
- `operations/mnt-analysis-cleanup` -- only if the user separately authorizes cleanup of pre-existing workspace residue.

## Completed Actions

- Updated `$HOME/.codex/config.toml`:
  - `approval_policy = "never"`
  - `sandbox_mode = "danger-full-access"`
- Installed executable wrapper `$HOME/.local/bin/codex`.
- The wrapper launches `$HOME/.npm-global/bin/codex --yolo "$@"`, giving the YOLO flag higher precedence than trusted project configuration.
- Used a RED/GREEN check: the desired config, wrapper resolution, and flag injection failed before the change and passed afterward.

## Verification Evidence

- Codex CLI: `codex-cli 0.144.1`.
- Config permissions: `0600`; wrapper permissions: `0755`.
- `bash -n` and ShellCheck passed for the wrapper.
- Wrapper execution tracing proved `--yolo` is inserted before caller arguments.
- A fresh interactive Bash shell resolved `codex` to `$HOME/.local/bin/codex`.
- A NUL-safe scan checked all 133 first-level entries under `/mnt/local-analysis`; the 102 entries with root `.git` metadata resolved plain `codex` to the wrapper, with zero timeouts or errors. Seven observed root project configs contained no permission/profile overrides. Nested repositories and other machines were not assessed.
- `codex features list` parsed the user configuration successfully.
- A targeted `scripts/legal/legal-sanity-scan.sh` run against the wrapper passed with no violations.

Official behavior references:

- Configuration precedence: <https://developers.openai.com/codex/config-basic>
- CLI `--yolo`: <https://developers.openai.com/codex/cli/reference>

## Repo / Issue / External-Action State

- No GitHub issue, PR, comment, email, or other external action was created for the configuration change.
- The two operational artifacts are user-level files outside every repository.
- The shared `workspace-hub` checkout was not used for implementation. Preflight found it on `main`, dirty from unrelated state, and diverged from `origin/main`; none of that state was altered or swept into this closeout.
- This handoff is the sole change on branch `chore/codex-yolo-exit-20260709`, based on the then-current `origin/main`.

## Cleanup / Preserved State

- Task-created legal-scan scratch was removed.
- Long-running probes created by this session were terminated.
- Other live Codex/Claude sessions and their processes were preserved.
- Pre-existing cleanup-trash evidence, automation locks/logs, unrelated workspace dirt, and existing stashes were left untouched.
- The full shared-checkout status/stash/partial-file audit exceeded its eight-second bounds; targeted handoff/config paths were verified clean before this document was written.

## Exact Next Checkpoint

No further implementation is required. Open a fresh shell and run:

```bash
codex
```

If reusing a shell that cached the previous executable path, run `hash -r` once first.

Any future request to propagate the default to other machines should start a new GitHub issue and follow the issue -> reviewed plan -> user approval -> implementation lifecycle. Never infer that this machine-local closeout authorizes fleet-wide rollout.
