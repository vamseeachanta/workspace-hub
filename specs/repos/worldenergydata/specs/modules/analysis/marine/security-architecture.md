# Security Architecture Specification
## Marine Safety Incidents Database

> **Document Version:** 1.0.0
> **Last Updated:** 2025-10-03
> **Status:** Production-Ready
> **Owner:** Security Architecture Team

---

## 1. Authentication Methods

### 1.1 API Key Authentication

**Primary Authentication Mechanism** for service-to-service and automated access.

#### Implementation Specifications

```yaml
api_key_structure:
  format: "msid_[environment]_[32_char_alphanumeric]"
  example: "msid_prod_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
  environments:
    - dev: "msid_dev_*"
    - staging: "msid_stg_*"
    - production: "msid_prod_*"

api_key_storage:
  algorithm: "bcrypt"
  work_factor: 12
  salt_rounds: 10

api_key_transmission:
  header: "X-API-Key"
  alternative_header: "Authorization: ApiKey [key]"
  query_param: "DISABLED" # Security best practice
```

#### API Key Management

**Generation Process:**
```python
# Pseudocode for API key generation
def generate_api_key(environment: str, user_id: str) -> tuple:
    """
    Generate cryptographically secure API key
    Returns: (plain_key, hashed_key, key_id)
    """
    prefix = f"msid_{environment}_"
    random_bytes = secrets.token_urlsafe(24)  # 32 chars base64url
    plain_key = prefix + random_bytes

    # Hash for storage
    salt = bcrypt.gensalt(rounds=12)
    hashed_key = bcrypt.hashpw(plain_key.encode(), salt)

    # Generate unique key ID
    key_id = uuid.uuid4()

    return (plain_key, hashed_key, key_id)
```

**Key Rotation Policy:**
- **Mandatory rotation:** Every 90 days
- **Emergency rotation:** Within 1 hour of suspected compromise
- **Deprecation period:** 7 days for planned rotation
- **Notification:** 14 days advance notice for scheduled rotation

**Key Revocation:**
```sql
-- API key revocation tracking
CREATE TABLE api_key_revocations (
    key_id UUID PRIMARY KEY,
    revoked_at TIMESTAMP NOT NULL DEFAULT NOW(),
    revoked_by UUID NOT NULL,
    reason TEXT NOT NULL,
    replaced_by_key_id UUID,
    FOREIGN KEY (revoked_by) REFERENCES users(id)
);

CREATE INDEX idx_key_revocations_revoked_at ON api_key_revocations(revoked_at);
```

### 1.2 OAuth 2.0 Authentication

**For Interactive User Applications** requiring delegated access.

#### OAuth 2.0 Flow Configuration

```yaml
oauth_configuration:
  authorization_server: "https://auth.marinesafety.gov"
  token_endpoint: "https://auth.marinesafety.gov/oauth/token"
  authorization_endpoint: "https://auth.marinesafety.gov/oauth/authorize"

  supported_flows:
    - authorization_code: "RECOMMENDED"
    - client_credentials: "ENABLED"
    - refresh_token: "ENABLED"
    - implicit: "DISABLED" # Security best practice
    - password: "DISABLED" # Security best practice

  token_lifetime:
    access_token: 3600 # 1 hour
    refresh_token: 2592000 # 30 days
    authorization_code: 300 # 5 minutes

  pkce:
    required: true
    supported_methods: ["S256"]

  scopes:
    - "incidents:read" # Read incident data
    - "incidents:write" # Submit incidents
    - "statistics:read" # Access aggregated statistics
    - "export:data" # Export data
    - "admin:users" # User management (restricted)
```

#### Authorization Code Flow Example

```http
# Step 1: Authorization Request
GET /oauth/authorize?
  response_type=code&
  client_id=client123&
  redirect_uri=https://app.example.com/callback&
  scope=incidents:read statistics:read&
  state=random_state_string&
  code_challenge=PKCE_challenge&
  code_challenge_method=S256

# Step 2: Token Exchange
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
code=AUTH_CODE&
redirect_uri=https://app.example.com/callback&
client_id=client123&
client_secret=secret&
code_verifier=PKCE_verifier

# Response
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "refresh_token_here",
  "scope": "incidents:read statistics:read"
}
```

### 1.3 JWT Token Authentication

**JSON Web Token** structure for stateless authentication.

#### JWT Configuration

```yaml
jwt_configuration:
  algorithm: "RS256" # RSA Signature with SHA-256
  issuer: "https://api.marinesafety.gov"
  audience: "marine-safety-api"

  key_management:
    private_key_storage: "Hardware Security Module (HSM)"
    public_key_endpoint: "https://api.marinesafety.gov/.well-known/jwks.json"
    key_rotation: "Every 180 days"

  token_structure:
    header:
      alg: "RS256"
      typ: "JWT"
      kid: "key-id-2025-10"

    payload:
      iss: "https://api.marinesafety.gov"
      sub: "user_id_or_client_id"
      aud: "marine-safety-api"
      exp: 1728000000 # Unix timestamp
      iat: 1727996400 # Issued at
      nbf: 1727996400 # Not before
      jti: "unique_token_id" # Prevents replay attacks

      # Custom claims
      scope: ["incidents:read", "statistics:read"]
      role: "analyst"
      organization_id: "org_123"

  validation_rules:
    - verify_signature: true
    - verify_expiration: true
    - verify_issuer: true
    - verify_audience: true
    - check_revocation: true # Against revocation list
    - max_age: 3600 # 1 hour
```

#### JWT Validation Implementation

```python
# Pseudocode for JWT validation
def validate_jwt(token: str) -> dict:
    """
    Validate JWT token with comprehensive checks
    Raises: AuthenticationError on validation failure
    """
    try:
        # Decode header to get key ID
        header = jwt.get_unverified_header(token)
        kid = header['kid']

        # Fetch public key from JWKS endpoint
        public_key = fetch_public_key(kid)

        # Verify and decode token
        payload = jwt.decode(
            token,
            public_key,
            algorithms=['RS256'],
            audience='marine-safety-api',
            issuer='https://api.marinesafety.gov',
            options={
                'verify_signature': True,
                'verify_exp': True,
                'verify_iat': True,
                'verify_aud': True,
                'verify_iss': True,
                'require_exp': True,
                'require_iat': True
            }
        )

        # Check revocation list
        if is_token_revoked(payload['jti']):
            raise AuthenticationError("Token has been revoked")

        # Verify token age
        token_age = current_timestamp() - payload['iat']
        if token_age > 3600:
            raise AuthenticationError("Token is too old")

        return payload

    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError as e:
        raise AuthenticationError(f"Invalid token: {str(e)}")
```

---

## 2. Authorization & User Roles (RBAC)

### 2.1 Role-Based Access Control Model

**Hierarchical RBAC** with role inheritance and permission aggregation.

#### Role Definitions

```yaml
roles:
  public_viewer:
    description: "Public access to aggregated statistics and anonymized data"
    inherits: []
    permissions:
      - "incidents:read:public"
      - "statistics:read:aggregated"
      - "metadata:read"
    data_access:
      - aggregated_statistics
      - anonymized_incident_summaries
      - public_reports
    restrictions:
      - no_pii_access
      - rate_limited: 100 requests/hour

  registered_user:
    description: "Authenticated users with basic analysis capabilities"
    inherits: ["public_viewer"]
    permissions:
      - "incidents:read:detailed"
      - "incidents:search:advanced"
      - "export:csv"
      - "reports:generate:standard"
    data_access:
      - detailed_incident_records
      - historical_data
      - trend_analysis
    restrictions:
      - bulk_export_limited: 10000 records/day

  analyst:
    description: "Data analysts conducting research and pattern analysis"
    inherits: ["registered_user"]
    permissions:
      - "incidents:read:full"
      - "statistics:compute:custom"
      - "export:bulk"
      - "reports:generate:advanced"
      - "api:advanced_queries"
    data_access:
      - complete_incident_database
      - raw_investigation_data
      - equipment_failure_details
      - personnel_qualifications (anonymized)
    restrictions:
      - must_agree_to_research_terms
      - attribution_required

  investigator:
    description: "Official investigators with PII access"
    inherits: ["analyst"]
    permissions:
      - "incidents:read:pii"
      - "incidents:write:comments"
      - "incidents:update:status"
      - "contacts:read"
      - "documents:upload"
    data_access:
      - full_incident_records_with_pii
      - personnel_identifiable_information
      - witness_statements
      - confidential_documents
    restrictions:
      - government_verified_identity
      - certified_investigator_credentials
      - audit_all_pii_access

  compliance_officer:
    description: "Regulatory compliance monitoring and enforcement"
    inherits: ["investigator"]
    permissions:
      - "compliance:read:all"
      - "violations:create"
      - "violations:update"
      - "enforcement:actions:read"
      - "reports:generate:compliance"
    data_access:
      - violation_tracking
      - enforcement_history
      - regulatory_citations
      - facility_compliance_records
    restrictions:
      - agency_verification_required
      - jurisdiction_limited

  data_administrator:
    description: "Database management and data quality"
    inherits: ["analyst"]
    permissions:
      - "incidents:update:all"
      - "incidents:merge"
      - "incidents:delete:duplicate"
      - "data_quality:manage"
      - "schema:read"
    data_access:
      - data_quality_metrics
      - duplicate_detection
      - schema_metadata
    restrictions:
      - no_pii_modification_without_audit
      - changes_require_justification

  security_administrator:
    description: "Security management and audit review"
    inherits: []
    permissions:
      - "users:read:all"
      - "audit_logs:read:all"
      - "security:manage"
      - "keys:revoke"
      - "access:grant"
      - "access:revoke"
    data_access:
      - audit_logs
      - security_events
      - authentication_logs
      - user_activity
    restrictions:
      - two_factor_authentication_required
      - privileged_access_management

  system_administrator:
    description: "Full system access for maintenance and operations"
    inherits: ["security_administrator", "data_administrator"]
    permissions:
      - "system:*" # All system permissions
    data_access:
      - all_data
      - system_configuration
      - infrastructure_logs
    restrictions:
      - multi_factor_authentication_required
      - all_actions_logged
      - emergency_access_only
```

### 2.2 Permissions Matrix

| Resource | Public | Registered | Analyst | Investigator | Compliance | Data Admin | Sec Admin | Sys Admin |
|----------|--------|------------|---------|--------------|------------|------------|-----------|-----------|
| **Incidents (Aggregated)** | R | R | R | R | R | R | R | RWD |
| **Incidents (Detailed)** | - | R | R | R | R | R | R | RWD |
| **Incidents (PII)** | - | - | - | R | R | - | - | RWD |
| **Statistics (Public)** | R | R | R | R | R | R | R | RWD |
| **Advanced Analytics** | - | - | R | R | R | R | - | RWD |
| **Export (Small)** | - | R | R | R | R | R | - | RWD |
| **Export (Bulk)** | - | - | R | R | R | R | - | RWD |
| **Investigation Documents** | - | - | - | R | R | - | - | RWD |
| **Compliance Records** | - | - | - | - | R | - | - | RWD |
| **User Management** | - | - | - | - | - | - | RW | RWD |
| **Audit Logs** | - | - | - | - | - | - | R | RWD |
| **System Configuration** | - | - | - | - | - | - | - | RWD |

**Legend:** R=Read, W=Write, D=Delete, -=No Access

### 2.3 Dynamic Authorization Rules

**Attribute-Based Access Control (ABAC)** for context-sensitive authorization.

```yaml
dynamic_authorization_rules:

  incident_jurisdiction:
    description: "Investigators can only access incidents in their jurisdiction"
    rule: |
      IF user.role == 'investigator' AND
         incident.state NOT IN user.authorized_states THEN
           DENY ACCESS

  time_based_access:
    description: "Sensitive data only accessible during business hours"
    rule: |
      IF data.sensitivity == 'high' AND
         current_time NOT BETWEEN 08:00 AND 18:00 AND
         user.role NOT IN ['system_administrator'] THEN
           REQUIRE additional_authorization

  data_age_restriction:
    description: "PII automatically redacted after retention period"
    rule: |
      IF incident.date < (current_date - 7 YEARS) AND
         user.role NOT IN ['compliance_officer', 'system_administrator'] THEN
           REDACT PII fields

  export_volume_limits:
    description: "Daily export limits based on role"
    rule: |
      IF user.daily_export_count > user.role.max_daily_exports THEN
           DENY EXPORT AND NOTIFY security_team

  concurrent_session_limits:
    description: "Prevent credential sharing"
    rule: |
      IF user.active_sessions > user.role.max_concurrent_sessions THEN
           TERMINATE oldest_session AND LOG security_event
```

