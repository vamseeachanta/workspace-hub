---
name: semantic-search-setup-status-monitoring
description: 'Sub-skill of semantic-search-setup: Status Monitoring.'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# Status Monitoring

## Status Monitoring


```python
def get_embedding_status(db_path):
    conn = sqlite3.connect(db_path, timeout=30)
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM chunks')
    total_chunks = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM embeddings')
    embedded = cursor.fetchone()[0]

    conn.close()

    return {
        'total': total_chunks,
        'embedded': embedded,
        'remaining': total_chunks - embedded,
        'progress': f"{100*embedded/total_chunks:.1f}%"
    }
```
