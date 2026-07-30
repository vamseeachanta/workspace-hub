# Plan for #3712: Required Status Checks for Main

> **Status:** plan-review
> **Complexity:** T2
> **Date:** 2026-07-30
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3712
> **Client:** N/A
> **Lane:** lane:codex
> **Review artifacts:** scripts/review/results/2026-07-30-plan-3712-codex-r1.md; scripts/review/results/2026-07-30-plan-3712-verification-log.md

---

## Resource Intelligence Summary

### Existing repo code

- `.github/workflows/baseline-check.yml` will supply the baseline PR jobs: `Run Tests`, `Code Quality`, and `Governance Checks`.
- `.github/workflows/enforcement-gate.yml` will supply PR enforcement jobs: `Scheduler Mutation Surface Guard`, `Stage Prompt Drift Guard`, `Review Evidence Check`, `Plan Approval Check`, `Marker-Label Parity Check`, `Model-ID Sourcing Guard`, `Skill-Index Coherence`, and `Compliance Dashboard`.
- `.github/workflows/legal-rule-authority-gate.yml` and `.github/workflows/legal-rule-authority-reusable.yml` will supply `strict-scan` and `strict-scan / authority`; the reusable workflow will read `secrets.LEGAL_SCAN_AUTH_CURRENT` into `AUTH_ENVELOPE` and will fail closed when it is empty.
- `.github/workflows/legal-client-pii-gate.yml`, `.github/workflows/claude-code-review.yml`, and `.github/workflows/skills-validation.yml` will add conditional PR checks.
- `.claude/rules/scheduler-mutation-safety.md:10` will continue to describe a pre-merge scheduler check requirement, but GitHub will not enforce that requirement until the ruleset or branch protection names the check as required.

### Standards

| Standard | Status | Source |
|---|---|---|
| Workspace planning gate | applies | `.claude/skills/coordination/issue-planning-mode/SKILL.md` requires issue -> resource intel -> plan -> adversarial review -> `status:plan-review` -> user approval before implementation. |
| Scheduler mutation safety rule | applies, but rule/reality gap exists | `.claude/rules/scheduler-mutation-safety.md:10` says to run the checker and HTML report check before merging scheduler-related changes. |
| Hard-stop planning workflow | applies | `CLAUDE.md` points agents to the mandatory planning workflow and says implementation will wait for user approval. |

### LLM Wiki pages consulted

- No relevant wiki pages will apply; this issue will be repo governance/CI wiring only.

### Documents consulted

- Issue #3712 will define the scope: no CI status check currently blocks merges; `strict-scan / authority` must not become required before the authority secret gap lands; candidate required checks will be `Run Tests`, `Scheduler Mutation Surface Guard`, `Plan Approval Check`, and `Review Evidence Check`.
- `docs/plans/README.md` will define the plan-index and review workflow shape.
- `docs/plans/_template-issue-plan.md` will define required plan sections and evidence expectations.
- Drive-file search will produce no relevant actionable document hits; the only token match will be an unrelated DNV cathodic protection PDF, while all configured indexes will be unreachable or stale in this checkout.

### Gaps identified

- No GitHub ruleset status-check requirement exists on `main`.
- No classic branch protection object exists for `main`.
- No repository secret named `LEGAL_SCAN_AUTH_CURRENT` is visible through `gh api repos/vamseeachanta/workspace-hub/actions/secrets`; the reusable workflow will consume that name as `AUTH_ENVELOPE`, so every in-repo PR that runs `strict-scan / authority` will fail before audit logic executes.
- No tracked policy will accurately distinguish advisory checks from merge-blocking checks until the ruleset and/or `.claude/rules/scheduler-mutation-safety.md` will be reconciled.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-07-30T10:42:25Z via `gh issue view`):

- `#3712` is OPEN: `infra: no CI check is merge-blocking on main - every 'required gate' enforceability argument is currently false`; labels are `cat:harness`, `domain:workstations`, and `status:needs-plan`.

