---
name: docx-templates-fastapi-service
description: 'Sub-skill of docx-templates: FastAPI Service.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# FastAPI Service

## FastAPI Service


```python
"""
Document generation service with FastAPI.
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from docxtpl import DocxTemplate
from pathlib import Path
import tempfile
import uuid

app = FastAPI(title="Document Generation Service")

# Template storage
TEMPLATES_DIR = Path("./templates")
OUTPUT_DIR = Path("./generated")
OUTPUT_DIR.mkdir(exist_ok=True)


class GenerateRequest(BaseModel):
    """Request model for document generation."""
    template_name: str
    data: Dict[str, Any]
    output_filename: Optional[str] = None


class BatchGenerateRequest(BaseModel):
    """Request for batch generation."""
    template_name: str
    records: List[Dict[str, Any]]
    filename_field: str = "id"


@app.get("/templates")
async def list_templates():
    """List available templates."""
    templates = []
    for f in TEMPLATES_DIR.glob("*.docx"):
        templates.append({
            "name": f.stem,
            "filename": f.name
        })
    return {"templates": templates}


@app.post("/generate")
async def generate_document(request: GenerateRequest):
    """Generate a single document."""
    template_path = TEMPLATES_DIR / f"{request.template_name}.docx"

    if not template_path.exists():
        raise HTTPException(404, f"Template '{request.template_name}' not found")

    try:
        template = DocxTemplate(str(template_path))
        template.render(request.data)

        # Generate output filename
        output_name = request.output_filename or f"{uuid.uuid4()}.docx"
        if not output_name.endswith(".docx"):
            output_name += ".docx"

        output_path = OUTPUT_DIR / output_name
        template.save(str(output_path))

        return FileResponse(
            str(output_path),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=output_name
        )

    except Exception as e:
        raise HTTPException(500, f"Generation failed: {str(e)}")


@app.post("/generate/batch")
async def generate_batch(request: BatchGenerateRequest):
    """Generate multiple documents."""
    template_path = TEMPLATES_DIR / f"{request.template_name}.docx"

    if not template_path.exists():
        raise HTTPException(404, f"Template '{request.template_name}' not found")

    generated = []
    errors = []

    for record in request.records:
        try:
            template = DocxTemplate(str(template_path))
            template.render(record)

            filename = f"{record.get(request.filename_field, uuid.uuid4())}.docx"
            output_path = OUTPUT_DIR / filename

            template.save(str(output_path))
            generated.append(filename)

        except Exception as e:
            errors.append({
                "record": record.get(request.filename_field),
                "error": str(e)
            })

    return {
        "generated": len(generated),
        "failed": len(errors),
        "files": generated,
        "errors": errors
    }


@app.post("/templates/upload")
async def upload_template(file: UploadFile = File(...)):
    """Upload a new template."""
    if not file.filename.endswith(".docx"):
        raise HTTPException(400, "Only .docx files are supported")

    template_path = TEMPLATES_DIR / file.filename

    content = await file.read()
    with open(template_path, "wb") as f:
        f.write(content)

    return {"message": f"Template '{file.filename}' uploaded", "name": Path(file.filename).stem}


# Run with: uvicorn service:app --reload
```
