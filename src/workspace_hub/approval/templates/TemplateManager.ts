import {
  ApprovalTemplate,
  ApprovalStepTemplate,
  ApprovalSettings,
  ApprovalCondition,
  TemplateCategory,
  User,
  UserRole,
  ApprovalRequest,
  ApprovalStep,
  ApprovalType,
  ApprovalPriority,
  Environment,
  RiskLevel
} from '../types/approval.types.js';
import { EventEmitter } from 'events';

export interface TemplateManagerOptions {
  enableVersioning: boolean;
  enableValidation: boolean;
  maxTemplateVersions: number;
  enableCache: boolean;
  cacheTimeout: number; // milliseconds
  enableInheritance: boolean;
  enableCustomFields: boolean;
}

export interface TemplateVersion {
  id: string;
  templateId: string;
  version: string;
  template: ApprovalTemplate;
  createdBy: User;
  createdAt: Date;
  isActive: boolean;
  changeLog: string[];
}

export interface TemplateUsage {
  templateId: string;
  usageCount: number;
  lastUsed: Date;
  averageProcessingTime: number;
  successRate: number;
  userFeedback: TemplateFeedback[];
}

export interface TemplateFeedback {
  id: string;
  templateId: string;
  userId: string;
  rating: number; // 1-5
  comment: string;
  usageContext: string;
  createdAt: Date;
}

export interface TemplateInheritance {
  templateId: string;
  parentTemplateId: string;
  inheritedFields: string[];
  overriddenFields: string[];
  createdAt: Date;
}

export interface CustomField {
  id: string;
  name: string;
  type: FieldType;
  required: boolean;
  defaultValue?: any;
  options?: string[];
  validation?: FieldValidation;
  description: string;
}

export interface FieldValidation {
  pattern?: string;
  minLength?: number;
  maxLength?: number;
  min?: number;
  max?: number;
  custom?: string; // Custom validation function name
}

export interface TemplateFilter {
  category?: TemplateCategory;
  isActive?: boolean;
  createdBy?: string;
  tags?: string[];
  environment?: Environment;
  riskLevel?: RiskLevel;
  searchTerm?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  limit?: number;
  offset?: number;
}

export interface TemplateCloneOptions {
  newName: string;
  newDescription?: string;
  category?: TemplateCategory;
  modifySteps?: boolean;
  removeSteps?: number[];
  addSteps?: ApprovalStepTemplate[];
  updateSettings?: Partial<ApprovalSettings>;
}

export enum FieldType {
  TEXT = 'text',
  NUMBER = 'number',
  BOOLEAN = 'boolean',
  DATE = 'date',
  SELECT = 'select',
  MULTI_SELECT = 'multi_select',
  TEXTAREA = 'textarea',
  EMAIL = 'email',
  URL = 'url',
  FILE = 'file'
}

export class TemplateManager extends EventEmitter {
  private templates: Map<string, ApprovalTemplate> = new Map();
  private templateVersions: Map<string, TemplateVersion[]> = new Map();
  private templateUsage: Map<string, TemplateUsage> = new Map();
  private templateInheritance: Map<string, TemplateInheritance> = new Map();
  private customFields: Map<string, CustomField> = new Map();
  private options: TemplateManagerOptions;
  private cache: Map<string, { data: any; expires: number }> = new Map();

  constructor(options: Partial<TemplateManagerOptions> = {}) {
    super();
    this.options = {
      enableVersioning: true,
      enableValidation: true,
      maxTemplateVersions: 10,
      enableCache: true,
      cacheTimeout: 300000, // 5 minutes
      enableInheritance: true,
      enableCustomFields: true,
      ...options
    };

    this.initializeDefaultTemplates();
  }

  /**
   * Create a new approval template
   */
  async createTemplate(
    templateData: Omit<ApprovalTemplate, 'id' | 'createdAt' | 'updatedAt'>,
    createdBy: User
  ): Promise<ApprovalTemplate> {
    // Validate template data
    await this.validateTemplate(templateData);

    const template: ApprovalTemplate = {
      ...templateData,
      id: this.generateId(),
      createdBy,
      createdAt: new Date(),
      updatedAt: new Date()
    };

    // Store template
    this.templates.set(template.id, template);

    // Create initial version if versioning is enabled
    if (this.options.enableVersioning) {
      await this.createTemplateVersion(template, createdBy, ['Initial template creation']);
    }

    // Initialize usage tracking
    this.templateUsage.set(template.id, {
      templateId: template.id,
      usageCount: 0,
      lastUsed: new Date(),
      averageProcessingTime: 0,
      successRate: 0,
      userFeedback: []
    });

    // Clear cache
    this.clearCachePattern('templates:');

    this.emit('templateCreated', template);

    return template;
  }

