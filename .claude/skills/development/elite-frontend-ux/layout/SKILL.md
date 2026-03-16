---
name: elite-frontend-ux-layout
description: 'Sub-skill of elite-frontend-ux: Layout (+3).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Layout (+3)

## Layout

```
┌─────────────────────────────────────────────────┐
│ Top Bar (56–64px): Logo, Search, User Menu      │
├──────────┬──────────────────────────────────────┤
│ Sidebar  │  Main Content (breadcrumbs if deep)  │
│ 240–280px│                                      │
│ collapsed│  Metric Cards → Charts → Tables      │
│ 64–80px  │                                      │
└──────────┴──────────────────────────────────────┘
```

| Nav scenario | Pattern |
|-------------|---------|
| 10+ sections | Collapsible sidebar |
| 3–6 sections | Top navigation |
| Secondary nav | Tabs (max 6) |
| Deep hierarchy | Breadcrumbs |


## Content Hierarchy

1. **Value-first metrics:** "You saved 4 hours" > raw numbers
2. **Actionable insights:** What should the user do next?
3. **Progressive disclosure:** Summary → detail on demand


## Empty States

```jsx
// GOOD: helpful, action-oriented
<EmptyState
  icon={<InboxIcon />}
  title="No messages yet"
  description="When you receive messages, they'll appear here."
  action={<Button>Compose message</Button>}
/>
// BAD: <p>No data</p>
```


## Toast Timing

- Default: 4–5 seconds; minimum (a11y): 6 seconds
- Formula: 500ms/word + 3s base; always include dismiss button

---
