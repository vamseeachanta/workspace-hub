# Multi-AI Commit Workflow

> Automated code review and testing using multiple AI models
>
> Version: 1.0.0
> Last Updated: 2025-12-22

## Overview

The Multi-AI Commit Workflow provides fully automated code review, testing, and auto-fix capabilities using a pipeline of AI models:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Claude    │ ──▶ │   OpenAI    │ ──▶ │   Tests     │ ──▶ │  Auto-Fix   │
│  (Analyze)  │     │  (Review)   │     │ (All Levels)│     │  (Claude)   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
      │                   │                   │                   │
      ▼                   ▼                   ▼                   ▼
   Report             Report              Report              Commits
```

## Quick Start

### Run Locally

```bash
# Full workflow on git diff
./scripts/ai-workflow/run-workflow.sh --diff

# Specific stages only
./scripts/ai-workflow/run-workflow.sh --stages review,test --diff

# Dry run to preview actions
./scripts/ai-workflow/run-workflow.sh --diff --dry-run
```

### Run Individual Stages

```bash
# Claude analysis
./scripts/ai-workflow/primary-claude.sh --diff

# OpenAI review
./scripts/ai-workflow/review-openai.sh --diff --checks "security,performance"

# Run tests
./scripts/ai-workflow/test-runner.sh --levels unit,integration --coverage

# Auto-fix from review report
./scripts/ai-workflow/auto-fix-loop.sh --issues reports/ai-workflow/review-*.json
```

## Architecture

### Stage 1: Claude Analysis (`primary-claude.sh`)

- **Model**: Claude Sonnet 4.5
- **Purpose**: Analyze code changes for potential issues
- **Capabilities**:
  - Code quality assessment
  - Bug detection
  - Security vulnerability identification
  - Performance concerns

### Stage 2: OpenAI Review (`review-openai.sh`)

- **Model**: GPT-4o
- **Purpose**: Comprehensive code review
- **Check Categories**:
  - `quality` - Readability, maintainability, DRY, complexity
  - `security` - Injection, credentials, data exposure
  - `performance` - Algorithms, N+1, memory, blocking
  - `best_practices` - Error handling, logging, types

### Stage 3: Testing (`test-runner.sh`)

- **Frameworks**: pytest, jest, mocha, native bash
- **Test Levels**:
  - `unit` - Function/module level tests
  - `integration` - Module interaction tests
  - `e2e` - End-to-end workflow tests
- **Features**:
  - Coverage reporting
  - Threshold enforcement
  - Factory.ai integration (optional)

### Stage 4: Auto-Fix (`auto-fix-loop.sh`)

- **Model**: Claude Sonnet 4.5
- **Process**:
  1. Parse issues from review report
  2. Generate fix using Claude
  3. Apply fix and verify syntax
  4. Re-run review to confirm
  5. Commit if configured
- **Safety**:
  - Automatic rollback on verification failure
  - Maximum 3 iterations default
  - Backup files before modification

## Configuration

### Environment Variables

```bash
# Required for Claude stages
export ANTHROPIC_API_KEY="your-key"

# Required for OpenAI review
export OPENAI_API_KEY="your-key"

# Optional for Gemini fallback
export GOOGLE_API_KEY="your-key"
```

### Configuration File

Edit `config/multi-ai-workflow.yaml`:

```yaml
models:
  primary:
    name: "claude"
    model: "claude-sonnet-4-20250514"
  reviewer:
    name: "openai"
    model: "gpt-4o"

stages:
  review:
    checks:
      - code_quality
      - security
      - performance
    severity_threshold: "warning"

  testing:
    levels:
      - unit
      - integration
      - e2e
    coverage_threshold: 80

auto_fix:
  enabled: true
  max_iterations: 3
  commit_fixes: true
