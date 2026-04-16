# Adversarial Review: Plan #2294 — Salvage #2290 Follow-On Learnings

**Reviewed:** `docs/plans/2026-04-15-issue-2294-salvage-2290-follow-on-learnings-for-regression-coverage-and-github-code-review-scope.md`

---

## 1. Verdict: MINOR

The plan is structurally sound — good scope discipline, honest risk identification, and a defensible keep/reject/defer framework. Two non-blocking flaws prevent APPROVE: (a) every TDD test is conditional ("If accepted…"), so the plan can pass all acceptance criteria by rejecting everything and landing an empty implementation; and (b) the plan leaves two critical design decisions as open questions that should be resolved before implementation, not during it.

---

## 2. Strengths

- **Scope discipline is genuine.** The explicit out-of-scope table names 5 specific exclusions with issue numbers. The plan does not attempt to reopen #2290 or redesign the GitHub skill taxonomy.
- **Risk identification is honest and actionable.** The three named risks (overfitted regression scans, skill-scope sprawl, hidden boundary decisions) directly match the real hazards visible in the preserved branch content. The 480-line branch draft does in fact mix auth detection boilerplate and PR lifecycle content already owned by `github-auth` and `github-pr-workflow`.
- **Resource intelligence is thorough.** 10+ distinct sources consulted; the plan correctly identifies that the current regression test (93 lines, 4 test functions) only covers audit-clearing and path existence, not auxiliary-file preservation or dangling-reference scans.
- **The keep/reject/defer framework** prevents wholesale cherry-picking and forces deliberate triage of each preserved assertion/section.
- **The preserved branch exists locally** (`issue-2290-implementation`, 2 commits ahead of the merge base), eliminating the retrieval risk flagged by Gemini.

---

## 3. Gaps