**File existence** (`rg --files .github/workflows` and direct reads, 2026-07-30T10:42Z):

- EXISTS: `.github/workflows/baseline-check.yml`
- EXISTS: `.github/workflows/enforcement-gate.yml`
- EXISTS: `.github/workflows/legal-rule-authority-gate.yml`
- EXISTS: `.github/workflows/legal-rule-authority-reusable.yml`
- EXISTS: `.github/workflows/legal-client-pii-gate.yml`
- EXISTS: `.github/workflows/claude-code-review.yml`
- EXISTS: `.github/workflows/claude.yml`
- EXISTS: `.github/workflows/skills-validation.yml`
- EXISTS: `.claude/rules/scheduler-mutation-safety.md`
- EXISTS: `CLAUDE.md`
- EXISTS: `docs/plans/_template-issue-plan.md`
- EXISTS: `docs/plans/README.md`

**Protection proofs**:

```bash
$ gh api repos/vamseeachanta/workspace-hub/rulesets/17369764 --jq '{id,name,target,enforcement,conditions:.conditions, rules:[.rules[] | {type:.type, parameters:.parameters}]}'
{"conditions":{"ref_name":{"exclude":[],"include":["~DEFAULT_BRANCH"]}},"enforcement":"active","id":17369764,"name":"protect-main","rules":[{"parameters":null,"type":"deletion"},{"parameters":null,"type":"non_fast_forward"}],"target":"branch"}

$ gh api repos/vamseeachanta/workspace-hub/branches/main/protection --include
HTTP/2.0 404 Not Found
{"message":"Branch not protected","documentation_url":"https://docs.github.com/rest/branches/branch-protection#get-branch-protection","status":"404"}
```

**AUTH_ENVELOPE/secret proof**:

```bash
$ gh api repos/vamseeachanta/workspace-hub/actions/secrets --jq '.secrets[] | .name' | rg 'LEGAL_SCAN_AUTH_CURRENT|AUTH_ENVELOPE|LEGAL|AUTH'
CLAUDE_CODE_OAUTH_TOKEN
LEGAL_CLIENT_MAP

$ nl -ba .github/workflows/legal-rule-authority-reusable.yml | sed -n '35,42p'
35      - name: Materialize protected envelope
36        env:
37          AUTH_ENVELOPE: ${{ secrets.LEGAL_SCAN_AUTH_CURRENT }}
38        run: |
39          set +x
40          umask 077
41          test -n "$AUTH_ENVELOPE"
42          mkdir -m 700 "$RUNNER_TEMP/authority" "$RUNNER_TEMP/report"
```

**Live PR check proof**:

```bash
$ gh pr checks 3590 --repo vamseeachanta/workspace-hub
strict-scan / authority  fail
Run Tests                pass
Scheduler Mutation Surface Guard  pass
Review Evidence Check    pass
Plan Approval Check      pass
claude-review            pass

$ gh pr checks 3583 --repo vamseeachanta/workspace-hub
strict-scan / authority  fail
Scheduler Mutation Surface Guard  fail
Client-PII Gate          fail
Run Tests                pass
Review Evidence Check    pass
Plan Approval Check      pass

$ gh pr checks 3569 --repo vamseeachanta/workspace-hub
strict-scan / authority  fail
Scheduler Mutation Surface Guard  fail
Client-PII Gate          fail
Run Tests                pass
Review Evidence Check    pass
Plan Approval Check      pass
```

**Open PR count proof**:

```bash
$ gh pr list --repo vamseeachanta/workspace-hub --state open --json number --jq '.[].number'
3590
3583
3569
3563
3546
3543
3540
3520
3471
3468
3465
3425
3411
3410
3379
3378
3363
3327
```

The issue body will mention 5 open PRs, but the live API will show 18 open PRs at plan time. The rollout path will therefore treat the blast radius as at least 18 open PRs, not 5.

**Drive-file search proof**:

```bash
$ uv run scripts/data/drive-index-search/search.py "required status checks branch protection AUTH_ENVELOPE scheduler mutation" --json --caller plan-resource-intel
coverage_gaps: ace_knowledge, dde_knowledge, og_standards_inventory, cad_readability, master_document_index unreachable
results: one unrelated /mnt/dde/Literature/Engineering/Dnv-Rp-b401-Cathodic Protection Design.pdf token match
```

**Reproduction proofs**:

- N/A - this will be governance/CI configuration planning, not a runtime bug fix. The live failure mode will be reproduced through `gh api` and `gh pr checks` proofs above.

---

## Check Inventory

| Check name | Workflow file | What it asserts | Today-status and proving command | Gate recommendation |
|---|---|---|---|---|
| `Run Tests` | `.github/workflows/baseline-check.yml:27` | `uv sync --group dev`; `uv run python -m pytest tests/test_deduplication_fix.py -v --tb=short --noconftest`; `PYTHONPATH=src uv run python -m pytest tests/ci_smoke/ -v --tb=short`. | PR #3590: pass; PR #3583: pass; PR #3569: pass via `gh pr checks <PR> --repo vamseeachanta/workspace-hub`. | Required, first. It will provide the minimal test baseline for every PR. |
| `Code Quality` | `.github/workflows/baseline-check.yml:73` | Attempts `ruff check .`, but `continue-on-error: true` and `|| echo` make this advisory. | PR #3590/#3583/#3569: pass via `gh pr checks`; workflow lines 91-100 show advisory behavior. | Do not require until the workflow becomes intentionally blocking. |
| `Governance Checks` | `.github/workflows/baseline-check.yml:102` | Runs `scripts/operations/compliance/check_governance.sh --mode warn --scope changed --base-ref origin/main`; `continue-on-error: true`. | PR #3590/#3583/#3569: pass via `gh pr checks`; workflow lines 113-120 show warn mode. | Do not require; advisory by implementation. |
| `Scheduler Mutation Surface Guard` | `.github/workflows/enforcement-gate.yml:14` | Runs scheduler registry check, cron identity inventory check, and scheduler HTML audit digest check. | PR #3590: pass; PR #3583/#3569/#3563/#3546/#3520: fail via `gh pr checks <PR>`. | Required after existing red PRs will be triaged or updated. It will make `.claude/rules/scheduler-mutation-safety.md:10` true. |
| `Stage Prompt Drift Guard` | `.github/workflows/enforcement-gate.yml:36` | Runs import smoke, stage prompt drift check with `--fail-on-issues`, and brand-token drift guard. | PR #3590/#3583/#3569: pass via `gh pr checks`. | Not in initial required set unless owners explicitly expand scope; separate policy issue can promote it later. |
| `Review Evidence Check` | `.github/workflows/enforcement-gate.yml:99` | Runs `scripts/enforcement/require-review-on-push.sh HEAD "$MERGE_BASE"` with `REVIEW_GATE_STRICT=1`. | PR #3590/#3583/#3569: pass via `gh pr checks`. | Required after `Run Tests` and scheduler guard. |
| `Plan Approval Check` | `.github/workflows/enforcement-gate.yml:146` | Runs `scripts/workflow/plan_approval_gate_check.py`, then `scripts/enforcement/require-plan-approval.sh --strict`; label-authority blocking depends on repo vars and admin prerequisites. | PR #3590/#3583/#3569: pass via `gh pr checks`; workflow lines 178-179 warn it should stay unset until required and protected-label prerequisites exist. | Required after label-authority prerequisites will be verified and after review evidence will already gate. |
| `Marker-Label Parity Check` | `.github/workflows/enforcement-gate.yml:200` | If a PR adds/modifies `.planning/plan-approved/<n>.md`, checks corresponding issue label authority. | PR #3590/#3583/#3569: pass via `gh pr checks`. | Recommended follow-on required check, not part of the initial issue candidates unless owner expands scope. |
| `Model-ID Sourcing Guard` | `.github/workflows/enforcement-gate.yml:242` | Runs model ID sourcing guard in advisory mode; comments say advisory first. | PR #3590/#3583/#3569: pass via `gh pr checks`; lines 244-247 say advisory. | Do not require now. |
| `Skill-Index Coherence` | `.github/workflows/enforcement-gate.yml:266` | Checks curated skill basenames and regenerated full index freshness. | PR #3379/#3378/#3363/#3327: fail via `gh pr checks`; PR #3590/#3583/#3569: pass. | Do not require in this rollout because legacy open PRs are red; open a separate migration once backlog is clean. |
| `Compliance Dashboard` | `.github/workflows/enforcement-gate.yml:293` | Runs compliance dashboard with `continue-on-error: true`; summarizes metrics. | PR #3590/#3583/#3569: pass via `gh pr checks`; workflow line 305 says advisory. | Do not require. |
| `Client-PII Gate` | `.github/workflows/legal-client-pii-gate.yml:25` | Scans changed files, PR metadata, and commits for private client identifiers when `LEGAL_CLIENT_MAP` exists; degrades open if the secret is absent. | PR #3583/#3569/#3425: fail; PR #3590: pass via `gh pr checks`; `gh api .../actions/secrets` lists `LEGAL_CLIENT_MAP`. | Consider future required security gate, but not in this issue's initial set because several open PRs are red and owner policy must accept strictness. |
| `strict-scan` | `.github/workflows/legal-rule-authority-gate.yml:12` | Fork PR denial path: prints owner review required and exits 1 for fork PRs; skips for same-repo PRs. | PR #3590/#3583/#3569: skipping via `gh pr checks`. | Do not require alone; requiring skipped contexts will create ambiguous behavior. |
| `strict-scan / authority` | `.github/workflows/legal-rule-authority-gate.yml:19` and `.github/workflows/legal-rule-authority-reusable.yml:10` | Same-repo authority scan; materializes `secrets.LEGAL_SCAN_AUTH_CURRENT` into `AUTH_ENVELOPE`, verifies authority, audits inert PR tree. | PR #3590/#3583/#3569/#3563/#3546/#3543/#3540: fail via `gh pr checks`; repo secrets API lists no `LEGAL_SCAN_AUTH_CURRENT`. | Do not require until the owner will provision the secret and at least one clean PR proves green. This fix must precede any required-check change. |
| `claude-review` | `.github/workflows/claude-code-review.yml:14` | Runs Anthropic Claude code-review action with `CLAUDE_CODE_OAUTH_TOKEN`; produces AI review feedback. | PR #3590/#3583/#3569: pass via `gh pr checks`; workflow lines 34-41 show review action. | Advisory by intent; do not require as a merge gate. |
| `claude` | `.github/workflows/claude.yml` | Responds to issue comments, PR review comments, issues, and PR reviews when trigger conditions match. | PR #3583/#3569/#3563/#3471/#3468: skipping via `gh pr checks` after comment/review-trigger runs. | Do not require; it is an interactive automation path, not a deterministic PR gate. |
| `Validate SKILL.md frontmatter` | `.github/workflows/skills-validation.yml:31` | Path-filtered skill validator plus regression tests for skill frontmatter and cron uv resolution. | Not present on sampled PR #3590/#3583/#3569 because path filters do not match; workflow lines 4-15 define PR path filters. | Do not include in global required set unless GitHub required-check configuration accounts for path-filtered pending/skipped behavior. |
| `GitGuardian Security Checks` | external GitGuardian app | Scans for secrets through an external integration. | PR #3590/#3583/#3569: pass via `gh pr checks`. | Leave as separately managed external security signal unless owner decides to require app contexts. |

