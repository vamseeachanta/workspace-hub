# Reporting and Notification System

## System Overview

The Reporting and Notification System provides comprehensive monitoring, alerting, and visualization capabilities for test baseline metrics, enabling teams to stay informed about quality trends and respond quickly to issues.

## Architecture Components

```
┌─────────────────────────────────────────────────────────────────┐
│                 Reporting & Notification System                │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────┐│
│  │  Real-time  │  │ Dashboard   │  │ Report      │  │  Alert   ││
│  │ Monitoring  │  │   Engine    │  │ Generator   │  │  Engine  ││
│  └─────────────┘  └─────────────┘  └─────────────┘  └──────────┘│
│         │               │               │               │       │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              Notification Gateway                          ││
│  └─────────────────────────────────────────────────────────────┘│
│                            │                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │         External Integrations (Slack, Email, etc.)         ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## 1. Real-time Monitoring System

### Monitoring Dashboard Backend
```javascript
// monitoring-service.js
class MonitoringService {
  constructor(config) {
    this.config = config;
    this.websocketServer = null;
    this.activeConnections = new Set();
    this.metricsBuffer = new Map();
    this.alertRules = new Map();
  }

  async initialize() {
    // Initialize WebSocket server for real-time updates
    this.websocketServer = new WebSocketServer({
      port: this.config.websocketPort || 8080,
      path: '/ws/monitoring'
    });

    this.websocketServer.on('connection', (ws, request) => {
      this.handleNewConnection(ws, request);
    });

    // Initialize alert engine
    await this.loadAlertRules();

    // Start metric aggregation service
    this.startMetricAggregation();

    console.log(`Monitoring service started on port ${this.config.websocketPort}`);
  }

  handleNewConnection(ws, request) {
    const connectionId = this.generateConnectionId();
    const connection = {
      id: connectionId,
      ws,
      subscriptions: new Set(),
      filters: {},
      lastActivity: Date.now()
    };

    this.activeConnections.add(connection);

    ws.on('message', (message) => {
      this.handleClientMessage(connection, message);
    });

    ws.on('close', () => {
      this.activeConnections.delete(connection);
    });

    ws.on('error', (error) => {
      console.error(`WebSocket error for connection ${connectionId}:`, error);
      this.activeConnections.delete(connection);
    });

    // Send initial connection confirmation
    this.sendToClient(connection, {
      type: 'connection_established',
      connectionId,
      timestamp: new Date().toISOString()
    });
  }

  handleClientMessage(connection, rawMessage) {
    try {
      const message = JSON.parse(rawMessage);

      switch (message.type) {
        case 'subscribe':
          this.handleSubscription(connection, message);
          break;

        case 'unsubscribe':
          this.handleUnsubscription(connection, message);
          break;

        case 'set_filters':
          this.handleFilterUpdate(connection, message);
          break;

        case 'request_historical':
          this.handleHistoricalRequest(connection, message);
          break;

        default:
          this.sendError(connection, `Unknown message type: ${message.type}`);
      }
    } catch (error) {
      this.sendError(connection, `Invalid message format: ${error.message}`);
    }
  }

  handleSubscription(connection, message) {
    const { channels, projects, branches, environments } = message;

    // Validate subscription parameters
    if (!channels || !Array.isArray(channels)) {
      return this.sendError(connection, 'Invalid channels parameter');
    }

    // Add subscriptions
    channels.forEach(channel => {
      connection.subscriptions.add(channel);
    });

    // Update filters
    if (projects) connection.filters.projects = projects;
    if (branches) connection.filters.branches = branches;
    if (environments) connection.filters.environments = environments;

    this.sendToClient(connection, {
      type: 'subscription_confirmed',
      channels,
      filters: connection.filters,
      timestamp: new Date().toISOString()
    });

    // Send current state for subscribed channels
    this.sendCurrentState(connection, channels);
  }

  async sendCurrentState(connection, channels) {
    for (const channel of channels) {
      switch (channel) {
        case 'live_metrics':
          await this.sendLiveMetrics(connection);
          break;

        case 'alerts':
          await this.sendActiveAlerts(connection);
          break;

        case 'builds':
          await this.sendRecentBuilds(connection);
          break;

        case 'trends':
          await this.sendTrendSummary(connection);
          break;
      }
    }
  }

