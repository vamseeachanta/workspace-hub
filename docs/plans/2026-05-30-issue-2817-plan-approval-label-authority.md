# Plan for #2817 (re-scoped): plan-approval gate trusts label-actor authority; retire the forgeable local marker

> **Status:** plan-review (NOT approved — awaiting USER; T3 ⇒ Claude + Codex + Gemini)
> **Complexity:** T3 (systemic security gate)
> **Date:** 2026-05-30
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2817
> **Client:** N/A
> **Design decisions (user-confirmed 2026-05-30):** REUSE the in-production #2798 helper (generalize `_verified_label_event`/`evaluate_close` into a shared `label_authority.py` used by both gates); RETARGET the existing `enforcement-gate.yml` `plan-approval` job (no new workflow); retire the marker fully (local hooks advisory); fail-closed; staged `PLAN_APPROVAL_GATE_ENABLED` rollout flag.
> **Review artifacts (to be produced):** scripts/review/results/2026-05-30-plan-2817v3-{claude,codex,gemini}.md
> **Supersedes:** the v1 atomic-approve-helper plan (branch feat/2817-approve-helper); refines the v2 label-authority plan (branch feat/2817-label-authority).

---

## Resource Intelligence Summary

> **CORRECTION to prior planning:** the v2 plan (and a fresh-context draft of this plan) assumed the #2798 completeness-gate helper is "unimplemented / vaporware, build from scratch." **That is false** — verified on `origin/main` (and used in production this session to close #2851/#2814/#2801). The label-actor-authority machinery EXISTS and is the reusable foundation; this plan *generalizes* it rather than rebuilding it. This materially de-risks the work.

### The reusable #2798 machinery (verified present on `origin/main`)
- **`scripts/workflow/completeness_gate_runner.py`** — contains `_verified_label_event(repo, issue)`: fetches the GH issue **timeline**, returns `(actor, applied_at)` for the most recent application of a label. Also `_gh_json()`, `_parse_iso()`, `body_is_fresh()` wiring. **This is exactly the label-actor-timeline primitive #2817 needs** — generalize it (parameterize the label name) into a shared helper.
- **`scripts/workflow/completeness_gate_check.py`** — `evaluate_close(...)`: pure decision function. Threshold-from-config-not-record; **owner-actor check**; `body_verified_fresh` (label must post-date the body/artifact, anti-forgery); unknown-class fail-closed. The #2817 gate mirrors this decision shape (replace "pct≥threshold" with "linked-issue label present + actor authorized + fresh").
- **`.github/workflows/completeness-gate.yml`** — the server-side Action pattern (fires on the relevant event, reopens/blocks on violation, reads owners from a repo var). The #2817 gate mirrors this structure on `pull_request`.
- **`scripts/enforcement/check-completeness-before-close.sh`** — the local advisory pre-flight pattern (reads `$<OWNERS>` from env, fast feedback, fail message). The #2817 local advisory mirrors this.
- **`tests/workflow/test_completeness_gate_check.py`** — test patterns to mirror.