  /**
   * Update an existing template
   */
  async updateTemplate(
    templateId: string,
    updates: Partial<ApprovalTemplate>,
    updatedBy: User,
    changeLog: string[] = []
  ): Promise<ApprovalTemplate> {
    const existingTemplate = this.templates.get(templateId);
    if (!existingTemplate) {
      throw new Error(`Template ${templateId} not found`);
    }

    // Create new version if versioning is enabled
    if (this.options.enableVersioning) {
      await this.createTemplateVersion(existingTemplate, updatedBy, changeLog);
    }

    // Apply updates
    const updatedTemplate: ApprovalTemplate = {
      ...existingTemplate,
      ...updates,
      updatedAt: new Date()
    };

    // Validate updated template
    await this.validateTemplate(updatedTemplate);

    // Store updated template
    this.templates.set(templateId, updatedTemplate);

    // Clear cache
    this.clearCachePattern('templates:');

    this.emit('templateUpdated', { oldTemplate: existingTemplate, newTemplate: updatedTemplate });

    return updatedTemplate;
  }

  /**
   * Clone an existing template
   */
  async cloneTemplate(
    templateId: string,
    cloneOptions: TemplateCloneOptions,
    clonedBy: User
  ): Promise<ApprovalTemplate> {
    const sourceTemplate = this.templates.get(templateId);
    if (!sourceTemplate) {
      throw new Error(`Template ${templateId} not found`);
    }

    let steps = [...sourceTemplate.steps];

    // Remove specified steps
    if (cloneOptions.removeSteps) {
      steps = steps.filter((_, index) => !cloneOptions.removeSteps!.includes(index));
    }

    // Add new steps
    if (cloneOptions.addSteps) {
      steps.push(...cloneOptions.addSteps);
    }

    // Renumber steps
    steps = steps.map((step, index) => ({ ...step, stepNumber: index + 1 }));

    const clonedTemplate: Omit<ApprovalTemplate, 'id' | 'createdAt' | 'updatedAt'> = {
      name: cloneOptions.newName,
      description: cloneOptions.newDescription || `Cloned from ${sourceTemplate.name}`,
      category: cloneOptions.category || sourceTemplate.category,
      steps,
      defaultSettings: {
        ...sourceTemplate.defaultSettings,
        ...cloneOptions.updateSettings
      },
      conditions: [...sourceTemplate.conditions],
      isActive: true,
      version: '1.0.0',
      createdBy: clonedBy
    };

    return await this.createTemplate(clonedTemplate, clonedBy);
  }

  /**
   * Get template by ID
   */
  getTemplate(templateId: string): ApprovalTemplate | undefined {
    const cacheKey = `template:${templateId}`;

    if (this.options.enableCache) {
      const cached = this.getFromCache(cacheKey);
      if (cached) return cached;
    }

    const template = this.templates.get(templateId);

    if (template && this.options.enableCache) {
      this.setCache(cacheKey, template);
    }

    return template;
  }

  /**
   * Get templates with filtering
   */
  getTemplates(filter: TemplateFilter = {}): ApprovalTemplate[] {
    const cacheKey = `templates:${JSON.stringify(filter)}`;

    if (this.options.enableCache) {
      const cached = this.getFromCache(cacheKey);
      if (cached) return cached;
    }

    let templates = Array.from(this.templates.values());

    // Apply filters
    if (filter.category) {
      templates = templates.filter(t => t.category === filter.category);
    }

    if (filter.isActive !== undefined) {
      templates = templates.filter(t => t.isActive === filter.isActive);
    }

    if (filter.createdBy) {
      templates = templates.filter(t => t.createdBy.id === filter.createdBy);
    }

    if (filter.environment) {
      templates = templates.filter(t =>
        t.conditions.some(c => c.field === 'environment' && c.value === filter.environment)
      );
    }

    if (filter.riskLevel) {
      templates = templates.filter(t =>
        t.conditions.some(c => c.field === 'riskLevel' && c.value === filter.riskLevel)
      );
    }

    if (filter.searchTerm) {
      const searchTerm = filter.searchTerm.toLowerCase();
      templates = templates.filter(t =>
        t.name.toLowerCase().includes(searchTerm) ||
        t.description.toLowerCase().includes(searchTerm)
      );
    }

    // Apply sorting
    if (filter.sortBy) {
      templates = this.sortTemplates(templates, filter.sortBy, filter.sortOrder);
    }

    // Apply pagination
    if (filter.offset) {
      templates = templates.slice(filter.offset);
    }

    if (filter.limit) {
      templates = templates.slice(0, filter.limit);
    }

    if (this.options.enableCache) {
      this.setCache(cacheKey, templates);
    }

    return templates;
  }

