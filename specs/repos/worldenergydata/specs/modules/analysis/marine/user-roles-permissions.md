# User Roles & Permissions Specification
## Marine Safety Incidents Database

**Document Version:** 1.0
**Last Updated:** 2025-10-03
**Status:** Draft
**Module:** Analysis > Marine Safety

---

## Table of Contents

1. [Overview](#overview)
2. [Role Definitions](#role-definitions)
3. [Permission Matrix](#permission-matrix)
4. [Role-Based Access Control (RBAC)](#role-based-access-control-rbac)
5. [Registration Workflow](#registration-workflow)
6. [API Key Management](#api-key-management)
7. [OAuth2 Scopes](#oauth2-scopes)
8. [User Lifecycle](#user-lifecycle)
9. [Audit Requirements](#audit-requirements)
10. [Multi-Tenancy](#multi-tenancy)
11. [Database Schema](#database-schema)
12. [Implementation Examples](#implementation-examples)
13. [Use Cases](#use-cases)
14. [Security Considerations](#security-considerations)

---

## Overview

### Purpose

This specification defines the comprehensive user roles, permissions, and access control mechanisms for the Marine Safety Incidents Database. It ensures secure, auditable, and flexible access management supporting various stakeholder needs from public researchers to system administrators.

### Goals

- **Security**: Implement defense-in-depth with role-based access control
- **Flexibility**: Support diverse user types and workflows
- **Auditability**: Track all access and modifications
- **Scalability**: Handle growth from individual researchers to enterprise organizations
- **Compliance**: Meet regulatory requirements for data access and privacy

### Scope

- User authentication and authorization
- Role definitions and hierarchies
- Permission matrices
- API key and OAuth2 token management
- User lifecycle management
- Audit logging
- Multi-tenancy support

---

## Role Definitions

### 1. Anonymous (Unauthenticated)

**Description**: Public users browsing the platform without authentication.

**Capabilities**:
- View public incident summaries (redacted sensitive data)
- Browse aggregate statistics and visualizations
- Access public API endpoints (rate-limited)
- View documentation and help resources

**Limitations**:
- No access to detailed incident reports
- Cannot download bulk data
- Cannot submit incidents or comments
- Strict rate limits (10 requests/minute)

**Use Cases**:
- General public browsing incident trends
- Students conducting preliminary research
- Media accessing public summaries

---

### 2. Researcher (Authenticated)

**Description**: Verified researchers from academic institutions, think tanks, or research organizations.

**Capabilities**:
- Full read access to all public incidents
- Access to detailed incident reports (excluding confidential fields)
- Download datasets in multiple formats (CSV, JSON, Parquet)
- Create saved searches and custom filters
- Generate custom reports and visualizations
- API access with increased rate limits (100 requests/minute)
- Request access to restricted datasets

**Limitations**:
- Cannot create, update, or delete incidents
- Cannot access personnel records or proprietary equipment data
- Cannot approve or curate submissions

**Registration Requirements**:
- Valid institutional email address
- ORCID iD (preferred)
- Research project description
- Affiliation verification

**Use Cases**:
- Academic research on maritime safety trends
- Statistical analysis of incident patterns
- Publication of peer-reviewed studies

---

### 3. Data Contributor (Authenticated)

**Description**: Verified personnel from maritime operators, regulatory bodies, or industry organizations authorized to submit incident reports.

**Capabilities**:
- All Researcher capabilities
- Submit new incident reports
- Update own submissions (before approval)
- Attach supporting documents (photos, diagrams, reports)
- Track submission status
- Receive notifications on submission review

**Limitations**:
- Cannot edit approved incidents
- Cannot approve or publish own submissions
- Cannot access incidents from competing organizations (optional isolation)
- Cannot delete published incidents

**Registration Requirements**:
- Organizational email verification
- Employer/organization validation
- Industry credentials verification
- Signed data sharing agreement

**Use Cases**:
- Offshore platform operators reporting incidents
- Vessel operators submitting collision reports
- Port authorities documenting spills or equipment failures

---

### 4. Curator (Authenticated + Elevated)

**Description**: Subject matter experts responsible for reviewing, enriching, and approving incident submissions.

**Capabilities**:
- All Data Contributor capabilities
- Review pending submissions
- Edit and enrich incident reports (add analysis, corrections)
- Approve or reject submissions with feedback
- Merge duplicate incidents
- Flag incidents for additional review
- Access to curation dashboard and workflow tools
- Assign incidents to other curators

**Limitations**:
- Cannot delete published incidents without Admin approval
- Cannot modify system configuration
- Cannot manage user accounts

**Appointment**:
- Nominated by Admin or existing Curator
- Requires domain expertise verification
- Background check for sensitive data access
- Training on curation standards and tools

**Use Cases**:
- Marine safety experts reviewing offshore incident reports
- Technical specialists validating equipment failure data
- Regulatory compliance officers ensuring data quality

---

### 5. Admin (System Administrator)

**Description**: System administrators with full platform access and management capabilities.

**Capabilities**:
- All Curator capabilities
- Full CRUD operations on all data
- User account management (create, modify, disable, delete)
- Role assignment and permission management
- API key generation and revocation
- System configuration and settings
- Access to audit logs and security monitoring
- Backup and data export operations
- Emergency incident takedown (with audit trail)

**Limitations**:
- Actions are fully audited
- Sensitive operations require second Admin approval (optional)
- Cannot bypass encryption or data protection mechanisms

**Appointment**:
- Designated by platform owner/organization
- Comprehensive background check
- Multi-factor authentication required
- Regular security training

**Use Cases**:
- System maintenance and configuration
- Security incident response
- User support escalations
- Compliance and audit support

---

### 6. API Service (Machine Account)

**Description**: Automated systems and services accessing the API programmatically.

**Capabilities**:
- Scoped API access based on service account configuration
- Typically read-only for analytics pipelines
- Write access for authorized data ingestion services
- Higher rate limits (1000+ requests/minute)
- Webhook and callback support

**Limitations**:
- No UI/console access
- Restricted to specific API endpoints
- Cannot perform interactive actions (approvals, curation)

**Registration**:
- Created by Admin
- Associated with organization/owner
- Defined OAuth2 scopes
- Regular key rotation enforced

**Use Cases**:
- Automated data pipelines for analytics platforms
- Integration with external safety management systems
- Real-time incident notification services
- Third-party application integrations

---

## Permission Matrix

### Comprehensive Permissions Table

| Permission | Anonymous | Researcher | Contributor | Curator | Admin | API Service |
|-----------|-----------|-----------|-------------|---------|-------|-------------|
| **Incidents** |||||||
| View public incidents | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ (scope) |
| View detailed incidents | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ (scope) |
| View restricted incidents | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ |
| Create incidents | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ (scope) |
| Update own incidents | ✗ | ✗ | ✓ (pre-approval) | ✓ | ✓ | ✓ (scope) |
| Update any incidents | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ |
| Delete incidents | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| Approve incidents | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ |
| Flag incidents | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ |
| Merge incidents | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ |
| **Data Access** |||||||
| Export CSV/JSON | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ (scope) |
| Bulk data download | ✗ | ✓ (limited) | ✓ | ✓ | ✓ | ✓ (scope) |
| Access raw data | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ |
| View deleted records | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| **User Management** |||||||
| View own profile | ✗ | ✓ | ✓ | ✓ | ✓ | N/A |
| Update own profile | ✗ | ✓ | ✓ | ✓ | ✓ | N/A |
| View other profiles | ✗ | ✗ | ✗ | ✓ (limited) | ✓ | ✗ |
| Create users | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| Modify user roles | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| Disable/delete users | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| **API Access** |||||||
| Public API endpoints | ✓ (limited) | ✓ | ✓ | ✓ | ✓ | ✓ |
| Authenticated endpoints | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Admin API endpoints | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| Generate API keys | ✗ | ✓ | ✓ | ✓ | ✓ | N/A |
| Revoke own API keys | ✗ | ✓ | ✓ | ✓ | ✓ | N/A |
| Revoke any API keys | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| **Audit & Monitoring** |||||||
| View own audit logs | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ |
| View all audit logs | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| Export audit logs | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| **System Configuration** |||||||
| View system settings | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| Modify system settings | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| Manage backups | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |

### Permission Inheritance

```
Anonymous
    ↓
Researcher
    ↓
Data Contributor
    ↓
Curator
    ↓
Admin
```

Each role inherits all permissions from roles below it in the hierarchy.

---

## Role-Based Access Control (RBAC)

### RBAC Architecture

```
User → [Roles] → [Permissions] → [Resources]
                      ↓
                 [Constraints]
```

### Permission Components

1. **Resource**: The entity being accessed (incident, user, system)
2. **Action**: The operation being performed (read, write, delete, approve)
3. **Scope**: Conditions limiting access (own records, organization, time range)
4. **Context**: Additional constraints (IP restrictions, time-based, device)

### Permission Expression Format

```
permission := <resource>:<action>[:<scope>]
```

**Examples**:
- `incidents:read:public` - Read public incidents
- `incidents:write:own` - Write own incidents
- `users:manage:*` - Manage all users
- `audit:read:organization` - Read organization audit logs

### Implementation Model

**Attribute-Based Access Control (ABAC) Extensions**:
- User attributes (role, organization, department)
- Resource attributes (sensitivity, status, owner)
- Environmental attributes (time, location, device)
- Action attributes (read, write, delete, approve)

### Decision Flow

```python
def check_permission(user, resource, action, context):
    # 1. Verify user authentication
    if not user.is_authenticated:
        return False

    # 2. Check role-based permissions
    if not has_role_permission(user.role, resource, action):
        return False

    # 3. Apply scope constraints
    if not check_scope(user, resource, action):
        return False

    # 4. Evaluate context rules
    if not evaluate_context(user, resource, action, context):
        return False

    # 5. Log access decision
    audit_log.record(user, resource, action, "GRANTED")
    return True
```

---

## Registration Workflow

### Self-Service Registration (Researcher/Contributor)

#### Step 1: Initial Registration

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant API
    participant Email
    participant DB

    User->>UI: Fill registration form
    UI->>API: POST /api/v1/auth/register
    API->>DB: Create user (status=pending)
    API->>Email: Send verification email
    Email->>User: Email with verification link
    User->>UI: Click verification link
    UI->>API: GET /api/v1/auth/verify/{token}
    API->>DB: Update user (email_verified=true)
    API->>Email: Send welcome email
```

#### Step 2: Profile Completion

**Required Fields**:
- Full name
- Email address (institutional preferred)
- Organization/Affiliation
- Country
- Role type (Researcher/Contributor)
- Research interests or contribution scope
- ORCID iD (optional for researchers)
- Professional credentials (optional)

#### Step 3: Identity Verification

**Researcher Verification**:
1. Institutional email verification
2. ORCID iD linking (auto-verifies affiliation)
3. Manual review for non-standard cases
4. Approval within 24-48 hours

**Contributor Verification**:
1. Organizational email verification
2. Employer validation (domain check + manual review)
3. Industry credentials verification
4. Signed data sharing agreement
5. Approval within 2-5 business days

#### Step 4: Account Activation

Once approved:
- User receives activation notification
- Role assigned automatically or by Admin
- API key generated (optional, user-initiated)
- Access to role-specific features enabled

### Admin-Initiated Registration (Curator/Admin)

1. Admin creates user account via admin panel
2. Initial temporary password generated
3. User receives welcome email with password reset link
4. User completes profile and sets password
5. Role and permissions assigned by Admin
6. Multi-factor authentication enforced

---

## API Key Management

### API Key Architecture

**Key Components**:
- **Key ID**: Public identifier (e.g., `msid_k_abc123xyz`)
- **Secret Key**: Private authentication token (e.g., `sk_live_...`)
- **Scopes**: OAuth2-style permission scopes
- **Expiration**: Automatic expiration date
- **Rate Limits**: Per-key rate limiting

### Key Generation

#### User-Initiated Generation

```python
# FastAPI endpoint
@router.post("/api/v1/auth/api-keys", response_model=APIKeyResponse)
async def generate_api_key(
    name: str,
    scopes: List[str],
    expires_days: int = 90,
    current_user: User = Depends(get_current_user)
):
    """
    Generate new API key for authenticated user.

    Args:
        name: Descriptive name for the key
        scopes: List of permission scopes
        expires_days: Days until expiration (max 365)
        current_user: Authenticated user from JWT

    Returns:
        APIKeyResponse with key_id and secret (shown once)
    """
    # Validate scopes against user role
    allowed_scopes = get_role_scopes(current_user.role)
    if not all(scope in allowed_scopes for scope in scopes):
        raise HTTPException(403, "Requested scopes exceed role permissions")

    # Generate secure key
    key_id = f"msid_k_{secrets.token_urlsafe(16)}"
    secret_key = f"sk_{'live' if is_production else 'test'}_{secrets.token_urlsafe(32)}"
    secret_hash = hash_secret(secret_key)  # Store only hash

    # Create database record
    api_key = APIKey(
        key_id=key_id,
        secret_hash=secret_hash,
        user_id=current_user.id,
        name=name,
        scopes=scopes,
        expires_at=datetime.utcnow() + timedelta(days=expires_days),
        created_at=datetime.utcnow(),
        last_used_at=None,
        usage_count=0
    )
    db.add(api_key)
    db.commit()

    # Audit log
    audit_log.record(
        user=current_user,
        action="api_key.create",
        resource=key_id,
        details={"name": name, "scopes": scopes}
    )

    return APIKeyResponse(
        key_id=key_id,
        secret=secret_key,  # Shown only once
        name=name,
        scopes=scopes,
        expires_at=api_key.expires_at,
        created_at=api_key.created_at,
        message="Save this secret key securely - it will not be shown again"
    )
```

#### Admin-Generated Service Keys

Admins can generate service account keys with elevated scopes:

```python
@router.post("/api/v1/admin/service-accounts/{account_id}/keys")
async def generate_service_key(
    account_id: UUID,
    scopes: List[str],
    expires_days: int = 365,
    current_user: User = Depends(require_admin)
):
    """Generate API key for service account (admin only)."""
    # Implementation similar to user key generation
    # but with service account context and elevated scopes
    pass
```

### Key Rotation

**Automated Rotation**:
- Keys expire after configured period (default 90 days)
- Email notifications sent 30/14/7/1 days before expiration
- Users can rotate keys via UI or API

**Manual Rotation**:

```python
@router.post("/api/v1/auth/api-keys/{key_id}/rotate")
async def rotate_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Rotate API key (generate new key, deprecate old).

    Returns:
        New key with same scopes and extended expiration
    """
    old_key = db.query(APIKey).filter(
        APIKey.key_id == key_id,
        APIKey.user_id == current_user.id
    ).first()

    if not old_key:
        raise HTTPException(404, "API key not found")

    # Generate new key with same configuration
    new_key = generate_api_key(
        name=f"{old_key.name} (rotated)",
        scopes=old_key.scopes,
        expires_days=90,
        current_user=current_user
    )

    # Mark old key as deprecated (allow 7-day grace period)
    old_key.status = "deprecated"
    old_key.deprecated_at = datetime.utcnow()
    old_key.expires_at = datetime.utcnow() + timedelta(days=7)
    db.commit()

    return new_key
```

### Key Revocation

```python
@router.delete("/api/v1/auth/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user)
):
    """Revoke API key immediately."""
    api_key = db.query(APIKey).filter(
        APIKey.key_id == key_id,
        APIKey.user_id == current_user.id
    ).first()

    if not api_key:
        raise HTTPException(404, "API key not found")

    api_key.status = "revoked"
    api_key.revoked_at = datetime.utcnow()
    db.commit()

    audit_log.record(
        user=current_user,
        action="api_key.revoke",
        resource=key_id
    )

    return {"message": "API key revoked successfully"}
```

### Key Usage Tracking

```python
async def track_key_usage(key_id: str, endpoint: str, response_code: int):
    """Track API key usage for analytics and rate limiting."""
    await redis.incr(f"api_key:{key_id}:usage_count")
    await redis.setex(f"api_key:{key_id}:last_used", 3600, datetime.utcnow().isoformat())

    # Update database (batched, every 100 requests or 5 minutes)
    if await redis.get(f"api_key:{key_id}:usage_count") % 100 == 0:
        db.query(APIKey).filter(APIKey.key_id == key_id).update({
            "last_used_at": datetime.utcnow(),
            "usage_count": APIKey.usage_count + 100
        })
        db.commit()
```

---

## OAuth2 Scopes

### Scope Definitions

OAuth2 scopes control granular API access. Format: `resource:action[:scope]`

#### Read Scopes

- `incidents:read` - Read all accessible incidents
- `incidents:read:public` - Read only public incidents
- `incidents:read:detailed` - Access detailed incident data
- `analytics:read` - Access analytics and statistics
- `users:read:self` - Read own user profile

#### Write Scopes

- `incidents:write` - Create and update incidents
- `incidents:write:own` - Update only own incidents
- `documents:write` - Upload supporting documents
- `comments:write` - Post comments on incidents

#### Admin Scopes

- `users:manage` - Full user management
- `incidents:approve` - Approve/reject incident submissions
- `system:configure` - System configuration access
- `audit:read` - Access audit logs

### Scope Assignment by Role

| Scope | Researcher | Contributor | Curator | Admin | Service |
|-------|-----------|-------------|---------|-------|---------|
| `incidents:read` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `incidents:read:detailed` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `incidents:write` | ✗ | ✓ | ✓ | ✓ | ✓ |
| `incidents:approve` | ✗ | ✗ | ✓ | ✓ | ✗ |
| `documents:write` | ✗ | ✓ | ✓ | ✓ | ✓ |
| `users:manage` | ✗ | ✗ | ✗ | ✓ | ✗ |
| `audit:read` | ✗ | ✗ | ✗ | ✓ | ✗ |

### Scope Validation Middleware

```python
def require_scopes(*required_scopes: str):
    """Dependency to enforce OAuth2 scopes."""
    async def validate_scopes(
        authorization: str = Header(...),
        db: Session = Depends(get_db)
    ):
        # Extract and validate API key or JWT token
        token = authorization.replace("Bearer ", "")

        # Decode token/key to get scopes
        if token.startswith("msid_k_"):
            # API key authentication
            key = db.query(APIKey).filter(APIKey.key_id == token).first()
            if not key or key.status != "active":
                raise HTTPException(401, "Invalid or inactive API key")
            granted_scopes = key.scopes
        else:
            # JWT token authentication
            payload = decode_jwt(token)
            granted_scopes = payload.get("scopes", [])

        # Check if all required scopes are granted
        if not all(scope in granted_scopes for scope in required_scopes):
            raise HTTPException(
                403,
                f"Insufficient scopes. Required: {required_scopes}, Granted: {granted_scopes}"
            )

        return granted_scopes

    return validate_scopes


# Usage in endpoints
@router.post("/api/v1/incidents")
async def create_incident(
    incident: IncidentCreate,
    scopes: List[str] = Depends(require_scopes("incidents:write"))
):
    """Create new incident (requires incidents:write scope)."""
    # Implementation
    pass
```

---

## User Lifecycle

### 1. Onboarding

#### Phase 1: Registration (Day 0)
- User completes registration form
- Email verification sent
- Temporary account created (status: `pending_verification`)

#### Phase 2: Verification (Days 0-2)
- User verifies email
- Profile completion
- Identity verification (automated + manual review)
- Account status: `pending_approval`

#### Phase 3: Approval (Days 1-5)
- Admin/automated review of credentials
- Role assignment
- Account activation
- Welcome email with getting started guide
- Account status: `active`

#### Phase 4: Activation (Day 5+)
- User logs in
- Completes onboarding tutorial
- Generates API key (optional)
- Makes first API request
- Account status: `active_engaged`

### 2. Active User Management

#### Profile Updates
- Users can update contact info, affiliation, research interests
- Email changes require re-verification
- Role change requests submitted to Admin

#### Activity Monitoring
- Track last login, API usage, contribution frequency
- Flag inactive accounts (no activity for 180 days)
- Send re-engagement emails

#### Role Progression
- Researchers can apply for Contributor status
- Active Contributors can be nominated for Curator role
- Progression tracked via contribution metrics

### 3. Role Changes

#### Promotion (e.g., Researcher → Contributor)

```python
@router.post("/api/v1/users/{user_id}/role-change")
async def request_role_change(
    user_id: UUID,
    new_role: UserRole,
    justification: str,
    current_user: User = Depends(get_current_user)
):
    """Request role change (requires approval)."""
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(403, "Can only request role change for yourself")

    # Create role change request
    request = RoleChangeRequest(
        user_id=user_id,
        current_role=current_user.role,
        requested_role=new_role,
        justification=justification,
        status="pending",
        requested_at=datetime.utcnow()
    )
    db.add(request)
    db.commit()

    # Notify admins
    notify_admins(f"Role change requested: {current_user.email} → {new_role}")

    return {"message": "Role change request submitted for review"}
```

#### Demotion/Restriction
- Admin-initiated
- Requires justification and audit trail
- User notified with explanation
- Restricted permissions take effect immediately

### 4. Offboarding

#### Voluntary Account Closure

```python
@router.delete("/api/v1/users/me")
async def close_account(
    current_user: User = Depends(get_current_user)
):
    """Close user account (soft delete)."""
    # Anonymize personal data
    current_user.email = f"deleted_{current_user.id}@example.com"
    current_user.full_name = "Deleted User"
    current_user.status = "closed"
    current_user.closed_at = datetime.utcnow()

    # Revoke all API keys
    db.query(APIKey).filter(APIKey.user_id == current_user.id).update({
        "status": "revoked",
        "revoked_at": datetime.utcnow()
    })

    # Preserve contributions (disassociate from user)
    # Incidents remain but attributed to "Former Contributor"

    db.commit()
    audit_log.record(current_user, "account.close", "self-initiated")

    return {"message": "Account closed successfully"}
```

#### Involuntary Suspension
- Admin-initiated
- Reasons: policy violation, security concerns, inactivity
- User notified with reason and appeal process
- Soft delete with option to reinstate

#### Data Retention
- **User data**: Anonymized after 30 days of account closure
- **Contributions**: Preserved indefinitely (public research value)
- **Audit logs**: Retained for 7 years (compliance)
- **API keys**: Revoked immediately, records retained for 1 year

---

## Audit Requirements

### Audit Logging Scope

**All Access Events**:
- User login/logout
- API authentication (key/token usage)
- Data access (read operations on sensitive resources)
- Data modifications (create, update, delete)
- Permission changes (role assignments, scope changes)
- System configuration changes
- Failed authentication attempts
- Access denials (insufficient permissions)

### Audit Log Schema

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_id UUID REFERENCES users(id),
    api_key_id VARCHAR(255),
    action VARCHAR(100) NOT NULL,  -- e.g., 'incident.read', 'user.update'
    resource_type VARCHAR(50) NOT NULL,  -- e.g., 'incident', 'user', 'api_key'
    resource_id VARCHAR(255),
    old_value JSONB,  -- For update/delete operations
    new_value JSONB,  -- For create/update operations
    ip_address INET,
    user_agent TEXT,
    request_id UUID,  -- Correlate with application logs
    status VARCHAR(20) NOT NULL,  -- 'success', 'failure', 'denied'
    error_message TEXT,
    metadata JSONB,  -- Additional context

    -- Indexes for common queries
    INDEX idx_audit_user_timestamp (user_id, timestamp DESC),
    INDEX idx_audit_action_timestamp (action, timestamp DESC),
    INDEX idx_audit_resource (resource_type, resource_id),
    INDEX idx_audit_timestamp (timestamp DESC)
);

-- Partition by month for performance
CREATE TABLE audit_logs_y2025m10 PARTITION OF audit_logs
    FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');
```

### Audit Logging Implementation

```python
class AuditLogger:
    """Centralized audit logging service."""

    @staticmethod
    async def log(
        user: Optional[User],
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        old_value: Optional[dict] = None,
        new_value: Optional[dict] = None,
        status: str = "success",
        error_message: Optional[str] = None,
        request: Optional[Request] = None
    ):
        """Log audit event."""
        log_entry = AuditLog(
            timestamp=datetime.utcnow(),
            user_id=user.id if user else None,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_value=old_value,
            new_value=new_value,
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None,
            request_id=request.state.request_id if request else None,
            status=status,
            error_message=error_message
        )

        db.add(log_entry)

        # Async write to avoid blocking (use background task)
        await background_tasks.add_task(db.commit)

        # Also log to application logger for real-time monitoring
        logger.info(
            f"AUDIT: {action} by {user.email if user else 'anonymous'} "
            f"on {resource_type}:{resource_id} - {status}"
        )


# Middleware to automatically log all requests
@app.middleware("http")
async def audit_middleware(request: Request, call_next):
    """Log all authenticated requests."""
    request.state.request_id = str(uuid.uuid4())

    # Get user from JWT token or API key
    user = await get_current_user_from_request(request)

    # Process request
    response = await call_next(request)

    # Log audit entry for sensitive endpoints
    if should_audit(request.url.path):
        await AuditLogger.log(
            user=user,
            action=f"{request.method.lower()}.{get_resource_from_path(request.url.path)}",
            resource_type=get_resource_type(request.url.path),
            resource_id=get_resource_id(request.url.path),
            status="success" if response.status_code < 400 else "failure",
            request=request
        )

    return response
```

### Change Tracking

For data modifications, track before/after states:

```python
@router.put("/api/v1/incidents/{incident_id}")
async def update_incident(
    incident_id: UUID,
    update: IncidentUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update incident with full audit trail."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(404, "Incident not found")

    # Capture old state
    old_state = {
        "title": incident.title,
        "description": incident.description,
        "severity": incident.severity,
        # ... other fields
    }

    # Apply updates
    for field, value in update.dict(exclude_unset=True).items():
        setattr(incident, field, value)

    incident.updated_at = datetime.utcnow()
    incident.updated_by = current_user.id
    db.commit()

    # Capture new state
    new_state = {
        "title": incident.title,
        "description": incident.description,
        "severity": incident.severity,
        # ... other fields
    }

    # Audit log
    await AuditLogger.log(
        user=current_user,
        action="incident.update",
        resource_type="incident",
        resource_id=str(incident_id),
        old_value=old_state,
        new_value=new_state,
        status="success"
    )

    return incident
```

### Audit Log Retention

- **Active logs**: 90 days in primary database (hot storage)
- **Archive**: 2-7 years in compressed archival storage
- **Compliance**: Meet regulatory requirements (GDPR, HIPAA equivalent for marine data)
- **Backup**: Replicated to separate audit-only database

### Audit Log Access

```python
@router.get("/api/v1/admin/audit-logs")
async def get_audit_logs(
    user_id: Optional[UUID] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(require_admin)
):
    """Retrieve audit logs (admin only)."""
    query = db.query(AuditLog)

    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)

    total = query.count()
    logs = query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "logs": logs
    }
```

---

## Multi-Tenancy

### Organization-Based Isolation (Optional)

For deployments supporting multiple organizations (e.g., multiple offshore operators):

#### Organization Model

```sql
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    type VARCHAR(50),  -- 'operator', 'regulator', 'research_institution'
    domain VARCHAR(255),  -- Email domain for auto-assignment
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);

CREATE TABLE organization_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,  -- 'member', 'admin', 'owner'
    joined_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(organization_id, user_id)
);

-- Link incidents to organizations
ALTER TABLE incidents ADD COLUMN organization_id UUID REFERENCES organizations(id);
CREATE INDEX idx_incidents_organization ON incidents(organization_id);
```

#### Access Isolation Levels

1. **No Isolation**: All users see all incidents (default for research database)
2. **View Isolation**: Users only see own organization's incidents
3. **Write Isolation**: Users can only create/modify own organization's incidents
4. **Complete Isolation**: Separate database schemas per organization

#### Row-Level Security (RLS)

```sql
-- PostgreSQL Row-Level Security example
ALTER TABLE incidents ENABLE ROW LEVEL SECURITY;

-- Researchers can see all public incidents
CREATE POLICY researcher_read_policy ON incidents
    FOR SELECT
    TO researcher_role
    USING (status = 'published');

-- Contributors can see own organization's incidents
CREATE POLICY contributor_org_policy ON incidents
    FOR ALL
    TO contributor_role
    USING (
        organization_id IN (
            SELECT organization_id
            FROM organization_memberships
            WHERE user_id = current_user_id()
        )
    );

-- Admins can see everything
CREATE POLICY admin_all_policy ON incidents
    FOR ALL
    TO admin_role
    USING (true);
```

#### Multi-Tenancy in API

```python
def get_current_organization(
    current_user: User = Depends(get_current_user)
) -> Organization:
    """Get user's primary organization."""
    membership = db.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == current_user.id,
        OrganizationMembership.role.in_(['admin', 'owner'])
    ).first()

    if not membership:
        raise HTTPException(403, "User not associated with an organization")

    return membership.organization


@router.get("/api/v1/incidents")
async def list_incidents(
    current_user: User = Depends(get_current_user)
):
    """List incidents (org-scoped for contributors)."""
    query = db.query(Incident)

    # Apply organization filter for non-admin roles
    if current_user.role in ['contributor', 'data_contributor']:
        user_org_ids = [m.organization_id for m in current_user.memberships]
        query = query.filter(Incident.organization_id.in_(user_org_ids))
    elif current_user.role == 'researcher':
        # Researchers see published incidents only
        query = query.filter(Incident.status == 'published')
    # Admins and curators see everything

    return query.all()
```

---

## Database Schema

### Core User Management Tables

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    password_hash VARCHAR(255),  -- NULL for SSO users
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'researcher',
    status VARCHAR(50) DEFAULT 'pending_verification',
    organization VARCHAR(255),
    country VARCHAR(100),
    orcid_id VARCHAR(19),  -- Format: 0000-0001-2345-6789
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login_at TIMESTAMPTZ,
    email_verification_token VARCHAR(255),
    email_verification_expires_at TIMESTAMPTZ,
    password_reset_token VARCHAR(255),
    password_reset_expires_at TIMESTAMPTZ,
    metadata JSONB,

    CHECK (role IN ('anonymous', 'researcher', 'contributor', 'curator', 'admin', 'service')),
    CHECK (status IN ('pending_verification', 'pending_approval', 'active', 'suspended', 'closed'))
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_organization ON users(organization);

-- API Keys table
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key_id VARCHAR(255) UNIQUE NOT NULL,  -- Public key ID
    secret_hash VARCHAR(255) NOT NULL,  -- Hashed secret
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    scopes TEXT[] NOT NULL,  -- Array of OAuth2 scopes
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    last_used_at TIMESTAMPTZ,
    deprecated_at TIMESTAMPTZ,
    revoked_at TIMESTAMPTZ,
    usage_count INTEGER DEFAULT 0,
    rate_limit_per_minute INTEGER DEFAULT 100,
    metadata JSONB,

    CHECK (status IN ('active', 'deprecated', 'revoked', 'expired'))
);

CREATE INDEX idx_api_keys_key_id ON api_keys(key_id);
CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_api_keys_status ON api_keys(status);

-- Roles table (for RBAC)
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    permissions TEXT[],  -- Array of permission strings
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Seed default roles
INSERT INTO roles (name, display_name, description, permissions) VALUES
('researcher', 'Researcher', 'Academic or industry researcher', ARRAY[
    'incidents:read', 'incidents:read:detailed', 'analytics:read',
    'users:read:self', 'export:data'
]),
('contributor', 'Data Contributor', 'Submit and manage incident reports', ARRAY[
    'incidents:read', 'incidents:read:detailed', 'incidents:write',
    'incidents:write:own', 'documents:write', 'analytics:read'
]),
('curator', 'Curator', 'Review and approve submissions', ARRAY[
    'incidents:read', 'incidents:write', 'incidents:approve',
    'incidents:merge', 'documents:write', 'analytics:read', 'users:read'
]),
('admin', 'Administrator', 'Full system access', ARRAY[
    'incidents:*', 'users:*', 'audit:*', 'system:*'
]);

-- User-Role assignments (for complex RBAC with multiple roles)
CREATE TABLE user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMPTZ DEFAULT NOW(),
    assigned_by UUID REFERENCES users(id),
    expires_at TIMESTAMPTZ,  -- Optional: time-limited role

    UNIQUE(user_id, role_id)
);

-- Role change requests
CREATE TABLE role_change_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    current_role VARCHAR(50) NOT NULL,
    requested_role VARCHAR(50) NOT NULL,
    justification TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    requested_at TIMESTAMPTZ DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ,
    reviewed_by UUID REFERENCES users(id),
    review_notes TEXT,

    CHECK (status IN ('pending', 'approved', 'rejected', 'withdrawn'))
);

-- Audit logs (as defined earlier)
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_id UUID REFERENCES users(id),
    api_key_id VARCHAR(255),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(255),
    old_value JSONB,
    new_value JSONB,
    ip_address INET,
    user_agent TEXT,
    request_id UUID,
    status VARCHAR(20) NOT NULL,
    error_message TEXT,
    metadata JSONB
);

CREATE INDEX idx_audit_user_timestamp ON audit_logs(user_id, timestamp DESC);
CREATE INDEX idx_audit_action_timestamp ON audit_logs(action, timestamp DESC);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp DESC);

-- Organizations (for multi-tenancy)
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    type VARCHAR(50),
    domain VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);

CREATE TABLE organization_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    joined_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(organization_id, user_id)
);

-- OAuth2 tokens (for third-party integrations)
CREATE TABLE oauth_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    client_id VARCHAR(255) NOT NULL,
    access_token VARCHAR(255) UNIQUE NOT NULL,
    refresh_token VARCHAR(255) UNIQUE,
    scopes TEXT[],
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    revoked_at TIMESTAMPTZ
);

CREATE INDEX idx_oauth_access_token ON oauth_tokens(access_token);
CREATE INDEX idx_oauth_refresh_token ON oauth_tokens(refresh_token);
```

---

## Implementation Examples

### 1. Role-Based Endpoint Protection

```python
from functools import wraps
from fastapi import HTTPException, Depends

def require_role(*allowed_roles: str):
    """Decorator to enforce role-based access."""
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required roles: {allowed_roles}"
            )
        return current_user
    return role_checker


# Usage
@router.post("/api/v1/incidents")
async def create_incident(
    incident: IncidentCreate,
    current_user: User = Depends(require_role('contributor', 'curator', 'admin'))
):
    """Create incident - requires contributor role or higher."""
    pass


@router.post("/api/v1/incidents/{incident_id}/approve")
async def approve_incident(
    incident_id: UUID,
    current_user: User = Depends(require_role('curator', 'admin'))
):
    """Approve incident - requires curator role or higher."""
    pass
```

### 2. Permission-Based Access Control

```python
class PermissionChecker:
    """Fine-grained permission checking."""

    ROLE_PERMISSIONS = {
        'researcher': [
            'incidents:read', 'incidents:read:detailed',
            'analytics:read', 'export:data'
        ],
        'contributor': [
            'incidents:read', 'incidents:write:own',
            'documents:write', 'analytics:read'
        ],
        'curator': [
            'incidents:read', 'incidents:write', 'incidents:approve',
            'incidents:merge', 'users:read'
        ],
        'admin': ['*']  # All permissions
    }

    @staticmethod
    def has_permission(user: User, permission: str) -> bool:
        """Check if user has specific permission."""
        if user.role == 'admin':
            return True  # Admins have all permissions

        user_permissions = PermissionChecker.ROLE_PERMISSIONS.get(user.role, [])

        # Check exact match
        if permission in user_permissions:
            return True

        # Check wildcard permissions (e.g., 'incidents:*')
        for perm in user_permissions:
            if perm.endswith(':*'):
                prefix = perm.rsplit(':', 1)[0]
                if permission.startswith(prefix):
                    return True

        return False

    @staticmethod
    def require_permission(permission: str):
        """Dependency to enforce specific permission."""
        async def check(current_user: User = Depends(get_current_user)):
            if not PermissionChecker.has_permission(current_user, permission):
                raise HTTPException(
                    status_code=403,
                    detail=f"Missing required permission: {permission}"
                )
            return current_user
        return check


# Usage
@router.delete("/api/v1/incidents/{incident_id}")
async def delete_incident(
    incident_id: UUID,
    current_user: User = Depends(
        PermissionChecker.require_permission('incidents:delete')
    )
):
    """Delete incident - requires explicit permission."""
    pass
```

### 3. API Key Authentication Middleware

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user_from_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Authenticate user via API key."""
    token = credentials.credentials

    # Check if token is API key (starts with msid_k_)
    if token.startswith('msid_k_'):
        # API key authentication
        api_key = db.query(APIKey).filter(
            APIKey.key_id == token,
            APIKey.status == 'active',
            APIKey.expires_at > datetime.utcnow()
        ).first()

        if not api_key:
            raise HTTPException(401, "Invalid or expired API key")

        # Verify secret hash (compare with hashed secret from request)
        # Note: In practice, both key_id and secret should be in Authorization header

        # Update usage tracking
        api_key.last_used_at = datetime.utcnow()
        api_key.usage_count += 1
        db.commit()

        # Get associated user
        user = db.query(User).filter(User.id == api_key.user_id).first()
        if not user or user.status != 'active':
            raise HTTPException(401, "User account inactive")

        # Attach API key scopes to user context
        user.api_scopes = api_key.scopes

        return user

    else:
        # JWT token authentication
        return await get_current_user_from_jwt(token, db)


async def get_current_user_from_jwt(token: str, db: Session) -> User:
    """Authenticate user via JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(401, "Invalid token")
    except JWTError:
        raise HTTPException(401, "Invalid token")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None or user.status != 'active':
        raise HTTPException(401, "User not found or inactive")

    return user


# Unified authentication dependency
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from API key or JWT token."""
    return await get_current_user_from_api_key(credentials, db)
```

### 4. Rate Limiting by Role

```python
from fastapi_limiter.depends import RateLimiter

# Define rate limits by role
RATE_LIMITS = {
    'anonymous': '10/minute',
    'researcher': '100/minute',
    'contributor': '200/minute',
    'curator': '500/minute',
    'admin': '1000/minute',
    'service': '5000/minute'
}

def get_rate_limiter(current_user: Optional[User] = None):
    """Get rate limiter based on user role."""
    role = current_user.role if current_user else 'anonymous'
    limit = RATE_LIMITS.get(role, '10/minute')
    return RateLimiter(times=int(limit.split('/')[0]), seconds=60)


@router.get("/api/v1/incidents")
async def list_incidents(
    current_user: Optional[User] = Depends(get_current_user),
    rate_limiter = Depends(get_rate_limiter)
):
    """List incidents with role-based rate limiting."""
    pass
```

---

## Use Cases

### Use Case 1: Researcher Workflow

**Persona**: Dr. Sarah Chen, Marine Safety Researcher at MIT

**Scenario**: Analyzing offshore platform incident trends for publication

#### Step 1: Registration
1. Dr. Chen visits the Marine Safety Database website
2. Clicks "Register as Researcher"
3. Fills form with MIT email (schen@mit.edu), ORCID iD, research description
4. Receives email verification link
5. Clicks link to verify email
6. Account moves to "pending_approval"

#### Step 2: Approval (Automated)
1. System detects MIT domain → trusted institution
2. ORCID iD verification confirms affiliation
3. Auto-approval within 5 minutes
4. Welcome email sent with getting started guide

#### Step 3: First API Request
1. Dr. Chen logs in to web interface
2. Navigates to API section
3. Generates API key with scopes:
   - `incidents:read`
   - `incidents:read:detailed`
   - `analytics:read`
   - `export:data`
4. Key generated: `msid_k_abc123xyz` / `sk_live_secret123...`
5. Saves secret in password manager

#### Step 4: Data Analysis
```python
import requests

API_BASE = "https://api.marine-safety-db.org/v1"
API_KEY = "sk_live_secret123..."

# Get all offshore platform incidents in 2024
response = requests.get(
    f"{API_BASE}/incidents",
    headers={"Authorization": f"Bearer {API_KEY}"},
    params={
        "asset_type": "offshore_platform",
        "incident_date_start": "2024-01-01",
        "incident_date_end": "2024-12-31",
        "limit": 1000
    }
)

incidents = response.json()

# Export to CSV for analysis
response = requests.post(
    f"{API_BASE}/export/csv",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={"incident_ids": [inc["id"] for inc in incidents["data"]]}
)

with open("platform_incidents_2024.csv", "wb") as f:
    f.write(response.content)
```

#### Step 5: Publication Credit
Dr. Chen cites the database:
> "Data sourced from Marine Safety Incidents Database (https://marine-safety-db.org), accessed October 2025."

---

### Use Case 2: Curator Approval Process

**Persona**: James Wilson, Senior Maritime Safety Officer at BSEE

**Scenario**: Reviewing and approving submitted incident reports

#### Step 1: Curator Onboarding
1. Admin creates curator account for James
2. James receives invitation email
3. Sets password and completes profile
4. Completes mandatory curator training module
5. Account activated with curator role

#### Step 2: Daily Review Workflow
1. James logs into curator dashboard
2. Sees 5 pending submissions in queue
3. Opens first incident: "Gas Release on Platform Alpha"

#### Step 3: Incident Review
**Submission Details**:
- Submitted by: operator_user@platformalpha.com (Contributor role)
- Asset: Platform Alpha (GoM)
- Incident Type: Gas Release
- Date: 2025-09-28
- Severity: Medium
- Status: Pending Approval

**James's Actions**:
1. Reads detailed description
2. Reviews attached photos and incident report PDF
3. Cross-references with internal BSEE records
4. Enriches data:
   - Adds regulatory reference: "CFR 250.1928"
   - Corrects equipment classification
   - Adds technical analysis notes
5. Approves incident for publication

```python
# Curator API workflow
import requests

CURATOR_API_KEY = "sk_live_curator_secret..."

# Get pending incidents
response = requests.get(
    f"{API_BASE}/curator/incidents/pending",
    headers={"Authorization": f"Bearer {CURATOR_API_KEY}"}
)

pending = response.json()["data"]

# Review first incident
incident_id = pending[0]["id"]

# Enrich incident data
requests.patch(
    f"{API_BASE}/incidents/{incident_id}",
    headers={"Authorization": f"Bearer {CURATOR_API_KEY}"},
    json={
        "regulatory_reference": "CFR 250.1928",
        "equipment_classification": "High-Pressure Separator",
        "curator_notes": "Cross-referenced with BSEE incident #2025-0928-GA. Confirmed timeline and cause."
    }
)

# Approve for publication
requests.post(
    f"{API_BASE}/curator/incidents/{incident_id}/approve",
    headers={"Authorization": f"Bearer {CURATOR_API_KEY}"},
    json={
        "approved": True,
        "approval_notes": "Data verified and enriched. Ready for publication."
    }
)
```

#### Step 4: Audit Trail
System logs:
```
2025-10-03 14:23:15 | jwilson@bsee.gov | curator.incident.review | incident:abc-123 | SUCCESS
2025-10-03 14:25:42 | jwilson@bsee.gov | curator.incident.update | incident:abc-123 | SUCCESS
2025-10-03 14:26:10 | jwilson@bsee.gov | curator.incident.approve | incident:abc-123 | SUCCESS
```

#### Step 5: Notification
- Contributor receives email: "Your submission has been approved and published"
- Incident appears in public database
- Researchers can now access the enriched data

---

## Security Considerations

### 1. Password Security
- **Hashing**: bcrypt or Argon2id with high work factor
- **Minimum strength**: 12 characters, complexity requirements
- **Password reset**: Time-limited tokens, email verification
- **MFA**: Required for Admin and Curator roles

### 2. API Key Security
- **Format**: Prefix-based (`msid_k_` for key ID, `sk_live_` for secret)
- **Storage**: Only hash stored in database
- **Transmission**: HTTPS only, never in URLs
- **Rotation**: Enforced every 90 days with grace period
- **Revocation**: Immediate effect, no caching

### 3. Session Management
- **JWT tokens**: Short-lived (15 minutes) with refresh tokens
- **Refresh tokens**: Long-lived (7 days), stored securely
- **Token binding**: IP address and user-agent validation (optional)
- **Logout**: Invalidate refresh tokens

### 4. Input Validation
- **SQL injection**: Parameterized queries, ORM usage
- **XSS**: Output encoding, Content-Security-Policy headers
- **CSRF**: Token-based protection for state-changing operations

### 5. Rate Limiting
- **Per-role limits**: As defined in rate limits table
- **Burst allowance**: Short-term burst handling
- **DDoS protection**: Cloudflare or similar
- **Adaptive throttling**: Slow down suspicious patterns

### 6. Data Privacy
- **PII minimization**: Collect only necessary personal data
- **Encryption**: At rest (database) and in transit (TLS 1.3)
- **Anonymization**: For closed accounts after 30 days
- **Access logs**: Audit all PII access

### 7. Third-Party Integrations
- **OAuth2**: Standard protocol for external integrations
- **Scope limitation**: Principle of least privilege
- **Token expiration**: Short-lived access tokens
- **Webhook verification**: HMAC signatures

### 8. Infrastructure Security
- **Database**: PostgreSQL with SSL, encrypted backups
- **API**: FastAPI with security middleware
- **Hosting**: Cloud platform with DDoS protection
- **Monitoring**: Real-time security alerts

---

## Appendix: Quick Reference

### API Endpoints Summary

| Endpoint | Method | Role Required | Description |
|----------|--------|---------------|-------------|
| `/auth/register` | POST | None | User registration |
| `/auth/login` | POST | None | User login (JWT) |
| `/auth/verify/{token}` | GET | None | Email verification |
| `/auth/api-keys` | POST | Authenticated | Generate API key |
| `/auth/api-keys/{id}` | DELETE | Authenticated | Revoke API key |
| `/incidents` | GET | Researcher+ | List incidents |
| `/incidents` | POST | Contributor+ | Create incident |
| `/incidents/{id}` | PUT | Contributor+ (own) / Curator+ (any) | Update incident |
| `/curator/incidents/pending` | GET | Curator+ | List pending submissions |
| `/curator/incidents/{id}/approve` | POST | Curator+ | Approve incident |
| `/admin/users` | GET | Admin | List users |
| `/admin/users/{id}/role` | PUT | Admin | Change user role |
| `/admin/audit-logs` | GET | Admin | View audit logs |

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/marine_safety

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# API Key Configuration
API_KEY_EXPIRY_DAYS=90
API_KEY_SECRET_LENGTH=32

# Email Configuration
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=notifications@marine-safety-db.org
SMTP_PASSWORD=smtp-password

# Rate Limiting
REDIS_URL=redis://localhost:6379

# Security
ALLOWED_HOSTS=api.marine-safety-db.org,localhost
CORS_ORIGINS=https://marine-safety-db.org,http://localhost:3000

# Feature Flags
ENABLE_MULTI_TENANCY=false
REQUIRE_ORCID_FOR_RESEARCHERS=false
AUTO_APPROVE_TRUSTED_DOMAINS=true
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-03 | System Architect | Initial comprehensive specification |

---

**End of Specification**
