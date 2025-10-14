import {
  ApprovalRequest,
  User,
  NotificationConfig,
  NotificationChannel,
  NotificationType,
  NotificationTrigger,
  NotificationFrequency,
  ApprovalStep,
  ApprovalResponse,
  EscalationRule
} from '../types/approval.types.js';
import { EventEmitter } from 'events';

export interface NotificationSystemOptions {
  enableEmail: boolean;
  enableSMS: boolean;
  enableSlack: boolean;
  enableWebhook: boolean;
  enableInApp: boolean;
  defaultChannel: NotificationChannel;
  retryAttempts: number;
  retryDelay: number; // milliseconds
  batchSize: number;
  enableQuietHours: boolean;
  enableTemplating: boolean;
}

export interface EmailConfig {
  host: string;
  port: number;
  secure: boolean;
  auth: {
    user: string;
    pass: string;
  };
  from: string;
  replyTo?: string;
}

export interface SMSConfig {
  provider: 'twilio' | 'aws-sns' | 'nexmo';
  apiKey: string;
  apiSecret: string;
  from: string;
}

export interface SlackConfig {
  botToken: string;
  workspaceUrl: string;
  defaultChannel: string;
  enableThreads: boolean;
}

export interface WebhookConfig {
  url: string;
  secret?: string;
  headers?: Record<string, string>;
  retryAttempts: number;
  timeout: number; // milliseconds
}

export interface NotificationTemplate {
  id: string;
  name: string;
  trigger: NotificationTrigger;
  channel: NotificationChannel;
  subject: string;
  body: string;
  variables: string[];
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface NotificationMessage {
  id: string;
  requestId: string;
  userId: string;
  channel: NotificationChannel;
  type: NotificationType;
  trigger: NotificationTrigger;
  subject: string;
  body: string;
  metadata: Record<string, any>;
  sentAt?: Date;
  deliveredAt?: Date;
  readAt?: Date;
  status: NotificationStatus;
  retryCount: number;
  error?: string;
}

export interface NotificationBatch {
  id: string;
  trigger: NotificationTrigger;
  recipients: User[];
  messages: NotificationMessage[];
  createdAt: Date;
  processedAt?: Date;
  status: BatchStatus;
}

export interface NotificationMetrics {
  totalSent: number;
  totalDelivered: number;
  totalRead: number;
  totalFailed: number;
  deliveryRate: number;
  readRate: number;
  averageDeliveryTime: number;
  channelMetrics: Record<NotificationChannel, ChannelMetrics>;
  triggerMetrics: Record<NotificationTrigger, TriggerMetrics>;
}

export interface ChannelMetrics {
  sent: number;
  delivered: number;
  failed: number;
  averageDeliveryTime: number;
  deliveryRate: number;
}

export interface TriggerMetrics {
  sent: number;
  averageResponseTime: number;
  escalationRate: number;
}

export enum NotificationStatus {
  PENDING = 'pending',
  SENDING = 'sending',
  SENT = 'sent',
  DELIVERED = 'delivered',
  READ = 'read',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

export enum BatchStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed'
}

export class NotificationSystem extends EventEmitter {
  private options: NotificationSystemOptions;
  private emailConfig?: EmailConfig;
  private smsConfig?: SMSConfig;
  private slackConfig?: SlackConfig;
  private webhookConfig?: WebhookConfig;
  private templates: Map<string, NotificationTemplate> = new Map();
  private messages: Map<string, NotificationMessage> = new Map();
  private batches: Map<string, NotificationBatch> = new Map();
  private retryQueues: Map<NotificationChannel, NotificationMessage[]> = new Map();

  constructor(options: Partial<NotificationSystemOptions> = {}) {
    super();
    this.options = {
      enableEmail: true,
      enableSMS: false,
      enableSlack: false,
      enableWebhook: false,
      enableInApp: true,
      defaultChannel: NotificationChannel.EMAIL,
      retryAttempts: 3,
      retryDelay: 5000,
      batchSize: 50,
      enableQuietHours: true,
      enableTemplating: true,
      ...options
    };

    this.initializeRetryQueues();
    this.setupDefaultTemplates();
  }

  /**
   * Configure email settings
   */
  configureEmail(config: EmailConfig): void {
    this.emailConfig = config;
    this.options.enableEmail = true;
  }

