---
name: hermes-model-switching
description: Quick provider/model switching for Hermes CLI — aliases, fallbacks, task routing matrix, and utilization audit pattern.
version: 2.0.0
tags: [hermes, model-switching, multi-provider, gemini, openai, claude, routing]
related_skills: [agent-usage-optimizer, overnight-parallel-agent-prompts, multi-machine-ai-readiness-and-issue-triage]
---

# Hermes Model Switching & Cross-Provider Routing

## When to Use

- Starting a session and want to pick the right provider for the task
- Gemini or Codex credits are underutilized (check weekly)
- Need to quickly switch Hermes between providers from command line
- Auditing how stale utilization tracking data is
- Assigning overnight batch tasks across providers

## Quick Switch (Shell Aliases)

Installed in `~/.bash_aliases` (updated 2026-04-09).

```bash
h              # hermes chat (default = config-driven; keep Codex-first)
h-codex        # gpt-5.4 via openai-codex
h-gpt          # same as h-codex
h-mini         # gpt-5.4-mini via openai-codex
h-batch        # gpt-5.2 via openai-codex

h-opus         # claude-opus-4-6 via Anthropic (explicit use)
h-sonnet       # claude-sonnet-4-6 via Anthropic (explicit use)

h-gemini       # gemini-2.5-pro via Google AI Studio direct (explicit use)
h-gemini-flash # gemini-2.5-flash via Google AI Studio direct (explicit use)
h-router-gemini # google/gemini-2.5-pro via OpenRouter (explicit use)

h-router       # qwen/qwen3.6-plus:free via OpenRouter (explicit use)
h-qwen         # same as h-router
h-nemotron     # nvidia/nemotron-3-super-120b-a12b:free via OpenRouter

h-copilot      # claude-sonnet-4.6 via Copilot (explicit use)
h-copilot-gemini # gemini-2.5-pro via Copilot (explicit use)
h-copilot-gpt  # gpt-5.4 via Copilot (explicit use)

h-o3           # o3 via OpenAI
h-which        # show current model block from ~/.hermes/config.yaml
h-quick        # show quick_commands block from ~/.hermes/config.yaml
```

Policy note: Gemini and Copilot remain available, but they are explicit-use only and should not be described or treated as automatic fallback/default routing.

**NOTE**: `h-gemini` and `h-gemini-flash` aliases exist but use `--provider google` which is NOT a valid Hermes CLI provider. Use `h-copilot-gemini` for Gemini via Copilot quota, OR use the direct AI Studio path below to route through your $20/mo Gemini sub instead.

### Gemini via AI Studio Direct API (uses $20/mo Gemini sub, not Copilot quota)

Google AI Studio exposes an OpenAI-compatible endpoint. Hermes can reach it via the
`openrouter` provider with a custom `--base-url`. GEMINI_API_KEY in ~/.hermes/.env
is NOT auto-detected by any provider — it must be passed explicitly.

Test first:
```bash
hermes chat --provider openrouter \
  --api-key $GEMINI_API_KEY \
  --base-url https://generativelanguage.googleapis.com/v1beta/openai/ \
  -m gemini-2.5-pro \
  -e "say hello in 5 words"
```

If that works, add aliases to ~/.bash_aliases:
```bash
alias h-gemini='hermes chat --provider openrouter --api-key $GEMINI_API_KEY --base-url https://generativelanguage.googleapis.com/v1beta/openai/ -m gemini-2.5-pro'
alias h-gemini-flash='hermes chat --provider openrouter --api-key $GEMINI_API_KEY --base-url https://generativelanguage.googleapis.com/v1beta/openai/ -m gemini-2.5-flash'
```

Then reload: `source ~/.bash_aliases`

Pitfall: GEMINI_API_KEY must be set in the shell environment (loaded from .env) for
the $GEMINI_API_KEY expansion to work in the alias. Verify with: `echo $GEMINI_API_KEY`

## Other Switching Methods

