# Interactive Mode Guidelines

> **Purpose**: Ensure Claude always asks clarifying questions before implementing tasks
> **Scope**: All 26 repositories in workspace-hub
> **Last Updated**: 2025-10-23

## Overview

Claude is now configured to **ALWAYS ask interactive questions** before starting any implementation work. This ensures:

1. **Clear requirements** - No assumptions about user intent
2. **Better solutions** - Understanding context leads to better design
3. **Reduced rework** - Getting it right the first time
4. **User control** - User makes all important decisions

## Configuration Changes

### Files Updated

1. **Global Configuration**: `~/.claude/CLAUDE.md`
   - Added "Interactive Engagement (MANDATORY)" section
   - Applies to all projects by default

2. **Workspace-Hub**: `/mnt/github/workspace-hub/CLAUDE.md`
   - Replaced "Proactiveness" section with "Interactive Engagement (MANDATORY)"
   - Project-specific implementation

3. **All Repositories**: Use propagation script to update all 26 repos
   - Script: `scripts/propagate_interactive_mode.sh`
   - Updates each repo's CLAUDE.md

### Section Added

The new "Interactive Engagement (MANDATORY)" section requires Claude to:

1. **Ask before implementing** - Always clarify requirements first
2. **Present options** - Show multiple approaches with trade-offs
3. **Wait for approval** - Never assume the user's preference
4. **Continue dialogue** - Ask follow-up questions as needed

## Required Question Pattern

### Before ANY Implementation

Claude MUST ask about:

1. **Scope clarification**
   - What exactly should be included?
   - What should be excluded?
   - What are the boundaries?

2. **Technical choices**
   - Which approach/technology/pattern?
   - Trade-offs between options?
   - Integration with existing code?

3. **Edge cases**
   - How to handle unusual scenarios?
   - Error conditions?
   - Boundary conditions?

4. **Testing requirements**
   - What tests are needed?
   - What coverage level?
   - Performance tests?

5. **Performance expectations**
   - Response time requirements?
   - Scalability needs?
   - Resource constraints?

6. **Error handling**
   - How should errors be handled?
   - User feedback on errors?
   - Logging requirements?

## Question Format Examples

### Example 1: Authentication Feature

**User**: "Add user authentication"

**Claude**: "I have some questions before implementing authentication:

1. **Authentication method**: Which approach?
   - Option A: JWT tokens (stateless, scales well, requires token refresh logic)
   - Option B: Session-based (simpler, requires server state, easier to revoke)
   - Option C: OAuth (third-party providers like Google/GitHub)

2. **User storage**: Where to store user data?
   - Existing database table?
   - New dedicated user table?
   - External service (Auth0, Firebase)?

3. **Password security**: Requirements?
   - Hashing algorithm: bcrypt (standard), argon2 (more secure)?
   - Password complexity rules?
   - MFA/2FA required?

4. **Session management**: How long should sessions last?
   - Short (15-30 minutes) with refresh?
   - Long (7-30 days)?
   - "Remember me" option?

5. **Error handling**: What should happen on failed login?
   - Lock account after X attempts?
   - Rate limiting?
   - Password reset flow needed?

Please let me know your preferences for these decisions."

### Example 2: API Endpoint

**User**: "Create an API endpoint for user search"

**Claude**: "Before implementing the user search endpoint, I need clarification:

1. **Search criteria**: What fields should be searchable?
   - Name only?
   - Email, username, profile data?
   - Full-text search or exact match?

2. **Performance**: Expected usage?
   - Real-time autocomplete (needs caching)?
   - Occasional searches (simple query)?
   - Large dataset (needs pagination/indexing)?

3. **Results**: How should results be returned?
   - Full user objects?
   - Minimal data (id, name, email)?
   - Pagination required? (page size?)

4. **Security**: Access control?
   - Public endpoint?
   - Authenticated users only?
   - Role-based restrictions?

5. **Response format**: Any specific structure?
   - REST JSON?
   - GraphQL?
   - Include metadata (total count, page info)?

Please specify your requirements."

### Example 3: Data Analysis Module

**User**: "Analyze hull stress data"

**Claude**: "I need to understand the analysis requirements:

1. **Input data format**: What format is the hull data?
   - CSV file with node coordinates?
   - Finite element mesh?
   - Point cloud data?

2. **Analysis type**: What calculations are needed?
   - Static stress analysis?
   - Dynamic/fatigue analysis?
   - Buckling analysis?
   - All of the above?

3. **Standards compliance**: Which standards to follow?
   - ABS (American Bureau of Shipping)?
   - DNV (Det Norske Veritas)?
   - Lloyd's Register?
   - Multiple standards?

4. **Output requirements**: What results format?
   - Interactive HTML report (Plotly visualizations)?
   - CSV summary statistics?
   - Detailed calculation log?
   - 3D stress plot?

5. **Performance**: Size of typical dataset?
   - Small (<1000 elements)?
   - Medium (1000-10000 elements)?
   - Large (>10000 elements)?

6. **Validation**: How to verify results?
   - Compare against reference solution?
   - Benchmark problems?
   - Cross-check with commercial software?

Please provide these details so I can design the module correctly."

## Benefits of Interactive Mode

### For Users

1. **Control**: User makes all important decisions
2. **Clarity**: No surprises from assumed requirements
3. **Efficiency**: Get it right the first time
4. **Learning**: Understand trade-offs through dialogue

