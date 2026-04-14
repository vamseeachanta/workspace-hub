# Workspace Hub File Structure

> **Last Updated:** 2026-04-02
>
> Visual representation of the workspace-hub directory structure.

## Top-Level Directory Structure

```mermaid
graph TB
    WH[workspace-hub/]

    WH --> CONFIG["📁 Configuration<br/>────────────<br/>.claude/<br/>.codex/<br/>.gemini/<br/>config/<br/>AGENTS.md"]

    WH --> TIER1["🚀 Tier-1 Repos<br/>────────────<br/>digitalmodel/<br/>assetutilities/<br/>assethold/<br/>worldenergydata/"]

    WH --> TIER2["📦 Tier-2 Repos<br/>────────────<br/>aceengineer-admin/<br/>aceengineer-website/<br/>aceengineer-strategy/<br/>frontierdeepwater/<br/>doris/ seanation/<br/>saipem/ rock-oil-field/<br/>OGManufacturing/<br/>client_projects/"]

    WH --> INFRA["🛠️ Infrastructure<br/>────────────<br/>scripts/<br/>tests/<br/>templates/<br/>tools/<br/>src/"]

    WH --> DATA["📊 Data & Knowledge<br/>────────────<br/>data/<br/>knowledge/<br/>knowledge-base/<br/>docs/<br/>reports/<br/>notes/"]

    WH --> OTHER["📂 Other<br/>────────────<br/>achantas-data/<br/>achantas-media/<br/>acma-projects/<br/>investments/<br/>hobbies/<br/>_archive/"]

    style WH fill:#f9f,stroke:#333,stroke-width:4px
    style CONFIG fill:#bbf,stroke:#333,stroke-width:2px
    style TIER1 fill:#bfb,stroke:#333,stroke-width:2px
    style TIER2 fill:#fbf,stroke:#333,stroke-width:2px
    style INFRA fill:#ffb,stroke:#333,stroke-width:2px
    style DATA fill:#bff,stroke:#333,stroke-width:2px
    style OTHER fill:#ddd,stroke:#333,stroke-width:2px
```

## Claude Configuration Structure

```mermaid
graph TB
    CLAUDE[📁 .claude/]

    CLAUDE --> SKILLS["skills/<br/>568 active + 2,166 archived"]
    CLAUDE --> STATE["state/<br/>Runtime reports & data"]
    CLAUDE --> RULES["rules/<br/>Behavioral constraints"]
    CLAUDE --> GSD["get-shit-done/<br/>GSD workflow data"]
    CLAUDE --> COMMANDS["commands/<br/>Slash commands"]
    CLAUDE --> KNOWLEDGE["knowledge/<br/>Domain knowledge"]
    CLAUDE --> WORKTREES["worktrees/<br/>Git worktree configs"]
    CLAUDE --> OTHER2["agents/ config/ docs/<br/>hooks/ memory/ plans/<br/>reports/ templates/<br/>tools/ workflows/"]

    style CLAUDE fill:#f96,stroke:#333,stroke-width:3px
    style SKILLS fill:#9cf,stroke:#333,stroke-width:2px
    style GSD fill:#9fc,stroke:#333,stroke-width:2px
```

## Provider Adapter Model

```mermaid
graph LR
    AGENTS[AGENTS.md<br/>Canonical Entry Point]

    AGENTS --> CLAUDE[".claude/<br/>Claude Code adapter<br/>Skills, rules, state"]
    AGENTS --> CODEX[".codex/<br/>Codex adapter<br/>Review config"]
    AGENTS --> GEMINI[".gemini/<br/>Gemini adapter<br/>Review config"]

    style AGENTS fill:#f96,stroke:#333,stroke-width:3px
    style CLAUDE fill:#9cf,stroke:#333,stroke-width:2px
    style CODEX fill:#9fc,stroke:#333,stroke-width:2px
    style GEMINI fill:#fc9,stroke:#333,stroke-width:2px
```