  async onNewMetrics(metrics, context) {
    // Buffer metrics for real-time transmission
    const key = `${context.project}:${context.branch}:${context.environment}`;
    this.metricsBuffer.set(key, {
      metrics,
      context,
      timestamp: new Date().toISOString()
    });

    // Broadcast to subscribed clients
    this.broadcastToSubscribers('live_metrics', {
      type: 'new_metrics',
      metrics,
      context,
      timestamp: new Date().toISOString()
    });

    // Check alert rules
    await this.evaluateAlertRules(metrics, context);
  }

  broadcastToSubscribers(channel, message) {
    this.activeConnections.forEach(connection => {
      if (connection.subscriptions.has(channel) && this.matchesFilters(message, connection.filters)) {
        this.sendToClient(connection, message);
      }
    });
  }

  matchesFilters(message, filters) {
    if (!message.context) return true;

    if (filters.projects && !filters.projects.includes(message.context.project)) {
      return false;
    }

    if (filters.branches && !filters.branches.includes(message.context.branch)) {
      return false;
    }

    if (filters.environments && !filters.environments.includes(message.context.environment)) {
      return false;
    }

    return true;
  }

  sendToClient(connection, message) {
    if (connection.ws.readyState === WebSocket.OPEN) {
      connection.ws.send(JSON.stringify(message));
      connection.lastActivity = Date.now();
    }
  }
}
```

### Real-time Dashboard Frontend
```javascript
// dashboard-client.js
class DashboardClient {
  constructor(config) {
    this.config = config;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
    this.subscriptions = new Set();
    this.eventHandlers = new Map();
  }

  async connect() {
    try {
      const wsUrl = `ws://${this.config.host}:${this.config.port}/ws/monitoring`;
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('Connected to monitoring service');
        this.reconnectAttempts = 0;
        this.onConnected();
      };

      this.ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        this.handleMessage(message);
      };

