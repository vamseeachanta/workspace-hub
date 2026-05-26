# Session Handoff — Hermes Kanban readability fixes made durable

**Date:** 2026-05-26
**Author:** Claude (main session)
**Scope:** Hermes Kanban dashboard UX fixes + durable user-override + recovery skill
**Branch worked on:** none (changes isolated to a single direct-to-`main` commit)

## What was done

Two readability fixes to the Hermes Kanban dashboard plugin, then made durable
against `hermes update` / `git pull` of the bundled `hermes-agent` checkout.

1. **Bare-URL autolinking** — `renderInline` in the kanban dashboard
   `dist/index.js` only linkified `[text](url)` markdown. GitHub-synced card
   descriptions carry bare lines like `Source: https://github.com/.../2795`,
   which stayed plain text. Patched to autolink bare `http(s)://` URLs
   (markdown links stashed first so they aren't double-wrapped; trailing
   sentence punctuation kept outside the anchor).
2. **Readable card-text font** — card titles/meta inherited the `Mondwest`
   *display* font (Hermes branding) at ~12.75px, which reads poorly for dense
   body text. Override pins the `system-ui` sans stack (the face the column
   headers already use) and bumps sizes (title 0.95rem, meta 0.8rem, id 0.7rem).
   *(An earlier light-background color experiment was reverted at user request —
   the font type/size was the real readability lever.)*

Verified live in-browser: card titles render `system-ui 14.25px`; the
`Source:` URL renders as `<a target="_blank" rel="noopener noreferrer">`.

## Durability mechanism (two layers)

| Layer | Location | Survives |
|---|---|---|
| User-override plugin | `~/.hermes/plugins/kanban/dashboard/` | `hermes update` / `git pull` (outside the repo; dashboard loader scans user plugins first and shadows the bundled `kanban` by name) |
| Recovery skill | `.claude/skills/devops/hermes-kanban-readability/` | Loss of `~/.hermes` entirely — `install.sh` regenerates the override from the current bundled plugin + reapplies both fixes (idempotent, drift-aware) |

The bundled plugin in the hermes-agent repo was reverted to **git-clean** — no
in-place edits remain there, so hermes-agent updates won't conflict.

## Repo state at handoff

- **`workspace-hub` `origin/main`:** advanced `0af5e50ea..de3410905` (this
  session's only push). Commit `de3410905` contains exactly the 6 skill files,
  nothing else. Pre-push hook ran and passed (no tier-1 CI gate triggered).
- **Local branch `fix/2795-dispatch-review-findings`:** UNCHANGED. The commit
  was built via an isolated `GIT_INDEX_FILE` temp-index parented on fresh
  `origin/main`, so the working tree, the real (already-populated) index, HEAD,
  and ~95 unrelated parallel-session dirty entries were never touched.
- **`hermes-agent` (`~/.hermes/hermes-agent`):** git-clean; on `main` at
  `2c6bbaf35` (the provenance commit recorded in the skill).

## Dirty exceptions (NOT this session's work — left as-is)

The `workspace-hub` working tree carries ~95 dirty/untracked entries from a
parallel session (memory snapshots, `.claude/state/*`, other new skills:
`kanban-codex-lane`, `kanban-worker`, `wiki-health-operations`,
`hermes-s6-container-supervision`, etc.). These were deliberately **not**
staged, committed, or otherwise disturbed.

## No external actions beyond the authorized push

Only one outward action: `git push origin de3410905:main` (user-authorized).
No issues opened/closed, no PRs, no deletions, no agent dispatch.

## Next steps / operational notes

- **After every `hermes update`:** re-run
  `.claude/skills/devops/hermes-kanban-readability/install.sh` (idempotent).
- **Known minor wart:** `kanban-readability.patch` is git-detected as binary
  because the captured diff included raw NUL bytes from the first hand-edit of
  `index.js`. It's a provenance reference only — the operative recovery
  artifacts (`patches/renderInline.{original,patched}.js`, `style.append.css`)
  are clean text and the installer uses those, not the `.patch`. Optional
  cleanup: regenerate the `.patch` from the now-clean files.
- **Optional upstream path (not taken):** the autolink fix is a clean bugfix
  candidate for a `NousResearch/hermes-agent` PR; the font swap is a local
  preference that may conflict with Hermes's deliberate Mondwest branding.
- Memory recorded: `reference_hermes_dashboard_plugin_override` (Claude
  auto-memory) — captures the user-override-survives-update mechanism.
