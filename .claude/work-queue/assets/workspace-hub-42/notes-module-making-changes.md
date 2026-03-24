# Module: Making Changes — Claude Code in Action

## Screenshots
- Paste with **Ctrl+V** (not Cmd+V) to paste screenshots into Claude chat
- Use for pinpointing specific UI areas to modify

## Planning Mode
- **Activate**: Shift+Tab twice (or once if already auto-accepting edits)
- Behaviour: Claude reads more files → creates detailed plan → waits for approval before acting
- Best for: multi-file changes, broad codebase understanding, multi-step implementations

## Thinking Modes (reasoning depth)
| Mode | Usage |
|------|-------|
| think | Basic reasoning |
| think more | Extended reasoning |
| think a lot | Comprehensive reasoning |
| think longer | Extended time reasoning |
| ultrathink | Maximum reasoning |

Each level = more tokens allocated to reasoning before responding.

- Best for: complex logic, debugging, algorithmic problems
- Can combine with Planning Mode for breadth + depth

## Cost Note
Both planning and thinking modes consume additional tokens.

## Workspace Gap Analysis

| Feature | Workspace status | Notes |
|---------|-----------------|-------|
| Ctrl+V screenshots | ✓ Works in Claude Code terminal | Useful for UI work on uigen |
| Planning Mode (Shift+Tab) | ✓ Available — rarely used deliberately | Should use more for multi-file WRK items |
| Thinking modes | ✓ Available via prompt keywords | `ultrathink` useful for complex gate analysis |
| Planning + Thinking combined | Not currently a habit | Good for Route C WRK items at Stage 4 |

## Action Items for WRK-1103

- Add note to `work-queue-workflow/SKILL.md`: recommend Planning Mode at Stage 4 (Plan Draft)
  for Route C items (already captured in WRK-1083 plan-mode integration)
- Consider adding `ultrathink` to cross-review prompts for MAJOR finding analysis
