import {
  ApprovalTemplate,
  ApprovalStepTemplate,
  ApprovalCondition,
  ApprovalSettings,
  User,
  UserRole,
  TemplateCategory,
  ConditionType,
  ComparisonOperator,
  LogicOperator,
  ApproverType,
  EscalationRule,
  EscalationAction,
  EscalationTrigger
} from '../types/approval.types.js';
import { EventEmitter } from 'events';

export interface WorkflowBuilderOptions {
  enableValidation: boolean;
  enablePreview: boolean;
  enableVersioning: boolean;
  maxSteps: number;
  maxConditions: number;
  enableDragDrop: boolean;
}

export interface WorkflowStep {
  id: string;
  type: StepType;
  name: string;
  description?: string;
  config: StepConfig;
  position: { x: number; y: number };
  connections: StepConnection[];
  isRequired: boolean;
  isActive: boolean;
}

export interface StepConfig {
  approvers?: ApproverConfig;
  conditions?: ConditionConfig[];
  escalation?: EscalationConfig;
  timeout?: number;
  notifications?: NotificationConfig;
  customFields?: CustomFieldConfig[];
}

export interface ApproverConfig {
  type: ApproverType;
  roles?: UserRole[];
  users?: string[]; // User IDs
  groups?: string[]; // Group IDs
  requiredCount: number;
  allowDelegation: boolean;
}

export interface ConditionConfig {
  field: string;
  operator: ComparisonOperator;
  value: any;
  logic: LogicOperator;
  description?: string;
}

export interface EscalationConfig {
  enabled: boolean;
  trigger: EscalationTrigger;
  delay: number; // minutes
  action: EscalationAction;
  escalateTo: string[]; // User IDs
  maxEscalations: number;
}

export interface NotificationConfig {
  enabled: boolean;
  channels: string[];
  customMessage?: string;
  recipients?: string[];
}

export interface CustomFieldConfig {
  name: string;
  type: string;
  required: boolean;
  defaultValue?: any;
  validation?: any;
}

export interface StepConnection {
  sourceStepId: string;
  targetStepId: string;
  condition?: string;
  label?: string;
}

export interface WorkflowValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
}

export interface ValidationError {
  stepId?: string;
  field?: string;
  message: string;
  severity: 'error' | 'warning' | 'info';
}

export interface ValidationWarning {
  stepId?: string;
  message: string;
  suggestion?: string;
}

export interface WorkflowPreview {
  template: ApprovalTemplate;
  flowDiagram: FlowDiagramNode[];
  estimatedTime: number;
  complexity: WorkflowComplexity;
  recommendations: string[];
}

export interface FlowDiagramNode {
  id: string;
  type: 'start' | 'step' | 'decision' | 'end';
  label: string;
  position: { x: number; y: number };
  connections: string[];
  metadata?: any;
}

export enum StepType {
  APPROVAL = 'approval',
  REVIEW = 'review',
  NOTIFICATION = 'notification',
  CONDITION = 'condition',
  PARALLEL = 'parallel',
  MERGE = 'merge',
  CUSTOM = 'custom'
}

export enum WorkflowComplexity {
  SIMPLE = 'simple',
  MODERATE = 'moderate',
  COMPLEX = 'complex',
  VERY_COMPLEX = 'very_complex'
}

export class WorkflowBuilder extends EventEmitter {
  private steps: Map<string, WorkflowStep> = new Map();
  private connections: StepConnection[] = [];
  private settings: ApprovalSettings;
  private metadata: Record<string, any> = {};
  private options: WorkflowBuilderOptions;

  constructor(options: Partial<WorkflowBuilderOptions> = {}) {
    super();
    this.options = {
      enableValidation: true,
      enablePreview: true,
      enableVersioning: true,
      maxSteps: 20,
      maxConditions: 10,
      enableDragDrop: true,
      ...options
    };

    this.settings = this.getDefaultSettings();
  }