  /**
   * Configure SMS settings
   */
  configureSMS(config: SMSConfig): void {
    this.smsConfig = config;
    this.options.enableSMS = true;
  }

  /**
   * Configure Slack settings
   */
  configureSlack(config: SlackConfig): void {
    this.slackConfig = config;
    this.options.enableSlack = true;
  }

  /**
   * Configure webhook settings
   */
  configureWebhook(config: WebhookConfig): void {
    this.webhookConfig = config;
    this.options.enableWebhook = true;
  }

  /**
   * Send approval request notification
   */
  async sendApprovalRequest(
    approvalRequest: ApprovalRequest,
    recipients: User[],
    channel?: NotificationChannel
  ): Promise<void> {
    const targetChannel = channel || this.options.defaultChannel;

    const batch = await this.createNotificationBatch(
      NotificationTrigger.APPROVAL_REQUIRED,
      recipients,
      approvalRequest
    );

    for (const recipient of recipients) {
      // Check quiet hours
      if (this.options.enableQuietHours && this.isQuietHours(recipient)) {
        continue;
      }

      // Get user's preferred channels
      const userChannels = this.getUserPreferredChannels(recipient, NotificationTrigger.APPROVAL_REQUIRED);

      for (const userChannel of userChannels) {
        if (this.isChannelEnabled(userChannel)) {
          await this.sendSingleNotification(
            approvalRequest,
            recipient,
            userChannel,
            NotificationTrigger.APPROVAL_REQUIRED,
            batch.id
          );
        }
      }
    }

    this.emit('approvalRequestSent', { batch, approvalRequest, recipients });
  }

  /**
   * Send approval decision notification
   */
  async sendApprovalDecision(
    approvalRequest: ApprovalRequest,
    response: ApprovalResponse,
    recipients: User[]
  ): Promise<void> {
    const batch = await this.createNotificationBatch(
      NotificationTrigger.DECISION_MADE,
      recipients,
      { approvalRequest, response }
    );

    for (const recipient of recipients) {
      const userChannels = this.getUserPreferredChannels(recipient, NotificationTrigger.DECISION_MADE);

      for (const userChannel of userChannels) {
        if (this.isChannelEnabled(userChannel)) {
          await this.sendSingleNotification(
            { approvalRequest, response },
            recipient,
            userChannel,
            NotificationTrigger.DECISION_MADE,
            batch.id
          );
        }
      }
    }

    this.emit('approvalDecisionSent', { batch, approvalRequest, response, recipients });
  }

  /**
   * Send escalation notification
   */
  async sendEscalationNotification(
    approvalRequest: ApprovalRequest,
    step: ApprovalStep,
    escalation: EscalationRule,
    recipients: User[]
  ): Promise<void> {
    const batch = await this.createNotificationBatch(
      NotificationTrigger.ESCALATED,
      recipients,
      { approvalRequest, step, escalation }
    );

    for (const recipient of recipients) {
      // Escalations are high priority - use all available channels
      const channels = [NotificationChannel.EMAIL, NotificationChannel.SMS, NotificationChannel.SLACK]
        .filter(ch => this.isChannelEnabled(ch));

      for (const channel of channels) {
        await this.sendSingleNotification(
          { approvalRequest, step, escalation },
          recipient,
          channel,
          NotificationTrigger.ESCALATED,
          batch.id,
          true // high priority
        );
      }
    }

    this.emit('escalationNotificationSent', { batch, approvalRequest, step, escalation, recipients });
  }

  /**
   * Send reminder notification
   */
  async sendReminder(
    approvalRequest: ApprovalRequest,
    recipients: User[],
    reminderText?: string
  ): Promise<void> {
    const batch = await this.createNotificationBatch(
      NotificationTrigger.REMINDER,
      recipients,
      { approvalRequest, reminderText }
    );

    for (const recipient of recipients) {
      const userChannels = this.getUserPreferredChannels(recipient, NotificationTrigger.REMINDER);

      for (const userChannel of userChannels) {
        if (this.isChannelEnabled(userChannel)) {
          await this.sendSingleNotification(
            { approvalRequest, reminderText },
            recipient,
            userChannel,
            NotificationTrigger.REMINDER,
            batch.id
          );
        }
      }
    }

    this.emit('reminderSent', { batch, approvalRequest, recipients });
  }