---

## Deliverable

A future implementation will create an owner-approved, staged GitHub ruleset or branch-protection configuration that requires the selected deterministic PR checks only after the red `strict-scan / authority` secret gap and current open-PR backlog risks will be handled.

---

## Required-Set Recommendation in Dependency Order

1. **Provision and verify `LEGAL_SCAN_AUTH_CURRENT` first.** The owner will create or repair the protected secret/environment path used by `.github/workflows/legal-rule-authority-reusable.yml`, then re-run one current PR to prove `strict-scan / authority` turns green. No required-check rollout will start before this proof, because making any broad status policy while a universal red authority check exists will create a predictable merge freeze.
2. **Require `Run Tests`.** This check will be the first deterministic baseline gate. It is currently green on the sampled open PRs and will assert the CI smoke suite plus the existing hub-level test slice.
3. **Require `Scheduler Mutation Surface Guard`.** This check will make the scheduler mutation rule's pre-merge language true. Before enabling it, owners will either update/redesign open PRs that are red or will intentionally exclude/close them from the migration batch.
4. **Require `Review Evidence Check`.** This will enforce adversarial review evidence for feature/fix commits after basic tests and scheduler safety already gate.
5. **Require `Plan Approval Check`.** This will come last among the four candidate checks because it depends on the plan-approval label/marker authority path being correct. The rollout will first verify `PLAN_APPROVAL_GATE_ENABLED`, `PLAN_APPROVAL_ADMIN_PREREQS_CONFIRMED`, and `PLAN_APPROVAL_OWNERS` behavior on a test PR.
6. **Defer `strict-scan / authority` until green for at least one current PR and owner-owned secret rotation is documented.** It should become required only in a follow-on activation after the secret gap no longer exists.

