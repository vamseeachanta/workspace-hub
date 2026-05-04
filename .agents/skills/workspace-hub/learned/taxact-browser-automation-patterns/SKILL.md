---
name: taxact-browser-automation-patterns
description: Patterns for automating TaxAct Business online (Ionic SPA) via Chrome browser MCP tools — field interaction, navigation, shadow DOM handling
version: 1.0.0
source: auto-extracted
extracted: 2026-04-15
metadata:
  tags: ["taxact", "browser-automation", "ionic", "tax-filing", "chrome-mcp"]
---

# TaxAct Business Browser Automation Patterns

## When to Use
Automating data entry in TaxAct Business online (www.taxact.com/online/) using Codex-in-Chrome MCP tools.

## Key Architecture
TaxAct is an **Ionic SPA** — single-page app with shadow DOM components. Standard DOM queries often miss elements rendered inside web components.

## Navigation
```javascript
// Continue to next page
document.getElementById('CONTINUE').click();

// Page detection (wait for SPA to render)
setTimeout(() => {
  document.title = document.body.innerText.substring(300, 1200);
}, 3000);

// Top-level tabs
document.getElementById('first-tab').click();   // About the Business
document.getElementById('third-tab').click();    // Federal
document.getElementById('fourth-tab').click();   // State
document.getElementById('fifth-tab').click();    // Review
document.getElementById('sixth-tab').click();    // Filing
```

## Field Interaction
TaxAct uses React-style controlled inputs. Direct `.value =` assignment is ignored. Use the native setter pattern:
```javascript
const nativeSetter = Object.getOwnPropertyDescriptor(
  window.HTMLInputElement.prototype, 'value'
).set;
nativeSetter.call(field, 'value');
field.dispatchEvent(new Event('input', {bubbles: true}));
field.dispatchEvent(new Event('change', {bubbles: true}));
field.dispatchEvent(new Event('blur', {bubbles: true}));
```

## Field Discovery
Fields have IDs like `FTXT_FEDERAL_317_1_12`. No aria-labels. Map by Y-position:
```javascript
const fields = Array.from(document.querySelectorAll('input[id^="FTXT_"]'))
  .map(f => ({id: f.id, y: f.getBoundingClientRect().y, val: f.value}))
  .sort((a, b) => a.y - b.y);
```

## Radio Buttons
Pattern: `FRAD_FEDERAL_NNN_N_NN` with name `FRAD_DEFAULT`:
```javascript
const radio = document.getElementById('FRAD_FEDERAL_146_1_25');
radio.checked = true;
radio.dispatchEvent(new Event('change', {bubbles: true}));
```

## Checkboxes
Pattern: `FCHK_FEDERAL_NNN_N_NNN`:
```javascript
const cb = document.getElementById('FCHK_FEDERAL_17_1_304');
cb.checked = true;
cb.dispatchEvent(new Event('change', {bubbles: true}));
```

## Select/Picklist
TaxAct picklists have a hidden `<select>` and a visible `picklist-input` text field. Set both:
```javascript
sel.value = '44';
sel.dispatchEvent(new Event('change', {bubbles: true}));
// Also update visible picklist-input if present
```

## Review Links (Federal Deductions)
On the Federal deductions summary, "Review" links are sequential `<a>` elements. Index from ~34:
- Compensation of officers = index 34
- Salaries and wages = index 35
- Taxes and licenses = index 39
- Other deductions = index 52

## Pitfalls
1. **Stale tab titles** — SPA navigation doesn't update `document.title`. Always re-read with `document.body.innerText`.
2. **Shadow DOM** — some pages (especially Alerts) render in Ionic shadow DOM. The `read_page` accessibility tree may show content the DOM walker cannot find. Use `read_page` with `filter: "interactive"` as fallback.
3. **Click timing** — after `.click()`, wait 3s before reading new page content. The SPA needs time to render.
4. **Balance sheet rounding** — TaxAct computes depreciation independently. Expect $1-3K variance from manual calculations. Adjust accumulated depreciation by $1 if needed to balance Schedule L.
5. **No Yes/No buttons** — some pages use `<input type="radio">` instead of `<button>`. Check both.
