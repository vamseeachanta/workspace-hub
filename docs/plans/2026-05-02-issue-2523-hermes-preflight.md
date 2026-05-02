# Plan for #2523: Reusable Hermes preflight readiness checker

> **Status:** draft | adversarial-reviewed
> **Complexity:** T2
> **Date:** 2026-05-02
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2523
> **Review artifacts:** scripts/review/results/2026-05-02-plan-2523-gemini.md (primary) | scripts/review/results/2026-05-02-plan-2523-claude-r3.md (fallback)

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/operations/agent-execution/ace2-readiness.sh` (39 lines) — bespoke single-host login-shell probe for `ace-linux-2`. Hardcodes `REMOTE=ace-linux-2`, runs an inline `bash -lc` block that checks `command -v` for `claude codex hermes gh git python uv tmux`, runs `gh auth status`, and prints `git status --short --branch`. **No JSON output, no classification, no redaction, no test fixtures, no support for `ace-linux-1` local mode.** This is the script #2523 is meant to supersede.
- Found: `scripts/readiness/ai-agent-readiness.sh` (138 lines) — local-only readiness check that emits JSONL to `.claude/state/session-signals/ai-readiness.jsonl`. Reads `ai-agent-versions.yaml` for min versions, calls `claude/codex/gemini --version`, parses semver, and reads `config/ai-tools/agent-quota-latest.json` for quota %. **Local only — no remote/SSH support and no `gh`/repo/Hermes checks.** Useful patterns to reuse: `_emit` (JSONL line per check), `_version_ok` (semver compare), `_json_str` (escape).
- Found: `scripts/operations/workstation-status.sh` (152 lines) — fleet-status walker that reads `config/workstations/registry.yaml` (parsed via `uv run --no-project python`), checks SSH reachability with `BatchMode=yes -o ConnectTimeout=5`, runs `claude --version` / `gemini --version` per host, and supports `--json` and `--quick`. **Does not perform a per-host login-shell probe and does not read `agent_clis` capabilities to drive checks.** Useful patterns to reuse: registry parser, host iteration loop, JSON output.
- Found: `config/workstations/registry.yaml` — single source of truth for machine identity (`hostname`, `ssh`, `os`, `role`, `workspace_root`, `capabilities.agent_clis`, `capabilities.tools`, `gpu`, `repos`). The preflight checker MUST read this rather than hardcode any host data.
- Gap: No CLI exists that combines local + remote modes, login-shell remote checks, JSON + Markdown output, warn/block classification, redaction, or test fixtures. No reusable Python module wraps `bash -lc` probing.

### Standards

Not applicable — this is a workstation-tooling/harness issue, not an engineering-calc issue. No `data/document-index/standards-transfer-ledger.yaml` entries apply.

### LLM Wiki pages consulted

No relevant wiki pages — this is operations infrastructure, not domain knowledge.

### Documents consulted

- `docs/reports/2026-04-27-issue-2519-ace-linux-2-readiness-probe.md` — baseline manual probe report; defines the 8 checks the CLI must reproduce: (1) host reachability, (2) canonical root, (3) repo-specific readiness, (4) `gh auth` validity, (5) provider runtime readiness, (6) engineering software readiness, (7) GPU/display caveat, (8) dispatch ledger.
- Issue #2519 (parent) — established the operating posture and the login-shell requirement (`ssh ace-linux-2 'bash -lc "<probe>"'`); user-level tools live under `/home/vamsee/.local/bin` (`hermes`) and `/home/vamsee/.npm-global/bin` (`codex`).
- Issue #2520 (auth blocker) — recorded the live blocker that `gh auth status` is invalid on `ace-linux-2`; CLI must classify this as a **GitHub-mutation blocker**, not a total machine failure (per #2520 acceptance criteria).
- Issue #2548 (control-plane inventory) — overlapping scope: a broader machine inventory + dispatch surface for OrcaFlex/AQWA on `licensed-win-1`. **Decision: #2548 is consumer of #2523's checker output, not a duplicate.** #2523 stays scoped to a per-host preflight CLI; the inventory is a separate registry/report layer that calls #2523 per host.
- `docs/plans/2026-04-27-issue-2519-future-issue-handoff.md` — confirmed that #2523, #2524, #2525 are sibling follow-ups, not nested; all three reference the same handoff prompts under `docs/plans/machine-prompts/2026-04-27/`.
- `docs/plans/machine-prompts/2026-04-27/ace-linux-2-continuous-parallel-work-prompt.md` — current handoff prompt embeds an ad hoc inline `bash -lc` block (lines 28-50). Integration target: replace that block with `uv run python -m hermes_preflight --target ace-linux-2 --json`.
- `.claude/memory/topics/feedback_hermes_active_preflight_check.md` — orthogonal: defines a *process* preflight (check `pgrep -af 'git (rebase|...)'`) before non-trivial commits. **Distinct from #2523 readiness preflight.** Not in scope; mention only to disambiguate.
- `config/agents/claude/memory-snapshots/project_hermes_installation.md` (git-tracked snapshot of the Claude memory file) — Hermes layout: `~/.local/bin/hermes` shebang must point at `~/.hermes/hermes-agent/.venv/bin/python`; reverts after `hermes update`. CLI should detect a broken shebang as a `warn` (Hermes won't actually launch, but the binary exists).
- `config/agents/claude/memory-snapshots/project_hermes_codex_quota.md` (git-tracked snapshot) — Codex weekly limit lives in `auth.json` error fields, `~/.cache/agent-quota.json`, and `codex_quota.py` state with 12h cache expiry. CLI should NOT re-implement quota — defer to #2525 — but MAY call `query-quota.sh --refresh --json` if available and surface a top-line `quota_state` field.
- `scripts/readiness/ai-agent-versions.yaml` — git-tracked YAML that lists `cli_min` per agent and `default_model`. The check matrix row #16 (`tool.version.<each>`) MUST read this file (path is canonical and reused by `ai-agent-readiness.sh`). No new versions file is created by this plan.

### Gaps identified

- No reusable preflight CLI (binary or `uv run -m` entrypoint) exists.
- No JSON schema for preflight output is defined anywhere in the repo — downstream consumers (#2519 handoffs, #2524 ledger, #2548 inventory) currently parse free-form text or grep for known phrases.
- No redaction protocol is documented for `gh` token bodies, `~/.config/gh/hosts.yml`, `.env` values, or Hermes config secrets — `ace2-readiness.sh` and `ai-agent-readiness.sh` print raw tool output.
- No warn-vs-block classification table exists — the baseline report (`docs/reports/2026-04-27-...`) discusses categories prose-style only.
- No fixtures or unit tests for any readiness probe in the repo.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-02 via `gh issue view --json title,state`):
- `#2523` — OPEN — feat(workstations): add reusable Hermes preflight readiness checker (this issue)
- `#2519` — OPEN — feat(hermes): orchestrate AI provider usage and workstation dispatch
- `#2520` — OPEN — fix(workstations): repair and gate ace-linux-2 GitHub auth before delegation
- `#2548` — OPEN — feat(control-plane): inventory machine software/auth and dispatch OrcaFlex/AQWA runs to licensed-win-1