Checks that will stay advisory in this plan: `claude-review`, `claude`, `Code Quality`, `Governance Checks`, `Model-ID Sourcing Guard`, and `Compliance Dashboard`. `Client-PII Gate`, `Skill-Index Coherence`, `Marker-Label Parity Check`, and `GitGuardian Security Checks` will be candidates for separate owner decisions, not bundled into the initial four-check rollout.

---

## AUTH_ENVELOPE Diagnosis and Required Ordering

The implementation will treat the authority-secret gap as the first migration item. The reusable workflow will evaluate:

```yaml
AUTH_ENVELOPE: ${{ secrets.LEGAL_SCAN_AUTH_CURRENT }}
test -n "$AUTH_ENVELOPE"
```

The repo secrets API visible to this token will list `CLAUDE_CODE_OAUTH_TOKEN` and `LEGAL_CLIENT_MAP`, but not `LEGAL_SCAN_AUTH_CURRENT`. The failure will therefore happen before authority materialization or legal audit can run. Because `strict-scan / authority` is red on every modern open PR that runs it, any required-check policy that includes this context before secret repair will block all affected merges. The plan will sequence secret repair, proof rerun, and only then ruleset changes.

---

## Rule/Reality Gap

The rule at `.claude/rules/scheduler-mutation-safety.md:10` will need one of two owner-approved outcomes:

- **Preferred:** the implementation will add `Scheduler Mutation Surface Guard` to the required status checks so the rule's pre-merge claim becomes true for PRs into `main`.
- **Fallback:** if the owner chooses not to enforce scheduler checks in GitHub, a separate owner-approved rule amendment will change the rule from enforced pre-merge language to advisory/manual language.

The implementation will not silently amend the rule. Any rule text change will be an owner-approval item because agents and reviewers use that rule as an authority source.

---

## Rollout and Migration Path

