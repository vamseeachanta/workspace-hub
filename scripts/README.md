# Scripts Directory

> Organized by discipline for discoverability.

## Entry Points

| Script | Description |
|--------|-------------|
| `workspace` | Main workspace CLI |
| `repository_sync` | Repository synchronization |
| `setup-claude-env.sh` | Claude environment setup |

## Discipline Directories

| Directory | Purpose |
|-----------|---------|
| `_core/` | Foundation utilities (bash, cli helpers) |
| `ai/` | AI tools and assessments |
| `coordination/` | Workspace coordination, routing, context |
| `data/` | Data processing and batch tools |
| `development/` | Development workflows, testing, AI review |
| `operations/` | Infrastructure, compliance, monitoring |
| `_archive/` | Deprecated scripts |

## Usage

Most scripts should be run from the workspace root:

```bash
./scripts/workspace --help
./scripts/repository_sync --help
```
