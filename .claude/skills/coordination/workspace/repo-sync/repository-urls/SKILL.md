---
name: workspace-repo-sync-repository-urls
description: 'Sub-skill of workspace-repo-sync: Repository URLs (+2).'
version: 1.2.0
category: coordination
type: reference
scripts_exempt: true
---

# Repository URLs (+2)

## Repository URLs


Configure in `config/repos.conf`:

```bash
# Repository URL Configuration
digitalmodel=git@github.com:username/digitalmodel.git
energy=git@github.com:username/energy.git
aceengineer-admin=git@github.com:username/aceengineer-admin.git
```


## Categories


Defined in `.gitignore`:

```bash
digitalmodel/        # Work
energy/              # Work
personal-project/    # Personal
mixed-repo/          # Work, Personal
```


## Configure Repositories


```bash
# Edit configuration
./scripts/repository_sync config

# Refresh repository list
./scripts/repository_sync refresh
```
