---
name: docusaurus-build-fails-with-module-not-found
description: 'Sub-skill of docusaurus: Build Fails with Module Not Found (+6).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Build Fails with Module Not Found (+6)

## Build Fails with Module Not Found


```bash
rm -rf node_modules .docusaurus build
npm install
npm run build
```


## Hot Reload Not Working


```bash
npm run clear
npm run start
```


## Broken Links


```javascript
module.exports = {
  onBrokenLinks: 'warn', // Change from 'throw' for debugging
};
```


## i18n Build Issues


```bash
npm run build -- --locale en
npm run write-translations -- --locale fr
```


## Debug Mode


```bash
DEBUG=docusaurus* npm run build
npm run start -- --port 3001
```


## Algolia Indexing Issues


```javascript
// Check Algolia configuration
module.exports = {
  themeConfig: {
    algolia: {
      appId: 'YOUR_APP_ID',       // Not the API key
      apiKey: 'SEARCH_ONLY_KEY',  // Search-only API key
      indexName: 'your_index',
      debug: true,                // Enable debug mode
    },
  },
};
```


## Version Dropdown Not Showing


```javascript
// Ensure versions.json exists and navbar is configured
module.exports = {
  themeConfig: {
    navbar: {
      items: [
        { type: 'docsVersionDropdown', position: 'right' },
      ],
    },
  },
};
```