  /**
   * Send request completion notification
   */
  async sendCompletionNotification(
    approvalRequest: ApprovalRequest,
    recipients: User[]
  ): Promise<void> {
    const batch = await this.createNotificationBatch(
      NotificationTrigger.COMPLETED,
      recipients,
      approvalRequest
    );

    for (const recipient of recipients) {
      const userChannels = this.getUserPreferredChannels(recipient, NotificationTrigger.COMPLETED);

      for (const userChannel of userChannels) {
        if (this.isChannelEnabled(userChannel)) {
          await this.sendSingleNotification(
            approvalRequest,
            recipient,
            userChannel,
            NotificationTrigger.COMPLETED,
            batch.id
          );
        }
      }
    }

    this.emit('completionNotificationSent', { batch, approvalRequest, recipients });
  }

  /**
   * Create or update notification template
   */
  async createTemplate(template: Omit<NotificationTemplate, 'id' | 'createdAt' | 'updatedAt'>): Promise<NotificationTemplate> {
    const notificationTemplate: NotificationTemplate = {
      ...template,
      id: this.generateId(),
      createdAt: new Date(),
      updatedAt: new Date()
    };

    this.templates.set(notificationTemplate.id, notificationTemplate);
    this.emit('templateCreated', notificationTemplate);

    return notificationTemplate;
  }

  /**
   * Update notification template
   */
  async updateTemplate(templateId: string, updates: Partial<NotificationTemplate>): Promise<NotificationTemplate> {
    const template = this.templates.get(templateId);
    if (!template) {
      throw new Error(`Template ${templateId} not found`);
    }

    const updatedTemplate = {
      ...template,
      ...updates,
      updatedAt: new Date()
    };

    this.templates.set(templateId, updatedTemplate);
    this.emit('templateUpdated', updatedTemplate);

    return updatedTemplate;
  }

  /**
   * Get notification templates
   */
  getTemplates(trigger?: NotificationTrigger, channel?: NotificationChannel): NotificationTemplate[] {
    let templates = Array.from(this.templates.values());

    if (trigger) {
      templates = templates.filter(t => t.trigger === trigger);
    }

    if (channel) {
      templates = templates.filter(t => t.channel === channel);
    }

    return templates;
  }

  /**
   * Mark notification as read
   */
  async markAsRead(messageId: string, userId: string): Promise<void> {
    const message = this.messages.get(messageId);
    if (!message) {
      throw new Error(`Message ${messageId} not found`);
    }

    if (message.userId !== userId) {
      throw new Error('Unauthorized to mark this message as read');
    }

    message.readAt = new Date();
    message.status = NotificationStatus.READ;

    this.emit('messageRead', message);
  }

  /**
   * Get user notifications
   */
  getUserNotifications(userId: string, limit: number = 50): NotificationMessage[] {
    return Array.from(this.messages.values())
      .filter(m => m.userId === userId)
      .sort((a, b) => (b.sentAt?.getTime() || 0) - (a.sentAt?.getTime() || 0))
      .slice(0, limit);
  }

  /**
   * Get unread notifications count
   */
  getUnreadCount(userId: string): number {
    return Array.from(this.messages.values())
      .filter(m => m.userId === userId && !m.readAt).length;
  }

