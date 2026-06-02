# Plan for #2945: Repo-ecosystem flywheel for reusable skills, scripts, and tools

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-06-02
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2945
> **Client:** N/A
> **Project:** N/A
> **Review artifacts:** attempted — `scripts/review/results/2026-06-02-plan-2945-claude.md` | `scripts/review/results/2026-06-02-plan-2945-codex.md` | `scripts/review/results/2026-06-02-plan-2945-gemini.md`

---

## Resource Intelligence Summary

### Existing repo code

- Found: `.claude/skills/coordination/issue-planning-mode/SKILL.md` — canonical planning gate, review gate, approval gate, and no-self-approval rules.
- Found: `.claude/skills/coordination/pre-completion-cleanup-audit/SKILL.md` — required closeout hygiene audit and residue classification.
- Found: `.claude/skills/coordination/provider-session-learning-transfer/SKILL.md`, `.claude/skills/coordination/comprehensive-learning-wrapper/SKILL.md`, `.claude/skills/workspace-hub/comprehensive-learning/SKILL.md`, `.claude/skills/coordination/cross-agent-skill-audit/SKILL.md`, `.claude/skills/coordination/skill-ecosystem-curation/SKILL.md`, `.claude/skills/extract-learnings-to-issues/SKILL.md`, and `.claude/skills/devops/agent-learnings-portability/SKILL.md` — adjacent learning/skill promotion assets already exist, but they are not currently bound into a required closeout flywheel for repo waves.
- Found: `scripts/learning/comprehensive-learning.sh`, `scripts/learnings/extract-learnings.sh`, `scripts/hooks/post-commit-learnings.sh`, `scripts/enforcement/correction-to-skill-candidates.sh`, `scripts/analysis/provider_session_ecosystem_audit.py`, `scripts/cron/provider-session-ecosystem-audit.sh`, `scripts/skills/weekly_skills_audit.py`, and `scripts/skills/validate-skills.sh` — existing learning/skill audit scripts that should be reused or wrapped rather than duplicated.
- Found: `scripts/review/plan-review-fanout.sh` — existing cross-provider adversarial plan-review automation and artifact convention.
- Found: `scripts/workflow/completeness_score.py` — existing closeout score gate; useful precedent for evidence-linked completion records.
- Found: `config/workflow-tips/tips-catalog.yaml` — existing ecosystem hints include skill improvement, subagent use, and auto-improvement tips.
- Found: `docs/governance/2026-04-25-cradle-to-grave-engineering-flywheel-design.md`, `docs/architecture/report-derived-learning-routing.md`, and `docs/document-intelligence/promotion-feedback-loop.md` — flywheel and report-derived-learning routing precedents.
- Gap: no operator-invoked wave-closeout workflow/skill/script explicitly enforces `work -> learning -> durable asset -> stronger next work` across repo ecosystem waves.

### Standards

Not applicable — this is agent workflow and repo-ecosystem tooling, not an engineering calculation or standards interpretation issue.

### LLM Wiki pages consulted

- `llm-wiki` issues #259 and #260 were consulted as the immediate canary. They define the local dispatch cockpit and learning-to-tools loop that #2945 should generalize.

### Documents consulted

- Issue #2945 — defines the ecosystem-wide flywheel, candidate assets, acceptance criteria, non-goals, and first recommended `llm-wiki` canary.
- `docs/plans/README.md` — defines the workspace-hub plan index and issue planning workflow.
- `docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md` — identifies skills and scripts as core workspace-hub capabilities.
- `docs/vision/VISION.md` — frames workspace-hub as central orchestration, skills, learning pipeline, and cross-repo synchronization infrastructure.
- `docs/work-queue-workflow.md` — describes current work-queue workflow context and legacy helper gaps.

### Gaps identified

- Existing learning/skill assets are fragmented by use case; no closeout skill requires evidence-linked learning promotion after significant waves.
- Current learning scripts are commit/session/nightly oriented; no operator-invoked script scans a specific wave's issues, PRs, commits, handoffs, and review artifacts to propose durable improvements with evidence links.
- No standard routing rule decides when a learning belongs in the local repo versus workspace-hub.
- No issue template exists specifically for promoted learnings with source evidence, asset class, acceptance criteria, and verification path.
- No lightweight enforcement/audit hook detects missing flywheel evidence at closeout.