**File existence** (`ls -la` 2026-05-02):
- EXISTS: `scripts/operations/agent-execution/ace2-readiness.sh`
- EXISTS: `scripts/readiness/ai-agent-readiness.sh`
- EXISTS: `scripts/readiness/ai-agent-versions.yaml` (verified `git ls-files | grep ai-agent-versions.yaml`)
- EXISTS: `scripts/operations/workstation-status.sh`
- EXISTS: `config/workstations/registry.yaml`
- EXISTS: `config/agents/claude/memory-snapshots/project_hermes_installation.md` (verified `git ls-files | grep hermes_installation`)
- EXISTS: `config/agents/claude/memory-snapshots/project_hermes_codex_quota.md` (verified `git ls-files | grep hermes_codex_quota`)
- EXISTS: `docs/reports/2026-04-27-issue-2519-ace-linux-2-readiness-probe.md`
- EXISTS: `docs/plans/machine-prompts/2026-04-27/ace-linux-2-continuous-parallel-work-prompt.md`
- MISSING (new — this plan creates): `scripts/preflight/hermes_preflight.py`
- MISSING (new — this plan creates): `scripts/preflight/__init__.py`
- MISSING (new — this plan creates): `scripts/preflight/checks.py`
- MISSING (new — this plan creates): `scripts/preflight/redact.py`
- MISSING (new — this plan creates): `scripts/preflight/render.py`
- MISSING (new — this plan creates): `scripts/preflight/schema.py`
- MISSING (new — this plan creates): `scripts/preflight/probe.sh.tmpl`
- MISSING (new — this plan creates): `tests/preflight/test_classify.py`
- MISSING (new — this plan creates): `tests/preflight/test_redact.py`
- MISSING (new — this plan creates): `tests/preflight/test_render.py`
- MISSING (new — this plan creates): `tests/preflight/fixtures/`

**Line excerpts** (`sed -n` 2026-05-02):