  /**
   * Delete a template
   */
  async deleteTemplate(templateId: string, deletedBy: User): Promise<void> {
    const template = this.templates.get(templateId);
    if (!template) {
      throw new Error(`Template ${templateId} not found`);
    }

    // Check if template is in use
    const usage = this.templateUsage.get(templateId);
    if (usage && usage.usageCount > 0) {
      // Soft delete - mark as inactive
      template.isActive = false;
      template.updatedAt = new Date();
    } else {
      // Hard delete
      this.templates.delete(templateId);
      this.templateVersions.delete(templateId);
      this.templateUsage.delete(templateId);
      this.templateInheritance.delete(templateId);
    }

    // Clear cache
    this.clearCachePattern('templates:');

    this.emit('templateDeleted', { templateId, template, deletedBy });
  }

  /**
   * Generate approval request from template
   */
  async generateApprovalRequest(
    templateId: string,
    requestData: {
      title: string;
      description: string;
      requester: User;
      approvers?: User[][];
      customData?: Record<string, any>;
    }
  ): Promise<Omit<ApprovalRequest, 'id' | 'status' | 'currentStep' | 'createdAt' | 'updatedAt' | 'auditTrail'>> {
    const template = this.getTemplate(templateId);
    if (!template) {
      throw new Error(`Template ${templateId} not found`);
    }

    if (!template.isActive) {
      throw new Error(`Template ${templateId} is not active`);
    }

    // Generate approval steps from template
    const approvalSteps: ApprovalStep[] = [];

    for (let i = 0; i < template.steps.length; i++) {
      const stepTemplate = template.steps[i];
      const stepApprovers = requestData.approvers?.[i] || await this.resolveApprovers(stepTemplate);

      const step: ApprovalStep = {
        id: this.generateId(),
        stepNumber: stepTemplate.stepNumber,
        name: stepTemplate.name,
        description: stepTemplate.description,
        approverType: stepTemplate.approverType,
        approvers: stepApprovers,
        requiredApprovals: stepTemplate.requiredApprovals,
        status: 'pending' as any,
        responses: [],
        timeout: stepTemplate.timeout,
        escalation: stepTemplate.escalation,
        conditions: stepTemplate.conditions
      };

      approvalSteps.push(step);
    }

    // Determine approval type based on template category
    const approvalType = this.mapCategoryToType(template.category);

    // Determine priority based on custom data or default
    const priority = this.determinePriority(requestData.customData, template);

    // Track template usage
    await this.trackTemplateUsage(templateId);

    const approvalRequest: Omit<ApprovalRequest, 'id' | 'status' | 'currentStep' | 'createdAt' | 'updatedAt' | 'auditTrail'> = {
      title: requestData.title,
      description: requestData.description,
      type: approvalType,
      priority,
      requester: requestData.requester,
      approvers: approvalSteps,
      metadata: {
        templateId,
        templateVersion: template.version,
        customData: requestData.customData
      }
    };

    this.emit('requestGeneratedFromTemplate', { templateId, approvalRequest });

    return approvalRequest;
  }

  /**
   * Get template versions
   */
  getTemplateVersions(templateId: string): TemplateVersion[] {
    if (!this.options.enableVersioning) {
      return [];
    }

    return this.templateVersions.get(templateId) || [];
  }

