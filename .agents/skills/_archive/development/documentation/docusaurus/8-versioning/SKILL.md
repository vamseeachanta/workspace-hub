---
name: docusaurus-8-versioning
description: 'Sub-skill of docusaurus: 8. Versioning (+5).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 8. Versioning (+5)

## 8. Versioning


```bash
# Create a new version
npm run docusaurus docs:version 1.0

# Creates:
# - versioned_docs/version-1.0/
# - versioned_sidebars/version-1.0-sidebars.json
# - versions.json
```


*See sub-skills for full details.*

## 9. Internationalization (i18n)


```javascript
// docusaurus.config.js
module.exports = {
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'fr', 'de'],
    localeConfigs: {
      en: { label: 'English', htmlLang: 'en-US' },
      fr: { label: 'Francais', htmlLang: 'fr-FR' },
    },

*See sub-skills for full details.*

## 10. Search with Algolia


```javascript
// docusaurus.config.js
module.exports = {
  themeConfig: {
    algolia: {
      appId: 'YOUR_APP_ID',
      apiKey: 'YOUR_SEARCH_API_KEY',
      indexName: 'your_index_name',
      contextualSearch: true,
    },

*See sub-skills for full details.*

## 11. Custom CSS


```css
/* src/css/custom.css */
:root {
  --ifm-color-primary: #2e8555;
  --ifm-code-font-size: 95%;
  --ifm-font-family-base: 'Inter', sans-serif;
}

[data-theme='dark'] {
  --ifm-color-primary: #25c2a0;
}

.navbar { box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
```

## 12. GitHub Pages Deployment


```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

permissions:
  contents: read

*See sub-skills for full details.*

## 13. Vercel/Netlify Deployment


```json
// vercel.json
{
  "buildCommand": "npm run build",
  "outputDirectory": "build",
  "framework": "docusaurus-2"
}
```

```toml
# netlify.toml
[build]
  command = "npm run build"
  publish = "build"
```
