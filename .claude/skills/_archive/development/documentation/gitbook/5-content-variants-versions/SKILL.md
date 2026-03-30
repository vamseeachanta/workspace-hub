---
name: gitbook-5-content-variants-versions
description: 'Sub-skill of gitbook: 5. Content Variants (Versions) (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 5. Content Variants (Versions) (+1)

## 5. Content Variants (Versions)


**REST API - Variants:**
```bash
# List variants for space
curl -s -H "Authorization: Bearer $GITBOOK_API_TOKEN" \
    "$API_BASE/spaces/SPACE_ID/variants" | jq

# Create variant
curl -s -X POST -H "Authorization: Bearer $GITBOOK_API_TOKEN" \
    -H "Content-Type: application/json" \
    "$API_BASE/spaces/SPACE_ID/variants" \
    -d '{
        "title": "v2.0",
        "slug": "v2"
    }' | jq

# Get variant content
curl -s -H "Authorization: Bearer $GITBOOK_API_TOKEN" \
    "$API_BASE/spaces/SPACE_ID/variants/VARIANT_ID/content" | jq

# Set primary variant
curl -s -X PUT -H "Authorization: Bearer $GITBOOK_API_TOKEN" \
    "$API_BASE/spaces/SPACE_ID/variants/VARIANT_ID/primary" | jq

# Delete variant
curl -s -X DELETE -H "Authorization: Bearer $GITBOOK_API_TOKEN" \
    "$API_BASE/spaces/SPACE_ID/variants/VARIANT_ID"
```

**Python - Variants:**
```python
class GitBookClient:
    # ... previous methods ...

    def list_variants(self, space_id):
        """List all variants for space."""
        return self._request("GET", f"/spaces/{space_id}/variants")

    def create_variant(self, space_id, title, slug):
        """Create a new variant."""
        return self._request(
            "POST",
            f"/spaces/{space_id}/variants",
            data={"title": title, "slug": slug}
        )

    def get_variant_content(self, space_id, variant_id):
        """Get variant content."""
        return self._request(
            "GET",
            f"/spaces/{space_id}/variants/{variant_id}/content"
        )

    def set_primary_variant(self, space_id, variant_id):
        """Set variant as primary."""
        return self._request(
            "PUT",
            f"/spaces/{space_id}/variants/{variant_id}/primary"
        )


# Create version variants
client.create_variant("space_xxxxx", "Version 1.0", "v1")
client.create_variant("space_xxxxx", "Version 2.0", "v2")
client.set_primary_variant("space_xxxxx", "variant_v2")
```


## 6. Git Synchronization


**GitBook YAML Configuration:**
```yaml
# .gitbook.yaml - Repository configuration

# Root path for documentation
root: ./docs/

# Structure file (table of contents)
structure:
  readme: README.md
  summary: SUMMARY.md

# Redirects for moved pages
redirects:
  old-page: new-page.md
  moved/page: new-location/page.md
```

**SUMMARY.md Structure:**
```markdown
# Summary
