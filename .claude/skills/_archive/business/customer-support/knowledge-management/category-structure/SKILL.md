---
name: knowledge-management-category-structure
description: 'Sub-skill of knowledge-management: Category Structure (+1).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Category Structure (+1)

## Category Structure


Organize articles into a hierarchy that matches how customers think:

```
Getting Started
├── Account setup
├── First-time configuration
└── Quick start guides

Features & How-tos
├── [Feature area 1]
├── [Feature area 2]
└── [Feature area 3]

Integrations
├── [Integration 1]
├── [Integration 2]
└── API reference

Troubleshooting
├── Common errors
├── Performance issues
└── Known issues

Billing & Account
├── Plans and pricing
├── Billing questions
└── Account management
```


## Linking Best Practices


- **Link from troubleshooting to how-to**: "For setup instructions, see [How to configure X]"
- **Link from how-to to troubleshooting**: "If you encounter errors, see [Troubleshooting X]"
- **Link from FAQ to detailed articles**: "For a full walkthrough, see [Guide to X]"
- **Link from known issues to workarounds**: Keep the chain from problem to solution short
- **Use relative links** within the KB -- they survive restructuring better than absolute URLs
- **Avoid circular links** -- if A links to B, B shouldn't link back to A unless both are genuinely useful entry points
