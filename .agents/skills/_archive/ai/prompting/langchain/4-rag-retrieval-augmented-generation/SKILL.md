---
name: langchain-4-rag-retrieval-augmented-generation
description: 'Sub-skill of langchain: 4. RAG (Retrieval Augmented Generation).'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# 4. RAG (Retrieval Augmented Generation)

## 4. RAG (Retrieval Augmented Generation)


**Complete RAG Pipeline:**
```python
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from pathlib import Path
from typing import List

def create_rag_pipeline(
    documents_dir: str,
    collection_name: str = "engineering_docs",
    chunk_size: int = 1000,
    chunk_overlap: int = 200
):
    """
    Create a complete RAG pipeline.

    Args:
        documents_dir: Directory containing documents
        collection_name: Name for vector store collection
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks

    Returns:
        RAG chain for question answering
    """
    # 1. Load documents
    loader = DirectoryLoader(
        documents_dir,
        glob="**/*.pdf",
        loader_cls=PyPDFLoader,
        show_progress=True
    )
    documents = loader.load()

    print(f"Loaded {len(documents)} document pages")

    # 2. Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)

    print(f"Created {len(chunks)} chunks")

    # 3. Create embeddings and vector store
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory="./chroma_db"
    )

    # 4. Create retriever
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}
    )

    # 5. Create RAG prompt
    rag_prompt = ChatPromptTemplate.from_template("""
    You are an expert assistant answering questions based on the provided context.
    Use only the information from the context to answer.
    If the context doesn't contain the answer, say "I don't have enough information."

    Context:
    {context}

    Question: {question}

    Answer:
    """)

    # 6. Create LLM
    llm = ChatOpenAI(model="gpt-4", temperature=0)

    # 7. Build RAG chain
    def format_docs(docs):
        return "\n\n---\n\n".join(
            f"Source: {doc.metadata.get('source', 'Unknown')}\n{doc.page_content}"
            for doc in docs
        )

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | rag_prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain, retriever

# Usage
rag_chain, retriever = create_rag_pipeline(
    documents_dir="./engineering_docs",
    collection_name="offshore_standards"
)

# Query
answer = rag_chain.invoke(
    "What are the safety factor requirements for mooring lines?"
)
print(answer)

# Get source documents
docs = retriever.get_relevant_documents(
    "mooring line safety factors"
)
for doc in docs:
    print(f"Source: {doc.metadata['source']}")
    print(f"Content: {doc.page_content[:200]}...")
    print()
```

**RAG with Reranking:**
```python
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

def create_reranked_rag_pipeline(
    vectorstore: Chroma,
    top_k_initial: int = 20,
    top_k_final: int = 5
):
    """
    Create RAG pipeline with reranking for better relevance.

    Args:
        vectorstore: Existing vector store
        top_k_initial: Number of docs to retrieve initially
        top_k_final: Number of docs after reranking
    """
    # Base retriever - get more docs initially
    base_retriever = vectorstore.as_retriever(
        search_kwargs={"k": top_k_initial}
    )

    # Reranker using cross-encoder
    reranker_model = HuggingFaceCrossEncoder(
        model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"
    )
    compressor = CrossEncoderReranker(
        model=reranker_model,
        top_n=top_k_final
    )

    # Compression retriever with reranking
    retriever = ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=base_retriever
    )

    # Build chain
    llm = ChatOpenAI(model="gpt-4", temperature=0)

    prompt = ChatPromptTemplate.from_template("""
    Answer the question based on the context below.
    Cite your sources by mentioning which document the information came from.

    Context:
    {context}

    Question: {question}

    Answer with citations:
    """)

    def format_docs_with_citations(docs):
        formatted = []

*Content truncated — see parent skill for full reference.*
