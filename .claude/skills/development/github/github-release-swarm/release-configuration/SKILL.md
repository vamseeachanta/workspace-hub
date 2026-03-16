---
name: github-release-swarm-release-configuration
description: 'Sub-skill of github-release-swarm: Release Configuration.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Release Configuration

## Release Configuration


```yaml
# .github/release-swarm.yml
version: 1
release:
  versioning:
    strategy: semantic
    breaking-keywords: ["BREAKING", "!"]

  changelog:
    sections:
      - title: "Features"
        labels: ["feature", "enhancement"]
      - title: "Bug Fixes"
        labels: ["bug", "fix"]
      - title: "Documentation"
        labels: ["docs", "documentation"]

  artifacts:
    - name: npm-package
      build: npm run build
      publish: npm publish

    - name: docker-image
      build: docker build -t app:$VERSION .
      publish: docker push app:$VERSION

*See sub-skills for full details.*
