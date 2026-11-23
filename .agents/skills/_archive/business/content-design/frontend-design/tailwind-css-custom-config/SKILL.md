---
name: frontend-design-tailwind-css-custom-config
description: 'Sub-skill of frontend-design: Tailwind CSS (Custom Config) (+1).'
version: 2.0.0
category: business
type: reference
scripts_exempt: true
---

# Tailwind CSS (Custom Config) (+1)

## Tailwind CSS (Custom Config)

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      fontFamily: {
        'display': ['Space Grotesk', 'sans-serif'],
        'body': ['Spectral', 'serif'],
      },
      colors: {
        'midnight': '#1a1a2e',
        'navy': '#16213e',
        'coral': '#e94560',
        'ocean': '#0f3460',
      },
      animation: {
        'fade-in': 'fadeIn 0.6s ease-out',
        'slide-up': 'slideUp 0.6s ease-out',
      },
    },
  },
}
```


## React Components

```jsx
const Button = ({ children, variant = 'primary', ...props }) => {
  const baseStyles = `
    px-6 py-3 font-display font-semibold
    transition-all duration-300
    focus:outline-none focus:ring-2 focus:ring-offset-2
  `;

  const variants = {
    primary: 'bg-coral text-white hover:bg-opacity-90 focus:ring-coral',
    secondary: 'bg-transparent border-2 border-coral text-coral hover:bg-coral hover:text-white',
    ghost: 'bg-transparent text-coral hover:underline',
  };

  return (
    <button className={`${baseStyles} ${variants[variant]}`} {...props}>
      {children}
    </button>
  );
};
```
