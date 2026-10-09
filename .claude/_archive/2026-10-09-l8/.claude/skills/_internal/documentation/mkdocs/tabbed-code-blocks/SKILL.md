---
name: mkdocs-tabbed-code-blocks
description: 'Sub-skill of mkdocs: Tabbed Code Blocks.'
version: 1.0.0
category: _internal
type: reference
scripts_exempt: true
---

# Tabbed Code Blocks

## Tabbed Code Blocks


=== "Python"
    ```python
    def greet(name):
        return f"Hello, {name}!"
    ```

=== "JavaScript"
    ```javascript
    function greet(name) {
        return `Hello, ${name}!`;
    }
    ```

=== "Go"
    ```go
    func greet(name string) string {
        return fmt.Sprintf("Hello, %s!", name)
    }
    ```

=== "Rust"
    ```rust
    fn greet(name: &str) -> String {
        format!("Hello, {}!", name)
    }
    ```
