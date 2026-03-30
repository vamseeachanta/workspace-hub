---
name: obsidian-table-of-books-with-ratings
description: 'Sub-skill of obsidian: Table of books with ratings.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Table of books with ratings

## Table of books with ratings


```dataview
TABLE author, rating, status
FROM #book
SORT rating DESC
```
