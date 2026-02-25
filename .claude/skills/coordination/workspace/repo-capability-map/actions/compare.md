# Repo Capability Map: Compare Action

> Side-by-side capability comparison between two repositories.

## Trigger

Invoked when `/repo-capability-map compare <repo1> <repo2>` is called.

## Prerequisites

Both repositories must exist in the workspace. Scan data for both repos is required -- if missing, the `scan` action runs for each repo first.

## Procedure

### Step 1 -- Validate Inputs

- Verify both repo names are valid directories or submodules
- Confirm they are distinct (comparing a repo to itself is a no-op)
- If either repo doesn't exist, error with available repo list

### Step 2 -- Scan Both Repos

Run the `scan` action for each repo if profiles don't already exist. Collect:
- Domain classifications
- Capability areas with maturity levels
- Key dependencies
- Activity status

### Step 3 -- Build Comparison Matrix

Create a unified list of all capability areas found across both repos:

```
CAPABILITY COMPARISON: <repo1> vs <repo2>
==========================================

| Capability Area        | <repo1>     | <repo2>        |
|------------------------|-------------|----------------|
| OrcaFlex Modeling      | Mature      | --             |
| Mooring Design         | Mature      | Nascent        |
| Data Pipelines         | --          | Established    |
| Test Coverage          | Established | Emerging       |
| CI/CD Automation       | Emerging    | Established    |
```

Use `--` for capabilities not present in a repo.

### Step 4 -- Analyze Overlaps and Differences

Classify each capability area:

| Category | Definition |
|----------|-----------|
| **Unique to repo1** | Present only in repo1 |
| **Unique to repo2** | Present only in repo2 |
| **Shared (repo1 leads)** | Both have it, repo1 at higher maturity |
| **Shared (repo2 leads)** | Both have it, repo2 at higher maturity |
| **Shared (equal)** | Both have it at same maturity level |

### Step 5 -- Domain Overlap Analysis

Compare domain classifications:

```
DOMAIN OVERLAP
  <repo1> domains: ENG, INFRA
  <repo2> domains: DATA, INFRA
  Shared domains:  INFRA
  Unique to <repo1>: ENG
  Unique to <repo2>: DATA
```

### Step 6 -- Dependency Analysis

Identify if either repo depends on the other:
- Shared dependencies (same libraries/tools)
- Direct dependencies (one imports/uses the other)
- Complementary capabilities (one produces what the other consumes)

### Step 7 -- Generate Summary

```
COMPARISON SUMMARY
  <repo1>: 8 capabilities across 2 domains (avg maturity: 3.1)
  <repo2>: 6 capabilities across 2 domains (avg maturity: 2.5)

  Shared capabilities: 3
  Unique to <repo1>:   5
  Unique to <repo2>:   3

  Recommendation: These repos are [complementary/overlapping/independent]
  [If overlapping]: Consider consolidating <capability> into <suggested repo>
  [If complementary]: Consider integration points for <shared domain>
```

## Output

Console output by default. If `--format=markdown` is passed, save to:
`reports/capability-map/compare-<repo1>-vs-<repo2>-YYYY-MM-DD.md`

## Error Handling

- Repo not found: list available repos and exit
- Identical repos: warn and exit
- One repo has no capabilities detected: note as "empty or unanalyzable"
