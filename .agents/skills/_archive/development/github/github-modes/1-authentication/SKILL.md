---
name: github-modes-1-authentication
description: 'Sub-skill of github-modes: 1. Authentication (+3).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 1. Authentication (+3)

## 1. Authentication

- Use `gh auth login` for initial setup
- Store tokens securely in GitHub Secrets
- Use GITHUB_TOKEN in workflows
- Rotate tokens regularly


## 2. Rate Limiting

- Batch operations when possible
- Use GraphQL for complex queries
- Implement exponential backoff
- Cache API responses


## 3. Workflow Design

- Use reusable workflows
- Implement proper error handling
- Add meaningful commit messages
- Follow semantic versioning


## 4. Security

- Enable branch protection
- Require PR reviews
- Use signed commits
- Enable security scanning
