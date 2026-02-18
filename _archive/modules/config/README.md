# Configuration Module

Central configuration files for the repository management system.

## 📁 Contents

### Package Configuration
- `package.json` - Node.js package configuration
- `package-lock.json` - Locked dependency versions

### TypeScript Configuration
- `tsconfig.json` - TypeScript compiler configuration

### Testing Configuration
- `jest.config.js` - Jest testing framework configuration

### Build Configuration
- `.babelrc` - Babel transpiler configuration

### Tool Configuration
- `.mcp.json` - MCP (Model Context Protocol) configuration
- `.pre-commit-config.yaml` - Pre-commit hook configuration
- `claude-flow` - Claude Flow configuration

## ⚙️ Configuration Overview

### Node.js Setup
```json
{
  "name": "repository-management",
  "scripts": {
    "test": "jest",
    "build": "tsc",
    "lint": "eslint"
  }
}
```

### TypeScript Settings
- Target: ES2020
- Module: CommonJS
- Strict mode enabled

### Testing
- Framework: Jest
- Coverage enabled
- Test match patterns configured

## 🚀 Usage

### Install Dependencies
```bash
npm install
```

### Run Tests
```bash
npm test
```

### Build Project
```bash
npm run build
```

## 📝 Updating Configuration

1. Edit the appropriate configuration file
2. Test changes locally
3. Commit with descriptive message
4. Update this README if adding new configs