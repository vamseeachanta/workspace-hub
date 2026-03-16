### Verdict: REQUEST_CHANGES

### Summary
A well-structured skill-splitting utility with clear dataclasses and separation of concerns, but it has a silent data-loss bug in the section parser, exceeds the project's 200-line file limit at 490 lines, includes dead code, and ships with no tests despite the project's mandatory TDD rule.

### Issues Found
- [P1] Critical: split-oversized-skill.py:123-124 — `flush_buffer(None)` silently discards content between the last H3 child and the next H2 heading. Any prose after the final ### subsection but before the next ## section is lost without warning. The buffer is reassigned to [] inside flush_buffer but never stored anywhere when target is None.
- [P1] Critical: No tests accompany this script. Project rules (testing.md) mandate TDD — tests before implementation, no exceptions. A file-rewriting script that can silently drop content is high-risk without test coverage.
- [P2] Important: split-oversized-skill.py (490 lines) — Exceeds the project's 200-line hard limit (coding-style.md). The file should be split into at least parsing, planning, and rendering modules.
- [P2] Important: split-oversized-skill.py:171-176 — `_total_section_lines()` is defined but never called anywhere. Dead code.
- [P2] Important: split-oversized-skill.py:367 — `max_content = LINE_LIMIT - header_count - 3` can go negative if the YAML frontmatter is large (many metadata fields). A negative slice index like `content_lines[:negative]` silently removes content from the end rather than keeping nothing, producing a corrupted sub-skill.
- [P3] Minor: split-oversized-skill.py:308 — `hub_section_names` is a list; membership test is O(n). Should be a set for clarity and performance, especially since HUB_SECTIONS is already a set.
- [P3] Minor: split-oversized-skill.py:440-446 — `batch_split` reads each file twice: once to count lines, then `split_skill` reads it again. Could pass content or count into split_skill to avoid the double read.
- [P3] Minor: split-oversized-skill.py:245 — `line_count=len(content_lines)` counts heading and blank lines mixed with content, inconsistent with how Section.line_count counts only body lines. This could cause inaccurate dry-run reporting.

### Suggestions
- Fix the data-loss bug: when flushing an H2 that has children and there's leftover buffer content, append it to the last child's content or to the parent H2 instead of discarding it.
- Add `max_content = max(0, max_content)` guard in render_sub_skill to prevent negative-index slicing.
- Remove the unused `_total_section_lines` function or wire it into the dry-run reporting where it was presumably intended.
- Split the 490-line file into separate modules (e.g., `parsing.py`, `planning.py`, `rendering.py`, `cli.py`) to meet the 200-line limit.
- Convert `hub_section_names` to a set in `render_hub` (or accept it as a set from the caller).
- Write tests covering: (1) frontmatter parsing edge cases, (2) sections with mixed H2/H3 content including trailing content after last H3, (3) dry-run output accuracy, (4) sub-skill truncation behavior near LINE_LIMIT, (5) batch mode with mix of over/under-limit files.

### Questions for Author
- Was the content between the last H3 and the next H2 intentionally discarded, or is this a bug? Some SKILL.md files may have notes or examples after the final subsection.
- Is `_total_section_lines` leftover from an earlier design, or is it intended for future use?
- Are there existing tests elsewhere that cover this script, or is test coverage still pending?
