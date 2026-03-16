---
name: elite-frontend-ux-required-cn-helper
description: 'Sub-skill of elite-frontend-ux: Required: cn() Helper (+3).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Required: cn() Helper (+3)

## Required: cn() Helper

```typescript
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```


## NEVER Use Dynamic Class Names

```typescript
// ❌ BROKEN — Tailwind purges these
<div className={`bg-${color}-500`} />

// ✅ CORRECT — object map
const colorMap = { blue: "bg-blue-500", red: "bg-red-500" };
<div className={colorMap[color]} />
```


## Component Variants (CVA)

```typescript
import { cva, type VariantProps } from "class-variance-authority";

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input bg-background hover:bg-accent",
        ghost: "hover:bg-accent hover:text-accent-foreground",
      },
      size: {
        sm: "h-9 px-3 text-sm",
        default: "h-10 px-4 py-2",
        lg: "h-11 px-8 text-base",
      },
    },
    defaultVariants: { variant: "default", size: "default" },
  }
);
```


## Mobile-First Responsive

```html
<div class="
  flex flex-col md:flex-row
  gap-4 md:gap-8
  p-4 md:p-6 lg:p-8
">
```

Breakpoints: `sm`=640px · `md`=768px · `lg`=1024px · `xl`=1280px · `2xl`=1536px

---