1. The owner will provision `LEGAL_SCAN_AUTH_CURRENT` for the `legal-rule-authority` environment or will deliberately disable/exclude the legal authority check from any required set until provisioned.
2. A maintainer will re-run checks on PR #3590 or another current same-repo PR and will capture `gh pr checks <PR>` showing `strict-scan / authority` green or intentionally out of scope.
3. Maintainers will inventory all open PRs immediately before enabling required checks with `gh pr list --state open --json number,title,statusCheckRollup` and will sort them into: green under proposed required set, needs rebase/rerun, needs PR fix, or close/supersede.
4. The initial required ruleset will name only stable deterministic contexts: `Run Tests`, then `Scheduler Mutation Surface Guard`, then `Review Evidence Check`, then `Plan Approval Check` after admin prerequisites are proven.
5. The rollout will use a temporary observation window: require `Run Tests` first, re-run affected PRs, then add each additional required context one at a time. Each step will record `gh pr checks` evidence before adding the next check.
6. Legacy red checks outside the required set, including `strict-scan / authority`, `Client-PII Gate`, and old `Skill-Index Coherence` failures, will remain visible but not merge-blocking until their own remediation plans land.
7. After ruleset activation, a follow-up verification comment on #3712 will include `gh api repos/vamseeachanta/workspace-hub/rulesets/<id>` output showing `required_status_checks` entries and `gh api repos/vamseeachanta/workspace-hub/branches/main/protection` output if classic protection will be used instead.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/plans/2026-07-30-issue-3712-required-status-checks.md` | Plan artifact for required status check rollout. |
| Update | `docs/plans/README.md` | Plan index row. |
| Create | `scripts/review/results/2026-07-30-plan-3712-codex-r1.md` | Adversarial self-review artifact. |
| Create | `scripts/review/results/2026-07-30-plan-3712-verification-log.md` | Verification command log committed with the plan. |

Future implementation, after user approval, will be external-state only unless the owner chooses a policy-doc amendment. It will not change workflows, branch protection, rulesets, or secrets during this planning issue.

---

## TDD Test List

| Test name / proof row | What it will verify | Today-status and proving command | Acceptance target |
|---|---|---|---|
| `ruleset_has_required_status_checks_after_rollout` | The active default-branch ruleset will include required status checks in the selected dependency order. | Today: no required checks. Prove with `gh api repos/vamseeachanta/workspace-hub/rulesets/17369764 --jq '.rules'`, which returns only `deletion` and `non_fast_forward`. | After implementation, the same command or the new ruleset ID will show required status-check rules for selected contexts. |
| `branch_protection_gap_not_used_as_false_green` | Classic branch protection will not be assumed when it is absent. | Today: `gh api repos/vamseeachanta/workspace-hub/branches/main/protection --include` returns HTTP 404. | After implementation, either ruleset evidence will be authoritative or classic protection will return the configured required checks. |
| `authority_secret_precondition_green_before_requirement` | `strict-scan / authority` will not become required while `LEGAL_SCAN_AUTH_CURRENT` is absent or empty. | Today: `gh api repos/vamseeachanta/workspace-hub/actions/secrets --jq '.secrets[] | .name' | rg 'LEGAL_SCAN_AUTH_CURRENT|AUTH_ENVELOPE|LEGAL|AUTH'` returns no `LEGAL_SCAN_AUTH_CURRENT`; `gh pr checks 3590` shows `strict-scan / authority fail`. | Before any required-check change, a rerun will show `strict-scan / authority` green or explicitly excluded. |
| `run_tests_required_candidate_is_green` | `Run Tests` can safely become the first required check. | Today: `gh pr checks 3590`, `gh pr checks 3583`, and `gh pr checks 3569` show `Run Tests pass`. | No new failure relative to current PR checks; if stale PRs are updated, their `Run Tests` will pass before merge. |
| `scheduler_guard_requirement_matches_rule` | The scheduler mutation rule's pre-merge claim will be enforced by GitHub. | Today: `.claude/rules/scheduler-mutation-safety.md:10` says to run the guard before merging, while `gh api rulesets/17369764` has no required status checks. `gh pr checks 3583` and `3569` show the guard can be red. | `Scheduler Mutation Surface Guard` will become required only after current red PRs are handled or intentionally excluded. |
| `review_evidence_required_candidate_is_green` | Adversarial review evidence will gate implementation commits. | Today: `gh pr checks 3590`, `3583`, and `3569` show `Review Evidence Check pass`. | Required ruleset includes `Review Evidence Check`; no new failures beyond existing gate behavior. |
| `plan_approval_required_candidate_is_green_after_admin_prereqs` | Plan approval checks will not be required before label/owner prerequisite vars are verified. | Today: `gh pr checks 3590`, `3583`, and `3569` show `Plan Approval Check pass`; `.github/workflows/enforcement-gate.yml:178-179` says `PLAN_APPROVAL_GATE_ENABLED=1` should remain unset until the check is required and protected-label ruleset is live. | Required ruleset includes `Plan Approval Check` only after admin prerequisites are documented. |
| `ace1_baseline_no_new_failures` | The rollout will not claim all local baseline suites are green. | Today-status from issue instruction: ace1 baseline is not green; `tests/enforcement` has 2 failed/417 passed and `tests/cron` has 284 passed/0 failed. Proving commands for implementation will be `uv run pytest tests/enforcement` and `uv run pytest tests/cron`. | Acceptance will be no new failures relative to that baseline, not universal green. |

