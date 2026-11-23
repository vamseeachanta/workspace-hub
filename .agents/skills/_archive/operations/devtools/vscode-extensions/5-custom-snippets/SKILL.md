---
name: vscode-extensions-5-custom-snippets
description: 'Sub-skill of vscode-extensions: 5. Custom Snippets.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 5. Custom Snippets

## 5. Custom Snippets


```jsonc
// snippets/python.json
// Location: ~/.config/Code/User/snippets/python.json
{
    "Python Main Block": {
        "prefix": "main",
        "body": [
            "def main():",
            "    ${1:pass}",
            "",
            "",
            "if __name__ == \"__main__\":",
            "    main()"
        ],
        "description": "Python main block"
    },
    "Python Class": {
        "prefix": "class",
        "body": [
            "class ${1:ClassName}:",
            "    \"\"\"${2:Class description.}\"\"\"",
            "",
            "    def __init__(self, ${3:args}):",
            "        ${4:pass}",
            "",
            "    def ${5:method}(self):",
            "        ${6:pass}"
        ],
        "description": "Python class definition"
    },
    "Python Dataclass": {
        "prefix": "dataclass",
        "body": [
            "from dataclasses import dataclass",
            "",
            "",
            "@dataclass",
            "class ${1:ClassName}:",
            "    \"\"\"${2:Description.}\"\"\"",
            "",
            "    ${3:field}: ${4:str}"
        ],
        "description": "Python dataclass"
    },
    "Python Type Hints": {
        "prefix": "typed",
        "body": [
            "def ${1:function_name}(",
            "    ${2:param}: ${3:str}",
            ") -> ${4:None}:",
            "    \"\"\"${5:Description.}\"\"\"",
            "    ${6:pass}"
        ],
        "description": "Typed function signature"
    },
    "Python Pytest Test": {
        "prefix": "test",
        "body": [
            "def test_${1:name}():",
            "    # Arrange",
            "    ${2:pass}",
            "",
            "    # Act",
            "    ${3:result = None}",
            "",
            "    # Assert",
            "    assert ${4:result is not None}"
        ],
        "description": "Pytest test function"
    },
    "ABOUTME Comment": {
        "prefix": "aboutme",
        "body": [
            "# ABOUTME: ${1:Brief description of file purpose}",
            "# ABOUTME: ${2:Additional detail about what the file does}"
        ],
        "description": "ABOUTME file header comment"
    }
}
```

```jsonc
// snippets/typescript.json
{
    "React Functional Component": {
        "prefix": "rfc",
        "body": [
            "interface ${1:ComponentName}Props {",
            "  ${2:prop}: ${3:string};",
            "}",
            "",
            "export function ${1:ComponentName}({ ${2:prop} }: ${1:ComponentName}Props) {",
            "  return (",
            "    <div>",
            "      ${4:content}",
            "    </div>",
            "  );",
            "}"
        ],
        "description": "React Functional Component with TypeScript"
    },
    "React useState Hook": {
        "prefix": "usestate",
        "body": [
            "const [${1:state}, set${1/(.*)/${1:/capitalize}/}] = useState<${2:string}>(${3:''});"
        ],
        "description": "React useState hook with TypeScript"
    },
    "React useEffect Hook": {
        "prefix": "useeffect",
        "body": [
            "useEffect(() => {",
            "  ${1:// effect}",
            "",
            "  return () => {",
            "    ${2:// cleanup}",
            "  };",
            "}, [${3:dependencies}]);"
        ],
        "description": "React useEffect hook"
    },
    "TypeScript Interface": {
        "prefix": "interface",
        "body": [
            "interface ${1:InterfaceName} {",
            "  ${2:property}: ${3:type};",
            "}"
        ],
        "description": "TypeScript interface"
    },
    "TypeScript Type": {
        "prefix": "type",
        "body": [
            "type ${1:TypeName} = {",
            "  ${2:property}: ${3:type};",
            "};"
        ],
        "description": "TypeScript type alias"
    },
    "Async Function": {
        "prefix": "asyncfn",
        "body": [
            "async function ${1:functionName}(${2:params}): Promise<${3:void}> {",
            "  try {",
            "    ${4:// implementation}",
            "  } catch (error) {",
            "    console.error(error);",
            "    throw error;",
            "  }",
            "}"
        ],
        "description": "Async function with error handling"
    }
}
```
