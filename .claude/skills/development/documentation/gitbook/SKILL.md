---
name: gitbook
version: 1.0.0
description: Publish documentation and books with GitBook including spaces, collections,
  variants, Git sync, collaboration, and API integration
author: workspace-hub
category: development
type: skill
capabilities:
- Documentation publishing
- Spaces and collections management
- Content variants (versions)
- Git synchronization
- Team collaboration
- API integration
- Custom domains
- Analytics
tools:
- gitbook-api
- git
- curl
- python-requests
tags:
- gitbook
- documentation
- publishing
- git-sync
- collaboration
- api
platforms:
- web
- api
- git
related_skills:
- mkdocs
- docusaurus
- sphinx
- pandoc
see_also:
- gitbook-getting-started
- gitbook-user-guide
- gitbook-api-reference
- gitbook-example-1-documentation-site-builder
---

# GitBook

## When to Use

### USE GitBook when:

- **Team documentation** - Collaborative docs with multiple editors
- **Product documentation** - User guides, API docs, tutorials
- **Knowledge bases** - Internal wikis and knowledge management
- **Multi-version docs** - Maintain docs for different product versions
- **Git-based workflow** - Sync docs with GitHub/GitLab
- **Custom branding** - Need custom domains and styling
- **Access control** - Restrict docs to authenticated users

### DON'T USE GitBook when:

- **Complex code docs** - Use Sphinx for Python API docs
- **Static site control** - Use MkDocs or Docusaurus
- **Offline-first** - GitBook is primarily cloud-hosted
- **Self-hosted required** - GitBook is SaaS (legacy self-hosted deprecated)

## Prerequisites

### GitBook Account Setup

```bash
# 1. Sign up at https://www.gitbook.com/
# 2. Create an organization (or use personal space)
# 3. Generate API token at https://app.gitbook.com/account/developer

export GITBOOK_API_TOKEN="gb_api_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

curl -s -H "Authorization: Bearer $GITBOOK_API_TOKEN" \
    "https://api.gitbook.com/v1/user" | jq '.id, .displayName'
```

### Git Sync Setup

```bash
# In your GitBook space settings:
# 1. Go to Integrations > Git Sync
# 2. Connect GitHub/GitLab account
# 3. Select repository and branch
```

*See sub-skills for full details.*

### Python Setup

```bash
uv add requests python-dateutil
```

## Resources

- **GitBook Documentation**: https://docs.gitbook.com/
- **GitBook API Reference**: https://developer.gitbook.com/
- **Git Sync Guide**: https://docs.gitbook.com/integrations/git-sync
- **Custom Domains**: https://docs.gitbook.com/published-documentation/custom-domain

## Version History

- **1.0.0** (2026-01-17): Initial release — spaces management, collections, variants,
  Git sync, collaboration, custom domains, migration tools, analytics, GitHub Actions

## Sub-Skills

- [1. API Authentication (+1)](1-api-authentication/SKILL.md)
- [3. Content Management (+1)](3-content-management/SKILL.md)
- [5. Content Variants (Versions) (+1)](5-content-variants-versions/SKILL.md)
- [GitHub Actions for Git Sync (+1)](github-actions-for-git-sync/SKILL.md)
- [1. Structure Content Properly (+3)](1-structure-content-properly/SKILL.md)
- [Common Issues](common-issues/SKILL.md)
- [Getting Started](getting-started/SKILL.md)
- [User Guide](user-guide/SKILL.md)
- [API Reference](api-reference/SKILL.md)
- [Example 1: Documentation Site Builder (+2)](example-1-documentation-site-builder/SKILL.md)