  /**
   * Restore template version
   */
  async restoreTemplateVersion(
    templateId: string,
    versionId: string,
    restoredBy: User
  ): Promise<ApprovalTemplate> {
    const versions = this.templateVersions.get(templateId) || [];
    const version = versions.find(v => v.id === versionId);

    if (!version) {
      throw new Error(`Template version ${versionId} not found`);
    }

    // Create new version for current state
    const currentTemplate = this.templates.get(templateId);
    if (currentTemplate) {
      await this.createTemplateVersion(
        currentTemplate,
        restoredBy,
        [`Backup before restoring version ${version.version}`]
      );
    }

    // Restore the version
    const restoredTemplate: ApprovalTemplate = {
      ...version.template,
      updatedAt: new Date()
    };

    this.templates.set(templateId, restoredTemplate);

    // Clear cache
    this.clearCachePattern('templates:');

    this.emit('templateVersionRestored', { templateId, versionId, restoredBy });

    return restoredTemplate;
  }

  /**
   * Get template usage statistics
   */
  getTemplateUsage(templateId: string): TemplateUsage | undefined {
    return this.templateUsage.get(templateId);
  }

  /**
   * Add feedback for a template
   */
  async addTemplateFeedback(
    templateId: string,
    feedback: Omit<TemplateFeedback, 'id' | 'templateId' | 'createdAt'>
  ): Promise<TemplateFeedback> {
    const templateFeedback: TemplateFeedback = {
      ...feedback,
      id: this.generateId(),
      templateId,
      createdAt: new Date()
    };

    const usage = this.templateUsage.get(templateId);
    if (usage) {
      usage.userFeedback.push(templateFeedback);
    }

    this.emit('templateFeedbackAdded', templateFeedback);

    return templateFeedback;
  }

  /**
   * Create custom field
   */
  createCustomField(
    fieldData: Omit<CustomField, 'id'>
  ): CustomField {
    if (!this.options.enableCustomFields) {
      throw new Error('Custom fields are not enabled');
    }

    const customField: CustomField = {
      ...fieldData,
      id: this.generateId()
    };

    this.customFields.set(customField.id, customField);

    this.emit('customFieldCreated', customField);

    return customField;
  }

  /**
   * Get custom fields
   */
  getCustomFields(): CustomField[] {
    return Array.from(this.customFields.values());
  }

  /**
   * Validate template configuration
   */
  async validateTemplate(template: Partial<ApprovalTemplate>): Promise<{ valid: boolean; errors: string[] }> {
    if (!this.options.enableValidation) {
      return { valid: true, errors: [] };
    }

    const errors: string[] = [];

    // Basic validation
    if (!template.name || template.name.trim().length === 0) {
      errors.push('Template name is required');
    }

    if (!template.description || template.description.trim().length === 0) {
      errors.push('Template description is required');
    }

    if (!template.steps || template.steps.length === 0) {
      errors.push('At least one approval step is required');
    }

    // Step validation
    if (template.steps) {
      for (let i = 0; i < template.steps.length; i++) {
        const step = template.steps[i];

        if (step.stepNumber !== i + 1) {
          errors.push(`Step ${i + 1} has incorrect step number`);
        }

        if (!step.name || step.name.trim().length === 0) {
          errors.push(`Step ${i + 1} name is required`);
        }

        if (step.requiredApprovals < 1) {
          errors.push(`Step ${i + 1} must require at least one approval`);
        }

        if (step.approverRoles && step.approverRoles.length === 0 && step.approverType === 'role') {
          errors.push(`Step ${i + 1} must specify approver roles when using role-based approval`);
        }
      }
    }

    // Condition validation
    if (template.conditions) {
      for (const condition of template.conditions) {
        if (!condition.field || !condition.operator) {
          errors.push('All conditions must have field and operator');
        }
      }
    }

    const result = { valid: errors.length === 0, errors };

    if (!result.valid) {
      this.emit('templateValidationFailed', { template, errors });
    }

    return result;
  }

  /**
   * Export templates
   */
  exportTemplates(templateIds?: string[]): string {
    let templatesToExport: ApprovalTemplate[];

    if (templateIds) {
      templatesToExport = templateIds
        .map(id => this.templates.get(id))
        .filter(Boolean) as ApprovalTemplate[];
    } else {
      templatesToExport = Array.from(this.templates.values());
    }

    const exportData = {
      version: '1.0',
      exportedAt: new Date().toISOString(),
      templates: templatesToExport,
      customFields: Array.from(this.customFields.values())
    };

    return JSON.stringify(exportData, null, 2);
  }

