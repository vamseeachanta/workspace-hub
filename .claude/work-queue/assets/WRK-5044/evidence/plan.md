# Plan — WRK-5044

Route A inline plan:
1. Read `scripts/review/submit-to-codex.sh` to find the `--commit` path
2. Convert commit SHA to diff via `git show`, route through `codex exec --output-schema`
3. Add tests T24-T25 for codex `--commit` path
4. Commit + push
