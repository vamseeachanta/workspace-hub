# WRK-1041 Plan — Claude

Route A (simple). Inline plan in WRK file.

## Steps
1. TDD: write 2 failing tests (`test_lifecycle_html_has_meta_refresh`, `test_review_html_has_meta_refresh`)
2. Add `<meta http-equiv="refresh" content="30">` to `generate_lifecycle()` head
3. Add same tag to `render_wrk_html()` head
4. Run tests, verify green
5. Commit
