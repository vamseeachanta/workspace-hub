---
name: visual-review-board
description: Use when sourcing destination preview photos for a trip plan. Encodes the Wikimedia-API thumburl pattern (no hand-construction), main-session re-verification, and the destination-specific selection rule. Invoked by trip-planner.
type: reference
---

# visual-review-board

Photos in the trip issue body are how the family decides whether they're excited about a destination. Bad photos are worse than no photos. This skill encodes what we learned from the #41–#68 incident.

## The lesson — what went wrong before

**#42–#66 (initial draft):** every Kansas issue used the same NPS Midwest Region homepage banner. Every Louisiana issue used the same NPS Atlantic Region homepage banner. The Florida set reused a `Henderson_Beach_State_Park_4` photo even on issues for Destin and 30A. The repetition made the issues unconvincing — six different Kansas destinations all visually identical.

**Root causes:**
1. The original draft used `nps.gov/common/uploads/banner_image/<region>/homepage/<hash>.jpg` URLs, which are the **NPS regional homepage banners** — not destination photos. These are intentionally generic.
2. Photos were chosen by URL pattern, not by what the photo actually depicts.

**#68 (Switzerland, second attempt):** A research subagent reported "all 5 photos verified 200" but two of them returned 400 when re-checked. The agent constructed Wikimedia thumb URLs by hand using the wrong width segment (`800px-` when the actual cached size for those files was `960px-`).

**Root cause:** Hand-constructing Wikimedia thumbnail URLs assumes you know which widths the cache serves for that specific file. You don't.

## Hard rules

1. **Source from Wikimedia Commons by default.** CC/PD-licensed, hot-link-friendly, stable CDN at `upload.wikimedia.org`, correctly attributed.
2. **Get the canonical thumburl from the API, don't construct it by hand.** Wikimedia's thumb cache only serves widths it generated for that specific file. The width buckets vary per file.
3. **Re-verify in the main session, never trust subagent verification.** Subagents have made false 200-claims twice now.
4. **Reject NPS banner_image URLs.** Anything matching `nps.gov/common/uploads/banner_image/<region>/homepage/` is a regional banner, not a destination photo.
5. **The photo must obviously depict the named destination.** A "generic prairie" photo for "Tallgrass Prairie National Preserve" is wrong if there's a labeled-by-name alternative available.
6. **No URL appears twice across the trip.** If two destinations would share a photo, find a different one for the second.

## The canonical workflow

For each photo slot in a trip issue:

### Step 1: Find the file on Wikimedia Commons

Search:
```
https://commons.wikimedia.org/w/index.php?search=<destination+name>&go=Go
```

Or use Special:Search with namespace File. Pick a file whose:
- Title obviously names the destination (e.g., `Bathhouse_Row,_Lamar,_Hot_Springs_National_Park,_Arkansas.jpg`)
- License is CC-BY, CC-BY-SA, CC0, or PD (visible on the file page)
- The image, when clicked, actually shows the destination — not a tangentially related place

### Step 2: Query the API for the canonical thumburl

```bash
UA="Mozilla/5.0 (compatible; trip-planner/1.0)"
FILE="File:Bathhouse_Row,_Lamar,_Hot_Springs_National_Park,_Arkansas.jpg"
encoded=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$FILE")
curl -s -A "$UA" "https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url&iiurlwidth=1024&format=json&titles=$encoded" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); [print(p['imageinfo'][0].get('thumburl')) for p in d['query']['pages'].values() if 'imageinfo' in p]"
```

The API returns a `thumburl` like:
`https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Bathhouse_Row%2C_Lamar%2C_Hot_Springs_National_Park%2C_Arkansas.jpg/1280px-Bathhouse_Row%2C_Lamar%2C_Hot_Springs_National_Park%2C_Arkansas.jpg`

Wikimedia auto-bumps the requested width (1024 → 1280 here) to a cached size. Use the returned URL exactly.

### Step 3: Re-verify with curl (200 + image content-type)

```bash
curl -sI -A "$UA" -L -o /dev/null -w "%{http_code} %{content_type}\n" "$THUMBURL"
```

Expected: `200 image/jpeg` or `200 image/png`. Anything else, reject.

**Important:** Wikimedia returns 403 to Python's default urllib User-Agent. Always use curl with a real UA, OR set `User-Agent` explicitly in Python.

### Step 4: Embed in the issue body

Use HTML `<img>` tag (not Markdown image syntax) so you can specify width:

```html
<img src="<thumburl>" width="320" alt="<short alt — destination name + scene>">
```

For destination issues, width=420. For visual-review-board tables (5+ scenic anchors), width=320.

## Fallback sources (in priority order)

If no good Wikimedia file exists for a destination:

1. **NPS direct photo gallery** — `nps.gov/<unit>/photosvideosmultimedia/index.htm`. Photos linked from there are usually fine. **NEVER** use the homepage banner image.
2. **State tourism site** — `arkansas.com`, `visitflorida.com`, `travelks.com`, etc. Their CMS image URLs are stable.
3. **USFS / BLM** — for national forests / BLM lands, `fs.usda.gov` and `blm.gov` direct image paths.
4. **Flickr Commons** — for older / archival photos (search by destination + "Commons").

What NOT to use as a fallback:
- TripAdvisor / Google Images / random blog hosts (link rot, unstable, often unlicensed)
- Stock photo sites (paywall + watermark)
- Instagram / Facebook (links break, often private)

## Sanity check before publishing

Before saving the issue body:

- [ ] Every photo URL re-verified in the **main session** (not subagent) with curl + real UA → 200
- [ ] Each URL appears at most once across the issue (and once across the trip's child issues)
- [ ] Each photo's filename or description obviously matches the destination it represents
- [ ] No URL contains `nps.gov/common/uploads/banner_image/`
- [ ] All `<img>` tags have meaningful `alt` text (not "preview" — name the actual scene)

## Reference patterns

- **#41 (gold standard):** 7 photos, all destination-specific, mix of state-park CMS URLs and direct photo CDNs. No regional banners.
- **#42–#66 (after fix on 2026-04-27):** 19 issues, each with exactly one Wikimedia Commons thumb URL. All API-sourced. All re-verified in main session.
- **#68 (Switzerland, after fix):** 5 thumbs at 960px (the actual cached width for those files). Initial 800px attempt returned 400 — caught by main-session verification.
