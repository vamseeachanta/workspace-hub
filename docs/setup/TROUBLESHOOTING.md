# Troubleshooting

Known issues and their resolution. Cross-referenced to feedback memories where applicable.

## During bootstrap

### "sudo: command not found" or auto-install fails

**Symptom:** Step 10 (auto-install provider CLIs) fails with elevation error.

**Cause:** On a fresh container or stripped-down OS, sudo may not be available.

**Fix:** Run the script as root (`sudo bash scripts/setup/new-machine-setup.sh`), OR install the CLIs manually before running setup:

```bash
# Linux (ubuntu/debian)
apt-get install -y gh nodejs npm
npm install -g @anthropic-ai/claude-code @google/gemini-cli

# macOS
brew install gh node
npm install -g @anthropic-ai/claude-code @google/gemini-cli
```

Then re-run `bash scripts/setup/new-machine-setup.sh` (idempotent).

### Codex stdin-hang under Claude Code Bash

**Symptom:** Codex CLI freezes when invoked from inside Claude Code (e.g., via `scripts/review/submit-to-codex.sh`).

**Cause:** Upstream regression — codex exec stdin-detection hangs when `CLAUDECODE` env var is set. Tracked at `feedback_codex_cli_0_124_upstream_regression` and openai/codex#19945.

**Fix:** Prepend `env -u CLAUDECODE` to the dispatch:

```bash
env -u CLAUDECODE bash scripts/review/submit-to-codex.sh --file <path>
```

### Browser flow doesn't open during Step 11 (auth)

**Symptom:** Terminal says "Waiting for OAuth completion..." but no browser opens.

**Causes:**
1. Headless environment (SSH session, container without DISPLAY)
2. Default browser not configured

**Fixes:**
- Set `BROWSER` env var: `BROWSER=firefox bash scripts/setup/new-machine-setup.sh`
- Copy the OAuth URL printed in terminal and open it manually on a machine with a browser; complete the flow; return to terminal.
- For Gemini specifically (which uses `gemini -p ping`): fall back to `GEMINI_API_KEY` env var — set it in `~/.bashrc` before running setup.
- Run setup with `WH_NON_INTERACTIVE=1` to skip Step 11 entirely; complete auth manually after.

## During verification

### `verify-setup.sh` shows WARN for `claude_cli_auth` after successful login

**Symptom:** You just ran `claude auth login` and it succeeded, but verify still says WARN.

**Cause:** Timing — `~/.claude/.credentials.json` may not exist for a few seconds after login. OR Claude wrote to a different path.

**Fix:**
```bash
ls -la ~/.claude/.credentials.json     # confirm it exists
ls -la ~/.claude/                      # check what Claude actually created
```

If the file is in `~/.claude/credentials/` or similar variant, file an issue — the check function may need updating.

### `gh auth status` succeeds in your shell but verify reports WARN

**Cause:** The verify script doesn't inherit your shell's environment — it spawns a clean subshell which may not have your PATH.

**Fix:** Check that `gh` is in `/usr/bin/`, `/usr/local/bin/`, or `/opt/homebrew/bin/` (system locations) rather than only your `~/.bashrc`-sourced PATH.

## NTFS / Windows-specific

### "filesystem refusing dirty volume" mount error

**Cause:** `ntfs3` kernel driver refuses dirty NTFS volumes (per `feedback_ntfs_dirty_volume_mount_path`).

**Fix:** Use `ntfs-3g` (FUSE userspace driver) instead:

```bash
sudo mount -t ntfs-3g -o uid=$(id -u),gid=$(id -g) /dev/sdX /mnt/wsl-shared
```

Auto-replays the NTFS journal. Stable for git operations.

### Git symlinks read as `IntxLNK` garbage on NTFS

**Cause:** In-kernel `ntfs3` reads `ntfs-3g`-created symlinks as raw `IntxLNK` data (per `feedback_ntfs3_symlink_intxlnk`).

**Fix:** Stay on `ntfs-3g` for git repos. Don't switch to `ntfs3` if you have symlinks in your worktree (workspace-hub does).

## Multi-session / parallel-work hazards

### `git status` shows files as UU (both modified) but no MERGE_HEAD exists

**Cause:** A parallel session ran `git pull --rebase --autostash` while your session was editing. The autostash pop hit conflicts. The merge "completed" without setting MERGE_HEAD but left files in unmerged state.

**Fix (recommended):** Reset to HEAD if the affected files are auto-generated dashboards/reports:

```bash
git checkout HEAD -- <list of UU files>
```

For other files, inspect with `git diff <file>` to decide.

**Prevention:** Before starting heavy editing, check for parallel claude/codex/hermes processes:

```bash
pgrep -af "claude|codex|hermes" | grep -v grep
```

If multiple sessions are active, coordinate or pause one.

### Auto-sync push race — "Everything up-to-date" but you just committed

**Symptom:** You run `git push` after a commit; it says "Everything up-to-date" before you could push.

**Cause:** A post-commit hook auto-pushed for you (per `feedback_autosync_silent_pusher`).

**Diagnosis:**
```bash
git reflog | head -5     # see what happened
git log -1 --format='%h %s'   # confirm your commit is on origin
git fetch && git log --oneline origin/main..HEAD     # should be empty
```

If empty, you're fine — the push happened silently.

## Idempotency violations

### Re-running `new-machine-setup.sh` shows diffs that shouldn't be there

**Symptom:** After re-run, `git status` shows files changed besides `config/machine-baselines/<token>.{md,yaml}` last_updated.

**Cause:** A check inside `bootstrap-machine.sh` or similar leaked content into a tracked file. Per the plan's r2 C5 patch, this should not happen, but new dimensions could regress.

**Diagnosis:**
```bash
git diff --stat        # see which files
git diff -- <file>     # see what changed
```

**Fix:** File an issue with the diff. The idempotency contract is load-bearing.

## Hermes-specific

### `~/.hermes/config.yaml` not generated even after Step 12

**Cause:** Step 12 is idempotent — if a file already exists, it skips. You may have an empty/stale file from a previous run.

**Fix:** Force re-render:

```bash
source scripts/setup/lib/instantiate-hermes-config.sh
instantiate_hermes_config "$(pwd)" --force
```

### Hermes binary not found, but config installed

**Cause:** The setup script does NOT install the Hermes binary. That's out-of-band per [PROVIDER_AUTH_GUIDE.md#hermes](PROVIDER_AUTH_GUIDE.md#hermes).

**Fix:** Install Hermes separately per upstream docs (typically `pipx install hermes-agent` or similar). Then re-run setup so the symlink installs.

## Sparse-checkout overlays

### Some directories missing from your worktree

**Cause:** Sparse-checkout may be filtering them out (per `feedback_sparse_checkout_add_not_disable`).

**Diagnosis:**
```bash
git config core.sparseCheckout    # is sparse on?
cat .git/info/sparse-checkout     # what's included?
```

**Fix:** Add the missing path:

```bash
git sparse-checkout add <path>
```

**Don't** run `git sparse-checkout disable` on `acma-projects/` — it hangs for ~22 minutes materializing 329K files.

## Cross-references

- [FRESH_MACHINE_SETUP.md](FRESH_MACHINE_SETUP.md) — bootstrap walkthrough
- [EXISTING_MACHINE_AUDIT.md](EXISTING_MACHINE_AUDIT.md) — repair flow
- [PROVIDER_AUTH_GUIDE.md](PROVIDER_AUTH_GUIDE.md) — auth-specific issues
- [MACHINE_REGISTRY.md](MACHINE_REGISTRY.md) — fleet-wide context