  /**
   * Get notification metrics
   */
  getMetrics(startDate?: Date, endDate?: Date): NotificationMetrics {
    let messages = Array.from(this.messages.values());

    if (startDate) {
      messages = messages.filter(m => m.sentAt && m.sentAt >= startDate);
    }

    if (endDate) {
      messages = messages.filter(m => m.sentAt && m.sentAt <= endDate);
    }

    const totalSent = messages.filter(m => m.status !== NotificationStatus.PENDING).length;
    const totalDelivered = messages.filter(m => m.status === NotificationStatus.DELIVERED || m.status === NotificationStatus.READ).length;
    const totalRead = messages.filter(m => m.status === NotificationStatus.READ).length;
    const totalFailed = messages.filter(m => m.status === NotificationStatus.FAILED).length;

    const deliveryRate = totalSent > 0 ? totalDelivered / totalSent : 0;
    const readRate = totalDelivered > 0 ? totalRead / totalDelivered : 0;

    // Calculate average delivery time
    const deliveredMessages = messages.filter(m => m.deliveredAt && m.sentAt);
    const averageDeliveryTime = deliveredMessages.length > 0
      ? deliveredMessages.reduce((sum, m) => sum + (m.deliveredAt!.getTime() - m.sentAt!.getTime()), 0) / deliveredMessages.length
      : 0;

    // Calculate channel metrics
    const channelMetrics: Record<NotificationChannel, ChannelMetrics> = {} as any;
    for (const channel of Object.values(NotificationChannel)) {
      const channelMessages = messages.filter(m => m.channel === channel);
      const channelSent = channelMessages.filter(m => m.status !== NotificationStatus.PENDING).length;
      const channelDelivered = channelMessages.filter(m => m.status === NotificationStatus.DELIVERED || m.status === NotificationStatus.READ).length;
      const channelFailed = channelMessages.filter(m => m.status === NotificationStatus.FAILED).length;

      const channelDeliveredWithTimes = channelMessages.filter(m => m.deliveredAt && m.sentAt);
      const channelAverageDeliveryTime = channelDeliveredWithTimes.length > 0
        ? channelDeliveredWithTimes.reduce((sum, m) => sum + (m.deliveredAt!.getTime() - m.sentAt!.getTime()), 0) / channelDeliveredWithTimes.length
        : 0;

      channelMetrics[channel] = {
        sent: channelSent,
        delivered: channelDelivered,
        failed: channelFailed,
        averageDeliveryTime: channelAverageDeliveryTime,
        deliveryRate: channelSent > 0 ? channelDelivered / channelSent : 0
      };
    }

    // Calculate trigger metrics
    const triggerMetrics: Record<NotificationTrigger, TriggerMetrics> = {} as any;
    for (const trigger of Object.values(NotificationTrigger)) {
      const triggerMessages = messages.filter(m => m.trigger === trigger);
      triggerMetrics[trigger] = {
        sent: triggerMessages.length,
        averageResponseTime: 0, // This would be calculated based on actual response times
        escalationRate: 0 // This would be calculated based on escalation data
      };
    }

    return {
      totalSent,
      totalDelivered,
      totalRead,
      totalFailed,
      deliveryRate,
      readRate,
      averageDeliveryTime,
      channelMetrics,
      triggerMetrics
    };
  }

  /**
   * Retry failed notifications
   */
  async retryFailedNotifications(): Promise<void> {
    for (const [channel, queue] of this.retryQueues) {
      const messages = queue.splice(0, this.options.batchSize);

      for (const message of messages) {
        if (message.retryCount < this.options.retryAttempts) {
          message.retryCount++;
          message.status = NotificationStatus.PENDING;
          await this.deliverMessage(message);
        }
      }
    }
  }

  // Private methods

  private async createNotificationBatch(
    trigger: NotificationTrigger,
    recipients: User[],
    data: any
  ): Promise<NotificationBatch> {
    const batch: NotificationBatch = {
      id: this.generateId(),
      trigger,
      recipients,
      messages: [],
      createdAt: new Date(),
      status: BatchStatus.PENDING
    };

    this.batches.set(batch.id, batch);
    return batch;
  }

  private async sendSingleNotification(
    data: any,
    recipient: User,
    channel: NotificationChannel,
    trigger: NotificationTrigger,
    batchId: string,
    highPriority: boolean = false
  ): Promise<void> {
    const template = this.getTemplate(trigger, channel);
    const { subject, body } = this.renderTemplate(template, data, recipient);

    const message: NotificationMessage = {
      id: this.generateId(),
      requestId: data.approvalRequest?.id || data.id,
      userId: recipient.id,
      channel,
      type: this.mapTriggerToType(trigger),
      trigger,
      subject,
      body,
      metadata: {
        batchId,
        highPriority,
        data
      },
      status: NotificationStatus.PENDING,
      retryCount: 0
    };

    this.messages.set(message.id, message);

    // Add to batch
    const batch = this.batches.get(batchId);
    if (batch) {
      batch.messages.push(message);
    }

    // Deliver immediately or queue
    if (highPriority) {
      await this.deliverMessage(message);
    } else {
      // Queue for batch processing
      setTimeout(() => this.deliverMessage(message), 0);
    }
  }

