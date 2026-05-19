# Client-Review Export Closeout for HTML Engineering Reports

Use this reference when a follow-up request starts from an existing HTML engineering report and asks for client-review copies, shareable paths, or downstream comment/review artifacts.

## Discovery pattern

1. Search for the report by tolerant tokens, not just the user's spelling. Engineering/vessel names are easy to mistype (`sorroco` vs `sirocco`), so try case-insensitive variants and nearby directory names before concluding the artifact is absent.
2. If the first exact filename glob returns no hits, do not stop or report absence. Immediately broaden across likely report extensions/directories using multiple axes:
   - spelling/case variants (`sorroco`, `sirocco`, `Sirocco`);
   - numeric condition variants (`30`, `30deg`, `30_deg`, `30-degree`, `30°`);
   - artifact type variants (`*.html`, `*report*`, `outputs/**`, `docs/**`, `results/**`).
3. Prefer the canonical repo artifact under `outputs/.../*_report.html` over transient `/tmp` or generated preview copies.
4. Once found, report both:
   - repo-relative path, and
   - GitHub/blob or raw URL if the repo is remote-backed.

## Export pattern

For client-review derivative artifacts:

1. Preserve the HTML report identity in filenames. Use suffixes such as `_client_review.pdf` and `_client_review.docx` next to the source report unless the user asks for another destination.
2. If the source report has interactive controls or selected-case charts, choose a documented screenshot/default state before export. Record any assumed default values in the derivative artifact or final note.
3. Convert/generate DOCX and PDF from the verified source content, not from a separate stale summary.
4. Keep client-review copies traceable to the source issue/report by including the issue number, source report name, and generation timestamp when the generator supports it.

## Verification before closeout

Do not call the export complete until all applicable checks pass:

- HTML renders in a browser or is structurally parsed.
- At least one interaction/default-state path is exercised when controls drive charts or readouts.
- PDF is checked for page count/metadata and text extraction for report identity, governing condition, and selected calculation values.
- DOCX text is extracted or otherwise inspected for report identity and client-review/default-state notes.
- Raw or blob URLs return HTTP 200 before handing them to the user.
- Scoped leakage scan over HTML/PDF/DOCX text checks for local paths, environment names, secrets, or unrelated machine details.
- Git closeout includes commit, push verification, and an issue comment when the work is issue-scoped.

## Closeout wording

Return the primary source report path first, then derivative artifacts, then commit/push/issue-comment evidence. Keep cleanup residue separate from artifact success: name unrelated dirty-state explicitly and do not imply the whole repo is clean if only the generated artifacts were cleaned up.