### 2.4 Permission Implementation

```sql
-- Database schema for RBAC
CREATE TABLE roles (
    role_id UUID PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    inherits_from UUID[], -- Array of parent role IDs
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE permissions (
    permission_id UUID PRIMARY KEY,
    resource VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    scope VARCHAR(50) DEFAULT 'all',
    description TEXT,
    UNIQUE(resource, action, scope)
);

CREATE TABLE role_permissions (
    role_id UUID NOT NULL,
    permission_id UUID NOT NULL,
    granted_at TIMESTAMP NOT NULL DEFAULT NOW(),
    granted_by UUID NOT NULL,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(role_id),
    FOREIGN KEY (permission_id) REFERENCES permissions(permission_id)
);

CREATE TABLE user_roles (
    user_id UUID NOT NULL,
    role_id UUID NOT NULL,
    granted_at TIMESTAMP NOT NULL DEFAULT NOW(),
    granted_by UUID NOT NULL,
    expires_at TIMESTAMP,
    conditions JSONB, -- Dynamic authorization attributes
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
);

CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX idx_user_roles_expires_at ON user_roles(expires_at);
CREATE INDEX idx_role_permissions_role_id ON role_permissions(role_id);

-- Function to get all permissions for a user (including inherited)
CREATE OR REPLACE FUNCTION get_user_permissions(p_user_id UUID)
RETURNS TABLE(resource VARCHAR, action VARCHAR, scope VARCHAR) AS $$
WITH RECURSIVE role_hierarchy AS (
    -- Base case: direct user roles
    SELECT ur.role_id, r.inherits_from
    FROM user_roles ur
    JOIN roles r ON ur.role_id = r.role_id
    WHERE ur.user_id = p_user_id
      AND (ur.expires_at IS NULL OR ur.expires_at > NOW())

    UNION

    -- Recursive case: inherited roles
    SELECT unnest(r.inherits_from), r2.inherits_from
    FROM role_hierarchy rh
    JOIN roles r ON rh.role_id = r.role_id
    JOIN roles r2 ON r2.role_id = ANY(r.inherits_from)
)
SELECT DISTINCT p.resource, p.action, p.scope
FROM role_hierarchy rh
JOIN role_permissions rp ON rh.role_id = rp.role_id
JOIN permissions p ON rp.permission_id = p.permission_id;
$$ LANGUAGE SQL STABLE;
```

---

## 3. API Security

### 3.1 HTTPS/TLS Configuration

**Transport Layer Security** requirements and configuration.

```yaml
tls_configuration:
  minimum_version: "TLS 1.3"
  supported_versions:
    - "TLS 1.3" # REQUIRED
    - "TLS 1.2" # Allowed for legacy compatibility

  cipher_suites_tls13:
    - "TLS_AES_256_GCM_SHA384"
    - "TLS_AES_128_GCM_SHA256"
    - "TLS_CHACHA20_POLY1305_SHA256"

  cipher_suites_tls12:
    - "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384"
    - "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256"
    - "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256"

  certificate_configuration:
    type: "RSA"
    key_size: 4096
    signature_algorithm: "SHA-384"
    certificate_authority: "DigiCert or Let's Encrypt"

    certificate_chain:
      - leaf_certificate: "*.marinesafety.gov"
      - intermediate_certificate: "DigiCert SHA2 Secure Server CA"
      - root_certificate: "DigiCert Global Root CA"

    validity_period: 365 days
    renewal_window: 30 days before expiration

  hsts_configuration:
    enabled: true
    max_age: 31536000 # 1 year
    include_subdomains: true
    preload: true

  certificate_transparency:
    enabled: true
    ct_logs: ["Google Argon2021", "Cloudflare Nimbus2021"]

  ocsp_stapling:
    enabled: true
    cache_duration: 3600 # 1 hour
```

#### Nginx TLS Configuration Example

```nginx
# /etc/nginx/conf.d/api-marinesafety.conf

server {
    listen 443 ssl http2;
    server_name api.marinesafety.gov;

    # TLS Certificate Configuration
    ssl_certificate /etc/ssl/certs/marinesafety.crt;
    ssl_certificate_key /etc/ssl/private/marinesafety.key;
    ssl_trusted_certificate /etc/ssl/certs/ca-chain.crt;

    # TLS Protocol Configuration
    ssl_protocols TLSv1.3 TLSv1.2;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'TLS_AES_256_GCM_SHA384:TLS_AES_128_GCM_SHA256:TLS_CHACHA20_POLY1305_SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256';

    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;

    # Session Configuration
    ssl_session_cache shared:SSL:50m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;

    # HSTS Header
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

    # Disable HTTP downgrade
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://api-backend:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name api.marinesafety.gov;
    return 301 https://$server_name$request_uri;
}
```

### 3.2 Rate Limiting

**Comprehensive rate limiting** to prevent abuse and ensure availability.

```yaml
rate_limiting_tiers:

  public_anonymous:
    requests_per_minute: 10
    requests_per_hour: 100
    requests_per_day: 1000
    burst_allowance: 5
    response_headers: true

  public_authenticated:
    requests_per_minute: 30
    requests_per_hour: 500
    requests_per_day: 5000
    burst_allowance: 10
    response_headers: true

  registered_user:
    requests_per_minute: 100
    requests_per_hour: 2000
    requests_per_day: 20000
    burst_allowance: 20

  analyst:
    requests_per_minute: 300
    requests_per_hour: 10000
    requests_per_day: 100000
    burst_allowance: 50

  investigator:
    requests_per_minute: 500
    requests_per_hour: 20000
    requests_per_day: 200000
    burst_allowance: 100

  system_integration:
    requests_per_minute: 1000
    requests_per_hour: 50000
    requests_per_day: 500000
    burst_allowance: 200

rate_limit_algorithms:
  algorithm: "Token Bucket with Sliding Window"

  implementation:
    storage: "Redis"
    key_format: "ratelimit:{endpoint}:{identifier}:{window}"

  sliding_window_log:
    enabled: true
    precision: "per_second"

  distributed_rate_limiting:
    enabled: true
    synchronization: "Redis Pub/Sub"

  response_headers:
    X-RateLimit-Limit: "Maximum requests allowed"
    X-RateLimit-Remaining: "Requests remaining in current window"
    X-RateLimit-Reset: "Unix timestamp when limit resets"
    Retry-After: "Seconds until limit resets (on 429 responses)"

endpoint_specific_limits:
  "/api/v1/incidents/search":
    requests_per_minute: 20 # More expensive query

  "/api/v1/incidents/export":
    requests_per_hour: 10 # Bulk export limitation

  "/api/v1/statistics/compute":
    requests_per_minute: 5 # Computationally intensive

  "/api/v1/auth/token":
    requests_per_minute: 5 # Prevent brute force
    requests_per_hour: 20

rate_limit_bypass:
  whitelist:
    - "Internal monitoring systems"
    - "Emergency response systems"
    - "Government agency integrations"

  bypass_header: "X-RateLimit-Bypass-Token"
  bypass_token_validation: "HMAC-SHA256 signature"
```

#### Rate Limiting Implementation

```python
# Pseudocode for token bucket rate limiting with Redis

class TokenBucketRateLimiter:
    def __init__(self, redis_client, rate_limit_config):
        self.redis = redis_client
        self.config = rate_limit_config

    def check_rate_limit(self, identifier: str, endpoint: str) -> dict:
        """
        Check if request is within rate limit
        Returns: {allowed: bool, limit: int, remaining: int, reset: int}
        """
        # Get endpoint-specific config or default
        config = self.config.get(endpoint, self.config['default'])

        # Check multiple time windows
        windows = {
            'minute': {'limit': config['requests_per_minute'], 'ttl': 60},
            'hour': {'limit': config['requests_per_hour'], 'ttl': 3600},
            'day': {'limit': config['requests_per_day'], 'ttl': 86400}
        }

        for window_name, window_config in windows.items():
            key = f"ratelimit:{endpoint}:{identifier}:{window_name}"

            # Get current count
            current_count = self.redis.get(key)
            if current_count is None:
                current_count = 0
            else:
                current_count = int(current_count)

            # Check limit
            if current_count >= window_config['limit']:
                ttl = self.redis.ttl(key)
                return {
                    'allowed': False,
                    'limit': window_config['limit'],
                    'remaining': 0,
                    'reset': int(time.time()) + ttl,
                    'window': window_name
                }

        # Increment all counters atomically
        pipe = self.redis.pipeline()
        for window_name, window_config in windows.items():
            key = f"ratelimit:{endpoint}:{identifier}:{window_name}"
            pipe.incr(key)
            pipe.expire(key, window_config['ttl'])
        pipe.execute()

        # Return success
        return {
            'allowed': True,
            'limit': config['requests_per_minute'],
            'remaining': config['requests_per_minute'] - (current_count + 1),
            'reset': int(time.time()) + 60
        }

# Middleware implementation
def rate_limit_middleware(request):
    """Rate limiting middleware for API requests"""

    # Identify requester
    if request.headers.get('X-API-Key'):
        identifier = get_api_key_owner(request.headers['X-API-Key'])
    elif request.headers.get('Authorization'):
        identifier = get_jwt_subject(request.headers['Authorization'])
    else:
        identifier = request.remote_addr

    # Check rate limit
    rate_limit_result = rate_limiter.check_rate_limit(
        identifier=identifier,
        endpoint=request.path
    )

    # Add rate limit headers
    response.headers['X-RateLimit-Limit'] = rate_limit_result['limit']
    response.headers['X-RateLimit-Remaining'] = rate_limit_result['remaining']
    response.headers['X-RateLimit-Reset'] = rate_limit_result['reset']

    # Block if exceeded
    if not rate_limit_result['allowed']:
        response.headers['Retry-After'] = rate_limit_result['reset'] - int(time.time())
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": f"Too many requests in {rate_limit_result['window']} window",
                "retry_after": rate_limit_result['reset']
            }
        )

    return next_handler(request)
```

### 3.3 CORS (Cross-Origin Resource Sharing)

**Cross-origin policy** for web application security.

```yaml
cors_configuration:

  allowed_origins:
    production:
      - "https://marinesafety.gov"
      - "https://www.marinesafety.gov"
      - "https://dashboard.marinesafety.gov"
      - "https://analytics.marinesafety.gov"

    development:
      - "http://localhost:3000"
      - "http://localhost:8080"
      - "http://127.0.0.1:3000"

  allowed_methods:
    - "GET"
    - "POST"
    - "PUT"
    - "DELETE"
    - "OPTIONS"
    - "PATCH"

  allowed_headers:
    - "Content-Type"
    - "Authorization"
    - "X-API-Key"
    - "X-Request-ID"
    - "X-Correlation-ID"

  exposed_headers:
    - "X-RateLimit-Limit"
    - "X-RateLimit-Remaining"
    - "X-RateLimit-Reset"
    - "X-Total-Count"
    - "X-Page-Number"
    - "X-Page-Size"

  credentials: true
  max_age: 86400 # 24 hours

  preflight_optimization:
    cache_preflight: true
    cache_duration: 86400

# CORS middleware configuration
cors_middleware:
  strict_mode: true
  validate_origin: true
  reject_invalid_origin: true

  origin_validation:
    method: "whitelist" # or "regex"
    case_sensitive: false
    allow_subdomains: false
```

### 3.4 Request Signing

**HMAC-based request signing** for integrity verification.