  /**
   * Add a step to the workflow
   */
  addStep(stepData: Omit<WorkflowStep, 'id' | 'connections'>): WorkflowStep {
    if (this.steps.size >= this.options.maxSteps) {
      throw new Error(`Maximum number of steps (${this.options.maxSteps}) exceeded`);
    }

    const step: WorkflowStep = {
      ...stepData,
      id: this.generateId(),
      connections: []
    };

    this.steps.set(step.id, step);
    this.emit('stepAdded', step);

    return step;
  }

  /**
   * Update an existing step
   */
  updateStep(stepId: string, updates: Partial<WorkflowStep>): WorkflowStep {
    const step = this.steps.get(stepId);
    if (!step) {
      throw new Error(`Step ${stepId} not found`);
    }

    const updatedStep = { ...step, ...updates };
    this.steps.set(stepId, updatedStep);
    this.emit('stepUpdated', { oldStep: step, newStep: updatedStep });

    return updatedStep;
  }

  /**
   * Remove a step from the workflow
   */
  removeStep(stepId: string): void {
    const step = this.steps.get(stepId);
    if (!step) {
      throw new Error(`Step ${stepId} not found`);
    }

    // Remove connections involving this step
    this.connections = this.connections.filter(
      conn => conn.sourceStepId !== stepId && conn.targetStepId !== stepId
    );

    // Update other steps' connections
    for (const otherStep of this.steps.values()) {
      otherStep.connections = otherStep.connections.filter(
        conn => conn.sourceStepId !== stepId && conn.targetStepId !== stepId
      );
    }

    this.steps.delete(stepId);
    this.emit('stepRemoved', { stepId, step });
  }

  /**
   * Connect two steps
   */
  connectSteps(sourceStepId: string, targetStepId: string, condition?: string, label?: string): StepConnection {
    const sourceStep = this.steps.get(sourceStepId);
    const targetStep = this.steps.get(targetStepId);

    if (!sourceStep) {
      throw new Error(`Source step ${sourceStepId} not found`);
    }

    if (!targetStep) {
      throw new Error(`Target step ${targetStepId} not found`);
    }

    // Check for circular dependencies
    if (this.wouldCreateCircularDependency(sourceStepId, targetStepId)) {
      throw new Error('Connection would create a circular dependency');
    }

    const connection: StepConnection = {
      sourceStepId,
      targetStepId,
      condition,
      label
    };

    this.connections.push(connection);
    sourceStep.connections.push(connection);

    this.emit('stepsConnected', connection);

    return connection;
  }

  /**
   * Disconnect two steps
   */
  disconnectSteps(sourceStepId: string, targetStepId: string): void {
    this.connections = this.connections.filter(
      conn => !(conn.sourceStepId === sourceStepId && conn.targetStepId === targetStepId)
    );

    const sourceStep = this.steps.get(sourceStepId);
    if (sourceStep) {
      sourceStep.connections = sourceStep.connections.filter(
        conn => !(conn.sourceStepId === sourceStepId && conn.targetStepId === targetStepId)
      );
    }

    this.emit('stepsDisconnected', { sourceStepId, targetStepId });
  }

  /**
   * Reorder steps
   */
  reorderSteps(stepIds: string[]): void {
    const reorderedSteps = new Map<string, WorkflowStep>();

    for (let i = 0; i < stepIds.length; i++) {
      const stepId = stepIds[i];
      const step = this.steps.get(stepId);
      if (step) {
        // Update position if using drag and drop
        if (this.options.enableDragDrop) {
          step.position = { x: i * 200, y: 100 };
        }
        reorderedSteps.set(stepId, step);
      }
    }

    this.steps = reorderedSteps;
    this.emit('stepsReordered', stepIds);
  }