### Evidence

**Issue statuses** (verified 2026-06-02 via `gh issue view`):

```text
#2945 — OPEN — [flywheel] Generalize repo-ecosystem work into reusable skills/scripts/tools after every agent wave
llm-wiki#259 — OPEN — [flywheel] Build Friday-demo dispatch cockpit for llm-wiki Codex/subagent push
llm-wiki#260 — OPEN — [flywheel] Convert verification and ingest learnings into reusable llm-wiki skills/scripts/tools
```

**Existing asset search** (verified 2026-06-02 with `find .claude/skills ...` and `rg`):

```text
EXISTS: .claude/skills/coordination/issue-planning-mode/SKILL.md
EXISTS: .claude/skills/coordination/pre-completion-cleanup-audit/SKILL.md
EXISTS: .claude/skills/coordination/provider-session-learning-transfer/SKILL.md
EXISTS: .claude/skills/coordination/comprehensive-learning-wrapper/SKILL.md
EXISTS: .claude/skills/extract-learnings-to-issues/SKILL.md
EXISTS: scripts/review/plan-review-fanout.sh
EXISTS: scripts/learning/comprehensive-learning.sh
EXISTS: scripts/learnings/extract-learnings.sh
EXISTS: scripts/hooks/post-commit-learnings.sh
EXISTS: scripts/enforcement/correction-to-skill-candidates.sh
EXISTS: docs/governance/2026-04-25-cradle-to-grave-engineering-flywheel-design.md
EXISTS: docs/architecture/report-derived-learning-routing.md
EXISTS: scripts/workflow/completeness_score.py
MISSING: .claude/skills/coordination/flywheel-closeout/SKILL.md
MISSING: scripts/workflow/flywheel_closeout.py
MISSING: scripts/workflow/tests/test_flywheel_closeout.py
```

**Workspace state note**:

`workspace-hub` had substantial pre-existing dirty state before this plan was drafted. This plan must be committed with a narrow pathspec if advanced later; do not sweep unrelated provider reports, memory snapshots, or logs.

**Live canary update — 2026-06-02:**

```text
llm-wiki#259 — status:plan-review — dispatch cockpit plan reviewed and pushed in llm-wiki commit 43d4ceb3
llm-wiki#260 — status:plan-review — learning-to-tools plan reviewed and pushed in llm-wiki commit 43d4ceb3
workspace-hub#2502 — OPEN — review artifact metadata/stale-SHA issue received the llm-wiki privacy-artifact canary comment
```

The canary exposed one ecosystem-level finding that #2945 should route rather than re-solve inline: plan-review artifacts need a publishability contract that distinguishes provider stdout, synthesis output, and stderr/error logs, and that fails closed on empty, stale, or privacy-contaminated artifacts. That finding was added to #2502 as canary evidence.

**Reproduction proofs:**

N/A — this is governance/tooling creation work and does not allege a runtime failure. The gap was verified by searching for existing flywheel/learning/closeout assets and comparing them against the explicit issue #2945 contract.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-06-02-issue-2945-repo-ecosystem-flywheel.md` |
| Plan index | `docs/plans/README.md` |
| Coordination skill | `.claude/skills/coordination/flywheel-closeout/SKILL.md` |
| Extraction script | `scripts/workflow/flywheel_closeout.py` |
| Tests | `scripts/workflow/tests/test_flywheel_closeout.py` |
| Issue template | `docs/templates/flywheel-learning-issue.md` |
| Example report | `docs/reports/flywheel/llm-wiki-2026-06-02-canary.html` |
| Plan review — Claude | `scripts/review/results/2026-06-02-plan-2945-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-06-02-plan-2945-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-06-02-plan-2945-gemini.md` |

---

## Deliverable