```

## GitHub Actions Integration

The workflow automatically triggers on:
- Push to `main`, `develop`, `feature/*`
- Pull requests to `main`, `develop`

### Required Secrets

Add these in GitHub → Settings → Secrets:

- `ANTHROPIC_API_KEY` - For Claude stages
- `OPENAI_API_KEY` - For OpenAI review

### Workflow File

Located at `.github/workflows/multi-ai-review.yml`

### PR Comments

The workflow automatically posts review results as PR comments:

```
## 🤖 AI Code Review Results

| Metric | Count |
|--------|-------|
| ❌ Errors | 2 |
| ⚠️ Warnings | 5 |

### 📄 src/main.py
Score: 7/10

- ❌ **security**: SQL injection risk in query function
  - Line: 42
  - Fix: Use parameterized queries

- ⚠️ **performance**: Inefficient loop detected
  - Line: 78
  - Fix: Use list comprehension
```

## Reports

All reports are saved to `reports/ai-workflow/`:

```
reports/ai-workflow/
├── analyze-20251222-143025.json    # Claude analysis
├── review-20251222-143045.json     # OpenAI review
├── test-20251222-143102.json       # Test results
├── autofix-20251222-143130.json    # Auto-fix results
└── workflow-20251222-143025.json   # Combined summary
```

### Report Format

```json
{
  "status": "passed|warnings|failed",
  "timestamp": "2025-12-22T14:30:25Z",
  "stage": "review-openai",
  "summary": {
    "errors": 0,
    "warnings": 3
  },
  "reviews": [
    {
      "file": "src/main.py",
      "overall_score": 8,
      "findings": [...],
      "recommendation": "approve"
    }
  ]
}
```

## Scripts Reference

### run-workflow.sh

Main entry point that orchestrates all stages.

```bash
./scripts/ai-workflow/run-workflow.sh [OPTIONS]

Options:
  -s, --stages STAGES       Stages to run: analyze,review,test,fix
  -d, --diff                Use git diff for file detection
  -f, --files FILES         Specific files to process
  --no-fix                  Skip auto-fix stage
  --no-commit               Don't commit auto-fixes
  --fix-iterations N        Max auto-fix iterations (default: 3)
  --coverage-threshold N    Test coverage threshold (default: 80)
  -n, --dry-run             Preview without changes
  -v, --verbose             Detailed output
```

### primary-claude.sh

Claude-based code analysis and fix generation.

```bash
./scripts/ai-workflow/primary-claude.sh [OPTIONS]

Options:
  -d, --diff                Analyze git diff
  -f, --files FILES         Specific files
  -i, --issue ISSUE         Fix specific issue
  -r, --report FILE         Output report path
  -n, --dry-run             Preview mode
```

### review-openai.sh

OpenAI GPT-4o code review.

```bash
./scripts/ai-workflow/review-openai.sh [OPTIONS]

Options:
  -d, --diff                Review git diff
  -f, --files FILES         Specific files
  -c, --checks CHECKS       Categories: quality,security,performance,best_practices
  -s, --severity LEVEL      Minimum: error,warning,info
  -r, --report FILE         Output report path
```

### test-runner.sh

Comprehensive test execution.

```bash
./scripts/ai-workflow/test-runner.sh [OPTIONS]

Options:
  -l, --levels LEVELS       Test levels: unit,integration,e2e
  -c, --coverage            Enable coverage reporting
  -t, --threshold PCT       Coverage threshold (default: 80)
  -f, --framework FW        Force: pytest,jest,mocha,native
  --use-factory             Use Factory.ai droids
  -r, --report FILE         Output report path
```

### auto-fix-loop.sh

Automated issue fixing with re-review.

```bash
./scripts/ai-workflow/auto-fix-loop.sh [OPTIONS]

Options:
  -i, --issues FILE         Issues JSON from review stage
  -m, --max-iterations N    Max fix attempts (default: 3)
  --commit                  Auto-commit fixes
  --commit-prefix PREFIX    Commit message prefix
  -n, --dry-run             Preview mode
  -r, --report FILE         Output report path
```

## Propagating to Other Repositories

To use this workflow in other repositories:

1. Copy the scripts:
   ```bash
   cp -r scripts/ai-workflow /path/to/other-repo/scripts/
   cp config/multi-ai-workflow.yaml /path/to/other-repo/config/
   cp .github/workflows/multi-ai-review.yml /path/to/other-repo/.github/workflows/
   ```

2. Or use the propagation script:
   ```bash
   ./scripts/propagate_ai_workflow.sh  # (to be created)
   ```

## Troubleshooting

### API Rate Limits

The scripts include built-in rate limiting (1 second delay between API calls). If you hit rate limits:

1. Increase `rate_limit_delay_ms` in config
2. Reduce `max_files_per_run`
3. Run on fewer files at once

### Missing Dependencies

```bash
# For pytest
pip install pytest pytest-cov pytest-json-report

# For jest
npm install --save-dev jest

# For jq (JSON processing)
sudo apt-get install jq  # Linux
brew install jq          # macOS
```

### Authentication Errors

Verify your API keys:
```bash
# Test Claude
curl -H "x-api-key: $ANTHROPIC_API_KEY" https://api.anthropic.com/v1/messages

# Test OpenAI
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```

## Best Practices

1. **Start with Dry Run**: Use `--dry-run` to preview before actual execution
2. **Review Auto-Fixes**: Even with auto-commit, review the changes
3. **Tune Severity**: Start with `error` only, then add `warning`
4. **Monitor Costs**: API calls have costs; use selectively on large repos
5. **Incremental Adoption**: Start with review only, then add testing, then auto-fix

## Related Documentation

- [AI Agent Guidelines](AI_AGENT_GUIDELINES.md)
- [AI Development Tools](AI_development_tools.md)
- [Development Workflow](../workflow/DEVELOPMENT_WORKFLOW.md)
- [Testing Standards](../testing/baseline-testing-standards.md)
