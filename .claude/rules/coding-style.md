# Coding Style Rules

> Consistent style reduces cognitive load and makes code reviews efficient.

## Naming Conventions

### Variables and Functions
- **JavaScript/TypeScript**: `camelCase` for variables and functions
- **Python**: `snake_case` for variables and functions
- **Go**: `camelCase` for private, `PascalCase` for exported

### Classes and Types
- **All languages**: `PascalCase` for classes, interfaces, types
- Prefix interfaces with `I` only if language convention (e.g., C#)

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

### Order (top to bottom)
1. Standard library imports
2. Third-party package imports
3. Internal/local imports

### Rules
- Blank line between each group
- Alphabetize within groups
- No unused imports
- Prefer explicit imports over wildcards

## Comments

### When to Comment
- Complex algorithms or business logic
- Non-obvious performance optimizations
- Workarounds with issue references
- Public API documentation

### When NOT to Comment
- Obvious code (let the code speak)
- Commented-out code (delete it)
- TODOs without owners or ticket numbers

### Comment Style
- Use complete sentences
- Explain "why", not "what"
- Keep comments up-to-date with code
