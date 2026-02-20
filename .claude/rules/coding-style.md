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
- **Maximum**: 400 lines (hard limit)
- **Target**: 200 lines (soft target)
- If a file exceeds limits, split by responsibility

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

## Agent Harness Files

CLAUDE.md, MEMORY.md, AGENTS.md, CODEX.md, GEMINI.md must not exceed 20 lines. Any content exceeding this limit must be migrated to a skill or doc before the file can be committed.
