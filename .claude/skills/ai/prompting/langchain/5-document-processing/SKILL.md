---
name: langchain-5-document-processing
description: 'Sub-skill of langchain: 5. Document Processing.'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# 5. Document Processing

## 5. Document Processing


**Multi-Format Document Loader:**
```python
from langchain_community.document_loaders import (
    DirectoryLoader,
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredExcelLoader,
    TextLoader,
    CSVLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class LoaderConfig:
    """Configuration for document loader."""
    glob_pattern: str
    loader_cls: type
    loader_kwargs: dict = None

LOADER_CONFIGS = {
    ".pdf": LoaderConfig("**/*.pdf", PyPDFLoader),
    ".docx": LoaderConfig("**/*.docx", Docx2txtLoader),
    ".xlsx": LoaderConfig("**/*.xlsx", UnstructuredExcelLoader),
    ".csv": LoaderConfig("**/*.csv", CSVLoader),
    ".txt": LoaderConfig("**/*.txt", TextLoader),
    ".md": LoaderConfig("**/*.md", TextLoader),
}

def load_documents_multi_format(
    directory: str,
    extensions: List[str] = None,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List:
    """
    Load documents from multiple formats.

    Args:
        directory: Base directory for documents
        extensions: List of extensions to load (None = all)
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks

    Returns:
        List of chunked documents
    """
    if extensions is None:
        extensions = list(LOADER_CONFIGS.keys())

    all_documents = []

    for ext in extensions:
        if ext not in LOADER_CONFIGS:
            print(f"Warning: No loader for {ext}")
            continue

        config = LOADER_CONFIGS[ext]

        try:
            loader = DirectoryLoader(
                directory,
                glob=config.glob_pattern,
                loader_cls=config.loader_cls,
                loader_kwargs=config.loader_kwargs or {},
                show_progress=True
            )
            docs = loader.load()

            print(f"Loaded {len(docs)} documents with extension {ext}")
            all_documents.extend(docs)

        except Exception as e:
            print(f"Error loading {ext} files: {e}")

    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    chunks = text_splitter.split_documents(all_documents)

    print(f"Total: {len(all_documents)} documents -> {len(chunks)} chunks")

    return chunks

def add_metadata_to_chunks(
    chunks: List,
    additional_metadata: Dict = None
) -> List:
    """
    Enrich document chunks with additional metadata.
    """
    for chunk in chunks:
        # Extract filename without path
        source = chunk.metadata.get("source", "")
        chunk.metadata["filename"] = Path(source).name
        chunk.metadata["extension"] = Path(source).suffix

        # Add custom metadata
        if additional_metadata:
            chunk.metadata.update(additional_metadata)

        # Add chunk stats
        chunk.metadata["chunk_length"] = len(chunk.page_content)
        chunk.metadata["word_count"] = len(chunk.page_content.split())

    return chunks

# Usage
chunks = load_documents_multi_format(
    directory="./project_docs",
    extensions=[".pdf", ".docx", ".md"],
    chunk_size=1500,
    chunk_overlap=300
)

enriched_chunks = add_metadata_to_chunks(
    chunks,
    additional_metadata={
        "project": "Offshore Platform Analysis",
        "version": "2.0"
    }
)

print(f"First chunk metadata: {enriched_chunks[0].metadata}")
```
