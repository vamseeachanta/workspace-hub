# Scripts Directory

> Organized by discipline for discoverability.

## Entry Points

| Script | Description |
|--------|-------------|
| `workspace` | Main workspace CLI |
| `repository_sync` | Repository synchronization |
| `setup-claude-env.sh` | Claude environment setup |
| `operations/compliance/check_governance.sh` | WRK/spec governance checks |
| `operations/compliance/audit_skill_symlink_policy.sh` | Skills link-only governance check |

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