      this.ws.onclose = () => {
        console.log('Disconnected from monitoring service');
        this.scheduleReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

    } catch (error) {
      console.error('Failed to connect:', error);
      this.scheduleReconnect();
    }
  }

  scheduleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      setTimeout(() => {
        this.reconnectAttempts++;
        console.log(`Reconnection attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
        this.connect();
      }, this.reconnectDelay * Math.pow(2, this.reconnectAttempts));
    }
  }

  onConnected() {
    // Re-establish subscriptions after reconnection
    if (this.subscriptions.size > 0) {
      this.subscribe(Array.from(this.subscriptions));
    }
  }

  subscribe(channels, filters = {}) {
    channels.forEach(channel => this.subscriptions.add(channel));

    this.send({
      type: 'subscribe',
      channels,
      ...filters
    });
  }

  unsubscribe(channels) {
    channels.forEach(channel => this.subscriptions.delete(channel));

    this.send({
      type: 'unsubscribe',
      channels
    });
  }

  on(eventType, handler) {
    if (!this.eventHandlers.has(eventType)) {
      this.eventHandlers.set(eventType, new Set());
    }
    this.eventHandlers.get(eventType).add(handler);
  }

  off(eventType, handler) {
    if (this.eventHandlers.has(eventType)) {
      this.eventHandlers.get(eventType).delete(handler);
    }
  }

  handleMessage(message) {
    const handlers = this.eventHandlers.get(message.type);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(message);
        } catch (error) {
          console.error(`Error in event handler for ${message.type}:`, error);
        }
      });
    }
  }

  send(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }
}

// Dashboard UI Components
class MetricsDashboard {
  constructor(containerId, client) {
    this.container = document.getElementById(containerId);
    this.client = client;
    this.charts = new Map();
    this.setupEventHandlers();
  }

  setupEventHandlers() {
    this.client.on('new_metrics', (message) => {
      this.updateMetricsDisplay(message.metrics, message.context);
    });

    this.client.on('alert_triggered', (message) => {
      this.showAlert(message.alert);
    });

    this.client.on('trend_update', (message) => {
      this.updateTrendCharts(message.trends);
    });
  }

  updateMetricsDisplay(metrics, context) {
    // Update real-time metric displays
    this.updateMetricCard('pass-rate', metrics.execution.pass_rate_percentage, '%');
    this.updateMetricCard('coverage', metrics.coverage?.overall?.line_coverage || 0, '%');
    this.updateMetricCard('execution-time', metrics.execution.total_execution_time_ms, 'ms');

    // Update charts
    this.updateChart('pass-rate-trend', context.timestamp, metrics.execution.pass_rate_percentage);
    this.updateChart('coverage-trend', context.timestamp, metrics.coverage?.overall?.line_coverage || 0);

    // Update context information
    this.updateContextDisplay(context);
  }

  updateMetricCard(cardId, value, unit) {
    const card = document.getElementById(cardId);
    if (card) {
      const valueElement = card.querySelector('.metric-value');
      const previousValue = parseFloat(valueElement.textContent);

      valueElement.textContent = `${value.toFixed(2)}${unit}`;

      // Add visual indication of change
      if (!isNaN(previousValue)) {
        const change = value - previousValue;
        card.classList.remove('improving', 'degrading');

        if (Math.abs(change) > 0.1) {
          card.classList.add(change > 0 ? 'improving' : 'degrading');
          setTimeout(() => {
            card.classList.remove('improving', 'degrading');
          }, 2000);
        }
      }
    }
  }

  updateChart(chartId, timestamp, value) {
    let chart = this.charts.get(chartId);

    if (!chart) {
      chart = this.createChart(chartId);
      this.charts.set(chartId, chart);
    }

    // Add new data point
    chart.data.labels.push(new Date(timestamp).toLocaleTimeString());
    chart.data.datasets[0].data.push(value);

    // Keep only last 50 data points
    if (chart.data.labels.length > 50) {
      chart.data.labels.shift();
      chart.data.datasets[0].data.shift();
    }

    chart.update('none'); // No animation for real-time updates
  }

  createChart(chartId) {
    const ctx = document.getElementById(chartId).getContext('2d');

    return new Chart(ctx, {
      type: 'line',
      data: {
        labels: [],
        datasets: [{
          label: 'Value',
          data: [],
          borderColor: '#4CAF50',
          backgroundColor: 'rgba(76, 175, 80, 0.1)',
          borderWidth: 2,
          fill: true,
          tension: 0.4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        scales: {
          x: {
            display: false
          },
          y: {
            beginAtZero: true
          }
        },
        plugins: {
          legend: {
            display: false
          }
        }
      }
    });
  }

  showAlert(alert) {
    const alertsContainer = document.getElementById('alerts-container');

    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${alert.severity}`;
    alertElement.innerHTML = `
      <div class="alert-header">
        <span class="alert-icon">${this.getAlertIcon(alert.severity)}</span>
        <span class="alert-title">${alert.title}</span>
        <span class="alert-time">${new Date(alert.timestamp).toLocaleTimeString()}</span>
      </div>
      <div class="alert-message">${alert.message}</div>
      <div class="alert-context">
        Project: ${alert.context.project} | Branch: ${alert.context.branch} | Environment: ${alert.context.environment}
      </div>
    `;

    alertsContainer.insertBefore(alertElement, alertsContainer.firstChild);

    // Auto-remove after 30 seconds for non-critical alerts
    if (alert.severity !== 'critical') {
      setTimeout(() => {
        if (alertElement.parentNode) {
          alertElement.remove();
        }
      }, 30000);
    }
  }

  getAlertIcon(severity) {
    const icons = {
      critical: '🚨',
      major: '⚠️',
      minor: '⚡',
      info: 'ℹ️'
    };
    return icons[severity] || '📊';
  }
}
```

## 2. Alert Engine

### Alert Rule Engine
```javascript
// alert-engine.js
class AlertEngine {
  constructor(config) {
    this.config = config;
    this.rules = new Map();
    this.activeAlerts = new Map();
    this.notificationGateway = new NotificationGateway(config.notifications);
    this.cooldownPeriods = new Map();
  }

  async loadRules() {
    // Load alert rules from configuration
    const ruleConfigs = await this.config.storage.getAlertRules();

    ruleConfigs.forEach(ruleConfig => {
      const rule = new AlertRule(ruleConfig);
      this.rules.set(rule.id, rule);
    });

    console.log(`Loaded ${this.rules.size} alert rules`);
  }

  async evaluateRules(metrics, context) {
    const alertsTriggered = [];

    for (const [ruleId, rule] of this.rules) {
      try {
        if (this.shouldEvaluateRule(rule, context)) {
          const evaluation = await rule.evaluate(metrics, context);

          if (evaluation.triggered) {
            const alert = await this.createAlert(rule, evaluation, context);
            alertsTriggered.push(alert);
          } else {
            // Check if we should resolve an existing alert
            await this.resolveAlertIfExists(ruleId, context);
          }
        }
      } catch (error) {
        console.error(`Error evaluating rule ${ruleId}:`, error);
      }
    }

    return alertsTriggered;
  }

  shouldEvaluateRule(rule, context) {
    // Check if rule applies to current context
    if (rule.filters.projects && !rule.filters.projects.includes(context.project)) {
      return false;
    }

    if (rule.filters.branches && !rule.filters.branches.includes(context.branch)) {
      return false;
    }

    if (rule.filters.environments && !rule.filters.environments.includes(context.environment)) {
      return false;
    }

    // Check cooldown period
    const cooldownKey = `${rule.id}:${context.project}:${context.branch}:${context.environment}`;
    const lastTrigger = this.cooldownPeriods.get(cooldownKey);

    if (lastTrigger && Date.now() - lastTrigger < rule.cooldownMs) {
      return false;
    }

    return true;
  }

  async createAlert(rule, evaluation, context) {
    const alertId = this.generateAlertId();

    const alert = {
      id: alertId,
      ruleId: rule.id,
      title: rule.title,
      message: this.formatAlertMessage(rule, evaluation, context),
      severity: rule.severity,
      context,
      triggeredAt: new Date().toISOString(),
      status: 'active',
      evaluation
    };

    // Store active alert
    this.activeAlerts.set(alertId, alert);

    // Set cooldown
    const cooldownKey = `${rule.id}:${context.project}:${context.branch}:${context.environment}`;
    this.cooldownPeriods.set(cooldownKey, Date.now());

    // Send notifications
    await this.notificationGateway.sendAlert(alert);

    // Log alert
    console.log(`Alert triggered: ${alert.title} (${alert.severity}) for ${context.project}/${context.branch}`);

    return alert;
  }

  formatAlertMessage(rule, evaluation, context) {
    let message = rule.messageTemplate || rule.description;

    // Replace placeholders
    const placeholders = {
      project: context.project,
      branch: context.branch,
      environment: context.environment,
      commit: context.commit,
      current_value: evaluation.currentValue,
      threshold: evaluation.threshold,
      baseline_value: evaluation.baselineValue
    };

    Object.entries(placeholders).forEach(([key, value]) => {
      message = message.replace(new RegExp(`{${key}}`, 'g'), value);
    });

    return message;
  }

  async resolveAlertIfExists(ruleId, context) {
    // Find and resolve existing alerts for this rule and context
    for (const [alertId, alert] of this.activeAlerts) {
      if (alert.ruleId === ruleId &&
          alert.context.project === context.project &&
          alert.context.branch === context.branch &&
          alert.context.environment === context.environment &&
          alert.status === 'active') {

        alert.status = 'resolved';
        alert.resolvedAt = new Date().toISOString();

        await this.notificationGateway.sendAlertResolution(alert);

        console.log(`Alert resolved: ${alert.title} for ${context.project}/${context.branch}`);
      }
    }
  }
}

class AlertRule {
  constructor(config) {
    this.id = config.id;
    this.title = config.title;
    this.description = config.description;
    this.severity = config.severity;
    this.metricPath = config.metricPath;
    this.condition = config.condition;
    this.threshold = config.threshold;
    this.comparisonType = config.comparisonType || 'absolute';
    this.filters = config.filters || {};
    this.cooldownMs = config.cooldownMs || 300000; // 5 minutes default
    this.messageTemplate = config.messageTemplate;
  }

  async evaluate(metrics, context) {
    const currentValue = this.extractMetricValue(metrics, this.metricPath);

    if (currentValue === null || currentValue === undefined) {
      return { triggered: false, reason: 'metric_not_available' };
    }

    let thresholdValue = this.threshold;
    let baselineValue = null;

    // For baseline comparison, get baseline value
    if (this.comparisonType === 'baseline') {
      baselineValue = await this.getBaselineValue(context);
      if (baselineValue === null) {
        return { triggered: false, reason: 'baseline_not_available' };
      }

      // Calculate percentage change
      const percentageChange = ((currentValue - baselineValue) / baselineValue) * 100;
      thresholdValue = this.threshold; // Threshold as percentage change
      currentValue = percentageChange;
    }

    // Evaluate condition
    const triggered = this.evaluateCondition(currentValue, thresholdValue);

    return {
      triggered,
      currentValue: this.extractMetricValue(metrics, this.metricPath),
      threshold: this.threshold,
      baselineValue,
      condition: this.condition,
      comparisonType: this.comparisonType
    };
  }

  evaluateCondition(value, threshold) {
    switch (this.condition) {
      case 'greater_than':
        return value > threshold;
      case 'less_than':
        return value < threshold;
      case 'greater_than_or_equal':
        return value >= threshold;
      case 'less_than_or_equal':
        return value <= threshold;
      case 'equals':
        return value === threshold;
      case 'not_equals':
        return value !== threshold;
      default:
        console.warn(`Unknown condition: ${this.condition}`);
        return false;
    }
  }

  extractMetricValue(metrics, path) {
    return path.split('.').reduce((obj, key) => obj?.[key], metrics);
  }

  async getBaselineValue(context) {
    // This would integrate with the baseline retrieval system
    // For now, return null to indicate baseline not available
    return null;
  }
}
```

## 3. Notification Gateway

### Multi-channel Notification System
```javascript
// notification-gateway.js
class NotificationGateway {
  constructor(config) {
    this.config = config;
    this.channels = new Map();
    this.initializeChannels();
  }

  initializeChannels() {
    // Initialize configured notification channels
    if (this.config.slack?.enabled) {
      this.channels.set('slack', new SlackNotificationChannel(this.config.slack));
    }

    if (this.config.email?.enabled) {
      this.channels.set('email', new EmailNotificationChannel(this.config.email));
    }

    if (this.config.webhook?.enabled) {
      this.channels.set('webhook', new WebhookNotificationChannel(this.config.webhook));
    }

    if (this.config.teams?.enabled) {
      this.channels.set('teams', new TeamsNotificationChannel(this.config.teams));
    }

    console.log(`Initialized ${this.channels.size} notification channels`);
  }

  async sendAlert(alert) {
    const notifications = [];

    for (const [channelName, channel] of this.channels) {
      if (this.shouldSendToChannel(alert, channelName)) {
        try {
          const result = await channel.sendAlert(alert);
          notifications.push({ channel: channelName, success: true, result });
        } catch (error) {
          console.error(`Failed to send alert to ${channelName}:`, error);
          notifications.push({ channel: channelName, success: false, error: error.message });
        }
      }
    }

    return notifications;
  }

  shouldSendToChannel(alert, channelName) {
    const channelConfig = this.config[channelName];

    // Check severity filter
    if (channelConfig.severityFilter &&
        !channelConfig.severityFilter.includes(alert.severity)) {
      return false;
    }

    // Check environment filter
    if (channelConfig.environmentFilter &&
        !channelConfig.environmentFilter.includes(alert.context.environment)) {
      return false;
    }

    // Check project filter
    if (channelConfig.projectFilter &&
        !channelConfig.projectFilter.includes(alert.context.project)) {
      return false;
    }

    return true;
  }

  async sendAlertResolution(alert) {
    const notifications = [];

    for (const [channelName, channel] of this.channels) {
      if (this.shouldSendToChannel(alert, channelName) && channel.sendResolution) {
        try {
          const result = await channel.sendResolution(alert);
          notifications.push({ channel: channelName, success: true, result });
        } catch (error) {
          console.error(`Failed to send resolution to ${channelName}:`, error);
          notifications.push({ channel: channelName, success: false, error: error.message });
        }
      }
    }

    return notifications;
  }
}

class SlackNotificationChannel {
  constructor(config) {
    this.config = config;
    this.webhook = new IncomingWebhook(config.webhookUrl);
  }

  async sendAlert(alert) {
    const color = this.getSeverityColor(alert.severity);
    const emoji = this.getSeverityEmoji(alert.severity);

    const attachment = {
      color,
      title: `${emoji} ${alert.title}`,
      text: alert.message,
      fields: [
        {
          title: 'Project',
          value: alert.context.project,
          short: true
        },
        {
          title: 'Branch',
          value: alert.context.branch,
          short: true
        },
        {
          title: 'Environment',
          value: alert.context.environment,
          short: true
        },
        {
          title: 'Severity',
          value: alert.severity.toUpperCase(),
          short: true
        }
      ],
      timestamp: Math.floor(new Date(alert.triggeredAt).getTime() / 1000),
      footer: 'Test Baseline Tracking System',
      footer_icon: 'https://example.com/tbts-icon.png'
    };

    if (alert.evaluation) {
      attachment.fields.push({
        title: 'Current Value',
        value: alert.evaluation.currentValue?.toString() || 'N/A',
        short: true
      });

      attachment.fields.push({
        title: 'Threshold',
        value: alert.evaluation.threshold?.toString() || 'N/A',
        short: true
      });
    }

    const result = await this.webhook.send({
      username: 'TBTS Bot',
      icon_emoji: ':warning:',
      attachments: [attachment]
    });

    return result;
  }

  async sendResolution(alert) {
    const attachment = {
      color: 'good',
      title: `✅ Resolved: ${alert.title}`,
      text: `Alert has been resolved for ${alert.context.project}/${alert.context.branch}`,
      fields: [
        {
          title: 'Duration',
          value: this.calculateDuration(alert.triggeredAt, alert.resolvedAt),
          short: true
        }
      ],
      timestamp: Math.floor(new Date(alert.resolvedAt).getTime() / 1000)
    };

    return await this.webhook.send({
      username: 'TBTS Bot',
      icon_emoji: ':white_check_mark:',
      attachments: [attachment]
    });
  }

  getSeverityColor(severity) {
    const colors = {
      critical: 'danger',
      major: 'warning',
      minor: 'warning',
      info: 'good'
    };
    return colors[severity] || 'warning';
  }

  getSeverityEmoji(severity) {
    const emojis = {
      critical: '🚨',
      major: '⚠️',
      minor: '⚡',
      info: 'ℹ️'
    };
    return emojis[severity] || '📊';
  }

  calculateDuration(startTime, endTime) {
    const duration = new Date(endTime) - new Date(startTime);
    const minutes = Math.floor(duration / 60000);
    const seconds = Math.floor((duration % 60000) / 1000);
    return `${minutes}m ${seconds}s`;
  }
}

class EmailNotificationChannel {
  constructor(config) {
    this.config = config;
    this.transporter = nodemailer.createTransporter(config.smtp);
  }

  async sendAlert(alert) {
    const html = this.generateAlertHTML(alert);
    const text = this.generateAlertText(alert);

    const mailOptions = {
      from: this.config.from,
      to: this.getRecipients(alert),
      subject: `[TBTS] ${alert.severity.toUpperCase()}: ${alert.title}`,
      text,
      html
    };

    return await this.transporter.sendMail(mailOptions);
  }

  generateAlertHTML(alert) {
    return `
      <!DOCTYPE html>
      <html>
      <head>
        <style>
          body { font-family: Arial, sans-serif; line-height: 1.6; }
          .alert-header { background: ${this.getSeverityColor(alert.severity)}; color: white; padding: 15px; }
          .alert-content { padding: 20px; }
          .metrics-table { border-collapse: collapse; width: 100%; margin-top: 15px; }
          .metrics-table th, .metrics-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
          .metrics-table th { background-color: #f2f2f2; }
        </style>
      </head>
      <body>
        <div class="alert-header">
          <h2>${alert.title}</h2>
          <p>Severity: ${alert.severity.toUpperCase()}</p>
        </div>
        <div class="alert-content">
          <p><strong>Message:</strong> ${alert.message}</p>

          <h3>Context Information</h3>
          <table class="metrics-table">
            <tr><th>Property</th><th>Value</th></tr>
            <tr><td>Project</td><td>${alert.context.project}</td></tr>
            <tr><td>Branch</td><td>${alert.context.branch}</td></tr>
            <tr><td>Environment</td><td>${alert.context.environment}</td></tr>
            <tr><td>Commit</td><td>${alert.context.commit || 'N/A'}</td></tr>
            <tr><td>Triggered At</td><td>${new Date(alert.triggeredAt).toLocaleString()}</td></tr>
          </table>

          ${alert.evaluation ? this.generateEvaluationHTML(alert.evaluation) : ''}
        </div>
      </body>
      </html>
    `;
  }

  generateEvaluationHTML(evaluation) {
    return `
      <h3>Evaluation Details</h3>
      <table class="metrics-table">
        <tr><th>Metric</th><th>Value</th></tr>
        <tr><td>Current Value</td><td>${evaluation.currentValue}</td></tr>
        <tr><td>Threshold</td><td>${evaluation.threshold}</td></tr>
        <tr><td>Condition</td><td>${evaluation.condition}</td></tr>
        ${evaluation.baselineValue ? `<tr><td>Baseline Value</td><td>${evaluation.baselineValue}</td></tr>` : ''}
      </table>
    `;
  }

  generateAlertText(alert) {
    let text = `ALERT: ${alert.title}\n`;
    text += `Severity: ${alert.severity.toUpperCase()}\n`;
    text += `Message: ${alert.message}\n\n`;
    text += `Context:\n`;
    text += `- Project: ${alert.context.project}\n`;
    text += `- Branch: ${alert.context.branch}\n`;
    text += `- Environment: ${alert.context.environment}\n`;
    text += `- Triggered At: ${new Date(alert.triggeredAt).toLocaleString()}\n`;

    if (alert.evaluation) {
      text += `\nEvaluation:\n`;
      text += `- Current Value: ${alert.evaluation.currentValue}\n`;
      text += `- Threshold: ${alert.evaluation.threshold}\n`;
      text += `- Condition: ${alert.evaluation.condition}\n`;
    }

    return text;
  }

  getRecipients(alert) {
    // Get recipients based on alert context and configuration
    let recipients = [...this.config.defaultRecipients];

    // Add project-specific recipients
    if (this.config.projectRecipients?.[alert.context.project]) {
      recipients.push(...this.config.projectRecipients[alert.context.project]);
    }

    // Add severity-specific recipients
    if (this.config.severityRecipients?.[alert.severity]) {
      recipients.push(...this.config.severityRecipients[alert.severity]);
    }

    return [...new Set(recipients)]; // Remove duplicates
  }

  getSeverityColor(severity) {
    const colors = {
      critical: '#d32f2f',
      major: '#f57c00',
      minor: '#fbc02d',
      info: '#1976d2'
    };
    return colors[severity] || '#757575';
  }
}
```

## 4. Report Generation System

### Automated Report Generator
```javascript
// report-generator.js
class ReportGenerator {
  constructor(config) {
    this.config = config;
    this.templates = new Map();
    this.scheduledReports = new Map();
    this.loadTemplates();
  }

  async loadTemplates() {
    // Load report templates
    const templateConfigs = [
      {
        id: 'daily_summary',
        name: 'Daily Test Summary',
        schedule: '0 9 * * *', // 9 AM daily
        template: 'daily-summary.hbs',
        recipients: ['team-leads@company.com'],
        format: 'html'
      },
      {
        id: 'weekly_trends',
        name: 'Weekly Trends Report',
        schedule: '0 9 * * 1', // Monday 9 AM
        template: 'weekly-trends.hbs',
        recipients: ['management@company.com'],
        format: 'pdf'
      },
      {
        id: 'monthly_quality',
        name: 'Monthly Quality Report',
        schedule: '0 9 1 * *', // First day of month 9 AM
        template: 'monthly-quality.hbs',
        recipients: ['executives@company.com'],
        format: 'pdf'
      }
    ];

    templateConfigs.forEach(config => {
      this.scheduleReport(config);
    });
  }

  scheduleReport(config) {
    const job = cron.schedule(config.schedule, async () => {
      await this.generateAndSendReport(config);
    });

    this.scheduledReports.set(config.id, {
      config,
      job
    });

    console.log(`Scheduled report: ${config.name} (${config.schedule})`);
  }

  async generateAndSendReport(config) {
    try {
      console.log(`Generating report: ${config.name}`);

      // Collect data for the report
      const reportData = await this.collectReportData(config);

      // Generate report content
      const reportContent = await this.renderReport(config.template, reportData);

      // Convert to requested format
      let finalContent;
      if (config.format === 'pdf') {
        finalContent = await this.convertToPDF(reportContent);
      } else {
        finalContent = reportContent;
      }

      // Send report
      await this.sendReport(config, finalContent, reportData);

      console.log(`Report sent: ${config.name}`);

    } catch (error) {
      console.error(`Failed to generate report ${config.name}:`, error);
    }
  }

  async collectReportData(config) {
    const endDate = new Date();
    let startDate;

    // Determine time range based on report type
    switch (config.id) {
      case 'daily_summary':
        startDate = new Date(endDate.getTime() - 24 * 60 * 60 * 1000);
        break;
      case 'weekly_trends':
        startDate = new Date(endDate.getTime() - 7 * 24 * 60 * 60 * 1000);
        break;
      case 'monthly_quality':
        startDate = new Date(endDate.getFullYear(), endDate.getMonth() - 1, 1);
        break;
      default:
        startDate = new Date(endDate.getTime() - 24 * 60 * 60 * 1000);
    }

    // Collect metrics data
    const metrics = await this.collectMetricsData(startDate, endDate);
    const trends = await this.calculateTrends(metrics);
    const alerts = await this.getAlertsInPeriod(startDate, endDate);
    const summary = this.generateSummary(metrics, trends, alerts);

    return {
      period: {
        start: startDate.toISOString(),
        end: endDate.toISOString(),
        duration: this.formatDuration(endDate - startDate)
      },
      metrics,
      trends,
      alerts,
      summary,
      generated_at: new Date().toISOString()
    };
  }

  async renderReport(templateName, data) {
    const template = Handlebars.compile(
      await fs.readFile(`templates/${templateName}`, 'utf8')
    );

    return template(data);
  }

  async convertToPDF(htmlContent) {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();

    await page.setContent(htmlContent);

    const pdf = await page.pdf({
      format: 'A4',
      printBackground: true,
      margin: {
        top: '20mm',
        right: '20mm',
        bottom: '20mm',
        left: '20mm'
      }
    });

    await browser.close();

    return pdf;
  }

  async sendReport(config, content, data) {
    const subject = `${config.name} - ${new Date().toLocaleDateString()}`;

    const emailOptions = {
      from: this.config.email.from,
      to: config.recipients,
      subject,
      html: config.format === 'html' ? content : this.generateEmailHTML(config, data),
      attachments: config.format === 'pdf' ? [{
        filename: `${config.id}_${new Date().toISOString().split('T')[0]}.pdf`,
        content
      }] : []
    };

    await this.config.emailTransporter.sendMail(emailOptions);
  }

  generateEmailHTML(config, data) {
    return `
      <h2>${config.name}</h2>
      <p>Report generated for period: ${new Date(data.period.start).toLocaleDateString()} - ${new Date(data.period.end).toLocaleDateString()}</p>

      <h3>Summary</h3>
      <ul>
        <li>Total Tests Executed: ${data.summary.total_tests}</li>
        <li>Average Pass Rate: ${data.summary.avg_pass_rate.toFixed(2)}%</li>
        <li>Alert Count: ${data.summary.alert_count}</li>
      </ul>

      <p>Please find the detailed report attached.</p>

      <p><em>Generated by Test Baseline Tracking System at ${new Date(data.generated_at).toLocaleString()}</em></p>
    `;
  }
}
```

This comprehensive reporting and notification system provides real-time monitoring, intelligent alerting, multi-channel notifications, and automated report generation to keep teams informed about test quality trends and issues.