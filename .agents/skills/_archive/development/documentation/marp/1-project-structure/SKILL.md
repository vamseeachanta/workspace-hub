---
name: marp-1-project-structure
description: 'Sub-skill of marp: 1. Project Structure (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 1. Project Structure (+1)

## 1. Project Structure


```
presentations/
├── slides/
│   ├── quarterly-review.md
│   └── product-demo.md
├── themes/
│   └── corporate.css
├── images/
├── dist/
├── .marprc.yml
└── package.json
```


## 2. Slide Template


```markdown
---
marp: true
theme: corporate
paginate: true
header: 'Company | Title'
footer: '2026'
---

<!-- _class: title -->
<!-- _paginate: false -->

# Presentation Title

**Presenter Name** | *Date*

---

# Agenda

1. Topic One
2. Topic Two
3. Q&A

---

<!-- _class: section -->

# Section 1

---
