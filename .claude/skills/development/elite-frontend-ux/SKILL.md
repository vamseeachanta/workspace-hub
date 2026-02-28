---
name: elite-frontend-ux
description: >
  Create distinctive, production-grade frontend interfaces with expert-level UX
  design. Use when building SaaS dashboards, landing pages, marketing sites,
  React/Vue components, HTML/CSS layouts, or any web UI. Combines bold aesthetic
  direction with systematic design tokens, WCAG accessibility, conversion
  optimization, and Tailwind/React best practices. Produces polished, memorable
  interfaces that avoid generic AI aesthetics while meeting professional standards.
version: 1.0.0
category: development
last_updated: 2026-02-28
tools: [Read, Write, Edit, Bash]
related_skills:
  - html-report-verify
  - webapp-testing
  - sparc:designer
tags: [frontend, ux, ui, tailwind, react, accessibility, wcag, dashboard, landing-page, design-tokens]
platforms: [linux, macos, windows]
---

# /elite-frontend-ux — Elite Frontend UX Design

Create distinctive, production-grade interfaces that combine bold aesthetics with
systematic UX excellence. Every output must be visually striking AND functionally
flawless.

## Trigger

```
/elite-frontend-ux <brief description of the UI to build>
```

Examples:
```
/elite-frontend-ux SaaS analytics dashboard for pipeline inspection data
/elite-frontend-ux landing page for offshore engineering software tool
/elite-frontend-ux React settings page with danger zone and form validation
```

---

## Phase 0 — Context Analysis (Answer Before Writing Any Code)

Before touching code, commit to explicit answers:

| Question | Answer required |
|----------|----------------|
| WHO uses this? | Persona, expertise level, device context |
| WHAT is the ONE action? | Single primary goal per page |
| WHY should they trust/engage? | Value proposition in one sentence |
| WHAT aesthetic direction? | Choose and name one (see §1) |
| WHAT is the ONE memorable thing? | If unclear, redesign concept |

---

## 1. Aesthetic Commitment (Choose ONE, COMMIT)

Timid design fails. Pick a clear direction:

| Direction | Reference brands |
|-----------|-----------------|
| Brutally minimal | Stripe, Linear |
| Maximalist editorial | Bloomberg, Awwwards winners |
| Retro-futuristic | Y2K revival, vaporwave |
| Organic/natural | Earthy, hand-drawn, textured |
| Luxury/refined | Fashion houses, premium brands |
| Playful/toy-like | Figma, Notion |
| Neo-brutalist | Raw, exposed, intentionally rough |
| Art deco/geometric | Bold shapes, gold accents |
| Soft/pastel | Gradient meshes, dreamy |
| Industrial/utilitarian | Data-dense, functional |

**Anti-patterns to avoid:**
- ❌ Purple/blue gradients on white (AI cliché)
- ❌ Inter, Roboto, Arial as display fonts
- ❌ Generic card grids with no visual identity

---

## 2. Design Token System

Always open the implementation with these CSS variables. Never eyeball spacing or
pick arbitrary colors.