## Key Directory Purposes

### 📁 Configuration
- **`.claude/`**: Claude Code config — skills, rules, state, GSD workflow
- **`.codex/`**: OpenAI Codex adapter for code review
- **`.gemini/`**: Google Gemini adapter for triggered reviews
- **`config/`**: Central configuration (schedule-tasks.yaml, quality baselines)
- **`AGENTS.md`**: Canonical entry point (Control-Plane Contract)

### 🚀 Tier-1 Repositories (Core Engineering)
- **`digitalmodel/`**: Engineering simulation (OrcaFlex, OrcaWave, FreeCAD)
- **`assetutilities/`**: Shared Python utilities
- **`assethold/`**: Asset management library
- **`worldenergydata/`**: Energy industry data and analysis

### 📦 Tier-2 Repositories (Business & Projects)
- **`aceengineer-admin/`**: Business administration automation
- **`aceengineer-website/`**: Company website (Flask)
- **`aceengineer-strategy/`**: Business strategy
- **`frontierdeepwater/`**: Marine engineering project
- **`doris/`**: Marine domain project
- **`seanation/`**: Drilling domain project
- **`saipem/`**: Construction/engineering domain
- **`rock-oil-field/`**: Oil field analysis
- **`OGManufacturing/`**: Manufacturing domain
- **`client_projects/`**: Client project collection

### 🛠️ Infrastructure
- **`scripts/`**: Automation scripts (quality checks, operations, cron)
- **`tests/`**: Test suites (pytest)
- **`templates/`**: Project templates
- **`tools/`**: Utility tools
- **`src/`**: Workspace-hub Python source

### 📊 Data & Knowledge
- **`data/`**: Shared data files
- **`knowledge/`**: Domain knowledge base
- **`knowledge-base/`**: Structured knowledge
- **`docs/`**: Documentation tree (standards, research, plans, reports)
- **`reports/`**: Generated reports
- **`notes/`**: Working notes

### 📂 Other
- **`achantas-data/`**, **`achantas-media/`**: Personal data/media
- **`acma-projects/`**: ACMA project collection
- **`investments/`**: Investment tracking
- **`hobbies/`**: Personal projects
- **`_archive/`**: Archived content

## Development Workflow

```mermaid
flowchart TB
    START[Start Development]

    START --> PLAN[Plan — explicit plan + approval]
    PLAN --> TDD[Write Tests First — TDD mandatory]
    TDD --> IMPL[Implement]
    IMPL --> COMMIT["Commit to main + push"]

    COMMIT --> REVIEW{Review needed?}
    REVIEW -->|Yes| CODEX_REVIEW["Codex reviews<br/>(AI Review Routing)"]
    REVIEW -->|No| DONE[Done]

    CODEX_REVIEW --> VERDICT{Verdict}
    VERDICT -->|APPROVE/MINOR| DONE
    VERDICT -->|MAJOR| IMPL

    style START fill:#9f9,stroke:#333,stroke-width:3px
    style DONE fill:#9f9,stroke:#333,stroke-width:3px
    style TDD fill:#99f,stroke:#333,stroke-width:2px
```

## Notes

- **AGENTS.md** is the canonical entry point — all provider adapters extend it
- **GSD workflow** is the standard task execution framework
- **GitHub Issues** are the single source of truth for task tracking
- **`uv run`** is always used for Python — never bare `python3`
- **Legacy directories** from earlier iterations have been archived — do not extend
- Projects are organized by tier (1-3) based on engineering criticality

This structure enables:
1. **Multi-provider AI** — Claude, Codex, and Gemini work from the same codebase
2. **Skills-based automation** — 568 active skills covering engineering, data, business
3. **Quality enforcement** — automated staleness, drift, and complexity checks
4. **Cron automation** — scheduled tasks via `config/schedule-tasks.yaml`
5. **TDD workflow** — tests before implementation, always
