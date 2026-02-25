import React from 'react';
import { Menu, Search, Bell, Settings, Moon, Sun, Wifi, WifiOff } from 'lucide-react';
import { useTheme } from '../../hooks/useTheme';
import { useWebSocket } from '../../hooks/useWebSocket';
import { ConnectionStatus } from '../common/ConnectionStatus';

interface HeaderProps {
  onMenuClick: () => void;
}

export function Header({ onMenuClick }: HeaderProps) {
  const { theme, toggleTheme } = useTheme();
  const { isConnected, connectionStatus } = useWebSocket();

  return (
    <header className="sticky top-0 z-40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b">
      <div className="flex h-16 items-center gap-4 px-4 sm:px-6 lg:px-8">
        {/* Mobile menu button */}
        <button
          onClick={onMenuClick}
          className="lg:hidden p-2 -ml-2 rounded-md hover:bg-accent transition-colors"
          aria-label="Open sidebar"
        >
          <Menu className="h-5 w-5" />
        </button>

        {/* Logo and title */}
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <div className="h-4 w-4 rounded-sm bg-primary-foreground" />
          </div>
          <div className="hidden sm:block">
            <h1 className="text-xl font-semibold text-gradient">
              Monitoring Dashboard
            </h1>
          </div>
        </div>

        {/* Search bar */}
        <div className="flex-1 max-w-md mx-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input
              type="search"
              placeholder="Search tests, alerts, metrics..."
              className="w-full h-9 pl-9 pr-4 rounded-md border border-input bg-background text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            />
          </div>
        </div>

        {/* Right side actions */}
        <div className="flex items-center gap-2">
          {/* Connection status */}
          <ConnectionStatus
            isConnected={isConnected}
            status={connectionStatus}
          />

          {/* Notifications */}
          <button
            className="relative p-2 rounded-md hover:bg-accent transition-colors"
            aria-label="Notifications"
          >
            <Bell className="h-5 w-5" />
            <span className="absolute -top-1 -right-1 h-4 w-4 rounded-full bg-destructive text-destructive-foreground text-xs flex items-center justify-center">
              3
            </span>
          </button>

          {/* Theme toggle */}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-md hover:bg-accent transition-colors"
            aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
          >
            {theme === 'light' ? (
              <Moon className="h-5 w-5" />
            ) : (
              <Sun className="h-5 w-5" />
            )}
          </button>

          {/* Settings */}
          <button
            className="p-2 rounded-md hover:bg-accent transition-colors"
            aria-label="Settings"
          >
            <Settings className="h-5 w-5" />
          </button>

          {/* User menu */}
          <div className="hidden sm:flex items-center gap-3 ml-4 pl-4 border-l">
            <div className="text-right">
              <p className="text-sm font-medium">Admin User</p>
              <p className="text-xs text-muted-foreground">admin@example.com</p>
            </div>
            <div className="h-8 w-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-sm font-medium">
              A
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}