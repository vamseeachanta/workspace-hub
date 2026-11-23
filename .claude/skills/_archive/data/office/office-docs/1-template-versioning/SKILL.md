---
name: office-docs-1-template-versioning
description: 'Sub-skill of office-docs: 1. Template Versioning (+3).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 1. Template Versioning (+3)

## 1. Template Versioning

```
templates/
├── v1/
│   └── contract_template.docx
├── v2/
│   └── contract_template.docx  # Updated branding
└── current -> v2/              # Symlink to current version
```


## 2. Validation Before Generation

```python
def validate_context(context, required_fields):
    """Validate context before document generation."""
    missing = [f for f in required_fields if f not in context or not context[f]]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")
    return True
```


## 3. Output Organization

```python
from datetime import datetime

def get_output_path(doc_type, client_id, extension='docx'):
    """Generate organized output path."""
    date_str = datetime.now().strftime('%Y/%m/%d')
    return f"output/{doc_type}/{date_str}/{client_id}.{extension}"
```


## 4. Logging and Audit Trail

```python
def generate_with_audit(template, context, output_path):
    """Generate document with audit logging."""
    start_time = time.time()

    result = generate_document(template, context, output_path)

    audit_log.info({
        'action': 'document_generated',
        'template': template,
        'output': output_path,
        'duration': time.time() - start_time,
        'context_keys': list(context.keys())
    })

    return result
```
