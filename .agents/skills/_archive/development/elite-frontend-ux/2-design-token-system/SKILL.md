---
name: elite-frontend-ux-2-design-token-system
description: 'Sub-skill of elite-frontend-ux: 2. Design Token System.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 2. Design Token System

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
