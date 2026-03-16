---
name: sparc-workflow-interface-design
description: 'Sub-skill of sparc-workflow: Interface Design.'
version: 1.1.0
category: coordination
type: reference
scripts_exempt: true
---

# Interface Design

## Interface Design


\`\`\`python
class IProcessor(Protocol):
    def process(self, data: InputData) -> OutputData:
        """Process input and return output."""
        ...

    def validate(self, data: InputData) -> bool:
        """Validate input data."""
        ...
\`\`\`
