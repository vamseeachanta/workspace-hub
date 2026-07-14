# Plan for #3525: Investigate safe remote Claude job dispatch to ACMA-WS014

> **Status:** plan-approved
> **Complexity:** T2
> **Date:** 2026-07-14
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3525
> **Client:** N/A
> **Lane:** lane:claude
> **Execution mode:** parallel-readonly
> **Review artifacts:** `scripts/review/results/2026-07-14-plan-3525-claude.md` | `scripts/review/results/2026-07-14-plan-3525-codex.md` | `scripts/review/results/2026-07-14-plan-3525-gemini.md` | `scripts/review/results/2026-07-14-plan-3525-disagreement.md` | `scripts/review/results/2026-07-14-plan-3525-codex-inline-final.md`

---

## Resource Intelligence Summary

### Existing repo code and operating contracts

- `config/workstations/registry.yaml` identifies `ACMA-WS014` as the `ace-win-2` alias, records Windows, `ssh: null`, Claude/Codex/Gemini availability, and `telegram_hermes.dispatch_enabled: false`. The discovery will treat that registry state as local policy evidence, not as proof of an Anthropic product capability.
- `docs/ops/telegram-hermes-multimachine-control-plane.md` keeps Windows hosts desktop/status-only and requires a separately approved dispatch plan before unattended work. The discovery will preserve that fail-closed posture.
- `docs/ops/windows-macos-dispatch-parity.md` documents a coordinator-routed, outbound pull-worker architecture with leases and no inbound per-host bot. The discovery will use it as the smallest existing workspace fallback precedent, while independently testing whether an official Anthropic feature supersedes it.
- `config/scheduled-tasks/schedule-tasks.yaml` and `.claude/rules/scheduler-mutation-safety.md` establish that scheduler registry evidence does not authorize live Windows Task Scheduler mutation. The discovery will inspect documentation and source only; it will not enumerate or change live scheduled tasks.
- `docs/plans/2026-06-18-issue-3207-agy-headless-dispatch.md` records a prior headless-dispatch design and its risks around unattended permission bypass, argv limits, live quota use, and isolated working directories. The discovery will treat these as threat-model inputs, not as a reusable Claude solution.
- `docs/plans/2026-05-20-issue-2756-licensed-win-1-solver-status-lane-baseline.md` records the prior decision to keep a licensed Windows host manual/status-only until Windows dispatch parity is proven. The discovery will test whether current supported Anthropic capabilities change that conclusion for ACMA-WS014.

### Standards

| Standard or policy | Status | Source |
|---|---|---|
| Issue planning and explicit user approval | active | `.claude/skills/coordination/issue-planning-mode/SKILL.md` |
| Scheduler mutation safety | active; discovery must remain non-mutating | `.claude/rules/scheduler-mutation-safety.md` |
| Secrets via environment/local secret stores only | active | `docs/ops/telegram-hermes-multimachine-control-plane.md` |
| Legal/client-identifier scan | required before commit | `scripts/legal/legal-sanity-scan.sh` |

Engineering standards and calc citations will not apply because this issue will produce a product/security discovery report, not an engineering calculation.

### LLM Wiki pages consulted

No wiki content will be changed or used as authority. Official Anthropic sources and current local read-only observations will remain the authority for product claims.

### Documents consulted