1. **In-session**: `/model deepseek:deepseek-chat` or `/model copilot:gemini-2.5-pro`
2. **Persistent config**: `hermes config set model.default <model> && hermes config set model.provider <provider>`
3. **Per-session flag**: `hermes chat -m <model> --provider <provider>`
4. **Interactive wizard**: `hermes model` (TUI picker — slowest method)

## Hermes --provider CLI Choices (HARDCODED — pitfall!)

Valid `--provider` values: `auto, openrouter, nous, openai-codex, copilot-acp, copilot, anthropic, huggingface, zai, kimi-coding, minimax, minimax-cn, kilocode, deepseek`

**DeepSeek was missing** from the hardcoded argparse choices in `hermes_cli/main.py` despite being in the auth registry. Patched on 2026-04-04 (line ~4041). If Hermes updates overwrite this, re-patch or use `/model deepseek:deepseek-chat` in-session instead.

Gemini is now a valid Hermes CLI provider (`hermes chat --provider gemini ...`). However, observed on 2026-04-09 that direct Gemini calls returned HTTP 429 free-tier quota exhaustion (`generate_content_free_tier_requests`) and Hermes then auto-fell back to Copilot, which was also exhausted. So Gemini should not be used as Hermes automatic cheap/default routing until quota behavior is stabilized.

## Horses-for-Courses Task Routing

| Task Type | Primary | Fallback | Rationale |
|-----------|---------|----------|-----------|
| Code implementation | Claude (h-opus) | Codex gpt-5.4 (h-gpt) | Deepest context, best code quality |
| Code review (adversarial) | Codex + Gemini | Claude | Independent eyes, cheaper |
| Research & literature | Gemini (h-gemini) | Claude | 1M+ context window, web grounding |
| Large document analysis | Gemini (h-gemini) | Claude | Long-context advantage |
| Data analysis / viz | Gemini (h-gemini) | Claude | Good at structured data |
| Plan review (adversarial) | All three | — | Policy already mandates this |
| Quick lookups / triage | Gemini Flash (h-gemini-flash) | Codex | Preserve Claude quota |
| Overnight batch prompts | Split evenly | — | Distribute load across all 3 |

## Reality Check (cross-agent audit 2026-04-02)

Config claims vs actual usage — routing must be actively enforced:
- Claude: 95.5% of all work (must actively push tasks to other providers)
- Codex: 99.8% review only, 0% implementation despite config claims
- Gemini: 100% review only, 0% research despite 1M context advantage
- Hermes: 2nd most active agent but absent from routing-config.yaml

## Utilization Data Audit Pattern

When asked about utilization, check these sources in order:

| Source | Path | Freshness Pattern |
|--------|------|-------------------|
| cost-tracking.jsonl | .claude/state/session-signals/ | Usually fresh (246K records, Claude-only) |
| weekly-trends.jsonl | .claude/state/trends/ | Usually fresh (5 weeks) but tracks violations, not credits |
| agent-quota.json | ~/.cache/ | Often stale (no cron refreshes it) |
| config/*_usage.json | config/ | Usually DEAD placeholders (all zeros, 2025 dates) |
| Codex history.jsonl | config/agents/codex/state-snapshots/ | Active raw session logs |
| check_claude_usage.sh | scripts/operations/monitoring/ | Script exists but log file often never created |

**Critical gap**: No automated Codex or Gemini spend tracking. No cron job refreshes any quota data. See #1855.

## Hermes Config (updated 2026-04-09 — Codex-first, no automatic Gemini/Copilot routing)

REASON: repeated Gemini 429 quota exhaustion and Copilot fallback exhaustion caused retry waste and stale-session confusion. Current baseline is Codex-first with smart routing disabled and automatic fallback disabled.

### Available Codex Models (as of 2026-04-08)
| Model | Description | Use Case |
|-------|-------------|----------|
| gpt-5.4 | Latest frontier agentic coding model | Default — general coding, implementation |
| gpt-5.4-mini | Smaller frontier agentic coding model | Quick tasks, cost-conscious |
| gpt-5.3-codex | Frontier Codex-optimized agentic coding model | Deep code generation, Codex-native tasks |
| gpt-5.2 | Optimized for professional work and long-running agents | Overnight batch, long context |

```yaml
model:
  default: gpt-5.4
  provider: openai-codex
  base_url: https://chatgpt.com/backend-api/codex
fallback_providers: []
fallback_model: {}
credential_pool_strategies:
  openai-codex: round_robin
  anthropic: fallback
smart_model_routing:
  enabled: false
  cheap_model:
    provider: openai-codex
    model: gpt-5.4-mini
quick_commands:
  research: { provider: openai-codex, model: gpt-5.4-mini }
  code:     { provider: openai-codex, model: gpt-5.4 }
  review:   { provider: openai-codex, model: gpt-5.4 }
  quick:    { provider: openai-codex, model: gpt-5.4-mini }
  data:     { provider: openai-codex, model: gpt-5.4-mini }
  batch:    { provider: openai-codex, model: gpt-5.2 }
delegation:
  model: gpt-5.4
  provider: openai-codex
```

### Routing Tiers (clean baseline — as of 2026-04-09)
```
DEFAULT:   openai-codex/gpt-5.4
QUICK:     openai-codex/gpt-5.4-mini
BATCH:     openai-codex/gpt-5.2
FALLBACK:  disabled
SMART ROUTING: disabled
```

Important runtime nuance:
- config edits do NOT repair an already-running session whose primary runtime was originally Gemini/Copilot
- `run_agent.py` restores the original primary runtime at the start of each new turn in long-lived sessions
- if logs show `Primary runtime restored for new turn: gemini...`, restart the long-lived Hermes process/session; config alone is not enough

To use Claude explicitly: h-opus, h-sonnet, h-copilot
To use Gemini explicitly: h-copilot-gemini, h-gemini, h-router-gemini

### Credential Pool (as of 2026-04-04)
```
anthropic:    2 creds (hermes_pkce + claude_code OAuth)
openai-codex: 2 creds (both $20/mo subs pooled, round-robin)
copilot:      1 cred  (GH_TOKEN from gh auth token)
deepseek:     1 cred  (DEEPSEEK_API_KEY in .env)
openrouter:   1 cred  (OPENROUTER_API_KEY in .env — added 2026-04-04)
gemini-direct: n/a    (GEMINI_API_KEY in .env — used via openrouter provider + custom base-url)
```
Add more Codex accounts: `hermes auth add openai-codex` → OAuth device flow.
View pool: `hermes auth list`. Reset exhaustion: `hermes auth reset <provider>`.

### Config Pitfall: Provider-Model Mismatch
If default provider is `openai-codex` but delegation.model is `claude-sonnet-4-6`, subagents try Claude on Codex endpoint → fails. **Always set delegation.provider explicitly.**

Similarly, if default is `openai-codex` and you run `hermes chat --provider nous`, it sends the default model name `gpt-5.4` to Nous — which Nous routes through their paid gateway, burning Nous credits instead of using a free model. **Always specify BOTH `--provider` AND `-m` when switching.**

### Config Mismatch Warning
If default provider is openai-codex but delegation.model is claude-sonnet-4-6, subagents will try to run a Claude model on the Codex endpoint — which fails. Always set delegation.provider explicitly when it differs from the default.

## Subscription Economics (Critical Context)

ALL providers use subscription billing — NOT pay-per-token API:
- Claude Max: $200/mo (CLI OAuth via ~/.claude/.credentials.json)
- OpenAI x2: $40/mo ($20 each, subscription)
- Gemini Pro: $20/mo (Google login)
- GitHub Copilot: $9/mo ($107/yr annual)
- **Total: ~$269/mo FIXED** — cost doesn't change with usage volume

Hermes authenticates to Claude via `read_claude_code_credentials()` which reads the Claude Code OAuth token. No separate API key needed — the ANTHROPIC_API_KEY in ~/.hermes/.env is empty/unused.

**Optimization is about maximizing VALUE from fixed spend, not reducing cost per token.** Every unused Gemini query slot is capacity already paid for but wasted.

## Gemini as Advance Scout Pattern

Gemini should run FIRST to prepare context for Claude/Codex coding:

1. **Research before coding** — APIs, standards, libraries → write to notes/prep/
2. **Large document ingestion** — 1M context for specs/PDFs → structured extracts
3. **Codebase recon** — scan repos, map deps → recon reports
4. **Standards mapping** — map functions to API/DNV/ISO standards (zero coding)
5. **Issue triage prep** — scan new issues, draft approach notes
6. **Test data generation** — fixtures, mock data for upcoming TDD work

Simple dispatch pattern:
```bash
# Gemini preps, Claude implements:
h-gemini "Research [topic]. Write findings to /tmp/prep-notes.md"
h-opus "Read /tmp/prep-notes.md. Implement [feature] based on the research."
```

## Subagent Delegation Config

In `~/.hermes/config.yaml`, set delegation model to Sonnet (applied 2026-04-04):
```yaml
delegation:
  model: 'claude-sonnet-4-6'   # was empty (inherited Opus)
  provider: ''                  # inherits parent provider
```
This stops subagents from burning Opus quota on research/triage work.

**Stronger option**: Route delegation through Copilot to fully bypass Anthropic OAuth:
```yaml
delegation:
  model: 'claude-sonnet-4.6'
  provider: 'copilot'
```
This routes ALL subagent work through $9/mo Copilot sub instead of $200/mo Claude OAuth. Use if Anthropic starts billing Hermes as "extra usage."

Within a single session, route subagent work to cheapest capable model:
- **Research/triage subagents** → Sonnet via delegation (NOT Opus)
- **Implementation subagents** → Claude Opus (only when needed)
- **Review subagents** → Codex

**Gemini limitation**: Google/Gemini is NOT a native Hermes provider. Cannot route subagents to Gemini. Use separate terminal sessions (`h-gemini`) or OpenRouter.

## Evidence-Based Routing (Phase-E Audit, 168K calls over 31 days)

Quantified shift opportunity from cross-agent audit:
- ~8,000 Claude read-calls/month → Gemini (research, doc ingestion, standards mapping)
- ~4,000 Claude write-calls/month → Codex (test writing, bounded implementation)
- ~800 Hermes doc-calls/month → Gemini (documentation, literature)
- Gemini reviews (81% approve) → repurpose to research (Codex is the hard gate at 38%)
- Net: Claude drops from 95% → ~65-70% of work

**Decision**: Don't over-engineer routing automation now. The priority order is:
1. Establish workflows (rolling queue, overnight batch, hard-stops)
2. Observe real patterns over 2-4 weeks — which tasks naturally fit which agent
3. Then formalize routing based on evidence, not theory
The current routing matrix is a hypothesis. Let the work prove it. See #1857.

## Rolling 1-Week Agent Work Queue (#1857)

Every agent should always have 5+ tasks queued. File: `notes/agent-work-queue.md`
- Updated every Sunday night
- Overnight pattern: Gemini=Terminal1 (prep), Claude=T2+T5 (impl), Codex=T3+T4 (tests+review)
- Gemini prep tasks explicitly linked to downstream Claude/Codex implementation tasks

## Anthropic Third-Party Harness Policy (CRITICAL — Apr 4, 2026)

Anthropic announced that starting Apr 4, 2026, third-party harnesses using Claude subscription OAuth will draw from "extra usage" (costs extra) instead of subscription quota.

**Hermes IS affected.** It spoofs Claude Code identity:
- Reads OAuth tokens from `~/.claude/.credentials.json`
- Sends `claude-code-20250219` beta headers
- Spoofs Claude Code user-agent version
- Same pattern as OpenClaw (348K stars, users canceling Anthropic subs over this)

**Mitigations:**
1. ~~Claim the free one-time credit (= $200, must redeem by Apr 17, good 90 days)~~ ✅ CLAIMED Apr 4, 2026 — valid 90 days (~Jul 3)
2. Pre-purchase extra usage bundles at up to 30% off
3. Use `--provider copilot` as alternative Claude access path (GitHub auth, not Anthropic OAuth)
4. Route subagents to free OSS models instead of Claude
5. Use Claude Code CLI directly for heavy work (not affected — it's Anthropic's own tool)

**Monitor**: Check `~/.hermes/logs/errors.log` for new error types: `extra_usage_required`, billing-related 402/403. Check https://console.anthropic.com/settings/billing.

As of Apr 4 12:37pm: Hermes still working on subscription. No extra charges detected yet. But OpenAI Plus (one of two subs) is maxed out until Apr 8.

## Proven Batch Execution Pattern (Updated 2026-04-04)

Gemini is most cost-effective when running 5-6 related research tasks per session (~2 min, 26 tool calls, $0 from $20/mo sub).

### Session Structure
```bash
h-router-gemini -t terminal,file,web -q "$(cat /tmp/gemini-batch-N.txt)"
```

### Task Template (for each batch)
- Group 5-6 **related** tasks together (e.g., all standards gaps, all research topics)
- Each task produces ONE file + commits + closes an issue
- Give clear file paths, commit messages, and issue close commands
- Set max 420s timeout per session to avoid rate limiting

### Proven Batches (2026-04-04)
| Batch | Tasks | Duration | Tool Calls | Issues Closed |
|-------|-------|----------|------------|---------------|
| 1 | Hydro mapping + standards gaps (5 tasks) | 5m 17s | 88 | 6 (#1823, #1821, #1822, #1819, #1860, #1864) |
| 2 | Subdomains + research tools (6 tasks) | 2m 3s | 26 | 3 (#1397, #1624, #152) |
| 3 | Research pipeline (5 tasks) | 2m 3s | 26 | 3 (#182, #120, #55) |

### Overnight Cron Pattern
```yaml
# 4 batches spaced 75 min apart through the night
# Each runs once, uses gemini-2.5-pro via openrouter provider
- name: gemini-overnight-batch-1
  schedule: 00:30  # starts at midnight
  model: google/gemini-2.5-pro
  provider: openrouter

- name: gemini-overnight-batch-2
  schedule: 01:30  # 60 min later
  model: google/gemini-2.5-pro
  provider: openrouter
```

### Sandbox Isolation Gotcha
Gemini hermes sessions run in isolated sandboxes. **Files created during the session are destroyed when it ends EXCEPT:**
- Git commits persist (sandbox shares the git repo)
- So: Always commit before session end, don't rely on uncommitted files

### Working vs Broken Aliases (as of 2026-04-04)
```bash
h-router-gemini  # WORKS: hermes chat --provider openrouter -m google/gemini-2.5-pro
h-gemini         # BROKEN: uses custom base-url that Hermes CLI doesn't support
h-copilot-gemini # WORKS: gemini via Copilot sub (uses Copilot quota, not $20 Gemini)
```

**Key finding**: `h-router-gemini` works perfectly for batch research. Use this one, not `h-gemini`.

## Free/OSS Model Tier (Zero Cost Alternatives)

Hermes supports 18 providers.

Hermes supports 18 providers. Several offer FREE open-source models:

| Provider | Command | Free Models | Auth |
|----------|---------|-------------|------|
| Nous Portal | `--provider nous` | `qwen/qwen3.6-plus:free`, `nvidia/nemotron-3-super-120b:free` | Free account |
| DeepSeek | `--provider deepseek` | `deepseek-chat`, `deepseek-reasoner` | Free tier API key |
| HuggingFace | `--provider huggingface` | Qwen3.5-397B, DeepSeek-V3.2, Kimi-K2.5 | Free HF token |
| GitHub Copilot | `--provider copilot` | Claude, Gemini, GPT, Grok — all models! | $9/mo (already paid) |

**Copilot is the hidden gem**: Your $9/mo annual sub gives Hermes access to Claude Opus/Sonnet + Gemini 2.5 Pro + GPT-5.4 through GitHub's auth (separate from Anthropic OAuth).

Copilot aliases (READY — GH_TOKEN configured Apr 4, 2026):
```bash
h-copilot='hermes chat --provider copilot -m claude-sonnet-4.6'
h-copilot-gemini='hermes chat --provider copilot -m gemini-2.5-pro'
h-copilot-gpt='hermes chat --provider copilot -m gpt-5.4'
```

DeepSeek aliases (WORKING — DEEPSEEK_API_KEY configured, CLI patched):
```bash
h-deepseek='hermes chat --provider deepseek -m deepseek-chat'
h-deepseek-reason='hermes chat --provider deepseek -m deepseek-reasoner'
```

**Nous Portal gotcha**: `:free` models are free to RUN, but creating an API key requires a funded account ("out of funds" error at portal.nousresearch.com). Bot detection blocks headless browser signup. Alternative: `hermes setup model` → Nous → OAuth device flow.

**DeepSeek CLI gotcha**: `deepseek` was missing from Hermes CLI `--provider` argparse choices. Patched in `~/.hermes/hermes-agent/hermes_cli/main.py` line ~4041. Hermes updates may overwrite this — re-check after updates.

**Local inference NOT viable**: dev-primary has GTX 750 Ti (2GB VRAM). Use cloud-hosted OSS instead.

**Copilot is the best multi-model hedge**: $9/mo sub gives Claude+Gemini+GPT via GitHub auth, independent of Anthropic OAuth billing. GH_TOKEN auto-generated from `gh auth token`.

## Launch Verification Pattern for Codex GPT-5.4

When a session says the config is fixed, do not stop at `codex --version` or TOML inspection. Verify an actual model invocation.

Use this exact smoke test:
```bash
codex exec --skip-git-repo-check --sandbox read-only -m gpt-5.4 \
  'Reply with exactly CODEX_GPT54_OK and nothing else.'
```

Expected success signals:
- output shows `model: gpt-5.4`
- a session id is created
- final assistant output is exactly `CODEX_GPT54_OK`

Observed on 2026-04-09:
- config loaded cleanly from `~/.codex/config.toml`
- invocation succeeded
- Codex printed `provider: openai` in the exec banner even though the subscription workflow is the Codex CLI path

Important CLI gotcha:
- `codex auth status` is NOT a valid subcommand in `codex-cli 0.118.0`
- use `codex --help`, `codex login --help`, and especially the `codex exec ...` smoke test above instead of trying `status`

## Error Log Monitoring

Check for billing/auth issues: `grep -i '401\|403\|429\|billing\|extra.usage\|rate.limit' ~/.hermes/logs/errors.log`

Known error patterns:
- Anthropic 429 "rate limit exceeded" = subscription rate limit (normal, transient)
- OpenAI 429 "usage_limit_reached" plan_type "plus" = sub maxed, check resets_at timestamp
- Anthropic 401 "Invalid authentication credentials" = OAuth token may need refresh, or policy enforcement
- OpenAI 400 model not supported = wrong model for Codex provider (gpt-4.1, o4-mini, gpt-4o don't work via ChatGPT account)

## Pitfalls

- GEMINI_API_KEY in ~/.hermes/.env is used only when you explicitly route to Gemini. Do NOT rely on Gemini as cheap/default automatic routing.
- Validate `~/.hermes/.env` for bad overrides like `GEMINI_BASE_URL=h-which`. A malformed env base URL can leak into active model state and then into `config.yaml`.
- As of 2026-04-09, Hermes was patched so `_model_flow_api_key_provider()` ignores invalid existing env base URLs and invalid typed base URL overrides unless they start with `http://` or `https://`.
- After fixing `.env`, also inspect `~/.hermes/auth.json` credential_pool entries for stale provider `base_url` residue. We observed Gemini still carrying `base_url: h-which` in auth metadata even after `.env` was corrected.
- If reviewing quota-hardening work, do not mistake the presence of `hermes_cli/codex_quota.py` for a complete solution. The critical check is whether `update_codex_credential_usage(...)` is actually called from live runtime paths. If it is not wired, `/quota` and startup warnings are mostly structural/stale.
- When reviewing provider health summaries, verify they reuse the real provider credential resolution paths. A simple env-var check can miss live configs (example observed: Copilot health checking only `GITHUB_TOKEN` while the actual machine used `GH_TOKEN`).
- OpenRouter key needs credits loaded to run paid models (Gemini, GPT, Claude via OR). Free-tier models like qwen/qwen3.6-plus:free work with zero balance.
- h-gemini uses Google AI Studio endpoint directly (not OpenRouter credits) — explicit use only under the Gemini subscription.
- smart_model_routing should remain disabled on this setup. Re-enabling it with Gemini/Copilot cheap routes reintroduces the exact quota/fallback failure mode that was cleaned up.
- Don't forget `source ~/.bash_aliases` in new terminals for aliases to take effect
- `hermes model` / command-window provider selection can prompt for `Base URL [...]`. If a nonsense token appears there, leave it blank; Hermes now ignores invalid values, but the safest operator habit is still blank unless you intend an advanced override.
- If you see a `128k context` message for Codex, treat it as likely generic metadata fallback, not proof of the real Codex endpoint limit.
- `deepseek` provider was missing from CLI argparse choices — patched in main.py; may need re-patching after Hermes updates
- Running `--provider nous` without `-m` sends the default model (e.g. gpt-5.4) to Nous gateway, burning Nous credits — always specify both provider AND model
- `hermes --h-deepseek` does NOT work — aliases are shell commands, type `h-deepseek` directly (no `hermes` prefix)
- The routing-config.yaml is a specification, not a live router — no script dispatches tasks from it
- cost-tracking.jsonl is the richest data source but Claude-only; you have zero visibility into Codex/Gemini spend
- agent-usage-optimizer sub-skills are all archived — the skill is effectively documentation-only
- Anthropic may start billing Hermes as "extra usage" — monitor errors.log for new error types
- OpenAI Codex provider only supports: gpt-5.4, gpt-5.4-mini, gpt-5.3-codex, gpt-5.2 — older models (gpt-4.1, o4-mini, gpt-4o) are no longer available via ChatGPT account
- GitHub Copilot provider accesses Claude/Gemini/GPT through GitHub auth — different auth path from direct Anthropic OAuth, useful as a hedge
- Nous Portal login has aggressive bot detection — cannot sign up or get API keys via headless browser; must use regular browser at https://portal.nousresearch.com/
- **Stale Codex exhaustion state** persists across three layers after weekly reset: `auth.json` error fields, `~/.cache/agent-quota.json` synthetic entries, and `codex_quota.py` state. As of 2026-04-10, `codex_quota.py` was patched with: (1) `last_error_reset_at` recovery check, (2) `last_error_message`-based detection, (3) 12h staleness expiry for `exhausted_*` cache entries. If false warnings recur, clear all three layers — see #2107.
- To manually clear stale Codex exhaustion: `python3 -c "import json,time; [code to clear auth.json and agent-quota.json]"` — or use `hermes auth reset openai-codex` followed by `query-quota.sh --refresh`.
- Related GitHub issues: #1838 (credit governance), #1839 (workflow hard-stops), #1855 (utilization tracker), #1856 (model switching), #1857 (rolling agent queue), #2107 (auto-clear stale exhaustion), #2108 (quota cache cron scrubber), #2109 (test coverage for recovery logic)
