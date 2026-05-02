# Plan for #2301: bug(hermes): classify and recover from openai-codex transport/challenge failures

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-26
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2301
> **Review artifacts:** scripts/review/results/2026-04-26-plan-2301-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `~/.hermes/hermes-agent/agent/error_classifier.py` (948 lines) — `classify_api_error()` already builds a `FailoverReason` taxonomy (`auth`, `billing`, `rate_limit`, `timeout`, `context_overflow`, `payload_too_large`, `model_not_found`, `provider_policy_blocked`, `format_error`, `thinking_signature`, `long_context_tier`, `unknown`). `APIConnectionError`/`APITimeoutError` are routed through `_TRANSPORT_ERROR_TYPES` (line 240-258) and classified as `FailoverReason.timeout` (line 498).
- Found: `~/.hermes/hermes-agent/agent/error_classifier.py:536-549` — HTTP 403 is classified as `FailoverReason.auth` with `should_fallback=True`. There is **no Codex-specific transport/challenge bucket**: a Cloudflare challenge-403 from `chatgpt.com/backend-api/codex` is treated identically to an auth 403, which is wrong (auth refresh will not unblock CF).
- Found: `~/.hermes/hermes-agent/agent/auxiliary_client.py:218-254` — `_codex_cloudflare_headers()` already exists and pins `originator: codex_cli_rs` + `User-Agent: codex_cli_rs/0.0.0` + extracts `ChatGPT-Account-ID` from the OAuth JWT. The function docstring explicitly calls out `cf-mitigated: challenge` as the failure mode it prevents. It is wired into the primary client (`run_agent.py:1361-1362`) and aux client (`auxiliary_client.py:1217, 1809`).
- Found: `~/.hermes/hermes-agent/run_agent.py:5332` — Codex Responses stream wraps `RemoteProtocolError`, `ReadTimeout`, `ConnectError`, `ConnectionError` in a 1-retry-then-fallback-stream flow. This burns `max_stream_retries` per turn and never escalates to provider fallback.
- Found: `~/.hermes/hermes-agent/run_agent.py:6843-6900` — `_try_activate_fallback(reason: FailoverReason)` switches to next chain entry. The retry loop at line 10766 calls `classify_api_error()` and consults `classified.should_fallback`.
- Gap: no `FailoverReason.codex_challenge` (or equivalent) exists. The `403` branch (line 536) cannot distinguish CF challenge from genuine auth-403 because it does not inspect response headers (`cf-mitigated`, `server: cloudflare`).
- Gap: no operator-facing message that says "this looks like a Codex transport/challenge issue, not a model error". `APIConnectionError` floods to `_vprint` with no actionable hint.
- Gap: no `hermes diagnose codex` (or equivalent) command — the user must `curl -I` manually.
- Gap: tests at `~/.hermes/hermes-agent/tests/agent/test_error_classifier.py` exist but contain no fixture for cf-mitigated headers or `chatgpt.com/backend-api/codex` 403 body shape.

### Standards

Not applicable — Hermes harness behavior, no engineering standard.

### LLM Wiki pages consulted

No relevant wiki pages — this is harness/infra, not a domain-knowledge issue.

### Documents consulted