- **No minimum-viable output is defined.** The plan can satisfy all acceptance criteria by classifying everything as "reject" — landing only the plan doc and review artifacts with zero test or skill changes. There is no floor on what constitutes a successful implementation.
- **Open questions are design decisions, not questions.** The two open items — (1) whether deleted-path scans use an allowlist vs. recursive walk, and (2) whether content belonging in a neighbor skill is updated here or deferred — are architectural choices that constrain implementation. Leaving them open means the implementer makes the design call unilaterally.
- **No criteria for "high-signal" classification.** The plan says to "keep only assertions that protect durable repo-governance surfaces" but doesn't define what makes a surface durable or an assertion high-signal. The preserved branch's `TestReferenceSurfacesClean` class (lines 130–197 of the branch test) scans `.claude/agent-skills-map.yaml`, `.claude/skill-registry.yaml`, `AGENTS.md`, `.mcp.json`, `.codex/`, `.gemini/`, `.hermes/`, `config/`, and `scripts/` — these are exactly the control-plane adapter surfaces named in `CONTROL_PLANE_CONTRACT.md`. That's a strong signal the plan should acknowledge pre-implementation rather than leaving to implementer judgment.
- **The Codex prior review gave MAJOR** due to retrieval failure (it couldn't access the plan). The plan's adversarial review summary shows "PENDING" for all three providers. The actual review artifacts exist but the plan hasn't been updated to incorporate them — this is a process gap.
- **No discussion of branch divergence.** Main has 3 commits ahead of the branch (`3f6ac3f5d`, `026cd30b2`, `2b0106fda`); the branch has 2 commits ahead of main. The plan doesn't address whether merge conflicts exist or how to handle them.

---

## 4. Risks

- **Empty implementation risk.** Without a minimum-viable output, the plan could land as pure documentation (keep/reject/defer decisions recorded, zero code changes). This would close the issue without capturing any learnings in executable form.
- **Self-referential test failure.** If the deleted-path scan is ported, it will find its own deleted-path fragments in the test file itself, in this plan document, and in the #2290 plan. The preserved branch test doesn't include any self-exclusion logic. Gemini flagged this; the plan doesn't address it.
- **Optional neighbor-skill update is a scope creep vector.** The "Optional update" row in Files to Change (`github-pr-workflow` or "another narrowly scoped neighboring skill") has no guard rail. If triggered, it pulls a third skill into scope without a separate issue.
- **The 480-line branch draft is ~68% boilerplate.** Quick inspection shows auth detection (~60 lines), PR creation/merge lifecycle (~80 lines), and CI monitoring (~50 lines) that duplicate `github-auth` and `github-pr-workflow` verbatim. Only ~150 lines are genuinely review-specific. The plan identifies this risk but doesn't pre-triage — the implementer will rediscover it.

---

## 5. Missing tests

| Missing test | Why it matters |
|---|---|
| **Mandatory minimum: at least one non-conditional test must exist** | All 5 TDD tests use "If accepted" — if nothing is accepted, no test runs. At minimum, `test_github_code_review_skill_remains_scope_bounded` should be unconditional since it guards an existing invariant. |
| `test_deleted_path_scan_excludes_self_and_historical_docs` | The preserved branch scan will match its own test file and plan documents. Without a whitelist/exclusion mechanism, this creates a CI loop. |
| `test_canonical_code_review_preserves_review_output_template_reference` | The `references/review-output-template.md` path is referenced at line 119 of the current canonical skill. Any merge must preserve this reference — should be unconditional. |
| `test_no_auth_or_lifecycle_content_imported` | Negative-scope test: verify `github-code-review` doesn't gain auth detection or PR merge content after any update. Guards against the primary skill-scope-sprawl risk. |

---

## 6. Scope creep concerns

- **The "Optional update" to neighbor skills** is explicitly concerning. The plan's own risk section names "hidden boundary decisions" as a risk, then creates the exact mechanism for that risk to manifest via the optional Files to Change row. Resolution: remove the optional row and replace with "create follow-up issue if content belongs elsewhere."
- **The acceptance criteria include "Review artifacts are posted"** — this is process overhead, not a functional deliverable. It's fine as a workflow step but shouldn't gate issue closure if the functional work is complete.
- **The plan touches 3 GitHub skills as context** (`code-review`, `pr-workflow`, `auth`). If the implementer reads all three and notices inconsistencies, the temptation to "fix while I'm here" is real. The plan should explicitly state: changes to `github-auth` and `github-pr-workflow` are out of scope under all circumstances.

---

## 7. Weakest assumption and what breaks if it is false

**Assumption:** The implementer will correctly distinguish "high-signal" from "low-signal" preserved content without defined criteria.

**What breaks:** Without criteria, the implementation becomes a subjective judgment call. If the implementer is aggressive, they port too much and create the overfitted-regression and scope-sprawl risks the plan warns about. If conservative, they reject everything and land an empty implementation. The plan has no mechanism to detect either failure mode because every test is conditional on what was accepted.

**Fix:** Pre-classify the two most obvious candidates before implementation:
1. The `TestReferenceSurfacesClean` class from the branch test → likely KEEP (it guards control-plane contract surfaces).
2. The auth/lifecycle boilerplate in the 480-line draft → likely REJECT (already owned by neighbor skills).

---

## 8. Most likely implementation failure mode

The implementer copies the 197-line branch test, runs it, hits self-referential failures (the test file contains the deleted-path strings it's searching for), spends time debugging exclusion logic, and ends up with a fragile allowlist that encodes incidental repo structure. Meanwhile the actual high-value work (deciding which preserved assertions to keep and which skill content to port) gets crowded out by test plumbing.

---

## 9. Most likely test gap

**Semantic preservation of the supplemental review checklist.** The current canonical `github-code-review` skill (lines 141–170) contains a "Supplemental Generic Review Checklist" that was merged from the former `software-development/code-review` path. No existing test or proposed test verifies this content survived. If a future skill update or merge accidentally drops this section, the regression test won't catch it because it only checks file existence and audit findings, not content.

---

## 10. Future issues suggested

- **GitHub skill-family boundary audit:** Formalize the boundary between `github-code-review`, `github-pr-workflow`, and `github-auth` — the current boundary is implicit and maintained only by convention.
- **Skill dedup semantic-preservation harness:** A reusable test pattern that verifies merged skill content, not just path existence — applicable to future dedup operations (#2019, #2083).
- **Control-plane deleted-path regression guard:** A generic test (not issue-specific) that scans adapter surfaces for references to any skill path that no longer exists on disk.

---

## 11. Review confidence

**High.** All context files read directly. Preserved branch content inspected via `git show` and `git diff`. Both prior review artifacts (Codex MAJOR, Gemini APPROVE) read and cross-referenced. The Codex MAJOR was caused by retrieval failure, not a substantive plan flaw — the plan itself is accessible and well-structured.

---

## 12. Retrieval adequacy: adequate

All referenced artifacts were accessible: the plan, the current regression test, the canonical and adjacent skills, the #2290 parent plan, the control-plane contract, the preserved branch content and diff stats, and both completed review artifacts. The only inaccessible artifact was the Claude review (empty file), which is a process gap but doesn't affect review adequacy.