A workspace-hub flywheel closeout workflow will help substantial agent waves capture evidence-linked learnings, classify durable improvement routes, and propose reusable skill/script/rule/issue artifacts without bypassing existing planning gates or duplicating the nightly comprehensive-learning pipeline. The first slice is advisory/report-only.

## First Slice Boundary

The first implementation slice will be advisory/report-only and will not add hard-blocking closeout enforcement. It will add a script-backed workflow plus skill wrapper that accepts explicit source inputs.

Example canary command:

```bash
uv run --no-project python scripts/workflow/flywheel_closeout.py \
  --repo vamseeachanta/llm-wiki \
  --source-issue vamseeachanta/workspace-hub#2945 \
  --issue 135 --issue 226 --issue 227 --issue 259 --issue 260 \
  --pr-range 176-258 \
  --artifact scripts/review/results/2026-06-02-plan-259-disagreement.md \
  --artifact scripts/review/results/2026-06-02-plan-260-disagreement.md \
  --fixture scripts/workflow/tests/fixtures/flywheel_llm_wiki_canary.yaml \
  --out-dir docs/reports/flywheel/llm-wiki-2026-06-02-canary \
  --format html,json,issue-drafts \
  --mode propose
```

The script will not run `/insights`, `/reflect`, `/knowledge`, `/improve`, or the nightly comprehensive-learning pipeline during an active session. It may read existing learning outputs, correction candidates, issue/PR metadata, handoffs, and explicitly provided review artifacts. Any new extraction logic will be limited to normalizing the named wave sources into a manifest and report.

The `llm-wiki` canary will be represented in tests through fixtures for #135/#226/#227/#259/#260 and PRs #176-#258, not hard-coded live GitHub behavior.

---

## Pseudocode

```text
function collect_sources(repo, issue_numbers, pr_range, artifact_paths):
    read issue bodies/comments through gh or fixture JSON
    read PR titles/bodies through gh or fixture JSON
    read local review artifacts and handoffs from explicit paths
    normalize to SourceRecord(kind, repo, locator, text, timestamp)

function validate_publishability(record):
    classify provider stdout, synthesis output, and stderr/error logs separately
    reject empty, stale, private-path-bearing, or unredacted records as non-publishable
    retain non-publishable records only as local evidence with a reason code

function identify_learnings(records):
    detect evidence-backed findings from phrases like found, fixed, blocker, lesson, risk
    require at least one locator: issue URL, PR URL, commit SHA, or file path
    classify candidate severity and recurrence
    discard source-less or purely speculative items

function route_learning(candidate):
    if it changes local repo behavior, route to local repo issue
    if it changes skills/rules/shared scripts/provider workflow, route to workspace-hub
    if it is high-risk/security/legal, route to rule/check issue
    attach asset_class: skill, script, rule_check, prompt_template, docs, issue

function route_review_artifact_contract(candidate):
    if candidate concerns review artifact metadata, stale SHA handling, stderr/stdout separation, or privacy/publishability:
        route to existing workspace-hub #2502
        emit a comment/draft update, not a duplicate issue

function render_flywheel_closeout(candidates):
    write HTML/Markdown report
    write JSON manifest
    write issue-draft markdown files
    include only publishable records in committed reports
    include non-publishable evidence as redacted reason codes, not raw text
    include no-self-approval warning and implementation gate state

function skill_checklist():
    at closeout, advisory-check for source evidence, classification, routing, asset/draft creation, and verification
    warn and produce follow-up drafts in the first slice; do not hard-block closeout until a later approved enforcement issue adds that behavior
```

---

## Script and Skill Contract

The first slice will implement `scripts/workflow/flywheel_closeout.py` as a generic dry-run/proposal generator. The `flywheel-closeout` skill will call this script and will not reimplement extraction logic.

Required CLI:

```bash
uv run --no-project python scripts/workflow/flywheel_closeout.py \
  --repo OWNER/REPO \
  --source-issue OWNER/REPO#N \
  --issue N --issue N \
  --pr-range START-END \
  --artifact PATH --artifact PATH \
  --fixture PATH \
  --out-dir docs/reports/flywheel/<wave-id>/ \
  --format html,json,issue-drafts \
  --mode propose
```

