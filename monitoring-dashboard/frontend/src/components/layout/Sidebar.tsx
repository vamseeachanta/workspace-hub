import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { X, BarChart3, TestTube, Shield, Zap, AlertTriangle, Settings, Home } from 'lucide-react';
import { cn } from '../../utils/cn';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: Home },
  { name: 'Tests', href: '/tests', icon: TestTube },
  { name: 'Coverage', href: '/coverage', icon: Shield },
  { name: 'Performance', href: '/performance', icon: Zap },
  { name: 'Alerts', href: '/alerts', icon: AlertTriangle },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const location = useLocation();

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div
        className={cn(
          'fixed top-0 left-0 z-50 h-full w-64 bg-card border-r transform transition-transform duration-200 ease-in-out lg:translate-x-0 lg:static lg:inset-0',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Header */}
        <div className="flex h-16 items-center justify-between px-6 border-b">
          <div className="flex items-center gap-3">
            <BarChart3 className="h-8 w-8 text-primary" />
            <span className="text-lg font-semibold">Monitor</span>
          </div>
          <button
            onClick={onClose}
            className="lg:hidden p-1 rounded-md hover:bg-accent transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-2">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href;
            const Icon = item.icon;

            return (
              <Link
                key={item.name}
                to={item.href}
                onClick={onClose}
                className={cn(
                  'flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                )}
              >
                <Icon className="h-5 w-5" />
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="px-6 py-4 border-t">
          <div className="text-xs text-muted-foreground">
            <div className="flex items-center justify-between mb-2">
              <span>Version</span>
              <span className="font-mono">v1.0.0</span>
            </div>
            <div className="flex items-center justify-between mb-2">
              <span>Status</span>
              <div className="flex items-center gap-1">
                <div className="h-2 w-2 bg-success rounded-full" />
                <span className="text-success">Online</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span>Uptime</span>
              <span className="font-mono">24h 15m</span>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}