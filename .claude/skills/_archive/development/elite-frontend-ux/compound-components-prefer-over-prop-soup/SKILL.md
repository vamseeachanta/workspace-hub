---
name: elite-frontend-ux-compound-components-prefer-over-prop-soup
description: 'Sub-skill of elite-frontend-ux: Compound Components (prefer over prop
  soup) (+3).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Compound Components (prefer over prop soup) (+3)

## Compound Components (prefer over prop soup)

```tsx
<Tabs defaultValue="tab1">
  <TabsList>
    <TabsTrigger value="tab1">Tab 1</TabsTrigger>
    <TabsTrigger value="tab2">Tab 2</TabsTrigger>
  </TabsList>
  <TabsContent value="tab1">Content 1</TabsContent>
  <TabsContent value="tab2">Content 2</TabsContent>
</Tabs>
```


## Reduced Motion

```tsx
import { useReducedMotion } from "framer-motion";

function AnimatedCard() {
  const reduce = useReducedMotion();
  return (
    <motion.div
      initial={{ opacity: 0, y: reduce ? 0 : 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: reduce ? 0 : 0.3 }}
    />
  );
}
```


## Loading States (skeleton > spinner)

```tsx
<div className="animate-pulse space-y-2">
  <div className="h-4 bg-muted rounded w-3/4" />
  <div className="h-4 bg-muted rounded w-1/2" />
</div>
```


## Animation Rules

- Button feedback: 100–150ms (must feel instantaneous)
- ONLY animate `transform` and `opacity` (GPU accelerated)
- NEVER animate `width`, `height`, `margin`, `padding` (triggers reflow)

---
