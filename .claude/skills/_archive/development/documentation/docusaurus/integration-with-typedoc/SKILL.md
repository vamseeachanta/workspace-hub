---
name: docusaurus-integration-with-typedoc
description: 'Sub-skill of docusaurus: Integration with TypeDoc (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Integration with TypeDoc (+1)

## Integration with TypeDoc


```bash
npm install typedoc docusaurus-plugin-typedoc
```

```javascript
module.exports = {
  plugins: [
    ['docusaurus-plugin-typedoc', {
      entryPoints: ['../src/index.ts'],
      tsconfig: '../tsconfig.json',
      out: 'api',
    }],
  ],
};
```


## Integration with OpenAPI


```bash
npm install docusaurus-plugin-openapi-docs docusaurus-theme-openapi-docs
```

```javascript
module.exports = {
  plugins: [
    ['docusaurus-plugin-openapi-docs', {
      id: 'openapi',
      config: {
        petstore: {
          specPath: 'api/openapi.yaml',
          outputDir: 'docs/api',
        },
      },
    }],
  ],
  themes: ['docusaurus-theme-openapi-docs'],
};
```
