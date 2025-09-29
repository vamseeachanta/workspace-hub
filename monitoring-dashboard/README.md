# Monitoring Dashboard

A comprehensive monitoring and visualization dashboard for test execution, code coverage, performance metrics, and real-time alerts.

## Features

### 🚀 Core Features
- **Real-time Test Execution Monitor** - Live test status updates with WebSocket integration
- **Interactive Data Visualizations** - D3.js charts for trends, heatmaps, and performance graphs
- **Coverage Heatmaps** - Visual representation of code coverage across files
- **Performance Analytics** - Response time tracking and bottleneck analysis
- **Alert System** - Configurable alerts with anomaly detection
- **Dark Mode Support** - Responsive design with theme switching

### 📊 Dashboard Components
- **Test Summary Metrics** - Pass/fail rates, duration trends
- **Coverage Reports** - Line, function, branch, and statement coverage
- **Performance Graphs** - Real-time metrics and historical trends
- **Alert Notifications** - Severity-based alerting with real-time updates

### 🛠 Technical Stack

#### Backend
- **Framework**: Express.js with TypeScript
- **Real-time**: Socket.IO for WebSocket connections
- **API**: REST endpoints + GraphQL for complex queries
- **Caching**: Redis with in-memory fallback
- **Monitoring**: Winston logging with performance tracking

#### Frontend
- **Framework**: React 18 with TypeScript
- **Styling**: TailwindCSS with custom design system
- **Charts**: D3.js for custom visualizations + Recharts
- **State**: React Query for server state management
- **Real-time**: Socket.IO client integration
- **Theme**: Dark/light mode with system preference detection

#### Shared
- **Types**: Zod schemas for runtime validation
- **Utilities**: Shared formatting and calculation functions

## Project Structure

```
monitoring-dashboard/
├── backend/                 # Express.js API server
│   ├── src/
│   │   ├── api/            # REST endpoints and controllers
│   │   ├── graphql/        # GraphQL resolvers and types
│   │   ├── cache/          # Redis caching layer
│   │   └── utils/          # Logging and utilities
├── frontend/               # React dashboard
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Route-based page components
│   │   ├── hooks/          # Custom React hooks
│   │   └── utils/          # Formatting and helper functions
├── shared/                 # Shared types and utilities
│   └── src/
│       ├── types/          # TypeScript type definitions
│       └── utils/          # Shared utility functions
└── package.json           # Workspace configuration
```

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- Redis (optional, uses in-memory fallback)

### Installation

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Build shared package**:
   ```bash
   npm run build:shared
   ```

3. **Start development servers**:
   ```bash
   npm run dev
   ```

This will start:
- Backend API server on http://localhost:3001
- Frontend development server on http://localhost:3000
- GraphQL playground at http://localhost:3001/graphql

### Environment Variables

Create `.env` files in the backend directory:

```bash
# Backend (.env)
NODE_ENV=development
PORT=3001
REDIS_URL=redis://localhost:6379  # Optional
FRONTEND_URL=http://localhost:3000
LOG_LEVEL=debug
```

## API Documentation

### REST Endpoints

#### Tests
- `GET /api/tests` - List tests with filtering
- `POST /api/tests` - Create new test result
- `GET /api/tests/:id` - Get specific test
- `PUT /api/tests/:id` - Update test result
- `DELETE /api/tests/:id` - Delete test

#### Coverage
- `GET /api/coverage` - Get coverage data
- `POST /api/coverage` - Upload coverage data
- `GET /api/coverage/summary` - Coverage summary
- `GET /api/coverage/trends` - Coverage trends

#### Metrics
- `GET /api/metrics` - Performance metrics
- `POST /api/metrics` - Record new metric
- `GET /api/metrics/trends/:type` - Metric trends

#### Alerts
- `GET /api/alerts` - List alerts
- `POST /api/alerts` - Create alert
- `PUT /api/alerts/:id/resolve` - Resolve alert

### GraphQL Schema

The GraphQL endpoint at `/graphql` provides a unified query interface for complex data requirements:

```graphql
query DashboardData {
  dashboardSummary {
    tests { total passed failed passRate }
    coverage { overall lines functions branches }
    performance { avgResponseTime throughput }
    alerts { total unresolved critical high }
  }

  tests(filter: { status: PASSED }, limit: 10) {
    nodes { id name suite status duration }
    pageInfo { total hasNextPage }
  }
}
```

### WebSocket Events

Real-time updates via Socket.IO:

```javascript
// Subscribe to channels
socket.emit('subscribe', ['tests', 'coverage', 'alerts', 'metrics']);

// Listen for events
socket.on('realtime_event', (event) => {
  console.log(event.type, event.payload);
});
```

Event types:
- `test_started` / `test_completed`
- `coverage_updated`
- `alert_triggered`
- `metric_updated`

## Development

### Running Tests
```bash
# Run all tests
npm test

# Run backend tests
npm run test:backend

# Run frontend tests
npm run test:frontend

# Run with coverage
npm run test:coverage
```

### Building for Production
```bash
# Build all packages
npm run build

# Build specific package
npm run build:backend
npm run build:frontend
```

### Linting and Type Checking
```bash
# Lint all packages
npm run lint

# Type check
npm run typecheck
```

## Features Deep Dive

### Real-time Test Execution Monitor

The test execution monitor provides live updates of test runs with:
- Real-time status changes (pending → running → passed/failed)
- Duration tracking for running tests
- Error details for failed tests
- Pass rate calculations
- WebSocket-based updates

### D3.js Visualizations

Custom D3.js components include:
- **Line Charts**: Trend analysis with animations and tooltips
- **Heatmaps**: Coverage and performance data visualization
- **Interactive Elements**: Hover effects, zoom, and filtering

### Alert System with Anomaly Detection

Intelligent alerting system featuring:
- **Rule-based Alerts**: Configurable thresholds for metrics
- **Anomaly Detection**: Statistical analysis for unusual patterns
- **Severity Levels**: Critical, high, medium, low priority
- **Real-time Notifications**: Instant WebSocket updates
- **Alert Management**: Resolution tracking and history

### Performance Optimization

- **Caching**: Redis for API responses with TTL
- **Lazy Loading**: Component-based code splitting
- **Real-time Updates**: Efficient WebSocket event handling
- **Query Optimization**: React Query for smart data fetching

## Customization

### Adding New Metrics

1. Define types in `shared/src/types/index.ts`
2. Add API endpoints in `backend/src/api/controllers/`
3. Create React components in `frontend/src/components/`
4. Add real-time updates via WebSocket

### Custom Visualizations

Create new D3.js components in `frontend/src/components/charts/`:

```typescript
interface CustomChartProps {
  data: DataPoint[];
  width?: number;
  height?: number;
}

export function CustomChart({ data, width = 400, height = 300 }: CustomChartProps) {
  // D3.js implementation
}
```

### Theme Customization

Modify the design system in:
- `frontend/tailwind.config.js` - Colors and design tokens
- `frontend/src/index.css` - CSS custom properties
- `frontend/src/hooks/useTheme.tsx` - Theme logic

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run linting and tests
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Performance Metrics

- **Backend Response Time**: < 100ms average
- **Frontend Load Time**: < 2s initial load
- **Real-time Latency**: < 50ms WebSocket updates
- **Memory Usage**: < 512MB backend, < 100MB frontend
- **Test Coverage**: > 80% across all packages