  /**
   * Validate the workflow
   */
  validateWorkflow(): WorkflowValidationResult {
    const errors: ValidationError[] = [];
    const warnings: ValidationWarning[] = [];

    if (!this.options.enableValidation) {
      return { isValid: true, errors, warnings };
    }

    // Check if workflow has steps
    if (this.steps.size === 0) {
      errors.push({
        message: 'Workflow must have at least one step',
        severity: 'error'
      });
    }

    // Validate each step
    for (const step of this.steps.values()) {
      const stepValidation = this.validateStep(step);
      errors.push(...stepValidation.errors);
      warnings.push(...stepValidation.warnings);
    }

    // Check for disconnected steps
    const disconnectedSteps = this.findDisconnectedSteps();
    if (disconnectedSteps.length > 0) {
      warnings.push({
        message: `Disconnected steps found: ${disconnectedSteps.map(s => s.name).join(', ')}`,
        suggestion: 'Connect all steps to ensure proper workflow flow'
      });
    }

    // Check for circular dependencies
    const circularDeps = this.findCircularDependencies();
    if (circularDeps.length > 0) {
      errors.push({
        message: 'Circular dependencies detected in workflow',
        severity: 'error'
      });
    }

    // Check workflow complexity
    const complexity = this.calculateComplexity();
    if (complexity === WorkflowComplexity.VERY_COMPLEX) {
      warnings.push({
        message: 'Workflow is very complex and may be difficult to manage',
        suggestion: 'Consider breaking into smaller workflows'
      });
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }

  /**
   * Generate preview of the workflow
   */
  generatePreview(): WorkflowPreview {
    if (!this.options.enablePreview) {
      throw new Error('Preview is not enabled');
    }

    const template = this.buildTemplate();
    const flowDiagram = this.generateFlowDiagram();
    const estimatedTime = this.calculateEstimatedTime();
    const complexity = this.calculateComplexity();
    const recommendations = this.generateRecommendations();

    return {
      template,
      flowDiagram,
      estimatedTime,
      complexity,
      recommendations
    };
  }

  /**
   * Build the final approval template
   */
  buildTemplate(): ApprovalTemplate {
    const validation = this.validateWorkflow();
    if (!validation.isValid) {
      throw new Error(`Cannot build template: ${validation.errors.map(e => e.message).join(', ')}`);
    }

    // Convert workflow steps to approval step templates
    const stepTemplates: ApprovalStepTemplate[] = [];
    let stepNumber = 1;

    // Sort steps by position or connection order
    const sortedSteps = this.getSortedSteps();

    for (const step of sortedSteps) {
      if (step.type === StepType.APPROVAL || step.type === StepType.REVIEW) {
        const stepTemplate: ApprovalStepTemplate = {
          stepNumber,
          name: step.name,
          description: step.description,
          approverType: step.config.approvers?.type || ApproverType.ROLE,
          approverRoles: step.config.approvers?.roles || [],
          requiredApprovals: step.config.approvers?.requiredCount || 1,
          timeout: step.config.timeout,
          escalation: step.config.escalation ? this.buildEscalationRule(step.config.escalation) : undefined,
          conditions: step.config.conditions ? step.config.conditions.map(this.buildCondition) : []
        };

        stepTemplates.push(stepTemplate);
        stepNumber++;
      }
    }

    const template: ApprovalTemplate = {
      id: this.generateId(),
      name: this.metadata.name || 'Untitled Workflow',
      description: this.metadata.description || 'Generated workflow',
      category: this.metadata.category || TemplateCategory.CUSTOM,
      steps: stepTemplates,
      defaultSettings: this.settings,
      conditions: this.buildGlobalConditions(),
      isActive: true,
      version: '1.0.0',
      createdBy: this.metadata.createdBy,
      createdAt: new Date(),
      updatedAt: new Date()
    };

    return template;
  }

  /**
   * Import workflow from template
   */
  importFromTemplate(template: ApprovalTemplate): void {
    this.clear();

    // Convert template steps to workflow steps
    for (let i = 0; i < template.steps.length; i++) {
      const stepTemplate = template.steps[i];

      const step: Omit<WorkflowStep, 'id' | 'connections'> = {
        type: StepType.APPROVAL,
        name: stepTemplate.name,
        description: stepTemplate.description,
        config: {
          approvers: {
            type: stepTemplate.approverType,
            roles: stepTemplate.approverRoles,
            requiredCount: stepTemplate.requiredApprovals,
            allowDelegation: true
          },
          timeout: stepTemplate.timeout,
          escalation: stepTemplate.escalation ? {
            enabled: true,
            trigger: stepTemplate.escalation.trigger,
            delay: stepTemplate.escalation.delay,
            action: stepTemplate.escalation.action,
            escalateTo: stepTemplate.escalation.escalateTo.map(u => u.id),
            maxEscalations: stepTemplate.escalation.maxEscalations
          } : undefined,
          conditions: stepTemplate.conditions?.map(c => ({
            field: c.field,
            operator: c.operator,
            value: c.value,
            logic: c.logic
          }))
        },
        position: { x: i * 200, y: 100 },
        isRequired: true,
        isActive: true
      };

      this.addStep(step);
    }

    // Connect steps sequentially
    const stepIds = Array.from(this.steps.keys());
    for (let i = 0; i < stepIds.length - 1; i++) {
      this.connectSteps(stepIds[i], stepIds[i + 1]);
    }

    this.settings = template.defaultSettings;
    this.metadata = {
      name: template.name,
      description: template.description,
      category: template.category,
      templateId: template.id
    };

    this.emit('workflowImported', template);
  }

  /**
   * Export workflow configuration
   */
  exportConfiguration(): any {
    return {
      steps: Array.from(this.steps.values()),
      connections: this.connections,
      settings: this.settings,
      metadata: this.metadata,
      version: '1.0'
    };
  }

  /**
   * Import workflow configuration
   */
  importConfiguration(config: any): void {
    this.clear();

    // Import steps
    if (config.steps) {
      for (const stepData of config.steps) {
        this.steps.set(stepData.id, stepData);
      }
    }

    // Import connections
    if (config.connections) {
      this.connections = config.connections;
    }

    // Import settings
    if (config.settings) {
      this.settings = config.settings;
    }

    // Import metadata
    if (config.metadata) {
      this.metadata = config.metadata;
    }

    this.emit('configurationImported', config);
  }

  /**
   * Clear the workflow
   */
  clear(): void {
    this.steps.clear();
    this.connections = [];
    this.settings = this.getDefaultSettings();
    this.metadata = {};

    this.emit('workflowCleared');
  }

  /**
   * Get workflow statistics
   */
  getStatistics(): any {
    const stepTypes = Array.from(this.steps.values()).reduce((acc, step) => {
      acc[step.type] = (acc[step.type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return {
      totalSteps: this.steps.size,
      stepTypes,
      totalConnections: this.connections.length,
      complexity: this.calculateComplexity(),
      estimatedTime: this.calculateEstimatedTime(),
      hasCircularDependencies: this.findCircularDependencies().length > 0,
      disconnectedSteps: this.findDisconnectedSteps().length
    };
  }

  // Private methods

  private validateStep(step: WorkflowStep): { errors: ValidationError[]; warnings: ValidationWarning[] } {
    const errors: ValidationError[] = [];
    const warnings: ValidationWarning[] = [];

    // Validate step name
    if (!step.name || step.name.trim().length === 0) {
      errors.push({
        stepId: step.id,
        field: 'name',
        message: 'Step name is required',
        severity: 'error'
      });
    }

    // Validate approvers configuration
    if (step.type === StepType.APPROVAL && step.config.approvers) {
      const approvers = step.config.approvers;

      if (approvers.requiredCount < 1) {
        errors.push({
          stepId: step.id,
          field: 'approvers.requiredCount',
          message: 'Required approvals must be at least 1',
          severity: 'error'
        });
      }

      if (approvers.type === ApproverType.ROLE && (!approvers.roles || approvers.roles.length === 0)) {
        errors.push({
          stepId: step.id,
          field: 'approvers.roles',
          message: 'Role-based approval must specify at least one role',
          severity: 'error'
        });
      }

      if (approvers.type === ApproverType.USER && (!approvers.users || approvers.users.length === 0)) {
        errors.push({
          stepId: step.id,
          field: 'approvers.users',
          message: 'User-based approval must specify at least one user',
          severity: 'error'
        });
      }
    }

    // Validate timeout
    if (step.config.timeout && step.config.timeout < 1) {
      errors.push({
        stepId: step.id,
        field: 'timeout',
        message: 'Timeout must be at least 1 minute',
        severity: 'error'
      });
    }

    // Validate conditions count
    if (step.config.conditions && step.config.conditions.length > this.options.maxConditions) {
      warnings.push({
        stepId: step.id,
        message: `Step has ${step.config.conditions.length} conditions, maximum recommended is ${this.options.maxConditions}`,
        suggestion: 'Consider simplifying conditions'
      });
    }

    return { errors, warnings };
  }

  private wouldCreateCircularDependency(sourceStepId: string, targetStepId: string): boolean {
    // Simple cycle detection using DFS
    const visited = new Set<string>();
    const stack = new Set<string>();

    const hasCycle = (stepId: string): boolean => {
      if (stack.has(stepId)) return true;
      if (visited.has(stepId)) return false;

      visited.add(stepId);
      stack.add(stepId);

      const step = this.steps.get(stepId);
      if (step) {
        for (const connection of step.connections) {
          if (hasCycle(connection.targetStepId)) {
            return true;
          }
        }
      }

      stack.delete(stepId);
      return false;
    };

    // Temporarily add the connection and check for cycles
    const tempConnection: StepConnection = { sourceStepId, targetStepId };
    const sourceStep = this.steps.get(sourceStepId);
    if (sourceStep) {
      sourceStep.connections.push(tempConnection);
      const wouldCycle = hasCycle(sourceStepId);
      sourceStep.connections.pop(); // Remove temporary connection
      return wouldCycle;
    }

    return false;
  }

  private findDisconnectedSteps(): WorkflowStep[] {
    const connectedSteps = new Set<string>();

    // Add all steps that are part of connections
    for (const connection of this.connections) {
      connectedSteps.add(connection.sourceStepId);
      connectedSteps.add(connection.targetStepId);
    }

    // Find steps that are not connected
    return Array.from(this.steps.values()).filter(step => !connectedSteps.has(step.id));
  }

  private findCircularDependencies(): string[] {
    const visited = new Set<string>();
    const stack = new Set<string>();
    const cycles: string[] = [];

    const dfs = (stepId: string, path: string[]): void => {
      if (stack.has(stepId)) {
        cycles.push(path.join(' -> '));
        return;
      }

      if (visited.has(stepId)) return;

      visited.add(stepId);
      stack.add(stepId);

      const step = this.steps.get(stepId);
      if (step) {
        for (const connection of step.connections) {
          dfs(connection.targetStepId, [...path, stepId]);
        }
      }

      stack.delete(stepId);
    };

    for (const stepId of this.steps.keys()) {
      if (!visited.has(stepId)) {
        dfs(stepId, []);
      }
    }

    return cycles;
  }

  private calculateComplexity(): WorkflowComplexity {
    const stepCount = this.steps.size;
    const connectionCount = this.connections.length;
    const conditionCount = Array.from(this.steps.values())
      .reduce((count, step) => count + (step.config.conditions?.length || 0), 0);

    const complexityScore = stepCount + (connectionCount * 0.5) + (conditionCount * 2);

    if (complexityScore <= 5) return WorkflowComplexity.SIMPLE;
    if (complexityScore <= 15) return WorkflowComplexity.MODERATE;
    if (complexityScore <= 30) return WorkflowComplexity.COMPLEX;
    return WorkflowComplexity.VERY_COMPLEX;
  }

  private calculateEstimatedTime(): number {
    let totalTime = 0;

    for (const step of this.steps.values()) {
      if (step.type === StepType.APPROVAL || step.type === StepType.REVIEW) {
        totalTime += step.config.timeout || 1440; // Default 24 hours
      }
    }

    return totalTime;
  }

  private generateRecommendations(): string[] {
    const recommendations: string[] = [];
    const complexity = this.calculateComplexity();

    if (complexity === WorkflowComplexity.VERY_COMPLEX) {
      recommendations.push('Consider simplifying the workflow by reducing the number of steps or conditions');
    }

    if (this.findDisconnectedSteps().length > 0) {
      recommendations.push('Connect all steps to ensure proper workflow execution');
    }

    const longTimeouts = Array.from(this.steps.values())
      .filter(step => (step.config.timeout || 0) > 2880); // More than 48 hours

    if (longTimeouts.length > 0) {
      recommendations.push('Consider reducing timeout values for faster workflow completion');
    }

    const stepsWithoutEscalation = Array.from(this.steps.values())
      .filter(step => step.type === StepType.APPROVAL && !step.config.escalation?.enabled);

    if (stepsWithoutEscalation.length > 0) {
      recommendations.push('Consider adding escalation rules to prevent workflow delays');
    }

    return recommendations;
  }

  private generateFlowDiagram(): FlowDiagramNode[] {
    const nodes: FlowDiagramNode[] = [];

    // Add start node
    nodes.push({
      id: 'start',
      type: 'start',
      label: 'Start',
      position: { x: 50, y: 50 },
      connections: []
    });

    // Add step nodes
    for (const step of this.steps.values()) {
      nodes.push({
        id: step.id,
        type: 'step',
        label: step.name,
        position: step.position,
        connections: step.connections.map(c => c.targetStepId),
        metadata: {
          stepType: step.type,
          isRequired: step.isRequired,
          hasConditions: (step.config.conditions?.length || 0) > 0
        }
      });
    }

    // Add end node
    nodes.push({
      id: 'end',
      type: 'end',
      label: 'End',
      position: { x: 500, y: 300 },
      connections: []
    });

    return nodes;
  }

  private getSortedSteps(): WorkflowStep[] {
    // Topological sort of steps based on connections
    const steps = Array.from(this.steps.values());
    const sorted: WorkflowStep[] = [];
    const visited = new Set<string>();

    const visit = (step: WorkflowStep): void => {
      if (visited.has(step.id)) return;

      visited.add(step.id);

      // Visit dependencies first (steps that this step depends on)
      for (const connection of this.connections) {
        if (connection.targetStepId === step.id) {
          const sourceStep = this.steps.get(connection.sourceStepId);
          if (sourceStep) {
            visit(sourceStep);
          }
        }
      }

      sorted.push(step);
    };

    for (const step of steps) {
      visit(step);
    }

    return sorted;
  }

  private buildEscalationRule(config: EscalationConfig): EscalationRule {
    return {
      id: this.generateId(),
      trigger: config.trigger,
      delay: config.delay,
      action: config.action,
      escalateTo: config.escalateTo.map(userId => ({
        id: userId,
        username: '',
        email: '',
        fullName: '',
        role: 'approver' as UserRole,
        permissions: [],
        isActive: true,
        timezone: 'UTC',
        notificationPreferences: []
      })),
      maxEscalations: config.maxEscalations,
      notificationTemplate: ''
    };
  }

  private buildCondition(config: ConditionConfig): ApprovalCondition {
    return {
      id: this.generateId(),
      type: ConditionType.FIELD_VALUE,
      field: config.field,
      operator: config.operator,
      value: config.value,
      logic: config.logic
    };
  }

  private buildGlobalConditions(): ApprovalCondition[] {
    // Extract global conditions from metadata or settings
    return [];
  }

  private getDefaultSettings(): ApprovalSettings {
    return {
      allowParallel: false,
      requireAllApprovers: false,
      allowDelegation: true,
      allowWithdrawal: true,
      autoEscalate: true,
      notifyOnDecision: true,
      auditLevel: 'standard' as any
    };
  }

  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  // Getters for external access
  get allSteps(): WorkflowStep[] {
    return Array.from(this.steps.values());
  }

  get allConnections(): StepConnection[] {
    return [...this.connections];
  }

  get workflowSettings(): ApprovalSettings {
    return { ...this.settings };
  }

  get workflowMetadata(): Record<string, any> {
    return { ...this.metadata };
  }

  // Setters
  updateSettings(settings: Partial<ApprovalSettings>): void {
    this.settings = { ...this.settings, ...settings };
    this.emit('settingsUpdated', this.settings);
  }

  updateMetadata(metadata: Record<string, any>): void {
    this.metadata = { ...this.metadata, ...metadata };
    this.emit('metadataUpdated', this.metadata);
  }
}