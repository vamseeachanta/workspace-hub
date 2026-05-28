# Plan for #2817 (re-scoped): plan-approval gate trusts label-actor authority; retire forgeable marker

> **Status:** plan-review (Claude r1 MAJOR→fixed; Codex + Gemini T3 pending — security gate)
> **Complexity:** T3 (systemic — security gate + server workflow + repo ruleset + skill + migration)
> **Date:** 2026-05-28
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2817
> **Client:** N/A
> **Review artifacts:** scripts/review/results/2026-05-28-plan-2817v2-{claude,codex,gemini}.md
> **Supersedes:** docs/plans/2026-05-27-issue-2817-atomic-approve-issue-helper.md (marker-helper premise was itself a self-approval primitive — Codex r2)

---

## Resource Intelligence Summary

### Existing repo code (prior art to REUSE — not rebuild)
- **`scripts/workflow/completeness_gate_runner.py`** (#2798) — `_verified_label_event(repo, issue)` returns `(actor, applied_at)` for a label's most-recent application; `COMPLETENESS_OWNERS` authorized-owner set; actor ≠ closing-bot cross-check. **This is the exact label-actor-authority pattern to reuse.**
- **`.github/workflows/completeness-gate.yml`** — server-side enforcement on a GitHub event (reopen-on-violation). Template for the plan-approval merge gate.
- **`.claude/hooks/plan-approval-gate.sh`** + **`.codex/hooks/plan-approval-gate.sh`** — local PreToolUse gates; today AUTHORITATIVE via forgeable marker. To become ADVISORY.
- **`scripts/enforcement/require-plan-approval.sh`** — pre-commit marker check (no age check — accepts marker immediately). To become advisory.
- **`scripts/enforcement/check-marker-label-parity.sh`** — enforces marker↔label parity. Re-purpose or retire as marker retires.
- **#2405** — attestation mechanism (considered; NOT chosen — server-authoritative is simpler, no signing infra).

### Gaps identified
- Approval authority is a **forgeable local marker** any process (incl. an agent) can create → self-approval bypass (Codex r2 on the superseded plan).
- No server-side verification that `status:plan-approved` was applied by an authorized **human**.
- The separate marker is why the 2-step exists (and keeps getting dropped — 3× this session).

### Evidence
- Bypass repro (review-derived): `plan-approval-gate.sh` trusts a marker >120s; `require-plan-approval.sh` has no age check → an agent that creates a marker self-approves. Verified by reading both scripts from `origin/main` 2026-05-28.
- #2798 already solved the analogous "agent can't self-certify" problem server-side via owner-only label + actor cross-check.

<!-- sources: #2817 + Codex r2 artifact, completeness_gate_runner.py, completeness-gate.yml, plan-approval-gate.sh, require-plan-approval.sh, #2798 = 6 -->

---

## Deliverable
Approval authority moves from the local marker to the **human-attributed `status:plan-approved` label**: a server-side Action verifies the label actor is an authorized human (repo-ruleset-restricted) and blocks merge otherwise; the local hooks become **advisory** fast-checks; the hand-created marker is **retired** (eliminating both the self-approval bypass and the dropped-marker papercut).

## Architecture (locked w/ user 2026-05-28: server-authoritative + local-advisory)
```
APPROVAL = a human applies `status:plan-approved` on the issue (one action, audit-attributed).
           No local marker step.

SERVER (authority): .github/workflows/plan-approval-gate.yml on pull_request to main:
  # A1: resolve linked issue(s) — branch `feat/<N>-*`, PR body `Closes/Refs #N`, or commit trailers.
  #     If NO plan-approved issue is resolvable -> FAIL CLOSED (block: "no linked plan-approved issue").
  for each linked issue:
    actor, applied_at = _verified_label_event(repo, issue)        # REUSE #2798 helper
    if actor is automation/bot (github-actions[bot], app tokens) -> FAIL (agents/bots never approve)
    if actor not in PLAN_APPROVAL_OWNERS (repo var, ruleset-restricted) -> FAIL (block merge)
    # A2: author≠approver is OPTIONAL (solo-friendly default OFF) — the boundary is human-vs-agent,
    #     not author-vs-approver. Only when PLAN_APPROVAL_REQUIRE_SEPARATE=1 do we also fail on
    #     PR-author == label-actor. Mirrors #2798 COMPLETENESS_REQUIRE_SEPARATE_CLOSER.
  Repo RULESET restricts who may apply `status:plan-approved` (admin prereq, like #2798's verified label).

LOCAL (discipline check, NON-authoritative): .claude + .codex plan-approval-gate.sh:
  # A3: local keeps a fast DISCIPLINE soft-check (honor-system, like today's marker) for UX —
  #     it is explicitly NOT the security authority (a local file is forgeable). Reads a read-only
  #     synced label-cache; soft-blocks/warns when the linked issue isn't plan-approved.
  #     Security lives at the SERVER. Hand-made marker RETIRED; require-plan-approval.sh +
  #     check-marker-label-parity.sh demoted to advisory/retired.

MIGRATION: existing .planning/plan-approved/*.md become legacy/no-op; label is authority going forward.
```

## Files to Change
| Action | Path | Reason |
|---|---|---|
| Create | `.github/workflows/plan-approval-gate.yml` | server-side merge gate (pull_request) |
| Create | `scripts/workflow/plan_approval_gate_check.py` | actor-authority check (reuse `_verified_label_event` + owners pattern) |
| Modify | `.claude/hooks/plan-approval-gate.sh`, `.codex/hooks/plan-approval-gate.sh` | authoritative→advisory; drop marker dependence |
| Modify | `scripts/enforcement/require-plan-approval.sh` | advisory; stop requiring hand-made marker |
| Modify/Retire | `scripts/enforcement/check-marker-label-parity.sh` | marker retired → repurpose to label-only or remove |
| Modify | `.claude/skills/coordination/issue-planning-mode/SKILL.md` | approve step = apply label (one action); no marker |
| Create | `tests/workflow/test_plan_approval_gate_check.py` | actor-auth: human pass, bot/agent fail, unauthorized fail, self-approve fail |
| Doc | `docs/governance/2026-05-28-plan-approval-label-authority.md` | ruleset prereq + migration note |
| Update | `docs/plans/README.md` | index + mark superseded plan |

## TDD Test List
| Test | Verifies | Expected |
|---|---|---|
| test_label_actor_authorized_human | label by owner in PLAN_APPROVAL_OWNERS → pass | merge allowed |
| test_label_actor_unauthorized | label by non-owner → fail | merge blocked |
| test_label_actor_is_bot | label by automation/github-actions → fail | blocked |
| test_separate_actor_toggle_off_solo_ok | default (toggle off): PR author == label actor, both authorized human → PASS (solo-friendly, A2) | merge allowed |
| test_separate_actor_toggle_on_blocks | REQUIRE_SEPARATE=1: PR author == label actor → fail | blocked |
| test_no_linked_issue_fails_closed | PR resolves no plan-approved issue → fail closed (A1) | blocked |
| test_no_plan_approved_label | linked issue lacks label → fail | blocked |
| test_local_hook_advisory_warns_not_blocks | local hook with no marker → WARN exit 0 (advisory) | non-blocking |
| test_local_hook_no_marker_dependence | hook no longer reads `.planning/plan-approved/` as authority | label-cache path used |
| test_legacy_marker_ignored | a stale local marker does NOT grant authority anymore | server still required |

## Acceptance Criteria
- [ ] Server Action blocks merge unless `status:plan-approved` was applied by an authorized human (actor ∈ owners, actor ≠ bot); author≠approver enforced ONLY when `PLAN_APPROVAL_REQUIRE_SEPARATE=1` (solo-friendly default off, A2)
- [ ] PR with no resolvable plan-approved issue → fail closed (A1)
- [ ] Repo ruleset restricting the label is documented as an admin prerequisite (governance doc)
- [ ] Local hooks are advisory (warn, exit 0) — no longer authoritative; no hand-made marker required
- [ ] A forged/agent-created local marker grants NO authority (bypass closed)
- [ ] `uv run pytest tests/workflow/test_plan_approval_gate_check.py` green; legal-sanity-scan clean
- [ ] issue-planning-mode approve step updated (apply label, no marker); migration documented
- [ ] Review artifacts posted (T3)

## Adversarial Review Summary
| Provider | Verdict | Findings |
|---|---|---|
| Claude (r1) | MAJOR → fixed | A1 PR↔issue linkage undefined → branch/Closes/trailer resolution + fail-closed; A2 hard self-approve-fail blocks solo operator → optional REQUIRE_SEPARATE toggle (default off); A3 local = discipline check, not silent |
| Codex (delta) | PENDING | re-scoped plan pushed |
| Gemini (delta) | PENDING | — |

**Overall:** Claude r1 fixed. T3 (security gate) ⇒ Codex + Gemini pending. Not approval-ready until they clear.

## Risks and Open Questions
- **Risk (local-bypass window):** an agent can still write LOCALLY (advisory hook won't hard-block) and even self-approve locally — but it CANNOT merge (server authority). Accept: the bypass is *contained at the merge gate*, where it matters. Document explicitly.
- **Risk (ruleset prereq):** requires repo-admin to configure the authorized-label-applier ruleset; until then the server check warns instead of blocking (degraded). Document.
- **Risk (offline approval):** approval now requires applying a GitHub label (network). Acceptable — approval is inherently a GitHub act.
- **Open (marker: retire vs cache):** recommend RETIRE the hand-made marker entirely (it's the bypass + papercut source); keep only a read-only synced label-cache for the advisory hook. Flag for approval.
- **Open (scope of server gate trigger):** pull_request to main only, or also push to protected branches? Recommend PR-to-main (merge is the authority point).
- **Migration:** existing `status:plan-approved` issues without a verified actor (pre-this-change) — grandfather, or require re-label? Recommend grandfather closed/merged; require label-actor for new merges only.

## Complexity: T3
Systemic security-gate change: server workflow + actor-auth module + 2 local hooks → advisory + enforcement-script demotion + skill + ruleset prereq + migration. T3 ⇒ Claude + Codex + Gemini.
