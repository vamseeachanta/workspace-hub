import React, { useState, useEffect, useCallback } from 'react';
import {
  ApprovalRequest,
  ApprovalStatus,
  ApprovalPriority,
  WorkflowMetrics,
  User,
  ApprovalResponse,
  ApprovalDecision
} from '../../types/approval.types.js';

// Component interfaces
interface ApprovalDashboardProps {
  userId: string;
  userRole: string;
  onApprovalAction: (requestId: string, decision: ApprovalDecision, reason?: string) => Promise<void>;
  onRequestDetails: (requestId: string) => void;
  onCreateRequest: () => void;
}

interface DashboardStats {
  pending: number;
  approved: number;
  rejected: number;
  total: number;
  myRequests: number;
  myApprovals: number;
}

interface FilterOptions {
  status: ApprovalStatus | 'all';
  priority: ApprovalPriority | 'all';
  type: string | 'all';
  assignedToMe: boolean;
  createdByMe: boolean;
}

export const ApprovalDashboard: React.FC<ApprovalDashboardProps> = ({
  userId,
  userRole,
  onApprovalAction,
  onRequestDetails,
  onCreateRequest
}) => {
  const [requests, setRequests] = useState<ApprovalRequest[]>([]);
  const [filteredRequests, setFilteredRequests] = useState<ApprovalRequest[]>([]);
  const [stats, setStats] = useState<DashboardStats>({
    pending: 0,
    approved: 0,
    rejected: 0,
    total: 0,
    myRequests: 0,
    myApprovals: 0
  });
  const [metrics, setMetrics] = useState<WorkflowMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTab, setSelectedTab] = useState<'dashboard' | 'pending' | 'history' | 'metrics'>('dashboard');
  const [filters, setFilters] = useState<FilterOptions>({
    status: 'all',
    priority: 'all',
    type: 'all',
    assignedToMe: false,
    createdByMe: false
  });

  // Fetch data
  useEffect(() => {
    fetchApprovalData();
  }, [userId]);

  // Apply filters
  useEffect(() => {
    applyFilters();
  }, [requests, filters]);

  const fetchApprovalData = async () => {
    try {
      setLoading(true);
      setError(null);

      // These would be actual API calls
      const [requestsData, metricsData] = await Promise.all([
        fetchApprovalRequests(),
        fetchWorkflowMetrics()
      ]);

      setRequests(requestsData);
      setMetrics(metricsData);
      updateStats(requestsData);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...requests];

    if (filters.status !== 'all') {
      filtered = filtered.filter(r => r.status === filters.status);
    }

    if (filters.priority !== 'all') {
      filtered = filtered.filter(r => r.priority === filters.priority);
    }

    if (filters.type !== 'all') {
      filtered = filtered.filter(r => r.type === filters.type);
    }

    if (filters.assignedToMe) {
      filtered = filtered.filter(r =>
        r.approvers[r.currentStep]?.approvers.some(a => a.id === userId)
      );
    }

    if (filters.createdByMe) {
      filtered = filtered.filter(r => r.requester.id === userId);
    }

    setFilteredRequests(filtered);
  };

  const updateStats = (requests: ApprovalRequest[]) => {
    const stats: DashboardStats = {
      pending: requests.filter(r => r.status === ApprovalStatus.PENDING || r.status === ApprovalStatus.IN_PROGRESS).length,
      approved: requests.filter(r => r.status === ApprovalStatus.APPROVED).length,
      rejected: requests.filter(r => r.status === ApprovalStatus.REJECTED).length,
      total: requests.length,
      myRequests: requests.filter(r => r.requester.id === userId).length,
      myApprovals: requests.filter(r =>
        r.approvers[r.currentStep]?.approvers.some(a => a.id === userId)
      ).length
    };

    setStats(stats);
  };

  const handleApprovalAction = async (requestId: string, decision: ApprovalDecision, reason?: string) => {
    try {
      await onApprovalAction(requestId, decision, reason);
      await fetchApprovalData(); // Refresh data
    } catch (err) {
      setError((err as Error).message);
    }
  };

  const getPriorityColor = (priority: ApprovalPriority): string => {
    switch (priority) {
      case ApprovalPriority.CRITICAL:
        return 'text-red-600 bg-red-100';
      case ApprovalPriority.HIGH:
        return 'text-orange-600 bg-orange-100';
      case ApprovalPriority.MEDIUM:
        return 'text-yellow-600 bg-yellow-100';
      case ApprovalPriority.LOW:
        return 'text-green-600 bg-green-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusColor = (status: ApprovalStatus): string => {
    switch (status) {
      case ApprovalStatus.APPROVED:
        return 'text-green-600 bg-green-100';
      case ApprovalStatus.REJECTED:
        return 'text-red-600 bg-red-100';
      case ApprovalStatus.PENDING:
      case ApprovalStatus.IN_PROGRESS:
        return 'text-blue-600 bg-blue-100';
      case ApprovalStatus.ESCALATED:
        return 'text-purple-600 bg-purple-100';
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

  const formatDuration = (start: Date, end?: Date): string => {
    const endTime = end || new Date();
    const duration = endTime.getTime() - new Date(start).getTime();
    const hours = Math.floor(duration / (1000 * 60 * 60));
    const minutes = Math.floor((duration % (1000 * 60 * 60)) / (1000 * 60));

    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };

  // Placeholder API functions
  const fetchApprovalRequests = async (): Promise<ApprovalRequest[]> => {
    // Mock data - replace with actual API call
    return [];
  };

  const fetchWorkflowMetrics = async (): Promise<WorkflowMetrics> => {
    // Mock data - replace with actual API call
    return {
      totalRequests: 0,
      pendingRequests: 0,
      approvedRequests: 0,
      rejectedRequests: 0,
      expiredRequests: 0,
      averageApprovalTime: 0,
      approvalRate: 0,
      escalationRate: 0,
      timeByStep: {},
      userMetrics: {}
    };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex">
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error Loading Dashboard</h3>
            <div className="mt-2 text-sm text-red-700">{error}</div>
            <div className="mt-4">
              <button
                onClick={fetchApprovalData}
                className="bg-red-100 hover:bg-red-200 text-red-800 px-3 py-1 rounded text-sm"
              >
                Retry
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Approval Dashboard</h1>
        <p className="mt-2 text-gray-600">Manage approval requests and track workflow metrics</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-blue-600 font-semibold text-sm">{stats.pending}</span>
              </div>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">Pending</h3>
              <p className="text-sm text-gray-500">Awaiting approval</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                <span className="text-green-600 font-semibold text-sm">{stats.approved}</span>
              </div>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">Approved</h3>
              <p className="text-sm text-gray-500">Successfully approved</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center">
                <span className="text-orange-600 font-semibold text-sm">{stats.myApprovals}</span>
              </div>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">My Approvals</h3>
              <p className="text-sm text-gray-500">Assigned to me</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                <span className="text-purple-600 font-semibold text-sm">{stats.myRequests}</span>
              </div>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">My Requests</h3>
              <p className="text-sm text-gray-500">Created by me</p>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-gray-200 mb-8">
        <nav className="-mb-px flex space-x-8">
          {[
            { key: 'dashboard', label: 'Dashboard', icon: '📊' },
            { key: 'pending', label: 'Pending Approvals', icon: '⏳' },
            { key: 'history', label: 'History', icon: '📋' },
            { key: 'metrics', label: 'Metrics', icon: '📈' }
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setSelectedTab(tab.key as any)}
              className={`${
                selectedTab === tab.key
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2`}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {selectedTab === 'dashboard' && (
        <DashboardOverview
          requests={filteredRequests}
          stats={stats}
          metrics={metrics}
          onCreateRequest={onCreateRequest}
          onRequestDetails={onRequestDetails}
        />
      )}

      {selectedTab === 'pending' && (
        <PendingApprovals
          requests={filteredRequests.filter(r =>
            r.status === ApprovalStatus.PENDING || r.status === ApprovalStatus.IN_PROGRESS
          )}
          userId={userId}
          onApprovalAction={handleApprovalAction}
          onRequestDetails={onRequestDetails}
          filters={filters}
          onFiltersChange={setFilters}
        />
      )}

      {selectedTab === 'history' && (
        <ApprovalHistory
          requests={filteredRequests}
          onRequestDetails={onRequestDetails}
          filters={filters}
          onFiltersChange={setFilters}
        />
      )}

      {selectedTab === 'metrics' && (
        <MetricsDashboard
          metrics={metrics}
          requests={requests}
        />
      )}
    </div>
  );
};

// Dashboard Overview Component
interface DashboardOverviewProps {
  requests: ApprovalRequest[];
  stats: DashboardStats;
  metrics: WorkflowMetrics | null;
  onCreateRequest: () => void;
  onRequestDetails: (requestId: string) => void;
}

const DashboardOverview: React.FC<DashboardOverviewProps> = ({
  requests,
  stats,
  metrics,
  onCreateRequest,
  onRequestDetails
}) => {
  const recentRequests = requests
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
    .slice(0, 5);

  return (
    <div className="space-y-8">
      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="flex space-x-4">
          <button
            onClick={onCreateRequest}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium"
          >
            Create New Request
          </button>
          <button className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-md text-sm font-medium">
            Export Reports
          </button>
          <button className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-md text-sm font-medium">
            View Templates
          </button>
        </div>
      </div>

      {/* Recent Requests */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Recent Requests</h2>
          <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
            View All
          </button>
        </div>
        {recentRequests.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No recent requests</p>
        ) : (
          <div className="space-y-4">
            {recentRequests.map((request) => (
              <div
                key={request.id}
                className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer"
                onClick={() => onRequestDetails(request.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900">{request.title}</h3>
                    <p className="text-sm text-gray-500 mt-1">
                      Created by {request.requester.fullName} • {formatDate(request.createdAt)}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(request.priority)}`}>
                      {request.priority.toUpperCase()}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(request.status)}`}>
                      {request.status.replace('_', ' ').toUpperCase()}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Metrics Overview */}
      {metrics && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Performance Metrics</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">
                {Math.round(metrics.approvalRate * 100)}%
              </div>
              <div className="text-sm text-gray-500">Approval Rate</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">
                {Math.round(metrics.averageApprovalTime / (1000 * 60 * 60))}h
              </div>
              <div className="text-sm text-gray-500">Avg. Processing Time</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-600">
                {Math.round(metrics.escalationRate * 100)}%
              </div>
              <div className="text-sm text-gray-500">Escalation Rate</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Pending Approvals Component
interface PendingApprovalsProps {
  requests: ApprovalRequest[];
  userId: string;
  onApprovalAction: (requestId: string, decision: ApprovalDecision, reason?: string) => Promise<void>;
  onRequestDetails: (requestId: string) => void;
  filters: FilterOptions;
  onFiltersChange: (filters: FilterOptions) => void;
}

const PendingApprovals: React.FC<PendingApprovalsProps> = ({
  requests,
  userId,
  onApprovalAction,
  onRequestDetails,
  filters,
  onFiltersChange
}) => {
  const [selectedRequests, setSelectedRequests] = useState<string[]>([]);
  const [bulkAction, setBulkAction] = useState<ApprovalDecision | ''>('');

  const myPendingRequests = requests.filter(r =>
    r.approvers[r.currentStep]?.approvers.some(a => a.id === userId)
  );

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedRequests(myPendingRequests.map(r => r.id));
    } else {
      setSelectedRequests([]);
    }
  };

  const handleSelectRequest = (requestId: string, checked: boolean) => {
    if (checked) {
      setSelectedRequests([...selectedRequests, requestId]);
    } else {
      setSelectedRequests(selectedRequests.filter(id => id !== requestId));
    }
  };

  const handleBulkAction = async () => {
    if (!bulkAction || selectedRequests.length === 0) return;

    try {
      await Promise.all(
        selectedRequests.map(requestId =>
          onApprovalAction(requestId, bulkAction as ApprovalDecision)
        )
      );
      setSelectedRequests([]);
      setBulkAction('');
    } catch (error) {
      console.error('Bulk action failed:', error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Filters</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <select
            value={filters.priority}
            onChange={(e) => onFiltersChange({...filters, priority: e.target.value as any})}
            className="border border-gray-300 rounded-md px-3 py-2"
          >
            <option value="all">All Priorities</option>
            {Object.values(ApprovalPriority).map(priority => (
              <option key={priority} value={priority}>{priority.toUpperCase()}</option>
            ))}
          </select>

          <select
            value={filters.type}
            onChange={(e) => onFiltersChange({...filters, type: e.target.value})}
            className="border border-gray-300 rounded-md px-3 py-2"
          >
            <option value="all">All Types</option>
            <option value="baseline_update">Baseline Update</option>
            <option value="configuration_change">Configuration Change</option>
            <option value="deployment">Deployment</option>
          </select>

          <label className="flex items-center">
            <input
              type="checkbox"
              checked={filters.assignedToMe}
              onChange={(e) => onFiltersChange({...filters, assignedToMe: e.target.checked})}
              className="mr-2"
            />
            Assigned to me
          </label>

          <label className="flex items-center">
            <input
              type="checkbox"
              checked={filters.createdByMe}
              onChange={(e) => onFiltersChange({...filters, createdByMe: e.target.checked})}
              className="mr-2"
            />
            Created by me
          </label>
        </div>
      </div>

      {/* Bulk Actions */}
      {selectedRequests.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <span className="text-blue-800">
              {selectedRequests.length} request(s) selected
            </span>
            <div className="flex items-center space-x-2">
              <select
                value={bulkAction}
                onChange={(e) => setBulkAction(e.target.value as any)}
                className="border border-blue-300 rounded px-2 py-1 text-sm"
              >
                <option value="">Select Action</option>
                <option value={ApprovalDecision.APPROVE}>Approve</option>
                <option value={ApprovalDecision.REJECT}>Reject</option>
              </select>
              <button
                onClick={handleBulkAction}
                disabled={!bulkAction}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-3 py-1 rounded text-sm"
              >
                Apply
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Requests List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">
              Pending Approvals ({myPendingRequests.length})
            </h3>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={selectedRequests.length === myPendingRequests.length && myPendingRequests.length > 0}
                onChange={(e) => handleSelectAll(e.target.checked)}
                className="mr-2"
              />
              Select All
            </label>
          </div>
        </div>

        {myPendingRequests.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            No pending approvals assigned to you
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {myPendingRequests.map((request) => (
              <PendingApprovalItem
                key={request.id}
                request={request}
                userId={userId}
                isSelected={selectedRequests.includes(request.id)}
                onSelect={(checked) => handleSelectRequest(request.id, checked)}
                onApprovalAction={onApprovalAction}
                onRequestDetails={onRequestDetails}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// Individual pending approval item
interface PendingApprovalItemProps {
  request: ApprovalRequest;
  userId: string;
  isSelected: boolean;
  onSelect: (checked: boolean) => void;
  onApprovalAction: (requestId: string, decision: ApprovalDecision, reason?: string) => Promise<void>;
  onRequestDetails: (requestId: string) => void;
}

const PendingApprovalItem: React.FC<PendingApprovalItemProps> = ({
  request,
  userId,
  isSelected,
  onSelect,
  onApprovalAction,
  onRequestDetails
}) => {
  const [showActions, setShowActions] = useState(false);
  const [reason, setReason] = useState('');
  const [processing, setProcessing] = useState(false);

  const handleAction = async (decision: ApprovalDecision) => {
    setProcessing(true);
    try {
      await onApprovalAction(request.id, decision, reason);
      setShowActions(false);
      setReason('');
    } catch (error) {
      console.error('Action failed:', error);
    } finally {
      setProcessing(false);
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

  const getPriorityColor = (priority: ApprovalPriority): string => {
    switch (priority) {
      case ApprovalPriority.CRITICAL:
        return 'text-red-600 bg-red-100';
      case ApprovalPriority.HIGH:
        return 'text-orange-600 bg-orange-100';
      case ApprovalPriority.MEDIUM:
        return 'text-yellow-600 bg-yellow-100';
      case ApprovalPriority.LOW:
        return 'text-green-600 bg-green-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="p-6">
      <div className="flex items-start space-x-4">
        <input
          type="checkbox"
          checked={isSelected}
          onChange={(e) => onSelect(e.target.checked)}
          className="mt-1"
        />

        <div className="flex-1">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {request.title}
              </h3>
              <p className="text-gray-600 mb-3">
                {request.description}
              </p>
              <div className="flex items-center space-x-4 text-sm text-gray-500">
                <span>Requested by {request.requester.fullName}</span>
                <span>•</span>
                <span>{formatDate(request.createdAt)}</span>
                <span>•</span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(request.priority)}`}>
                  {request.priority.toUpperCase()}
                </span>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <button
                onClick={() => onRequestDetails(request.id)}
                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                View Details
              </button>
              <button
                onClick={() => setShowActions(!showActions)}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-sm font-medium"
              >
                Take Action
              </button>
            </div>
          </div>

          {showActions && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <div className="mb-3">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Reason (optional)
                </label>
                <textarea
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                  rows={2}
                  placeholder="Add a reason for your decision..."
                />
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleAction(ApprovalDecision.APPROVE)}
                  disabled={processing}
                  className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-4 py-2 rounded text-sm font-medium"
                >
                  {processing ? 'Processing...' : 'Approve'}
                </button>
                <button
                  onClick={() => handleAction(ApprovalDecision.REJECT)}
                  disabled={processing}
                  className="bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white px-4 py-2 rounded text-sm font-medium"
                >
                  {processing ? 'Processing...' : 'Reject'}
                </button>
                <button
                  onClick={() => setShowActions(false)}
                  className="bg-gray-300 hover:bg-gray-400 text-gray-700 px-4 py-2 rounded text-sm font-medium"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Approval History Component
interface ApprovalHistoryProps {
  requests: ApprovalRequest[];
  onRequestDetails: (requestId: string) => void;
  filters: FilterOptions;
  onFiltersChange: (filters: FilterOptions) => void;
}

const ApprovalHistory: React.FC<ApprovalHistoryProps> = ({
  requests,
  onRequestDetails,
  filters,
  onFiltersChange
}) => {
  const completedRequests = requests
    .filter(r => r.status === ApprovalStatus.APPROVED || r.status === ApprovalStatus.REJECTED)
    .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime());

  const formatDate = (date: Date): string => {
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(new Date(date));
  };

  const getStatusColor = (status: ApprovalStatus): string => {
    switch (status) {
      case ApprovalStatus.APPROVED:
        return 'text-green-600 bg-green-100';
      case ApprovalStatus.REJECTED:
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Filters</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <select
            value={filters.status}
            onChange={(e) => onFiltersChange({...filters, status: e.target.value as any})}
            className="border border-gray-300 rounded-md px-3 py-2"
          >
            <option value="all">All Status</option>
            <option value={ApprovalStatus.APPROVED}>Approved</option>
            <option value={ApprovalStatus.REJECTED}>Rejected</option>
          </select>

          <label className="flex items-center">
            <input
              type="checkbox"
              checked={filters.createdByMe}
              onChange={(e) => onFiltersChange({...filters, createdByMe: e.target.checked})}
              className="mr-2"
            />
            Created by me
          </label>

          <input
            type="date"
            className="border border-gray-300 rounded-md px-3 py-2"
            placeholder="Date range"
          />
        </div>
      </div>

      {/* History List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">
            Approval History ({completedRequests.length})
          </h3>
        </div>

        {completedRequests.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            No completed approvals found
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {completedRequests.map((request) => (
              <div key={request.id} className="p-6 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 mb-1">
                      {request.title}
                    </h4>
                    <p className="text-sm text-gray-600 mb-2">
                      {request.description}
                    </p>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span>By {request.requester.fullName}</span>
                      <span>•</span>
                      <span>Completed {formatDate(request.updatedAt)}</span>
                      <span>•</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(request.status)}`}>
                        {request.status.toUpperCase()}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={() => onRequestDetails(request.id)}
                    className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                  >
                    View Details
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// Metrics Dashboard Component
interface MetricsDashboardProps {
  metrics: WorkflowMetrics | null;
  requests: ApprovalRequest[];
}

const MetricsDashboard: React.FC<MetricsDashboardProps> = ({ metrics, requests }) => {
  if (!metrics) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-500 text-center">No metrics data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Overview Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-2xl font-bold text-blue-600">{metrics.totalRequests}</div>
          <div className="text-sm text-gray-500">Total Requests</div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-2xl font-bold text-green-600">
            {Math.round(metrics.approvalRate * 100)}%
          </div>
          <div className="text-sm text-gray-500">Approval Rate</div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-2xl font-bold text-orange-600">
            {Math.round(metrics.averageApprovalTime / (1000 * 60 * 60))}h
          </div>
          <div className="text-sm text-gray-500">Avg. Processing Time</div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-2xl font-bold text-red-600">
            {Math.round(metrics.escalationRate * 100)}%
          </div>
          <div className="text-sm text-gray-500">Escalation Rate</div>
        </div>
      </div>

      {/* Charts placeholder */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Request Trends</h3>
        <div className="h-64 bg-gray-100 rounded flex items-center justify-center">
          <p className="text-gray-500">Chart visualization would go here</p>
        </div>
      </div>

      {/* Performance by User */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Performance by User</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Total Requests
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Avg. Response Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Approval Rate
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {Object.entries(metrics.userMetrics).map(([userId, userMetric]) => (
                <tr key={userId}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {userId}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {userMetric.totalRequests}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {Math.round(userMetric.averageResponseTime / (1000 * 60))}m
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {Math.round((userMetric.approvedRequests / userMetric.totalRequests) * 100)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ApprovalDashboard;