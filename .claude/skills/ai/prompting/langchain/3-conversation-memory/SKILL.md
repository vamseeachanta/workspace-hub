---
name: langchain-3-conversation-memory
description: 'Sub-skill of langchain: 3. Conversation Memory.'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# 3. Conversation Memory

## 3. Conversation Memory


**Conversation Buffer Memory:**
```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

# Store for session histories
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """Get or create message history for a session."""
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

def create_conversational_chain():
    """
    Create a chain with conversation memory.
    """
    llm = ChatOpenAI(model="gpt-4", temperature=0.7)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert offshore engineering consultant.
        You help with mooring design, vessel dynamics, and marine operations.
        Maintain context from previous messages in the conversation."""),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])

    chain = prompt | llm

    # Wrap with message history
    chain_with_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history"
    )

    return chain_with_history

# Usage
conversational_chain = create_conversational_chain()

# First message
response1 = conversational_chain.invoke(
    {"input": "I'm designing a spread mooring system for a 100,000 DWT tanker."},
    config={"configurable": {"session_id": "project-123"}}
)
print(f"Assistant: {response1.content}")

# Follow-up (remembers context)
response2 = conversational_chain.invoke(
    {"input": "What line configuration would you recommend?"},
    config={"configurable": {"session_id": "project-123"}}
)
print(f"Assistant: {response2.content}")

# Check history
history = get_session_history("project-123")
print(f"\nConversation has {len(history.messages)} messages")
```

**Summary Memory for Long Conversations:**
```python
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chains import ConversationChain

def create_summary_memory_chain():
    """
    Create chain with summary memory for long conversations.
    Keeps recent messages verbatim, summarizes older ones.
    """
    llm = ChatOpenAI(model="gpt-4", temperature=0.7)

    # Summary buffer keeps last 1000 tokens verbatim
    memory = ConversationSummaryBufferMemory(
        llm=llm,
        max_token_limit=1000,
        return_messages=True
    )

    chain = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=True
    )

    return chain, memory

# Usage
chain, memory = create_summary_memory_chain()

# Simulate long conversation
responses = []
questions = [
    "What are the main types of mooring systems?",
    "Tell me about spread moorings in detail.",
    "What about single point moorings?",
    "How do turret moorings work?",
    "Compare the maintenance requirements.",
    "What are the cost implications?"
]

for q in questions:
    response = chain.predict(input=q)
    responses.append(response)
    print(f"Q: {q}")
    print(f"A: {response[:200]}...")
    print()

# Check memory state
print("Memory Summary:")
print(memory.moving_summary_buffer)
```
