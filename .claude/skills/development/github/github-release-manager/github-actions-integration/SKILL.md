---
name: github-release-manager-github-actions-integration
description: 'Sub-skill of github-release-manager: GitHub Actions Integration.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# GitHub Actions Integration

## GitHub Actions Integration


```yaml
name: Release Management
on:
  pull_request:
    branches: [main]
    paths: ['**/package.json', 'CHANGELOG.md']

jobs:
  release-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      - name: Install and Test
        run: |
          npm install
          npm test
          npm run lint
          npm run build
      - name: Validate Release
```