```yaml
request_signing:

  algorithm: "HMAC-SHA256"

  signature_components:
    - http_method
    - request_uri
    - query_string (sorted)
    - request_body (for POST/PUT/PATCH)
    - timestamp
    - nonce

  signature_headers:
    signature: "X-Signature"
    timestamp: "X-Timestamp"
    nonce: "X-Nonce"
    algorithm: "X-Signature-Algorithm"

  timestamp_validation:
    max_clock_skew: 300 # 5 minutes
    require_timestamp: true

  nonce_validation:
    enabled: true
    storage: "Redis"
    ttl: 900 # 15 minutes
    cache_key_format: "nonce:{api_key}:{nonce}"

  signature_format:
    encoding: "base64"
    example: "X-Signature: SHA256=base64_encoded_signature"
```

#### Request Signing Implementation

```python
# Pseudocode for request signature generation and validation

import hmac
import hashlib
import base64
import time
from urllib.parse import urlencode

def generate_request_signature(
    api_key: str,
    api_secret: str,
    method: str,
    uri: str,
    query_params: dict,
    body: str,
    timestamp: int,
    nonce: str
) -> str:
    """
    Generate HMAC-SHA256 signature for API request
    """
    # Sort query parameters
    sorted_query = urlencode(sorted(query_params.items()))

    # Build canonical string
    canonical_string = "\n".join([
        method.upper(),
        uri,
        sorted_query,
        body or "",
        str(timestamp),
        nonce
    ])

    # Generate HMAC-SHA256 signature
    signature = hmac.new(
        api_secret.encode('utf-8'),
        canonical_string.encode('utf-8'),
        hashlib.sha256
    ).digest()

    # Base64 encode
    signature_b64 = base64.b64encode(signature).decode('utf-8')

    return f"SHA256={signature_b64}"

def validate_request_signature(request, api_secret: str) -> bool:
    """
    Validate incoming request signature
    """
    # Extract signature components
    provided_signature = request.headers.get('X-Signature')
    timestamp = int(request.headers.get('X-Timestamp'))
    nonce = request.headers.get('X-Nonce')

    # Validate timestamp (prevent replay attacks)
    current_time = int(time.time())
    if abs(current_time - timestamp) > 300:  # 5 minutes
        raise SecurityError("Request timestamp outside acceptable window")

    # Validate nonce uniqueness
    nonce_key = f"nonce:{request.api_key}:{nonce}"
    if redis.exists(nonce_key):
        raise SecurityError("Nonce has already been used (replay attack)")

    # Store nonce with TTL
    redis.setex(nonce_key, 900, "1")  # 15 minutes

    # Generate expected signature
    expected_signature = generate_request_signature(
        api_key=request.api_key,
        api_secret=api_secret,
        method=request.method,
        uri=request.path,
        query_params=request.query_params,
        body=request.body,
        timestamp=timestamp,
        nonce=nonce
    )

    # Constant-time comparison
    return hmac.compare_digest(expected_signature, provided_signature)

# Example request with signature
"""
POST /api/v1/incidents/search HTTP/1.1
Host: api.marinesafety.gov
Content-Type: application/json
X-API-Key: msid_prod_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
X-Timestamp: 1728000000
X-Nonce: unique_random_value_12345
X-Signature: SHA256=k7jVf8Hs3Pm9Ld2Nx6Qw1Rt4Yz5...
X-Signature-Algorithm: HMAC-SHA256

{"incident_type": "collision", "year": 2024}
"""
```

---

## 4. Data Protection

### 4.1 Encryption at Rest

**Database and file system encryption** specifications.

```yaml
encryption_at_rest:

  database_encryption:
    method: "Transparent Data Encryption (TDE)"
    algorithm: "AES-256-GCM"

    postgresql_configuration:
      encryption_method: "pgcrypto"
      key_management: "AWS KMS" # or "HashiCorp Vault"

      encrypted_columns:
        - personnel_name: "PII"
        - personnel_ssn: "PII - Sensitive"
        - contact_email: "PII"
        - contact_phone: "PII"
        - witness_statement: "Confidential"
        - investigation_notes: "Confidential"
        - medical_records: "PHI"

      encryption_implementation: |
        -- Example: Encrypting sensitive columns
        CREATE TABLE personnel (
            personnel_id UUID PRIMARY KEY,
            name_encrypted BYTEA NOT NULL,
            ssn_encrypted BYTEA NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );

        -- Insert with encryption
        INSERT INTO personnel (personnel_id, name_encrypted, ssn_encrypted)
        VALUES (
            gen_random_uuid(),
            pgp_sym_encrypt('John Doe', 'encryption_key_from_kms'),
            pgp_sym_encrypt('123-45-6789', 'encryption_key_from_kms')
        );

        -- Query with decryption (requires key)
        SELECT
            personnel_id,
            pgp_sym_decrypt(name_encrypted, 'encryption_key_from_kms') AS name,
            pgp_sym_decrypt(ssn_encrypted, 'encryption_key_from_kms') AS ssn
        FROM personnel
        WHERE personnel_id = 'uuid';

    full_database_encryption:
      method: "LUKS volume encryption"
      algorithm: "AES-XTS-Plain64-256"
      key_derivation: "PBKDF2-SHA512"

  file_storage_encryption:
    uploaded_documents:
      encryption: "Server-side encryption"
      algorithm: "AES-256-GCM"
      key_per_file: true

    s3_configuration:
      encryption_type: "SSE-KMS" # Server-Side Encryption with KMS
      kms_key_id: "arn:aws:kms:us-east-1:123456789:key/uuid"
      bucket_policy_enforcement: true

  backup_encryption:
    method: "AES-256-CBC"
    encryption_before_transfer: true
    encrypted_backup_storage: true

  key_management:
    kms_provider: "AWS KMS" # or "HashiCorp Vault", "Azure Key Vault"

    key_hierarchy:
      master_key:
        location: "Hardware Security Module (HSM)"
        rotation: "Annual"
        backup: "Distributed key shares"

      data_encryption_keys:
        generation: "Per-environment"
        rotation: "Quarterly"
        versioning: true

      key_encryption_keys:
        purpose: "Encrypt data encryption keys"
        rotation: "Semi-annual"

    key_rotation_policy:
      automatic_rotation: true
      rotation_schedule: "Every 90 days"
      key_version_retention: 2 # Keep 2 previous versions

      rotation_process:
        1: "Generate new key version"
        2: "Mark old key as deprecated"
        3: "Re-encrypt data with new key (background job)"
        4: "Deactivate old key after re-encryption complete"
        5: "Schedule old key deletion (30 days)"
```

### 4.2 Encryption in Transit

**End-to-end encryption** for data transmission.

```yaml
encryption_in_transit:

  api_communication:
    protocol: "TLS 1.3"
    minimum_version: "TLS 1.2"
    certificate_validation: "Required"

  internal_service_communication:
    method: "mTLS (Mutual TLS)"
    certificate_authority: "Internal CA"
    certificate_rotation: "Every 90 days"

    service_mesh_configuration:
      platform: "Istio" # or "Linkerd", "Consul Connect"
      automatic_mtls: true

  database_connections:
    ssl_mode: "require"
    ssl_cipher: "ECDHE-RSA-AES256-GCM-SHA384"
    certificate_verification: "full"

    connection_string: |
      postgresql://user@host:5432/marinesafety?
        sslmode=require&
        sslcert=/path/to/client-cert.pem&
        sslkey=/path/to/client-key.pem&
        sslrootcert=/path/to/ca-cert.pem

  message_queue_encryption:
    protocol: "TLS 1.3"
    authentication: "SASL/SCRAM-SHA-512"

  email_notifications:
    protocol: "TLS 1.3"
    opportunistic_tls: false # Reject if TLS unavailable
    dkim_signing: true
    spf_enforcement: true
```

### 4.3 PII (Personally Identifiable Information) Handling

**Privacy protection** for sensitive personal data.

```yaml
pii_classification:

  pii_categories:
    direct_identifiers:
      - full_name
      - social_security_number
      - driver_license_number
      - passport_number
      - email_address
      - phone_number
      - home_address
      - date_of_birth
      - biometric_data

    quasi_identifiers:
      - zip_code
      - age
      - gender
      - employer
      - job_title
      - vessel_registration (when linked to owner)

    sensitive_pii:
      - medical_information
      - financial_information
      - criminal_history
      - union_membership
      - religious_affiliation

pii_protection_measures:

  data_minimization:
    principle: "Collect only necessary PII"
    retention_justification: "Required for each field"
    periodic_review: "Annual"

  access_controls:
    pii_access_role: "investigator" # Minimum required
    access_logging: "Mandatory"
    access_justification: "Required"

  anonymization_techniques:

    k_anonymity:
      k_value: 5 # Each record indistinguishable from 4 others

    pseudonymization:
      method: "Cryptographic hashing"
      algorithm: "HMAC-SHA256 with secret key"
      reversibility: "Only with key access"

      example: |
        # Pseudonymize personnel name
        original: "John Smith"
        pseudonym: "PERSON_5f4dcc3b5aa765d61d8327deb882cf99"

        # Maintain referential integrity
        SELECT COUNT(*) FROM incidents
        WHERE personnel_pseudonym = 'PERSON_5f4dcc3b5aa765d61d8327deb882cf99'

    data_masking:
      partial_masking:
        email: "j***@example.com"
        phone: "(555) ***-1234"
        ssn: "***-**-6789"

      full_redaction:
        medical_notes: "[REDACTED]"
        witness_statement: "[REDACTED]"

    aggregation:
      minimum_group_size: 10
      suppress_small_cells: true

  automated_pii_detection:
    enabled: true
    scanning_tools:
      - "Named Entity Recognition (NER)"
      - "Regular expression patterns"
      - "Machine learning classifiers"

    scan_frequency:
      new_data: "Real-time"
      existing_data: "Weekly"

    pii_patterns:
      ssn: '\\d{3}-\\d{2}-\\d{4}'
      email: '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}'
      phone: '\\(\\d{3}\\)\\s*\\d{3}-\\d{4}'
      credit_card: '\\d{4}[\\s-]\\d{4}[\\s-]\\d{4}[\\s-]\\d{4}'

pii_retention_policy:

  retention_periods:
    active_investigations: "Duration + 7 years"
    closed_investigations: "7 years after closure"
    statistical_data_anonymized: "Indefinite"

  deletion_process:
    method: "Cryptographic erasure"
    verification: "Required"
    audit_trail: "Permanent record of deletion"

    secure_deletion:
      database: "VACUUM FULL + overwrite free space"
      file_storage: "3-pass overwrite (DoD 5220.22-M)"
      backups: "Automatic expiration enforcement"

  right_to_erasure:
    request_processing_time: "30 days"
    verification_required: true
    exceptions:
      - "Legal hold"
      - "Ongoing investigation"
      - "Regulatory requirement"

pii_breach_notification:

  breach_detection:
    automated_monitoring: true
    anomaly_detection: true

  notification_timeline:
    internal_notification: "Within 1 hour"
    affected_individuals: "Within 72 hours"
    regulatory_authorities: "Within 72 hours"

  notification_content:
    - Nature of breach
    - Types of PII affected
    - Number of individuals affected
    - Mitigation measures taken
    - Contact information for inquiries
```

---

## 5. Access Control

### 5.1 IP Whitelisting

**Network-level access restrictions** for enhanced security.

