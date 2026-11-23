---
name: dash-gunicorn-production-server
description: 'Sub-skill of dash: Gunicorn Production Server (+2).'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# Gunicorn Production Server (+2)

## Gunicorn Production Server


```python
# wsgi.py
from app import app

server = app.server

if __name__ == "__main__":
    server.run()
```

```bash
# Run with Gunicorn
gunicorn wsgi:server -b 0.0.0.0:8050 -w 4
```

## Docker Deployment


```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

*See sub-skills for full details.*

## Cloud Deployment (Heroku)


```txt
# Procfile
web: gunicorn wsgi:server

# requirements.txt
dash>=2.14.0
dash-bootstrap-components>=1.5.0
plotly>=5.18.0
pandas>=2.0.0
gunicorn>=21.0.0
```
