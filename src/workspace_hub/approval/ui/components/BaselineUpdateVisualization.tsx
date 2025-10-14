import React, { useState, useEffect, useMemo } from 'react';
import {
  BaselineUpdateRequest,
  BaselineChange,
  ImpactAssessment,
  RollbackPlan,
  DeploymentState,
  DeploymentStatus,
  RiskLevel,
  ChangeType,
  Environment
} from '../../types/approval.types.js';

// Component interfaces
interface BaselineUpdateVisualizationProps {
  updateRequest: BaselineUpdateRequest;
  deploymentState?: DeploymentState;
  onApprove?: () => void;
  onReject?: () => void;
  onRollback?: () => void;
  readonly?: boolean;
}

interface ChangeVisualizationProps {
  changes: BaselineChange[];
  currentChange?: number;
  onChangeSelect?: (changeId: string) => void;
}

interface ImpactVisualizationProps {
  impact: ImpactAssessment;
  showDetails?: boolean;
}

interface RollbackVisualizationProps {
  rollbackPlan: RollbackPlan;
  onExecuteRollback?: () => void;
  canExecute?: boolean;
}

interface DeploymentProgressProps {
  deploymentState: DeploymentState;
  onCancel?: () => void;
  onViewLogs?: () => void;
}

export const BaselineUpdateVisualization: React.FC<BaselineUpdateVisualizationProps> = ({
  updateRequest,
  deploymentState,
  onApprove,
  onReject,
  onRollback,
  readonly = false
}) => {
  const [selectedTab, setSelectedTab] = useState<'overview' | 'changes' | 'impact' | 'rollback' | 'deployment'>('overview');
  const [selectedChange, setSelectedChange] = useState<string | null>(null);
  const [showDiff, setShowDiff] = useState(false);

  const getRiskLevelColor = (risk: RiskLevel): string => {
    switch (risk) {
      case RiskLevel.CRITICAL:
        return 'text-red-600 bg-red-100 border-red-200';
      case RiskLevel.HIGH:
        return 'text-orange-600 bg-orange-100 border-orange-200';
      case RiskLevel.MEDIUM:
        return 'text-yellow-600 bg-yellow-100 border-yellow-200';
      case RiskLevel.LOW:
        return 'text-green-600 bg-green-100 border-green-200';
      default:
        return 'text-gray-600 bg-gray-100 border-gray-200';
    }
  };

  const getEnvironmentColor = (env: Environment): string => {
    switch (env) {
      case Environment.PRODUCTION:
        return 'text-red-600 bg-red-100';
      case Environment.STAGING:
        return 'text-yellow-600 bg-yellow-100';
      case Environment.DEVELOPMENT:
        return 'text-green-600 bg-green-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const formatDate = (date: Date): string => {
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(new Date(date));
  };

  return (
    <div className="max-w-6xl mx-auto bg-white rounded-lg shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Baseline Update Request</h1>
            <p className="text-blue-100 mt-1">
              {updateRequest.updateType} for {updateRequest.targetEnvironment}
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getEnvironmentColor(updateRequest.targetEnvironment)}`}>
              {updateRequest.targetEnvironment.toUpperCase()}
            </span>
            <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getRiskLevelColor(updateRequest.impactAssessment.riskLevel)}`}>
              {updateRequest.impactAssessment.riskLevel.toUpperCase()} RISK
            </span>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8 px-6">
          {[
            { key: 'overview', label: 'Overview', icon: '📋' },
            { key: 'changes', label: `Changes (${updateRequest.changes.length})`, icon: '🔧' },
            { key: 'impact', label: 'Impact Assessment', icon: '📊' },
            { key: 'rollback', label: 'Rollback Plan', icon: '🔄' },
            ...(deploymentState ? [{ key: 'deployment', label: 'Deployment', icon: '🚀' }] : [])
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setSelectedTab(tab.key as any)}
              className={`${
                selectedTab === tab.key
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2`}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="p-6">
        {selectedTab === 'overview' && (
          <OverviewTab
            updateRequest={updateRequest}
            deploymentState={deploymentState}
            onApprove={onApprove}
            onReject={onReject}
            readonly={readonly}
          />
        )}

        {selectedTab === 'changes' && (
          <ChangesTab
            changes={updateRequest.changes}
            currentChange={deploymentState?.currentChange}
            selectedChange={selectedChange}
            onChangeSelect={setSelectedChange}
            showDiff={showDiff}
            onToggleDiff={() => setShowDiff(!showDiff)}
          />
        )}

        {selectedTab === 'impact' && (
          <ImpactTab impact={updateRequest.impactAssessment} />
        )}

        {selectedTab === 'rollback' && (
          <RollbackTab
            rollbackPlan={updateRequest.rollbackPlan}
            onExecuteRollback={onRollback}
            canExecute={deploymentState?.status === DeploymentStatus.FAILED}
          />
        )}

        {selectedTab === 'deployment' && deploymentState && (
          <DeploymentTab
            deploymentState={deploymentState}
            updateRequest={updateRequest}
          />
        )}
      </div>
    </div>
  );
};