```yaml
ip_whitelisting:

  enforcement_levels:

    production_api:
      mode: "Whitelist only"
      default_action: "DENY"

      whitelist_categories:
        government_agencies:
          - "192.168.10.0/24" # Coast Guard HQ
          - "10.20.30.0/24" # NTSB Office
          - "172.16.0.0/16" # DOT Network

        research_institutions:
          - "128.112.0.0/16" # University network
          - "18.0.0.0/8" # MIT network

        trusted_partners:
          - "203.0.113.0/24" # Partner organization

        internal_networks:
          - "10.0.0.0/8" # Internal corporate network

        emergency_services:
          - "198.51.100.0/24" # Emergency response center

      bypass_with_authentication:
        enabled: true
        requires:
          - "Valid API key"
          - "Multi-factor authentication"
          - "IP reputation check"

    administrative_panel:
      mode: "Strict whitelist"
      default_action: "DENY"
      bypass_allowed: false

      whitelist:
        - "10.0.1.0/24" # Admin VPN subnet
        - "10.0.2.0/24" # Office network

      additional_requirements:
        - "VPN connection required"
        - "Certificate-based authentication"

    public_statistics_api:
      mode: "No restriction"
      rate_limiting: "Aggressive"
      monitoring: "Enhanced"

  dynamic_whitelisting:
    enabled: true

    auto_whitelist_conditions:
      - "Successful authentication from new IP"
      - "IP reputation score > 90"
      - "Valid SSL certificate presented"

    temporary_whitelist:
      duration: 3600 # 1 hour
      extension_policy: "Require re-authentication"

  ip_reputation_integration:
    provider: "IPQualityScore" # or "MaxMind", "Cloudflare"

    blocking_criteria:
      - vpn_or_proxy_detected: true
      - fraud_score_threshold: 75
      - abuse_velocity_threshold: "High"
      - bot_detected: true

    whitelisting_criteria:
      - known_good_ip: true
      - consistent_behavior: true
      - valid_reverse_dns: true

  geo_blocking:
    enabled: true
    mode: "Allowlist"

    allowed_countries:
      - "US" # United States
      - "CA" # Canada
      - "MX" # Mexico
      # Add additional countries as needed

    blocked_regions:
      - "High-risk countries based on threat intelligence"

    exceptions:
      - "Government authenticated users (any location)"
      - "Registered investigators (any location)"

  implementation:
    method: "WAF + Application-level"

    waf_configuration: |
      # AWS WAF IP Set example
      {
        "IPSetId": "marinesafety-whitelist",
        "IPSetDescriptors": [
          {"Type": "IPV4", "Value": "192.168.10.0/24"},
          {"Type": "IPV4", "Value": "10.20.30.0/24"},
          {"Type": "IPV6", "Value": "2001:db8::/32"}
        ]
      }

    nginx_configuration: |
      # /etc/nginx/conf.d/ip-whitelist.conf

      geo $whitelist {
          default 0;

          # Government agencies
          192.168.10.0/24 1;
          10.20.30.0/24 1;

          # Research institutions
          128.112.0.0/16 1;

          # Internal networks
          10.0.0.0/8 1;
      }

      map $whitelist $ip_restriction {
          0 "denied";
          1 "allowed";
      }

      server {
          location /api/v1/admin {
              if ($ip_restriction = "denied") {
                  return 403 "Access denied from your IP address";
              }
              proxy_pass http://backend;
          }
      }
```

### 5.2 API Key Scopes

**Granular permission control** through API key scopes.

```yaml
api_key_scopes:

  scope_definitions:

    "incidents:read:public":
      description: "Read anonymized public incident data"
      resources:
        - "/api/v1/incidents (public fields only)"
        - "/api/v1/statistics/aggregated"
      restrictions:
        - "No PII access"
        - "Rate limited"

    "incidents:read:detailed":
      description: "Read detailed incident information"
      resources:
        - "/api/v1/incidents (all non-PII fields)"
        - "/api/v1/incidents/{id}"
        - "/api/v1/incidents/search"
      requires_role: "registered_user"

    "incidents:read:pii":
      description: "Access personally identifiable information"
      resources:
        - "/api/v1/incidents (including PII fields)"
        - "/api/v1/personnel"
        - "/api/v1/contacts"
      requires_role: "investigator"
      audit_level: "high"

    "incidents:write":
      description: "Create and update incident reports"
      resources:
        - "POST /api/v1/incidents"
        - "PUT /api/v1/incidents/{id}"
        - "PATCH /api/v1/incidents/{id}"
      requires_role: "investigator"

    "incidents:delete":
      description: "Delete incident records (restricted)"
      resources:
        - "DELETE /api/v1/incidents/{id}"
      requires_role: "data_administrator"
      requires_approval: true

    "statistics:read":
      description: "Access statistical aggregations"
      resources:
        - "/api/v1/statistics/*"
      restrictions:
        - "Minimum aggregation: 10 records"

    "statistics:compute":
      description: "Run custom statistical computations"
      resources:
        - "POST /api/v1/statistics/compute"
      requires_role: "analyst"
      rate_limit: "10 per hour"

    "export:csv":
      description: "Export data in CSV format"
      resources:
        - "/api/v1/export/csv"
      max_records_per_export: 10000
      requires_role: "registered_user"

    "export:bulk":
      description: "Bulk data export"
      resources:
        - "/api/v1/export/bulk"
      max_records_per_export: 1000000
      requires_role: "analyst"
      approval_required: true

    "admin:users":
      description: "User management operations"
      resources:
        - "/api/v1/admin/users/*"
      requires_role: "security_administrator"
      mfa_required: true

    "admin:system":
      description: "System configuration and management"
      resources:
        - "/api/v1/admin/system/*"
      requires_role: "system_administrator"
      mfa_required: true

  scope_validation:
    method: "OAuth 2.0 scope semantics"

    validation_algorithm: |
      function validate_scopes(required_scope, granted_scopes):
          # Check exact match
          if required_scope in granted_scopes:
              return true

          # Check wildcard permissions
          for granted_scope in granted_scopes:
              if granted_scope.endswith("*"):
                  prefix = granted_scope[:-1]
                  if required_scope.startswith(prefix):
                      return true

          # Check hierarchical permissions
          # e.g., "incidents:write" implies "incidents:read"
          scope_hierarchy = {
              "incidents:write": ["incidents:read:detailed", "incidents:read:public"],
              "incidents:delete": ["incidents:write", "incidents:read:detailed"],
              "admin:system": ["admin:users", "admin:keys"]
          }

          if required_scope in scope_hierarchy:
              for implied_scope in scope_hierarchy[required_scope]:
                  if implied_scope in granted_scopes:
                      return true

          return false

  scope_request_process:

    initial_key_creation:
      default_scopes:
        - "incidents:read:public"
        - "statistics:read"

    scope_elevation:
      request_method: "API or admin panel"
      approval_workflow:
        1: "User submits scope request with justification"
        2: "Security team reviews request"
        3: "Automatic approval for standard scopes"
        4: "Manual review for sensitive scopes"
        5: "MFA verification for approval"

      approval_criteria:
        - "Legitimate use case"
        - "User role permits scope"
        - "Organization verification"
        - "Compliance with terms of service"

      scope_grant_expiration:
        standard: "No expiration"
        elevated: "Annual renewal required"
        administrative: "Quarterly renewal required"
```

---

## 6. Audit Logging

### 6.1 Comprehensive Audit Trail

**Immutable logging** of all security-relevant events.

```yaml
audit_logging:

  logged_events:

    authentication_events:
      - login_attempt:
          fields: [timestamp, user_id, ip_address, success, failure_reason]
      - logout:
          fields: [timestamp, user_id, session_duration]
      - password_change:
          fields: [timestamp, user_id, ip_address, method]
      - password_reset:
          fields: [timestamp, user_id, ip_address, token_used]
      - mfa_enabled:
          fields: [timestamp, user_id, mfa_method]
      - mfa_disabled:
          fields: [timestamp, user_id, approved_by]
      - api_key_created:
          fields: [timestamp, key_id, created_by, scopes]
      - api_key_revoked:
          fields: [timestamp, key_id, revoked_by, reason]

    authorization_events:
      - access_granted:
          fields: [timestamp, user_id, resource, action, granted_by_rule]
      - access_denied:
          fields: [timestamp, user_id, resource, action, denial_reason]
      - role_assigned:
          fields: [timestamp, user_id, role, assigned_by]
      - role_revoked:
          fields: [timestamp, user_id, role, revoked_by, reason]
      - permission_elevated:
          fields: [timestamp, user_id, old_permission, new_permission, approved_by]

    data_access_events:
      - pii_accessed:
          fields: [timestamp, user_id, record_id, fields_accessed, justification]
          severity: "high"
      - bulk_export:
          fields: [timestamp, user_id, export_format, record_count, filters_used]
      - data_search:
          fields: [timestamp, user_id, search_query, result_count]
      - incident_viewed:
          fields: [timestamp, user_id, incident_id, view_duration]

    data_modification_events:
      - incident_created:
          fields: [timestamp, user_id, incident_id, incident_data_hash]
      - incident_updated:
          fields: [timestamp, user_id, incident_id, changed_fields, old_values, new_values]
      - incident_deleted:
          fields: [timestamp, user_id, incident_id, deletion_reason, approved_by]
      - data_import:
          fields: [timestamp, user_id, source, record_count, import_hash]

    security_events:
      - rate_limit_exceeded:
          fields: [timestamp, user_id_or_ip, endpoint, limit_type]
      - suspicious_activity:
          fields: [timestamp, user_id_or_ip, activity_description, risk_score]
      - failed_authentication_threshold:
          fields: [timestamp, user_id_or_ip, attempt_count, lockout_applied]
      - unauthorized_access_attempt:
          fields: [timestamp, user_id, resource, attempted_action]
      - security_setting_changed:
          fields: [timestamp, user_id, setting_name, old_value, new_value]

    administrative_events:
      - user_created:
          fields: [timestamp, created_user_id, created_by, initial_role]
      - user_disabled:
          fields: [timestamp, disabled_user_id, disabled_by, reason]
      - system_configuration_changed:
          fields: [timestamp, user_id, config_parameter, old_value, new_value]
      - backup_created:
          fields: [timestamp, backup_id, backup_size, initiated_by]
      - backup_restored:
          fields: [timestamp, backup_id, restored_by, reason]

  audit_log_storage:

    primary_storage:
      database: "PostgreSQL (append-only table)"
      retention: "7 years"

      schema: |
        CREATE TABLE audit_logs (
            log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            event_type VARCHAR(100) NOT NULL,
            severity VARCHAR(20) NOT NULL,
            user_id UUID,
            session_id UUID,
            ip_address INET,
            user_agent TEXT,
            resource VARCHAR(200),
            action VARCHAR(100),
            outcome VARCHAR(20), -- success, failure, partial
            details JSONB,
            correlation_id UUID,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

        -- Prevent updates and deletes
        CREATE OR REPLACE RULE audit_logs_no_update AS
            ON UPDATE TO audit_logs DO INSTEAD NOTHING;

        CREATE OR REPLACE RULE audit_logs_no_delete AS
            ON DELETE TO audit_logs DO INSTEAD NOTHING;

        -- Indexes for efficient querying
        CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp DESC);
        CREATE INDEX idx_audit_user_id ON audit_logs(user_id);
        CREATE INDEX idx_audit_event_type ON audit_logs(event_type);
        CREATE INDEX idx_audit_severity ON audit_logs(severity);
        CREATE INDEX idx_audit_ip_address ON audit_logs(ip_address);
        CREATE INDEX idx_audit_correlation ON audit_logs(correlation_id);

        -- Full-text search on details
        CREATE INDEX idx_audit_details_gin ON audit_logs USING GIN(details);

    backup_storage:
      destination: "Write-once object storage (S3 Glacier)"
      format: "Compressed JSON Lines"
      encryption: "AES-256-GCM"
      replication: "Cross-region"

    siem_integration:
      enabled: true
      destinations:
        - "Splunk"
        - "ELK Stack (Elasticsearch, Logstash, Kibana)"
        - "AWS CloudWatch Logs"

      forwarding_method: "Real-time streaming"
      protocol: "TLS 1.3 encrypted syslog"

  audit_log_integrity:

    cryptographic_chaining:
      enabled: true
      algorithm: "SHA-256 hash chain"

      implementation: |
        # Each log entry includes hash of previous entry
        log_entry = {
            "log_id": "uuid",
            "timestamp": "2024-10-03T12:00:00Z",
            "event_type": "incident_viewed",
            "details": {...},
            "previous_hash": "sha256_of_previous_log",
            "entry_hash": "sha256(log_id + timestamp + details + previous_hash)"
        }

    digital_signatures:
      enabled: true
      signing_interval: "Every 1000 entries or 1 hour"
      algorithm: "RSA-4096"

      verification_process: "Weekly automated verification"

    immutability_verification:
      scheduled_checks: "Daily"
      anomaly_detection: "Enabled"
      alert_on_tampering: "Immediate"

  audit_log_querying:

    search_api:
      endpoint: "/api/v1/audit/search"
      required_role: "security_administrator"

      query_parameters:
        - start_date
        - end_date
        - user_id
        - event_type
        - severity
        - ip_address
        - resource
        - outcome

      example_query: |
        GET /api/v1/audit/search?
          start_date=2024-10-01&
          end_date=2024-10-03&
          event_type=pii_accessed&
          severity=high

    retention_policy:
      active_logs: "7 years in hot storage"
      archived_logs: "Indefinite in cold storage"
      deletion: "Only by court order or legal requirement"

    compliance_reporting:
      automated_reports:
        - "Monthly access summary"
        - "Quarterly security events"
        - "Annual compliance audit"

      report_delivery:
        - "Compliance officer"
        - "Security team"
        - "Management dashboard"
```