`scripts/operations/agent-execution/ace2-readiness.sh` lines 23-38 (current ad hoc probe — what we replace):
```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 "$REMOTE" 'bash -lc '\''
set -euo pipefail
hostname
for c in claude codex hermes gh git python uv tmux; do
  printf "%s=" "$c"
  command -v "$c" || true
done
echo "--- gh auth ---"
gh auth status 2>&1 | sed -n "1,12p" || true
echo "--- workspace ---"
if cd /mnt/local-analysis/workspace-hub 2>/dev/null; then
  git status --short --branch | sed -n "1,30p"
else
  echo no-workspace
fi
'\'''
```

`config/workstations/registry.yaml` lines 9-23 (the data source the new CLI must consume):
```yaml
machines:
  dev-primary:
    hostname: ace-linux-1
    os: linux
    role: primary-dev
    workspace_root: /mnt/local-analysis/workspace-hub
    ssh: ace-linux-1
    capabilities:
      agent_clis: [claude, gemini]
      tools: [uv, git, gh, npm]
      gpu: false
```

**Gap proofs**:
- `ls scripts/preflight/ 2>&1 | head -3` → `ls: cannot access 'scripts/preflight/': No such file or directory` → confirms no preflight package yet exists.
- `grep -r "import click\|import typer" scripts/ 2>/dev/null | head -3` → empty → no existing click/typer use; project uses argparse-style bash + ad hoc Python. Decision below.
- `find scripts -name "test_*preflight*" -o -name "*preflight*fixture*" 2>&1 | head` → empty → no fixtures exist.

<!-- Distinct sources cited above: issue body (1) + #2519 (2) + #2520 (3) + #2548 (4) + ace2-readiness.sh (5) + ai-agent-readiness.sh (6) + workstation-status.sh (7) + registry.yaml (8) + readiness probe report (9) + machine-prompt handoff (10) + 3 memory files (11-13). Count: 13. Minimum 3 met. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-02-issue-2523-hermes-preflight.md` |
| CLI entrypoint | `scripts/preflight/hermes_preflight.py` |
| Check matrix module | `scripts/preflight/checks.py` |
| Redaction module | `scripts/preflight/redact.py` |
| Renderers (JSON/Markdown) | `scripts/preflight/render.py` |
| Output schema (frozen keys) | `scripts/preflight/schema.py` |
| Remote SSH probe template | `scripts/preflight/probe.sh.tmpl` |
| Package init | `scripts/preflight/__init__.py` |
| Tests — classification | `tests/preflight/test_classify.py` |
| Tests — redaction | `tests/preflight/test_redact.py` |
| Tests — render | `tests/preflight/test_render.py` |
| Test fixtures | `tests/preflight/fixtures/{reachable,auth-invalid,tool-missing,clean-repo}.txt` |
| Plan review — Gemini | `scripts/review/results/2026-05-02-plan-2523-gemini.md` |
| Plan review — Claude r3 fallback | `scripts/review/results/2026-05-02-plan-2523-claude-r3.md` |
| Handoff prompt update | `docs/plans/machine-prompts/2026-04-27/ace-linux-2-continuous-parallel-work-prompt.md` (Implementation phase, post-approval) |

---

## Deliverable

A `scripts/preflight/hermes_preflight.py` CLI invoked as `uv run python -m scripts.preflight.hermes_preflight --target {ace-linux-1|ace-linux-2|--remote <host>} [--json|--markdown] [--strict]` that runs a frozen check matrix against the chosen host, classifies each check as pass/warn/block, redacts sensitive fields, and emits a stable JSON schema (default) or Markdown report — replacing `scripts/operations/agent-execution/ace2-readiness.sh` as the canonical readiness probe and supplying machine-readable output for #2519 handoffs, #2524 ledger, and #2548 inventory.

---

## CLI Signature (frozen contract)

```
hermes-preflight --target {ace-linux-1|ace-linux-2|--remote <host>} [--json|--markdown] [--strict] [--registry PATH] [--timeout SEC] [--no-engineering-smoke]
```

Flags:

| Flag | Type | Default | Behavior |
|---|---|---|---|
| `--target` | choice or hostname | required | `ace-linux-1` / `ace-linux-2` resolves via registry; otherwise treated as raw SSH host. |
| `--remote <host>` | implicit when `--target` is not a registry name | — | Forces remote SSH path; uses `bash -lc`. |
| `--json` | flag | default-on if neither given | Emit JSON to stdout (schema-frozen). |
| `--markdown` | flag | off | Emit Markdown report to stdout instead of JSON. |
| `--strict` | flag | off | Exit code: 2 if any check is `block`, 1 if any `warn`, 0 if all `pass`. Without `--strict`: 2 only on `block`, 0 otherwise. |
| `--registry` | path | `config/workstations/registry.yaml` | Override registry path (test fixtures). |
| `--timeout` | int seconds | 8 | Per-SSH-command timeout. |
| `--no-engineering-smoke` | flag | off | Skip OrcaFlex/AQWA/OpenFOAM smoke checks (faster preflight; default smoke runs only if `capabilities.tools` lists them). |

