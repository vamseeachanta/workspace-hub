---
name: langchain-1-basic-chain-composition
description: 'Sub-skill of langchain: 1. Basic Chain Composition.'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# 1. Basic Chain Composition

## 1. Basic Chain Composition


**Simple LLM Chain:**
```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def create_simple_chain(
    model: str = "gpt-4",
    temperature: float = 0.7
):
    """
    Create a simple prompt-model-output chain.

    Args:
        model: Model name to use
        temperature: Sampling temperature

    Returns:
        Runnable chain that accepts dict input
    """
    # Define prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant specializing in {domain}."),
        ("human", "{question}")
    ])

    # Initialize LLM
    llm = ChatOpenAI(model=model, temperature=temperature)

    # Create chain with LCEL (LangChain Expression Language)
    chain = prompt | llm | StrOutputParser()

    return chain

# Usage
chain = create_simple_chain(model="gpt-4", temperature=0.3)

response = chain.invoke({
    "domain": "marine engineering",
    "question": "What are the key factors in mooring system design?"
})

print(response)
```

**Sequential Chain with Multiple Steps:**
```python
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

def create_analysis_chain():
    """
    Create a multi-step analysis chain:
    1. Extract key points
    2. Analyze implications
    3. Generate recommendations
    """
    llm = ChatOpenAI(model="gpt-4", temperature=0.3)

    # Step 1: Extract key points
    extract_prompt = ChatPromptTemplate.from_template(
        "Extract the 5 most important points from this text:\n\n{text}\n\nKey Points:"
    )

    # Step 2: Analyze implications
    analyze_prompt = ChatPromptTemplate.from_template(
        "Based on these key points:\n{key_points}\n\n"
        "What are the main implications and potential risks?"
    )

    # Step 3: Generate recommendations
    recommend_prompt = ChatPromptTemplate.from_template(
        "Given these key points:\n{key_points}\n\n"
        "And this analysis:\n{analysis}\n\n"
        "Provide 3-5 actionable recommendations."
    )

    # Build chain
    chain = (
        {"text": RunnablePassthrough()}
        | RunnableParallel(
            text=RunnablePassthrough(),
            key_points=extract_prompt | llm | StrOutputParser()
        )
        | RunnableParallel(
            key_points=lambda x: x["key_points"],
            analysis=analyze_prompt | llm | StrOutputParser()
        )
        | recommend_prompt
        | llm
        | StrOutputParser()
    )

    return chain

# Usage
analysis_chain = create_analysis_chain()

document_text = """
The offshore wind farm project faces several challenges including
supply chain delays, regulatory approval processes, and environmental
impact assessments. Budget overruns of 15% have been reported...
"""

recommendations = analysis_chain.invoke(document_text)
print(recommendations)
```