```css
:root {
  /* Typography */
  --font-size-xs:   0.75rem;    /* 12px — captions, labels */
  --font-size-sm:   0.875rem;   /* 14px — secondary text */
  --font-size-base: 1rem;       /* 16px — body (MINIMUM mobile) */
  --font-size-lg:   1.125rem;   /* 18px — lead paragraphs */
  --font-size-xl:   1.25rem;    /* 20px — H4 */
  --font-size-2xl:  1.5rem;     /* 24px — H3 */
  --font-size-3xl:  2rem;       /* 32px — H2 */
  --font-size-4xl:  2.5rem;     /* 40px — H1 */
  --font-size-5xl:  3.5rem;     /* 56px — Display */

  /* Spacing (8px base) */
  --space-1:  0.25rem;  /* 4px */
  --space-2:  0.5rem;   /* 8px */
  --space-4:  1rem;     /* 16px */
  --space-6:  1.5rem;   /* 24px */
  --space-8:  2rem;     /* 32px */
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */
  --space-20: 5rem;     /* 80px — section gaps */
  --space-32: 8rem;     /* 128px — major section gaps */

  /* Colors (HSL for easy dark mode) */
  --background: 0 0% 100%;
  --foreground: 222 47% 11%;
  --primary: 222 47% 11%;
  --primary-foreground: 210 40% 98%;
  --secondary: 210 40% 96%;
  --secondary-foreground: 222 47% 11%;
  --muted: 210 40% 96%;
  --muted-foreground: 215 16% 47%;
  --border: 214 32% 91%;
  --ring: 222 47% 11%;
  --destructive: 0 84% 60%;
  --success: 142 76% 36%;
  --warning: 38 92% 50%;
  --radius: 0.5rem;

  /* Animation */
  --duration-fast:   100ms;
  --duration-normal: 200ms;
  --duration-slow:   300ms;
  --ease-default:    cubic-bezier(0.4, 0, 0.2, 1);
  --ease-out:        cubic-bezier(0, 0, 0.2, 1);
  --ease-bounce:     cubic-bezier(0.34, 1.56, 0.64, 1);
}

.dark {
  --background: 222 47% 4%;
  --foreground: 210 40% 98%;
  --border: 217 33% 17%;
  --muted: 217 33% 17%;
  --muted-foreground: 215 20% 65%;
}
```

**Typography rules:**
- Line height: 1.5–1.6 body, 1.1–1.2 headings
- Line length: 45–75 chars (`max-w-prose` or `max-w-2xl`)
- Max 2–3 typefaces per design
- NEVER use Inter/Roboto/Arial as primary (overused)
- PAIR: one distinctive display font + one refined body font

**Distinctive font suggestions:**
- Display: Fraunces, Instrument Serif, Space Grotesk, Clash Display, Cabinet Grotesk, Satoshi
- Body: Source Serif Pro, IBM Plex Sans, Libre Franklin, Plus Jakarta Sans

---

## 3. Accessibility Requirements (Hard Gates)

### Contrast (WCAG 2.1 AA)
| Element | Minimum ratio |
|---------|--------------|
| Body text | 4.5:1 |
| Large text (18pt+ or 14pt bold) | 3:1 |
| UI components, icons | 3:1 |
| Focus indicators | 3:1 |

### Touch Targets
- Minimum size: 44×44px
- Minimum spacing between adjacent targets: 8px

### Interactive Elements
- ALL interactive elements MUST have visible focus states
- NEVER use `outline: none` without a replacement
- Tab order must be logical; avoid `tabindex > 0`

### Forms
- Every input MUST have an associated `<label>` (not just placeholder)
- Error messages: use `aria-describedby` to associate with input
- Don't disable submit buttons before first submission attempt
- Use `autocomplete` attributes

### Semantic HTML (first rule of ARIA: don't use ARIA if native HTML works)
```html
<!-- CORRECT -->
<button type="button">Action</button>
<a href="/page">Navigate</a>

<!-- WRONG -->
<div onclick="...">Action</div>
<span class="link">Navigate</span>
```

---

## 4. SaaS Dashboard Patterns

### Layout
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

### Content Hierarchy
1. **Value-first metrics:** "You saved 4 hours" > raw numbers
2. **Actionable insights:** What should the user do next?
3. **Progressive disclosure:** Summary → detail on demand

### Empty States
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

### Toast Timing
- Default: 4–5 seconds; minimum (a11y): 6 seconds
- Formula: 500ms/word + 3s base; always include dismiss button

---

## 5. Landing Page Patterns

### Above-the-Fold Essentials
Must fit within one viewport:
1. Headline (5–10 words)
2. Supporting subheadline (value proposition)
3. Single primary CTA
4. Hero visual

### Section Flow
```
1. Hero (headline + CTA + visual)
2. Social proof (logos, snippet)
3. Problem / Solution
4. Features / Benefits (3–4 max)
5. Testimonials
6. Pricing (if applicable)
7. FAQ
8. Final CTA
9. Footer
```

### CTA Design
- Height: min 44px; padding: 2× font size
- Copy: action verbs, first-person ("Get my free trial" > "Sign up")
- Length: 2–5 words max
- One primary CTA per viewport

