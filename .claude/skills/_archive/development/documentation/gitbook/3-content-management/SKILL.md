---
name: gitbook-3-content-management
description: 'Sub-skill of gitbook: 3. Content Management (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 3. Content Management (+1)

## 3. Content Management


**REST API - Content:**
```bash
# Get page content
curl -s -H "Authorization: Bearer $GITBOOK_API_TOKEN" \
    "$API_BASE/spaces/SPACE_ID/content/page/PAGE_ID" | jq

# List pages in space
curl -s -H "Authorization: Bearer $GITBOOK_API_TOKEN" \
    "$API_BASE/spaces/SPACE_ID/content" | jq '.pages'

# Import content from Git
curl -s -X POST -H "Authorization: Bearer $GITBOOK_API_TOKEN" \
    -H "Content-Type: application/json" \
    "$API_BASE/spaces/SPACE_ID/content/import/git" \
    -d '{
        "url": "https://github.com/user/docs-repo",
        "ref": "main"
    }' | jq

# Export content
curl -s -H "Authorization: Bearer $GITBOOK_API_TOKEN" \
    "$API_BASE/spaces/SPACE_ID/content/export" \
    -o content-export.zip

# Search content
curl -s -H "Authorization: Bearer $GITBOOK_API_TOKEN" \
    "$API_BASE/spaces/SPACE_ID/search?query=installation" | jq
```

**Python - Content:**
```python
class GitBookClient:
    # ... previous methods ...

    def get_page(self, space_id, page_id):
        """Get page content."""
        return self._request(
            "GET",
            f"/spaces/{space_id}/content/page/{page_id}"
        )

    def list_pages(self, space_id):
        """List all pages in space."""
        content = self.get_space_content(space_id)
        return content.get("pages", [])

    def search_content(self, space_id, query):
        """Search content in space."""
        return self._request(
            "GET",
            f"/spaces/{space_id}/search",
            params={"query": query}
        )

    def import_from_git(self, space_id, repo_url, ref="main"):
        """Import content from Git repository."""
        return self._request(
            "POST",
            f"/spaces/{space_id}/content/import/git",
            data={"url": repo_url, "ref": ref}
        )


# Search example
results = client.search_content("space_xxxxx", "getting started")
for result in results.get("items", []):
    print(f"Found: {result['title']} - {result['path']}")
```


## 4. Collections Management


**REST API - Collections:**
```bash
# List collections
curl -s -H "Authorization: Bearer $GITBOOK_API_TOKEN" \
    "$API_BASE/orgs/ORG_ID/collections" | jq

# Get collection
curl -s -H "Authorization: Bearer $GITBOOK_API_TOKEN" \
    "$API_BASE/collections/COLLECTION_ID" | jq

# Create collection
curl -s -X POST -H "Authorization: Bearer $GITBOOK_API_TOKEN" \
    -H "Content-Type: application/json" \
    "$API_BASE/orgs/ORG_ID/collections" \
    -d '{
        "title": "Product Documentation",
        "description": "All product-related documentation"
    }' | jq

# Add space to collection
curl -s -X POST -H "Authorization: Bearer $GITBOOK_API_TOKEN" \
    "$API_BASE/collections/COLLECTION_ID/spaces/SPACE_ID" | jq

# Remove space from collection
curl -s -X DELETE -H "Authorization: Bearer $GITBOOK_API_TOKEN" \
    "$API_BASE/collections/COLLECTION_ID/spaces/SPACE_ID"

# List spaces in collection
curl -s -H "Authorization: Bearer $GITBOOK_API_TOKEN" \
    "$API_BASE/collections/COLLECTION_ID/spaces" | jq
```

**Python - Collections:**
```python
class GitBookClient:
    # ... previous methods ...

    def list_collections(self, org_id):
        """List all collections in organization."""
        return self._request("GET", f"/orgs/{org_id}/collections")

    def get_collection(self, collection_id):
        """Get collection details."""
        return self._request("GET", f"/collections/{collection_id}")

    def create_collection(self, org_id, title, description=None):
        """Create a new collection."""
        data = {"title": title}
        if description:
            data["description"] = description

        return self._request(
            "POST",
            f"/orgs/{org_id}/collections",
            data=data
        )

    def add_space_to_collection(self, collection_id, space_id):
        """Add space to collection."""
        return self._request(
            "POST",
            f"/collections/{collection_id}/spaces/{space_id}"
        )

    def list_collection_spaces(self, collection_id):
        """List spaces in collection."""
        return self._request(
            "GET",
            f"/collections/{collection_id}/spaces"
        )


# Create collection and add spaces
collection = client.create_collection(
    org_id="org_xxxxx",
    title="API Reference",
    description="All API documentation"
)

client.add_space_to_collection(collection["id"], "space_xxxxx")
```
