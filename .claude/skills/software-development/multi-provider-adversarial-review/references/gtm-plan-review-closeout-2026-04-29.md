# GTM plan-review closeout pattern — 2026-04-29

Session pattern from workspace-hub GTM issues #2554/#2555.

## What happened
- Codex live review of #2554 returned `MAJOR`; the plan stayed draft even after safe textual patches because the live target count was 19, not the claimed >=20, and follow-up evidence issues were not opened.
- #2555 required all three live providers after prior `UNAVAILABLE` placeholders. Codex and Gemini returned `MINOR`; Claude initially timed out / hit `max turns` with an empty output, then succeeded using a compact prompt with more turns.
- Claude found a numeric defect (`108 cases` was wrong; matrix total was 156) that text-only reviews missed. Numeric GTM claims need independent calculation or source-file verification before promotion.
- Global `git status` hung because other background agents/VS Code had long-running git operations. Closeout used scoped `git diff -- <target-files>`, `git ls-files <target-files>`, explicit `git add <target-files>`, and `git diff --cached --name-only` instead of `git add -A` or broad status.

## Reusable pattern
1. Treat a single `MAJOR` plan-review verdict as blocking. Patch safe text, but do not promote until blockers are actually cleared or explicitly owner-scoped.
2. When replacing `UNAVAILABLE` placeholders with live artifacts, update every plan location that can drift: frontmatter artifact list, Artifact Map, Adversarial Review Summary, Overall Result, and Remaining Tasks.
3. Validate raw provider outputs before canonicalizing: non-zero file length plus a real `Verdict:` marker.
4. For Claude CLI review failures:
   - if `claude -p` times out with an empty tee file, retry with a compact prompt;
   - if it exits with `Error: Reached max turns`, increase `--max-turns` and rerun;
   - save the successful raw output as the canonical `scripts/review/results/YYYY-MM-DD-plan-NNNN-claude.md` artifact.
5. For GTM numeric/caption claims, calculate from source JSON or source reports rather than accepting prose from prior plans. Record whether the value is verified now or must be recomputed at render time.
6. Post two levels of GitHub evidence when useful: issue-specific review completion comments on child issues, and an owner decision packet on the GTM command-center issue.
7. In dirty/concurrent repos, stage only the intended target files and verify the staged name list before commit. Avoid broad `git add -A` while background agents are active.

## Owner-decision packet fields for downstream GTM work
- Which blockers are hard gates vs owner-scope decisions.
- Recommended defaults.
- Explicit no-outreach boundary.
- Inputs needed before brochure/outbound assembly.
