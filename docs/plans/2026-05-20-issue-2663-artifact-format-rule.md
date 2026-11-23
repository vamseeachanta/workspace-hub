# Plan for #2663: chore(harness): adopt HTML as default artifact format — .claude/rules/artifact-format.md

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-05-20
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2663
> **Review artifacts:** scripts/review/results/2026-05-20-plan-2663-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- `.claude/rules/README.md` — lists 4 existing rule files (`coding-style.md`, `patterns.md`, `calc-citation-contract.md`, `goal-invocation.md`); `artifact-format.md` is NOT listed — gap confirmed.
- `.claude/rules/coding-style.md` — exemplar format: ~14 lines, H2 sections with bullet lists, no tables.
- `.claude/rules/patterns.md` — exemplar format: ~18 lines, uses markdown table, inline issue references.
- `config/agents/claude/SOUL.runtime.md` line 64 — must-fire rule already references this issue as the canonical tracker: "HTML default for rich artifacts … (`feedback_html_default_artifact`, [#2663])" — confirms this plan is the fulfilment path.

### Standards

Not applicable — governance rule file.

### LLM Wiki pages consulted

Not applicable.

### Documents consulted

- `.claude/memory/topics/feedback_html_default_artifact.md` — user decision verbatim (2026-05-11): "let us go with HTML going forward. during reruns, update to htmls". Defines: HTML trigger (human-facing, >100 lines or diagrams), Markdown trigger (agent-facing harness/skill/rule files), regeneration contract (overwrite-in-place + `<meta http-equiv="refresh" content="30">`), accepted tradeoffs (2–4× slower, noisy diffs, higher token cost), and explicit anti-pattern (do NOT create a `/html` skill — "the rule lives in `.claude/rules/artifact-format.md`").
- Issue [#2664](https://github.com/vamseeachanta/workspace-hub/issues/2664) — HTML PR explainer child issue filed in same batch. Confirms HTML-default is a policy, not a per-workflow feature.
- Issue #2663 body — defines 6 acceptance criteria, non-goals (no `/html` skill, no backfill PRs), and cross-references `feedback_html_refresh`, `frontend-design` plugin, and `playground` skill as related HTML surfaces.

### Gaps identified

- `.claude/rules/artifact-format.md` does NOT exist — confirmed via `ls .claude/rules/`.
- `.claude/rules/README.md` does not mention `artifact-format.md` — update needed.
- No test validates rule file properties (existence, line count, required strings).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-20 via GitHub MCP `issue_read`):
- `#2663` — OPEN — "chore(harness): adopt HTML as default artifact format — .claude/rules/artifact-format.md"
- `#2664` — (child, filed same batch) — referenced in issue body

**File existence** (`ls .claude/rules/` 2026-05-20):
- EXISTS: `.claude/rules/README.md`
- EXISTS: `.claude/rules/coding-style.md`
- EXISTS: `.claude/rules/patterns.md`
- EXISTS: `.claude/rules/calc-citation-contract.md`
- EXISTS: `.claude/rules/goal-invocation.md`
- MISSING (this plan creates): `.claude/rules/artifact-format.md`

**Line excerpts** — SOUL.runtime.md line 64:
```
- **HTML default for rich artifacts.** Human-facing plans, specs, reports, PR-explainers default to HTML;
  harness/skill/rule files stay Markdown. (`feedback_html_default_artifact`,
  [#2663](https://github.com/vamseeachanta/workspace-hub/issues/2663))
```

**Gap proof** (`ls .claude/rules/ | grep artifact-format` 2026-05-20):
```
(no output)
```
→ File does not exist; confirms gap.

**CLAUDE.md line count** (`wc -l CLAUDE.md` 2026-05-20):
```
14 CLAUDE.md
```
→ 14 lines; CLAUDE.md line 2 already references `.claude/rules/` generically; updating
  `.claude/rules/README.md` fulfils the cross-link acceptance criterion without touching CLAUDE.md.

**Reproduction proof:**
N/A — documentation/governance issue; no runtime failure to reproduce. Skip intentional.