// Overview Tab Component
interface OverviewTabProps {
  updateRequest: BaselineUpdateRequest;
  deploymentState?: DeploymentState;
  onApprove?: () => void;
  onReject?: () => void;
  readonly?: boolean;
}

const OverviewTab: React.FC<OverviewTabProps> = ({
  updateRequest,
  deploymentState,
  onApprove,
  onReject,
  readonly
}) => {
  const summary = useMemo(() => {
    const changesByType = updateRequest.changes.reduce((acc, change) => {
      acc[change.type] = (acc[change.type] || 0) + 1;
      return acc;
    }, {} as Record<ChangeType, number>);

    const changesByRisk = updateRequest.changes.reduce((acc, change) => {
      acc[change.risk] = (acc[change.risk] || 0) + 1;
      return acc;
    }, {} as Record<RiskLevel, number>);

    return { changesByType, changesByRisk };
  }, [updateRequest.changes]);

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-lg font-medium text-blue-900 mb-2">Update Summary</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-blue-700">Total Changes:</span>
              <span className="font-medium">{updateRequest.changes.length}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-blue-700">Environment:</span>
              <span className="font-medium">{updateRequest.targetEnvironment}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-blue-700">Type:</span>
              <span className="font-medium">{updateRequest.updateType}</span>
            </div>
          </div>
        </div>

        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
          <h3 className="text-lg font-medium text-orange-900 mb-2">Impact Summary</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-orange-700">Risk Level:</span>
              <span className="font-medium">{updateRequest.impactAssessment.riskLevel}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-orange-700">Affected Users:</span>
              <span className="font-medium">{updateRequest.impactAssessment.affectedUsers.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-orange-700">Downtime:</span>
              <span className="font-medium">{updateRequest.impactAssessment.downtime}m</span>
            </div>
          </div>
        </div>

        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h3 className="text-lg font-medium text-green-900 mb-2">Rollback Plan</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-green-700">Strategy:</span>
              <span className="font-medium">{updateRequest.rollbackPlan.strategy}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-green-700">Steps:</span>
              <span className="font-medium">{updateRequest.rollbackPlan.steps.length}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-green-700">Est. Time:</span>
              <span className="font-medium">{updateRequest.rollbackPlan.estimatedTime}m</span>
            </div>
          </div>
        </div>
      </div>

      {/* Changes Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Changes by Type</h3>
          <div className="space-y-3">
            {Object.entries(summary.changesByType).map(([type, count]) => (
              <div key={type} className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className={`w-3 h-3 rounded-full ${getChangeTypeColor(type as ChangeType)}`}></div>
                  <span className="capitalize">{type}</span>
                </div>
                <span className="font-medium">{count}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Changes by Risk</h3>
          <div className="space-y-3">
            {Object.entries(summary.changesByRisk).map(([risk, count]) => (
              <div key={risk} className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className={`w-3 h-3 rounded-full ${getRiskColor(risk as RiskLevel)}`}></div>
                  <span className="capitalize">{risk}</span>
                </div>
                <span className="font-medium">{count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Deployment Status */}
      {deploymentState && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Current Status</h3>
          <DeploymentProgressIndicator deploymentState={deploymentState} />
        </div>
      )}

      {/* Action Buttons */}
      {!readonly && !deploymentState && (onApprove || onReject) && (
        <div className="flex items-center justify-end space-x-4 pt-6 border-t border-gray-200">
          {onReject && (
            <button
              onClick={onReject}
              className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg font-medium"
            >
              Reject Update
            </button>
          )}
          {onApprove && (
            <button
              onClick={onApprove}
              className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium"
            >
              Approve Update
            </button>
          )}
        </div>
      )}
    </div>
  );
};

