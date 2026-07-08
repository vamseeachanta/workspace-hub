# Session handoff - perforating gun training visual intake

Date: 2026-07-08
Repo: `workspace-hub`
Branch: `main`
Workspace: `/mnt/local-analysis`
Exit purpose: document the current state before exiting. No perforating-gun visual was created in this session.

## Active task

The user asked whether the workspace already has a good picture, labeled diagram, data, or schematics for a perforating gun, for use in a crash course for interns and employees. After inventorying the local workspace, the user authorized the boundary of creating an original generic training handout/diagram, but then requested "document and prepare to exit" before implementation.

## Completed in this session

- Inspected `/mnt/local-analysis` as a multi-repo/local data workspace. The top level is not itself a git repo.
- Searched for perforating-gun-related text, image, PDF, CAD, and schematic candidates across the relevant local workspace while excluding common dependency/noise paths.
- Identified usable internal text sources in `llm-wiki`, especially the production-engineering perforating cluster.
- Did not find a usable local labeled picture, diagram, schematic, CAD, PDF, or embedded image for a perforating-gun assembly.
- Confirmed `llm-wiki` production-engineering perforating pages have no embedded image references matching `![`, `<img`, `.png`, `.jpg`, `.jpeg`, `.svg`, `diagram`, `schematic`, `figure`, `image`, `picture`, or `labeled`.
- Proposed a future standalone HTML training handout with an inline SVG cutaway. The detailed design was proposed but not explicitly approved after the proposal; the user asked to exit instead.

## Useful source files

- `llm-wiki/wikis/production-engineering/wiki/concepts/perforating.md`
  - Lines 14-16 explain perforating as the operation that creates hydraulic communication through casing, cement, and formation.
  - Lines 30-37 list the four design questions: gun system, charge, shot density/phasing, and pressure differential.
- `llm-wiki/wikis/production-engineering/wiki/concepts/perforating-gun-systems.md`
  - Lines 14-23 define the gun system and conveyance families: TCP, wireline, coiled tubing, and through-tubing.
  - Lines 31-42 summarize TCP concept and strengths.
  - Lines 142-160 cover hollow-carrier vs strip/port-plug and gun-to-casing stand-off.
  - Lines 176-184 summarize firing-head systems.
- `llm-wiki/wikis/production-engineering/wiki/concepts/perforating-shaped-charges.md`
  - Lines 18-28 provide charge anatomy: case, explosive load, liner, primer/detonator pellet, and detonator-cord interface.
- `llm-wiki/wikis/production-engineering/wiki/concepts/perforation-strategy.md`
  - Covers shot density, phasing, deep-penetrating vs big-hole charges, and underbalanced/overbalanced/extreme-overbalanced strategy.
- `worldenergydata/docs/knowledge-base/bsee/data-dictionaries/wells/completion-fields.md`
  - Lines 58-66 include operational data fields: perforation top/bottom, interval, shots per foot, total shots, perf gun size, and charge type.

## Proposed future artifact

Recommended artifact: one standalone HTML file under `/mnt/local-analysis`, not repo-tracked unless the user later asks to add it to a repo.

Draft design:

- Title: `Perforating Gun System: Assembly and Operation`
- Main visual: horizontal cutaway of a generic hollow-carrier perforating gun inside casing, cement, and formation.
- Labels: carrier, charge tube/loading tube, shaped charge, liner, explosive load, detonating cord, firing head, tandem/sub connection, centralizer/stand-off, scallop/port, casing, cement sheath, perforation tunnel, and formation.
- Side panel: four-step operation sequence: convey to depth, position/orient, fire, create tunnels/flow path.
- Footer disclaimer: generic training schematic; not vendor-specific; not for manufacturing tolerance or job design.
- Source basis: internal wiki files listed above.

Do not copy vendor diagrams or infer proprietary internals. Keep the visual generic and conceptual.

## Current repo and workspace state

- `workspace-hub` branch: `main`
- `workspace-hub` status before this handoff had unrelated modified provider/config/report files:
  - `config/ai-tools/agent-quota-latest.json`
  - `config/ai-tools/provider-autolabel-candidates.json`
  - `config/ai-tools/provider-kanban.json`
  - `config/ai-tools/provider-routing-scorecard.json`
  - `config/ai-tools/provider-utilization-weekly.json`
  - `config/ai-tools/provider-work-queue.json`
  - `docs/reports/provider-autolabel-candidates.md`
  - `docs/reports/provider-kanban-dashboard.html`
  - `docs/reports/provider-kanban-dashboard.md`
  - `docs/reports/provider-routing-scorecard.md`
  - `docs/reports/provider-utilization-weekly.md`
  - `docs/reports/provider-work-queue.md`
- Those pre-existing modifications were not touched by this session.
- `llm-wiki` had untracked `.worktrees/` and `coordination/locks/` during cleanup audit. These were not created by this session and were not modified.
- `/mnt/local-analysis/.cleanup-trash/20260616-095709` exists from an older cleanup pass.
- `/tmp` contains unrelated recent logs and scratch files, including `cl_phase*.log`, `cl_codex_ingest.log`, `uv-*.lock`, and a temporary test directory. None were created by this handoff task.

## Blockers and boundaries

- No implementation artifact exists yet.
- The user approved the generic/non-vendor source boundary, but the specific HTML/SVG handout design should be re-confirmed before building if the next session follows the brainstorming gate strictly.
- If the future artifact is kept local under `/mnt/local-analysis`, no GitHub issue/plan is required unless the user wants repo integration.
- If the future artifact is committed to a repo, follow the normal issue -> plan -> review -> user approval gate before implementation.

## Exact next checkpoint

1. Ask the user whether to proceed with the proposed standalone HTML handout design.
2. If approved, create `/mnt/local-analysis/perforating-gun-training-handout.html` as a self-contained HTML file with inline SVG and no external assets.
3. Verify by opening or rendering the file locally and checking that all labels fit at desktop and mobile widths.
4. Optionally export a PNG or PDF only if the user requests a slide-ready or printable artifact.
5. Run the pre-completion cleanup audit before final closeout.

## Suggested skills

- `superpowers:using-superpowers`
- `superpowers:brainstorming` if the design changes or needs approval
- `frontend-design:frontend-design` if turning the handout into a polished browser artifact
- `browser-use:browser` if visual verification in a browser is needed
- `coordination/pre-completion-cleanup-audit`
