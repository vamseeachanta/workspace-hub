# Review by Claude
# Source: commit-da181dd9
# Type: implementation
# Date: 20260213T155221Z

[Claude review requires interactive session or API call]
## Content to Review
```
Commit: da181dd9
commit da181dd90fd00bf2dd411d30e33a4c2217fb8acb
Author: Vamsee Achanta <achantav@gmail.com>
Date:   Fri Feb 13 09:02:50 2026 -0600

    feat(orcaflex): add CALM buoy moored template from C06
    
    WRK-126 Phase 2: Discretised CALM buoy with 6-leg chain mooring,
    supply vessel with RAOs, product loadhose, hawser, and yaw-only
    swivel constraint. 887 lines, 100/100 quality, schema valid.
    
    Key components: 8 6D buoys (CALM Top + Main + 6 radials), 8 lines
    (6 mooring + loadhose + hawser), vessel type with displacement/load
    RAOs, wave drift QTFs, and added mass/damping matrices.
    
    Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

 .../orcaflex/library/templates/audit_results.yaml  |  43 +-
 .../library/templates/calm_buoy_moored/spec.yml    | 887 +++++++++++++++++++++
 .../orcaflex/library/templates/catalog.yaml        |  17 +
 3 files changed, 933 insertions(+), 14 deletions(-)
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