<!-- Verification: distinct sources: (1) issue body, (2) .claude/rules/README.md, (3) feedback_html_default_artifact memory,
     (4) SOUL.runtime.md line 64, (5) coding-style.md + patterns.md format exemplars. Count: 5 ≥ 3. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-20-issue-2663-artifact-format-rule.md` |
| New rule file | `.claude/rules/artifact-format.md` |
| Updated README | `.claude/rules/README.md` |
| Tests | `tests/enforcement/test_artifact_format_rule.py` |
| Plan review — Claude | `scripts/review/results/2026-05-20-plan-2663-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-20-plan-2663-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-20-plan-2663-gemini.md` |

---

## Deliverable

A new `.claude/rules/artifact-format.md` rule file that codifies the HTML-default-for-rich-artifacts policy with triggers, tradeoffs, and explicit anti-patterns, making the `feedback_html_default_artifact` memory node enforceable as a universal constraint discoverable at session start.

---

## Pseudocode

Trivial — see Files to Change. Rule file is prose with one optional decision table; no logic.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `.claude/rules/artifact-format.md` | New rule: HTML-default policy, triggers, tradeoffs, anti-pattern |
| Modify | `.claude/rules/README.md` | Add `artifact-format.md` line to the Files list |
| Create | `tests/enforcement/test_artifact_format_rule.py` | TDD: validate file properties before and after implementation |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_artifact_format_rule_file_exists` | Rule file was created at the correct path | Path check | File exists |
| `test_artifact_format_rule_under_80_lines` | File stays within prose-rule length budget | Line count | `< 80` |
| `test_artifact_format_rule_readme_lists_it` | README updated with new rule | `.claude/rules/README.md` content | Contains `artifact-format.md` |
| `test_artifact_format_rule_no_html_skill_warning` | Anti-pattern explicitly documented | Rule file content | Contains "do NOT create" or "don't make" adjacent to "skill" |
| `test_artifact_format_rule_tradeoffs_documented` | Accepted tradeoffs are present | Rule file content | Contains both "token" and ("slower" or "diff") |

---

## Acceptance Criteria

- [ ] `.claude/rules/artifact-format.md` exists, < 80 lines, and matches the style of `coding-style.md` / `patterns.md`
- [ ] `.claude/rules/README.md` lists `artifact-format.md` in the Files section
- [ ] Rule references the article anti-pattern ("don't make a /html skill") attributed to Thariq Shihipar / issue #2663
- [ ] Rule documents accepted tradeoffs: 2–4× slower generation, noisy diffs, higher token cost
- [ ] No new skill files are created (intentional non-goal)
- [ ] No backfill PRs of existing Markdown → HTML (intentional non-goal)
- [ ] All TDD tests pass: `uv run pytest tests/enforcement/test_artifact_format_rule.py -v`
- [ ] No regression: `uv run pytest tests/enforcement/ -v` passes

---

## Adversarial Review Summary

<!-- Filled in after Step 4 completes. Do not post to GitHub until this section is populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | (pending) | — |
| Codex | (pending) | — |
| Gemini | (pending) | — |

**Overall result:** (pending adversarial review)

Revisions made based on review:
- (none yet)

---

## Risks and Open Questions

- **Risk:** Rule file could be mistakenly placed in a harness file (CLAUDE.md, AGENTS.md) which has a 20-line limit. Mitigated: target is `.claude/rules/artifact-format.md`, which has no line limit per `coding-style.md` constraints.
- **Risk:** `SOUL.runtime.md` is a generated artifact (`build-soul-runtime.sh`); the must-fire rule on line 64 already references #2663. After this plan lands, no change to SOUL.runtime.md is needed — the rule file's existence IS the closure, not an edit to the generated file.
- **Open:** Should `artifact-format.md` cross-reference `frontend-design` plugin and `playground` skill (both produce HTML)? Issue body says yes — include brief cross-reference so agents don't re-derive the HTML pattern from scratch.

---

## Complexity: T1

**T1** — creates one new rule file and updates one README list entry. No logic, no cross-repo dependencies, no runtime state. Pure documentation/governance artifact.