  /**
   * Import templates
   */
  async importTemplates(
    importData: string,
    importedBy: User,
    options: {
      overwriteExisting?: boolean;
      validateBeforeImport?: boolean;
    } = {}
  ): Promise<{ imported: number; skipped: number; errors: string[] }> {
    const result = { imported: 0, skipped: 0, errors: [] };

    try {
      const data = JSON.parse(importData);

      if (!data.templates || !Array.isArray(data.templates)) {
        throw new Error('Invalid import data format');
      }

      // Import custom fields first
      if (data.customFields && this.options.enableCustomFields) {
        for (const fieldData of data.customFields) {
          try {
            this.createCustomField(fieldData);
          } catch (error) {
            // Field might already exist, skip
          }
        }
      }

      // Import templates
      for (const templateData of data.templates) {
        try {
          // Check if template already exists
          const existingTemplate = Array.from(this.templates.values())
            .find(t => t.name === templateData.name);

          if (existingTemplate && !options.overwriteExisting) {
            result.skipped++;
            continue;
          }

          // Validate if required
          if (options.validateBeforeImport) {
            const validation = await this.validateTemplate(templateData);
            if (!validation.valid) {
              result.errors.push(`Template ${templateData.name}: ${validation.errors.join(', ')}`);
              continue;
            }
          }

          // Remove ID and dates to create new template
          const { id, createdAt, updatedAt, ...templateToImport } = templateData;

          if (existingTemplate && options.overwriteExisting) {
            await this.updateTemplate(
              existingTemplate.id,
              templateToImport,
              importedBy,
              ['Imported template update']
            );
          } else {
            await this.createTemplate(templateToImport, importedBy);
          }

          result.imported++;

        } catch (error) {
          result.errors.push(`Template ${templateData.name}: ${(error as Error).message}`);
        }
      }

    } catch (error) {
      result.errors.push(`Import failed: ${(error as Error).message}`);
    }

    this.emit('templatesImported', result);

    return result;
  }

  // Private methods

  private async createTemplateVersion(
    template: ApprovalTemplate,
    createdBy: User,
    changeLog: string[]
  ): Promise<TemplateVersion> {
    const versions = this.templateVersions.get(template.id) || [];

    const version: TemplateVersion = {
      id: this.generateId(),
      templateId: template.id,
      version: this.generateVersionNumber(versions),
      template: { ...template },
      createdBy,
      createdAt: new Date(),
      isActive: true,
      changeLog
    };

    versions.push(version);

    // Deactivate old versions and keep only the latest N versions
    if (versions.length > this.options.maxTemplateVersions) {
      const versionsToRemove = versions.splice(0, versions.length - this.options.maxTemplateVersions);
      versionsToRemove.forEach(v => v.isActive = false);
    }

    this.templateVersions.set(template.id, versions);

    return version;
  }

  private generateVersionNumber(existingVersions: TemplateVersion[]): string {
    if (existingVersions.length === 0) {
      return '1.0.0';
    }

    const latestVersion = existingVersions[existingVersions.length - 1].version;
    const [major, minor, patch] = latestVersion.split('.').map(Number);

    return `${major}.${minor}.${patch + 1}`;
  }

  private async resolveApprovers(stepTemplate: ApprovalStepTemplate): Promise<User[]> {
    // This would typically integrate with a user service
    // For now, return empty array - would be populated by the calling code
    return [];
  }

  private mapCategoryToType(category: TemplateCategory): ApprovalType {
    switch (category) {
      case TemplateCategory.BASELINE:
        return ApprovalType.BASELINE_UPDATE;
      case TemplateCategory.DEPLOYMENT:
        return ApprovalType.DEPLOYMENT;
      case TemplateCategory.CONFIGURATION:
        return ApprovalType.CONFIGURATION_CHANGE;
      case TemplateCategory.EMERGENCY:
        return ApprovalType.EMERGENCY_CHANGE;
      default:
        return ApprovalType.CONFIGURATION_CHANGE;
    }
  }

  private determinePriority(customData?: Record<string, any>, template?: ApprovalTemplate): ApprovalPriority {
    if (customData?.priority) {
      return customData.priority as ApprovalPriority;
    }

    if (template?.category === TemplateCategory.EMERGENCY) {
      return ApprovalPriority.CRITICAL;
    }

    return ApprovalPriority.MEDIUM;
  }