### 6.2 Audit Event Implementation

```python
# Pseudocode for audit logging implementation

import hashlib
import json
from datetime import datetime
from typing import Dict, Any, Optional

class AuditLogger:
    def __init__(self, db_connection, signing_key):
        self.db = db_connection
        self.signing_key = signing_key
        self.last_hash = self._get_last_hash()

    def log_event(
        self,
        event_type: str,
        severity: str,
        user_id: Optional[str],
        resource: Optional[str],
        action: Optional[str],
        outcome: str,
        details: Dict[str, Any],
        request_context: Dict[str, Any]
    ) -> str:
        """
        Create immutable audit log entry
        Returns: log_id
        """
        # Generate log entry
        log_entry = {
            'log_id': generate_uuid(),
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'severity': severity,
            'user_id': user_id,
            'session_id': request_context.get('session_id'),
            'ip_address': request_context.get('ip_address'),
            'user_agent': request_context.get('user_agent'),
            'resource': resource,
            'action': action,
            'outcome': outcome,
            'details': details,
            'correlation_id': request_context.get('correlation_id'),
            'previous_hash': self.last_hash
        }

        # Calculate entry hash
        entry_string = json.dumps(log_entry, sort_keys=True)
        entry_hash = hashlib.sha256(entry_string.encode()).hexdigest()
        log_entry['entry_hash'] = entry_hash

        # Insert into database (append-only)
        self.db.execute("""
            INSERT INTO audit_logs (
                log_id, timestamp, event_type, severity,
                user_id, session_id, ip_address, user_agent,
                resource, action, outcome, details, correlation_id
            ) VALUES (
                %(log_id)s, %(timestamp)s, %(event_type)s, %(severity)s,
                %(user_id)s, %(session_id)s, %(ip_address)s, %(user_agent)s,
                %(resource)s, %(action)s, %(outcome)s, %(details)s, %(correlation_id)s
            )
        """, log_entry)

        # Update last hash for next entry
        self.last_hash = entry_hash

        # Forward to SIEM
        self._forward_to_siem(log_entry)

        return log_entry['log_id']

    def _get_last_hash(self) -> str:
        """Get hash of most recent log entry"""
        result = self.db.execute("""
            SELECT entry_hash FROM audit_logs
            ORDER BY timestamp DESC LIMIT 1
        """)
        return result[0]['entry_hash'] if result else None

    def _forward_to_siem(self, log_entry: Dict[str, Any]):
        """Forward log entry to SIEM system"""
        # Send to Splunk, ELK, etc.
        siem_client.send_event(log_entry)

# Middleware for automatic audit logging
def audit_logging_middleware(request):
    """Automatically log all API requests"""

    start_time = datetime.utcnow()

    try:
        # Process request
        response = process_request(request)

        # Log successful request
        audit_logger.log_event(
            event_type=f"api_{request.method.lower()}",
            severity="info",
            user_id=request.user.id if request.user else None,
            resource=request.path,
            action=request.method,
            outcome="success",
            details={
                "status_code": response.status_code,
                "response_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000,
                "query_params": request.query_params,
                "content_length": len(response.content)
            },
            request_context={
                "session_id": request.session.id,
                "ip_address": request.remote_addr,
                "user_agent": request.headers.get('User-Agent'),
                "correlation_id": request.headers.get('X-Correlation-ID')
            }
        )

        return response

    except Exception as e:
        # Log failed request
        audit_logger.log_event(
            event_type=f"api_{request.method.lower()}_error",
            severity="error",
            user_id=request.user.id if request.user else None,
            resource=request.path,
            action=request.method,
            outcome="failure",
            details={
                "error_type": type(e).__name__,
                "error_message": str(e),
                "response_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000
            },
            request_context={
                "session_id": request.session.id if hasattr(request, 'session') else None,
                "ip_address": request.remote_addr,
                "user_agent": request.headers.get('User-Agent'),
                "correlation_id": request.headers.get('X-Correlation-ID')
            }
        )

        raise

# Example usage
def access_pii_endpoint(request, incident_id):
    """Endpoint that accesses PII - requires audit logging"""

    # Check authorization
    if not request.user.has_permission('incidents:read:pii'):
        audit_logger.log_event(
            event_type="unauthorized_access_attempt",
            severity="warning",
            user_id=request.user.id,
            resource=f"/api/v1/incidents/{incident_id}/pii",
            action="read",
            outcome="denied",
            details={"reason": "Insufficient permissions"},
            request_context=get_request_context(request)
        )
        return JSONResponse(status_code=403, content={"error": "Access denied"})

    # Access PII data
    incident_data = get_incident_with_pii(incident_id)

    # Log PII access
    audit_logger.log_event(
        event_type="pii_accessed",
        severity="high",
        user_id=request.user.id,
        resource=f"/api/v1/incidents/{incident_id}",
        action="read_pii",
        outcome="success",
        details={
            "incident_id": incident_id,
            "pii_fields_accessed": ["name", "ssn", "address"],
            "justification": request.query_params.get('justification')
        },
        request_context=get_request_context(request)
    )

    return JSONResponse(content=incident_data)
```

---

## 7. Security Headers

### 7.1 HTTP Security Headers

**Essential security headers** for web application protection.

```yaml
security_headers:

  strict_transport_security:
    header: "Strict-Transport-Security"
    value: "max-age=31536000; includeSubDomains; preload"
    description: "Force HTTPS for 1 year, including subdomains"
    enforcement: "MANDATORY"

  content_security_policy:
    header: "Content-Security-Policy"
    value: |
      default-src 'self';
      script-src 'self' 'unsafe-inline' https://cdn.marinesafety.gov;
      style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
      font-src 'self' https://fonts.gstatic.com;
      img-src 'self' data: https:;
      connect-src 'self' https://api.marinesafety.gov;
      frame-ancestors 'none';
      base-uri 'self';
      form-action 'self';
      upgrade-insecure-requests;
    description: "Restrict resource loading to prevent XSS"
    enforcement: "MANDATORY"
    reporting_endpoint: "https://api.marinesafety.gov/csp-report"

  x_frame_options:
    header: "X-Frame-Options"
    value: "DENY"
    description: "Prevent clickjacking attacks"
    enforcement: "MANDATORY"

  x_content_type_options:
    header: "X-Content-Type-Options"
    value: "nosniff"
    description: "Prevent MIME type sniffing"
    enforcement: "MANDATORY"

  x_xss_protection:
    header: "X-XSS-Protection"
    value: "1; mode=block"
    description: "Enable XSS filtering (legacy browsers)"
    enforcement: "RECOMMENDED"

  referrer_policy:
    header: "Referrer-Policy"
    value: "strict-origin-when-cross-origin"
    description: "Control referrer information leakage"
    enforcement: "MANDATORY"

  permissions_policy:
    header: "Permissions-Policy"
    value: |
      geolocation=(),
      microphone=(),
      camera=(),
      payment=(),
      usb=(),
      magnetometer=(),
      gyroscope=(),
      accelerometer=()
    description: "Disable unnecessary browser features"
    enforcement: "RECOMMENDED"

  cross_origin_embedder_policy:
    header: "Cross-Origin-Embedder-Policy"
    value: "require-corp"
    description: "Prevent loading cross-origin resources"
    enforcement: "OPTIONAL"

  cross_origin_opener_policy:
    header: "Cross-Origin-Opener-Policy"
    value: "same-origin"
    description: "Isolate browsing context"
    enforcement: "RECOMMENDED"

  cross_origin_resource_policy:
    header: "Cross-Origin-Resource-Policy"
    value: "same-origin"
    description: "Prevent cross-origin resource access"
    enforcement: "RECOMMENDED"

  cache_control:
    header: "Cache-Control"
    value: "no-store, no-cache, must-revalidate, private"
    description: "Prevent caching of sensitive data"
    enforcement: "MANDATORY for authenticated endpoints"

implementation_example:

  nginx_configuration: |
    # /etc/nginx/conf.d/security-headers.conf

    # Add security headers to all responses
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.marinesafety.gov; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://api.marinesafety.gov; frame-ancestors 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests;" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=(), payment=(), usb=(), magnetometer=(), gyroscope=(), accelerometer=()" always;
    add_header Cross-Origin-Opener-Policy "same-origin" always;
    add_header Cross-Origin-Resource-Policy "same-origin" always;

    # Cache control for sensitive endpoints
    location ~ ^/api/v1/(incidents|personnel|auth) {
        add_header Cache-Control "no-store, no-cache, must-revalidate, private" always;
        proxy_pass http://backend;
    }

  express_middleware: |
    // Node.js/Express security headers middleware

    const helmet = require('helmet');

    app.use(helmet({
      hsts: {
        maxAge: 31536000,
        includeSubDomains: true,
        preload: true
      },
      contentSecurityPolicy: {
        directives: {
          defaultSrc: ["'self'"],
          scriptSrc: ["'self'", "'unsafe-inline'", "https://cdn.marinesafety.gov"],
          styleSrc: ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
          fontSrc: ["'self'", "https://fonts.gstatic.com"],
          imgSrc: ["'self'", "data:", "https:"],
          connectSrc: ["'self'", "https://api.marinesafety.gov"],
          frameAncestors: ["'none'"],
          baseUri: ["'self'"],
          formAction: ["'self'"],
          upgradeInsecureRequests: []
        }
      },
      frameguard: {
        action: 'deny'
      },
      referrerPolicy: {
        policy: 'strict-origin-when-cross-origin'
      }
    }));

    // Additional custom headers
    app.use((req, res, next) => {
      res.setHeader('Permissions-Policy', 'geolocation=(), microphone=(), camera=()');
      res.setHeader('Cross-Origin-Opener-Policy', 'same-origin');
      res.setHeader('Cross-Origin-Resource-Policy', 'same-origin');

      // Cache control for sensitive endpoints
      if (req.path.startsWith('/api/v1/incidents') ||
          req.path.startsWith('/api/v1/personnel') ||
          req.path.startsWith('/api/v1/auth')) {
        res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate, private');
      }

      next();
    });
```

---

## 8. Vulnerability Management

### 8.1 OWASP Top 10 Protection

**Comprehensive protection** against common web vulnerabilities.

