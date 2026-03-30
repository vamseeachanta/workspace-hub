---
name: obsidian-1-vault-structure-and-organization
description: 'Sub-skill of obsidian: 1. Vault Structure and Organization (+1).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 1. Vault Structure and Organization (+1)

## 1. Vault Structure and Organization


**PARA Method Structure:**
```markdown
# Vault Organization with PARA Method
#
# Projects/ - Active projects with deadlines
# Areas/    - Ongoing responsibilities
# Resources/- Reference materials
# Archive/  - Completed or inactive items

# Example folder structure:
ObsidianVault/
├── Daily Notes/           # Daily journal entries
├── Inbox/                 # Quick capture, process later
├── Projects/
│   ├── Project-Alpha/
│   │   ├── Overview.md
│   │   ├── Tasks.md
│   │   └── Meeting Notes/
│   └── Project-Beta/
├── Areas/
│   ├── Health/
│   ├── Finance/
│   ├── Career/
│   └── Learning/
├── Resources/
│   ├── Books/
│   ├── Courses/
│   ├── Articles/
│   └── Recipes/
├── Archive/
│   └── 2025-Q1/
├── Templates/
│   ├── Daily Note.md
│   ├── Meeting Note.md
│   ├── Project.md
│   └── Book Note.md
└── Attachments/
    └── images/
```

**Zettelkasten Structure:**
```markdown
# Zettelkasten-style vault
ObsidianVault/
├── 0-Inbox/               # Fleeting notes
├── 1-Literature Notes/    # Notes from sources
├── 2-Permanent Notes/     # Your own ideas
├── 3-Structure Notes/     # MOCs (Maps of Content)
├── 4-Projects/            # Project-specific notes
└── Templates/
```

**Naming Conventions:**
```markdown
# Date-based naming for daily notes
Daily Notes/2025-01-17.md

# Timestamp-based for Zettelkasten
202501171430 - Concept Name.md

# Descriptive naming for permanent notes
How to Structure a Knowledge Base.md

# Project-prefixed naming
Project-Alpha - Meeting 2025-01-17.md

# Use lowercase with hyphens for consistency
my-note-about-something.md
```


## 2. Linking and Backlinking


**Basic Linking:**
```markdown
# Internal links
[[Note Name]]
[[Note Name|Display Text]]
[[Folder/Subfolder/Note Name]]

# Link to heading
[[Note Name#Heading Name]]
[[Note Name#Heading Name|Custom Text]]

# Link to block
[[Note Name#^block-id]]

# Embed notes
![[Note Name]]
![[Note Name#Heading]]
![[image.png]]
![[document.pdf]]

# External links
[External Link](https://example.com)
```

**Block References:**
```markdown
# In source note (Source Note.md)
This is an important concept. ^important-concept

This paragraph explains something crucial about the topic.
It spans multiple lines. ^key-explanation

# In referencing note
As mentioned in [[Source Note#^important-concept]], this concept is key.

# Embed the block
![[Source Note#^important-concept]]
```

**Linking Best Practices:**
```markdown
# Note: The Power of Compound Interest.md
