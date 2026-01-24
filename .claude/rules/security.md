# Security Rules

> Mandatory security practices for all code in this workspace.

## Secrets Management

### Never Hardcode Secrets
- API keys, passwords, tokens, and credentials must NEVER appear in code
- No secrets in configuration files committed to version control
- No secrets in comments, documentation, or test fixtures

### Environment Variables
- All secrets must be loaded from environment variables
- Use `.env` files for local development (never commit these)
- Document required environment variables in `.env.example`
- Validate presence of required secrets at application startup

### Secret Detection
- Pre-commit hooks should scan for potential secrets
- Use patterns to detect: API keys, tokens, passwords, private keys
- Fail builds if secrets are detected in commits

## Input Validation

### All External Input is Untrusted
- User input (forms, query params, headers)
- API responses from external services
- File uploads and parsed data
- Environment variables (validate format)

### Validation Requirements
- Validate type, length, format, and range
- Use allowlists over denylists when possible
- Sanitize before storage and escape before output
- Reject invalid input early with clear error messages

## Injection Prevention

### SQL Injection
- Always use parameterized queries or prepared statements
- Never concatenate user input into SQL strings
- Use ORM query builders with proper escaping
- Validate and sanitize identifiers (table/column names)

### XSS Prevention
- Escape all dynamic content before HTML rendering
- Use framework-provided templating with auto-escaping
- Sanitize HTML input with allowlisted tags only
- Set Content-Security-Policy headers

### CSRF Prevention
- Include CSRF tokens in all state-changing requests
- Validate tokens server-side before processing
- Use SameSite cookie attribute (Strict or Lax)
- Verify Origin/Referer headers for sensitive operations

## Authentication & Authorization

### Authentication
- Use established libraries (never roll your own crypto)
- Enforce strong password policies
- Implement rate limiting on auth endpoints
- Use secure session management

### Authorization
- Check permissions on every request
- Implement principle of least privilege
- Validate resource ownership before access
- Log authorization failures
