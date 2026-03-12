import re
text = """1: text
2: ```python
3: code
4: code
5: ```
6: count the files
"""
clean = re.sub(r'```[^\n]*\n.*?```', '', text, flags=re.DOTALL)
print("Original:")
for i, line in enumerate(text.splitlines(), start=1): print(f"{i}: {line}")
print("Clean:")
for i, line in enumerate(clean.splitlines(), start=1): print(f"{i}: {line}")
