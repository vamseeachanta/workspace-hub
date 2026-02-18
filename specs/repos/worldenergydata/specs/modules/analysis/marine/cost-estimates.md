# Marine Safety Incidents Database - Cost Estimates

**Version:** 1.0.0
**Date:** 2025-10-03
**Status:** Planning
**Module:** HSE (Health, Safety, Environment) - Marine Safety
**Related:** [MARINE_SAFETY_SPEC.md](./MARINE_SAFETY_SPEC.md)

---

## Executive Summary

This document provides detailed cost estimates for developing, deploying, and operating the Marine Safety Incidents Database. Total estimated costs range from **$42,500 - $67,500** for development (28 weeks) and **$385 - $785/month** for infrastructure, with scalability planning up to 100x traffic.

### Quick Reference
- **Development (One-Time):** $42,500 - $67,500
- **Infrastructure (Monthly):** $385 - $785
- **First Year Total:** $47,120 - $76,920
- **Annual Operations (Year 2+):** $4,620 - $9,420
- **Cost per 1,000 Incidents:** $0.15 - $0.30

---

## Table of Contents

1. [Infrastructure Costs](#1-infrastructure-costs)
2. [Third-Party Services](#2-third-party-services)
3. [Development Costs](#3-development-costs)
4. [Operational Costs](#4-operational-costs)
5. [Scaling Scenarios](#5-scaling-scenarios)
6. [Cost Optimization](#6-cost-optimization)
7. [Budget Breakdown by Phase](#7-budget-breakdown-by-phase)
8. [ROI Analysis](#8-roi-analysis)
9. [Cost Monitoring](#9-cost-monitoring)
10. [Alternative Pricing](#10-alternative-pricing)

---

## 1. Infrastructure Costs

### AWS Infrastructure (Monthly Baseline)

#### 1.1 Compute - EC2 Instances

**Production API Server**
- Instance Type: `t3.medium` (2 vCPU, 4 GB RAM)
- Purpose: FastAPI application, background jobs
- Cost: **$30.37/month** (On-Demand)
- Reserved (1-year): **$18.25/month** (-40%)
- Details: 730 hours/month × $0.0416/hour

**Development/Staging Server**
- Instance Type: `t3.small` (2 vCPU, 2 GB RAM)
- Purpose: Testing, QA, staging environment
- Cost: **$15.18/month** (On-Demand)
- Reserved (1-year): **$9.13/month** (-40%)
- Details: 730 hours/month × $0.0208/hour

**Data Processing Worker (Spot Instance)**
- Instance Type: `t3.medium` (intermittent use)
- Purpose: Web scraping, data processing
- Cost: **$45/month** (estimated 150 hours/month)
- Spot Instance: **$13.50/month** (-70%)
- Details: 150 hours/month × $0.30/hour (spot) vs $0.0416 (on-demand)

**Subtotal EC2:** $90.55/month (on-demand) | $40.88/month (optimized)

#### 1.2 Database - RDS PostgreSQL

**Production Database**
- Instance Type: `db.t3.medium` (2 vCPU, 4 GB RAM)
- Storage: 100 GB General Purpose SSD (GP3)
- Multi-AZ: No (single AZ for cost optimization)
- Backup Retention: 7 days automated backups
- Cost Breakdown:
  - Instance: **$60.74/month** (730 hours × $0.0832/hour)
  - Storage: **$11.50/month** (100 GB × $0.115/GB-month)
  - Backup Storage: **$5/month** (estimated 50 GB × $0.095/GB-month)
  - I/O Operations: **$5/month** (estimated)
- **Total: $82.24/month**
- Reserved (1-year): **$49.35/month** (-40%)

**Development Database**
- Instance Type: `db.t3.small` (2 vCPU, 2 GB RAM)
- Storage: 20 GB GP3
- Cost: **$25/month**

**Subtotal RDS:** $107.24/month (on-demand) | $74.35/month (optimized)

#### 1.3 Storage - S3

**Raw Data Storage**
- Purpose: Scraped PDFs, JSON, HTML files
- Estimated Size: 50 GB initial, +5 GB/month growth
- Storage Class: S3 Standard
- Cost: **$1.15/month** (50 GB × $0.023/GB-month)

**Processed Data Archives**
- Purpose: Historical CSV exports, backups
- Estimated Size: 25 GB
- Storage Class: S3 Glacier Instant Retrieval
- Cost: **$1.00/month** (25 GB × $0.004/GB-month)

**Database Snapshots**
- Purpose: RDS snapshots, point-in-time recovery
- Estimated Size: 30 GB
- Cost: **$2.85/month** (30 GB × $0.095/GB-month)

**API Response Cache**
- Purpose: CloudFront caching, static assets
- Estimated Size: 5 GB
- Cost: **$0.12/month** (5 GB × $0.023/GB-month)

**Data Transfer Out**
- Estimated: 100 GB/month (API responses, downloads)
- Cost: **$9.00/month** (100 GB × $0.09/GB for first 10 TB)

**Subtotal S3:** $14.12/month

#### 1.4 Content Delivery - CloudFront CDN

**Purpose:** Cache API responses, serve static dashboard assets
- Requests: 500,000/month
- Data Transfer Out: 50 GB/month
- Cost Breakdown:
  - HTTP/HTTPS Requests: **$0.42/month** (500K × $0.0075/10K requests)
  - Data Transfer: **$4.25/month** (50 GB × $0.085/GB)
- **Total: $4.67/month**

#### 1.5 Caching - ElastiCache Redis

**Cache Instance**
- Instance Type: `cache.t3.micro` (0.5 GB memory)
- Purpose: API response caching, session management
- Cost: **$11.52/month** (730 hours × $0.0158/hour)
- Alternative: Amazon MemoryDB (higher cost, Redis-compatible)

#### 1.6 Load Balancing - Application Load Balancer

**Purpose:** Distribute traffic, SSL termination, health checks
- Load Balancer Hours: **$16.20/month** (730 hours × $0.0225/hour)
- Load Balancer Capacity Units (LCU): **$5.50/month** (estimated)
- **Total: $21.70/month**
- **Alternative:** Use EC2 instance with Nginx ($0 additional cost for low traffic)

#### 1.7 Monitoring & Logging - CloudWatch

**Logs**
- Ingestion: 10 GB/month
- Storage: 10 GB (1-month retention)
- Cost: **$5.00/month** (10 GB × $0.50/GB)

**Metrics & Dashboards**
- Custom Metrics: 50 metrics
- Dashboard: 3 dashboards
- Cost: **$3.00/month**

**Alarms**
- Metric Alarms: 10 alarms
- Cost: **$1.00/month** (10 × $0.10/alarm)

**Subtotal CloudWatch:** $9.00/month

#### 1.8 Secrets Management - AWS Secrets Manager

**Secrets Stored**
- Database credentials, API keys, third-party tokens
- Number of Secrets: 5
- API Calls: 10,000/month
- Cost:
  - Secret Storage: **$2.00/month** (5 × $0.40/secret)
  - API Calls: **$0.50/month** (10K × $0.05/10K calls)
- **Total: $2.50/month**

#### 1.9 Container Registry - ECR (Optional)

**Purpose:** Docker image storage for containerized deployment
- Storage: 5 GB
- Data Transfer: 10 GB/month
- Cost: **$0.50/month** (5 GB × $0.10/GB-month)

#### 1.10 Auto Scaling & Elastic IPs

**Elastic IP Addresses**
- Production: 1 static IP
- Cost: **$3.65/month** (1 IP × $0.005/hour × 730 hours)

**Auto Scaling Groups**
- Cost: **$0/month** (no charge for Auto Scaling service)

---

### Total AWS Infrastructure Costs (Monthly)

| Service | On-Demand | Optimized (Reserved/Spot) |
|---------|-----------|---------------------------|
| EC2 Compute | $90.55 | $40.88 |
| RDS Database | $107.24 | $74.35 |
| S3 Storage | $14.12 | $14.12 |
| CloudFront CDN | $4.67 | $4.67 |
| ElastiCache Redis | $11.52 | $11.52 |
| Load Balancer | $21.70 | $0 (Use Nginx) |
| CloudWatch | $9.00 | $9.00 |
| Secrets Manager | $2.50 | $2.50 |
| ECR | $0.50 | $0.50 |
| Elastic IP | $3.65 | $3.65 |
| **TOTAL** | **$265.45/month** | **$161.19/month** |

**AWS Pricing Calculator Link:**
[https://calculator.aws/#/estimate?id=marine-safety-db-baseline-2025](https://calculator.aws/#/estimate?id=marine-safety-db-baseline-2025)
*(Note: Generate actual link using AWS Pricing Calculator with above specifications)*

---

## 2. Third-Party Services

### 2.1 Geocoding Services

**Mapbox Geocoding API**
- Purpose: Convert addresses to coordinates, reverse geocoding
- Estimated Volume: 10,000 requests/month (initial data load higher)
- Pricing Tiers:
  - Free Tier: 100,000 requests/month (sufficient for initial use)
  - Pay-as-you-go: $0.0050 per request after free tier
- **Cost: $0/month** (within free tier)
- **Fallback:** OpenStreetMap Nominatim (free, self-hosted rate limits)

**Google Maps Geocoding API (Alternative)**
- Pricing: $0.005 per request
- Free Tier: $200 credit/month (40,000 requests)
- **Cost: $0/month** (within free tier initially)

### 2.2 Vessel Data Enrichment

**MarineTraffic API** (Optional)
- Purpose: Vessel details, IMO lookup, AIS data
- Pricing: Custom enterprise pricing (estimated $200-500/month for moderate use)
- Alternative: Free public sources (slower, limited)
- **Cost: $0 - $500/month** (optional feature)

### 2.3 Weather Data Integration

**OpenWeatherMap API**
- Purpose: Historical weather data for incident correlation
- Pricing: Free tier (60 calls/min) or Professional ($40/month, unlimited)
- **Cost: $0 - $40/month**

**NOAA Data** (Alternative)
- Free government data, no API limits
- **Cost: $0/month**

### 2.4 SSL Certificates

**AWS Certificate Manager (ACM)**
- Purpose: HTTPS certificates for API and dashboard
- **Cost: $0/month** (free with AWS)

**Alternative: Let's Encrypt**
- Free automated SSL certificates
- **Cost: $0/month**

### 2.5 Domain Name

**Domain Registration**
- Example: `marinesafetydb.com`
- Registrar: Route 53, Namecheap, etc.
- **Cost: $12/year** ($1/month)

**DNS Hosting (Route 53)**
- Hosted Zone: $0.50/month
- Queries: $0.40/month (estimated 1M queries)
- **Cost: $0.90/month**

### 2.6 Monitoring & Uptime

**UptimeRobot** (Free Tier)
- Purpose: Uptime monitoring, alerting
- 50 monitors, 5-minute checks
- **Cost: $0/month**

**Alternative: Pingdom**
- Paid service with advanced features
- **Cost: $10/month**

### 2.7 Error Tracking

**Sentry**
- Purpose: Error tracking, performance monitoring
- Free Tier: 5,000 events/month
- Developer Plan: $26/month (50,000 events)
- **Cost: $0 - $26/month**

### 2.8 Email Service (Alerts & Notifications)

**Amazon SES**
- Purpose: Send alert emails, user notifications
- Pricing: $0.10 per 1,000 emails
- Estimated: 500 emails/month
- **Cost: $0.05/month**

**Alternative: SendGrid**
- Free Tier: 100 emails/day (3,000/month)
- **Cost: $0/month** (within free tier)

---

### Total Third-Party Services (Monthly)

| Service | Cost | Required |
|---------|------|----------|
| Geocoding (Mapbox) | $0 | Yes |
| Vessel Data (MarineTraffic) | $0 - $500 | Optional |
| Weather Data (OpenWeather) | $0 - $40 | Optional |
| SSL Certificates | $0 | Yes |
| Domain & DNS | $1.90 | Yes |
| Uptime Monitoring | $0 - $10 | Yes |
| Error Tracking | $0 - $26 | Recommended |
| Email Service | $0 - $0.05 | Yes |
| **TOTAL** | **$1.90 - $577.95/month** | - |

**Recommended Baseline:** $1.90/month (free tiers)
**With Optional Services:** $50 - $200/month

---

## 3. Development Costs

### Hourly Rate Assumptions
- **Senior Developer:** $125/hour
- **Mid-Level Developer:** $85/hour
- **Junior Developer:** $50/hour
- **DevOps Engineer:** $100/hour
- **Data Engineer:** $110/hour
- **QA Engineer:** $75/hour

### 3.1 Phase 1: Foundation (Weeks 1-4, 160 hours)

| Role | Hours | Rate | Cost |
|------|-------|------|------|
| Senior Developer (Architecture) | 40 | $125 | $5,000 |
| Mid-Level Developer (Implementation) | 80 | $85 | $6,800 |
| Junior Developer (Testing, Setup) | 40 | $50 | $2,000 |
| **Phase 1 Subtotal** | **160** | - | **$13,800** |

**Deliverables:**
- Database schema design and implementation
- SQLAlchemy models
- Base infrastructure code
- Configuration management
- Initial test suite
- Logging framework

---

### 3.2 Phase 2: Data Collection - US Sources (Weeks 5-8, 160 hours)

| Role | Hours | Rate | Cost |
|------|-------|------|------|
| Data Engineer (Scrapers) | 80 | $110 | $8,800 |
| Mid-Level Developer (Processing) | 60 | $85 | $5,100 |
| Junior Developer (Testing) | 20 | $50 | $1,000 |
| **Phase 2 Subtotal** | **160** | - | **$14,900** |

**Deliverables:**
- USCG, NTSB, BTS, USCG Boating scrapers
- Data processing pipeline
- Deduplication logic
- Historical US data collection

---

### 3.3 Phase 3: Data Collection - International (Weeks 9-12, 140 hours)

| Role | Hours | Rate | Cost |
|------|-------|------|------|
| Data Engineer (Scrapers) | 80 | $110 | $8,800 |
| Mid-Level Developer (Enrichment) | 40 | $85 | $3,400 |
| Junior Developer (Testing) | 20 | $50 | $1,000 |
| **Phase 3 Subtotal** | **140** | - | **$13,200** |

**Deliverables:**
- IMCA, IMO, III scrapers
- Data enrichment (geocoding, vessel lookup)
- International historical data
- Cross-source deduplication

---

### 3.4 Phase 4: Analysis Tools (Weeks 13-16, 160 hours)

| Role | Hours | Rate | Cost |
|------|-------|------|------|
| Senior Developer (ML, Analytics) | 60 | $125 | $7,500 |
| Mid-Level Developer (Implementation) | 80 | $85 | $6,800 |
| Junior Developer (Notebooks) | 20 | $50 | $1,000 |
| **Phase 4 Subtotal** | **160** | - | **$15,300** |

**Deliverables:**
- Trend analyzer, geographic analyzer
- Root cause analyzer, risk calculator
- Statistical summaries, BSEE comparison
- Jupyter notebooks for analysis

---

### 3.5 Phase 5: API & Visualization (Weeks 17-20, 160 hours)

| Role | Hours | Rate | Cost |
|------|-------|------|------|
| Senior Developer (FastAPI, Architecture) | 60 | $125 | $7,500 |
| Mid-Level Developer (Dashboard) | 80 | $85 | $6,800 |
| Junior Developer (Testing, Docs) | 20 | $50 | $1,000 |
| **Phase 5 Subtotal** | **160** | - | **$15,300** |

**Deliverables:**
- REST API (FastAPI)
- Interactive dashboard (Streamlit/Dash)
- API documentation (OpenAPI/Swagger)
- Interactive maps (Folium/Mapbox)
- Export functionality

---

### 3.6 Phase 6: Automation & Testing (Weeks 21-24, 140 hours)

| Role | Hours | Rate | Cost |
|------|-------|------|------|
| Senior Developer (Automation) | 40 | $125 | $5,000 |
| Mid-Level Developer (Testing) | 60 | $85 | $5,100 |
| QA Engineer (Test Suite) | 40 | $75 | $3,000 |
| **Phase 6 Subtotal** | **140** | - | **$13,100** |

**Deliverables:**
- Scheduled scraping (Celery/cron)
- Automated data processing
- Comprehensive pytest suite
- Integration and performance tests
- Error monitoring setup

---

### 3.7 Phase 7: Deployment & Optimization (Weeks 25-28, 160 hours)

| Role | Hours | Rate | Cost |
|------|-------|------|------|
| DevOps Engineer (Deployment) | 80 | $100 | $8,000 |
| Senior Developer (Optimization) | 40 | $125 | $5,000 |
| Mid-Level Developer (Monitoring) | 40 | $85 | $3,400 |
| **Phase 7 Subtotal** | **160** | - | **$16,400** |

**Deliverables:**
- Production PostgreSQL setup
- Docker containerization
- AWS deployment and CI/CD
- Performance optimization
- Caching implementation
- Monitoring and alerting
- User documentation

---

### Total Development Costs (28 Weeks)

| Phase | Hours | Cost |
|-------|-------|------|
| Phase 1: Foundation | 160 | $13,800 |
| Phase 2: US Data Collection | 160 | $14,900 |
| Phase 3: International Data | 140 | $13,200 |
| Phase 4: Analysis Tools | 160 | $15,300 |
| Phase 5: API & Visualization | 160 | $15,300 |
| Phase 6: Automation & Testing | 140 | $13,100 |
| Phase 7: Deployment & Optimization | 160 | $16,400 |
| **TOTAL** | **1,080 hours** | **$102,000** |

**Blended Rate:** $94.44/hour

**Cost Reduction Scenarios:**
- **Junior-Heavy Team (50% junior, 35% mid, 15% senior):** $68,000 (-33%)
- **Mid-Level Team (20% senior, 60% mid, 20% junior):** $85,000 (-17%)
- **Offshore Development (50% cost reduction):** $51,000 (-50%)
- **Open Source Contributions (community support):** $75,000 (-26%)

**Recommended Budget Range:** $75,000 - $102,000

---

## 4. Operational Costs

### 4.1 Ongoing Maintenance & Support

**System Administration (Monthly)**
- Infrastructure monitoring: 10 hours/month
- Security updates: 5 hours/month
- Database optimization: 5 hours/month
- Rate: $100/hour (DevOps)
- **Cost: $2,000/month** ($24,000/year)

**Development & Bug Fixes (Monthly)**
- Bug fixes: 10 hours/month
- Minor enhancements: 10 hours/month
- Rate: $85/hour (Mid-Level)
- **Cost: $1,700/month** ($20,400/year)

**Data Quality & Curation (Monthly)**
- Data validation: 8 hours/month
- Quality checks: 4 hours/month
- Rate: $110/hour (Data Engineer)
- **Cost: $1,320/month** ($15,840/year)

**Total Ongoing Development:** $5,020/month ($60,240/year)

**Cost Reduction Option:**
- Part-time maintenance (25% effort): $1,255/month ($15,060/year)

### 4.2 Infrastructure Operations

**AWS Monthly Costs (from Section 1)**
- Baseline: $265.45/month (on-demand)
- Optimized: $161.19/month (reserved/spot)

**Third-Party Services (from Section 2)**
- Baseline: $1.90/month
- With Optional: $50 - $200/month

**Total Infrastructure:** $163 - $465/month

### 4.3 Data Collection Costs

**Compute for Scraping**
- Already included in EC2 spot instance costs ($13.50/month)

**Bandwidth for Scraping**
- Estimated: 50 GB/month downloads
- AWS Data Transfer In: **$0/month** (free)

**Storage Growth**
- 5 GB/month × $0.023/GB = **$0.12/month** added cost
- Annual Storage Growth: ~$1.44/year

### 4.4 Backup & Disaster Recovery

**Automated Database Backups**
- Included in RDS costs (7-day retention)

**Long-Term Archives (Quarterly Snapshots)**
- 4 snapshots/year × 100 GB × $0.004/GB (Glacier)
- **Cost: $1.60/year** ($0.13/month)

**Disaster Recovery Testing**
- Quarterly DR drills: 4 hours/quarter
- Rate: $100/hour
- **Cost: $1,600/year** ($133/month)

### 4.5 Security & Compliance

**SSL Certificates**
- **Cost: $0/month** (AWS ACM free)

**Security Audits**
- Annual penetration testing: $3,000/year
- Quarterly security reviews: $2,000/year
- **Cost: $5,000/year** ($417/month)

**Vulnerability Scanning**
- AWS Inspector or third-party
- **Cost: $50/month**

### 4.6 Documentation & Training

**Documentation Maintenance**
- Update user guides, API docs: 8 hours/quarter
- Rate: $85/hour
- **Cost: $2,720/year** ($227/month)

**User Training (Optional)**
- Quarterly webinars or training sessions
- **Cost: $500/quarter** ($167/month)

---

### Total Operational Costs (Annual)

| Category | Monthly | Annual |
|----------|---------|--------|
| System Administration | $2,000 | $24,000 |
| Development & Bug Fixes | $1,700 | $20,400 |
| Data Quality & Curation | $1,320 | $15,840 |
| Infrastructure (AWS) | $161 - $265 | $1,932 - $3,180 |
| Third-Party Services | $2 - $200 | $24 - $2,400 |
| Disaster Recovery Testing | $133 | $1,600 |
| Security & Compliance | $467 | $5,600 |
| Documentation & Training | $227 - $394 | $2,720 - $4,720 |
| **TOTAL** | **$6,010 - $6,779/month** | **$72,116 - $81,348/year** |

**Minimum Operating Cost (Part-Time Maintenance):**
- Infrastructure: $161/month
- Third-Party: $2/month
- Part-Time Maintenance (25%): $1,255/month
- **Total: $1,418/month** ($17,016/year)

---

## 5. Scaling Scenarios

### 5.1 Current Baseline (1x)

**Assumptions:**
- 50,000 incidents in database
- 10,000 API requests/month
- 100 GB total storage
- 5 concurrent users
- Daily data updates

**Infrastructure Cost:** $161/month (optimized)

---

### 5.2 Medium Scale (10x Traffic)

**Assumptions:**
- 500,000 incidents in database
- 100,000 API requests/month
- 500 GB total storage
- 50 concurrent users
- Hourly data updates

**Infrastructure Changes:**
- EC2 API Server: Upgrade to `t3.large` (2 → 4 vCPU, 4 → 8 GB)
  - Cost: $60.74/month (on-demand) | $36.44/month (reserved)
- RDS Database: Upgrade to `db.r6g.large` (2 → 2 vCPU, 4 → 16 GB)
  - Cost: $175/month | $105/month (reserved)
- S3 Storage: 500 GB
  - Cost: $11.50/month
- CloudFront: 5M requests, 500 GB transfer
  - Cost: $46/month
- ElastiCache: Upgrade to `cache.t3.medium` (0.5 → 3.2 GB)
  - Cost: $46.20/month
- Data Transfer: 1 TB/month
  - Cost: $90/month

**10x Infrastructure Cost:** $385/month (on-demand) | $335/month (reserved)

**Increase:** +139% over baseline

---

### 5.3 High Scale (100x Traffic)

**Assumptions:**
- 5,000,000 incidents in database
- 1,000,000 API requests/month
- 2 TB total storage
- 500 concurrent users
- Real-time data updates

**Infrastructure Changes:**
- EC2 API Server: 2× `t3.xlarge` (behind load balancer)
  - Cost: 2 × $121.47 = $242.94/month | $145.77/month (reserved)
- RDS Database: Upgrade to `db.r6g.xlarge` (4 vCPU, 32 GB) + Read Replica
  - Primary: $350/month | $210/month (reserved)
  - Read Replica: $350/month | $210/month (reserved)
  - Total: $700/month | $420/month
- S3 Storage: 2 TB
  - Cost: $46/month
- CloudFront: 50M requests, 5 TB transfer
  - Cost: $462/month
- ElastiCache: `cache.r6g.large` (13.07 GB)
  - Cost: $154/month
- Load Balancer: Application Load Balancer
  - Cost: $21.70 + $55 LCU = $76.70/month
- Data Transfer: 10 TB/month
  - Cost: $850/month

**100x Infrastructure Cost:** $2,532/month (on-demand) | $1,905/month (reserved)

**Increase:** +1,470% over baseline (15.7x cost for 100x traffic)

---

### Scaling Cost Summary

| Metric | 1x (Baseline) | 10x | 100x |
|--------|---------------|-----|------|
| Incidents in DB | 50,000 | 500,000 | 5,000,000 |
| API Requests/Month | 10,000 | 100,000 | 1,000,000 |
| Storage | 100 GB | 500 GB | 2 TB |
| Concurrent Users | 5 | 50 | 500 |
| **Infrastructure Cost (Optimized)** | **$161/month** | **$335/month** | **$1,905/month** |
| **Cost per 1,000 Incidents** | **$3.22** | **$0.67** | **$0.38** |
| **Cost per 1,000 API Requests** | **$16.10** | **$3.35** | **$1.91** |

**Key Insight:** Infrastructure costs scale sub-linearly due to economies of scale and caching efficiencies.

---

## 6. Cost Optimization

### 6.1 Reserved Instances (1-Year Commitment)

**EC2 Savings:**
- `t3.medium` API Server: $30.37 → $18.25/month (-40%)
- `t3.small` Dev Server: $15.18 → $9.13/month (-40%)

**RDS Savings:**
- `db.t3.medium` Production: $60.74 → $36.44/month (-40%)

**Total Annual Savings:** $494/year ($41/month)

**Break-Even:** Immediate (assuming 12-month uptime)

---

### 6.2 Spot Instances for Processing

**Data Processing Worker:**
- On-Demand: $45/month (150 hours × $0.0416/hour)
- Spot: $13.50/month (150 hours × $0.09/hour avg)
- **Savings: $31.50/month** ($378/year)

**Risk Mitigation:**
- Use Spot Fleet with on-demand fallback
- Implement checkpointing for long-running jobs

---

### 6.3 S3 Lifecycle Policies

**Archive Old Data:**
- Move raw PDFs older than 6 months to Glacier Instant Retrieval
  - Standard: $0.023/GB-month
  - Glacier IR: $0.004/GB-month
  - Savings: $0.019/GB-month

**Example:**
- 40 GB archived data
- Savings: $0.76/month ($9.12/year)

**Intelligent-Tiering:**
- Automatic cost optimization for varying access patterns
- No retrieval fees, $0.0025/1,000 objects monitoring fee
- Recommended for unpredictable access patterns

---

### 6.4 Caching Strategy

**ElastiCache for API Responses:**
- Cache frequently accessed queries (e.g., statistics, aggregations)
- Reduce database load and RDS instance size
- Potential Savings: Defer `db.t3.medium` → `db.t3.large` upgrade

**Example:**
- 70% cache hit rate at 10x scale
- Avoid database upgrade: **$50/month savings**

**CloudFront Caching:**
- Cache API responses with TTL (5-60 minutes)
- Reduce origin requests to API server
- Reduce data transfer from origin

**Example:**
- 80% cache hit rate
- Data transfer savings: $40/month at 10x scale

---

### 6.5 Database Optimization

**Read Replicas:**
- Use read replicas for analytics queries
- Offload read traffic from primary database
- Cost: +$36.44/month (reserved)
- Benefit: Improved performance, avoid larger primary instance

**Connection Pooling:**
- Use PgBouncer or SQLAlchemy pooling
- Reduce connection overhead
- Defer instance upgrades

**Indexing Strategy:**
- Optimize indexes for common queries
- Reduce query execution time and I/O costs
- Estimated I/O Savings: $2-5/month

---

### 6.6 Alternative Database Options

**Amazon Aurora Serverless v2:**
- Pay-per-second billing for compute
- Auto-scales from 0.5 to 128 ACUs (Aurora Capacity Units)
- Pricing: $0.12 per ACU-hour
- **Example Cost:**
  - Average 2 ACUs × 730 hours = $175/month
  - Comparable to `db.t3.medium` but auto-scales

**PostgreSQL on EC2:**
- Self-managed PostgreSQL
- Lower cost than RDS
- Requires more operational overhead
- **Example Cost:**
  - `t3.medium` EC2: $18.25/month (reserved)
  - 100 GB EBS SSD: $10/month
  - Total: $28.25/month vs $74.35/month RDS
  - **Savings: $46/month** ($552/year)
- **Trade-off:** Manual backups, patching, management

---

### 6.7 Cost Monitoring & Budgets

**AWS Budgets:**
- Set monthly budget alerts
- Example: Alert at 80% and 100% of $200/month budget
- Cost: **$0.02/budget/day** ($0.60/month for 1 budget)

**AWS Cost Explorer:**
- Identify cost anomalies
- Rightsizing recommendations
- Free service

**AWS Trusted Advisor:**
- Cost optimization checks
- Idle resource detection
- Free with Business support plan

---

### Total Optimization Savings (Annual)

| Optimization | Savings (Annual) |
|--------------|------------------|
| Reserved Instances | $494 |
| Spot Instances | $378 |
| S3 Lifecycle Policies | $109 |
| Caching (defer upgrades) | $600 |
| Database Optimization (PostgreSQL on EC2) | $552 |
| **TOTAL** | **$2,133/year** |

**Optimized Infrastructure Cost:** $161/month → $126/month (-22%)

---

## 7. Budget Breakdown by Phase

### 7.1 Phase-by-Phase Investment

| Phase | Development Cost | Infrastructure (4 weeks) | Total |
|-------|------------------|--------------------------|-------|
| Phase 1: Foundation (Weeks 1-4) | $13,800 | $644 | $14,444 |
| Phase 2: US Data Collection (Weeks 5-8) | $14,900 | $644 | $15,544 |
| Phase 3: International Data (Weeks 9-12) | $13,200 | $644 | $13,844 |
| Phase 4: Analysis Tools (Weeks 13-16) | $15,300 | $644 | $15,944 |
| Phase 5: API & Visualization (Weeks 17-20) | $15,300 | $644 | $15,944 |
| Phase 6: Automation & Testing (Weeks 21-24) | $13,100 | $644 | $13,744 |
| Phase 7: Deployment & Optimization (Weeks 25-28) | $16,400 | $644 | $17,044 |
| **TOTAL (28 Weeks)** | **$102,000** | **$4,508** | **$106,508** |

**Monthly Infrastructure During Development:** $161/month (optimized)

---

### 7.2 First Year Total Cost

| Category | Cost |
|----------|------|
| Development (Phases 1-7) | $102,000 |
| Infrastructure (28 weeks development) | $4,508 |
| Infrastructure (24 weeks post-launch) | $3,864 |
| Third-Party Services (12 months) | $23 - $2,400 |
| Operational (6 months post-launch) | $7,109 - $20,337 |
| **TOTAL FIRST YEAR** | **$117,504 - $133,109** |

**Cost Reduction Scenarios:**
- Junior-Heavy Team: $83,504 - $99,109 (-29%)
- Offshore Development: $68,504 - $84,109 (-42%)
- Part-Time Maintenance: $109,895 - $112,772 (-11% operational)

---

### 7.3 Year 2+ Annual Operating Cost

| Category | Cost |
|----------|------|
| Infrastructure (AWS) | $1,932 - $3,180 |
| Third-Party Services | $23 - $2,400 |
| Ongoing Maintenance (Part-Time) | $15,060 |
| Disaster Recovery Testing | $1,600 |
| Security & Compliance | $5,600 |
| Documentation & Training | $2,720 - $4,720 |
| **TOTAL ANNUAL (Year 2+)** | **$26,935 - $31,560** |

**Monthly:** $2,245 - $2,630

**With Full-Time Maintenance:** $72,116 - $81,348/year

---

## 8. ROI Analysis

### 8.1 Value Delivered

**Quantifiable Benefits:**

1. **Research Time Savings**
   - Manual data collection: 200 hours/year per researcher
   - Cost per researcher: $125/hour × 200 hours = $25,000/year
   - Database access: 10 hours/year per researcher
   - **Savings per User:** $23,750/year

2. **Insurance Risk Assessment**
   - Improved actuarial models using comprehensive incident data
   - Estimated value: $100,000 - $500,000/year for insurance companies
   - Database subscription fee: $5,000 - $20,000/year
   - **ROI for Customer:** 5-25x

3. **Safety Compliance & Training**
   - Reduced incident rates through data-driven safety programs
   - Cost of major marine incident: $1M - $100M+
   - Preventing 1 incident every 5 years: **$200,000 - $20M/year value**

4. **Operational Benchmarking**
   - Companies compare safety performance against industry
   - Estimated value: $50,000 - $200,000/year for fleet operators

**Total Estimated Value to Stakeholders:** $250,000 - $20M+/year

---

### 8.2 Revenue Potential (Subscription Model)

**Potential Customer Segments:**

1. **Academic Institutions**
   - Target: 50 universities/research institutions
   - Price: $2,000 - $5,000/year
   - **Revenue:** $100,000 - $250,000/year

2. **Insurance Companies**
   - Target: 10 marine insurance firms
   - Price: $10,000 - $25,000/year
   - **Revenue:** $100,000 - $250,000/year

3. **Maritime Companies (Fleet Operators)**
   - Target: 100 companies
   - Price: $3,000 - $10,000/year
   - **Revenue:** $300,000 - $1,000,000/year

4. **Government Agencies**
   - Target: 5 agencies (USCG, NTSB, state agencies)
   - Price: $5,000 - $15,000/year
   - **Revenue:** $25,000 - $75,000/year

5. **API Access (Developers/Startups)**
   - Target: 200 API users
   - Price: $500 - $2,000/year
   - **Revenue:** $100,000 - $400,000/year

**Total Potential Revenue:** $625,000 - $1,975,000/year

**Conservative Estimate (20% Adoption):** $125,000 - $395,000/year

---

### 8.3 Break-Even Analysis

**Scenario 1: Free Public Access (Funded by Grants/Government)**
- No revenue
- Annual Operating Cost: $26,935 - $31,560
- **Funding Required:** $27,000 - $32,000/year

**Scenario 2: Freemium Model**
- Free tier: 80% of users
- Paid tier: 20% of users
- Revenue: $125,000 - $395,000/year (conservative)
- Operating Cost: $26,935 - $31,560/year
- **Profit:** $93,440 - $368,065/year
- **Break-Even:** Month 3-8 after launch (covering development cost)

**Scenario 3: Full Subscription Model**
- Revenue: $625,000 - $1,975,000/year
- Operating Cost: $72,116 - $81,348/year (full-time staff)
- **Profit:** $552,884 - $1,902,884/year
- **Break-Even:** Month 2-3 after launch

---

### 8.4 ROI Summary

**Investment:**
- Development: $102,000
- First Year Total: $117,504 - $133,109

**Return (Conservative, Year 1):**
- Revenue: $125,000 - $395,000
- Operating Cost: $26,935 - $31,560
- Net Profit: $93,440 - $368,065

**ROI (Year 1):**
- Conservative: **79% - 176%**
- Optimistic: **370% - 1,317%**

**Payback Period:**
- Conservative: 10-14 months
- Optimistic: 4-6 months

---

## 9. Cost Monitoring

### 9.1 AWS Cost Monitoring Setup

**AWS Budgets:**
```yaml
Budget 1: Monthly Infrastructure
  Amount: $200/month
  Alerts:
    - 80% threshold: Email to DevOps team
    - 100% threshold: Email to management + Slack alert
    - 120% threshold: Email + SMS + PagerDuty

Budget 2: Annual Total Cost
  Amount: $2,400/year
  Alerts:
    - 80% threshold: Quarterly review
    - 100% threshold: Immediate action
```

**Cost Allocation Tags:**
```yaml
Tags:
  Project: marine-safety-db
  Environment: production | staging | development
  CostCenter: research | operations
  Component: compute | database | storage | networking
```

**Example Query:**
- "Show costs for Project=marine-safety-db, Environment=production, by Service"

---

### 9.2 Cost Anomaly Detection

**AWS Cost Anomaly Detection:**
- Machine learning-based anomaly detection
- Alerts for unusual spending patterns
- Example: Detect 50% increase in S3 costs due to scraping error

**Custom Alerts:**
```python
# CloudWatch Alarm for High Data Transfer
Alarm: HighDataTransferCost
Metric: AWS/Billing/EstimatedCharges
Dimension: ServiceName=AmazonS3
Threshold: $50/day
Action: SNS notification to cost-alert-topic
```

---

### 9.3 Regular Cost Reviews

**Weekly:**
- Review AWS Cost Explorer dashboard
- Check for unexpected charges
- Verify resource utilization

**Monthly:**
- Compare actual vs budgeted costs
- Analyze cost trends
- Identify optimization opportunities
- Update forecasts

**Quarterly:**
- Review reserved instance utilization
- Evaluate savings plans
- Assess third-party service usage
- Plan capacity changes

---

### 9.4 Cost Optimization Dashboards

**CloudWatch Dashboard:**
```yaml
Widgets:
  - EstimatedCharges by Service (last 30 days)
  - EC2 CPU Utilization (avg, p95)
  - RDS Database Connections (count)
  - S3 Storage Growth (GB)
  - API Request Rate (requests/sec)
  - Cache Hit Rate (%)
  - Data Transfer (GB/day)
```

**Custom Dashboard (Grafana/Tableau):**
- Cost per incident record processed
- Cost per API request
- Cost per user (if subscription model)
- Cost trend projections
- Budget variance analysis

---

### 9.5 Automated Cost Governance

**Resource Tagging Policy:**
- All resources must have `Project`, `Environment`, `CostCenter` tags
- Automated enforcement via AWS Config Rules

**Auto-Shutdown for Dev/Staging:**
```yaml
Schedule:
  Dev Environment:
    Start: Monday-Friday 8 AM
    Stop: Monday-Friday 6 PM
  Staging Environment:
    Start: On-demand (manual)
    Stop: After 8 hours
```

**Savings:** ~$500/month (70% reduction in dev/staging costs)

**Instance Rightsizing:**
- Monthly AWS Compute Optimizer reports
- Automated recommendations for underutilized instances
- Potential Savings: 10-30% of compute costs

---

## 10. Alternative Pricing

### 10.1 AWS vs GCP vs Azure

#### Compute Comparison (API Server: 2 vCPU, 4 GB RAM)

| Provider | Instance Type | On-Demand (Monthly) | Reserved (1-Year) | Spot/Preemptible |
|----------|---------------|---------------------|-------------------|------------------|
| **AWS** | t3.medium | $30.37 | $18.25 | $9.00 |
| **GCP** | e2-standard-2 | $48.92 | $31.80 (1-year commitment) | $14.68 |
| **Azure** | B2s (2 vCPU, 4 GB) | $30.37 | $19.71 (1-year reserved) | $12.15 |

**Winner:** AWS (lowest reserved and spot pricing)

---

#### Database Comparison (Managed PostgreSQL: 2 vCPU, 4 GB RAM)

| Provider | Service | Instance Type | Monthly Cost | Storage (100 GB) |
|----------|---------|---------------|--------------|------------------|
| **AWS** | RDS PostgreSQL | db.t3.medium | $60.74 | $11.50 |
| **GCP** | Cloud SQL PostgreSQL | db-custom-2-4096 | $84.53 | $17.00 |
| **Azure** | Azure Database for PostgreSQL | General Purpose, 2 vCores | $73.00 | $11.50 |

**Total Database Cost (Compute + Storage 100 GB):**
- AWS: **$72.24/month** (on-demand) | $47.85/month (reserved)
- GCP: **$101.53/month**
- Azure: **$84.50/month**

**Winner:** AWS (lowest cost, especially with reserved instances)

---

#### Storage Comparison (S3-equivalent: 100 GB Standard)

| Provider | Service | Storage Cost (GB/month) | Data Transfer Out (GB) | Requests (per 1,000) |
|----------|---------|-------------------------|------------------------|----------------------|
| **AWS** | S3 Standard | $0.023 | $0.09 (first 10 TB) | $0.0004 (GET) |
| **GCP** | Cloud Storage Standard | $0.020 | $0.12 (first 10 TB) | $0.0004 (GET) |
| **Azure** | Blob Storage (Hot) | $0.018 | $0.087 (first 10 TB) | $0.0004 (GET) |

**100 GB Storage + 100 GB Transfer:**
- AWS: $2.30 + $9.00 = **$11.30/month**
- GCP: $2.00 + $12.00 = **$14.00/month**
- Azure: $1.80 + $8.70 = **$10.50/month**

**Winner:** Azure (storage), AWS (overall ecosystem)

---

#### CDN Comparison (CloudFront-equivalent)

| Provider | Service | Requests (per 10K) | Data Transfer (GB) |
|----------|---------|--------------------|--------------------|
| **AWS** | CloudFront | $0.0075 | $0.085 |
| **GCP** | Cloud CDN | $0.0075 | $0.08 |
| **Azure** | Azure CDN | $0.0081 | $0.087 |
| **Cloudflare** | Cloudflare CDN | Free (up to limits) | Free (unlimited) |

**500K Requests + 50 GB Transfer:**
- AWS: $0.38 + $4.25 = **$4.63/month**
- GCP: $0.38 + $4.00 = **$4.38/month**
- Azure: $0.41 + $4.35 = **$4.76/month**
- Cloudflare: **$0/month** (Free plan) or $20/month (Pro plan with extra features)

**Winner:** Cloudflare (free tier) or GCP (paid)

---

### 10.2 Total Infrastructure Cost Comparison

**Baseline Configuration:**
- API Server: 2 vCPU, 4 GB RAM (reserved/committed)
- Database: PostgreSQL 2 vCPU, 4 GB RAM, 100 GB storage (reserved/committed)
- Storage: 100 GB object storage, 100 GB transfer/month
- CDN: 500K requests, 50 GB transfer
- Caching: 0.5 GB Redis-equivalent (reserved/committed)
- Monitoring: CloudWatch-equivalent (basic)

| Provider | Monthly Cost (Optimized) | Notes |
|----------|--------------------------|-------|
| **AWS** | **$161** | With reserved instances, Spot for workers |
| **GCP** | **$195** | With committed use discounts |
| **Azure** | **$178** | With reserved instances |
| **Hybrid (Cloudflare CDN + AWS)** | **$156** | Best of breed |

**Winner:** AWS (most cost-effective with optimization)
**Runner-Up:** Hybrid approach using Cloudflare CDN

---

### 10.3 Alternative Deployment Options

#### DigitalOcean (Simpler, SMB-focused)

**Droplet (VM):**
- API Server: 2 vCPU, 4 GB RAM = **$24/month**
- Database: 2 vCPU, 4 GB RAM, 30 GB SSD = **$60/month**
- Spaces (Object Storage): 250 GB + 1 TB outbound = **$5/month**
- Load Balancer: **$12/month**
- **Total: $101/month**

**Pros:**
- Simpler pricing, predictable costs
- Lower cost for small/medium workloads
- Great developer experience

**Cons:**
- Less scalable than AWS/GCP/Azure
- Fewer advanced services (managed Redis, advanced monitoring)
- Limited global regions

---

#### Hetzner Cloud (European, Budget)

**Server:**
- CX21 (2 vCPU, 4 GB RAM, 40 GB SSD): **€5.39/month** (~$5.75)
- PostgreSQL Database (managed): Not available (self-hosted)
- Storage Box (100 GB): **€3.81/month** (~$4.07)
- **Total: ~$10 - $15/month** (self-managed database)

**Pros:**
- Extremely low cost
- Good performance
- EU data residency

**Cons:**
- Manual database management
- Limited to European regions
- Fewer managed services

---

#### Linode (Now Akamai Cloud Computing)

**Instance:**
- Linode 4 GB (2 vCPU, 4 GB RAM, 80 GB SSD): **$24/month**
- Managed Database (PostgreSQL 4 GB): **$60/month**
- Object Storage: 250 GB = **$5/month**
- **Total: $89/month**

**Pros:**
- Competitive pricing
- Good performance
- Akamai CDN integration

**Cons:**
- Smaller ecosystem than AWS/GCP/Azure

---

#### Self-Hosted (On-Premises or Dedicated Server)

**Dedicated Server (OVH, Hetzner):**
- Example: Intel Xeon, 32 GB RAM, 2× 512 GB SSD
- Cost: **€49/month** (~$52)
- Includes: Compute, storage, bandwidth (100 Mbps unmetered)

**Pros:**
- Lowest cost for high-utilization workloads
- Predictable pricing
- No vendor lock-in

**Cons:**
- Manual management (OS, database, backups)
- No auto-scaling
- Higher operational overhead
- Single point of failure (need redundancy)

**Estimated Total Cost (with admin time):**
- Server: $52/month
- Admin/DevOps time (10 hours/month × $100/hour): $1,000/month
- **Total: $1,052/month** (not cost-effective unless extremely high utilization)

---

### 10.4 Cost Comparison Summary (Monthly)

| Platform | Infrastructure | Admin Overhead | Total | Scalability | Ease of Use |
|----------|----------------|----------------|-------|-------------|-------------|
| **AWS (Optimized)** | $161 | Low | $161 | Excellent | Moderate |
| **GCP** | $195 | Low | $195 | Excellent | Moderate |
| **Azure** | $178 | Low | $178 | Excellent | Moderate |
| **DigitalOcean** | $101 | Low | $101 | Good | Excellent |
| **Linode** | $89 | Low | $89 | Good | Good |
| **Hetzner Cloud** | $15 | High | $515 | Limited | Fair |
| **Self-Hosted** | $52 | Very High | $1,052 | Limited | Poor |

**Recommendation:**
- **Best for Production:** AWS (mature ecosystem, scalability)
- **Best for Budget-Conscious:** DigitalOcean or Linode
- **Best for EU/GDPR:** Hetzner Cloud (with self-managed DB) or AWS Frankfurt

---

## Conclusion

### Total Cost Summary

**Development (One-Time):**
- Standard Team: $102,000
- Budget Option: $68,000 - $85,000
- Premium Option: $102,000+

**Infrastructure (Monthly):**
- Baseline (AWS Optimized): $161/month
- With Optional Services: $211 - $361/month
- 10x Scale: $335/month
- 100x Scale: $1,905/month

**First Year Total:**
- Development + Infrastructure + Operations: $117,504 - $133,109
- With Budget Optimizations: $83,504 - $99,109

**Annual Operating (Year 2+):**
- Part-Time Maintenance: $26,935 - $31,560/year
- Full-Time Team: $72,116 - $81,348/year

**Cost per Incident Record:**
- Initial: $3.22 per 1,000 records (50K records)
- At Scale (5M records): $0.38 per 1,000 records

**ROI:**
- Payback Period: 4-14 months (depending on revenue model)
- Year 1 ROI: 79% - 1,317%
- Annual Value Delivered: $250,000 - $20M+ to stakeholders

---

### Cost Optimization Recommendations

1. **Use AWS Reserved Instances:** Save $494/year immediately
2. **Implement Spot Instances for Workers:** Save $378/year
3. **Deploy Caching Aggressively:** Defer scaling costs ($600/year)
4. **S3 Lifecycle Policies:** Save $109/year on storage
5. **Consider PostgreSQL on EC2:** Save $552/year (trade-off: more admin)
6. **Use Cloudflare CDN (Free Tier):** Save $56/year
7. **Auto-Shutdown Dev/Staging:** Save $500/month on non-production

**Total Annual Savings Potential:** $2,133+ per year

---

### Budget Allocation Recommendation

**Recommended Budget (First Year):**
- Development: $75,000 - $85,000 (mid-level team with junior support)
- Infrastructure: $2,000 (optimized AWS)
- Third-Party Services: $250 (free tiers + domain)
- Operations (6 months): $9,000 (part-time maintenance)
- **Total: $86,250 - $96,250**

**Recommended Budget (Year 2+):**
- Infrastructure: $2,000/year
- Third-Party Services: $250/year
- Operations: $18,000/year (part-time)
- Security & Compliance: $5,600/year
- **Total: $25,850/year**

---

**Document Version:** 1.0.0
**Last Updated:** 2025-10-03
**Next Review:** After Phase 1 completion

**AWS Pricing Calculator Links:**
- Baseline Configuration: [Generate using AWS Pricing Calculator](https://calculator.aws/)
- 10x Scale: [Generate using AWS Pricing Calculator](https://calculator.aws/)
- 100x Scale: [Generate using AWS Pricing Calculator](https://calculator.aws/)

**Appendix Resources:**
- AWS TCO Calculator: https://aws.amazon.com/tco-calculator/
- GCP Pricing Calculator: https://cloud.google.com/products/calculator
- Azure Pricing Calculator: https://azure.microsoft.com/en-us/pricing/calculator/
