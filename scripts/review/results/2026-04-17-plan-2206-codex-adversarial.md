# Adversarial Review: #2206 Pyramid Conformance Checks Design

> **Reviewer:** Codex (cross-provider second opinion per planning-skill Step 3)
> **Date:** 2026-04-17
> **Transcribed by:** Claude — Codex's local sandbox (`bwrap`) blocked file writes; Codex pivoted to GitHub-connector reads against `vamseeachanta/workspace-hub` and produced a substantive review. Claude has spot-verified each load-bearing claim against the **local** working tree and noted where GitHub-connector evidence diverges from local reality.
> **Deliverable under review:** `docs/document-intelligence/pyramid-conformance-checks.md`
> **Sibling Claude review:** `scripts/review/results/2026-04-17-plan-2206-claude-adversarial.md`

## Stance declaration (Codex)

> "Adversarial stance applied. No praise. No restatement of the deliverable."

## Verdict: **MAJOR** — 6 findings (5 MAJOR, 1 MINOR), with 4 findings non-overlapping the Claude pass

---

## Codex Finding 1 — MAJOR: DT-1 false positives across multiple live wiki frontmatter shapes

**Claim under review:** `pyramid-conformance-checks.md` Section 5.4 DT-1 pass signal: "Every wiki page has `title`, `tags`, `sources`, `last_updated` in frontmatter"; Section 7.1 marks DT-1 as "Automatable (now)".

**Codex evidence (sampled across 4 wiki domains):**
- `knowledge/wikis/maritime-law/wiki/index.md:1-5` has frontmatter `{domain, created, last_updated, page_count}` — no `title`, no `tags`, no `sources`.
- `knowledge/wikis/naval-architecture/wiki/index.md:1-5` similar — `{domain, created, last_updated, page_count}`.
- `knowledge/wikis/maritime-law/wiki/entities/torrey-canyon-1967.md:1-6` uses `source` (singular), not `sources` (plural).
- `knowledge/wikis/marine-engineering/CLAUDE.md:26-33` declares `sources` as "recommended", not required.
- `knowledge/wikis/marine-engineering/CLAUDE.md:51-59` declares `index.md` schema explicitly without `title/tags/sources`.

**Why this is a defect:** Sampled repo pages already use at least three live frontmatter shapes (page pages with `sources`, page pages with singular `source`, auto-generated indexes with neither). A full DT-1 scan would emit large false-positive drift on the current corpus, so "automatable now" is not true.

**Required fix:** Split DT-1 into page-class-specific checks; at minimum exempt `wiki/index.md` files; accept the currently-shipped `source` variant or define and sequence a migration before enforcing DT-1.

**Claude verification:** Confirmed broader than my own #2206 Finding 1 (which only contrasted contract-vs-contract). Codex's sampling reveals the on-disk reality is even more fragmented — three live frontmatter shapes, not just two contracts disagreeing.

---

## Codex Finding 2 — MAJOR: DT-3 retention check assumes `.planning/` artifacts are issue-addressable; many are not

**Claim under review:** `pyramid-conformance-checks.md` Section 5.4 DT-3 fail signal: "`.planning/` file references an issue closed > 14 days ago"; Section 7.3 marks `.planning/` retention as "Automatable (partial)".

**Codex evidence:**
- `.planning/.continue-here.md:1-6` has frontmatter `{phase, task, total_tasks, status, last_updated}` — no issue identifier.
- `.planning/STATE.md:1-10` has frontmatter `{gsd_state_version, milestone, milestone_name, status, stopped_at, last_updated}` — no issue identifier.
- `.claude/hooks/plan-approval-gate.sh:4-8` documents that approval markers may be `.planning/plan-approved/<issue-number>.md` **OR** `.planning/plan-approved/session.md` — explicitly non-issue-bound.

**Why this is a defect:** DT-3 assumes `.planning` artifacts can be mapped to a single GitHub issue closure date. Live repo artifacts include state files and session-level markers that are not issue-addressable, so the proposed checker cannot deterministically compute retention without a new classification/metadata layer.

**Required fix:** Narrow DT-3 to only issue-addressable subtrees/files with a mandatory issue field; document non-issue `.planning` artifacts as out of scope or governed by a different retention rule.

**Claude verification:** Confirmed against the harness `plan-approval-gate.sh` text. This is the same operational ground-truth issue as Codex's #2209 Finding 2 (`.planning/` is heterogeneous), now applied to the conformance check rather than the policy.

---

## Codex Finding 3 — MAJOR: Section 11 item 10 runner contract is incompatible with both existing harness surfaces

