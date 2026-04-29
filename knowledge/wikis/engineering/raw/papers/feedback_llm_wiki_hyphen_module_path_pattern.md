> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_llm_wiki_hyphen_module_path_pattern.md

---
name: llm-wiki directory name poisons every Python dotted-path reference below it
description: The `scripts/data/llm-wiki/` directory name contains a hyphen, which makes every Python dotted module path below it syntactically invalid. Recurred 3 times in plans drafted on 2026-04-24 across different contexts (imports, pytest plugin paths, subprocess invocations). Plan drafters must treat this as a systemic hazard.
type: feedback
originSessionId: 5b5fa564-d428-4456-ad9a-5bab022aefa8
---
Python module identifiers cannot contain hyphens. The directory `scripts/data/llm-wiki/` is valid as a filesystem path but invalid as the start of any Python dotted name. Any reference to a file below it via a dotted path fails — `from llm-wiki.foo import bar`, `pytest -p scripts.data.llm-wiki.tests.conftest`, `importlib.import_module("scripts.data.llm-wiki.ingest_orcina")` all raise `SyntaxError`/`ModuleNotFoundError` before the actual logic runs.

**Observed recurrence pattern (2026-04-24 session):**

1. **#2124 v1** — plan pseudocode wrote `from ingest_orcina import html_to_markdown, fetch_page` while Files-to-Change listed source as `ingest-orcina.py` (hyphen in filename). Caught by Claude r1.
2. **#2124 v2** — fix for v1 introduced a NEW file `ingest-orcina-extended.py` with the same hyphen pattern, and its test module couldn't import it. Caught by Claude r2.
3. **#2126 v4** — regression test used `-p scripts.data.llm-wiki.tests.markdown_qa.conftest` as a pytest plugin argument (also doubly wrong because `-p` loads plugins, not conftest files). Caught by Claude r3.

**Why:** The `llm-wiki/` directory name predates the planning work and can't be changed without cascading migrations across every script, test, and piece of tooling that imports from it. Agents drafting plans tend to treat the directory as a normal Python package, and the hyphen keeps slipping through.

**How to apply:**
- When drafting or reviewing ANY plan touching `scripts/data/llm-wiki/` or adjacent paths, treat every Python dotted reference below that directory as a likely defect. Grep the plan for `llm-wiki\.` (dot after the hyphenated segment) and `llm-wiki/.*\.py` paired with `from .* import` or `import .*`.
- Sanctioned patterns for reaching code under `llm-wiki/`:
  - Run pytest via `cd scripts/data/llm-wiki && pytest` (relative path, no dotted import).
  - Use `importlib.util.spec_from_file_location("module_name", "/abs/path/to/file.py")` for runtime loading.
  - Create NEW files with underscore-only names (e.g., `ingest_orcina_extended.py`) even though they live in a hyphen-containing directory — sibling imports work because CWD-relative imports don't traverse the hyphenated ancestor.
  - Subprocess invocation: `python -m pytest <relative-path>` from repo root works because pytest handles collection.
- Avoid:
  - `from <any>.llm-wiki.<any> import ...` — always invalid.
  - `pytest -p scripts.data.llm-wiki...` — plugin paths are dotted module names.
  - `importlib.import_module("scripts.data.llm-wiki.foo")` — raises.
- If a plan proposes a substantial rename (e.g., `llm-wiki/` → `llm_wiki/`), it's a multi-repo migration and should be its own scoped issue — not a side-effect of a feature plan.
- When REVIEWING a plan adversarially, grep the pseudocode for the literal string `llm-wiki.` (hyphen followed by dot) as a P1 smell.

**Related:** `feedback_codex_cli_0_124_upstream_regression`, `feedback_gemini_trust_env_blocks_reviews` (infra hazards). This is a planning-drafting hazard of the same severity — recurs silently across agent generations until explicitly flagged.