  private async deliverMessage(message: NotificationMessage): Promise<void> {
    try {
      message.status = NotificationStatus.SENDING;
      message.sentAt = new Date();

      switch (message.channel) {
        case NotificationChannel.EMAIL:
          await this.sendEmail(message);
          break;
        case NotificationChannel.SMS:
          await this.sendSMS(message);
          break;
        case NotificationChannel.SLACK:
          await this.sendSlack(message);
          break;
        case NotificationChannel.WEBHOOK:
          await this.sendWebhook(message);
          break;
        case NotificationChannel.IN_APP:
          await this.sendInApp(message);
          break;
        default:
          throw new Error(`Unsupported channel: ${message.channel}`);
      }

      message.status = NotificationStatus.DELIVERED;
      message.deliveredAt = new Date();
      this.emit('messageDelivered', message);

    } catch (error) {
      message.status = NotificationStatus.FAILED;
      message.error = (error as Error).message;

      // Add to retry queue if retries available
      if (message.retryCount < this.options.retryAttempts) {
        const queue = this.retryQueues.get(message.channel) || [];
        queue.push(message);
        this.retryQueues.set(message.channel, queue);
      }

      this.emit('messageFailed', { message, error });
    }
  }

  private async sendEmail(message: NotificationMessage): Promise<void> {
    if (!this.emailConfig) {
      throw new Error('Email not configured');
    }

    // Implementation would use nodemailer or similar
    // This is a placeholder
    await new Promise(resolve => setTimeout(resolve, 100));
  }

  private async sendSMS(message: NotificationMessage): Promise<void> {
    if (!this.smsConfig) {
      throw new Error('SMS not configured');
    }

    // Implementation would use Twilio, AWS SNS, or similar
    // This is a placeholder
    await new Promise(resolve => setTimeout(resolve, 100));
  }

  private async sendSlack(message: NotificationMessage): Promise<void> {
    if (!this.slackConfig) {
      throw new Error('Slack not configured');
    }

    // Implementation would use Slack Web API
    // This is a placeholder
    await new Promise(resolve => setTimeout(resolve, 100));
  }

  private async sendWebhook(message: NotificationMessage): Promise<void> {
    if (!this.webhookConfig) {
      throw new Error('Webhook not configured');
    }

    // Implementation would make HTTP POST request
    // This is a placeholder
    await new Promise(resolve => setTimeout(resolve, 100));
  }

  private async sendInApp(message: NotificationMessage): Promise<void> {
    // In-app notifications are just stored in memory/database
    // No external delivery required
    message.status = NotificationStatus.DELIVERED;
    message.deliveredAt = new Date();
  }

  private getTemplate(trigger: NotificationTrigger, channel: NotificationChannel): NotificationTemplate {
    const template = Array.from(this.templates.values())
      .find(t => t.trigger === trigger && t.channel === channel && t.isActive);

    if (!template) {
      // Return default template
      return this.getDefaultTemplate(trigger, channel);
    }

    return template;
  }

  private getDefaultTemplate(trigger: NotificationTrigger, channel: NotificationChannel): NotificationTemplate {
    // Return built-in default templates
    return {
      id: 'default',
      name: 'Default Template',
      trigger,
      channel,
      subject: this.getDefaultSubject(trigger),
      body: this.getDefaultBody(trigger),
      variables: ['user.name', 'request.title', 'request.url'],
      isActive: true,
      createdAt: new Date(),
      updatedAt: new Date()
    };
  }

  private getDefaultSubject(trigger: NotificationTrigger): string {
    switch (trigger) {
      case NotificationTrigger.APPROVAL_REQUIRED:
        return 'Approval Required: {{request.title}}';
      case NotificationTrigger.DECISION_MADE:
        return 'Approval Decision: {{request.title}}';
      case NotificationTrigger.ESCALATED:
        return 'URGENT: Approval Escalated - {{request.title}}';
      case NotificationTrigger.REMINDER:
        return 'Reminder: Approval Pending - {{request.title}}';
      case NotificationTrigger.COMPLETED:
        return 'Approval Completed: {{request.title}}';
      default:
        return 'Notification';
    }
  }

