---
name: activepieces-6-custom-piece-development
description: 'Sub-skill of activepieces: 6. Custom Piece Development.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 6. Custom Piece Development

## 6. Custom Piece Development


```typescript
// pieces/my-custom-api/src/index.ts
import { createPiece, PieceAuth } from '@activepieces/pieces-framework';
import { createCustomResource } from './lib/actions/create-resource';
import { getCustomResource } from './lib/actions/get-resource';
import { listCustomResources } from './lib/actions/list-resources';
import { resourceCreatedTrigger } from './lib/triggers/resource-created';

const authDescription = `
To get your API key:
1. Go to Settings > API Keys in your dashboard
2. Click "Create New Key"
3. Copy the generated key
`;

export const customApiAuth = PieceAuth.SecretText({
  displayName: 'API Key',
  required: true,
  description: authDescription,
  validate: async ({ auth }) => {
    // Validate the API key
    const response = await fetch('https://api.example.com/validate', {
      headers: { Authorization: `Bearer ${auth}` }
    });

    if (!response.ok) {
      return {
        valid: false,
        error: 'Invalid API key'
      };
    }

    return { valid: true };
  }
});

export const myCustomApi = createPiece({
  displayName: 'My Custom API',
  auth: customApiAuth,
  minimumSupportedRelease: '0.20.0',
  logoUrl: 'https://example.com/logo.png',
  authors: ['your-name'],
  description: 'Connect to My Custom API for resource management',
  actions: [createCustomResource, getCustomResource, listCustomResources],
  triggers: [resourceCreatedTrigger]
});
```

```typescript
// pieces/my-custom-api/src/lib/actions/create-resource.ts
import { createAction, Property } from '@activepieces/pieces-framework';
import { customApiAuth } from '../../index';

export const createCustomResource = createAction({
  name: 'create_resource',
  displayName: 'Create Resource',
  description: 'Create a new resource in My Custom API',
  auth: customApiAuth,
  props: {
    name: Property.ShortText({
      displayName: 'Resource Name',
      required: true,
      description: 'The name of the resource'
    }),
    type: Property.Dropdown({
      displayName: 'Resource Type',
      required: true,
      refreshers: [],
      options: async () => ({
        options: [
          { label: 'Document', value: 'document' },
          { label: 'Image', value: 'image' },
          { label: 'Video', value: 'video' }
        ]
      })
    }),
    tags: Property.Array({
      displayName: 'Tags',
      required: false,
      description: 'Tags to categorize the resource'
    }),
    metadata: Property.Object({
      displayName: 'Metadata',
      required: false,
      description: 'Additional metadata for the resource'
    }),
    content: Property.LongText({
      displayName: 'Content',
      required: true,
      description: 'The content of the resource'
    })
  },
  async run(context) {
    const { auth, propsValue } = context;

    const response = await fetch('https://api.example.com/resources', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${auth}`
      },
      body: JSON.stringify({
        name: propsValue.name,
        type: propsValue.type,
        tags: propsValue.tags || [],
        metadata: propsValue.metadata || {},
        content: propsValue.content
      })
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Failed to create resource: ${error}`);
    }

    const result = await response.json();

    return {
      id: result.id,
      name: result.name,
      type: result.type,
      created_at: result.created_at,
      url: result.url
    };
  }
});
```

```typescript
// pieces/my-custom-api/src/lib/triggers/resource-created.ts
import {
  createTrigger,
  TriggerStrategy,
  Property
} from '@activepieces/pieces-framework';
import { customApiAuth } from '../../index';

export const resourceCreatedTrigger = createTrigger({
  name: 'resource_created',
  displayName: 'Resource Created',
  description: 'Triggers when a new resource is created',
  auth: customApiAuth,
  props: {
    resourceType: Property.Dropdown({
      displayName: 'Resource Type',
      required: false,
      refreshers: [],
      options: async () => ({
        options: [
          { label: 'All Types', value: 'all' },
          { label: 'Document', value: 'document' },
          { label: 'Image', value: 'image' },
          { label: 'Video', value: 'video' }
        ]
      })
    })
  },
  type: TriggerStrategy.WEBHOOK,
  async onEnable(context) {
    const { auth, propsValue, webhookUrl, store } = context;

    // Register webhook with the external API
    const response = await fetch('https://api.example.com/webhooks', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${auth}`
      },
      body: JSON.stringify({
        url: webhookUrl,
        events: ['resource.created'],
        filter: propsValue.resourceType !== 'all'
          ? { type: propsValue.resourceType }
          : undefined
      })
    });

    const webhook = await response.json();

    // Store webhook ID for cleanup
    await store.put('webhookId', webhook.id);
  },
  async onDisable(context) {
    const { auth, store } = context;

*Content truncated — see parent skill for full reference.*