### For Claude

1. **Accuracy**: Understand requirements fully before coding
2. **Context**: Learn domain-specific constraints
3. **Options**: Present multiple valid approaches
4. **Validation**: Confirm understanding before proceeding

### For Projects

1. **Quality**: Better solutions from better requirements
2. **Documentation**: Question-answer history documents decisions
3. **Maintainability**: Clear intent captured in conversation
4. **Consistency**: Same question pattern across all repos

## Propagation to All Repositories

### Using the Propagation Script

```bash
# Run from workspace-hub root
./scripts/propagate_interactive_mode.sh

# The script will:
# 1. Find all repositories in workspace-hub
# 2. Locate CLAUDE.md in each repo
# 3. Replace "Proactiveness" section with "Interactive Engagement"
# 4. Create backups (.backup-YYYYMMDD-HHMMSS)
# 5. Report success/failure for each repo
```

### Manual Propagation

If you need to update a specific repository manually:

1. Open the repository's `CLAUDE.md`
2. Find the "## Proactiveness" section
3. Replace entire section with "Interactive Engagement (MANDATORY)" section from workspace-hub/CLAUDE.md
4. Save and commit

### Verification

After propagation, verify changes:

```bash
# Check all repos have the new section
grep -r "## Interactive Engagement (MANDATORY)" /mnt/github/workspace-hub/*/CLAUDE.md

# Count repos with interactive mode enabled
grep -l "## Interactive Engagement (MANDATORY)" /mnt/github/workspace-hub/*/CLAUDE.md | wc -l

# Should match number of repos with CLAUDE.md files
```

## Exceptions

### When Questions May Be Skipped

**ONLY in these scenarios:**

1. **Explicit command**: User says "no questions, just do X"
2. **Emergency fix**: Critical bug fix with clear scope
3. **Trivial change**: Single-line obvious fix (typo, formatting)
4. **Follow-up**: User already answered in previous message

**Even then, Claude should confirm understanding.**

### Never Skip Questions For

- New features (always ask about requirements)
- Architecture changes (always discuss trade-offs)
- Breaking changes (always confirm impact)
- Data migrations (always verify safety)
- Security changes (always review implications)

## Integration with Existing Workflows

### SPARC Methodology

Interactive mode enhances SPARC phases:

1. **Specification**: Ask questions to clarify requirements
2. **Pseudocode**: Confirm algorithm approach before coding
3. **Architecture**: Discuss design choices and patterns
4. **Refinement**: Ask about refactoring priorities
5. **Completion**: Verify integration points and deployment

### TDD Workflow

Questions help with TDD:

1. **Before tests**: What scenarios to test? What coverage?
2. **Test design**: What assertions? What edge cases?
3. **Implementation**: Which approach to make tests pass?
4. **Refactoring**: What to optimize? What to keep simple?

### YAML-Driven Development

Questions improve YAML configuration:

1. **Execution parameters**: Memory limits? Timeouts? Retries?
2. **Inputs**: File formats? Validation rules? Units?
3. **Outputs**: Report formats? Visualization types? Summaries?
4. **Performance**: Benchmarks? Thresholds? Optimization?

## Best Practices

### For Users

1. **Expect questions** - This is the new normal
2. **Answer thoroughly** - Provide context and constraints
3. **Ask for options** - Request multiple approaches if unsure
4. **Iterate** - Refine requirements through dialogue

### For Claude

1. **Always ask first** - Never assume
2. **Present options** - Show multiple approaches
3. **Explain trade-offs** - Help user make informed decisions
4. **Confirm understanding** - Summarize before proceeding

## Troubleshooting

### Claude Not Asking Questions

**Possible causes:**
1. Old configuration not updated
2. Project CLAUDE.md overriding global settings
3. Repository missing CLAUDE.md

**Solutions:**
1. Re-run propagation script
2. Check project CLAUDE.md has Interactive Engagement section
3. Add CLAUDE.md if missing

### Too Many Questions

**If Claude asks excessive questions:**
1. User can say "Use your best judgment for minor details"
2. User can provide comprehensive initial requirements
3. User can reference similar existing implementations

### Questions Not Relevant

**If questions miss the mark:**
1. User should clarify the actual concern
2. Claude should refine question based on feedback
3. Iterate until understanding is aligned

## Examples from Real Projects

### Marine Structural Analysis

**Good question pattern:**
- Ask about classification society standards (ABS, DNV, Lloyd's)
- Clarify mesh density requirements
- Confirm safety factors and validation approach
- Verify output format (interactive HTML vs static PDF)

### Web Application

**Good question pattern:**
- Ask about authentication method early
- Clarify database schema before implementing
- Confirm API design patterns
- Verify error handling strategy

### Data Processing Pipeline

**Good question pattern:**
- Ask about input data formats and sizes
- Clarify performance requirements
- Confirm error recovery strategy
- Verify logging requirements

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-23 | Initial interactive mode guidelines |

## Related Documentation

- `CLAUDE.md` - Configuration file with Interactive Engagement section
- `DEVELOPMENT_WORKFLOW_GUIDELINES.md` - Overall development workflow
- `~/.agent-os/standards/best-practices.md` - Global best practices

---

**Remember**: The goal is better software through better communication. Questions are not obstacles—they're the path to excellent solutions.
