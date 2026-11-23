# Utilities Module

General-purpose utility scripts and helper functions.

## 📁 Contents

### Command Utilities
- `list_all_commands.py` - List all available commands
- `copy_git_commands.py` - Copy git commands

### Repository Utilities
- `clean_all_repos_trunk.py` - Clean trunk branches
- `fix_agent_os_modules.py` - Fix Agent OS module issues
- `fix_problem_repos.sh` - Fix problematic repositories
- `fix_remaining_repos.sh` - Fix remaining repository issues
- `verify_enhanced_specs.py` - Verify enhanced specifications

### JavaScript Utilities
- `utils/config-validator.js` - Configuration validation
- `utils/error-handler.js` - Error handling utilities
- `utils/logger.js` - Logging utilities

## 🚀 Usage

### List All Commands
```bash
python list_all_commands.py
```

### Clean Repository Trunks
```bash
python clean_all_repos_trunk.py
```

### Verify Specifications
```bash
python verify_enhanced_specs.py
```

## 🔧 JavaScript Utilities

### Config Validator
```javascript
const validator = require('./utils/config-validator');
validator.validate(config);
```

### Error Handler
```javascript
const errorHandler = require('./utils/error-handler');
errorHandler.handle(error);
```

### Logger
```javascript
const logger = require('./utils/logger');
logger.info('Operation completed');
```

## 📋 Features

- **Command Management**: List and manage commands
- **Repository Maintenance**: Clean and fix repositories
- **Validation**: Configuration and spec validation
- **Error Handling**: Robust error management
- **Logging**: Comprehensive logging utilities

## 📝 Adding New Utilities

1. Create utility in appropriate language
2. Add clear documentation
3. Include usage examples
4. Update this README