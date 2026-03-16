---
name: ai-prompting-langchain-rag-pipeline
description: 'Sub-skill of ai-prompting: LangChain RAG Pipeline (+4).'
version: 1.0.0
category: ai
type: reference
scripts_exempt: true
---

# LangChain RAG Pipeline (+4)

## LangChain RAG Pipeline


```python
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI

# Load and split documents
loader = DirectoryLoader("./docs", glob="**/*.md")

*See sub-skills for full details.*

## DSPy Optimized Pipeline


```python
import dspy
from dspy.teleprompt import BootstrapFewShot

# Define signature
class QASignature(dspy.Signature):
    """Answer questions based on context."""
    context = dspy.InputField(desc="Relevant context")
    question = dspy.InputField(desc="Question to answer")
    answer = dspy.OutputField(desc="Concise answer")

*See sub-skills for full details.*

## Prompt Engineering Patterns


```python
# Chain-of-Thought Prompting
COT_TEMPLATE = """
Solve this step by step:

Problem: {problem}

Let's think through this carefully:
1. First, I'll identify the key information...
2. Next, I'll determine the approach...

*See sub-skills for full details.*

## PandasAI Data Querying


```python
import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm import OpenAI

# Load data
df = pd.read_csv("sales_data.csv")

# Create AI-enabled dataframe
llm = OpenAI(api_token="...")

*See sub-skills for full details.*

## Agenta Prompt Management


```python
from agenta import Agenta

# Initialize
ag = Agenta()

# Define prompt variant
@ag.variant
def summarize_text(text: str, style: str = "concise"):
    prompt = f"""

*See sub-skills for full details.*
