> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_superpowers_specs_gitignored.md

---
name: superpowers/specs path is gitignored
description: workspace-hub `.gitignore` line 438 silently drops anything written to `docs/superpowers/specs/`; brainstorming skill's default spec path never persists
type: feedback
originSessionId: 85425ab4-4551-420c-b5c2-2f93ef0a457a
---
The `superpowers:brainstorming` skill defaults to writing the validated design to `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`. In `vamseeachanta/workspace-hub` that directory is gitignored (`.gitignore:438` matches `specs/`), so any spec written there is local-only — invisible to git, won't be on remote, won't be reviewable, won't survive a fresh clone.

**Why:** discovered 2026-04-25 during cradle-to-grave engineering flywheel brainstorm — written design spec + decision panel were both invisible to `git status` because the path was silently dropped. Caught at commit time when staging produced an empty diff for those paths. The brainstorming skill is upstream and treats `docs/superpowers/specs/` as the canonical location, but workspace-hub gitignore policy treats it as throwaway scratch.

**How to apply:**
- For workspace-hub: write durable design specs / governance artifacts to `docs/governance/` instead. Existing siblings there: `llm-wiki-to-gtm-boundary.md`, `SESSION-GOVERNANCE.md`, `TRUST-ARCHITECTURE.md`, and now the 2026-04-25 flywheel design + decision panel.
- For decision-collection or single-pass approval surfaces, also use `docs/governance/`.
- For longer-form design narratives (analysis reports, research write-ups), consider `docs/reports/` per memory `project_assethold_spec_location.md`.
- Verify any time the brainstorming skill writes a spec: run `git check-ignore -v <path>` on the file before declaring the spec "saved." If gitignored, move it before committing.
- Future fix candidate: either change `.gitignore` line 438 to allow `docs/superpowers/specs/` (preserving the upstream skill default), OR patch the local skill copy to write to `docs/governance/` by default. Both are valid; until one happens, the rule above holds.
