import React, { useEffect, useState } from 'react';
import { useQuery } from 'react-query';
import { Play, Pause, CheckCircle, XCircle, Clock, RotateCcw } from 'lucide-react';
import { useWebSocket } from '../../hooks/useWebSocket';
import { formatDuration } from '../../utils/formatters';

interface TestExecution {
  id: string;
  name: string;
  suite: string;
  status: 'pending' | 'running' | 'passed' | 'failed' | 'skipped';
  duration: number;
  startTime: string;
  endTime?: string;
  error?: string;
}

async function fetchRecentTests(): Promise<TestExecution[]> {
  const response = await fetch('/api/tests?limit=10&page=1');
  if (!response.ok) {
    throw new Error('Failed to fetch recent tests');
  }
  return response.json().then(data => data.data.tests);
}

export function TestExecutionMonitor() {
  const [realtimeTests, setRealtimeTests] = useState<TestExecution[]>([]);
  const { isConnected } = useWebSocket();

  const { data: tests, isLoading } = useQuery(
    'recent-tests',
    fetchRecentTests,
    {
      refetchInterval: 5000,
    }
  );

  // Simulate real-time test updates
  useEffect(() => {
    if (!isConnected) return;

    const interval = setInterval(() => {
      // Simulate a new test execution
      const mockTest: TestExecution = {
        id: `test-${Date.now()}`,
        name: `Test Case ${Math.floor(Math.random() * 1000)}`,
        suite: ['Authentication', 'API', 'UI', 'Database'][Math.floor(Math.random() * 4)],
        status: 'running',
        duration: 0,
        startTime: new Date().toISOString(),
      };

      setRealtimeTests(prev => [mockTest, ...prev.slice(0, 4)]);

      // Complete the test after a random delay
      setTimeout(() => {
        const completed: TestExecution = {
          ...mockTest,
          status: Math.random() > 0.2 ? 'passed' : 'failed',
          duration: Math.floor(Math.random() * 5000) + 500,
          endTime: new Date().toISOString(),
          error: Math.random() > 0.8 ? 'Assertion failed: Expected true but got false' : undefined,
        };

        setRealtimeTests(prev =>
          prev.map(test => test.id === mockTest.id ? completed : test)
        );
      }, Math.random() * 3000 + 1000);
    }, Math.random() * 2000 + 3000);

    return () => clearInterval(interval);
  }, [isConnected]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <RotateCcw className="h-4 w-4 animate-spin text-info" />;
      case 'passed':
        return <CheckCircle className="h-4 w-4 text-success" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-error" />;
      case 'skipped':
        return <Clock className="h-4 w-4 text-warning" />;
      case 'pending':
      default:
        return <Pause className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const getStatusBadge = (status: string) => {
    return (
      <span className={`status-badge status-${status}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const allTests = [...realtimeTests, ...(tests || [])].slice(0, 10);

  if (isLoading) {
    return (
      <div className="dashboard-card">
        <div className="flex items-center justify-center h-48">
          <div className="loading-spinner" />
          <span className="ml-2 text-muted-foreground">Loading test executions...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Real-time Test Execution</h3>
        <div className="flex items-center gap-2">
          {isConnected && (
            <div className="flex items-center gap-1 text-success text-sm">
              <div className="pulse-dot" />
              Live
            </div>
          )}
          <span className="text-sm text-muted-foreground">
            {allTests.length} recent executions
          </span>
        </div>
      </div>

      <div className="space-y-3">
        {allTests.map((test) => (
          <div
            key={test.id}
            className={`p-3 rounded-lg border transition-all duration-200 ${
              test.status === 'running' ? 'bg-accent/50 animate-pulse-slow' : 'bg-card'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {getStatusIcon(test.status)}
                <div>
                  <p className="font-medium text-sm">{test.name}</p>
                  <p className="text-xs text-muted-foreground">{test.suite}</p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                {getStatusBadge(test.status)}

                <div className="text-right text-xs text-muted-foreground">
                  {test.status === 'running' ? (
                    <span className="text-info font-medium">Running...</span>
                  ) : (
                    <span>{formatDuration(test.duration)}</span>
                  )}
                  <div className="mt-1">
                    {new Date(test.startTime).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            </div>

            {test.error && (
              <div className="mt-2 p-2 bg-error/10 border border-error/20 rounded text-xs text-error">
                {test.error}
              </div>
            )}
          </div>
        ))}

        {allTests.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            <Play className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p>No recent test executions</p>
          </div>
        )}
      </div>

      <div className="mt-4 pt-4 border-t">
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">
            Tests running: {allTests.filter(t => t.status === 'running').length}
          </span>
          <span className="text-muted-foreground">
            Pass rate: {allTests.length > 0 ?
              Math.round((allTests.filter(t => t.status === 'passed').length / allTests.filter(t => t.status !== 'running' && t.status !== 'pending').length) * 100)
              : 0}%
          </span>
        </div>
      </div>
    </div>
  );
}