**Claim under review:** `pyramid-conformance-checks.md` Section 11 item 10: "Recommend: each script exits 0 (pass) or 1 (fail) and emits a single-line JSON result."

**Codex evidence — two existing enforcement surfaces use incompatible contracts:**
- `.claude/hooks/plan-approval-gate.sh:97-106` (PreToolUse hook): blocks by printing JSON and exiting **0**:
  ```bash
  echo "[plan-gate] BLOCKED: ..." >&2
  printf '{"decision":"block","reason":"..."}\n'
  exit 0
  ```
- `scripts/enforcement/require-plan-approval.sh:1-4, 92-109` (pre-commit): blocks with **exit 1**:
  ```bash
  # Level 3 (hard enforcement) — exits 1 to block the commit
  ...
  if [[ "$STRICT_MODE" == "1" ]]; then
    ...
    exit 1
  ```

**Why this is a defect:** The repo already has two incompatible enforcement surfaces — JSON+exit-0 for tool interception, plain text+exit-1 for pre-commit blocking. A single 0/1 JSON contract fits neither cleanly. Without an adapter contract, any Phase 1/3 integration will either fail to block where intended or violate the existing hook protocol.

**Required fix:** Define two explicit integration modes in #2206: `hook-mode` (stdout JSON decision, exit 0) and `cli/pre-commit-mode` (text or JSON, exit 1 on fail). Do not describe them as one interchangeable runner contract.

**Claude verification:** Confirmed against both files. This goes deeper than my own #2206 Finding 7 (CF-3 timing mismatch); Codex identified a structural API incompatibility in addition to the philosophy mismatch.

---

## Codex Finding 4 — MAJOR (with caveat): ID-5 has a real cross-repo dependency the plan treats as local

**Claim under review:** `pyramid-conformance-checks.md` Section 5.2 ID-5 input: "`digitalmodel/` promoted modules"; Section 10 Phase 3.4 lists "Add promoted-artifact backlink check | ID-5 | ... | `digitalmodel/` repo access" as a local follow-on.

**Codex evidence:** GitHub fetch of `digitalmodel/README.md` returned 404 against `vamseeachanta/workspace-hub`.

**Claude correction (load-bearing):** `digitalmodel/` **does exist** in the local working tree at `/mnt/local-analysis/workspace-hub/digitalmodel/` AND is a separate git repository (has its own `.git/` directory). It is not git-tracked by `workspace-hub` (verified: `git ls-files digitalmodel/README.md` returns empty), but the directory and its `README.md` are present locally as a sibling repo checkout.

**Why this is a defect (corrected framing):** Codex's underlying defect claim still holds, but the evidence quality matters: `digitalmodel/` is a **separate git repository** that happens to share a parent directory. ID-5's check would need to operate across repo boundaries — read files from a separate git tree, depend on its checkout being present, depend on its branch state. The plan treats this as a normal local check; in reality it is a cross-repo dependency without a defined invocation contract.

**Required fix:** Move ID-5 out of the local Phase 3 sequence unless a concrete cross-repo execution contract is added: how `digitalmodel/` is checked out, which branch is canonical, what happens when the sibling repo is absent, and who owns failures found in `digitalmodel/`.

---

## Codex Finding 5 — MAJOR (with caveat): ACC-6 references stale or non-tracked navigation targets

**Claim under review:** `pyramid-conformance-checks.md` Section 5.5 ACC-6: "Verify all files referenced in the weekly accessibility checklist exist", marked "Automatable (now)", consuming "File paths from #2096 Section 7 checklist."

**Codex evidence:**
- `docs/document-intelligence/README.md:28-32` lists "Personal | [wiki/index.md](../../knowledge/wikis/personal/wiki/index.md) | ~5 pages".
- GitHub fetch of `knowledge/wikis/personal/wiki/index.md` returned 404.
- `docs/document-intelligence/README.md:33` lists "Cross-wiki references | [cross-links.md](../../knowledge/wikis/cross-links.md) | 25 links".
- `knowledge/wikis/cross-links.md:1-6` reports `total_cross_references: 15`.

**Claude correction (partial):** `knowledge/wikis/personal/wiki/index.md` **does exist** in the local working tree (39 lines, verified earlier in this session). Like `digitalmodel/`, it appears to be present locally but not git-tracked (`git ls-files` returned empty for it). Codex's GitHub-connector evidence missed this because the file isn't on the remote main branch.

