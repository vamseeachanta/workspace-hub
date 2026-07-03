# Cross-machine consistency prompt — post 2026-07-03 logo + PDF-portability session

Paste the block below into a fresh Claude session on another machine to bring that machine into
consistency with what landed on `main` today. It fetches canonical state from git (not local paths),
so it is portable across machines.

---

**CONTEXT — what merged to `main` on 2026-07-03 (all live):**
- **digitalmodel #1352** — new **mooring-bollard "moored to standards" logo** at `assets/logo/digitalmodel_logo.svg`. Tagline: *"Engineering moored to → Traceable codes and standards / Deterministic workflows / Single source of truth (SSOT)"*. Old taglines (Asset Lifecycle / Offshore·Subsea·Marine / "Automation: ASCII Data to Engineering Insights") are RETIRED — replace on sight. Portable by construction (rope texture = explicit `<line>` elements, no `<pattern>`).
- **workspace-hub #3376** — new rule `.claude/rules/svg-pdf-portability.md` (registered in `.claude/rules/README.md`): PDF-bound / logo SVG must use portable primitives only — **no `<pattern>`/`<clipPath>`/`<filter>`/`<mask>`** — and be verified with `pdftocairo`, not just a Chrome screenshot. (Root cause: Cairo/Evince mis-paints those as a spurious fill/band.) *Note: a non-blocking "Skill-Index Coherence" check failed on this merge — worth a glance.*
- **aceengineer-strategy** — #148 (Subsea7 pre-read on new logo, closed #145), #149 (2 Deckhand vote rope SVGs flattened, closed #146), #151 (engagement one-pager DRAFT). Epic **#144** and Lane-C decision **#147** (does Deckhand adopt the bollard mark?) remain OPEN = user decision.

**TASK — bring THIS machine to consistency:**
1. **Sync** ecosystem repos to `origin/main`, fast-forward only, never discarding local work (use `repo-sync` / `reconcile-ecosystem`): `workspace-hub`, `aceengineer-strategy`, `digitalmodel`, `worldenergydata`. Handle detached-HEAD / diverged / dirty per repo. **digitalmodel is SLOW-git — never `git worktree add`** (checkout gets killed by tool timeout).
2. **Verify landed artifacts on main:**
   - `digitalmodel/assets/logo/digitalmodel_logo.svg` contains `Engineering moored to` and has **0** matches for `<pattern`/`clip-path`.
   - `workspace-hub/.claude/rules/svg-pdf-portability.md` exists and is listed in `.claude/rules/README.md`.
   - `aceengineer-strategy/pipeline/subsea7-fdg/pre-read-one-pager.html` contains `Single source of truth (SSOT)`; the 2 files `strategy/deckhand/release/assets/vote/logo-{A1,B1}-rope.svg` have **0** pattern refs.
3. **Portability self-check:** render any PDF-bound logo SVG → `chrome --headless --print-to-pdf` → `pdftocairo -png` and inspect for a spurious band/fill. Inter font is usually absent → force `Liberation Sans` for the PNG only (keep the Inter stack in the committed SVG).
4. **Machine-equality:** run `/reconcile-ecosystem` (or `publish-equality.sh --repo <workspace-hub> --rebuild`) to bring this machine to equivalence and refresh the matrix.
5. **Report** drift found + fixed. Open PRs for any fixes; **do NOT self-merge** — hand the user `gh pr merge <N> --squash --delete-branch --repo <owner>/<name>`.

**GUARDRAILS:**
- digitalmodel slow-git assets-only commits via the **plumbing recipe** (`hash-object -w` → `read-tree origin/main` into a temp `GIT_INDEX_FILE` → `update-index --cacheinfo` → `write-tree` → `commit-tree -p origin/main` → `update-ref` → push). Never touches the shared working tree/HEAD.
- **Do NOT touch `aceengineer-website`** — it has its own "AceEngineer" brand (`assets/img/logo.svg`, tagline "ANALYTICAL & COMPUTATIONAL ENGINEERING"). Out of scope.
- Auto-sync is active in aceengineer-strategy + workspace-hub — plumbing commits stay auto-sync-safe; after any working-tree edit, restore files you don't want swept onto the current branch.
- **HELD (do not action without explicit user approval):** Deckhand rebrand (#147); engagement deck + one-pager 3 decisions (deck scope / IP stance / pricing).

---

Full session detail: [`2026-07-03-handoff-subsea7-preread-logo-portability.md`](2026-07-03-handoff-subsea7-preread-logo-portability.md). Memory: `feedback_svg_pdf_portability_no_patterns_clippaths`, `project_digitalmodel_logo_moored_mark`, `project_subsea7_fdg_deck`.
