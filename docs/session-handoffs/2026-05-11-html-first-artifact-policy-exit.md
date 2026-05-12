# Session handoff — HTML-first artifact policy + cadence-trigger inspiration

**Date:** 2026-05-11
**Operator:** Vamsee Achanta
**Session goal:** review two external articles, distill working-style improvements, route to GitHub issues per `extract-learnings-to-issues` skill
**Outcome:** 4 issue comments + 2 new issues + 2 memory files. No code changes.

## Sources reviewed

| Source | Status | Take-away |
|---|---|---|
| [X article — Thariq Shihipar / @trq212](https://x.com/trq212/status/2053632475294400084) "Using Claude Code: The Unreasonable Effectiveness of HTML" | Login-gated; user pasted full content into session | Default rich human-facing artifacts to HTML; do NOT make a `/html` skill |
| [YouTube — Goldie](https://www.youtube.com/watch?v=nN_CV3620m8) "Hermes AI Agent + Obsidian + Omi is Insane (FREE!)" | Title-only via og:meta; thesis recovered via web search | Cadence-triggered self-improvement: 10 user turns / 15 tool iters / 2-day idle → 4AM batch |

> ⚠️ The video's "Hermes" is **not** the workspace-hub orchestrator (`project_hermes_installation`). Two unrelated tools sharing a name.

## Artifacts produced

### New issues

- **[#2663](https://github.com/vamseeachanta/workspace-hub/issues/2663)** — `chore(harness): adopt HTML as default artifact format — .claude/rules/artifact-format.md` (parent rule)
- **[#2664](https://github.com/vamseeachanta/workspace-hub/issues/2664)** — `feat(workflow): HTML PR explainer artifact (author-side)` (first concrete use case; child of #2663)

### Comments on existing issues

| Issue | Theme contributed |
|---|---|
| [#2154](https://github.com/vamseeachanta/workspace-hub/issues/2154#issuecomment-4427037438) | SVG diagrams, share-link surface, auto-refresh tag, tradeoffs for HTML report renderer |
| [#2432](https://github.com/vamseeachanta/workspace-hub/issues/2432#issuecomment-4427037819) | Persist design-system HTML at stable path so it compounds across future generations |
| [#2235](https://github.com/vamseeachanta/workspace-hub/issues/2235#issuecomment-4427038086) | `artifacts:` metadata block in plan template — `html_companion:` when >100 lines or diagrams |
| [#2549](https://github.com/vamseeachanta/workspace-hub/issues/2549#issuecomment-4427038313) | Add non-time-based cadence triggers (activity / mission-change / idle-batch) to Business Brain refresh |

### Memory files (new)

- `feedback_html_default_artifact.md` — durable decision with verbatim user quote
- `reference_thariq_html_article.md` — article URL + examples gallery
- `MEMORY.md` index updated with both entries

## Decisions captured

1. **User decision (2026-05-11) verbatim:** *"let us go with HTML going forward. during reruns, update to htmls"* — recorded in `feedback_html_default_artifact.md`. Ambiguity flagged: phrase could mean (a) overwrite-in-place during regeneration, or (b) backfill existing markdown when next touched. **Current interpretation in #2663:** (a) — organic adoption only, no forced backfill. If user later signals (b), update the rule and memory.
2. **PR-explainer scope split:** author-side (#2664) first; reviewer-side deferred until first artifact lands.
3. **No `/html` skill** — explicit per article author and codified in #2663 acceptance criteria.

## Deliberate non-actions

- No `frontend-design` plugin or `playground` skill modifications (plugin cache is not editable from workspace-hub per `feedback_plugin_cache_not_repo_tracked.md`)
- No `.claude/rules/artifact-format.md` written yet — that lands as the deliverable of #2663, not in this session
- No PR explainer trial artifact generated — that lands as the deliverable of #2664
- No backfill PRs converting existing Markdown to HTML

## Suggested next-session actions (not committed)

1. Pick up #2663 — draft `.claude/rules/artifact-format.md` (<80 lines, matches style of `coding-style.md` / `patterns.md`). Add a one-line pointer from `CLAUDE.md` and update `.claude/rules/README.md` Files line. **Plan-review gate applies** — do not self-approve.
2. Pick up #2664 — pick the next harness-touching PR and generate a trial explainer to validate the artifact contract before writing `docs/pr-explainers/README.md`.
3. If user clarifies the "during reruns" ambiguity → update `feedback_html_default_artifact.md` and #2663's "Non-goals" section.
4. Consider whether the `frontend-design` plugin and `playground` skill should be cross-referenced from `.claude/rules/artifact-format.md` once it lands (they pre-date this rule and already produce HTML; rule should claim them, not duplicate them).

## Ground-truth checks for next session

Run these before trusting the session record:

```bash
gh issue view 2663 --json state,title              # expect: OPEN, "chore(harness): adopt HTML as default artifact format..."
gh issue view 2664 --json state,title              # expect: OPEN, "feat(workflow): HTML PR explainer artifact (author-side)..."
gh issue list --search "is:open author:@me created:2026-05-11" --json number,title | head
test -f /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_html_default_artifact.md
test -f /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/reference_thariq_html_article.md
grep -F 'HTML default for rich artifacts' /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md
test -f /mnt/local-analysis/workspace-hub/.claude/rules/artifact-format.md   # expect: FAILS — file not yet created, that's #2663's deliverable
```

## References

- Skill used: `extract-learnings-to-issues` — route first, create last
- Related memory: `feedback_html_refresh`, `feedback_inline_gh_issue_url`, `feedback_parallel_gh_issue_create_reverses_numbers`, `feedback_plugin_cache_not_repo_tracked`, `feedback_never_offer_to_self_label_plan_approved`
- Related project memory: `project_hermes_installation` (the *workspace-hub* Hermes — disambiguates from the YouTube Hermes), `project_claude_design_adoption`