- Issue body (#2301) — defines failure signature: repeated `APIConnectionError` on `openai-codex/gpt-5.4`, plus probe result `curl -I https://chatgpt.com/backend-api/codex` → `HTTP/2 403` with `cf-mitigated: challenge`.
- Issue #2479 (OPEN, 2026-04-23) — codex-cli 0.124.0 stdin-hang regression; **distinct concern** (dev-time CLI wrapper bug, not Hermes runtime). Now superseded by upstream 0.125.0 (verified via `codex --version` in this env). Do not conflate with #2301.
- Issue #2406 (CLOSED 2026-04-20) — `submit-to-codex.sh` argv-vs-stdin bug. Distinct from #2301 (review-dispatch script, not Hermes inference).
- Hermes config `/home/vamsee/.hermes/config.yaml` lines 1-7: confirms the issue's premise — `provider: openai-codex`, `default: gpt-5.5`, `fallback_providers: []`.
- `.claude/memory/topics/feedback_codex_cli_0_124_upstream_regression.md` — context that codex-cli **dev tool** had a stdin-hang regression. Live verification today: `codex --version` returns `codex-cli 0.125.0` and a successful r4 review (`scripts/review/results/2026-04-26-plan-2511-codex-r4.md`) demonstrates upstream is healthy again.
- `.claude/memory/topics/feedback_codex_sandbox_no_execution.md` — Codex sandbox cannot exec shell. Implication: any plan-side adversarial review can verify documents but cannot run `curl -I` to repro CF challenge. Tests must use mocked fixtures.

### Gaps identified

1. No `FailoverReason` value distinguishes Codex transport/challenge failure from generic timeout or auth.
2. The 403 classification path does not inspect `cf-mitigated`/`server: cloudflare` headers, so CF challenges are silently mis-bucketed as auth.
3. No operator-facing diagnostic message that names the failure mode and points to the request dump path or recovery commands.
4. No `hermes diag codex` (or equivalent) one-shot reachability probe.
5. No regression fixture in `test_error_classifier.py` covers a CF-challenge 403 response body.
6. The default config keeps `fallback_providers: []`. Even after classification works, recovery has no chain to walk. Config must document a recommended transport-only fallback chain (opt-in, not flipped by default — preserves the issue's "Codex-first default" requirement).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-26 via `gh issue view`):
- `#2301` — OPEN — bug(hermes): classify and recover from openai-codex transport/challenge failures
- `#2479` — OPEN — fix(review): Codex stdin-hang regression post-#2406 closure (size-dependent)
- `#2406` — CLOSED — fix(review): submit-to-codex.sh hangs on 'Reading additional input from stdin' for substantial plan files

**Live state-shift probe** (2026-04-26):
```
$ codex --version
codex-cli 0.125.0

$ curl -sI https://chatgpt.com/backend-api/codex | head -5
HTTP/2 403
date: Mon, 27 Apr 2026 03:03:27 GMT
content-type: text/html; charset=UTF-8
content-length: 8428
accept-ch: ...
cf-mitigated: challenge
server: cloudflare
```
The CF-challenge condition is **still reproducible from this environment today**, confirming #2301's premise has not been fixed by upstream. (codex-cli 0.125.0 fixed the unrelated #2479 stdin-hang; #2301's Hermes-runtime gap remains.)

**File existence** (`ls -la` 2026-04-26):
- EXISTS: `~/.hermes/hermes-agent/agent/error_classifier.py`
- EXISTS: `~/.hermes/hermes-agent/agent/auxiliary_client.py`
- EXISTS: `~/.hermes/hermes-agent/run_agent.py`
- EXISTS: `~/.hermes/hermes-agent/tests/agent/test_error_classifier.py`
- EXISTS: `~/.hermes/sessions/request_dump_20260416_085420_dc45db_20260416_085636_052140.json` (the dump cited in #2301 evidence)
- EXISTS: `~/.hermes/config.yaml` (default `fallback_providers: []`)
- MISSING (new — this plan creates): `~/.hermes/hermes-agent/agent/codex_diag.py` (or equivalent diagnostic helper)

**Line excerpts** (`error_classifier.py` status-403 path):
```
536:    if status_code == 403:
537:        # OpenRouter 403 "key limit exceeded" is actually billing
538:        if "key limit exceeded" in error_msg or "spending limit" in error_msg:
...
545:        return result_fn(
546:            FailoverReason.auth,
547:            retryable=False,
548:            should_fallback=True,
549:        )
```
No CF-challenge branch above line 545 — confirms the gap.

```
240:_TRANSPORT_ERROR_TYPES = frozenset({
...
256:    "APIConnectionError",
257:    "APITimeoutError",
258:})
...
498:    if error_type in _TRANSPORT_ERROR_TYPES or isinstance(error, (TimeoutError, ConnectionError, OSError)):
499:        return _result(FailoverReason.timeout, retryable=True)
```
APIConnectionError → `FailoverReason.timeout` (generic). No Codex-host-specific branch.

**Hermes config snapshot** (`head -7 ~/.hermes/config.yaml`):
```
model:
  default: gpt-5.5
  provider: openai-codex
providers: {}
fallback_providers: []
```
Confirms #2301's premise: Codex-first, no fallback configured.

**Source count:** 5 distinct sources cited (issue body, error_classifier.py, auxiliary_client.py, run_agent.py, ~/.hermes/config.yaml) — exceeds the ≥3 minimum.

---

## Verification Log (state-shift before drafting)

- **Bug still reproduces:** YES. `cf-mitigated: challenge` 403 returned on `curl -I` 2026-04-26.
- **Classifier exists:** YES (`error_classifier.py`, 948 lines, FailoverReason enum). #2301 was filed before this module landed; the issue text says "Hermes burns retry budget and dies", which still holds because no CF-specific bucket exists.
- **CF mitigation already partial:** YES (`_codex_cloudflare_headers` pins originator/UA/account-id). Fixes the *common* CF 403 case. But challenges still fire from non-residential IPs / when CF tightens — the headers are necessary, not sufficient.
- **Adjacent issue #2479 healed upstream:** YES (codex-cli 0.125.0 verified working). Do **not** include #2479 work in this plan's scope.
- **No prior plan exists for #2301:** verified by `ls docs/plans/ | grep 2301` → empty.
- **Hermes is at v0.11.0:** `pyproject.toml:version = "0.11.0"` (note: project memory `project_hermes_installation` says v0.4.0; the local install has been updated since).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-26-issue-2301-codex-transport-classification.md |
| Tests (classifier) | `~/.hermes/hermes-agent/tests/agent/test_error_classifier.py` (extend) |
| Tests (diag) | `~/.hermes/hermes-agent/tests/agent/test_codex_diag.py` (new) |
| Implementation (taxonomy) | `~/.hermes/hermes-agent/agent/error_classifier.py` (extend) |
| Implementation (diag helper) | `~/.hermes/hermes-agent/agent/codex_diag.py` (new) |
| Operator-facing wiring | `~/.hermes/hermes-agent/run_agent.py` (modify ~10770-10800 retry-loop block) |
| Config example | `~/.hermes/hermes-agent/cli-config.yaml.example` (annotate `fallback_providers` with transport-only example) |
| Plan review — Claude | scripts/review/results/2026-04-26-plan-2301-claude.md |
| Plan review — Codex | scripts/review/results/2026-04-26-plan-2301-codex.md |
| Plan review — Gemini | scripts/review/results/2026-04-26-plan-2301-gemini.md |
| Docs updates | `~/.hermes/hermes-agent/website/docs/user-guide/troubleshooting/codex-transport.md` (new) |

Note on repo boundary: Hermes lives at `~/.hermes/hermes-agent/` (separate upstream). Changes will be drafted as a Hermes-side patch. Workspace-hub artifacts in scope: only the plan file + review artifacts. The plan is filed against vamseeachanta/workspace-hub#2301 because that is where the operator-facing pain was reported; the actual code change PR will be filed upstream against `NousResearch/hermes-agent`.

---

## Deliverable

A new `FailoverReason.codex_challenge` taxonomy value plus header-aware classification in `error_classifier.py`, an operator-facing diagnostic message printed when this reason fires, a `codex_diag.codex_reachability_probe()` helper, regression fixtures, and config-example annotation that together let Hermes (a) name the failure mode in user-visible output, (b) optionally fall back via an explicitly-configured chain when the operator opts in, and (c) refuse to keep burning retry budget on a CF-challenged endpoint.

---

## Pseudocode

```
# 1. Taxonomy extension (error_classifier.py)
class FailoverReason(enum.Enum):
    ...existing values...
    codex_challenge = "codex_challenge"   # cf-mitigated challenge or 403 from chatgpt.com/backend-api/codex

# 2. Header-aware 403 classification
def _classify_by_status(status_code, ..., body, error, ...):
    if status_code == 403:
        if _is_codex_cloudflare_challenge(error):
            return result_fn(
                FailoverReason.codex_challenge,
                retryable=False,             # do not retry — CF will challenge again
                should_fallback=True,        # walk fallback chain if configured
                should_rotate_credential=False,  # auth refresh will NOT help
            )
        if "key limit exceeded" in error_msg ...:  # existing OpenRouter branch unchanged
            ...
        # existing auth-403 fallthrough unchanged

def _is_codex_cloudflare_challenge(error) -> bool:
    # Inspect response headers attached to the OpenAI SDK exception.
    # The OpenAI APIStatusError carries `.response` (httpx.Response). Headers
    # are case-insensitive. Match: cf-mitigated == 'challenge' OR
    # (server contains 'cloudflare' AND host == chatgpt.com AND status == 403).
    response = getattr(error, "response", None)
    if response is None:
        return False
    headers = getattr(response, "headers", {}) or {}
    cf_mit = (headers.get("cf-mitigated") or headers.get("CF-Mitigated") or "").lower()
    if cf_mit == "challenge":
        host = _safe_request_host(error)
        return host == "chatgpt.com"
    return False

# 3. Reachability probe (codex_diag.py)
def codex_reachability_probe(timeout_sec=5) -> CodexProbeResult:
    # HEAD https://chatgpt.com/backend-api/codex
    # Return: status_code, cf-mitigated value, server header, recommended action.
    # Does NOT use the user's OAuth — just header probe.
    # Returns a structured result the CLI can format for the operator.

# 4. Operator-facing wiring (run_agent.py inside retry loop ~10770)
if classified.reason == FailoverReason.codex_challenge:
    self._vprint(
        f"{self.log_prefix}🚫 Codex backend (chatgpt.com/backend-api/codex) returned a "
        f"Cloudflare challenge. This is NOT a model or quota error.\n"
        f"   Likely cause: this environment's IP is not whitelisted by Cloudflare.\n"
        f"   Latest request dump: {self._latest_request_dump_path()}\n"
        f"   Recovery options:\n"
        f"     • Run from a residential IP, OR\n"
        f"     • Configure fallback_providers (see ~/.hermes/cli-config.yaml.example)\n"
        f"     • Switch provider for this turn: /model <model> --provider openrouter\n"
        f"     • Probe reachability: hermes diag codex\n",
        force=True,
    )
    # Honor classified.should_fallback — _try_activate_fallback() walks the chain.

# 5. Config example annotation (cli-config.yaml.example)
# Add a commented stanza showing transport-only fallback chain:
#
#   # Recommended for environments that hit chatgpt.com CF challenges.
#   # Hermes only walks this chain on classified transport/codex_challenge
#   # failures — it does NOT rotate on quota or model errors.
#   fallback_providers:
#     - provider: anthropic
#       model: claude-opus-4-7
#     - provider: openrouter
#       model: openai/gpt-4o
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `~/.hermes/hermes-agent/agent/error_classifier.py` | add `FailoverReason.codex_challenge`; add `_is_codex_cloudflare_challenge()`; refine 403 branch |
| Create | `~/.hermes/hermes-agent/agent/codex_diag.py` | reachability probe helper |
| Modify | `~/.hermes/hermes-agent/run_agent.py` | operator-facing message in retry loop when `codex_challenge` fires; ensure `should_fallback` is honored without burning retry budget |
| Modify | `~/.hermes/hermes-agent/hermes_cli/cli.py` (or equivalent CLI subcommand entry) | optional: register `hermes diag codex` if the helper is exposed at CLI surface |
| Modify | `~/.hermes/hermes-agent/tests/agent/test_error_classifier.py` | add fixtures for cf-mitigated 403 body |
| Create | `~/.hermes/hermes-agent/tests/agent/test_codex_diag.py` | unit-test the probe helper with mocked httpx |
| Modify | `~/.hermes/hermes-agent/cli-config.yaml.example` | add commented transport-only fallback chain example |
| Create | `~/.hermes/hermes-agent/website/docs/user-guide/troubleshooting/codex-transport.md` | operator doc explaining failure mode + recovery |
| Update | `docs/plans/README.md` | add this plan's row |
| Update | this plan's `Adversarial Review Summary` | after Step 4 |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_classify_codex_challenge_403_cf_mitigated | CF-challenge 403 classifies as `codex_challenge`, not `auth` | mock APIStatusError with `response.headers["cf-mitigated"] = "challenge"`, status 403, host `chatgpt.com` | `reason == FailoverReason.codex_challenge`, `retryable == False`, `should_fallback == True`, `should_rotate_credential == False` |
| test_classify_genuine_auth_403_unchanged | non-CF 403 still classifies as `auth` | mock APIStatusError 403, no cf-mitigated header | `reason == FailoverReason.auth` (regression guard) |
| test_classify_openrouter_keylimit_403_unchanged | OpenRouter 403 "key limit exceeded" still classifies as `billing` | mock APIStatusError 403, body `"key limit exceeded"` | `reason == FailoverReason.billing` (regression guard) |
| test_classify_codex_challenge_no_response_object | exception missing `.response` does not crash classifier | APIError with no response attribute, status 403 | `reason == FailoverReason.auth` (graceful fallback, no exception raised) |
| test_classify_codex_challenge_wrong_host | cf-mitigated header on a non-Codex host does not falsely fire | mock 403 with `cf-mitigated: challenge`, host `api.openai.com` | `reason == FailoverReason.auth` (host gate honored) |
| test_codex_diag_probe_success | probe returns reachable when 200 | mock httpx.head returning 200, no cf-mitigated | `result.reachable == True`, `result.recommendation == "ok"` |
| test_codex_diag_probe_cf_challenge | probe identifies CF challenge | mock httpx.head returning 403 + `cf-mitigated: challenge` | `result.reachable == False`, `result.cf_challenge == True`, `result.recommendation` mentions IP whitelist |
| test_codex_diag_probe_dns_failure | probe handles network errors | mock httpx.head raising ConnectError | `result.reachable == False`, `result.cf_challenge == False`, `result.error_class == "network"` |
| test_run_agent_codex_challenge_message_emitted | operator-facing message is printed when codex_challenge fires | mock retry loop with classified `codex_challenge` reason | captured stdout contains "Cloudflare challenge", "request dump", and "fallback_providers" |
| test_run_agent_codex_challenge_does_not_rotate_creds | credential pool rotation is NOT triggered for codex_challenge | mock retry loop with codex_challenge | `_recover_with_credential_pool` called with `should_rotate_credential=False` (i.e., not invoked) |
| test_classifier_exhaustive_failover_reasons | enum membership regression — new value added without breaking serialization | dump and re-load `FailoverReason.codex_challenge.value` | round-trip equals `"codex_challenge"` |

---

## Acceptance Criteria

- [ ] `FailoverReason.codex_challenge` exists and is documented in the enum docstring.
- [ ] `_is_codex_cloudflare_challenge()` (or equivalent) inspects response headers and returns True only when host is `chatgpt.com` AND `cf-mitigated: challenge` is present.
- [ ] 403 classification: CF-challenge → `codex_challenge`; OpenRouter "key limit exceeded" → `billing` (unchanged); generic 403 → `auth` (unchanged).
- [ ] Retry loop in `run_agent.py` emits an operator-facing message that names "Cloudflare challenge", points to the request-dump path, and lists at least 3 recovery options (run from residential IP, configure `fallback_providers`, switch provider for this turn).
- [ ] `should_fallback=True` is honored — `_try_activate_fallback(FailoverReason.codex_challenge)` is invoked when a fallback chain is configured.
- [ ] `codex_diag.codex_reachability_probe()` returns a structured result; raises no exceptions for network errors.
- [ ] All new tests pass: `cd ~/.hermes/hermes-agent && uv run pytest tests/agent/test_error_classifier.py tests/agent/test_codex_diag.py -v`
- [ ] No regression: `cd ~/.hermes/hermes-agent && uv run pytest tests/agent/` passes.
- [ ] `cli-config.yaml.example` carries a commented `fallback_providers` example labeled "transport/codex_challenge only".
- [ ] Troubleshooting doc exists at `website/docs/user-guide/troubleshooting/codex-transport.md` and explains: what cf-mitigated means, what request_dump path to inspect, how to opt into fallback chain, how the classifier disambiguates from auth.
- [ ] Review artifacts posted under `scripts/review/results/2026-04-26-plan-2301-{claude,codex,gemini}.md` with at least one MINOR or MAJOR-then-revised finding documented.
- [ ] Manual verification: with no fallback configured, a forced CF-challenge (mock injection at integration-test layer) produces the new operator message instead of bare `APIConnectionError` repeats.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | TBD | (filled after Step 4) |
| Codex | TBD | (filled after Step 4) |
| Gemini | TBD | (filled after Step 4) |

**Overall result:** TBD

Revisions made based on review:
- (filled after Step 4)

---

## Risks and Open Questions

- **Risk — repo boundary:** Hermes lives at `~/.hermes/hermes-agent/` (separate upstream `NousResearch/hermes-agent`). The implementation PR will be filed there, not in workspace-hub. Workspace-hub holds only the plan + review artifacts. Confirm with user that this is the intended split before opening the upstream PR.
- **Risk — header inspection coupling:** `_is_codex_cloudflare_challenge()` depends on the OpenAI SDK exposing `.response.headers` on `APIStatusError`. If a future SDK upgrade changes the attribute path, the classifier silently drops to the auth branch. Mitigation: graceful fallback already in pseudocode (`if response is None: return False`); add a unit test guarding the attribute name and an SDK-version pin warning in the docstring.
- **Risk — false positive on host gate:** if Cloudflare ever fronts another OpenAI host with `cf-mitigated: challenge`, the host-gate (`host == 'chatgpt.com'`) will mis-bucket. Acceptable: false-positive surface is narrow, and the `else` path is auth (not catastrophic). Re-evaluate if upstream changes the base URL.
- **Risk — fallback chain rotation thrash:** if the operator configures `fallback_providers` with another provider that *also* CF-challenges, the chain walks until exhausted. Mitigation: `should_rotate_credential=False` plus `retryable=False` ensures we walk the chain *once*, not loop within a provider.
- **Risk — `_codex_cloudflare_headers` already prevents most CF 403s:** for non-residential IPs that *still* CF-challenge despite the originator pin, the new branch fires correctly. For environments where the headers fix everything, this branch never trips — that's the desired no-op.
- **Open — diagnostic CLI surface:** should `hermes diag codex` be a top-level subcommand or a `/diag codex` slash-command in the TUI? The plan exposes the function; CLI registration is left to a follow-up unless reviewers push for inclusion in scope.
- **Open — interaction with `_run_codex_create_stream_fallback` (run_agent.py:5367):** the existing stream-level fallback retries on `RemoteProtocolError`/`ReadTimeout`/`ConnectError` but not on a 403. Confirm during implementation that a CF-challenge 403 from the streaming endpoint propagates as `APIStatusError` (with `.response.headers`), not as a swallowed transport error. If swallowed, add detection in the stream path too.
- **Open — version-skew of project memory:** memory file `project_hermes_installation` says Hermes v0.4.0; local install is v0.11.0. Decide whether to update the memory doc as part of this PR or in a follow-up.

---

## Complexity: T2

**T2** — taxonomy + classification + operator messaging + a small diagnostic helper + tests + docs. Touches 1 new module, 4 modified files, 2 new test files. No cross-repo refactor, no schema migration, no protocol change. Concentrated in `agent/` plus a thin `run_agent.py` callsite edit.
