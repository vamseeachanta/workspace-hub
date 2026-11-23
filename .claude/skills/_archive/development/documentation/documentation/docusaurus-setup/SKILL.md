---
name: documentation-docusaurus-setup
description: 'Sub-skill of documentation: Docusaurus Setup.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Docusaurus Setup

## Docusaurus Setup


```bash
# See docusaurus for complete patterns
npx create-docusaurus@latest my-docs classic

cd my-docs

# docusaurus.config.js customization
cat > docusaurus.config.js << 'EOF'
module.exports = {
  title: 'My Documentation',

*See sub-skills for full details.*