### The forgeable surfaces to retire (verified present)
- **`.claude/hooks/plan-approval-gate.sh` + `.codex/hooks/plan-approval-gate.sh`** — local PreToolUse gates. `has_approval()` is **directory-level**: accepts ANY non-self-approved `.md` under `.planning/plan-approved/`, NOT the per-issue marker. `is_self_approved()` only catches markers <120s old AND uncommitted (or containing "Worker session/auto-approved"). **A committed marker is always trusted → the bypass.** (Confirmed live this session: implementing #2814 passed the gate via unrelated committed markers.)
- **`scripts/enforcement/require-plan-approval.sh`** — pre-commit gate; default `STRICT_ISSUE_MODE=0` accepts "any marker newer than STATE.md" OR a commit-message regex OR a session-log grep. No actor check, no age check.
- **`scripts/enforcement/check-marker-label-parity.sh`** — reverse gate (requires a non-bot label when a marker is added); already fails-closed on missing/unauthed `gh`.
- **`.github/workflows/enforcement-gate.yml`** — ALREADY has a `plan-approval` job (line 117, `require-plan-approval.sh --strict`) and a `marker-label-parity` job (line 148). **This is the CI surface to retarget** — no brand-new workflow file needed.

### Documents consulted
- Issue #2817 body + 5 comments — the re-scope decision and the **5 Codex MAJORs** (in the 2026-05-28T16:17Z comment; note: the cited `2817-codex.md` review artifact does NOT exist as a file — the comment is the agenda of record, and producing the missing artifact is part of this plan's T3 review).
- v2 plan `docs/plans/2026-05-28-issue-2817-plan-approval-label-authority.md` (branch feat/2817-label-authority) + its Claude r1 (A1 linkage / A2 solo-toggle / A3 advisory framing, already folded).
- `docs/plans/_template-issue-plan.md`.
<!-- sources: #2817 body+comments, v2 plan, v2-claude review, completeness_gate_runner.py, completeness_gate_check.py, completeness-gate.yml, plan-approval-gate.sh (both), require-plan-approval.sh, enforcement-gate.yml = 10 ≥ 3 -->

### Reproduction (Step 1.5)
The bypass is demonstrable: this session implemented #2814 with NO per-issue `2814.md` marker — the directory-level `has_approval()` passed because unrelated committed markers exist. An agent that commits any marker (or finds one) gains local "approval." The security claim "only an approved plan is implemented" is therefore unenforced locally; merge authority is what must be hardened.

---

## Deliverable
Approval authority moves from the **forgeable local marker** to the **human-attributed `status:plan-approved` label actor**, verified **server-side at the PR→main merge gate** by a shared `label_authority` helper generalized from #2798's proven `_verified_label_event`. Local hooks/scripts become **advisory** (UX/discipline, never the security authority); the marker is retired. Closes the self-approval bypass (an agent-created marker grants no merge authority) and eliminates the dropped-marker papercut by design.

---

## Design

### Shared helper (generalize, don't rebuild)
Extract #2798's label-timeline + freshness + owner-actor logic into `scripts/workflow/label_authority.py`:
```
verified_label_event(repo, issue, label)         # generalized from _verified_label_event (param the label)
  -> (actor, applied_at) | (None, None)
is_authorized_human(actor, owners, *, allow_bots=False)   # actor in owners AND not *[bot]/App/PAT machine user
label_is_fresh(applied_at, *not_before_times)    # applied_at >= max(plan_revision_time, pr_head_time)
```
`completeness_gate_{runner,check}.py` are refactored to import this helper (no behavior change — covered by the existing `tests/workflow/test_completeness_gate_check.py`), proving the generalization is non-regressive. `#2798` and `#2817` then share one audited authority primitive.

### Server gate (the security authority) — retarget the existing job
On `pull_request` to `main` `[opened, synchronize, reopened]` (the existing `enforcement-gate.yml` `plan-approval` job, retargeted from `require-plan-approval.sh` to a new `plan_approval_gate_check.py`):
```
issues = resolve_linked_issues(PR)      # branch feat/<N>-*  ∪  PR body Closes/Refs #N  ∪  commit trailers
if not issues: FAIL CLOSED                                            # MAJOR-1, MAJOR-2
for N in issues:
    actor, at = verified_label_event(repo, N, "status:plan-approved")
    if actor is None: FAIL CLOSED                                    # MAJOR-1
    if not is_authorized_human(actor, PLAN_APPROVAL_OWNERS): FAIL    # MAJOR-4 (bot/App/PAT rejected)
    if not label_is_fresh(at, plan_revision_time(N), pr_head_time):  FAIL   # MAJOR-3
    if REQUIRE_SEPARATE and actor == pr_author: FAIL                 # A2 (default OFF, solo-friendly)
if owners-var / ruleset / gh-auth unverifiable: FAIL CLOSED          # MAJOR-1 (no degraded-open)
```
Gated behind `PLAN_APPROVAL_GATE_ENABLED` (staged rollout: the fail-closed gate only enforces once the repo ruleset restricting the label + `PLAN_APPROVAL_OWNERS` var are confirmed — config-gating the rollout, NOT degraded-open of the authority check).

### Local hooks (advisory only)
`.claude` + `.codex` `plan-approval-gate.sh`: remove marker reads (`has_approval`/`is_self_approved`); read a synced read-only label-cache (or `gh` if available) for the linked issue; **soft-warn** when not plan-approved; never block-as-authority. `require-plan-approval.sh` → advisory (`--check`, warn/exit 0); `check-marker-label-parity.sh` retired with the marker. Sequenced so CI never has two conflicting authorities.

### The 5 Codex MAJORs — each addressed
- **MAJOR-1 fail-CLOSED:** no degraded-open path. Unset owners var / unconfirmable ruleset / gh-auth failure / no linked issue / no label event → **block** with explicit reason. (Inverts the v2 "warn until ruleset" posture.)
- **MAJOR-2 anti-substitution:** bind approval to the resolved linked issue AND the specific plan artifact (record the plan path + revision SHA the issue references; freshness ties the label to that revision). A PR cannot borrow approval from an unrelated approved issue.
- **MAJOR-3 freshness:** label `applied_at` ≥ plan-revision time AND ≥ PR head commit time; `synchronize` re-evaluates, so a post-approval push invalidates until re-approval. (Reuses #2798's `body_is_fresh` shape.)
- **MAJOR-4 PAT/bot:** reject `*[bot]`, GitHub App tokens, and PAT machine users even if the login is in OWNERS; validate `PLAN_APPROVAL_OWNERS` is human-only at startup (assert no entry resolves to `type: Bot`).
- **MAJOR-5 migration:** `migrate_plan_approval_markers.py --report` enumerates in-flight open issues under the old marker/label regime for owner re-labeling; closed/merged issues grandfathered.

---

## Files to Change
| Action | Path | Reason |
|---|---|---|
| Create | `scripts/workflow/label_authority.py` | shared label-actor-authority helper (generalized from #2798's `_verified_label_event`) |
| Refactor | `scripts/workflow/completeness_gate_{runner,check}.py` | import the shared helper (non-regressive; existing tests guard) |
| Create | `scripts/workflow/plan_approval_gate_check.py` | the #2817 server decision (linked-issue + actor + freshness + anti-substitution; fail-closed) |
| Modify | `.github/workflows/enforcement-gate.yml` | retarget `plan-approval` job → `plan_approval_gate_check.py`; add `synchronize` trigger (MAJOR-3); retire `marker-label-parity` job |
| Modify | `.claude/hooks/plan-approval-gate.sh` | authoritative → advisory; remove marker reads |
| Modify | `.codex/hooks/plan-approval-gate.sh` | same (kept in lockstep) |
| Modify | `scripts/enforcement/require-plan-approval.sh` | demote to advisory |
| Retire | `scripts/enforcement/check-marker-label-parity.sh` | marker retired |
| Create | `scripts/workflow/migrate_plan_approval_markers.py` | MAJOR-5 audit/report |
| Modify | `.claude/skills/coordination/issue-planning-mode/SKILL.md` | approve = apply label only (drop marker step) |
| Create | `docs/governance/2026-05-30-plan-approval-label-authority.md` | ruleset prereq, OWNERS setup, migration, fail-closed rationale |
| Create | `tests/workflow/test_plan_approval_gate_check.py` | unit tests (below) |
| Create | `tests/workflow/test_label_authority.py` | shared-helper unit tests |
| Update | `docs/plans/README.md` | index; mark v1/v2 superseded |

---

## TDD Test List (`tests/workflow/test_plan_approval_gate_check.py` + `test_label_authority.py`)
| Test | Verifies | Expected |
|---|---|---|
| `test_authorized_human_label_passes` | owner human, fresh, linked | allowed |
| `test_unauthorized_actor_fails` | actor ∉ OWNERS | blocked |
| `test_bot_actor_fails` | login `*[bot]` / type Bot | blocked (MAJOR-4) |
| `test_app_token_pat_actor_fails` | GitHub App / machine user | blocked (MAJOR-4) |
| `test_owners_var_unset_fails_closed` | OWNERS empty | blocked, not warned (MAJOR-1) |
| `test_gh_auth_unavailable_fails_closed` | gh/token unverifiable | blocked (MAJOR-1) |
| `test_no_linked_issue_fails_closed` | no branch/body/trailer issue | blocked (MAJOR-2) |
| `test_no_plan_approved_label_fails` | linked issue unlabeled | blocked |
| `test_label_predates_plan_revision_fails` | label before plan revision | blocked (MAJOR-3) |
| `test_label_predates_pr_head_fails` | label before PR head | blocked (MAJOR-3) |
| `test_synchronize_after_approval_invalidates` | push after approval | blocked until re-approve (MAJOR-3) |
| `test_anti_substitution_unrelated_issue_fails` | PR borrows another issue's label | blocked (MAJOR-2) |
| `test_separate_off_solo_author_approver_ok` | default: author==actor, human owner | allowed (A2) |
| `test_separate_on_blocks_self_approve` | REQUIRE_SEPARATE=1, author==actor | blocked (A2) |
| `test_legacy_marker_grants_no_authority` | forged local marker present | server still required |
| `test_owners_containing_bot_fails_startup` | OWNERS has a Bot | startup assertion fails (MAJOR-4) |
| `test_verified_label_event_param_label` (helper) | `verified_label_event` works for any label name | returns (actor, applied_at) |
| `test_completeness_gate_unchanged_after_refactor` (helper) | existing completeness tests still green | non-regressive generalization |
| (hook) `test_local_hook_advisory_warns_not_blocks` | no approval | exit 0 + WARN |
| (migration) `test_migration_report_lists_inflight` | audit lists in-flight issues | correct report (MAJOR-5) |

---

## Acceptance Criteria
- [ ] Server gate blocks merge unless `status:plan-approved` was applied on the resolved linked issue by an authorized **human** owner (∈ OWNERS, not bot/App/PAT).
- [ ] **Fails closed** on unverifiable owners/ruleset/gh-auth/linked-issue/label-event (MAJOR-1).
- [ ] Linkage resolved from branch / PR-body / commit trailer; approval bound to the specific plan artifact+revision (MAJOR-2).
- [ ] Label must post-date plan revision and PR head; `synchronize` invalidates stale approvals (MAJOR-3).
- [ ] Bot/App/PAT actors rejected; OWNERS validated human-only at startup (MAJOR-4).
- [ ] Migration audit lists in-flight issues; closed issues grandfathered (MAJOR-5).
- [ ] Shared `label_authority.py` used by BOTH gates; completeness tests still green (non-regressive).
- [ ] Local hooks advisory + marker-independent; a forged marker grants NO authority.
- [ ] Repo ruleset restricting the label documented as an admin prerequisite; gate behind `PLAN_APPROVAL_GATE_ENABLED` until ruleset + OWNERS confirmed.
- [ ] `issue-planning-mode/SKILL.md` approve step = apply label only.
- [ ] `uv run pytest tests/workflow/` green; `scripts/legal/legal-sanity-scan.sh` clean.
- [ ] T3 review artifacts (Claude + Codex + Gemini) posted, incl. the previously-missing Codex artifact.

---

## Risks
- **Local bypass window (accepted, contained):** an agent can still write locally + self-approve locally — but CANNOT merge (server is the authority). Contained at the gate that matters.
- **Ruleset prerequisite is hard-blocking** (because fail-closed). Mitigation: `PLAN_APPROVAL_GATE_ENABLED` staged flag flipped on only after the ruleset + OWNERS var are confirmed (config-gating the rollout, not degraded-open).
- **Shared-helper refactor regressing #2798:** mitigated by the existing completeness tests + a `test_completeness_gate_unchanged_after_refactor` guard; land the refactor as its own reviewed step.
- **Freshness false-positives on legitimate force-push/rebase:** changes head time, can invalidate a still-valid approval → re-approve. Accepted for security; documented (mirrors #2798 reopen-on-freshness).
- **5 MAJORs sourced from a comment, not a reviewed artifact:** the T3 review must produce the missing Codex artifact and may surface findings beyond the 5.

## Complexity: T3
Systemic, security-critical (a wrong fail-open re-opens the bypass), cross-provider (`.claude`+`.codex`), touches a shared helper used by another live gate, needs a repo-ruleset admin prerequisite + migration. ⇒ Claude + Codex + Gemini review.

## Open Questions (need the USER)
1. `PLAN_APPROVAL_OWNERS` membership — presumably just `vamseeachanta` (solo). Confirm the exact human login set + that the repo ruleset can be admin-configured to restrict the label.
2. Advisory hook: read a synced label-cache file, or call `gh` live? (Recommend label-cache for offline UX; `gh` when available.)
3. Land the shared-helper refactor of #2798 in THIS PR, or as a separate prerequisite PR? (Recommend separate prerequisite PR so the non-regressive refactor is reviewed in isolation.)

*Not self-approved. Future-tense. Awaiting USER approval to move `status:needs-plan` → `status:plan-review` → (USER) `status:plan-approved`.*
