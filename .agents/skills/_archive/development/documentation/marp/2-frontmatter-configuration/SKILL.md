---
name: marp-2-frontmatter-configuration
description: 'Sub-skill of marp: 2. Frontmatter Configuration (+4).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 2. Frontmatter Configuration (+4)

## 2. Frontmatter Configuration


```markdown
---
marp: true
title: Project Presentation
description: Quarterly review for Q4 2025
author: Your Name
theme: default
paginate: true
header: 'Company Name'
footer: 'Confidential - Internal Use Only'

*See sub-skills for full details.*

## 3. Themes and Styling


```markdown
---
marp: true
theme: default
---

<!-- Available built-in themes: default, gaia, uncover -->

# Default Theme


*See sub-skills for full details.*

## 4. Custom CSS Theme


```css
/* themes/custom.css */

/* @theme custom-theme */
@import 'default';

section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-family: 'Inter', sans-serif;

*See sub-skills for full details.*

## 5. Directives and Classes


```markdown
---
marp: true
---

<!-- Local directive (applies to current slide only) -->
<!-- _class: lead -->
<!-- _backgroundColor: #2563eb -->
<!-- _color: white -->


*See sub-skills for full details.*

## 6. Speaker Notes


```markdown
---
marp: true
---

# Presentation Title

Overview of topics

<!--

*See sub-skills for full details.*
