# Plan for #2500: chore(harness): #2476 non-standard approval pattern (no plan branch)

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-04-27
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2500
> **Review artifacts:** scripts/review/results/2026-04-27-plan-2500-claude.md | scripts/review/results/2026-04-27-plan-2500-codex.md | scripts/review/results/2026-04-27-plan-2500-gemini.md

> **Plan-class:** harness/audit chore. Deliverable will be a documentation/governance correction plus a routing decision for #2476, not a code change. The plan honestly reframes the issue premise after verification.

---

## Resource Intelligence Summary

### Existing repo code

- Found: `docs/plans/2026-04-23-issue-2476-llm-wiki-semantic-equivalence-contract.md` exists on `main` at blob `322d10ef8cfa7d8d61e4ed2fa045bd899ffa6b9e` (verified 2026-04-27 via `git hash-object`); last touched at commit `5339798efc6c3b94aa19491bd236993014f13ce4` "docs(plan): approve OrcaWave OrcaFlex next-wave plans" on 2026-04-24.
- Found: `.planning/plan-approved/2476.md` exists and is git-tracked (verified via `git ls-files .planning/plan-approved/2476.md`); landed in commit `5339798e` on 2026-04-24 alongside the plan-approval push.
- Found: `.claude/skills/coordination/issue-planning-mode/SKILL.md` v3.1.0 — Step 4/5/6 prescribe the canonical approval gate as: `status:plan-approved` GitHub label + `.planning/plan-approved/<NNN>.md` marker. **No mention of a `plan/issue-NNN-*` branch as part of the approval contract.**
- Found: `docs/plans/_template-issue-plan.md` defines plan structure (Resource Intelligence, Artifact Map, Deliverable, Pseudocode, Files to Change, TDD Test List, Acceptance Criteria, Adversarial Review, Risks, Complexity). **No mandate for a plan branch.**
- Confirmed no existing implementation: a workspace grep of `scripts/`, `.claude/rules/`, `.claude/skills/coordination/issue-planning-mode/SKILL.md`, `AGENTS.md`, `CLAUDE.md`, and `docs/plans/README.md` for the literal terms `plan/issue-`, `plan-branch`, `plan branch`, `execute-from-plan-branch`, `exec routine`, and `one-shot exec` returned **zero matches** (verified 2026-04-27 via two grep sweeps, see Evidence). The "standard execute-from-plan-branch pattern" the #2500 body invokes is not a documented workspace convention.
- Found: 13 `plan/issue-*` branches do exist in `origin/` (2103, 2124, 2125, 2126, 2227, 2363, 2364, 2368, 2369, 2373, 2380, 2392, 2471) but they are a **partial pattern** used by some lanes (notably wiki-promotion batch packs and faceted-portal work), not by the recently-approved general plan corpus (#2486, #2508, #2514 each have a plan file on `main`, a `status:plan-approved` label, and **no plan branch**, mirroring #2476's shape exactly).
- Gap: no documented rule named the plan-branch convention as either mandatory or conditional, so #2500's premise that #2476 "breaks the standard execute-from-plan-branch pattern" is unverifiable against the canonical workflow contract.

### Standards

| Standard | Status | Source |
|---|---|---|
| Approval-gate canonical contract | applicable | `.claude/skills/coordination/issue-planning-mode/SKILL.md` Step 4/5/6 — label + local marker only |
| Revision-bound approval marker (per #2460 closure decision) | applicable | Memory note: "approval markers must be revision-bound (SHA + review artifact paths + storage surface), not mutable file-path refs" — cited via `~/.claude/projects/.../memory/MEMORY.md` and #2499 sibling chore which restates the rule |
| Plan-branch convention | **not a standard** | Searched repeatedly; no rule, skill, or script mandates it |
| Calc-citation contract | not applicable | This is a harness/audit issue, no calc constants |

### LLM Wiki pages consulted

- Not applicable; this is a workflow/harness chore and does not add domain wiki content.

### Documents consulted

- Issue #2476 body and 5 comments (verified 2026-04-27 via `gh issue view 2476 --comments`). Final comment (advisory posted 2026-04-26) is itself the same framing #2500 escalates.
- Issue #2500 body (verified 2026-04-27 via `gh issue view 2500`). Cluster sibling chore issues #2498, #2499, #2501, #2502 each surfaced same-day from the autonomous-wave session and follow the same `chore(harness):` shape.
- Issue #2477 body (referenced in #2476's approval comment as the parking lot for "Codex/Gemini review-runner hardening"). Confirmed OPEN — the underlying provider-runner regression that justified the waiver has not been closed; codex-cli 0.124.0 stdin-hang regression #2479 also remains unresolved (per memory).
- Issue #2460 (closed 2026-04-23): tier-1 indexing contract. The "revision-bound approval" lesson tied to #2460's closure (per memory + #2499 chore body) requires every approval to bind to a SHA + review artifacts + storage surface — that rule is the actually-applicable governance lever for #2500, not the plan-branch framing.
- Issue #2469 (closed) and #2467/#2468 (closed): worldenergydata flake8 lanes — confirmed they are unrelated to #2500's actual scope. They were cited in the dispatch prompt because they were the parent forensics issues for the revision-bound approval rule. They contain no plan-branch contract; their relevance is solely the binding-rule lineage.
- `docs/plans/2026-04-27-issue-2503-canonical-approval-request-comments.md` — concurrent ongoing work to standardize approval-request comment shape (parser/validator + backfill template). #2500's documentation deliverable should align with the schema #2503 will publish, not duplicate it.
- `docs/plans/README.md` — onboarding guide; does not mandate a plan branch (verified 2026-04-27).
- Absence of any `docs/governance/*-plan-branch*` or `docs/standards/*plan-branch*` document (confirmed via repo listing).

### Gaps identified

- The plan-branch convention is undocumented but partially practiced; no governance artifact decides whether it is mandatory, optional, or contextual (e.g., only required for batch/multi-issue lanes).
- #2476's approval comment cites the explicit Codex/Gemini review-runner waiver, but there is no durable governance record of what counts as a valid waiver. **This is the actually-non-standard element of #2476's approval, not the missing plan branch.**
- #2500's three proposed "decision" options (reconstruct branch / inline-draft / wait for #2477) all assume the false premise that the missing branch is the blocker. Honest scope is to correct the framing first, then make a much smaller routing decision for #2476 execution.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-27 via `gh issue view`):

- `#2500` — OPEN — chore(harness): #2476 non-standard approval pattern (no plan branch); labels: cat:harness, priority:medium
- `#2476` — OPEN — docs(llm-wiki): add canonical spec semantic-equivalence contract and fixture cookbook; labels include `status:plan-approved`
- `#2477` — OPEN (referenced; provider-runner hardening parking lot)
- `#2486` — CLOSED with `status:plan-approved` (plan-on-main, no plan branch — same shape as #2476)
- `#2508` — CLOSED with `status:plan-approved` (plan-on-main, no plan branch)
- `#2514` — CLOSED with `status:done` (plan-on-main, no plan branch)
- `#2498`, `#2499`, `#2501`, `#2502` — OPEN, all `cat:harness, priority:medium`, all surfaced 2026-04-26 from the same autonomous-wave session
- `#2467` — CLOSED (worldenergydata pathological flake8 blocker)
- `#2468` — CLOSED (worldenergydata first-wave safe rules + durable inventory)
- `#2469` — CLOSED (worldenergydata final green-gate verification)
- `#2460` — CLOSED (tier-1 indexing contract; closure produced the revision-bound approval-marker lesson per memory)

**File existence** (verified 2026-04-27):

- EXISTS: `docs/plans/2026-04-23-issue-2476-llm-wiki-semantic-equivalence-contract.md` (blob `322d10ef8cfa7d8d61e4ed2fa045bd899ffa6b9e`)
- EXISTS: `.planning/plan-approved/2476.md` (git-tracked, landed at `5339798e`)
- EXISTS: `.claude/skills/coordination/issue-planning-mode/SKILL.md`
- EXISTS: `docs/plans/_template-issue-plan.md`
- EXISTS: `docs/plans/2026-04-27-issue-2503-canonical-approval-request-comments.md`
- MISSING (would be created by this plan): `docs/governance/plan-branch-convention.md` — short note clarifying that the plan-branch pattern is optional, naming when it is and is not used; **OR** a one-line addition to `docs/plans/README.md` that does the same.
- MISSING: no audit script enforces a plan-branch requirement (confirmed via `grep -rn "plan/issue-" scripts/ai scripts/review` returning zero hits).

**Live state for #2476** (verified 2026-04-27):

- Plan file path: `docs/plans/2026-04-23-issue-2476-llm-wiki-semantic-equivalence-contract.md`
- Plan file blob: `322d10ef8cfa7d8d61e4ed2fa045bd899ffa6b9e`
- Plan file landed at commit: `5339798efc6c3b94aa19491bd236993014f13ce4` on `main`
- Local approval marker: `.planning/plan-approved/2476.md` (git-tracked at the same commit)
- GitHub label: `status:plan-approved` present
- Approval comment (2026-04-24) on #2476 explicitly states: "User explicitly instructed: waive the broken Codex/Gemini review-runner issue for this pair and approve based on remaining review evidence. Waiver applies only to #2475/#2476."
- Provider review artifacts under `scripts/review/results/`: `2026-04-23-plan-2476-claude.md`, `2026-04-23-plan-2476-codex.md`, `2026-04-23-plan-2476-gemini.md`, `2026-04-23-plan-2476-disagreement.md` (cited in #2476 comment thread; not re-verified inline here).

**Gap proofs**:

- `grep -rn "plan/issue-\|plan-branch\|plan branch\|execute-from-plan-branch\|exec routine\|one-shot exec" .claude/rules .claude/skills/coordination/issue-planning-mode/SKILL.md docs/plans/README.md AGENTS.md CLAUDE.md` → zero matches.
- `grep -rn "plan/issue-" scripts/ai scripts/review` → zero matches.
- No `docs/governance/plan-branch*.md` file exists.

<!-- Verification: distinct sources cited above — issue #2500 body, issue #2476 body+comments, issue #2477 body, issue #2460 closure thread, issue #2486 / #2508 / #2514 metadata, issue #2498/#2499 sibling chores, MEMORY.md project notes, `docs/plans/_template-issue-plan.md`, `docs/plans/README.md`, `.claude/skills/coordination/issue-planning-mode/SKILL.md`, `docs/plans/2026-04-27-issue-2503-canonical-approval-request-comments.md`, git blob/commit verification. Count: 12+ distinct sources. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-27-issue-2500-llm-wiki-2476-approval-pattern-audit.md` |
| Governance note clarifying plan-branch convention | `docs/governance/plan-branch-convention.md` (new, ~20 lines) **OR** an additive section in `docs/plans/README.md` (single source preferred) |
| Optional: short rule note | `.claude/rules/plan-branch.md` only if Level-2 enforcement is later wanted; not part of this plan |
| Routing decision artifact for #2476 | A decision comment posted on #2476 binding the existing approval to commit SHA `5339798e`, plan blob `322d10ef`, and review artifacts list (consistent with #2503 schema once it lands) |
| Plan review — Claude | `scripts/review/results/2026-04-27-plan-2500-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-27-plan-2500-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-27-plan-2500-gemini.md` |

---

## Deliverable

A short governance note declaring the plan-branch pattern **optional and contextual** (mandatory only when explicitly required by an exec routine that we do not yet have), plus a revision-bound approval-binding comment on #2476 that re-anchors the existing approval to the live commit SHA, plan blob, and review artifacts — so #2476 can execute under the documented (label + marker) gate without inventing a branch retroactively, and so the cluster siblings (#2498/#2499/#2501) can reference the same governance correction.

This plan does **not** propose to reconstruct a plan branch for #2476, and does **not** treat the missing branch as a defect. It treats the **missing waiver-governance documentation** and the **missing revision-bound marker comment** as the real defects.

---

## Pseudocode

```
# Step A — clarify the convention (durable doc edit)
write docs/governance/plan-branch-convention.md OR append to docs/plans/README.md:
    SECTION "Plan branches"
    state: plan branches (refs/heads/plan/issue-NNN-*) are an OPTIONAL pattern
    enumerate when we DO use them:
        - multi-issue batch packs (issue-2364 batch-pack-1, issue-2369 batch-pack-2, ...)
        - wiki-promotion lanes (issue-2227, issue-2471)
        - any case where multiple commits accumulate before approval and rebase-on-main risks losing review evidence
    enumerate when we DON'T use them (and #2476 falls here):
        - single-file plan additions on main
        - plans where review artifacts already capture the reviewed revision
    explicitly state: missing plan branch is NOT an approval-gate violation
    cross-link: revision-bound approval-marker rule (#2460 lineage), #2503 canonical approval-request comment template

# Step B — emit revision-bound approval-binding comment on #2476
gather:
    plan_path = docs/plans/2026-04-23-issue-2476-llm-wiki-semantic-equivalence-contract.md
    plan_blob = 322d10ef8cfa7d8d61e4ed2fa045bd899ffa6b9e
    plan_commit = 5339798efc6c3b94aa19491bd236993014f13ce4
    marker_path = .planning/plan-approved/2476.md
    review_artifacts = [
        scripts/review/results/2026-04-23-plan-2476-claude.md,
        scripts/review/results/2026-04-23-plan-2476-codex.md,    # waived per 2026-04-24 user instruction
        scripts/review/results/2026-04-23-plan-2476-gemini.md,   # waived per 2026-04-24 user instruction
        scripts/review/results/2026-04-23-plan-2476-disagreement.md,
    ]
    waiver_basis = "User explicit waiver 2026-04-24 due to codex-cli stdin-hang regression (#2477/#2479); waiver scope limited to #2475/#2476."
post comment that includes ALL fields above, in the schema #2503 will codify (or at minimum the
fields the memory rule requires: SHA + review artifact paths + storage surface).

# Step C — close #2500 referencing the governance note + the binding comment
no further work needed; #2476 is already executable under the documented gate.
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/governance/plan-branch-convention.md` (~25 lines) | Document plan-branch as optional pattern; remove ambiguity that surfaced as #2500 |
| OR Modify | `docs/plans/README.md` | Add a "Plan branches (optional)" subsection if a single-source approach is preferred over a new governance file |
| Update | `docs/plans/README.md` index | Add row for this plan |
| No-op | `docs/plans/2026-04-23-issue-2476-llm-wiki-semantic-equivalence-contract.md` | DO NOT edit — its approval is preserved as-is |
| No-op | `.planning/plan-approved/2476.md` | DO NOT edit — preserved at commit `5339798e` |
| No code | n/a | Pure documentation/governance + a GitHub comment; no scripts, no tests |

Outside-repo (GitHub comment, not a file change):

- Post revision-bound binding comment on #2476 (Step B above) at execution time.
- Close #2500 with a comment summarizing the governance correction and naming the binding comment URL.

---

## TDD Test List

This is a documentation/governance plan with no executable behavior; classical TDD does not apply. The verification checklist below substitutes:

| Check | What it verifies | Method |
|---|---|---|
| Governance note links from `docs/plans/README.md` | Discoverability | grep for the new file path in `docs/plans/README.md` |
| Governance note states "optional, not mandatory" | Honest scope | grep for the literal phrase in the new file |
| Governance note enumerates ≥3 lanes that historically used plan branches | Concreteness | grep for cited issue numbers (2364, 2369, 2227, 2471, etc.) |
| Binding comment on #2476 cites SHA + plan blob + marker + review artifacts | Revision-bound rule (#2460 lineage) | gh issue view 2476 --comments | grep for `5339798e`, `322d10ef`, `.planning/plan-approved/2476.md` |
| #2500 close comment links the binding comment + governance note | Audit trail | gh issue view 2500 --comments after close |

If a future iteration promotes the convention to a Level-2 script (per `.claude/rules/patterns.md`), at that point a real test suite (e.g., `tests/governance/test_plan_branch_audit.py`) becomes appropriate. Out of scope for #2500.

---

## Acceptance Criteria

- [ ] `docs/governance/plan-branch-convention.md` exists (or equivalent additive section in `docs/plans/README.md`) and explicitly says: plan branches are OPTIONAL; missing plan branch is NOT an approval-gate violation.
- [ ] The governance note cross-references the canonical approval gate (label + `.planning/plan-approved/<NNN>.md` marker) per `issue-planning-mode` skill v3.1.0.
- [ ] The governance note acknowledges the partial-practice lanes (batch-pack and wiki-promotion) so readers do not interpret the note as forbidding plan branches.
- [ ] A revision-bound binding comment is posted on #2476 carrying: plan path, plan blob (`322d10ef`), plan-landing commit (`5339798e`), local marker path, list of review artifacts, and the explicit Codex/Gemini waiver text from the 2026-04-24 user instruction.
- [ ] Acceptance bullet 1 of #2500 is satisfied via the second clause: "the non-standard approval-on-main path is documented as an explicit alternate workflow" — except this plan reframes it as the **standard** path with the plan-branch lane as the alternate, since the evidence supports that direction.
- [ ] #2500 closes with a comment naming the governance note path and the #2476 binding-comment URL.
- [ ] No edits to `docs/plans/2026-04-23-issue-2476-llm-wiki-semantic-equivalence-contract.md` or `.planning/plan-approved/2476.md`.
- [ ] Plan-review artifacts produced for #2500 itself in `scripts/review/results/2026-04-27-plan-2500-{claude,codex,gemini}.md` (or documented waiver per #2477/#2479 if review-runner remains regressed at execution time).
- [ ] Sibling chore #2499 (which restates the revision-bound rule for #2368) is cross-linked from the binding comment as the precedent pattern.

---

## Adversarial Review Summary

<!-- To be filled in after review wave; pre-emptive likely-finding inventory below for transparency. -->

| Provider | Verdict | Key findings (anticipated) |
|---|---|---|
| Claude | TBD | likely-MINOR: ensure the governance note does not retroactively label batch-pack/wiki-promotion plan-branch use as deviant |
| Codex | TBD (may be blocked by codex-cli 0.124.0 stdin-hang per #2479) | n/a until provider-runner restored |
| Gemini | TBD | likely-MINOR: confirm Gemini sandbox can read the new `docs/governance/` file (per memory: Gemini overlay-blindness) |

**Pre-emptive defect-hunting against this plan:**

1. The plan REFRAMES the issue premise. Reviewers may interpret this as scope-shifting. **Defense:** the verification log establishes that the original premise ("breaks the standard execute-from-plan-branch pattern") is unsupported by any documented standard; the honest scope is to correct the framing. This is the same lesson as the "plan past-tense drift" memory rule applied to #2500's body assumptions.
2. Option 1 in #2500 ("reconstruct plan branch") is rejected here without offering a second-class alternative. **Defense:** reconstructing a branch from `origin/main` would create a branch with no commit history before approval — i.e., the branch would not preserve any review evidence the main-line plan does not already carry. Cost without benefit.
3. The governance note may collide with #2503's canonical-approval-request scope. **Defense:** #2503 covers the comment shape; this plan covers the branch convention. Distinct surfaces; cross-linked.
4. The waiver-governance gap (#2476's review-runner waiver) is identified but not closed by this plan. **Defense:** waiver-governance is a strictly larger scope; explicitly named as out-of-scope and routed to a future issue rather than swept under #2500.

**Overall result (target):** PASS once review wave completes. PRE-APPROVAL READY: no.

---

## Risks and Open Questions

- **Risk:** User may prefer Option 1 from #2500 (reconstruct the plan branch) on aesthetic/consistency grounds. **Mitigation:** the plan presents the evidence and lets the user choose; if Option 1 is preferred, the plan becomes a 1-line `git switch -c plan/issue-2476-... origin/main && git push -u origin HEAD` and then deleting the governance note. The cost is a short branch with no preserved planning history.
- **Risk:** The governance note becomes a maintenance burden if plan-branch usage drifts further. **Mitigation:** keep the note short (~25 lines), enumerate lanes by name, and accept that drift is governed by the broader continuous-planning-pipeline (#2489 / #2503) rather than by this note.
- **Risk:** Posting the binding comment without #2503's canonical schema being landed yet creates schema-drift later. **Mitigation:** post the comment with **all fields the #2503 plan currently enumerates** (Issue, Plan-Path, Plan-SHA256, Reviewed-Revision, Review-Artifacts, Review-Verdicts, Requested-Decision, Approval-Options, Authority-Warning, Requested-At-UTC). #2503's parser will treat it as a clean retroactive binding comment when it lands.
- **Risk:** The `Plan-SHA256` field expects the file's sha256, not the git blob hash. **Mitigation:** compute both at execution time (`sha256sum docs/plans/2026-04-23-...md` and `git hash-object docs/plans/2026-04-23-...md`) and include both with explicit labels.
- **Risk:** Codex/Gemini provider runners may still be regressed (per memory entries on codex-cli 0.124.0 + Gemini overlay-blindness). **Mitigation:** if review-runner is still broken at execution time, document the waiver in the plan's Adversarial Review Summary using the same shape #2476 used, and proceed.
- **Open question:** Should `docs/governance/plan-branch-convention.md` be promoted to `.claude/rules/` later? Defer to whoever picks up the next iteration of the convention; not in scope for #2500.
- **Open question:** Do the cluster siblings (#2498 plan-branch drift recovery for #2364; #2499 missing revision-bound marker for #2368; #2501 #2105 governance lock) all want to share this governance note? The note should be written so they can.

---

## Complexity: T1

**T1** — single short documentation file (or one additive section in `docs/plans/README.md`) plus one GitHub comment plus one issue-close comment. No code changes, no tests, no scripts. The "complexity" lives entirely in the verification log establishing that the issue premise needed correction; once that is documented, execution is mechanical.
