# HTML extraction — coverage protocol

For web pages, blog posts, online articles.

## Pre-extraction estimate

```bash
curl -sL <url> -o <source.html>
wc -l <source.html>
grep -c '<article\|<main\|class="post\|class="entry' <source.html>   # CMS clues
grep -c '<script' <source.html>                                       # JS-heavy?
```

`extraction_estimate` baseline:

| Indicator | Estimate |
|---|---|
| Server-rendered article with semantic markup (`<article>`, `<main>`) | 0.98 |
| JS-heavy SPA where content requires execution | 0.30 (needs headless browser) |
| Paywalled or login-gated | 0.0 (need access first) |
| Already-clean markdown source (e.g., `?format=md`) | 1.0 |

## Primary extractor: `trafilatura`

```python
import trafilatura
downloaded = trafilatura.fetch_url("<url>")
text = trafilatura.extract(
    downloaded,
    include_comments=False,
    include_tables=True,
    output_format="markdown",
)
```

`trafilatura` is the best-of-class boilerplate stripper. Handles 90%+ of
modern article pages cleanly.

## Fallback: `BeautifulSoup` + `readability-lxml`

```python
from readability import Document
from bs4 import BeautifulSoup

doc = Document(open("<source.html>").read())
article_html = doc.summary()
soup = BeautifulSoup(article_html, "lxml")
text = soup.get_text(separator="\n\n", strip=True)
```

Use when `trafilatura` returns suspiciously short content or fails on
unusual layouts.

## JS-rendered pages

If `trafilatura` returns only the skeleton (likely SPA), use the existing
chrome MCP tools per `mcp__claude-in-chrome__navigate` + `read_page_text`:

```
mcp__claude-in-chrome__navigate <url>
mcp__claude-in-chrome__get_page_text
```

This is appropriate for individual sources. For bulk: configure
trafilatura with a headless-browser backend.

Per `feedback_webfetch_first_for_linkedin`: LinkedIn returns full content
via WebFetch (og:description); try that before the chrome route.

## Post-extraction yield

Compared against the original page's textual content (excluding ads,
nav, footer, related-posts):

```python
import re
# Extract all text from <article> or <main>
article_text_chars = len(soup.find("article").get_text(strip=True))
extracted_chars = len(text)
yield_ = extracted_chars / article_text_chars
```

If no `<article>` tag: use the rendered viewport's textual content as
the baseline. This is approximate but defensible.

## Anchor format

`[[sources/<slug>]]#<heading-slug>`

Example: `[[sources/blog-post-yaw-moments]]#stability-analysis`

Heading slug: kebab-case lowercase of the section heading text.

If the source HTML has explicit `id=` anchors on headings, use those
directly: `[[sources/<slug>]]#h2-method`.

## Spot-check

Open the URL in a browser. Verify the extracted markdown matches the
visible article content. Flag:
- Truncated mid-section (boilerplate stripper cut too aggressively)
- Comments / replies included that shouldn't be
- Image captions absent when material to the article

## Common pitfalls

- Paywalled content: trafilatura returns the "subscribe" wall, not the
  article. Yield = 0; route to authenticated access or skip
- Newsletter pages: often have multiple articles; extract the specific
  permalink, not the digest
- Image-heavy posts (Substack visual essays): text yield can be high
  but the article's value is in the images; flag in
  `extraction_yield_lost`
- Embedded tweets / videos: `trafilatura` strips them; if material,
  ingest the embedded source separately as its own `sources/<slug>.md`
- Code blocks: trafilatura preserves them as markdown fences; verify
  language hints survive
