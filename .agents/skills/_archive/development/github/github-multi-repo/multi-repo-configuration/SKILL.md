---
name: github-multi-repo-multi-repo-configuration
description: 'Sub-skill of github-multi-repo: Multi-Repo Configuration.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Multi-Repo Configuration

## Multi-Repo Configuration


```yaml
# .swarm/multi-repo.yml
version: 1
organization: my-org
repositories:
  - name: frontend
    url: github.com/my-org/frontend
    role: ui
    agents: [coder, designer, tester]

  - name: backend
    url: github.com/my-org/backend
    role: api
    agents: [architect, coder, tester]

  - name: shared
    url: github.com/my-org/shared
    role: library
    agents: [analyst, coder]

coordination:
  topology: hierarchical
  communication: webhook
  memory: redis://shared-memory


*See sub-skills for full details.*