CLI rules:

- `--repo` is the source repository for repo-local routing decisions.
- `--source-issue` is the fully qualified parent flywheel issue or wave anchor. It must include the owning repo so cross-repo waves do not infer the source issue from `--repo`.
- `--issue`, `--pr-range`, and `--artifact` are repeatable source selectors.
- `--fixture` loads deterministic JSON/YAML `SourceRecord` fixtures and bypasses live `gh` reads for tests.
- `--out-dir` receives the HTML report, JSON manifest, and issue-draft markdown files.
- `--mode propose` is the default and the only first-slice mode.
- The first slice must not call `gh issue create`, `gh issue comment`, or mutate labels. Any GitHub write path is out of scope unless a later approved issue adds an explicit `--apply` mode with user-approval evidence.

Fixture schema:

```yaml
sources:
  - kind: issue|pr|commit|review_artifact|handoff
    repo: OWNER/REPO
    locator: URL-or-path-or-sha
    title: string
    text: string
    timestamp: ISO-8601-string
existing_issues:
  - repo: OWNER/REPO
    number: 2502
    title: string
    state: OPEN
    labels: []
```

Output contract:

- `manifest.json` lists source records, candidates, routes, evidence locators, duplicate/suppression decisions, and proposed issue/comment draft paths.
- `report.html` is the human-facing report.
- `issue-drafts/*.md` are proposed issue bodies or proposed comments to existing issues.
- Exit `0` means report generated, including any first-slice advisory warnings. Advisory warnings such as missing flywheel evidence are recorded in `manifest.json` and `report.html`, not expressed as a failing process status. Exit `2` means invalid input/schema/parser failure.

Existing comprehensive-learning scripts remain upstream/adjacent sources, not code duplicated into this first slice. The closeout script may read their reports or invoke documented read-only summary commands when fixtures request them, but heavyweight nightly learning, memory writes, and provider-session transfer remain out of scope for #2945's first implementation.

