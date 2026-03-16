# Coding Style Rules

> Consistent style reduces cognitive load and makes code reviews efficient.

## Naming Conventions

### Variables and Functions
- **Python**: `snake_case`; **JS/TS**: `camelCase`

### Classes and Types
- `PascalCase` for classes, interfaces, types (all languages)

### Constants
- **SCREAMING_SNAKE_CASE** for true constants
- `camelCase` for const variables that hold objects/arrays

### Files and Directories
- Use `kebab-case` for file names
- Match file name to primary export when applicable
- One component/class per file (generally)

## Size Limits

### File Length
- **Maximum**: 200 lines (hard limit)
- **Target**: 100 lines (soft target)
- If a file exceeds limits, split by responsibility — smaller files force clearer subtask/subutility boundaries

### Function Length
- **Maximum**: 50 lines
- **Target**: 20-30 lines
- Each function should do one thing well

### Line Length
- **Maximum**: 100 characters
- **Target**: 80 characters
- Break long lines at logical points

## Import Organization
Order: stdlib → third-party → local. Blank line between groups. Alphabetize within groups. No unused imports or wildcards.

## Comments
Comment when: complex algorithms, non-obvious optimizations, workarounds with refs, public API docs. Explain "why" not "what". No commented-out code or ownerless TODOs.

## Edit Safety

- Prefer targeted single-site edits over bulk find-replace — verify each change site
- After edits: confirm imports not mangled, no duplicate definitions, no deleted adjacent code
- Multi-file refactors: edit one file at a time, run tests between files

## Path Handling

- In scripts: use relative paths or `$(git rev-parse --show-toplevel)` / `${REPO_ROOT}` — never hardcode `/mnt/local-analysis/workspace-hub/`
- Absolute paths are permitted only when a tool call explicitly requires them (e.g., `file_path` parameter in Read/Edit/Write tools)
- Exception: CI/CD configs and Docker bind-mounts may need absolute paths; document the reason inline

## Data Format Selection (Hard Rule)

> **YAML-first for all agent-facing structured data.** Markdown is for prose only.

### Decision Matrix

| Writer | Format | Rationale |
|--------|--------|-----------|
| Agent writes structured data | **YAML** + schema validation | 30-40% fewer tokens = more instructions fit in context; inline comments guide agent behavior |
| Agent writes prose (plans, reviews) | **Markdown** | Rendering matters; human review at gates |
| Script generates deterministic output | **JSON** | Schema-enforceable; no ambiguity |
| Human curates config | **YAML** | Comments, readability, diff-friendly |
| External API interchange | **JSON** | Industry standard |
| Append-only machine logs | **JSONL** | One record per line; grep-friendly |

### Why YAML Over JSON for Agent Work

1. **Token density**: YAML uses ~30-40% fewer tokens → more rules/context per window → agent follows instructions longer before degradation
2. **Inline instructions**: `# HARD RULE: never edit this field` next to the data improves compliance vs separate instruction files
3. **Multiline blocks**: `|` preserves formatting; JSON `\n` escaping degrades instruction parsing
4. **Visual hierarchy**: indentation costs fewer attention tokens than brace-matching

JSON's only advantage was strict parsing catching corruption — **schema validation on YAML eliminates that gap**.

### File Extension Rules

| Content type | Extension | Never use |
|-------------|-----------|-----------|
| Test results, verdicts, AC matrices | `.yaml` | `.md` with pipe tables |
| Evidence files (claim, checkpoint, legal scan) | `.yaml` | `.md` |
| Gate summaries (script-generated) | `.json` | `.md` |
| Plans, review narratives | `.md` | `.yaml` |
| WRK items | `.md` (YAML frontmatter + MD body) | pure `.yaml` |
| Metrics, accumulator state | `.json` | `.md` |

### Prohibited Pattern

Never use Markdown tables (`| col | col |`) for structured data that agents write.
Markdown tables have no parser — corruption (deleted rows, misaligned columns) is silent and undetectable. Use YAML lists-of-dicts instead.

### Schema Validation

New YAML evidence files should have a companion schema in `config/work-queue/schemas/`.
Validator scripts (`validate-*.py`) must reject structural changes to protected fields.

## Agent Harness Files

CLAUDE.md, MEMORY.md, AGENTS.md, CODEX.md, GEMINI.md must not exceed 20 lines. Any content exceeding this limit must be migrated to a skill or doc before the file can be committed.
