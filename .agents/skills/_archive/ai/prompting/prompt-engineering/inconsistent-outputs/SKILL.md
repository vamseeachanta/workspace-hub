---
name: prompt-engineering-inconsistent-outputs
description: 'Sub-skill of prompt-engineering: Inconsistent Outputs (+2).'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# Inconsistent Outputs (+2)

## Inconsistent Outputs


```python
# Lower temperature for consistency
response = client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    temperature=0.1  # Lower = more consistent
)

# Or use seed for reproducibility
response = client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    seed=42
)
```


## Outputs Too Long/Short


```python
# Control length explicitly
prompt = """
Provide a summary in exactly 3 sentences.
Do not exceed 100 words.
"""

# Or use max_tokens
response = client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    max_tokens=150
)
```


## Wrong Format


```python
# Be very explicit about format
prompt = """
Return ONLY a JSON object. No explanation, no markdown.

{
    "key": "value"
}
"""

# Validate and retry
def get_json_response(prompt, max_retries=3):
    for attempt in range(max_retries):
        response = llm(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            prompt = f"Your response was not valid JSON. Try again.\n\n{prompt}"
    raise ValueError("Failed to get valid JSON")
```
