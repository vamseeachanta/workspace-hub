# Review by Claude
# Source: commit-318fa23d
# Type: implementation
# Date: 20260213T155230Z

[Claude review requires interactive session or API call]
## Content to Review
```
Commit: 318fa23d
commit 318fa23dda2c0fcdb87158c84ca0613d052c1bc9
Author: Vamsee Achanta <achantav@gmail.com>
Date:   Fri Feb 13 09:21:26 2026 -0600

    fix(orcaflex): add complete wing type aerofoil data to wind turbine template
    
    Address Gemini cross-review P2: wind turbine template referenced wing
    types AF01-AF30 without defining them. Added all 30 aerofoil polar
    tables (200 angle-of-attack points each) from K02 monolithic model.
    
    Template is now self-contained with no external dependencies.
    
    Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

 .../orcaflex/library/templates/audit_results.yaml  |    2 +-
 .../library/templates/wind_turbine_fixed/spec.yml  | 6126 +++++++++++++++++++-
 2 files changed, 6122 insertions(+), 6 deletions(-)
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