```yaml
owasp_top10_mitigations:

  A01_broken_access_control:
    mitigations:
      - "Implement RBAC with principle of least privilege"
      - "Deny by default; explicit allow required"
      - "Validate authorization on every request (server-side)"
      - "Disable directory listing"
      - "Log all access control failures"
      - "Rate limit API access"
      - "Invalidate JWT tokens on logout"

    testing:
      - "Automated authorization testing"
      - "Manual privilege escalation testing"
      - "IDOR (Insecure Direct Object Reference) testing"

  A02_cryptographic_failures:
    mitigations:
      - "Enforce TLS 1.3 for all data in transit"
      - "Encrypt sensitive data at rest (AES-256)"
      - "Use bcrypt (work factor 12) for password hashing"
      - "Implement proper key management (KMS)"
      - "Disable weak ciphers and protocols"
      - "Use cryptographically secure random number generators"

    testing:
      - "SSL/TLS configuration scanning (Qualys SSL Labs)"
      - "Cipher suite vulnerability testing"
      - "Password storage review"

  A03_injection:
    mitigations:
      - "Use parameterized queries (prepared statements)"
      - "Implement ORM/query builder with automatic escaping"
      - "Input validation with whitelist approach"
      - "Escape special characters for output encoding"
      - "Use stored procedures with proper input validation"
      - "Principle of least privilege for database accounts"

    implementation: |
      # SQL Injection Prevention

      # ❌ VULNERABLE
      query = f"SELECT * FROM incidents WHERE id = {user_input}"

      # ✅ SAFE - Parameterized query
      query = "SELECT * FROM incidents WHERE id = %s"
      cursor.execute(query, (user_input,))

      # ✅ SAFE - ORM
      incident = Incident.objects.get(id=user_input)

    testing:
      - "Automated SQL injection scanning (SQLMap)"
      - "Manual injection testing"
      - "Code review for dynamic queries"

  A04_insecure_design:
    mitigations:
      - "Threat modeling during design phase"
      - "Security requirements in development lifecycle"
      - "Secure design patterns and reference architectures"
      - "Defense in depth (multiple security layers)"
      - "Principle of least privilege"
      - "Segregation of duties"

    practices:
      - "Security architecture review"
      - "Attack tree analysis"
      - "STRIDE threat modeling"

  A05_security_misconfiguration:
    mitigations:
      - "Automated hardening and configuration management"
      - "Disable unnecessary features, components, and services"
      - "Remove default accounts and credentials"
      - "Keep all software up-to-date"
      - "Implement security headers"
      - "Error messages do not reveal sensitive information"

    hardening_checklist:
      database:
        - "Change default passwords"
        - "Disable remote root login"
        - "Enable query logging"
        - "Configure connection limits"
        - "Enable SSL connections only"

      web_server:
        - "Remove server version headers"
        - "Disable directory browsing"
        - "Configure appropriate timeouts"
        - "Limit request body size"
        - "Enable security headers"

      application:
        - "Disable debug mode in production"
        - "Remove test endpoints"
        - "Configure secure session cookies"
        - "Set appropriate CORS policies"
        - "Enable CSRF protection"

    testing:
      - "Configuration scanning (OpenSCAP)"
      - "Baseline compliance checking"
      - "Regular security audits"

  A06_vulnerable_outdated_components:
    mitigations:
      - "Inventory all components and versions"
      - "Automated dependency scanning"
      - "Subscribe to security advisories"
      - "Patch management process"
      - "Remove unused dependencies"
      - "Only use components from official sources"

    dependency_scanning:
      tools:
        - "Snyk (npm, Python, Ruby)"
        - "OWASP Dependency-Check"
        - "GitHub Dependabot"
        - "npm audit / pip-audit"

      scanning_schedule: "Daily for critical dependencies, weekly for all"

      update_policy:
        critical_vulnerabilities: "Patch within 24 hours"
        high_vulnerabilities: "Patch within 7 days"
        medium_vulnerabilities: "Patch within 30 days"
        low_vulnerabilities: "Patch with next release"

  A07_identification_authentication_failures:
    mitigations:
      - "Implement MFA for privileged accounts"
      - "Strong password policy enforcement"
      - "Account lockout after failed attempts"
      - "Secure password recovery mechanism"
      - "Use bcrypt/scrypt/Argon2 for password hashing"
      - "Validate password strength"
      - "Protect against credential stuffing"
      - "Implement CAPTCHA for public endpoints"

    password_policy:
      minimum_length: 12
      require_complexity: true
      require_uppercase: true
      require_lowercase: true
      require_digit: true
      require_special_character: true
      prevent_common_passwords: true
      password_history: 5
      max_age_days: 90

    account_lockout:
      failed_attempts_threshold: 5
      lockout_duration_minutes: 30
      progressive_delays: true

    session_management:
      session_timeout_minutes: 30
      absolute_timeout_minutes: 480 # 8 hours
      regenerate_session_on_login: true
      secure_cookie_flag: true
      httponly_cookie_flag: true
      samesite_cookie: "Strict"

  A08_software_data_integrity_failures:
    mitigations:
      - "Digital signatures for software updates"
      - "Verify integrity of dependencies (checksums)"
      - "Use CI/CD pipeline with integrity checks"
      - "Code signing for releases"
      - "Audit logging with cryptographic chaining"
      - "Implement secure deserialization"

    ci_cd_security:
      - "Signed commits required"
      - "Protected branches"
      - "Code review required before merge"
      - "Automated security testing in pipeline"
      - "Container image scanning"
      - "SBOM (Software Bill of Materials) generation"

  A09_security_logging_monitoring_failures:
    mitigations:
      - "Log all authentication events"
      - "Log all authorization failures"
      - "Log all input validation failures"
      - "Centralized logging infrastructure"
      - "Real-time alerting for suspicious activity"
      - "Log retention per compliance requirements"
      - "Protect log integrity"

    alerting_rules:
      - rule: "5 failed login attempts in 5 minutes"
        severity: "medium"
        action: "Alert security team"

      - rule: "PII access outside business hours"
        severity: "high"
        action: "Alert security team + require justification"

      - rule: "Bulk export > 100,000 records"
        severity: "high"
        action: "Alert data administrator"

      - rule: "Rate limit exceeded 10 times"
        severity: "medium"
        action: "Temporary IP block + alert"

      - rule: "Unauthorized access attempt"
        severity: "critical"
        action: "Alert security team + log IP"

  A10_server_side_request_forgery:
    mitigations:
      - "Sanitize and validate all user-supplied URLs"
      - "Whitelist allowed protocols (http, https only)"
      - "Whitelist allowed domains"
      - "Disable HTTP redirections"
      - "Network segmentation (prevent access to internal services)"
      - "Do not send raw responses to clients"

    implementation: |
      # SSRF Prevention

      def fetch_external_resource(user_provided_url):
          # Validate URL scheme
          parsed = urlparse(user_provided_url)
          if parsed.scheme not in ['http', 'https']:
              raise SecurityError("Invalid URL scheme")

          # Whitelist allowed domains
          allowed_domains = ['api.example.com', 'data.gov']
          if parsed.netloc not in allowed_domains:
              raise SecurityError("Domain not whitelisted")

          # Prevent access to private IP ranges
          ip = socket.gethostbyname(parsed.netloc)
          if ipaddress.ip_address(ip).is_private:
              raise SecurityError("Access to private IP not allowed")

          # Make request with timeout and size limit
          response = requests.get(
              user_provided_url,
              timeout=5,
              allow_redirects=False,
              stream=True,
              headers={'User-Agent': 'MarineSafetyAPI/1.0'}
          )

          # Limit response size
          content = response.iter_content(chunk_size=1024)
          data = b''
          max_size = 10 * 1024 * 1024  # 10 MB
          for chunk in content:
              data += chunk
              if len(data) > max_size:
                  raise SecurityError("Response too large")

          return data

    testing:
      - "SSRF vulnerability scanning"
      - "Manual testing with various URL payloads"
      - "Network segmentation validation"
```

### 8.2 Security Scanning and Testing

```yaml
security_scanning:

  static_application_security_testing:
    tools:
      - name: "SonarQube"
        purpose: "Code quality and security analysis"
        scan_schedule: "On every commit"

      - name: "Bandit (Python)"
        purpose: "Python-specific security linting"
        scan_schedule: "On every commit"

      - name: "ESLint Security Plugin"
        purpose: "JavaScript security analysis"
        scan_schedule: "On every commit"

    fail_build_on:
      - "Critical vulnerabilities"
      - "High severity security issues"
      - "Hardcoded secrets detected"

  dynamic_application_security_testing:
    tools:
      - name: "OWASP ZAP"
        purpose: "Web application security testing"
        scan_schedule: "Nightly on staging environment"

      - name: "Burp Suite Professional"
        purpose: "Manual penetration testing"
        scan_schedule: "Quarterly"

    test_coverage:
      - "Authentication bypass"
      - "Authorization vulnerabilities"
      - "Injection attacks"
      - "XSS vulnerabilities"
      - "CSRF vulnerabilities"
      - "Security misconfiguration"

  software_composition_analysis:
    tools:
      - "Snyk"
      - "WhiteSource"
      - "GitHub Dependabot"

    scan_schedule: "Daily"

    action_on_vulnerability:
      critical: "Immediate patch + emergency deployment"
      high: "Patch within 7 days"
      medium: "Patch within 30 days"
      low: "Address in next release"

  container_scanning:
    tools:
      - "Trivy"
      - "Clair"
      - "Anchore"

    scan_points:
      - "Image build time"
      - "Before deployment"
      - "Runtime scanning (weekly)"

  infrastructure_scanning:
    tools:
      - "OpenSCAP"
      - "Nessus"
      - "Qualys"

    scan_schedule: "Weekly"

    scan_targets:
      - "Web servers"
      - "Database servers"
      - "API gateways"
      - "Load balancers"

  penetration_testing:
    schedule: "Annual"
    scope: "Full application stack"
    provider: "Third-party security firm"

    testing_methodology: "OWASP Testing Guide"

    deliverables:
      - "Executive summary"
      - "Detailed vulnerability report"
      - "Proof-of-concept exploits"
      - "Remediation recommendations"

    retest: "After critical vulnerabilities fixed"

vulnerability_disclosure:

  responsible_disclosure_program:
    contact_email: "security@marinesafety.gov"
    pgp_key: "https://marinesafety.gov/.well-known/pgp-key.txt"

    scope:
      in_scope:
        - "*.marinesafety.gov"
        - "api.marinesafety.gov"
        - "Mobile applications"

      out_of_scope:
        - "Social engineering"
        - "Physical attacks"
        - "DoS attacks"

    response_timeline:
      acknowledgment: "Within 24 hours"
      initial_assessment: "Within 7 days"
      resolution_timeline: "Based on severity"

    rewards:
      bug_bounty_program: "Under consideration"
      public_acknowledgment: "Yes (with permission)"
```

---

## 9. Incident Response

### 9.1 Security Incident Classification

```yaml
incident_classification:

  severity_levels:

    critical:
      definition: "Successful breach with data exfiltration or system compromise"
      examples:
        - "Unauthorized access to PII database"
        - "Ransomware encryption of production systems"
        - "Data exfiltration confirmed"
        - "Root/admin account compromise"
      response_time: "Immediate (< 15 minutes)"
      escalation: "CISO + Executive team"

    high:
      definition: "Active attack or significant vulnerability exploitation"
      examples:
        - "Ongoing DDoS attack affecting availability"
        - "SQL injection vulnerability being exploited"
        - "Privilege escalation attempt detected"
        - "Suspicious bulk data access"
      response_time: "< 1 hour"
      escalation: "Security team + Management"

    medium:
      definition: "Suspicious activity or minor security policy violation"
      examples:
        - "Multiple failed authentication attempts"
        - "Unusual access pattern detected"
        - "Minor security misconfiguration discovered"
        - "Vulnerability in non-critical component"
      response_time: "< 4 hours"
      escalation: "Security team"

    low:
      definition: "Informational security event requiring monitoring"
      examples:
        - "Security scan detected from external IP"
        - "Password policy violation"
        - "Outdated dependency with low-risk vulnerability"
      response_time: "< 24 hours"
      escalation: "Security analyst"

incident_types:

  data_breach:
    definition: "Unauthorized access, disclosure, or exfiltration of sensitive data"
    indicators:
      - "Unusual database query patterns"
      - "Large data transfers to external IPs"
      - "Access to PII by unauthorized users"
      - "Backup files accessed or copied"

  account_compromise:
    definition: "Unauthorized access to user or system accounts"
    indicators:
      - "Login from unusual locations"
      - "Impossible travel scenarios"
      - "Privilege escalation detected"
      - "API key used from multiple IPs simultaneously"

  denial_of_service:
    definition: "Attack designed to disrupt service availability"
    indicators:
      - "Abnormal traffic volume"
      - "Distributed requests from multiple IPs"
      - "Resource exhaustion (CPU, memory, connections)"
      - "Application slowdown or crash"

  malware_infection:
    definition: "Malicious software detected in system"
    indicators:
      - "Antivirus alerts"
      - "Unusual process execution"
      - "Outbound connections to known malicious IPs"
      - "File integrity changes"

  insider_threat:
    definition: "Security incident caused by insider with legitimate access"
    indicators:
      - "Unusual data access by employee"
      - "After-hours access to sensitive systems"
      - "Bulk download of confidential data"
      - "Access attempts after termination"
```