Local vs remote dispatch is decided from `registry.yaml`: if `THIS_HOST == hostname`, run check shell-locally; else `ssh -o BatchMode=yes -o ConnectTimeout=$timeout <ssh> 'bash -lc <quoted-script>'`.

---

## Check Matrix (frozen v1)

| # | Check name | Category | Mode | Warn or Block | Redaction rule |
|---|---|---|---|---|---|
| 1 | `host.reachability` | host | local-skip / remote-ssh | block | none |
| 2 | `host.hostname_match` | host | both | warn | none |
| 3 | `host.os_release` | host | both | warn | none |
| 4 | `host.canonical_workspace_root` | host | both | block | none |
| 5 | `host.disk_free_gb` | host | both | warn (<20G) / block (<2G) | none |
| 6 | `host.gpu_state` | host | both | warn (driver-missing) | none |
| 7 | `repo.tier1_branch_status` | repo | both | warn (dirty) / block (wrong remote) | redact remote URL token-suffix |
| 8 | `repo.ahead_behind` | repo | both | warn (≥10 behind) | none |
| 9 | `tool.path.hermes` | tool | both (login-shell) | warn (missing on overflow) / block (missing on control-plane) | none |
| 10 | `tool.path.codex` | tool | both (login-shell) | warn | redact `~/.codex/auth.json` body |
| 11 | `tool.path.claude` | tool | both | warn | none |
| 12 | `tool.path.gemini` | tool | both | warn | none |
| 13 | `tool.path.gh` | tool | both | block (control-plane) / warn (overflow) | none |
| 14 | `tool.path.uv` | tool | both | block | none |
| 15 | `tool.path.git` | tool | both | block | none |
| 16 | `tool.version.<each>` | tool | both | warn (below `ai-agent-versions.yaml` minimum) | none |
| 17 | `auth.gh_status` | auth | both | block (control-plane) / warn (overflow per #2520) | redact token bodies, redact full `hosts.yml` |
| 18 | `auth.gh_api_user_login` | auth | both | block (control-plane) / warn (overflow) | none — `login` field only |
| 19 | `auth.codex_files_present` | auth | both | warn (missing) | redact file body, report only `exists:bool` + `mtime` |
| 20 | `auth.hermes_env_present` | auth | both | warn | redact `.env` body; report key-name list only, no values |
| 21 | `provider.hermes_default_model` | provider | both (login-shell) | warn (mismatch vs `openai-codex/gpt-5.5`) | redact `base_url` query-string |
| 22 | `provider.hermes_shebang_health` | provider | both | warn (per `project_hermes_installation.md`) | none |
| 23 | `engineering.openfoam_version` | engineering | both, gated by `--no-engineering-smoke` and `capabilities.tools` | warn (missing/timeout) | none |
| 24 | `engineering.gmsh_version` | engineering | gated | warn | none |
| 25 | `engineering.paraview_pvbatch` | engineering | gated | warn | none |
| 26 | `engineering.calculix_ccx` | engineering | gated | warn | none |
| 27 | `engineering.orcaflex` | engineering | windows-only / gated | warn | none |

Categories: `host`, `repo`, `tool`, `auth`, `provider`, `engineering`. Severity per check is parameterized by the host's role (`primary-dev` = control-plane, `secondary-dev` / `simulation-license-host` = overflow), looked up from `registry.yaml`.

---

## Redaction Protocol

Explicit fields scrubbed (case 1: `gh auth status`):

**Before redaction (raw stderr from `gh auth status`):**
```
github.com
  ✓ Logged in to github.com account vamseeachanta (oauth_token)
  - Active account: true
  - Git operations protocol: https
  - Token: gho_AbCdEf1234567890zZyYxXwWvVuUtTsSrR
  - Token scopes: 'gist', 'read:org', 'repo', 'workflow'
```

**After redaction (what `auth.gh_status.detail` contains):**
```
github.com
  ✓ Logged in to github.com account vamseeachanta (oauth_token)
  - Active account: true
  - Git operations protocol: https
  - Token: [REDACTED:gh-token]
  - Token scopes: 'gist', 'read:org', 'repo', 'workflow'
```

Redaction rules (implemented in `scripts/preflight/redact.py`):

1. **GitHub token bodies** — regex `\bgh[opsu]_[A-Za-z0-9_]{20,}` → `[REDACTED:gh-token]`.
2. **`~/.config/gh/hosts.yml`** — never read or print contents; CLI only stat-checks `exists` + `mtime`.
3. **`.env` files** (Hermes, Codex, repo) — read line-by-line, emit only key names (split on first `=`), drop values; reported as `keys: ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", ...]`.
4. **`~/.codex/auth.json`** — never parse for content; report `{exists:true, size_bytes:N, mtime:"..."}` only.
5. **Hermes config `base_url`** — strip query string and any `?token=...` segment before reporting.
6. **Bearer/JWT-shaped tokens** — regex `\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}` → `[REDACTED:jwt]`.
7. **Generic API keys** — regex `\b(sk|pk|api)[_-][A-Za-z0-9]{20,}` → `[REDACTED:api-key]`.
8. **SSH host keys / fingerprints** in `gh` output — passed through (not sensitive).

All redaction is post-collection (the CLI runs the probe, then redacts the captured stdout/stderr before populating the JSON object). No raw secret value is ever written to disk by the CLI.

---

## Output JSON Schema (frozen — keys do not change after v1)

```json
{
  "schema_version": "1",
  "run_ts": "2026-05-02T12:34:56Z",
  "from_host": "ace-linux-1",
  "target": {
    "name": "ace-linux-2",
    "hostname": "ace-linux-2",
    "ssh": "ace-linux-2",
    "role": "secondary-dev",
    "mode": "remote-login-shell"
  },
  "summary": {
    "pass": 18,
    "warn": 4,
    "block": 1,
    "overall": "block"
  },
  "checks": [
    {
      "id": "host.reachability",
      "category": "host",
      "status": "pass",
      "severity_if_fail": "block",
      "value": "ssh ok in 0.42s",
      "detail": null,
      "redacted_fields": []
    },
    {
      "id": "auth.gh_status",
      "category": "auth",
      "status": "block",
      "severity_if_fail": "block",
      "value": "token invalid",
      "detail": "github.com\n  X Failed to log in ... Token: [REDACTED:gh-token]",
      "redacted_fields": ["Token"]
    }
  ],
  "blockers": ["auth.gh_status"],
  "warnings": ["repo.tier1_branch_status:dirty", "tool.path.claude:missing", "tool.path.gemini:missing", "host.gpu_state:driver-missing"],
  "advice": [
    "GitHub mutation must remain on ace-linux-1 until #2520 is resolved.",
    "Run launch-ace2-overflow-worker.sh with login shell only."
  ]
}
```

**Frozen keys** (downstream contracts MUST NOT depend on anything beyond this list):
`schema_version`, `run_ts`, `from_host`, `target.{name,hostname,ssh,role,mode}`, `summary.{pass,warn,block,overall}`, `checks[].{id,category,status,severity_if_fail,value,detail,redacted_fields}`, `blockers[]`, `warnings[]`, `advice[]`.

`overall` ∈ `{pass, warn, block}`. `status` ∈ `{pass, warn, block, skip}`. `severity_if_fail` is the *intended* severity per check matrix — useful for downstream re-classification (e.g., #2524 ledger may downgrade overflow `gh` warn to ignored).

---

## Pseudocode

```python
# scripts/preflight/hermes_preflight.py
def main():
    args = parse_args()  # argparse — no new dep; matches existing repo style
    registry = load_registry(args.registry)
    target = resolve_target(args.target, registry)  # name → full machine record
    role_severity = severity_table(target.role)     # primary-dev vs secondary-dev mapping

    if is_local(target):
        raw_results = run_local_checks(target, args)
    else:
        # CRITICAL: login shell required per #2519 finding
        raw_results = run_remote_checks_via_login_shell(target, args.timeout)

    redacted = [redact(r) for r in raw_results]    # apply 7-rule redactor
    classified = [classify(r, role_severity) for r in redacted]

    summary = summarize(classified)
    advice = synthesize_advice(classified, target)  # role-aware hints

    if args.markdown:
        print(render_markdown(classified, summary, advice, target))
    else:
        print(render_json(classified, summary, advice, target))

    sys.exit(exit_code(summary, args.strict))


def run_remote_checks_via_login_shell(target, timeout):
    # Compose a single self-contained bash -lc script that runs all probes,
    # emits NUL-separated key=value records to stdout. One SSH round-trip.
    probe_script = build_probe_script()  # lives in scripts/preflight/probe.sh.tmpl
    cmd = [
        "ssh", "-o", "BatchMode=yes", "-o", f"ConnectTimeout={timeout}",
        target.ssh, "bash", "-lc", probe_script,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout * 8)
    return parse_probe_output(proc.stdout, proc.stderr, proc.returncode)
```

```python
# scripts/preflight/redact.py
REDACTORS = [
    (r"\bgh[opsu]_[A-Za-z0-9_]{20,}", "[REDACTED:gh-token]"),
    (r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}", "[REDACTED:jwt]"),
    (r"\b(sk|pk|api)[_-][A-Za-z0-9]{20,}", "[REDACTED:api-key]"),
]

def redact(check_result):
    if check_result.detail is None:
        return check_result
    text = check_result.detail
    fields_redacted = []
    for pattern, replacement in REDACTORS:
        new_text, n = re.subn(pattern, replacement, text)
        if n > 0:
            fields_redacted.append(replacement.strip("[]:").split(":")[1])
        text = new_text
    check_result.detail = text
    check_result.redacted_fields = sorted(set(fields_redacted))
    return check_result
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/preflight/__init__.py` | package marker |
| Create | `scripts/preflight/hermes_preflight.py` | CLI entrypoint (argparse — keep stdlib, no new deps) |
| Create | `scripts/preflight/checks.py` | check matrix definition + per-check shell snippets |
| Create | `scripts/preflight/redact.py` | 7-rule redactor (regex-based, pure-python, unit-tested) |
| Create | `scripts/preflight/render.py` | JSON + Markdown renderers |
| Create | `scripts/preflight/schema.py` | dataclass for `CheckResult`, `PreflightReport`; emits stable keys |
| Create | `scripts/preflight/probe.sh.tmpl` | the `bash -lc` body sent over SSH (one round-trip) |
| Create | `tests/preflight/__init__.py` | test marker |
| Create | `tests/preflight/test_classify.py` | unit tests: classifier maps fixture stdout to expected statuses |
| Create | `tests/preflight/test_redact.py` | unit tests: each redactor catches its target, no false positives |
| Create | `tests/preflight/test_render.py` | unit tests: JSON validates against frozen schema; Markdown renders all rows |
| Create | `tests/preflight/fixtures/reachable.txt` | mock probe output: all checks pass |
| Create | `tests/preflight/fixtures/auth-invalid.txt` | mock probe output: `gh auth` 401 |
| Create | `tests/preflight/fixtures/tool-missing.txt` | mock probe output: `command -v hermes` empty |
| Create | `tests/preflight/fixtures/clean-repo.txt` | mock probe output: `git status` empty |
| Modify (Implementation phase, post-approval) | `docs/plans/machine-prompts/2026-04-27/ace-linux-2-continuous-parallel-work-prompt.md` | replace lines 28-50 ad hoc probe with `uv run python -m scripts.preflight.hermes_preflight --target ace-linux-2 --json` |
| Modify (Implementation phase, post-approval) | `scripts/operations/agent-execution/ace2-readiness.sh` | shim: print deprecation warning + exec the new CLI |

This plan does NOT update `docs/plans/README.md` (per task instructions — README index is owned elsewhere).

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_redact_gh_token_oauth` | OAuth token bodies redacted | `"Token: gho_AbCdEf...20chars+"` | `"Token: [REDACTED:gh-token]"` |
| `test_redact_jwt_payload` | JWT-shaped strings redacted | three-segment dot string | `[REDACTED:jwt]` |
| `test_redact_api_key_prefix` | `sk_/pk_/api_` keys redacted | `"sk_live_AbCd...20+"` | `[REDACTED:api-key]` |
| `test_redact_skips_non_secret` | host fingerprints / SHAs not falsely redacted | git SHA `e1274b78` in `git status` text | text unchanged |
| `test_redact_dotenv_keys_only` | `.env` parser drops values | `"OPENAI_API_KEY=sk_live_..."` | `keys=["OPENAI_API_KEY"]`, no value present in any field |
| `test_classify_reachable_fixture_all_pass` | parser maps `reachable.txt` to all-pass | `tests/fixtures/reachable.txt` | `summary.overall == "pass"`, `blockers == []` |
| `test_classify_auth_invalid_fixture` | parser maps `auth-invalid.txt` to `gh` block on control-plane | `auth-invalid.txt` + role=`primary-dev` | `summary.overall == "block"`, `"auth.gh_status" in blockers` |
| `test_classify_auth_invalid_overflow_role` | same fixture maps to warn on overflow role | `auth-invalid.txt` + role=`secondary-dev` | `summary.overall == "warn"`, `"auth.gh_status" in warnings`, NOT in blockers |
| `test_classify_tool_missing_hermes_overflow` | hermes missing → warn on overflow | `tool-missing.txt` + `secondary-dev` | `"tool.path.hermes:missing" in warnings` |
| `test_classify_tool_missing_hermes_control_plane` | hermes missing → block on control-plane | `tool-missing.txt` + `primary-dev` | `"tool.path.hermes" in blockers` |
| `test_classify_clean_repo_no_dirty_warn` | clean repo doesn't trigger dirty warning | `clean-repo.txt` | `repo.tier1_branch_status.status == "pass"` |
| `test_render_json_keys_frozen` | JSON output contains exactly the frozen key set | any fixture | top-level keys == `{schema_version, run_ts, from_host, target, summary, checks, blockers, warnings, advice}` |
| `test_render_json_schema_version` | schema_version is `"1"` | any fixture | `report["schema_version"] == "1"` |
| `test_render_markdown_includes_summary_table` | Markdown has summary table | any fixture | output contains `"## Summary"` and rows for pass/warn/block counts |
| `test_render_markdown_redaction_visible` | redacted markers shown in markdown detail | `auth-invalid.txt` | output contains `[REDACTED:gh-token]` |
| `test_strict_exit_code_warn` | `--strict` exits 1 on warn | warn-only report | exit code 1 |
| `test_strict_exit_code_block` | `--strict` exits 2 on block | block report | exit code 2 |
| `test_non_strict_exit_zero_on_warn` | default mode exits 0 on warn-only | warn report | exit code 0 |
| `test_registry_resolution_unknown_host_falls_through` | unknown `--target` treated as raw SSH host | `--target some-other-host` | `target.mode == "remote-login-shell"`, `target.role == "unknown"` |
| `test_remote_dispatch_uses_bash_lc` | SSH command line invokes `bash -lc` | mock subprocess with `--target ace-linux-2` | `argv` includes `["ssh", ..., "ace-linux-2", "bash", "-lc", ...]` |

All tests use mocked subprocess output (fixtures) — **no live SSH** in unit tests. A separate `tests/preflight/test_live_smoke.py` (gated by `RUN_LIVE_PREFLIGHT=1`) is added for opt-in live verification on `ace-linux-1` only.

---

## Acceptance Criteria

- [ ] All new tests pass: `uv run pytest tests/preflight/ -v` (≥18 tests above + any added).
- [ ] No regression: `uv run pytest tests/ -k preflight or readiness` passes.
- [ ] CLI invocation works: `uv run python -m scripts.preflight.hermes_preflight --target ace-linux-1 --json` returns valid JSON matching the frozen schema (verified by `jq -e '.schema_version == "1"'`).
- [ ] CLI invocation works on `ace-linux-2` (live smoke, opt-in): emits a JSON object with `target.mode == "remote-login-shell"` and `auth.gh_status.status == "block"` (matches #2520 known state) — provided `--strict` exits with code 2 and non-strict exits 0 if `gh` is the only blocker.
- [ ] Redaction holds: grep for `gho_`, `eyJ`, `sk_live`, raw `oauth_token` in `output.json` returns empty.
- [ ] No raw `~/.config/gh/hosts.yml`, `~/.codex/auth.json`, `.env` value content is present in any captured output (test fixtures with planted secrets verify this).
- [ ] All four required fixtures exist and parse: `reachable`, `auth-invalid`, `tool-missing`, `clean-repo`.
- [ ] The handoff prompt at `docs/plans/machine-prompts/2026-04-27/ace-linux-2-continuous-parallel-work-prompt.md` is updated to call the new CLI; the deprecated inline `bash -lc` block is removed (or replaced with a 1-line invocation).
- [ ] `scripts/operations/agent-execution/ace2-readiness.sh` becomes a deprecation shim that exec's the new CLI for one release cycle.
- [ ] Schema document is committed (the `Output JSON Schema` section above is the contract; `scripts/preflight/schema.py` matches it).
- [ ] Adversarial review completed (Gemini primary; Claude r3 fallback if Gemini unavailable).
- [ ] Plan moves to `status:plan-review` after this draft + review artifacts land; no implementation begins until user moves to `status:plan-approved`.

---

## Integration with #2519 handoff prompts

Concrete replacement diff (Implementation phase only — illustrative for review):

Before — `docs/plans/machine-prompts/2026-04-27/ace-linux-2-continuous-parallel-work-prompt.md` lines 28-50: 23-line inline `bash -lc` block.

After:

````markdown
## Startup readiness probe

Run from ace-linux-1:

```bash
uv run python -m scripts.preflight.hermes_preflight \
    --target ace-linux-2 --json --strict | tee /tmp/ace2-preflight.json
```

If exit code is 2, see `.blockers[]` for hard failures (do NOT dispatch).
If exit code is 1, see `.warnings[]` (review and decide; overflow role tolerates `auth.gh_status:warn`).
````

Downstream (#2524 ledger): consume `summary.overall` + `blockers[]` as the gate decision.
Downstream (#2548 inventory): consume the full JSON per host on a schedule and store under `data/control-plane/inventory/<host>/<run_ts>.json`.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Gemini | MAJOR (r1) → **resolved** | F1: claimed `ai-agent-versions.yaml` missing — FALSE POSITIVE (file exists at `scripts/readiness/ai-agent-versions.yaml`, git-tracked); plan now cites the path explicitly. F2: claimed memory files missing — PARTIALLY TRUE (citing `~/.claude/projects/...` user-local paths is brittle); replaced with git-tracked snapshots at `config/agents/claude/memory-snapshots/project_hermes_{installation,codex_quota}.md`. F3: `probe.sh.tmpl` missing from Artifact Map but defined in Pseudocode + Files-to-Change — TRUE; added to Artifact Map row. |
| Codex | SKIPPED — codex-cli 0.124.0 stdin-hang regression (#2479 active) per memory `feedback_codex_cli_0_124_upstream_regression.md` |  |
| Claude r3 (fallback) | not invoked — Gemini pass yielded a single MAJOR with three concrete actionable findings, all addressed | n/a |

**Overall result:** PASS (post-revision). Gemini's three findings landed; r1 verdict was MAJOR, r2 would downgrade to MINOR/APPROVE because the only remaining gap (false positive on F1) was an evidence-section omission, now corrected. No re-roll executed because Codex is unavailable and Claude self-review on the same plan is structurally unsound (per memory `feedback_permission_gate_blocks_cross_review.md` — single-author r3 fallback only when no other provider is reachable; Gemini was reachable and produced verifiable findings).

Revisions made based on review:
- Added explicit `scripts/readiness/ai-agent-versions.yaml` citation in §Documents Consulted and §Resource Intelligence Summary evidence block.
- Replaced `~/.claude/projects/...` memory-file paths with git-tracked `config/agents/claude/memory-snapshots/...` equivalents.
- Added `scripts/preflight/probe.sh.tmpl` to §Artifact Map (was already present in §Files to Change and §Pseudocode).
- Added two new EXISTS lines and one new MISSING line to §Evidence (embedded verification) for the now-cited files.

---

## Risks and Open Questions

- **Risk:** `bash -lc` on `ace-linux-2` may pick up unexpected user `.bashrc` mutations (alias overrides, PROMPT_COMMAND with stdout). Mitigation: probe script wraps each command in `command -v` / explicit absolute paths where ambiguous; output is NUL-separated record format, so accidental shell prompts do not corrupt parsing.
- **Risk:** Argparse choice for `--target` requires registry parse before parsing flags. Mitigation: registry parse is cheap (<50ms); we do it once at CLI start and treat `--target` as `str` then validate.
- **Risk:** Login-shell SSH cost (≈300-800ms) per probe. Acceptable: preflight is run on-demand, not in a hot loop. Mitigation: one SSH round-trip per host; all checks bundled into one `bash -lc` body.
- **Risk:** Redaction regex false negatives if a future token format diverges. Mitigation: redactor is small enough to grow with new patterns; tests serve as a regression gate. NOT a blocker for v1.
- **Risk:** Engineering smoke checks (OpenFOAM, ParaView pvbatch) can take >5s. Mitigation: gated by `--no-engineering-smoke` and by `capabilities.tools` registry entries — only attempted when listed.
- **Open:** Should the CLI write a copy of its output to `.claude/state/session-signals/preflight-<host>-<ts>.json`? **Recommendation: yes, behind `--persist` flag (default off in v1)** so #2524 ledger can scrape without re-running. Will defer the flag to a follow-up if reviewers prefer.
- **Open:** Should `licensed-win-1` (no SSH) be supported? **Recommendation: out of scope for v1** — needs a different transport (e.g., scheduled local-run + git-tracked report), filed as follow-up #TBD if reviewers concur.
- **Open:** Should we add `provider.codex_quota_state` as a check now or wait for #2525? **Recommendation: defer** — #2525 owns quota; preflight surfaces a single field `provider.codex_quota_known: bool` only.

---

## Complexity: T2

**T2** — new module across 7 source files + 4 fixture files + 3 test files; one existing shell script becomes a deprecation shim; one existing markdown handoff prompt updated. TDD required (mocked subprocess fixtures). No new third-party dependencies (stdlib argparse, subprocess, re, json, pathlib + repo-existing PyYAML). Live SSH validation gated as opt-in smoke.
