# Security Policy

## 🔒 Repository Security Guidelines

This is a **shared development repository** used across multiple teams. Security is our top priority.

## ⚠️ Critical Security Rules

### NEVER Commit:
- API keys, tokens, or credentials
- SSH keys or certificates
- Database passwords or connection strings
- Cloud provider credentials (AWS, Azure, GCP)
- Personal or customer data
- Production configuration files
- Private keys or certificates

### Before Every Commit:
1. Review your changes: `git diff --staged`
2. Check for secrets: `git secrets --scan` (if installed)
3. Verify no personal data is included
4. Ensure all credentials are in environment variables

## 🛡️ Security Best Practices

### For Teams:
- Use environment variables for all secrets
- Store credentials in secure vaults (e.g., HashiCorp Vault, AWS Secrets Manager)
- Rotate credentials regularly
- Use `.env.example` files to document required variables (without values)
- Keep personal workspaces separate from shared code

### Protected Patterns:
The `.gitignore` file automatically excludes:
- All files with extensions: `.key`, `.pem`, `.cert`
- All `.env` files and variants
- Directories: `secrets/`, `credentials/`, `private/`, `.ssh/`
- Files matching: `*_secret*`, `*_token*`, `*_api_key*`
- Personal configurations: `my-*`, `local-*`, `personal-*`
- AI memory states: `.claude/`, `.hive-mind/`, `memory/`

## 🚨 Incident Response

If you accidentally commit sensitive data:

1. **DO NOT PANIC** - Act quickly but carefully
2. **DO NOT** force push to main branch
3. **Immediately**:
   - Rotate the exposed credential
   - Create a new branch to fix the issue
   - Use `git filter-branch` or BFG Repo-Cleaner to remove from history
   - Contact the security team
   - Document the incident

## 📋 Security Checklist

Before pushing code:
- [ ] No hardcoded credentials
- [ ] No production URLs with embedded auth
- [ ] No customer data or PII
- [ ] No internal network information
- [ ] No private keys or certificates
- [ ] All secrets in environment variables
- [ ] `.env.example` updated if new variables added

## 🔍 Scanning Tools

Recommended security scanning tools:
- **git-secrets**: Prevents commits with secrets
- **gitleaks**: Detect and prevent secrets in git repos
- **trufflehog**: Search for secrets in repositories
- **GitHub Secret Scanning**: Automatic detection (enabled on this repo)

## 📞 Contact

For security concerns or incidents:
- Create a private security advisory in this repository
- Or contact the repository maintainers directly

## 🤝 Shared Responsibility

Security is everyone's responsibility. When working in this shared repository:
- Be vigilant about what you commit
- Review teammates' PRs for security issues
- Report concerns immediately
- Keep your local development environment secure

---

**Remember**: This repository is PUBLIC. Everything you commit will be visible to the world.