# SPARC Tester Mode

## Purpose
Comprehensive testing with parallel execution capabilities.

## Activation

### Option 1: Using MCP Tools (Preferred in Claude Code)
```javascript
  mode: "tester",
  task_description: "full regression suite",
  options: {
    parallel: true,
    coverage: true
  }
}
```

### Option 2: Using NPX CLI (Fallback when MCP not available)
```bash
# Use when running from terminal or MCP tools unavailable

# For alpha features
```

### Option 3: Local Installation
```bash
```

## Core Capabilities
- Test planning
- Test execution
- Bug detection
- Coverage analysis
- Report generation

## Test Types
- Unit tests
- Integration tests
- E2E tests
- Performance tests
- Security tests

## Parallel Features
- Concurrent test runs
- Distributed testing
- Load testing
- Cross-browser testing
- Multi-environment validation
