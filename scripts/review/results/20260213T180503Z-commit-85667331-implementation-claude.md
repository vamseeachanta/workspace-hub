# Review by Claude
# Source: commit-85667331
# Type: implementation
# Date: 20260213T180503Z

[Claude review requires interactive session or API call]
## Content to Review
```
Commit: 85667331
commit 8566733129da1a30d9343816c74b185e4252e3c3
Author: Vamsee Achanta <achantav@gmail.com>
Date:   Fri Feb 13 08:43:29 2026 -0600

    feat(orcaflex): add riser steep wave and pliant wave templates
    
    WRK-126 Phase 1: Complete the riser template set with steep wave and
    pliant wave configurations curated from tier2_fast specs. Both score
    100/100 quality with proven statics convergence (0.14s and 0.24s).
    
    Templates: 6 -> 8, Riser set: catenary, lazy wave, pliant wave, steep wave
    
    Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

 .../orcaflex/library/templates/audit_results.yaml  | 1091 +-------------------
 .../orcaflex/library/templates/catalog.yaml        |   31 +
 .../library/templates/riser_pliant_wave/spec.yml   |  183 ++++
 .../library/templates/riser_steep_wave/spec.yml    |  142 +++
 4 files changed, 382 insertions(+), 1065 deletions(-)
```
## Review Prompt
# Implementation Review Prompt

You are reviewing code changes (implementation) for a software engineering project. Evaluate the following:

## Review Criteria

1. **Correctness**: Does the code do what it's supposed to? Are there logic errors?
2. **Security**: Are there injection vulnerabilities, hardcoded secrets, or auth issues?
3. **Testing**: Are the changes adequately tested? Are edge cases covered?
4. **Style**: Does the code follow project conventions (snake_case for Python, etc.)?
5. **Performance**: Are there obvious performance issues (N+1 queries, unbounded loops)?
6. **Simplicity**: Is the code as simple as it could be? Is there over-engineering?

## Output Format

### Verdict: APPROVE | REQUEST_CHANGES | REJECT

### Summary
[1-3 sentence overall assessment]

### Issues Found
- [P1] Critical: [file:line] [description]
- [P2] Important: [file:line] [description]
- [P3] Minor: [file:line] [description]

### Suggestions
- [suggestion]

### Test Coverage Assessment
- [covered/not covered]