Existing-issue routing for #2502 will use a deterministic matcher: normalize candidate title/body terms for `review artifact`, `stale SHA`, `metadata`, `privacy`, `publishability`, and `stderr`; search provided `existing_issues` fixtures first, then optional live GitHub read mode; if an open workspace-hub issue matches #2502, emit a proposed comment draft under `issue-drafts/workspace-hub-2502-comment.md` and mark `suppressed_duplicate_issue=true` in `manifest.json`.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `.claude/skills/coordination/flywheel-closeout/SKILL.md` | Define the required closeout workflow and routing checklist. |
| Create | `scripts/workflow/flywheel_closeout.py` | Provide an operator-invoked, deterministic adapter/report generator for a named wave; normalize explicit sources and existing learning outputs without duplicating the nightly/session learning pipeline. |
| Create | `scripts/workflow/tests/test_flywheel_closeout.py` | TDD coverage for extraction, classification, routing, dedup, and rendering. |
| Create | `docs/templates/flywheel-learning-issue.md` | Standard issue body template for promoted learnings. |
| Create | `docs/reports/flywheel/llm-wiki-2026-06-02-canary.html` | Demonstrate the workflow using `llm-wiki` #135/#226/#227 and #259/#260. |
| Update | `docs/plans/README.md` | Add this plan to the plan index. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_requires_evidence_locator` | Learning candidates without issue/PR/path evidence are rejected. | Candidate text with no locator. | No emitted candidate. |
| `test_routes_local_repo_script_to_source_repo` | Local repo behavior changes route to the source repo. | `llm-wiki` verification selector lesson. | Route `repo=vamseeachanta/llm-wiki`, asset `script`. |
| `test_routes_shared_skill_to_workspace_hub` | Shared workflow/skill changes route to workspace-hub. | Cross-provider closeout lesson. | Route `repo=vamseeachanta/workspace-hub`, asset `skill`. |
| `test_dedupes_repeated_findings` | Same defect class across multiple PRs becomes one candidate with multiple evidence links. | Three review artifacts with same failure class. | One candidate, three sources. |
| `test_renders_issue_template` | Issue draft includes parent/source, what-to-build, acceptance criteria, and blocked-by. | Candidate fixture. | Markdown body with required sections. |
| `test_preserves_planning_gate_language` | Generated closeout never labels implementation as approved. | Draft issue candidate. | Output says plan/review/user approval required. |
| `test_canary_report_includes_llm_wiki_examples` | Canary report contains #259/#260 and examples from #135/#226/#227. | Fixture source records. | HTML report includes linked examples. |
| `test_routes_review_artifact_contract_to_existing_workspace_issue` | Generalizable review-artifact privacy/staleness findings route to existing workspace-hub work instead of duplicate issues. | `llm-wiki` #259/#260 canary finding plus open workspace-hub #2502 fixture. | Candidate links to #2502 and emits a comment/draft update, not a duplicate issue. |
| `test_rejects_private_or_empty_review_artifacts_as_non_publishable` | Provider artifacts with private paths, empty content, stderr-only failure text, or stale metadata are not committed into reports as evidence. | Review artifact fixtures for private path, empty file, stale SHA, stderr log, and clean provider stdout. | Manifest marks bad artifacts `publishable=false` with reason codes; HTML omits raw private/stderr text. |
| `test_first_slice_is_advisory_not_blocking` | Missing flywheel evidence warns without failing closeout in the first slice. | Candidate set with missing flywheel evidence. | Exit code is `0`; manifest/report mark the warning as advisory-only and link follow-up work. |
| `test_cli_accepts_explicit_wave_sources_without_running_nightly_pipeline` | The script uses explicit issue/PR/artifact fixtures and does not invoke comprehensive-learning phases. | Fixture command arguments plus monkeypatched subprocess runner. | Sources are collected; no `/insights`, `/reflect`, `/knowledge`, `/improve`, or `comprehensive-learning.sh` call occurs. |
| `test_cli_accepts_generic_repo_issue_pr_artifact_inputs` | CLI accepts generic source selectors without hard-coded `llm-wiki` behavior. | Fixture with arbitrary `OWNER/REPO`, issue ids, PR range, and artifact path. | Manifest source records preserve the provided repo and locators. |
| `test_fixture_mode_bypasses_live_github_reads` | Canary tests are deterministic and do not depend on live `gh` output. | `--fixture tests/fixtures/flywheel_llm_wiki_canary.yaml`. | Script produces the same manifest without invoking GitHub writes. |
| `test_propose_mode_never_writes_to_github` | First-slice issue routing is draft/propose-only. | Candidate that would become a new issue plus candidate routed to #2502. | Issue draft/comment draft files are written; no `gh issue create`, `gh issue comment`, or label mutation is attempted. |
| `test_review_artifact_matcher_suppresses_duplicate_2502_issue` | Existing-issue routing is deterministic for the llm-wiki review-artifact canary. | Existing open #2502 fixture plus candidate terms for review artifact metadata, stale SHA, privacy, publishability, and stderr. | Manifest sets `suppressed_duplicate_issue=true` and writes `issue-drafts/workspace-hub-2502-comment.md`. |

---

## Acceptance Criteria

- [ ] A `flywheel-closeout` coordination skill defines capture, classify, promote, verify, and link steps.
- [ ] A deterministic script or documented command extracts candidate learnings from issues, PRs, commits, handoffs, and review artifacts.
- [ ] The script exposes the generic CLI contract above and supports fixture-driven tests without hard-coded `llm-wiki` behavior.
- [ ] First-slice operation is propose-only: generated output may include issue/comment draft files, but no GitHub issue creation, issue comments, or label mutations occur.
- [ ] The script reuses or documents interaction with existing comprehensive-learning and learnings scripts rather than duplicating nightly/session pipelines.
- [ ] The first slice has a pinned CLI contract and fixture-backed `llm-wiki` canary scope for #135/#226/#227/#259/#260 and PRs #176-#258.
- [ ] The script does not invoke heavyweight comprehensive-learning phases during active sessions; it only reads existing outputs or explicit fixtures/artifacts.
- [ ] Candidates are classified as `skill`, `script`, `rule/check`, `prompt/template`, `docs`, or `issue`.
- [ ] Routing guidance distinguishes repo-local implementation issues from workspace-hub ecosystem issues.
- [ ] The `llm-wiki` canary examples include #259/#260 and source evidence from #135/#226/#227.
- [ ] The `llm-wiki` canary examples include the #259/#260 `status:plan-review` outcome and route the review-artifact publishability finding to #2502 rather than creating duplicate workspace-hub work.
- [ ] Review artifacts are classified by publishability before citation or report rendering; empty, stale, stderr-only, or private-path-bearing artifacts are non-publishable and redacted.
- [ ] Every promoted learning requires evidence links; source-less memory claims are rejected.
- [ ] Missing flywheel evidence is advisory in the first slice; generated reports should warn and route follow-up work, not hard-block closeout, until the `llm-wiki` canary proves value.
- [ ] Tests cover extraction, dedup, routing, issue-draft rendering, and gate language.
- [ ] Existing gates remain intact: issue planning, adversarial review, user approval, TDD for code, and cleanup audit.

---

## Adversarial Review Summary

Adversarial review was refreshed on 2026-06-02 after the first-slice boundary, generic CLI/fixture contract, propose-only issue behavior, publishability validator, #2502 routing, comprehensive-learning reuse boundary, fully qualified source issue, and advisory exit semantics were added.

| Provider | Verdict | Key findings |
|---|---|---|
| Codex subagent r1 | MAJOR, patched | Required pinned CLI contract, propose-only/no GitHub writes, advisory wording, comprehensive-learning reuse boundary, and deterministic #2502 routing. |
| Codex subagent r2 | MAJOR, patched | Required first-slice boundary, review-artifact publishability tests, advisory-only language, and bounded adapter scope. |
| Codex subagent r3 | MAJOR, patched | Required fully qualified cross-repo `--source-issue` and advisory warnings to exit `0`. Reviewer stated remaining fixture/propose-only/publishability/#2502/reuse sections were sufficient. |

**Overall result:** Ready for `status:plan-review`; not implementation-approved. Implementation remains blocked until explicit user approval moves the issue to `status:plan-approved`.

---

## Risks and Open Questions

- **Risk:** This could duplicate existing learning skills and scripts. Mitigation: the new skill should wrap/reference existing comprehensive-learning, extraction, and skill-audit assets rather than replacing them.
- **Risk:** Over-enforcement could make tiny issues noisy. Mitigation: scope flywheel requirement to substantial waves, repeated defect classes, or explicit user requests.
- **Risk:** Automatic issue creation can spam trackers. Mitigation: default to issue drafts; require explicit flag or user approval to create issues.
- **Risk:** Blocking enforcement before the canary proves useful could slow urgent work. Mitigation: first slice should be advisory/reporting plus skill wrapper; hard blocking enforcement should be a follow-on issue unless the user explicitly approves it.
- **Risk:** The current workspace-hub worktree is dirty with unrelated generated/provider state. Mitigation: later commits must use pathspec serialization and avoid sweep commits.
- **User decision recorded 2026-06-02:** Missing flywheel evidence should be advisory in the first slice until the `llm-wiki` canary proves value.
- **Planning decision recorded 2026-06-02:** The first implemented asset should be a script-backed workflow plus skill wrapper, not a skill-only checklist.
- **Planning decision recorded 2026-06-02:** The first implementation should accept generic CLI inputs, with the `llm-wiki` #135/#226/#227 canary represented as fixtures rather than hard-coded behavior.
- **Gate reminder:** This plan may move to `status:plan-review`, but implementation remains blocked until user approval moves the issue to `status:plan-approved`.

---

## Complexity: T3

T2 first slice, T3 overall. The recommended initial implementation is T2: script-backed workflow plus skill wrapper and canary fixtures, with hard enforcement deferred. The broader issue remains T3 because it can affect closeout policy across the ecosystem.