  private async trackTemplateUsage(templateId: string): Promise<void> {
    const usage = this.templateUsage.get(templateId);
    if (usage) {
      usage.usageCount++;
      usage.lastUsed = new Date();
    }
  }

  private sortTemplates(
    templates: ApprovalTemplate[],
    sortBy: string,
    sortOrder: 'asc' | 'desc' = 'desc'
  ): ApprovalTemplate[] {
    return templates.sort((a, b) => {
      let aValue: any, bValue: any;

      switch (sortBy) {
        case 'name':
          aValue = a.name.toLowerCase();
          bValue = b.name.toLowerCase();
          break;
        case 'createdAt':
          aValue = a.createdAt.getTime();
          bValue = b.createdAt.getTime();
          break;
        case 'updatedAt':
          aValue = a.updatedAt.getTime();
          bValue = b.updatedAt.getTime();
          break;
        case 'category':
          aValue = a.category;
          bValue = b.category;
          break;
        case 'usage':
          const usageA = this.templateUsage.get(a.id);
          const usageB = this.templateUsage.get(b.id);
          aValue = usageA?.usageCount || 0;
          bValue = usageB?.usageCount || 0;
          break;
        default:
          return 0;
      }

      if (sortOrder === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
      }
    });
  }

  private getFromCache(key: string): any {
    if (!this.options.enableCache) return null;

    const cached = this.cache.get(key);
    if (cached && cached.expires > Date.now()) {
      return cached.data;
    }

    this.cache.delete(key);
    return null;
  }

  private setCache(key: string, data: any): void {
    if (!this.options.enableCache) return;

    this.cache.set(key, {
      data,
      expires: Date.now() + this.options.cacheTimeout
    });
  }

  private clearCachePattern(pattern: string): void {
    if (!this.options.enableCache) return;

    for (const key of this.cache.keys()) {
      if (key.startsWith(pattern)) {
        this.cache.delete(key);
      }
    }
  }

  private initializeDefaultTemplates(): void {
    // Initialize with some default templates
    const defaultTemplates = [
      {
        name: 'Standard Baseline Update',
        description: 'Standard approval process for baseline updates',
        category: TemplateCategory.BASELINE,
        steps: [
          {
            stepNumber: 1,
            name: 'Technical Review',
            description: 'Technical review of the baseline update',
            approverType: 'role' as any,
            approverRoles: ['reviewer' as UserRole],
            requiredApprovals: 1,
            timeout: 480 // 8 hours
          },
          {
            stepNumber: 2,
            name: 'Management Approval',
            description: 'Management approval for the update',
            approverType: 'role' as any,
            approverRoles: ['approver' as UserRole],
            requiredApprovals: 1,
            timeout: 1440 // 24 hours
          }
        ],
        defaultSettings: {
          allowParallel: false,
          requireAllApprovers: false,
          allowDelegation: true,
          allowWithdrawal: true,
          autoEscalate: true,
          notifyOnDecision: true,
          auditLevel: 'standard' as any
        },
        conditions: [],
        isActive: true,
        version: '1.0.0'
      },
      {
        name: 'Emergency Change',
        description: 'Fast-track approval for emergency changes',
        category: TemplateCategory.EMERGENCY,
        steps: [
          {
            stepNumber: 1,
            name: 'Emergency Approval',
            description: 'Emergency approval by on-call manager',
            approverType: 'role' as any,
            approverRoles: ['admin' as UserRole],
            requiredApprovals: 1,
            timeout: 60 // 1 hour
          }
        ],
        defaultSettings: {
          allowParallel: false,
          requireAllApprovers: true,
          allowDelegation: false,
          allowWithdrawal: false,
          autoEscalate: true,
          notifyOnDecision: true,
          auditLevel: 'detailed' as any
        },
        conditions: [],
        isActive: true,
        version: '1.0.0'
      }
    ];

    // Create system user for default templates
    const systemUser: User = {
      id: 'system',
      username: 'system',
      email: 'system@system.local',
      fullName: 'System',
      role: 'admin' as UserRole,
      permissions: [],
      isActive: true,
      timezone: 'UTC',
      notificationPreferences: []
    };

    for (const templateData of defaultTemplates) {
      this.createTemplate(templateData, systemUser);
    }
  }

  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
}