### 9.2 Incident Response Procedures

```yaml
incident_response_workflow:

  phase_1_preparation:
    activities:
      - "Maintain updated incident response plan"
      - "Define roles and responsibilities"
      - "Establish communication channels"
      - "Conduct regular IR drills"
      - "Maintain forensic tools and resources"

    incident_response_team:
      incident_commander:
        role: "CISO or Security Manager"
        responsibilities:
          - "Overall incident coordination"
          - "Decision making authority"
          - "External communication"

      security_analysts:
        role: "Security Operations Team"
        responsibilities:
          - "Incident detection and analysis"
          - "Evidence collection"
          - "Initial containment"

      system_administrators:
        role: "Infrastructure Team"
        responsibilities:
          - "System isolation"
          - "Log collection"
          - "System restoration"

      legal_counsel:
        role: "Legal Department"
        responsibilities:
          - "Regulatory notification guidance"
          - "Evidence preservation"
          - "Law enforcement liaison"

      communications:
        role: "Public Relations"
        responsibilities:
          - "External notifications"
          - "Media management"
          - "Stakeholder communication"

  phase_2_detection_analysis:
    activities:
      - "Monitor security alerts"
      - "Analyze suspicious activity"
      - "Determine incident severity"
      - "Document initial findings"
      - "Activate incident response team"

    detection_sources:
      - "SIEM alerts"
      - "IDS/IPS notifications"
      - "Audit log analysis"
      - "User reports"
      - "Threat intelligence feeds"
      - "Vulnerability scanner reports"

    initial_assessment:
      questions:
        - "What happened?"
        - "When did it happen?"
        - "What systems are affected?"
        - "What data is at risk?"
        - "Is the incident ongoing?"
        - "What is the severity level?"

    documentation:
      incident_ticket:
        fields:
          - "Incident ID"
          - "Detection timestamp"
          - "Incident type"
          - "Severity level"
          - "Affected systems"
          - "Initial indicators"
          - "Assigned responder"

      incident_log:
        format: "Chronological timeline"
        required_entries:
          - "All actions taken"
          - "All findings discovered"
          - "All communications sent"
          - "All decisions made"

  phase_3_containment:

    short_term_containment:
      objectives:
        - "Stop the attack"
        - "Prevent lateral movement"
        - "Preserve evidence"

      actions:
        - "Isolate affected systems (network segmentation)"
        - "Block malicious IPs at firewall"
        - "Disable compromised accounts"
        - "Revoke compromised API keys"
        - "Take snapshot of affected systems"
        - "Enable enhanced logging"

      example_commands: |
        # Isolate compromised server
        iptables -A INPUT -j DROP
        iptables -A OUTPUT -j DROP
        iptables -A INPUT -s 10.0.0.0/8 -p tcp --dport 22 -j ACCEPT  # Allow admin SSH

        # Revoke API key
        psql -c "UPDATE api_keys SET revoked_at = NOW(),
                 revocation_reason = 'Security incident INC-2024-001'
                 WHERE key_id = 'compromised_key_id'"

        # Create system snapshot
        lvcreate -L 100G -s -n incident_snapshot /dev/vg0/root

    long_term_containment:
      objectives:
        - "Allow business operations to continue"
        - "Implement temporary fixes"
        - "Prepare for recovery"

      actions:
        - "Apply emergency patches"
        - "Deploy temporary workarounds"
        - "Implement additional monitoring"
        - "Update firewall rules"
        - "Rotate credentials"

  phase_4_eradication:
    activities:
      - "Remove malware"
      - "Close vulnerabilities"
      - "Improve defenses"
      - "Verify complete removal"

    procedures:
      malware_removal:
        - "Identify all infected systems"
        - "Disconnect from network"
        - "Run malware removal tools"
        - "Rebuild from clean backups if necessary"
        - "Verify with multiple scanners"

      vulnerability_remediation:
        - "Identify root cause"
        - "Apply security patches"
        - "Implement configuration changes"
        - "Deploy code fixes"
        - "Conduct security testing"

      credential_rotation:
        - "Change all compromised passwords"
        - "Rotate API keys"
        - "Regenerate encryption keys"
        - "Update service credentials"
        - "Force password reset for affected users"

  phase_5_recovery:
    activities:
      - "Restore systems to normal operation"
      - "Verify system functionality"
      - "Monitor for recurring issues"
      - "Gradually restore services"

    recovery_checklist:
      - verification: "Systems clean and patched"
      - verification: "Security controls operational"
      - verification: "Monitoring enhanced"
      - verification: "Business functionality restored"
      - verification: "No signs of attacker presence"

    staged_recovery:
      stage_1:
        description: "Restore critical services in isolated environment"
        monitoring: "Intensive monitoring for 48 hours"

      stage_2:
        description: "Restore remaining services"
        monitoring: "Enhanced monitoring for 7 days"

      stage_3:
        description: "Return to normal operations"
        monitoring: "Baseline monitoring continues"

  phase_6_post_incident_activity:
    activities:
      - "Conduct lessons learned meeting"
      - "Document incident details"
      - "Update incident response procedures"
      - "Implement preventive measures"
      - "Complete regulatory notifications"

    incident_report:
      sections:
        executive_summary:
          - "Incident overview"
          - "Business impact"
          - "Resolution summary"

        timeline:
          - "Detection timestamp"
          - "Response actions taken"
          - "Recovery timestamp"

        technical_details:
          - "Attack vector"
          - "Systems affected"
          - "Data compromised"
          - "Vulnerabilities exploited"

        lessons_learned:
          - "What went well"
          - "What needs improvement"
          - "Recommended actions"

        preventive_measures:
          - "Security enhancements"
          - "Policy updates"
          - "Training recommendations"

    metrics_tracking:
      - "Mean time to detect (MTTD)"
      - "Mean time to respond (MTTR)"
      - "Mean time to recover (MTTR)"
      - "False positive rate"
      - "Incident recurrence rate"
```

### 9.3 Breach Notification

```yaml
breach_notification:

  regulatory_requirements:

    gdpr_notification:
      authority: "Data Protection Authority"
      timeline: "72 hours from becoming aware"
      required_information:
        - "Nature of data breach"
        - "Categories and number of data subjects affected"
        - "Categories and number of records affected"
        - "Likely consequences of breach"
        - "Measures taken or proposed"
        - "Contact details of DPO"

      exemption: "If breach unlikely to result in risk to rights and freedoms"

    us_state_breach_laws:
      varies_by_state: true
      typical_timeline: "Without unreasonable delay"
      notification_method: "Written, email, or substitute notice"

      example_california:
        authority: "California Attorney General (if >500 residents)"
        timeline: "Most expedient time possible, without unreasonable delay"
        required_information:
          - "Incident date or estimated date"
          - "Types of PII involved"
          - "Summary of incident"
          - "Contact information"

    sector_specific_requirements:
      maritime_sector:
        authority: "Department of Homeland Security (if critical infrastructure)"
        timeline: "Varies by incident severity"

  notification_templates:

    affected_individuals_notification:
      subject: "Important Security Notice: Data Breach Notification"

      content: |
        Dear [Name],

        We are writing to inform you of a data security incident that may have
        affected your personal information in the Marine Safety Incidents Database.

        **What Happened:**
        On [DATE], we discovered [DESCRIPTION OF INCIDENT]. We immediately began
        an investigation and took steps to secure our systems.

        **What Information Was Involved:**
        The incident may have affected the following information:
        - [LIST OF DATA TYPES]

        **What We Are Doing:**
        - [REMEDIATION STEPS TAKEN]
        - [ADDITIONAL SECURITY MEASURES]
        - [ONGOING MONITORING]

        **What You Can Do:**
        We recommend that you:
        - Monitor your accounts for suspicious activity
        - Change your password if you use the same password elsewhere
        - Consider placing a fraud alert or credit freeze (if financial data affected)
        - Be alert for phishing attempts

        **Credit Monitoring Services:**
        [IF APPLICABLE] We are offering [DURATION] of complimentary credit monitoring
        services through [PROVIDER].

        **For More Information:**
        If you have questions, please contact:
        - Email: security@marinesafety.gov
        - Phone: 1-800-XXX-XXXX (toll-free)
        - Website: https://marinesafety.gov/security-incident

        We sincerely apologize for this incident and any inconvenience it may cause.

        Sincerely,
        [CISO Name]
        Chief Information Security Officer
        Marine Safety Administration

    regulatory_authority_notification:
      format: "Formal written notification"

      required_sections:
        - "Executive summary"
        - "Incident timeline"
        - "Description of breach"
        - "Categories of data affected"
        - "Number of individuals affected"
        - "Assessment of harm"
        - "Remediation measures"
        - "Preventive measures"
        - "Contact information"

    media_statement:
      approval: "Legal and PR review required"

      template: |
        [ORGANIZATION NAME] today announced that it has discovered a data security
        incident affecting the Marine Safety Incidents Database. Upon discovery on
        [DATE], we immediately launched an investigation and engaged cybersecurity
        experts to assist.

        The incident involved [BRIEF DESCRIPTION]. [NUMBER] individuals may have
        been affected.

        We are notifying affected individuals and providing [RESOURCES/SUPPORT].
        We have also notified [REGULATORY AUTHORITIES] and are cooperating fully
        with their investigations.

        The security and privacy of information in our systems is a top priority.
        We have implemented [SECURITY ENHANCEMENTS] to prevent similar incidents.

        For more information, visit [WEBSITE] or contact [EMAIL/PHONE].

  notification_decision_tree:

    step_1_assess_impact:
      question: "Was PII compromised or exfiltrated?"
      yes: "Proceed to step 2"
      no: "No notification required (document rationale)"

    step_2_assess_risk:
      question: "Does the breach pose a risk to individuals?"
      high_risk: "Notify individuals and regulators"
      low_risk: "Document risk assessment; may still notify"

    step_3_determine_scope:
      question: "How many individuals affected?"
      large_scale: "Media notification may be required"
      small_scale: "Direct notification sufficient"

    step_4_notification_timeline:
      regulatory: "72 hours or per jurisdiction"
      individuals: "Without unreasonable delay"
      media: "If required by scale or law"
```

---

## 10. Compliance

### 10.1 GDPR Compliance

```yaml
gdpr_compliance:

  lawful_basis_for_processing:
    basis: "Public interest and legal obligation"
    justification: |
      Marine safety incident data is processed for public safety and regulatory
      compliance purposes under maritime safety laws.

    data_minimization:
      principle: "Collect only necessary data"
      review_frequency: "Annual"

    purpose_limitation:
      purpose: "Marine safety investigation and analysis"
      secondary_uses: "Require explicit consent or legal basis"

  data_subject_rights:

    right_to_access:
      request_method: "Online portal or email"
      response_time: "30 days (extendable to 60)"
      provided_information:
        - "Categories of data processed"
        - "Purposes of processing"
        - "Recipients of data"
        - "Retention period"
        - "Copy of personal data"

    right_to_rectification:
      process: "Allow users to correct inaccurate data"
      verification: "Identity verification required"
      response_time: "30 days"

    right_to_erasure:
      conditions:
        - "Data no longer necessary"
        - "Consent withdrawn"
        - "Unlawful processing"

      exceptions:
        - "Legal obligation to retain (safety records)"
        - "Public interest (safety investigations)"
        - "Statistical purposes (anonymized data)"

      process: "Verify exception doesn't apply, then delete"
      response_time: "30 days"

    right_to_data_portability:
      format: "Structured, machine-readable format (JSON, CSV)"
      scope: "Data provided by data subject"
      response_time: "30 days"

    right_to_object:
      scenarios:
        - "Processing based on public interest"
        - "Direct marketing (N/A for this system)"
        - "Profiling (N/A for this system)"

      process: "Assess objection and cease processing unless compelling legitimate grounds"

  data_protection_impact_assessment:
    when_required:
      - "Large-scale processing of sensitive data"
      - "Systematic monitoring"
      - "Processing of PII at scale"

    dpia_components:
      - "Description of processing operations"
      - "Purposes of processing"
      - "Necessity and proportionality assessment"
      - "Risk assessment"
      - "Mitigation measures"
      - "Consultation with DPO"

    review_frequency: "Annual or when significant changes"

  data_protection_officer:
    required: true
    contact: "dpo@marinesafety.gov"
    responsibilities:
      - "Monitor GDPR compliance"
      - "Advise on data protection"
      - "Conduct DPIAs"
      - "Liaise with supervisory authorities"
      - "Handle data subject requests"

  international_data_transfers:
    mechanism: "Standard Contractual Clauses (SCCs)"
    adequacy_decision: "Check if recipient country has adequacy decision"
    additional_measures: "Encryption, access controls"

  record_of_processing_activities:
    maintained: true
    includes:
      - "Purposes of processing"
      - "Categories of data subjects"
      - "Categories of personal data"
      - "Recipients of data"
      - "International transfers"
      - "Retention periods"
      - "Security measures"
```

