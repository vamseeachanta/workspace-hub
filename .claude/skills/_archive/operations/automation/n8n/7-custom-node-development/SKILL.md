---
name: n8n-7-custom-node-development
description: 'Sub-skill of n8n: 7. Custom Node Development.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 7. Custom Node Development

## 7. Custom Node Development


```typescript
// packages/nodes-custom/nodes/MyCustomNode/MyCustomNode.node.ts
import {
  IExecuteFunctions,
  INodeExecutionData,
  INodeType,
  INodeTypeDescription,
  NodeOperationError,
} from 'n8n-workflow';

export class MyCustomNode implements INodeType {
  description: INodeTypeDescription = {
    displayName: 'My Custom Node',
    name: 'myCustomNode',
    icon: 'file:myicon.svg',
    group: ['transform'],
    version: 1,
    subtitle: '={{$parameter["operation"]}}',
    description: 'Custom node for specific business logic',
    defaults: {
      name: 'My Custom Node',
    },
    inputs: ['main'],
    outputs: ['main'],
    credentials: [
      {
        name: 'myCustomApi',
        required: true,
      },
    ],
    properties: [
      {
        displayName: 'Operation',
        name: 'operation',
        type: 'options',
        noDataExpression: true,
        options: [
          {
            name: 'Process',
            value: 'process',
            description: 'Process data through custom logic',
          },
          {
            name: 'Validate',
            value: 'validate',
            description: 'Validate data against rules',
          },
        ],
        default: 'process',
      },
      {
        displayName: 'Input Field',
        name: 'inputField',
        type: 'string',
        default: 'data',
        required: true,
        description: 'Field to process',
      },
      {
        displayName: 'Options',
        name: 'options',
        type: 'collection',
        placeholder: 'Add Option',
        default: {},
        options: [
          {
            displayName: 'Strict Mode',
            name: 'strictMode',
            type: 'boolean',
            default: false,
            description: 'Enable strict validation',
          },
          {
            displayName: 'Output Format',
            name: 'outputFormat',
            type: 'options',
            options: [
              { name: 'JSON', value: 'json' },
              { name: 'Array', value: 'array' },
            ],
            default: 'json',
          },
        ],
      },
    ],
  };

  async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
    const items = this.getInputData();
    const returnData: INodeExecutionData[] = [];

    const operation = this.getNodeParameter('operation', 0) as string;
    const inputField = this.getNodeParameter('inputField', 0) as string;
    const options = this.getNodeParameter('options', 0, {}) as {
      strictMode?: boolean;
      outputFormat?: string;
    };

    // Get credentials
    const credentials = await this.getCredentials('myCustomApi');

    for (let i = 0; i < items.length; i++) {
      try {
        const item = items[i].json;
        const inputData = item[inputField];

        if (!inputData && options.strictMode) {
          throw new NodeOperationError(
            this.getNode(),
            `Field "${inputField}" not found in item ${i}`,
            { itemIndex: i }
          );
        }

        let result: any;

        if (operation === 'process') {
          result = await this.processData(inputData, credentials);
        } else if (operation === 'validate') {
          result = this.validateData(inputData, options.strictMode);
        }

        returnData.push({
          json: {
            ...item,
            processed: result,
            timestamp: new Date().toISOString(),
          },
        });
      } catch (error) {
        if (this.continueOnFail()) {
          returnData.push({
            json: {
              error: (error as Error).message,
              itemIndex: i,
            },
          });
          continue;
        }
        throw error;
      }
    }

    return [returnData];
  }

  private async processData(data: any, credentials: any): Promise<any> {
    // Custom processing logic
    return {
      original: data,
      processed: true,
      api_key_length: credentials.apiKey?.length || 0,
    };
  }

  private validateData(data: any, strict: boolean): any {
    const isValid = data !== null && data !== undefined;
    return {
      valid: isValid,
      strict_mode: strict,
      type: typeof data,
    };
  }
}
```

```typescript
// packages/nodes-custom/credentials/MyCustomApi.credentials.ts
import {
  ICredentialType,
  INodeProperties,
} from 'n8n-workflow';

export class MyCustomApi implements ICredentialType {
  name = 'myCustomApi';
  displayName = 'My Custom API';
  documentationUrl = 'https://docs.example.com/api';
  properties: INodeProperties[] = [
    {
      displayName: 'API Key',
      name: 'apiKey',
      type: 'string',
      typeOptions: {
        password: true,

*Content truncated — see parent skill for full reference.*