### Pricing Tables
- 3–4 tiers max (more causes paralysis)
- Highlight recommended tier
- Annual/monthly toggle showing savings
- CTA button on every tier

### Form Optimization
- Single column (120% fewer errors vs multi-column)
- Minimize fields (4 vs 11 fields = 120% more conversions)
- Never ask for phone unless essential (58% abandon)
- Labels above inputs; validate on blur, not while typing

---

## 6. Tailwind CSS Best Practices

### Required: cn() Helper
```typescript
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

### NEVER Use Dynamic Class Names
```typescript
// ❌ BROKEN — Tailwind purges these
<div className={`bg-${color}-500`} />

// ✅ CORRECT — object map
const colorMap = { blue: "bg-blue-500", red: "bg-red-500" };
<div className={colorMap[color]} />
```

### Component Variants (CVA)
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

### Mobile-First Responsive
```html
<div class="
  flex flex-col md:flex-row
  gap-4 md:gap-8
  p-4 md:p-6 lg:p-8
">
```

Breakpoints: `sm`=640px · `md`=768px · `lg`=1024px · `xl`=1280px · `2xl`=1536px

---

## 7. React Patterns

### Compound Components (prefer over prop soup)
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

### Reduced Motion
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

### Loading States (skeleton > spinner)
```tsx
<div className="animate-pulse space-y-2">
  <div className="h-4 bg-muted rounded w-3/4" />
  <div className="h-4 bg-muted rounded w-1/2" />
</div>
```

### Animation Rules
- Button feedback: 100–150ms (must feel instantaneous)
- ONLY animate `transform` and `opacity` (GPU accelerated)
- NEVER animate `width`, `height`, `margin`, `padding` (triggers reflow)

---

## 8. Anti-Patterns (Never Do)

| Category | Forbidden |
|----------|-----------|
| Visual | Purple/blue gradient on white; Inter/Roboto/Arial as display; inconsistent border-radius; >3 font weights |
| UX | Confirmshaming; pre-selected options favoring company; infinite scroll without pagination; disabled submit before first attempt; placeholder-as-label |
| Technical | `outline:none` without replacement; `<div onclick>` instead of `<button>`; dynamic Tailwind classes; animating layout properties |
| Mobile | Touch targets <44×44px; body text <16px; horizontal content scroll; no tap feedback |
| Dark patterns | Fake urgency/scarcity; cancellation harder than signup; auto-ticking consent checkboxes |

---

## 9. Pre-Delivery Checklist

Before delivering any frontend code, verify all items:

**Accessibility**
- [ ] Color contrast ≥4.5:1 text / ≥3:1 UI components
- [ ] Touch targets ≥44×44px
- [ ] All images have `alt` text (decorative: `alt=""`)
- [ ] All form fields have `<label>`
- [ ] Visible focus states on all interactive elements
- [ ] No color-only information conveyance

**Visual Design**
- [ ] Clear typographic hierarchy (3–5 levels)
- [ ] Consistent spacing from token scale
- [ ] Max 2–3 typefaces
- [ ] Cohesive 60/30/10 color palette
- [ ] ONE memorable design element present

**Technical**
- [ ] Mobile-first responsive approach
- [ ] Animations use only `transform`/`opacity`
- [ ] No dynamic Tailwind class names
- [ ] `cn()` helper used for class merging
- [ ] Dark mode support via CSS variables
- [ ] `prefers-reduced-motion` respected

**UX Integrity**
- [ ] Single primary goal per page
- [ ] No dark patterns or confirmshaming
- [ ] Footer always accessible
- [ ] Error states are descriptive and helpful
- [ ] Loading states exist for all async operations
- [ ] Empty states have helpful action prompts

---

## 10. Implementation Order

1. Define CSS token block (§2)
2. Sketch semantic HTML structure (§3 — no ARIA until HTML exhausted)
3. Apply Tailwind mobile-first (§6)
4. Add component variants via CVA (§6)
5. Wire interactivity with React patterns (§7)
6. Run pre-delivery checklist (§9)
7. Verify one distinctive aesthetic element is present (§1)