- [Issue #3525](https://github.com/vamseeachanta/workspace-hub/issues/3525) defines the discovery-only scope, prohibited actions, evidence split, requested options, and go/no-go decision.
- `docs/ops/telegram-hermes-multimachine-control-plane.md` supplies the current fail-closed Windows dispatch posture and canonical lease/log model.
- `docs/ops/windows-macos-dispatch-parity.md` supplies the existing pull-worker fallback precedent for no-SSH hosts.
- `config/workstations/registry.yaml` supplies the canonical machine alias and current dispatch-disabled state.
- `docs/plans/2026-06-18-issue-3207-agy-headless-dispatch.md` supplies prior headless-agent risk controls.
- [Claude Code Remote Control](https://code.claude.com/docs/en/remote-control) documents the official local-machine remote-control, Trusted Devices, browser/mobile, local-resource, awake-process, and same-account/organization surfaces that the approved discovery will verify against the installed version and account boundary.
- [Claude Code Desktop](https://code.claude.com/docs/en/desktop), [Desktop scheduled tasks](https://code.claude.com/docs/en/desktop-scheduled-tasks), [Cowork Dispatch](https://support.claude.com/en/articles/13947068-assign-tasks-from-anywhere-in-claude-cowork), and [Channels](https://code.claude.com/docs/en/channels) identify official Windows, scheduling, phone dispatch, and webhook/channel surfaces that will be assessed independently rather than collapsed into one capability claim.
- [Claude Code authentication](https://code.claude.com/docs/en/authentication), [Claude Platform authentication](https://platform.claude.com/docs/en/manage-claude/authentication), and [Claude Platform workspaces](https://platform.claude.com/docs/en/manage-claude/workspaces) distinguish interactive product auth from API/WIF/service-account and spend-control concepts; the approved discovery will not treat API service accounts as Remote Control credentials without explicit support.
- [Anthropic Consumer Terms](https://www.anthropic.com/legal/consumer-terms) and [Commercial Terms](https://www.anthropic.com/legal/commercial-terms) will anchor the account-sharing analysis for the applicable account class.
- Drive-file index: `uv run python scripts/data/drive-index-search/search.py "Claude remote worker dispatch" --json --limit 20 --caller plan-resource-intel` returned no relevant files. Only one literature catalog was effectively reachable; five other indexes were unreachable, and three of those were also marked stale. No raw drive paths or client-identifying metadata will be persisted.

### Gaps identified

- Official Anthropic documentation now describes Remote Control/Trusted Devices, Desktop scheduled tasks, Dispatch, and Channels, but no reviewed repo artifact currently establishes whether those features satisfy the full request or permit cross-individual-account delegation.
- No current official-source matrix in the repo distinguishes Claude Desktop, Claude Code, Claude web, Team, Enterprise, and API automation for this use case.
- No current report separates verified facts, local observations, assumptions, and unsupported inferences for ACMA-WS014.
- No evidence-backed decision currently ranks an official Anthropic feature against the existing pull-worker fallback.
- No bounded implementation/operations estimate currently covers OS isolation, queue authentication, concurrency, spend controls, logs, and wake handling.

### Evidence (embedded verification)

**Issue status** (verified 2026-07-14 via `gh issue view 3525`):

```text
#3525 — OPEN — [WRK] Investigate safe remote Claude job dispatch to ACMA-WS014
labels: cat:ai-orchestration, lane:claude, priority:medium, status:needs-plan, wrk-item
```

**Machine registry facts** (curated from `sed -n '256,288p' config/workstations/registry.yaml`, verified 2026-07-14; dotted names preserve YAML nesting):

```text
hostname_aliases: [licensed-win-2, acma-ws014]
os: windows
ssh: null
capabilities.agent_clis: [claude, codex, gemini]
telegram_hermes.dispatch_enabled: false
telegram_hermes.telegram_mode: desktop-status-only
```

**Related issue state** (verified 2026-07-14 via `gh issue view 3511`):

```text
#3511 — OPEN — Windows sentinel emits empty unknown fingerprint and corrupts mktree filenames
status:plan-approved, lane:claude
```

This related issue will warn the discovery against assuming that a CLI listed in the registry is unattended-ready on Windows; it will not expand #3525 into fixing #3511.

**Gap proof** (pre-draft check on 2026-07-14): `rg -n "trusted-machine|cloud-to-local|remote Claude" docs/plans scripts/review/results -g '!README.md' -g '!2026-07-14-issue-3525-*' -g '!2026-07-14-plan-3525-*'` returned no output. The exclusions make the proof reproducible after this plan and its review artifacts exist.

**Drive-index proof** (verified 2026-07-14):

```text
query: Claude remote worker dispatch
results: 0 relevant files
coverage: partial — 5 indexes unreachable; 3 of those also marked stale
```

The zero-hit result will not be interpreted as proof that no past work exists because index coverage was partial.

**Reproduction proofs:** N/A — this is a discovery-only research issue and alleges no runtime failure. Local probes will be limited to non-sensitive version/help/capability observations after plan approval.

**Distinct sources consulted:** 6 repo/issue sources, 10 official Anthropic source pages/groups, and the mandatory drive-index query.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-14-issue-3525-claude-remote-worker-discovery.md` |
| Report contract tests | `tests/docs/test_issue_3525_claude_remote_worker_report.py` |
| Human-facing discovery report | `docs/reports/2026-07-14-issue-3525-claude-remote-worker-discovery.html` |
| Plan review — Claude | `scripts/review/results/2026-07-14-plan-3525-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-07-14-plan-3525-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-07-14-plan-3525-gemini.md` |
| Plan review — disagreement history | `scripts/review/results/2026-07-14-plan-3525-disagreement.md` |
| Plan review — final inline remediation verification | `scripts/review/results/2026-07-14-plan-3525-codex-inline-final.md` |
| Plan index | `docs/plans/README.md` |

---

## Deliverable

A self-contained HTML discovery report will state whether an existing supported Anthropic feature meets the requested workflow, document official evidence and local observations without exposing credentials, rank safe options, recommend one path, give a go/no-go decision, and estimate implementation plus operational burden.

---

## Pseudocode

```text
define evidence classes = verified_official, local_observation, assumption, unresolved
define product surfaces = Claude Desktop, Claude Code, Claude web, Team, Enterprise, API
define requested capabilities = registration, remote trigger, scheduling, unattended run,
                                cross-account delegation, local resource use

write report-contract tests first and confirm they fail because the report is absent
load the registry canonical hostname and aliases for ace-win-2
case-fold the observed hostname and accept it only if it matches the canonical name or an alias
if host attestation fails, record the blocked lane and stop local commands
collect non-sensitive local version/help/process metadata using a predeclared read-only command allowlist
never open auth files, print environment secrets, sign in, pair, install, or mutate configuration
collect current official Anthropic sources and record URL, title, access date, supported claim
reject marketing/search snippets as authority; mark undocumented behavior unresolved
assess Remote Control, Trusted Devices, scheduled tasks, Dispatch, and Channels separately
using documentation and passive installed-version/help evidence only; never exercise those features
build capability-by-product and account-boundary matrices
assess credential-sharing and local-repository threat boundaries
rank official feature, small isolated runner, and defer options using safety/fit/burden criteria
estimate build size and recurring operations with assumptions and confidence
render the HTML report with facts, observations, assumptions, risks, recommendation, and go/no-go
run report tests, link checks, legal scan, and adversarial artifact review
```

### Machine-checkable HTML contract

The RED tests will pin the report structure before the report is written:

- Required section IDs: `current-state`, `evidence`, `gaps-risks`, `ranked-options`, `decision`, `implementation-burden`, and `local-observations`.
- Every evidence row will carry exactly one `data-evidence-class` value from `verified_official`, `local_observation`, `assumption`, or `unresolved`.
- Every `verified_official` row will contain an `<a data-source-role="official">` URL and a `<time datetime="YYYY-MM-DD">` access date.
- Official-source links will be limited to HTTPS URLs on `code.claude.com`, `support.claude.com`, `platform.claude.com`, `docs.anthropic.com`, `anthropic.com`, `www.anthropic.com`, `claude.ai`, `claude.com`, or `www.claude.com`.
- Each option row will carry `data-rank`, `data-size`, `data-ops-burden`, and `data-confidence` attributes.
- The decision block will carry one `data-decision` value from `use-existing-feature`, `build-small-runner`, or `defer`.
- The local-observation section will carry `data-lane-status="completed|blocked"`. A completed lane will record the observed hostname, observation timestamp, allowlisted command names, and the registry-canonical `ace-win-2` versus physical-host alias distinction. A blocked lane will record only the observed hostname and blocker reason. Host matching will be case-insensitive against the registry canonical hostname plus all aliases.
- Prohibited credential-sharing practices will use the exact `data-rejected-practice` values `password-sharing`, `session-cookie-sharing`, `raw-oauth-sharing`, and `personal-api-key-sharing`.
- Required fallback safeguards will use the exact `data-control` values `dedicated-os-account`, `isolated-auth-config`, `least-privilege`, `authenticated-pull-queue`, `repo-action-allowlist`, `audit-log`, `concurrency-lock`, `spend-rate-limit`, `failure-quarantine`, and `wake-handling`.

“Official-link validation” will have two distinct mechanisms. The approved discovery will fetch each cited official page read-only and record the retrieval date and success/failure in the evidence table. Offline pytest will validate URL syntax, the exact domain allowlist, direct per-claim linkage, and access-date markup; pytest will not make live HTTP requests.

### Local read-only command allowlist

Only these command families will be permitted for the local-observation lane after approval:

- `hostname` — host binding only.
- `claude --version` and `claude --help` — CLI version and documented command/flag names; output will be reduced to the version and relevant help headings before persistence.
- `Get-Process -Name Claude -ErrorAction SilentlyContinue | Select-Object ProcessName,ProductVersion` — Desktop process presence/version only, if running.
- The following exact read-only registry query; no other registry fields or application rows will be persisted:

```powershell
$uninstall_keys = @(
  'Registry::HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Uninstall\*',
  'Registry::HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Uninstall\*',
  'Registry::HKEY_LOCAL_MACHINE\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*'
)
Get-ItemProperty -Path $uninstall_keys -ErrorAction SilentlyContinue |
  Where-Object { $_.DisplayName -match '^Claude($|\s)' -or $_.Publisher -eq 'Anthropic PBC' } |
  Select-Object DisplayName, DisplayVersion, Publisher
```

The lane will not run `claude auth`, `/login`, `setup-token`, `remote-control`, `/schedule`, Channels/plugin commands, Dispatch, diagnostic dumps, environment enumeration, credential-manager commands, or filesystem searches under user profile/config/auth directories.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `tests/docs/test_issue_3525_claude_remote_worker_report.py` | TDD contract for required sections, evidence labeling, official-link policy, and forbidden credential content |
| Create | `docs/reports/2026-07-14-issue-3525-claude-remote-worker-discovery.html` | Human-facing discovery deliverable |
| Update | `docs/plans/README.md` | Index this plan and track its gate status |
| Create/update | `scripts/review/results/2026-07-14-plan-3525-*.md` | Preserve adversarial plan-review evidence |

No scheduler, account, authentication, registry, firewall, OS-user, repository credential, or installed-product file will change during this issue.

---

## TDD Test List

| Test name | What it will verify | Expected result |
|---|---|---|
| `test_report_has_required_decision_sections` | All six requested outputs and local-observation appendix will exist | Required headings and one explicit recommendation/go-no-go block will be present |
| `test_report_separates_evidence_classes` | Facts, local observations, assumptions, and unresolved items will not be conflated | Four labeled evidence classes will be present |
| `test_product_matrix_covers_all_surfaces` | Desktop, Code, web, Team, Enterprise, and API will be compared | Each surface will appear in the capability matrix |
| `test_account_boundary_matrix_is_explicit` | Separate-account, same-account, Team, Enterprise, and API cases will be distinguished | All account contexts will have supported/unsupported/unverified status |
| `test_html_contract_is_machine_checkable` | Semantic assertions will target stable markup rather than free-form prose | Required IDs, evidence attributes, option attributes, and decision enum will be present |
| `test_verified_claims_use_official_anthropic_links` | Product/security/terms claims will cite primary sources | Every `verified_official` row will contain a direct HTTPS link on the pinned Anthropic-domain allowlist and an access-date `<time>` element |
| `test_report_rejects_credential_sharing` | Unsafe auth shortcuts will not be recommended | The pinned `data-rejected-practice` set will cover password, session-cookie, raw-OAuth, and personal-key sharing |
| `test_fallback_controls_are_complete` | The fallback will cover the full safety envelope | The pinned `data-control` set will cover isolation, least privilege, authenticated queue, allowlists, logs, concurrency, spend, failure quarantine, and wake handling |
| `test_report_contains_no_secret_material` | Report will contain no token/key/cookie values or local auth paths | Secret-pattern and forbidden-path scan will pass |
| `test_local_observations_are_host_bound_and_scrubbed` | Observations will be host-bound or explicitly blocked without raw diagnostics | `data-lane-status` will be valid; completed status will require `ACMA-WS014`, alias/canonical-host note, allowlisted command names, and scrubbed summaries |
| `test_report_contains_no_client_identifier_markers` | Public artifact will remain de-identified by construction | Proper nouns will be limited to the issue-approved machine alias and official vendor/product names; no person, colleague, client, project, or repository names will appear |
| `test_options_include_size_and_burden` | Each viable option will include bounded implementation and operations estimates | Size, assumptions, confidence, and recurring burden will be present |

The RED checkpoint will be the focused test failing because the report does not yet exist. The GREEN checkpoint will be the same test passing after the report is written.

---

## Acceptance Criteria

- [ ] The approved run will case-fold the observed hostname and compare it with the registry canonical hostname plus aliases for `ace-win-2`; a non-match will produce a `data-lane-status="blocked"` appendix row and will not run any further local command.
- [ ] Read-only local observations will capture only product names, versions, documented help/capability output, and non-sensitive process/install presence through a predeclared command allowlist.
- [ ] No auth file, credential store, environment secret, session cookie, OAuth token, personal API key, account membership, or billing data will be read or displayed.
- [ ] Every verified product, security, and terms claim will have a direct official Anthropic source and 2026-07-14-or-later access date; unsupported claims will be labeled unresolved.
- [ ] The report will answer all six issue questions and distinguish separate individual accounts, same account, Team, Enterprise, and API automation.
- [ ] The report will assess whether an official supported feature solves trusted-machine registration, remote trigger, scheduling, unattended execution, and local-resource use as one coherent workflow.
- [ ] Account/password/session-cookie/raw-OAuth/personal-key sharing will be rejected explicitly.
- [ ] Ranked options will include one recommendation and one explicit decision: use an existing feature, build a small runner, or defer.
- [ ] Any runner option will specify a dedicated OS account, isolated auth/config, authenticated pull queue, repo/action allowlists, logs, concurrency lock, spend/rate limit, failure quarantine, and wake/sleep handling.
- [ ] Each viable option will include implementation size, assumptions, confidence, and ongoing operational burden.
- [ ] Each cited official page will be fetched read-only during research and will record retrieval status/date; offline tests will validate the pinned domain/markup contract without network access.
- [ ] The report will contain only official vendor/product names, neutral account terminology, and the issue-approved machine alias; it will contain no person, colleague, client, project, or repository names.
- [ ] The report and its focused test will be staged explicitly before `scripts/legal/legal-sanity-scan.sh --diff-only` runs in the isolated issue worktree, so the scanner cannot omit the newly created report.
- [ ] Code/artifact adversarial review will explicitly attest that the staged report contains no client identifiers. The private-map scanner will not be claimed because neither its default map nor `LEGAL_CLIENT_MAP` is present on this host, and discovery scope forbids provisioning configuration.
- [ ] No install, update, login, pairing, scheduler/config mutation, webhook setup, test dispatch, or paid request will occur.
- [ ] Any recommended implementation will be filed as a separate issue and will require its own plan, adversarial review, explicit user approval, and TDD.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MINOR (r3) | No blockers; requested review-artifact persistence and case-insensitive hostname semantics. |
| Codex CLI | MAJOR (r3, sustained minority) | Flagged canonical-or-alias matching and the absent private PII map; both were patched inline without a fourth review cycle. |
| Codex main session | MINOR (final inline verification) | Verified both r3 blockers are resolved and review evidence is force-added; no remaining blocker. |
| Gemini | UNAVAILABLE | Non-interactive Gemini authentication is not configured on this machine; T3 review degraded to T2 with Claude + Codex. |

**Overall result:** PASS with disclosed consensus split — Claude remained MINOR while Codex CLI returned MAJOR for three rounds. The two final r3 findings were concrete and were patched inline; the main Codex session verified the patched text and did not dispatch a prohibited fourth automatic cycle.

Revisions made through r2:

- Replaced feature “testing” with documentation-only assessment and prohibited exercising Remote Control, Dispatch, Channels, schedules, pairing, or login.
- Made the gap proof reproducible after plan/review artifacts exist.
- Added physical-host attestation, completed/blocked local-lane semantics, an exact command allowlist, and registry-alias reporting.
- Pinned semantic HTML attributes for evidence, options, decision, rejected credential practices, and fallback controls.
- Separated read-only live source retrieval from offline link-contract tests.
- Required strict artifact-scoped client-PII checking and explicit staging before the diff-based legal scan.
- Replaced exact physical-host matching with case-insensitive registry canonical-or-alias resolution.
- Recorded that the private PII map is absent and replaced the non-executable strict scan claim with source minimization, staged legal scanning, and an explicit artifact-review attestation; no configuration will be provisioned.
- Preserved the provider, disagreement, and final inline-remediation artifacts with force-add because `scripts/review/results/` is ignored by default.

---

## Risks and Open Questions

- **Risk — discovery becomes configuration:** even harmless-looking UI navigation can trigger sign-in, pairing, updates, or settings writes. The approved run will use only the exact command allowlist above and will perform no UI navigation.
- **Risk — wrong execution host:** registry evidence is not proof that observations ran on ACMA-WS014. The local lane will fail closed unless the hostname attestation matches, and the report appendix will record that attestation.
- **Risk — auth leakage:** CLI diagnostics can reveal account identifiers or paths. Commands and captured excerpts will be allowlisted; raw output will be summarized and scrubbed before entering the public report.
- **Risk — private PII map unavailable:** the strict private-map scanner cannot run on this host without provisioning configuration, which is outside discovery scope. The report will minimize inputs to official public sources plus allowlisted local fields, will pass the staged legal scan, and will receive an explicit no-client-identifier artifact review before completion.
- **Risk — absence-of-documentation inference:** failure to find an official feature will not prove that it does not exist. The report will say “not documented in sources checked” and list the exact source coverage.
- **Risk — product drift:** Anthropic features and terms can change. Every official source will carry an access date and the conclusion will be time-bounded.
- **Risk — feature-name conflation:** Remote Control, Trusted Devices, Dispatch, Channels, cloud web, and Desktop scheduled tasks have different execution and identity boundaries. The report will evaluate them as separate rows before considering a combined workflow.
- **Risk — service-account category error:** Claude Platform WIF/API service accounts and a Team/Enterprise owner identity will not be treated as non-human Remote Control credentials unless an official source explicitly connects those surfaces.
- **Risk — account ambiguity:** the colleague's exact subscription/workspace type is unknown. The report will compare account classes without inspecting either person's account and will state which conclusion depends on Team/Enterprise confirmation.
- **Risk — local policy conflict:** an Anthropic capability may exist while workspace policy still keeps ACMA-WS014 non-dispatchable. The recommendation will require both vendor support and local safety gates.
- **Risk — overbuilding fallback:** the workspace already has a no-SSH pull-worker precedent. The report will prefer that smallest reviewed substrate over a new inbound daemon if no official feature fits.
- **Open — commercial confirmation:** if public official docs do not resolve Team/Enterprise delegation or service-account behavior, the report will identify an Anthropic sales/support confirmation as a blocker rather than infer support.

## Explicit Non-Goals

- The issue will not register, pair, enroll, authenticate, or remotely control ACMA-WS014.
- The issue will not inspect or copy authentication material.
- The issue will not create an OS account, scheduled task, service, queue, webhook, tunnel, firewall rule, wake timer, or spending control.
- The issue will not test-dispatch a job or consume paid model/API usage.
- The issue will not implement the recommended architecture.

## Complexity: T2

**T2** — the work will be read-only but will span local Windows observations, multiple Anthropic product/account surfaces, security and terms evidence, a tested HTML artifact, and multi-provider adversarial review.
