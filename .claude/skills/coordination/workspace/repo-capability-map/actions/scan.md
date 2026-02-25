# Repo Capability Map: Scan Action

> Extract capabilities from one or all repositories by reading declared identity, structural evidence, and behavioral signals.

## Trigger

Invoked when `/repo-capability-map scan [repo]` is called.

- No argument: scan all active repos in workspace-hub
- With `<repo>`: scan only the named repository

## Procedure

### Step 1 -- Identify Target Repos

If scanning all repos:
```bash
ls -d */ | grep -v node_modules | grep -v .git | grep -v reports | grep -v specs
```

If scanning a single repo, verify it exists as a subdirectory or submodule.

Exclude repos marked as archived or dormant unless `--include-dormant` is passed.

### Step 2 -- Read Tier 1 Sources (Declared Identity)

For each repo, attempt to read these files in order. Missing files are noted but not failures.

1. **README.md** -- Extract:
   - Project title and one-line description
   - Listed features or capabilities
   - Tech stack mentions
   - Domain keywords (engineering, data, web, etc.)

2. **CLAUDE.md** -- Extract:
   - Project rules and conventions
   - Tool and dependency references
   - Skill references
   - Domain-specific terminology

3. **.agent-os/product/mission.md** -- Extract:
   - Mission statement
   - Strategic phases and their status
   - Success metrics

4. **.agent-os/product/roadmap.md** -- Extract:
   - Planned features and completion percentage
   - Current phase focus

### Step 3 -- Read Tier 2 Sources (Structural Evidence)

1. **Source directory structure**:
   ```bash
   find <repo>/src -type f -name "*.py" -o -name "*.ts" -o -name "*.js" | head -50
   ```
   - Map module names to capability areas
   - Identify sub-packages as capability signals

2. **Skills directory**:
   ```bash
   ls <repo>/.claude/skills/ 2>/dev/null
   ```
   - Each skill file = one capability signal

3. **Package metadata**:
   - `pyproject.toml`: Read `[project]` section for dependencies, entry points, description
   - `package.json`: Read `dependencies`, `scripts`, `description`

4. **Tests and docs**:
   - `tests/` exists → +1 maturity signal
   - `docs/` exists → +1 maturity signal
   - Count test files for coverage estimation

### Step 4 -- Read Tier 3 Sources (Behavioral Evidence)

1. **Recent git activity**:
   ```bash
   cd <repo> && git log --oneline -30 --since="6 months ago"
   ```
   - Active commits → repo is alive
   - Commit messages reveal development focus areas

2. **Scripts directory**:
   ```bash
   ls <repo>/scripts/ 2>/dev/null
   ```
   - Automation scripts = operational maturity signal

3. **Data and config**:
   - `data/` directory → data domain involvement
   - `config/` directory → configurable system

### Step 5 -- Classify Domain

Map extracted signals to the capability taxonomy:

| Signal Pattern | Domain |
|---------------|--------|
| orcaflex, mooring, fatigue, structural, FEA | `ENG` |
| pandas, polars, dataset, analytics, visualization | `DATA` |
| react, nextjs, html, css, frontend, website | `WEB` |
| invoice, admin, client, CRM, operations | `BIZ` |
| docker, CI, deploy, package, utility, template | `INFRA` |
| media, resume, documentation, knowledge, training | `KNOW` |
| investment, portfolio, financial, ROI, valuation | `FIN` |

A repo may belong to multiple domains. Assign primary and secondary domains.

If no known domain matches, create a new domain ID using a 3-4 letter uppercase abbreviation.

### Step 6 -- Assess Maturity

For each capability area within a repo, assign maturity based on artifact presence:

| Artifact | Maturity Contribution |
|----------|----------------------|
| Mentioned in README/mission only | Level 1 (Nascent) |
| Source files exist, <50% test coverage | Level 2 (Emerging) |
| Source + tests + docs/CLI present | Level 3 (Established) |
| Source + 80%+ coverage + skills + production use | Level 4 (Mature) |

Use the **highest level for which all criteria are met**.

### Step 7 -- Build Capability Profile

For each repo, produce a structured profile following the `templates/repo-profile.md` template:

- Repository name and description
- Primary and secondary domains
- List of capability areas with maturity levels
- Key dependencies and integration points
- Activity status (active, dormant, archived)

### Step 8 -- Aggregate by Domain

Group all repo profiles by their primary domain. Within each domain:

- List all capability areas across repos
- Identify the "lead repo" for each capability (highest maturity)
- Note overlapping capabilities between repos
- Flag capability areas with no lead repo (maturity < 2)

## Output

Return the aggregated capability map as structured data for use by the `report` or `gaps` action.

For console display, output a summary table per domain (see SKILL.md output format).

## Error Handling

- Missing repos: warn and skip
- Unreadable files: note in profile as "access denied"
- Empty repos: classify as Nascent across all detected domains
- Git errors: fall back to file-system-only analysis
