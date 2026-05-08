# Repo Ecosystem Flowchart Collateral

Use when the user asks for a concise, client-facing PDF that explains how the repo ecosystem supports an engineering consulting company, especially after a prospect email or pilot discussion.

## Pattern

1. **Review live tier-1 repo evidence before drafting**
   - Inspect `docs/BUSINESS_BRAIN.md` and `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md` for current repo roles.
   - Check the actual tier-1 repo directories, remotes, and strongest mission source (`AGENTS.md`, `README.md`, or `.agent-os/product/mission.md`).
   - Capture dirty-state caveats, but do not let unrelated dirt block a read-only collateral draft.

2. **Translate repo roles into a consulting flow**
   - Prospect/pilot intake: `aceengineer-strategy`.
   - Public proof surface: `aceengineer-website`.
   - AI control plane / GSD governance: `workspace-hub`.
   - Utility substrate: `assetutilities`.
   - Data layer: `worldenergydata`.
   - Engineering computation core: `digitalmodel`.
   - Business/finance evidence: `assethold`.
   - Final deliverable: client-ready PDF/HTML analysis pack.

3. **Keep the page prospect-friendly**
   - One page only; use flowchart language, not internal workflow jargon alone.
   - Tie the story to the email/prospect context: one representative problem -> governed issue -> reusable automation -> traceable report for senior-engineer review.
   - Include clickable GitHub repo links in the PDF when public/safe.
   - Add a caveat that client-specific/confidential data stays out of public repos.

4. **Recommended artifact layout**
   - Draft as self-contained HTML first for layout control and clickable links.
   - Render PDF with headless Chrome:
     ```bash
     google-chrome --headless --disable-gpu --no-sandbox \
       --no-pdf-header-footer \
       --print-to-pdf="$OUT" "file://$ABS_HTML"
     ```
   - Use landscape Letter for dense ecosystem diagrams.

5. **Verification checklist**
   - `pdfinfo "$OUT"` confirms `Pages: 1` and expected page size.
   - `pdftotext "$OUT" -` confirms key labels are present.
   - `strings "$OUT" | grep 'https://github.com/...'` confirms embedded links when link validation libraries are unavailable.
   - Optionally render a preview with `pdftoppm -f 1 -l 1 -png -singlefile`.

6. **Client follow-up Markdown packet**
   - When the user asks to refine an email response and collect links, create a companion Markdown file in the same sendable bundle, e.g. `docs/gtm/sendable-bundles/YYYY-MM-DD/<prospect>-follow-up-email-and-links.md`.
   - Include: polished email response, local PDF links, GitHub blob links for committed/pushed files, tier-1 repo links with one-line roles, and a send checklist.
   - Verify all local relative links resolve before opening or reporting:
     ```bash
     python - <<'PY'
     from pathlib import Path
     base = Path('docs/gtm/sendable-bundles/YYYY-MM-DD')
     for p in ['repo-ecosystem-flowchart.pdf', '../../capability-summary.pdf']:
         q = (base / p).resolve()
         print(('OK   ' if q.exists() else 'MISS ') + p + ' -> ' + str(q))
     PY
     ```
   - State clearly when GitHub links point to `main` but the files are still untracked/unpushed; do not imply links are live until committed and pushed.
   - If requested, open the Markdown or PDF with VS Code after verification: `code -g "$FILE:1"` for Markdown and `code -g "$PDF"` for PDF.

## Pitfalls

- `pypdf` may not be installed in the active environment; do not stop verification there. Fall back to `pdfinfo`, `pdftotext`, `strings`, and `pdftoppm`.
- Avoid sending or committing the artifact unless explicitly approved. For outreach collateral, report artifact paths and note that no external action was taken.
- Treat `aceengineer-strategy` as private/pipeline ops in wording even if a local checkout exists; keep PII and named contact details out of public artifacts.