---

## Acceptance Criteria

- [ ] `LEGAL_SCAN_AUTH_CURRENT` / `AUTH_ENVELOPE` will be fixed or `strict-scan / authority` will be explicitly excluded before any required-check rollout begins.
- [ ] A live PR will show `strict-scan / authority` green, or the plan will carry an owner-approved exclusion before status checks become required.
- [ ] Ruleset or branch-protection evidence will show `Run Tests` required first.
- [ ] Ruleset or branch-protection evidence will show `Scheduler Mutation Surface Guard` required only after red open PRs are triaged.
- [ ] Ruleset or branch-protection evidence will show `Review Evidence Check` required after scheduler guard.
- [ ] Ruleset or branch-protection evidence will show `Plan Approval Check` required after plan-approval admin prerequisites are verified.
- [ ] Advisory checks will remain advisory unless a separate owner decision promotes them.
- [ ] `.claude/rules/scheduler-mutation-safety.md:10` will either become true through required status checks or will be amended under explicit owner approval.
- [ ] Baseline verification will use no-new-failures semantics for ace1: `tests/enforcement` starts with 2 failed/417 passed; `tests/cron` starts with 284 passed/0 failed.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Codex self-review | MINOR | Independent review is still required; the plan will rely on live GitHub external state that can change before implementation, so implementation must refresh every `gh api` and `gh pr checks` proof immediately before changing rulesets. |

**Overall result:** PASS FOR PLAN-REVIEW ONLY - implementation will remain blocked pending independent review and user approval.

Revisions made based on review:
- The migration path will require fresh pre-activation PR inventory because live open PR count already differs from the issue-body count.
- The authority secret repair will be first in the dependency order and will block any required-check change until proven.

---

## Risks and Open Questions

- **Risk:** Open PR state will change before implementation; every migration row will need fresh `gh pr checks` evidence at implementation time.
- **Risk:** Required-check names can be duplicated by repeated workflow runs or matrix behavior; implementation will need exact GitHub context names from live checks, not guessed YAML job IDs.
- **Risk:** Requiring path-filtered checks globally can leave required contexts pending or absent; `Validate SKILL.md frontmatter` will stay out of scope unless GitHub skip behavior is explicitly tested.
- **Risk:** `Plan Approval Check` has two layers: local marker/script logic and label-authority logic governed by vars. Implementation will need admin-prereq evidence before requiring it.
- **Open:** Whether owners will want `Client-PII Gate`, `Skill-Index Coherence`, or `strict-scan / authority` promoted in a separate second wave once their current red/backlog state is resolved.
- **Unverified:** Actual contents/validity of any future `LEGAL_SCAN_AUTH_CURRENT` secret cannot be read; only presence and green check behavior can prove it.

---

## Complexity: T2

This will be T2 because implementation will mutate GitHub repository protection/ruleset external state in a dependency-sensitive rollout, but it will not require repo code changes unless the owner chooses the fallback rule amendment.
