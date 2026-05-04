---
name: dspy-3-retrieval-augmented-generation
description: 'Sub-skill of dspy: 3. Retrieval-Augmented Generation.'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# 3. Retrieval-Augmented Generation

## 3. Retrieval-Augmented Generation


**RAG with DSPy:**
```python
import dspy
from dspy.retrieve.chromadb_rm import ChromadbRM

# Configure retriever
retriever = ChromadbRM(
    collection_name="engineering_docs",
    persist_directory="./chroma_db",
    k=5
)

# Configure DSPy with retriever
dspy.settings.configure(
    lm=dspy.OpenAI(model="gpt-4"),
    rm=retriever
)

class RAGSignature(dspy.Signature):
    """Answer questions using retrieved context."""
    context = dspy.InputField(desc="Retrieved relevant passages")
    question = dspy.InputField(desc="Question to answer")
    answer = dspy.OutputField(desc="Answer based on context")

class RAGModule(dspy.Module):
    """RAG module with retrieval and generation."""

    def __init__(self, num_passages=5):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=num_passages)
        self.generate = dspy.ChainOfThought(RAGSignature)

    def forward(self, question):
        # Retrieve relevant passages
        passages = self.retrieve(question).passages

        # Generate answer with context
        context = "\n\n".join(passages)
        result = self.generate(context=context, question=question)

        return dspy.Prediction(
            answer=result.answer,
            passages=passages,
            reasoning=result.rationale
        )

# Usage
rag = RAGModule(num_passages=5)
result = rag(question="What are the safety factor requirements for moorings?")

print(f"Answer: {result.answer}")
print(f"Sources: {len(result.passages)} passages retrieved")
```

**Multi-Hop RAG:**
```python
class MultiHopRAG(dspy.Module):
    """
    Multi-hop RAG that retrieves, reasons, and retrieves again
    for complex questions requiring multiple pieces of information.
    """

    def __init__(self, num_hops=2, passages_per_hop=3):
        super().__init__()
        self.num_hops = num_hops
        self.retrieve = dspy.Retrieve(k=passages_per_hop)
        self.generate_query = dspy.ChainOfThought(
            "context, question -> search_query"
        )
        self.generate_answer = dspy.ChainOfThought(RAGSignature)

    def forward(self, question):
        context = []
        current_query = question

        for hop in range(self.num_hops):
            # Retrieve for current query
            passages = self.retrieve(current_query).passages
            context.extend(passages)

            if hop < self.num_hops - 1:
                # Generate refined query for next hop
                all_context = "\n\n".join(context)
                query_result = self.generate_query(
                    context=all_context,
                    question=question
                )
                current_query = query_result.search_query

        # Final answer generation
        full_context = "\n\n".join(context)
        result = self.generate_answer(
            context=full_context,
            question=question
        )

        return dspy.Prediction(
            answer=result.answer,
            hops=self.num_hops,
            total_passages=len(context)
        )

# Usage
multi_hop_rag = MultiHopRAG(num_hops=3, passages_per_hop=3)
result = multi_hop_rag(
    question="How does fatigue analysis relate to mooring safety factors?"
)
```
