---
name: nextflow-pipelines-docker-issues
description: 'Sub-skill of nextflow-pipelines: Docker issues (+2).'
version: 1.0.0
category: science
type: reference
scripts_exempt: true
---

# Docker issues (+2)

## Docker issues


| Problem | Fix |
|---------|-----|
| Not installed | Install from https://docs.docker.com/get-docker/ |
| Permission denied | `sudo usermod -aG docker $USER` then re-login |
| Daemon not running | `sudo systemctl start docker` |

## Nextflow issues


| Problem | Fix |
|---------|-----|
| Not installed | `curl -s https://get.nextflow.io \| bash && mv nextflow ~/bin/` |
| Version < 23.04 | `nextflow self-update` |

## Java issues


| Problem | Fix |
|---------|-----|
| Not installed / < 11 | `sudo apt install openjdk-11-jdk` |

**Do not proceed until all checks pass.** For HPC/Singularity, see [references/troubleshooting.md](references/troubleshooting.md).

---