  private getDefaultBody(trigger: NotificationTrigger): string {
    switch (trigger) {
      case NotificationTrigger.APPROVAL_REQUIRED:
        return `
Hello {{user.name}},

You have a new approval request that requires your attention:

**Request:** {{request.title}}
**Priority:** {{request.priority}}
**Requested by:** {{request.requester.name}}

Please review and approve or reject this request.

[View Request]({{request.url}})

Best regards,
Approval System
        `;
      case NotificationTrigger.DECISION_MADE:
        return `
Hello {{user.name}},

An approval decision has been made on: {{request.title}}

**Decision:** {{response.decision}}
**By:** {{response.approver.name}}
**Reason:** {{response.reason}}

[View Request]({{request.url}})

Best regards,
Approval System
        `;
      case NotificationTrigger.ESCALATED:
        return `
URGENT: An approval request has been escalated and requires immediate attention.

**Request:** {{request.title}}
**Escalated from:** {{step.name}}
**Reason:** {{escalation.reason}}

Please review this request immediately.

[View Request]({{request.url}})

Best regards,
Approval System
        `;
      default:
        return 'You have a new notification.';
    }
  }

  private renderTemplate(template: NotificationTemplate, data: any, user: User): { subject: string; body: string } {
    const context = {
      user,
      request: data.approvalRequest || data,
      response: data.response,
      step: data.step,
      escalation: data.escalation,
      reminderText: data.reminderText
    };

    const subject = this.replaceVariables(template.subject, context);
    const body = this.replaceVariables(template.body, context);

    return { subject, body };
  }

  private replaceVariables(template: string, context: any): string {
    return template.replace(/\{\{([^}]+)\}\}/g, (match, path) => {
      const value = this.getNestedValue(context, path.trim());
      return value !== undefined ? String(value) : match;
    });
  }

  private getNestedValue(obj: any, path: string): any {
    return path.split('.').reduce((current, key) => current?.[key], obj);
  }

  private getUserPreferredChannels(user: User, trigger: NotificationTrigger): NotificationChannel[] {
    // Get user's notification preferences for this trigger
    const preferences = user.notificationPreferences.filter(p => p.triggers.includes(trigger) && p.enabled);

    if (preferences.length > 0) {
      return preferences.map(p => p.channel);
    }

    // Return default channel if no preferences
    return [this.options.defaultChannel];
  }

  private isChannelEnabled(channel: NotificationChannel): boolean {
    switch (channel) {
      case NotificationChannel.EMAIL:
        return this.options.enableEmail && !!this.emailConfig;
      case NotificationChannel.SMS:
        return this.options.enableSMS && !!this.smsConfig;
      case NotificationChannel.SLACK:
        return this.options.enableSlack && !!this.slackConfig;
      case NotificationChannel.WEBHOOK:
        return this.options.enableWebhook && !!this.webhookConfig;
      case NotificationChannel.IN_APP:
        return this.options.enableInApp;
      default:
        return false;
    }
  }

  private isQuietHours(user: User): boolean {
    if (!this.options.enableQuietHours) {
      return false;
    }

    // Check if current time is within user's quiet hours
    const now = new Date();
    const currentTime = now.toTimeString().slice(0, 5); // HH:MM format

    for (const pref of user.notificationPreferences) {
      if (pref.quietHours) {
        const { start, end } = pref.quietHours;
        if (this.isTimeInRange(currentTime, start, end)) {
          return true;
        }
      }
    }

    return false;
  }

  private isTimeInRange(time: string, start: string, end: string): boolean {
    if (start <= end) {
      return time >= start && time <= end;
    } else {
      // Overnight range (e.g., 22:00 - 06:00)
      return time >= start || time <= end;
    }
  }

  private mapTriggerToType(trigger: NotificationTrigger): NotificationType {
    switch (trigger) {
      case NotificationTrigger.ESCALATED:
        return NotificationType.SMS; // High priority
      default:
        return NotificationType.EMAIL;
    }
  }

  private initializeRetryQueues(): void {
    for (const channel of Object.values(NotificationChannel)) {
      this.retryQueues.set(channel, []);
    }
  }

  private setupDefaultTemplates(): void {
    if (!this.options.enableTemplating) {
      return;
    }

    const defaultTemplates = [
      {
        name: 'Approval Required Email',
        trigger: NotificationTrigger.APPROVAL_REQUIRED,
        channel: NotificationChannel.EMAIL,
        subject: 'Approval Required: {{request.title}}',
        body: this.getDefaultBody(NotificationTrigger.APPROVAL_REQUIRED),
        variables: ['user.name', 'request.title', 'request.priority', 'request.requester.name', 'request.url'],
        isActive: true
      },
      // Add more default templates...
    ];

    for (const template of defaultTemplates) {
      this.createTemplate(template);
    }
  }

  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
}