**Why this is a defect (corrected framing):** The personal wiki index existing only as untracked local state is itself a defect — a navigation doc (`docs/document-intelligence/README.md`) advertises a path that resolves on the author's machine but not in the canonical repo. ACC-6 implemented against the remote/canonical state would correctly flag this as a missing target. The 15-vs-25 cross-link count drift in `cross-links.md` is the same class of defect (header text and content disagree).

**Required fix:** ACC-6 must be precise about whether it checks "files exist in working tree" (tolerates untracked) or "files are git-tracked" (catches the personal/wiki/index.md class of issue). The contract today doesn't say. Add a precondition that checklist-source navigation docs themselves must be refreshed/validated before ACC-6 runs, or scope ACC-6 to a curated tracked-only manifest.

---

## Codex Finding 6 — MINOR: DT-2 / DT-5 retention based on mtime is unstable

**Claim under review:** `pyramid-conformance-checks.md` Section 5.4 DT-2 ("modification date > 30 days ago") and DT-5 ("Review file with date > 90 days ago").

**Codex evidence:**
- `docs/handoffs/2026-04-10-claude-parallel-exit-handoff.md` content explicitly dated 2026-04-10; current mtime reports 2026-04-17 (rebased/resynced).
- `scripts/review/results/2026-04-02T132222Z-retroactive-review-codex.md` content explicitly dated 2026-04-02; current mtime reports 2026-04-17.

**Why this is a defect:** mtime-based retention can be reset by unrelated touches, rebases, or sync churn. The proposed checks would measure "last changed in git" rather than "age of the artifact event," making DT-2/DT-5 unstable even before they hit the policy/advisory problem (Claude #2206 Finding 3).

**Required fix:** Define retention against embedded artifact timestamps or filename dates, not repository modification time.

---

## Verified claims (Codex's confirmed checks)

- `docs/document-intelligence/README.md:19-22` does link parent + provenance + boundary + conformance docs in one architecture table.
- `docs/README.md` has a dedicated `## Knowledge & Intelligence Ecosystem` section linking the intelligence landing page, wikis, registries, and weekly review.
- `knowledge/wikis/engineering/CLAUDE.md:39` and `knowledge/wikis/marine-engineering/CLAUDE.md:97-99` reference the parent operating model — ACC-5 is directionally grounded.
- `data/document-index/resource-intelligence-maturity.yaml:1-5` exists and is machine-readable.

## Disagreements with Claude review (Codex)

> "I agree with Claude's overall MAJOR verdict, but not for the same reasons. Claude's DT-1 finding was a contract-level mismatch between #2206 and sibling docs; my Finding 1 is live-corpus evidence that the shipped wiki corpus already violates DT-1's proposed shape in multiple ways. Claude focused on identity namespace collisions and the advisory nature of retention. I found additional implementation blockers he did not call out: `.planning` artifacts that are not issue-addressable at all, a runner contract that does not match the current hook/pre-commit split, a missing `digitalmodel/` input surface in this repo, and stale checklist targets already referenced by the source navigation docs. I do not disagree with Claude's cross-provider-process complaint; I am adding defects that still stand even if that process gap were fixed."

## Coverage notes (Codex)

> "Sampled 9 wiki artifacts across engineering, marine-engineering, maritime-law, naval-architecture, and personal surfaces; read the deliverable, plan, four sibling context docs, prior Claude adversarial review, two existing enforcement scripts, one existing hook, two `.planning` artifacts, one handoff, one review-result artifact, and the current navigation index docs. Local shell/JS access was blocked by sandbox `bwrap` failures, so evidence collection used GitHub connector reads against `vamseeachanta/workspace-hub`. Residual risk remains around unsampled hook files, unsampled `.planning` subtrees, and full-corpus wiki drift rates beyond the sampled pages."

## Process notes (Claude)

- Codex's local sandbox failed; Codex pivoted to GitHub-connector reads. This produces evidence that reflects only `main` branch on the remote. Two findings (4 and 5) misread "not git-tracked but present locally" as "absent from repo." The underlying defects survive the corrections, but the evidence statements needed adjustment.
- Going forward, when Codex evidence cites file absence, treat it as "not on remote main" until verified locally. The `digitalmodel/` and `personal/wiki/index.md` cases both reflect the same systemic gap — local-only state masquerading as canonical.

## Combined #2206 finding totals (after both passes)

- Claude pass: 5 MAJOR + 3 MINOR
- Codex pass: 5 MAJOR + 1 MINOR (Findings 4 and 5 amended for evidence; defect claims preserved)
- **Total #2206: 10 MAJOR + 4 MINOR = 14 findings**