// Changes Tab Component
interface ChangesTabProps {
  changes: BaselineChange[];
  currentChange?: number;
  selectedChange: string | null;
  onChangeSelect: (changeId: string) => void;
  showDiff: boolean;
  onToggleDiff: () => void;
}

const ChangesTab: React.FC<ChangesTabProps> = ({
  changes,
  currentChange,
  selectedChange,
  onChangeSelect,
  showDiff,
  onToggleDiff
}) => {
  const selectedChangeData = changes.find(c => c.id === selectedChange);

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-gray-900">
          Changes ({changes.length})
        </h3>
        <button
          onClick={onToggleDiff}
          className="bg-blue-100 hover:bg-blue-200 text-blue-700 px-4 py-2 rounded-lg text-sm font-medium"
        >
          {showDiff ? 'Hide Diff' : 'Show Diff'}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Changes List */}
        <div className="space-y-4">
          {changes.map((change, index) => (
            <div
              key={change.id}
              className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                selectedChange === change.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              } ${
                currentChange !== undefined && index < currentChange
                  ? 'bg-green-50 border-green-200'
                  : currentChange === index
                  ? 'bg-yellow-50 border-yellow-200'
                  : ''
              }`}
              onClick={() => onChangeSelect(change.id)}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <span className={`w-3 h-3 rounded-full ${getChangeTypeColor(change.type)}`}></span>
                  <span className="font-medium">{change.component}</span>
                </div>
                <div className="flex items-center space-x-2">
                  {currentChange !== undefined && index < currentChange && (
                    <span className="text-green-600 text-sm">✅ Applied</span>
                  )}
                  {currentChange === index && (
                    <span className="text-yellow-600 text-sm">🔄 In Progress</span>
                  )}
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRiskColor(change.risk)}`}>
                    {change.risk}
                  </span>
                </div>
              </div>
              <p className="text-sm text-gray-600 mb-2">
                {change.type.toUpperCase()} operation
              </p>
              {change.dependencies.length > 0 && (
                <div className="text-xs text-gray-500">
                  Dependencies: {change.dependencies.join(', ')}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Change Details */}
        <div className="bg-gray-50 rounded-lg p-4">
          {selectedChangeData ? (
            <div className="space-y-4">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Change Details</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Component:</span>
                    <span className="font-medium">{selectedChangeData.component}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Type:</span>
                    <span className="font-medium capitalize">{selectedChangeData.type}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Risk Level:</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRiskColor(selectedChangeData.risk)}`}>
                      {selectedChangeData.risk}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Testing Required:</span>
                    <span className="font-medium">{selectedChangeData.testingRequired ? 'Yes' : 'No'}</span>
                  </div>
                </div>
              </div>

              {selectedChangeData.dependencies.length > 0 && (
                <div>
                  <h5 className="font-medium text-gray-900 mb-2">Dependencies</h5>
                  <ul className="text-sm text-gray-600 space-y-1">
                    {selectedChangeData.dependencies.map((dep, index) => (
                      <li key={index}>• {dep}</li>
                    ))}
                  </ul>
                </div>
              )}

              {showDiff && (
                <div>
                  <h5 className="font-medium text-gray-900 mb-2">Changes</h5>
                  <div className="bg-white border rounded p-3 text-sm font-mono">
                    <div className="text-red-600 mb-2">
                      - Before: {JSON.stringify(selectedChangeData.before, null, 2)}
                    </div>
                    <div className="text-green-600">
                      + After: {JSON.stringify(selectedChangeData.after, null, 2)}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center text-gray-500 py-8">
              Select a change to view details
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Impact Tab Component
interface ImpactTabProps {
  impact: ImpactAssessment;
}

const ImpactTab: React.FC<ImpactTabProps> = ({ impact }) => {
  return (
    <div className="space-y-6">
      {/* Impact Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-lg font-medium text-blue-900 mb-2">Affected Users</h3>
          <div className="text-2xl font-bold text-blue-600">
            {impact.affectedUsers.toLocaleString()}
          </div>
          <p className="text-sm text-blue-700">users may be impacted</p>
        </div>

        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
          <h3 className="text-lg font-medium text-orange-900 mb-2">Downtime</h3>
          <div className="text-2xl font-bold text-orange-600">
            {impact.downtime}
          </div>
          <p className="text-sm text-orange-700">minutes estimated</p>
        </div>

        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <h3 className="text-lg font-medium text-purple-900 mb-2">Rollback Time</h3>
          <div className="text-2xl font-bold text-purple-600">
            {impact.rollbackTime}
          </div>
          <p className="text-sm text-purple-700">minutes to rollback</p>
        </div>

        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-lg font-medium text-red-900 mb-2">Risk Level</h3>
          <div className={`text-2xl font-bold ${getRiskTextColor(impact.riskLevel)}`}>
            {impact.riskLevel.toUpperCase()}
          </div>
          <p className="text-sm text-red-700">overall assessment</p>
        </div>
      </div>

      {/* Scope and Dependencies */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Affected Components</h3>
          <div className="space-y-2">
            {impact.scope.map((component, index) => (
              <div key={index} className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                <span className="text-sm">{component}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Dependencies</h3>
          <div className="space-y-2">
            {impact.dependencies.map((dependency, index) => (
              <div key={index} className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-orange-400 rounded-full"></div>
                <span className="text-sm">{dependency}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Testing Requirements */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Testing Requirements</h3>
        <div className="space-y-3">
          {impact.testingRequired.map((test, index) => (
            <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded">
              <div className={`w-3 h-3 rounded-full mt-0.5 ${test.mandatory ? 'bg-red-400' : 'bg-yellow-400'}`}></div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <span className="font-medium">{test.type}</span>
                  <span className="text-sm text-gray-500">{test.estimatedTime}m</span>
                </div>
                <p className="text-sm text-gray-600 mt-1">{test.description}</p>
                {test.mandatory && (
                  <span className="text-xs text-red-600 font-medium">MANDATORY</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Business Impact */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <h3 className="text-lg font-medium text-yellow-900 mb-2">Business Impact</h3>
        <p className="text-yellow-800">{impact.businessImpact}</p>
      </div>
    </div>
  );
};

// Rollback Tab Component
interface RollbackTabProps {
  rollbackPlan: RollbackPlan;
  onExecuteRollback?: () => void;
  canExecute?: boolean;
}

const RollbackTab: React.FC<RollbackTabProps> = ({
  rollbackPlan,
  onExecuteRollback,
  canExecute = false
}) => {
  const [selectedStep, setSelectedStep] = useState<string | null>(null);

  return (
    <div className="space-y-6">
      {/* Rollback Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-lg font-medium text-blue-900 mb-2">Strategy</h3>
          <div className="text-xl font-bold text-blue-600 capitalize">
            {rollbackPlan.strategy}
          </div>
        </div>

        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
          <h3 className="text-lg font-medium text-orange-900 mb-2">Total Steps</h3>
          <div className="text-xl font-bold text-orange-600">
            {rollbackPlan.steps.length}
          </div>
        </div>

        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h3 className="text-lg font-medium text-green-900 mb-2">Estimated Time</h3>
          <div className="text-xl font-bold text-green-600">
            {rollbackPlan.estimatedTime}m
          </div>
        </div>
      </div>

      {/* Rollback Steps */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Rollback Steps</h3>
          {onExecuteRollback && (
            <button
              onClick={onExecuteRollback}
              disabled={!canExecute}
              className={`px-4 py-2 rounded-lg font-medium ${
                canExecute
                  ? 'bg-red-600 hover:bg-red-700 text-white'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }`}
            >
              Execute Rollback
            </button>
          )}
        </div>

        <div className="space-y-3">
          {rollbackPlan.steps.map((step, index) => (
            <div
              key={step.id}
              className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                selectedStep === step.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => setSelectedStep(selectedStep === step.id ? null : step.id)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-blue-600 font-medium text-sm">{step.order}</span>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">{step.description}</h4>
                    <p className="text-sm text-gray-500">Timeout: {step.timeout}s</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {step.rollbackOnFailure && (
                    <span className="text-xs bg-red-100 text-red-600 px-2 py-1 rounded">
                      Critical
                    </span>
                  )}
                  <span className="text-gray-400">
                    {selectedStep === step.id ? '▼' : '▶'}
                  </span>
                </div>
              </div>

              {selectedStep === step.id && (
                <div className="mt-4 pl-11 space-y-3">
                  {step.command && (
                    <div>
                      <h5 className="font-medium text-gray-700 mb-1">Command</h5>
                      <code className="block bg-gray-100 p-2 rounded text-sm font-mono">
                        {step.command}
                      </code>
                    </div>
                  )}
                  <div>
                    <h5 className="font-medium text-gray-700 mb-1">Validation</h5>
                    <p className="text-sm text-gray-600">{step.validation}</p>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Triggers and Data Recovery */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Rollback Triggers</h3>
          <div className="space-y-2">
            {rollbackPlan.triggers.map((trigger, index) => (
              <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <span className="text-sm font-medium">{trigger.condition}</span>
                <span className="text-sm text-gray-500">{trigger.action}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Data Recovery</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Strategy:</span>
              <span className="font-medium">{rollbackPlan.dataRecovery.strategy}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Recovery Time:</span>
              <span className="font-medium">{rollbackPlan.dataRecovery.recoveryTime}m</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Backup Location:</span>
              <span className="font-medium text-xs">{rollbackPlan.dataRecovery.backupLocation}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Validation Checks */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Post-Rollback Validation</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {rollbackPlan.validationChecks.map((check, index) => (
            <div key={index} className="flex items-center space-x-2 p-2 bg-gray-50 rounded">
              <div className="w-2 h-2 bg-green-400 rounded-full"></div>
              <span className="text-sm">{check.replace('_', ' ').toLowerCase()}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Deployment Tab Component
interface DeploymentTabProps {
  deploymentState: DeploymentState;
  updateRequest: BaselineUpdateRequest;
}

const DeploymentTab: React.FC<DeploymentTabProps> = ({
  deploymentState,
  updateRequest
}) => {
  return (
    <div className="space-y-6">
      <DeploymentProgressIndicator deploymentState={deploymentState} />

      {/* Deployment Logs */}
      <div className="bg-black text-green-400 rounded-lg p-4 font-mono text-sm max-h-96 overflow-y-auto">
        <div className="mb-2 text-green-300">Deployment Logs:</div>
        {deploymentState.logs.map((log, index) => (
          <div key={index} className="mb-1">
            <span className="text-gray-400">[{log.timestamp.toISOString()}]</span>
            <span className={`ml-2 ${getLogLevelColor(log.level)}`}>
              [{log.level.toUpperCase()}]
            </span>
            <span className="ml-2">{log.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// Deployment Progress Indicator Component
const DeploymentProgressIndicator: React.FC<{ deploymentState: DeploymentState }> = ({
  deploymentState
}) => {
  const getStatusColor = (status: DeploymentStatus): string => {
    switch (status) {
      case DeploymentStatus.COMPLETED:
        return 'text-green-600 bg-green-100';
      case DeploymentStatus.FAILED:
      case DeploymentStatus.ROLLED_BACK:
        return 'text-red-600 bg-red-100';
      case DeploymentStatus.ROLLING_BACK:
        return 'text-orange-600 bg-orange-100';
      default:
        return 'text-blue-600 bg-blue-100';
    }
  };

  const formatDate = (date: Date): string => {
    return new Intl.DateTimeFormat('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }).format(new Date(date));
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900">Deployment Progress</h3>
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(deploymentState.status)}`}>
          {deploymentState.status.replace('_', ' ').toUpperCase()}
        </span>
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="flex justify-between text-sm text-gray-600 mb-1">
          <span>Progress</span>
          <span>{deploymentState.progress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${deploymentState.progress}%` }}
          ></div>
        </div>
      </div>

      {/* Status Info */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
        <div>
          <span className="text-gray-500">Stage:</span>
          <div className="font-medium capitalize">{deploymentState.stage}</div>
        </div>
        <div>
          <span className="text-gray-500">Changes:</span>
          <div className="font-medium">{deploymentState.currentChange}/{deploymentState.totalChanges}</div>
        </div>
        <div>
          <span className="text-gray-500">Started:</span>
          <div className="font-medium">{formatDate(deploymentState.startTime)}</div>
        </div>
        <div>
          <span className="text-gray-500">Est. Complete:</span>
          <div className="font-medium">{formatDate(deploymentState.estimatedCompletion)}</div>
        </div>
      </div>

      {/* Health Checks */}
      {deploymentState.healthChecks.length > 0 && (
        <div className="mt-4">
          <h4 className="font-medium text-gray-700 mb-2">Health Checks</h4>
          <div className="space-y-2">
            {deploymentState.healthChecks.map((check, index) => (
              <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <div className="flex items-center space-x-2">
                  <span className={`w-2 h-2 rounded-full ${check.passed ? 'bg-green-400' : 'bg-red-400'}`}></span>
                  <span className="text-sm font-medium">{check.name}</span>
                </div>
                <span className="text-xs text-gray-500">{check.responseTime}ms</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Helper functions
const getChangeTypeColor = (type: ChangeType): string => {
  switch (type) {
    case 'add':
      return 'bg-green-400';
    case 'modify':
      return 'bg-blue-400';
    case 'delete':
      return 'bg-red-400';
    case 'move':
      return 'bg-purple-400';
    default:
      return 'bg-gray-400';
  }
};

const getRiskColor = (risk: RiskLevel): string => {
  switch (risk) {
    case RiskLevel.CRITICAL:
      return 'text-red-600 bg-red-100';
    case RiskLevel.HIGH:
      return 'text-orange-600 bg-orange-100';
    case RiskLevel.MEDIUM:
      return 'text-yellow-600 bg-yellow-100';
    case RiskLevel.LOW:
      return 'text-green-600 bg-green-100';
    default:
      return 'text-gray-600 bg-gray-100';
  }
};

const getRiskTextColor = (risk: RiskLevel): string => {
  switch (risk) {
    case RiskLevel.CRITICAL:
      return 'text-red-600';
    case RiskLevel.HIGH:
      return 'text-orange-600';
    case RiskLevel.MEDIUM:
      return 'text-yellow-600';
    case RiskLevel.LOW:
      return 'text-green-600';
    default:
      return 'text-gray-600';
  }
};

const getLogLevelColor = (level: string): string => {
  switch (level.toLowerCase()) {
    case 'error':
      return 'text-red-400';
    case 'warn':
      return 'text-yellow-400';
    case 'info':
      return 'text-blue-400';
    case 'debug':
      return 'text-gray-400';
    default:
      return 'text-green-400';
  }
};

export default BaselineUpdateVisualization;