### 10.2 Data Attribution

```yaml
data_attribution:

  source_attribution:
    principle: "Clearly identify data sources"

    metadata_fields:
      - source_organization: "e.g., USCG, NTSB, State Maritime Authority"
      - submission_date: "Date data submitted"
      - verification_status: "Verified, Unverified, In Review"
      - data_quality_score: "Automated quality assessment"
      - last_updated: "Most recent modification date"
      - update_frequency: "How often source updates"

    api_response_attribution:
      format: |
        {
          "incident": {...},
          "_metadata": {
            "source": "US Coast Guard",
            "source_id": "USCG-2024-001234",
            "submission_date": "2024-09-15",
            "verification_status": "Verified",
            "last_updated": "2024-10-01",
            "data_quality_score": 0.95
          }
        }

  citation_requirements:
    academic_use:
      required_citation: |
        Marine Safety Incidents Database (MSID). [Year]. [Incident Title or Query Description].
        Retrieved from https://api.marinesafety.gov on [Access Date].
        DOI: [if applicable]

    commercial_use:
      required_attribution: "Data provided by Marine Safety Incidents Database (MSID)"
      logo_usage: "Per brand guidelines"

    government_use:
      attribution_recommended: true
      license: "Public domain or open government license"

  open_data_licensing:
    license_type: "Creative Commons CC0 or Open Data Commons"

    cc0_public_domain:
      description: "No copyright restrictions"
      use_cases: "Aggregated statistics, anonymized data"

    open_database_license:
      description: "Attribution required"
      use_cases: "Detailed incident records"
      share_alike: false

  data_quality_indicators:
    completeness_score:
      calculation: "Percentage of required fields populated"
      thresholds:
        high: ">90%"
        medium: "70-90%"
        low: "<70%"

    verification_status:
      verified: "Official investigation completed"
      preliminary: "Initial report, not yet verified"
      unverified: "User-submitted, awaiting review"

    confidence_level:
      high: "Multiple corroborating sources"
      medium: "Single authoritative source"
      low: "Unverified source"
```

### 10.3 Public Records Laws

```yaml
public_records_compliance:

  freedom_of_information_act:
    principle: "Government records are presumptively public"

    exemptions_applicable:
      exemption_6:
        description: "Personnel and medical files privacy"
        application: "Redact PII from public disclosures"

      exemption_7c:
        description: "Law enforcement records - personal privacy"
        application: "Protect identities in ongoing investigations"

      exemption_4:
        description: "Trade secrets and confidential information"
        application: "Protect proprietary vessel designs (if applicable)"

    foia_request_process:
      submission_methods:
        - "Online portal"
        - "Email: foia@marinesafety.gov"
        - "Mail: FOIA Office address"

      response_timeline: "20 business days (extendable)"

      fee_structure:
        search: "$X per hour"
        review: "$X per hour"
        duplication: "$X per page"
        fee_waiver: "Available for public interest requests"

      request_tracking:
        system: "FOIAonline or custom portal"
        status_updates: "Automated notifications"

  state_public_records_laws:
    varies_by_state: true

    example_requirements:
      california:
        law: "California Public Records Act"
        response_time: "10 days"

      new_york:
        law: "Freedom of Information Law (FOIL)"
        response_time: "5 business days"

  proactive_disclosure:
    open_data_portal:
      url: "https://data.marinesafety.gov"

      datasets_published:
        - "Anonymized incident statistics"
        - "Aggregate safety metrics"
        - "Vessel type categorization"
        - "Incident type taxonomy"
        - "Geographic distribution (non-sensitive)"

      update_frequency: "Quarterly"

      data_formats:
        - "CSV"
        - "JSON"
        - "XML"
        - "API access"

    transparency_reporting:
      annual_report:
        includes:
          - "Total incidents recorded"
          - "Incident types distribution"
          - "Geographic distribution"
          - "Trend analysis"
          - "Safety recommendations"

        publication: "Publicly available website"

  data_redaction_guidelines:
    automatic_redaction:
      - "Social Security Numbers"
      - "Personal addresses"
      - "Personal phone numbers"
      - "Email addresses"
      - "Medical information"
      - "Financial account numbers"

    contextual_redaction:
      - "Names (depending on role - public officials not redacted)"
      - "Vessel registration numbers (case-by-case)"
      - "Investigation details (ongoing investigations)"

    redaction_marking:
      method: "[REDACTED - Exemption X]"
      documentation: "Maintain log of redactions"
```

---

## 11. Security Monitoring & Alerting

```yaml
security_monitoring:

  real_time_monitoring:

    siem_platform:
      system: "Splunk / ELK / Azure Sentinel"

      log_sources:
        - "Application logs"
        - "Web server logs"
        - "Database audit logs"
        - "Firewall logs"
        - "IDS/IPS alerts"
        - "Authentication logs"
        - "Cloud infrastructure logs"

      correlation_rules:
        - name: "Brute Force Attack"
          condition: ">5 failed logins from same IP in 5 minutes"
          action: "Alert + Temporary IP block"

        - name: "Privilege Escalation"
          condition: "User role changed to admin + subsequent sensitive data access"
          action: "Critical alert + Require justification"

        - name: "Data Exfiltration"
          condition: "Bulk export >50,000 records + external IP destination"
          action: "Critical alert + Block transfer + Notify CISO"

        - name: "Anomalous Access Pattern"
          condition: "Access from unusual location + unusual time + high-value data"
          action: "Alert + Require MFA verification"

    metrics_monitoring:

      system_health:
        - cpu_usage: "Alert if >80% for 5 minutes"
        - memory_usage: "Alert if >85%"
        - disk_usage: "Alert if >90%"
        - api_response_time: "Alert if >2 seconds (p95)"

      security_metrics:
        - failed_authentication_rate: "Alert if >10% of total requests"
        - rate_limit_exceeded_count: "Alert if >100 per hour"
        - api_error_rate: "Alert if >5%"
        - tls_handshake_failures: "Alert if >50 per hour"

  threat_intelligence_integration:

    feeds:
      - "CISA Cybersecurity Advisories"
      - "FBI InfraGard"
      - "Commercial threat intelligence (e.g., Recorded Future)"
      - "Open-source threat feeds (e.g., AlienVault OTX)"

    automated_blocking:
      - "Known malicious IP addresses"
      - "C2 server IPs"
      - "Tor exit nodes (optional)"
      - "VPN services (optional, with policy exceptions)"

  user_behavior_analytics:

    baseline_establishment:
      duration: "30 days of normal activity"
      metrics:
        - "Typical login times"
        - "Usual access locations"
        - "Standard data volume accessed"
        - "Common API endpoints used"

    anomaly_detection:
      - "Access from new location"
      - "Access during unusual hours"
      - "Volume spike (10x normal)"
      - "New API endpoint usage pattern"
      - "Privilege level change"

    machine_learning:
      models:
        - "Isolation Forest for anomaly detection"
        - "LSTM for sequence anomaly detection"
        - "Clustering for user behavior grouping"

      retraining_frequency: "Weekly"

  alerting_system:

    alert_channels:
      critical:
        - "PagerDuty (immediate)"
        - "SMS to security team"
        - "Email to CISO"
        - "Slack #security-incidents channel"

      high:
        - "Email to security team"
        - "Slack #security-alerts channel"

      medium:
        - "Email digest (hourly)"
        - "Dashboard notification"

      low:
        - "Daily summary email"

    alert_fatigue_prevention:
      - "Intelligent alert aggregation"
      - "Threshold tuning based on false positive rate"
      - "Alert suppression during maintenance windows"
      - "Context-enriched alerts"

    escalation_policy:
      level_1:
        responder: "Security Analyst"
        response_time: "15 minutes"

      level_2:
        responder: "Security Lead"
        escalation_after: "30 minutes if unacknowledged"

      level_3:
        responder: "CISO"
        escalation_after: "1 hour or critical incident"
```

---

## 12. Security Training & Awareness

```yaml
security_training:

  developer_security_training:
    frequency: "Annual + onboarding"

    topics:
      - "Secure coding practices"
      - "OWASP Top 10"
      - "Input validation and sanitization"
      - "Authentication and authorization"
      - "Cryptography best practices"
      - "Secure API design"
      - "Security testing"

    certifications_encouraged:
      - "Certified Secure Software Lifecycle Professional (CSSLP)"
      - "GIAC Secure Software Programmer (GSSP)"

  security_administrator_training:
    frequency: "Annual + ongoing"

    topics:
      - "Incident response procedures"
      - "Log analysis"
      - "Threat hunting"
      - "Forensics basics"
      - "Security tool administration"

    certifications_recommended:
      - "Certified Information Systems Security Professional (CISSP)"
      - "GIAC Security Essentials (GSEC)"
      - "Certified Ethical Hacker (CEH)"

  general_user_awareness:
    frequency: "Annual + phishing simulations (quarterly)"

    topics:
      - "Password security"
      - "Phishing recognition"
      - "Social engineering"
      - "Physical security"
      - "Data handling"
      - "Incident reporting"

    delivery_methods:
      - "Interactive e-learning modules"
      - "Simulated phishing campaigns"
      - "Security awareness posters"
      - "Monthly security tips newsletter"
```

---

## 13. Conclusion

This Security Architecture specification provides a comprehensive, production-ready security framework for the Marine Safety Incidents Database. It addresses:

- **Authentication** with multiple methods (API keys, OAuth 2.0, JWT)
- **Authorization** using RBAC with dynamic rules
- **API Security** through TLS, rate limiting, CORS, and request signing
- **Data Protection** with encryption at rest and in transit
- **Access Control** via IP whitelisting and API key scopes
- **Audit Logging** with immutable, cryptographically-chained logs
- **Security Headers** for web application protection
- **Vulnerability Management** covering OWASP Top 10 and scanning
- **Incident Response** with detailed procedures and breach notification
- **Compliance** with GDPR, data attribution, and public records laws

### Implementation Priorities

**Phase 1 (Critical - Week 1-2):**
1. Implement TLS 1.3 with proper certificate management
2. Deploy API key authentication with secure storage
3. Implement RBAC with core roles
4. Enable audit logging for all authenticated requests
5. Configure security headers

**Phase 2 (High Priority - Week 3-4):**
1. Deploy rate limiting
2. Implement PII encryption and handling
3. Configure CORS policies
4. Set up SIEM integration
5. Establish incident response procedures

**Phase 3 (Standard - Week 5-8):**
1. Implement OAuth 2.0 flows
2. Deploy request signing
3. Set up automated vulnerability scanning
4. Implement IP whitelisting
5. Configure comprehensive monitoring and alerting

**Phase 4 (Ongoing):**
1. Conduct security training
2. Perform penetration testing
3. Refine incident response procedures
4. Optimize security monitoring rules
5. Maintain compliance documentation

### Maintenance and Review

- **Security controls review:** Quarterly
- **Penetration testing:** Annual
- **Incident response drill:** Semi-annual
- **Policy updates:** As needed, minimum annual review
- **Dependency updates:** Weekly (automated), critical patches immediately

---

**Document Control:**
- **Version:** 1.0.0
- **Status:** Production-Ready
- **Next Review:** 2026-04-03
- **Owner:** Security Architecture Team
- **Approval:** CISO

---
