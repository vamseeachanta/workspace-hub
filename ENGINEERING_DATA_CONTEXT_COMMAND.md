# Engineering Data Context Command

## Overview

The `/engineering-data-context` command generates comprehensive context for engineering data repositories, including:
- Recursive folder processing
- Web research integration
- Module-aware context distribution
- Agent-friendly data formats

## Installation

Already installed in all repositories via `.agent-os/commands/engineering_data_context.py`

## Usage

### Generate Context for a Folder

```bash
# Basic context generation
/engineering-data-context generate --folder ./data

# With deep web research
/engineering-data-context generate --folder ./data --deep-research

# With module assignment
/engineering-data-context generate --folder ./data --modules

# All features
/engineering-data-context generate --folder ./data --deep-research --modules
```

### Enhance Existing Context

```bash
# Add specific research topics
/engineering-data-context enhance --folder ./data --research-topics "API documentation" "best practices"
```

### Query Context

```bash
# Search for specific data
/engineering-data-context query --context "sensor measurements"
```

### Export Context

```bash
# Export in different formats
/engineering-data-context export --format json
/engineering-data-context export --format yaml
/engineering-data-context export --format markdown
```

## Output Structure

Context is saved in `.agent-os/data-context/` with:

```
.agent-os/data-context/
├── context.db                 # SQLite database
├── exports/
│   └── [folder_name]/
│       ├── context.json       # All contexts
│       ├── context.yaml       # YAML format
│       ├── README.md          # Human-readable docs
│       └── modules/           # Module-specific contexts
│           └── [module]_context.json
```

## Features

### Data Type Recognition

Automatically recognizes:
- Tabular data (CSV, Excel)
- Structured data (JSON, XML)
- Scientific data (HDF5, NetCDF)
- Database files (SQLite, DB)
- CAD/Engineering files (STEP, IGES, STL)
- Geographic data (GeoJSON, Shapefile)

### Schema Extraction

Automatically extracts:
- Column names and types from CSVs
- JSON/YAML structure
- Database table schemas
- Row/record counts

### Web Research

Performs research for:
- Technical documentation
- Data format specifications
- Best practices
- Industry standards
- API references

### Module Assignment

Automatically assigns data to modules based on:
- File paths
- Tags and keywords
- Module naming patterns

## Agent-Friendly Formats

All context is saved in formats optimized for AI agents:
- JSON with clear structure
- YAML for configuration
- Markdown for documentation
- SQLite for queries

## Benefits

1. **Comprehensive Understanding**: Full context of all engineering data
2. **Reusability**: Context can be reused across projects
3. **Research Integration**: Augments local data with web knowledge
4. **Module Organization**: Keeps context organized by module
5. **Easy Retrieval**: Query interface for finding specific data

## Example Workflow

```bash
# 1. Generate initial context
/engineering-data-context generate --folder ./engineering_data --deep-research --modules

# 2. Review generated context
cat .agent-os/data-context/exports/engineering_data/README.md

# 3. Enhance with specific research
/engineering-data-context enhance --folder ./engineering_data --research-topics "sensor calibration"

# 4. Query for specific data
/engineering-data-context query --context "temperature sensor"

# 5. Use context in other commands
# The context is now available for all AI agents working on this repository
```

## Integration with Other Commands

The generated context integrates with:
- `/create-spec` - Uses data context for specifications
- `/execute-tasks` - Accesses data schemas for implementation
- `/test-automation-enhanced` - Uses data formats for test generation

---

Last Updated: $(date)
Synced to: All 25 repositories
