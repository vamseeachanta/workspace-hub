# Per-provider authentication guide

Authentication for each AI provider in the workspace-hub stack. What the setup script handles automatically (Step 11), what's manual, and how to rotate tokens.

## Quick reference

| Provider | CLI command | Where auth lives | Rotation cadence |
|---|---|---|---|
| Claude (Anthropic) | `claude auth login` | `~/.claude/.credentials.json` | When session expires (subscription-managed) |
| Codex (OpenAI) | `codex auth login` | `~/.codex/auth.json` | When seat changes or token revoked |
| GitHub | `gh auth login` | `~/.config/gh/hosts.yml` | Per token TTL (typically 90 days for fine-grained PATs) |
| Gemini (Google) | `gemini -p ping` (first-run trigger) | `~/.gemini/oauth_creds.json` | Per OAuth refresh-token policy |
| Hermes | `read -s` prompts (.env populate) | `~/.hermes/.env` | Per upstream service token TTL |

## Claude

**Mode: subscription only.** Per `config/agents/claude/SOUL.delta.md`, never use API-key auth (`ANTHROPIC_API_KEY`) without explicit user permission. Claude Max subscription is the paid surface; API-key fallback bypasses the rate-limit budgeting in place.

### First-time auth (Step 11 launches this)

```bash
claude auth login
# Opens browser → Anthropic account login → returns to terminal
```

Auth persists in `~/.claude/.credentials.json` (mode 600). Status emitter checks `[[ -f ]]` — presence only, never reads the file content (per 7-pattern secret-scrub).

### Token rotation

Anthropic subscription auth typically self-refreshes. If you see "authentication required" mid-session:

```bash
claude auth logout
claude auth login
```

### Multi-machine note

Each machine needs its own `claude auth login`. The credentials file is intentionally NOT in the repo and never syncs cross-machine.

## Codex (OpenAI)

### First-time auth (Step 11 launches this)

```bash
codex auth login
# Opens browser → OpenAI account login → returns to terminal
```

Auth persists in `~/.codex/auth.json` (mode 600).

### Version pin

The CLI version is pinned by `scripts/install/pin-codex.sh` (per [#2479](https://github.com/vamseeachanta/workspace-hub/issues/2479)) — Step 5b of bootstrap. Pin is currently `0.123.0` per `scripts/install/codex-pin.env`. Drift triggers a WARN in verify-setup.sh.

### Stdin-hang workaround

If you dispatch Codex from inside Claude Code Bash (e.g., via `scripts/review/submit-to-codex.sh`), you may hit the `feedback_codex_cli_0_124_upstream_regression` issue — codex exec stdin-hangs regardless of version. Workaround: prepend `env -u CLAUDECODE` to the dispatch command. This issue is upstream (openai/codex#19945).

## GitHub

### First-time auth (Step 11 launches this)

```bash
gh auth login
# Choose: github.com → HTTPS → Yes (Git ops) → Login with web browser → paste code
```

Auth persists in `~/.config/gh/hosts.yml`. Status emitter calls `gh auth status` — exits 0 if authed.

### Required scopes

The workspace-hub workflows need:
- `repo` (read+write to issues, PRs, commits)
- `read:org` (for cross-repo navigation)
- `workflow` (if you'll modify Actions)

`gh auth login` defaults are usually sufficient.

### Token rotation

Fine-grained PATs expire on a schedule (typically 90 days). When that happens:

```bash
gh auth logout
gh auth login
# Re-grant required scopes
```

If `gh auth status` returns "401 Bad credentials", that's the trigger.

## Gemini (Google)

### Special: no `gemini auth` subcommand exists

Verified empirically 2026-05-19 via `gemini --help`. The Gemini CLI does NOT have a built-in `auth login` subcommand. Auth happens via one of:

1. **First-run trigger** (Step 11 uses this): `gemini -p "ping"` — if not authed, opens browser OAuth.
2. **gcloud-based**: `gcloud auth application-default login` (requires `gcloud` installed separately).
3. **Env-var**: `export GEMINI_API_KEY=...` (skip-OAuth path; bypass interactive).

After OAuth completes, auth persists in `~/.gemini/oauth_creds.json` (mode 600). Status emitter checks file presence only.

### Token rotation

OAuth refresh tokens auto-renew. If you see auth errors, delete `~/.gemini/oauth_creds.json` and re-run the first-run trigger.

## Hermes

### Hermes is different — no `auth login` flow

Hermes uses a `.env` file at `~/.hermes/.env` containing upstream service credentials. The setup orchestrator (Step 11) prompts for fields via `read -s` so values are **never echoed** to terminal. The file is written with mode 600.

Fields prompted:
- `HERMES_TELEGRAM_BOT_TOKEN` — from BotFather if using Telegram dispatch
- `HERMES_OPENAI_API_KEY` — if Hermes routes to OpenAI
- `HERMES_ANTHROPIC_API_KEY` — if Hermes routes to Anthropic

Leave a field blank to skip — the helper writes only non-empty values.

### Hermes binary install (out-of-band)

The setup script does NOT install the Hermes binary itself. That's a separate installer:

```bash
# Follow upstream installer (typically pip-based):
pipx install hermes-agent
# or per the Hermes project docs at the time of bootstrap
```

After installing the binary, re-run `scripts/setup/new-machine-setup.sh` so Step 9 (bootstrap-machine.sh) can create the symlink `~/.hermes/SOUL.md → repo`.

### Hermes config

Step 12 renders `~/.hermes/config.yaml` from `config/agents/hermes/config.yaml.template` (idempotent — preserves manual edits). Force re-render:

```bash
source scripts/setup/lib/instantiate-hermes-config.sh
instantiate_hermes_config "$(pwd)" --force
```

## Secret-handling guarantees

Per the plan UX Contract + r2 C7 absorption:

1. **Auth values never appear in `config/machine-baselines/<token>.{md,yaml}`**. The status emitter checks file *presence*, never reads token contents.
2. **All output passes through 7-pattern regex scrub** before write: classic GitHub PAT, fine-grained PAT, OpenAI, Anthropic, Google, JWT, OAuth refresh/access tokens.
3. **`read -s` in Hermes prompts**: terminal never displays the value as typed.
4. **Mode 600 enforced** on all credential files we create (`~/.hermes/.env`, `~/.hermes/config.yaml`).

If you ever see what looks like a token leak in a tracked file, file an issue immediately.

## Cross-references

- [FRESH_MACHINE_SETUP.md](FRESH_MACHINE_SETUP.md) — initial bootstrap
- [EXISTING_MACHINE_AUDIT.md](EXISTING_MACHINE_AUDIT.md) — when auth drifts
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — auth-specific issues
- `scripts/setup/lib/orchestrate-auth.sh` — implementation
