# Solution Architecture Document
## Claims Processing Platform

### Document Information
| Field | Value |
|-------|-------|
| **Project** | Claims Processing Platform |
| **Version** | 1.0 |
| **Date** | January 2026 |
| **Status** | Draft |

---

## Executive Summary

The Claims Processing Platform is a comprehensive healthcare claims management system designed to digitize the end-to-end claims submission, administration, and automated adjudication process based on Alberta Health Care Insurance Plan (AHCIP) rules. This document outlines the solution architecture for a scalable, secure, and HIPAA-compliant platform that serves healthcare providers, administrators, and adjudicators.

---

## 1. System Architecture

### 1.1 High-Level System Overview

The platform follows a modern three-tier architecture with clear separation between presentation, application, and data layers, enhanced with cloud-native services for scalability, security, and reliability.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION LAYER                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │ Provider Claims  │  │ Admin Dashboard  │  │ Claim Template   │          │
│  │     Portal       │  │                  │  │   Management     │          │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘          │
│           │                     │                     │                     │
│  ┌────────┴─────────┐  ┌────────┴─────────┐  ┌────────┴─────────┐          │
│  │ Claim Form       │  │ Rule Config      │  │ Claim Form       │          │
│  │ Builder          │  │ Interface        │  │ Builder          │          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                        ┌───────────┴───────────┐
                        │    CloudFront/CDN     │
                        └───────────┬───────────┘
                                    │
┌─────────────────────────────────────────────────────────────────────────────┐
│                           EDGE & SECURITY LAYER                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │     WAF     │  │ API Gateway │  │    Load     │  │  Identity   │        │
│  │  (OWASP)   │  │             │  │  Balancer   │  │  Provider   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────────────────┐
│                          APPLICATION LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │                     API MIDDLEWARE STACK                          │      │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │      │
│  │  │   Auth   │ │   Rate   │ │Validation│ │  Audit   │ │  CSRF  │ │      │
│  │  │Middleware│ │ Limiting │ │Middleware│ │ Logging  │ │ Protect│ │      │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘ │      │
│  └──────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────┐       │
│  │                        API SERVICES                              │       │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐   │       │
│  │  │  Claims    │ │   Forms    │ │   Rules    │ │  Document  │   │       │
│  │  │    API     │ │Templates   │ │  Engine    │ │ Management │   │       │
│  │  │  Service   │ │    API     │ │    API     │ │    API     │   │       │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────────┘   │       │
│  │  ┌────────────┐ ┌────────────┐                                  │       │
│  │  │   AHCIP    │ │   Audit    │                                  │       │
│  │  │Code Lookup │ │ Compliance │                                  │       │
│  │  │    API     │ │    API     │                                  │       │
│  │  └────────────┘ └────────────┘                                  │       │
│  └─────────────────────────────────────────────────────────────────┘       │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────┐       │
│  │                       CONTROLLERS                                │       │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐│       │
│  │  │ Claims   │ │  Forms   │ │  Rules   │ │ Document │ │ Audit  ││       │
│  │  │Controller│ │Controller│ │Controller│ │Controller│ │  Ctrl  ││       │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘│       │
│  │  ┌──────────────┐ ┌──────────────┐                              │       │
│  │  │ Adjudication │ │ Rule Testing │                              │       │
│  │  │  Workflow    │ │  Controller  │                              │       │
│  │  │  Controller  │ │              │                              │       │
│  │  └──────────────┘ └──────────────┘                              │       │
│  └─────────────────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DATA LAYER                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │ PostgreSQL RDS   │  │  Redis Cache     │  │  S3/Blob Storage │          │
│  │  (Multi-AZ)      │  │   Cluster        │  │   (Documents)    │          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL SERVICES                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐               │
│  │   AHCIP    │ │Notification│ │  Identity  │ │   Secrets  │               │
│  │Fee Schedule│ │  Service   │ │  Provider  │ │  Manager   │               │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Key Architectural Principles

| Principle | Description | Implementation |
|-----------|-------------|----------------|
| **Security-First** | HIPAA compliance throughout | Encryption at rest/transit, RBAC, audit logging |
| **Scalability** | Handle peak AHCIP processing loads | Auto-scaling, load balancing, caching |
| **Resilience** | High availability with disaster recovery | Multi-AZ, cross-region replication |
| **Modularity** | Loosely coupled services | API-first design, service boundaries |
| **Testability** | Comprehensive quality assurance | Test modes, contract testing, E2E automation |

### 1.3 System Context (C4 Level 1)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SYSTEM CONTEXT                                  │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌───────────────┐                              ┌───────────────┐
    │   Healthcare  │                              │   AHCIP Fee   │
    │   Provider    │                              │   Schedule    │
    │               │                              │   Service     │
    └───────┬───────┘                              └───────┬───────┘
            │ Submits claims,                              │
            │ uploads documents                            │ Provides codes
            │                                              │ & fee schedules
            ▼                                              ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                                                             │
    │              CLAIMS PROCESSING PLATFORM                     │
    │                                                             │
    │  • Digital claims submission & tracking                     │
    │  • Automated adjudication via rules engine                  │
    │  • Document management                                      │
    │  • Compliance & audit reporting                             │
    │                                                             │
    └─────────────────────────────────────────────────────────────┘
            │                                              │
            │ Manage forms,                                │
            │ configure rules                              │ Sends notifications
            ▼                                              ▼
    ┌───────────────┐                              ┌───────────────┐
    │ Administrator │                              │  Notification │
    │ / Adjudicator │                              │    Service    │
    └───────────────┘                              └───────────────┘
```

---

## 2. Component Design

### 2.1 Presentation Layer Components

#### 2.1.1 Provider Claims Portal
**Purpose:** Primary interface for healthcare providers to manage claims

| Component | Description | Key Features |
|-----------|-------------|--------------|
| **Claims List Table** | Sortable, filterable table of claims | Status indicators, action buttons, pagination |
| **Claim Submission Form** | Dynamic form renderer | Template-based, validation, draft saving |
| **Claim Status Tracker** | Status and history view | Timeline, notifications, document attachments |
| **Claim Detail Modal** | Full claim information display | History, attachments, adjudication results |
| **Document Uploader** | File attachment interface | Drag-drop, validation, progress indicators |

```typescript
// Claim Submission Form Structure
interface ClaimSubmissionFormProps {
  templateId: string;
  claimId?: string; // For editing drafts
  onSave: (draft: ClaimDraft) => void;
  onSubmit: (claim: Claim) => void;
}

// Key hooks
- useClaimFormState(): Manages field values, validation, draft status
- useAHCIPCodeSearch(): Procedure code lookup with auto-pricing
- useDocumentUpload(): File validation and upload handling
```

#### 2.1.2 Admin Dashboard
**Purpose:** Centralized administration interface

| Component | Description | Epic Reference |
|-----------|-------------|----------------|
| **Admin Stats Cards** | Key metrics display | E-005: Pending, flagged claims |
| **Recent Activity Feed** | Real-time system events | WebSocket-based updates |
| **Quick Actions Panel** | Shortcut navigation | Review, rules, reports |
| **Flagged Claims Queue** | Manual review queue | E-005: Adjudication workflow |

#### 2.1.3 Form & Template Management
**Purpose:** Administrative form design and template versioning

| Component | Description | Epic Reference |
|-----------|-------------|----------------|
| **Form Designer Canvas** | Drag-drop form builder | E-002-F-001 |
| **Form Field Palette** | Available field types | E-002-F-001 |
| **Template List View** | Template management | E-002-F-003 |
| **Template Version History** | Version tracking, rollback | E-002-F-003 |

#### 2.1.4 Rule Configuration Interface
**Purpose:** Define and manage adjudication rules

| Component | Description | Epic Reference |
|-----------|-------------|----------------|
| **Rule Editor Component** | Rule definition builder | E-004-F-001 |
| **Rule Test Case Selector** | Test case configuration | E-006-F-002 |
| **Rule Test Results Panel** | Test execution results | E-006-F-002 |

### 2.2 Application Layer Components

#### 2.2.1 API Services

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           API SERVICE ARCHITECTURE                           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              API GATEWAY                                     │
│  • Rate limiting: 10K req/min per provider                                  │
│  • SSL termination, API versioning                                          │
│  • WAF integration                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────┬───────────┼───────────┬───────────────┐
        ▼               ▼           ▼           ▼               ▼
┌───────────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
│ /api/v1/claims│ │/api/v1/   │ │/api/v1/   │ │/api/v1/   │ │/api/v1/   │
│               │ │ forms     │ │  rules    │ │ documents │ │  audit    │
├───────────────┤ ├───────────┤ ├───────────┤ ├───────────┤ ├───────────┤
│ Claims API    │ │ Forms &   │ │ Rules     │ │ Document  │ │ Audit     │
│ Service       │ │ Templates │ │ Engine    │ │ Management│ │ Compliance│
│               │ │ API       │ │ API       │ │ API       │ │ API       │
└───────┬───────┘ └─────┬─────┘ └─────┬─────┘ └─────┬─────┘ └─────┬─────┘
        │               │             │             │             │
        ▼               ▼             ▼             ▼             ▼
┌───────────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
│    Claims     │ │   Forms   │ │   Rules   │ │  Document │ │   Audit   │
│   Router      │ │  Router   │ │  Router   │ │  Router   │ │  Router   │
└───────────────┘ └───────────┘ └───────────┘ └───────────┘ └───────────┘
```

##### Claims API Service
**Endpoint:** `/api/v1/claims`
**Description:** Handles all claims-related operations

| Method | Endpoint | Description | Epic Reference |
|--------|----------|-------------|----------------|
| POST | `/claims` | Create new claim | E-003-F-001 |
| PUT | `/claims/:id/draft` | Save draft | E-003-F-001-S-001 |
| POST | `/claims/:id/submit` | Submit claim | E-003-F-001-S-002 |
| GET | `/claims` | List provider claims | E-003-F-003 |
| GET | `/claims/:id` | Get claim details | E-003-F-003 |
| GET | `/claims/:id/status` | Get status history | E-003-F-003 |

```typescript
// Claims Controller Interface
interface ClaimsController {
  // Core CRUD
  createClaim(providerId: string, data: ClaimCreateDTO): Promise<Claim>;
  saveDraft(claimId: string, data: ClaimDraftDTO): Promise<Claim>;
  submitClaim(claimId: string): Promise<Claim>;
  getClaim(claimId: string): Promise<ClaimWithDetails>;
  listClaims(providerId: string, filters: ClaimFilters): Promise<PaginatedResult<Claim>>;
  
  // Test mode support
  setTestMode(enabled: boolean): void;
  injectMockProvider(provider: MockProvider): void;
}
```

##### Forms & Templates API Service
**Endpoint:** `/api/v1/forms`, `/api/v1/templates`
**Description:** Manages claim form definitions and templates

| Method | Endpoint | Description | Epic Reference |
|--------|----------|-------------|----------------|
| POST | `/forms` | Create form definition | E-002-F-001 |
| PUT | `/forms/:id` | Update form | E-002-F-001 |
| GET | `/templates` | List templates | E-002-F-003 |
| POST | `/templates/:id/duplicate` | Duplicate template | E-002-F-003 |
| GET | `/templates/:id/versions` | Get version history | E-002-F-003 |
| POST | `/templates/:id/rollback` | Rollback to version | E-002-F-003 |

##### Rules Engine API Service
**Endpoint:** `/api/v1/rules`
**Description:** Rule management and execution

| Method | Endpoint | Description | Epic Reference |
|--------|----------|-------------|----------------|
| POST | `/rules` | Create rule | E-004-F-001, E-006-F-001 |
| PUT | `/rules/:id` | Update rule | E-006-F-001 |
| GET | `/rules/:id/versions` | Version history | E-006-F-001 |
| POST | `/rules/test` | Test rules (dry-run) | E-006-F-002 |
| POST | `/rules/execute` | Execute against claim | E-004 |

##### Document Management API Service
**Endpoint:** `/api/v1/documents`
**Description:** Secure document handling

| Method | Endpoint | Description | Epic Reference |
|--------|----------|-------------|----------------|
| POST | `/documents/upload` | Upload document | E-004-F-001 |
| GET | `/documents/:id` | Get document | E-004-F-002 |
| GET | `/claims/:id/documents` | List claim documents | E-004-F-002 |
| DELETE | `/documents/:id` | Delete document | E-004-F-001 |

##### AHCIP Code Lookup API Service
**Endpoint:** `/api/v1/ahcip-codes`
**Description:** Procedure code search and fee schedules

| Method | Endpoint | Description | Epic Reference |
|--------|----------|-------------|----------------|
| GET | `/ahcip-codes/search` | Search codes | E-002-F-002 |
| GET | `/ahcip-codes/:code` | Get code details | E-002-F-002 |
| GET | `/ahcip-codes/:code/fee` | Get fee schedule | E-002-F-002 |

#### 2.2.2 Controllers

##### Claims Controller
**Purpose:** Core claims lifecycle management

```typescript
class ClaimsController {
  // Dependencies
  private claimsService: ClaimsService;
  private validationService: ValidationService;
  private auditLogger: AuditLogger;
  
  // Test hooks
  private testMode: boolean = false;
  private mockProviders: Map<string, MockProvider> = new Map();
  
  async submitClaim(claimId: string, userId: string): Promise<Claim> {
    // 1. Validate claim completeness
    const claim = await this.claimsService.getClaim(claimId);
    const validation = await this.validationService.validateClaim(claim);
    
    if (!validation.isValid) {
      throw new ValidationError(validation.errors);
    }
    
    // 2. Update status and trigger adjudication
    const submittedClaim = await this.claimsService.updateStatus(
      claimId, 
      ClaimStatus.SUBMITTED
    );
    
    // 3. Audit logging
    await this.auditLogger.log({
      action: 'CLAIM_SUBMITTED',
      claimId,
      userId,
      timestamp: new Date()
    });
    
    // 4. Trigger async adjudication workflow
    await this.eventBus.publish('claim.submitted', { claimId });
    
    return submittedClaim;
  }
}
```

##### Adjudication Workflow Controller
**Purpose:** Orchestrates automated adjudication and manual review

```typescript
class AdjudicationWorkflowController {
  async processSubmittedClaim(claimId: string): Promise<AdjudicationResult> {
    const claim = await this.claimsService.getClaim(claimId);
    
    // 1. Get applicable rules
    const rules = await this.rulesService.getActiveRules(claim.serviceDate);
    
    // 2. Execute validation rules
    const validationResults = await this.rulesEngine.executeValidationRules(
      claim, 
      rules.filter(r => r.type === 'validation')
    );
    
    // 3. Execute adjudication rules
    const adjudicationResults = await this.rulesEngine.executeAdjudicationRules(
      claim,
      rules.filter(r => r.type === 'adjudication')
    );
    
    // 4. Determine outcome
    if (adjudicationResults.requiresManualReview) {
      await this.flagForManualReview(claimId, adjudicationResults.flagReasons);
      return { status: 'PENDING_REVIEW', flagged: true };
    }
    
    // 5. Calculate payment
    const payment = await this.feeCalculator.calculatePayment(
      claim,
      adjudicationResults
    );
    
    // 6. Update claim with results
    return await this.claimsService.finalizeAdjudication(claimId, {
      status: adjudicationResults.approved ? 'APPROVED' : 'DENIED',
      paymentAmount: payment.amount,
      rulesApplied: adjudicationResults.rulesApplied,
      denialReason: adjudicationResults.denialReason
    });
  }
}
```

##### Rule Testing Controller
**Purpose:** Test rules against sample data without affecting live claims

```typescript
class RuleTestingController {
  async testRules(testRequest: RuleTestRequest): Promise<RuleTestResult> {
    // 1. Create isolated test context
    const testContext = this.createTestContext();
    
    // 2. Load test data or generate synthetic data
    const testClaim = testRequest.claimData || 
      await this.testDataFactory.generateClaim(testRequest.scenario);
    
    // 3. Execute rules in dry-run mode
    const results = await this.rulesEngine.execute(
      testClaim,
      testRequest.ruleIds,
      { dryRun: true, testContext }
    );
    
    // 4. Generate detailed trace
    return {
      passed: results.assertions.every(a => a.passed),
      executionTrace: results.trace,
      coverageReport: this.generateCoverageReport(results),
      assertions: results.assertions
    };
  }
}
```

#### 2.2.3 Middleware Stack

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MIDDLEWARE PIPELINE                                 │
└─────────────────────────────────────────────────────────────────────────────┘

  Request → ┌──────────────┐ → ┌──────────────┐ → ┌──────────────┐
            │ Correlation  │   │     Auth     │   │    Rate      │
            │     ID       │   │  Middleware  │   │  Limiting    │
            └──────────────┘   └──────────────┘   └──────────────┘
                    │                  │                  │
                    ▼                  ▼                  ▼
            ┌──────────────┐ → ┌──────────────┐ → ┌──────────────┐
            │    CSRF      │   │    Input     │   │  Validation  │
            │  Protection  │   │ Sanitization │   │  Middleware  │
            └──────────────┘   └──────────────┘   └──────────────┘
                    │                  │                  │
                    ▼                  ▼                  ▼
            ┌──────────────┐ → ┌──────────────┐ → ┌──────────────┐
            │    Audit     │   │  Test Mode   │   │  Controller  │
            │   Logging    │   │  (QA only)   │   │              │
            └──────────────┘   └──────────────┘   └──────────────┘
```

| Middleware | Purpose | Key Features |
|------------|---------|--------------|
| **Request Correlation** | Distributed tracing | Generates/propagates correlation IDs |
| **Auth Middleware** | Authentication/Authorization | JWT RS256, OAuth 2.0, SAML SSO |
| **Rate Limiting** | API abuse prevention | 100 req/min per provider, burst handling |
| **CSRF Protection** | Anti-CSRF attacks | Token validation, SameSite cookies |
| **Input Sanitization** | Security hardening | XSS, SQL injection prevention |
| **Validation Middleware** | Schema validation | JSON schema, detailed errors |
| **Audit Logging** | HIPAA compliance | PHI access logging, PII masking |
| **Test Mode (QA)** | Test isolation | Synthetic data injection |

### 2.3 Data Layer Components

#### 2.3.1 Database Design

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DATABASE ARCHITECTURE                                 │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────────────────┐
                    │     PostgreSQL RDS (Primary)    │
                    │          Multi-AZ               │
                    └────────────────┬────────────────┘
                                     │
           ┌─────────────────────────┼─────────────────────────┐
           │                         │                         │
           ▼                         ▼                         ▼
    ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
    │   Read      │          │   Read      │          │  Standby    │
    │  Replica 1  │          │  Replica 2  │          │   (AZ-B)    │
    │ (Reporting) │          │   (API)     │          │             │
    └─────────────┘          └─────────────┘          └─────────────┘
```

**Entity Relationship Diagram:**

```
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│    providers     │       │      users       │       │     claims       │
├──────────────────┤       ├──────────────────┤       ├──────────────────┤
│ provider_id (PK) │◄──┐   │ user_id (PK)     │   ┌──│ claim_id (PK)    │
│ npi_number (UQ)  │   │   │ email (UQ)       │   │  │ provider_id (FK) │──┐
│ provider_name    │   │   │ password_hash    │   │  │ patient_info     │  │
│ organization     │   │   │ role             │   │  │ service_date     │  │
│ address          │   │   │ provider_id (FK) │───┘  │ status           │  │
│ contact_email    │   │   │ mfa_enabled      │      │ total_amount     │  │
│ phone            │   │   │ last_login       │      │ submitted_at     │  │
│ status           │   │   │ created_at       │      │ adjudicated_at   │  │
│ created_at       │   │   └──────────────────┘      │ created_at       │  │
│ updated_at       │   │                             │ updated_at       │  │
└──────────────────┘   │                             └──────────────────┘  │
                       │                                      │            │
                       │    ┌──────────────────┐              │            │
                       │    │  claim_fields    │              │            │
                       │    ├──────────────────┤              │            │
                       │    │ field_id (PK)    │              │            │
                       │    │ claim_id (FK)    │──────────────┘            │
                       │    │ field_name       │                           │
                       │    │ field_value      │                           │
                       │    │ created_at       │                           │
                       │    └──────────────────┘                           │
                       │                                                   │
┌──────────────────┐   │    ┌──────────────────┐       ┌──────────────────┐
│     rules        │   │    │   documents      │       │adjudication_     │
├──────────────────┤   │    ├──────────────────┤       │results           │
│ rule_id (PK)     │   │    │ document_id (PK) │       ├──────────────────┤
│ rule_name        │   │    │ claim_id (FK)    │───────│ result_id (PK)   │
│ rule_type        │   │    │ file_path        │       │ claim_id (FK)    │──┐
│ condition_logic  │   │    │ file_type        │       │ status           │  │
│ action_type      │   │    │ file_size        │       │ payment_amount   │  │
│ priority         │   │    │ uploaded_at      │       │ denial_reason    │  │
│ is_active        │   │    │ created_at       │       │ processed_by(FK) │  │
│ effective_from   │   │    └──────────────────┘       │ processed_at     │  │
│ effective_to     │   │                               │ rules_applied    │  │
│ created_by (FK)  │───┘                               │ created_at       │  │
│ created_at       │                                   └──────────────────┘  │
│ updated_at       │                                            │            │
└──────────────────┘                                            │            │
        │                                                       │            │
        │           ┌──────────────────┐                        │            │
        │           │  rule_versions   │                        │            │
        │           ├──────────────────┤                        │            │
        └──────────►│ version_id (PK)  │                        │            │
                    │ rule_id (FK)     │                        │            │
                    │ version_number   │                        │            │
                    │ condition_logic  │                        │            │
                    │ created_by (FK)  │                        │            │
                    │ created_at       │                        │            │
                    └──────────────────┘                        │            │
                                                                │            │
┌──────────────────┐       ┌──────────────────┐                 │            │
│form_definitions  │       │ form_templates   │                 │            │
├──────────────────┤       ├──────────────────┤                 │            │
│ form_id (PK)     │◄──────│ template_id (PK) │                 │            │
│ field_definitions│       │ form_id (FK)     │                 │            │
│ validation_rules │       │ version_number   │                 │            │
│ is_active        │       │ template_name    │                 │            │
│ created_at       │       │ metadata         │                 │            │
│ updated_at       │       │ created_at       │                 │            │
└──────────────────┘       └──────────────────┘                 │            │
                                                                │            │
┌──────────────────┐       ┌──────────────────┐                 │            │
│  ahcip_codes     │       │   audit_logs     │                 │            │
├──────────────────┤       ├──────────────────┤                 │            │
│ id (PK)          │       │ log_id (PK)      │                 │            │
│ procedure_code   │       │ claim_id (FK)    │─────────────────┘            │
│ description      │       │ rule_id (FK)     │                              │
│ category         │       │ execution_result │                              │
│ fee_amount       │       │ decision_rationale│                             │
│ effective_date   │       │ user_id (FK)     │──────────────────────────────┘
│ expiration_date  │       │ timestamp        │
│ created_at       │       │ created_at       │
│ updated_at       │       └──────────────────┘
└──────────────────┘

┌──────────────────┐
│    sessions      │
├──────────────────┤
│ session_id (PK)  │
│ user_id (FK)     │
│ token_hash       │
│ created_at       │
│ expires_at       │
│ ip_address       │
│ user_agent       │
└──────────────────┘
```

#### 2.3.2 Schema Definitions

##### Claims Schema
```typescript
interface ClaimsSchema {
  claim_id: UUID;           // Primary Key
  provider_id: UUID;        // FK to providers
  patient_info: EncryptedJSON; // AES-256 encrypted PHI
  service_lines: ServiceLine[];
  status: ClaimStatus;      // draft|submitted|in_review|adjudicated|paid|denied
  total_amount: Decimal;
  submitted_at: Timestamp | null;
  adjudicated_at: Timestamp | null;
  created_at: Timestamp;
  updated_at: Timestamp;
}

type ClaimStatus = 'draft' | 'submitted' | 'in_review' | 'adjudicated' | 'paid' | 'denied';

interface ServiceLine {
  procedure_code: string;
  description: string;
  service_date: Date;
  quantity: number;
  unit_price: Decimal;
  total: Decimal;
}
```

##### Rules Engine Schema
```typescript
interface RuleSchema {
  rule_id: UUID;
  rule_name: string;
  rule_type: 'validation' | 'adjudication';
  condition_logic: ConditionLogic; // JSON structure
  action_type: 'approve' | 'deny' | 'flag' | 'calculate';
  priority: number;
  is_active: boolean;
  effective_from: Date;
  effective_to: Date | null;
  created_by: UUID;
  created_at: Timestamp;
  updated_at: Timestamp;
}

interface ConditionLogic {
  type: 'AND' | 'OR' | 'NOT' | 'COMPARISON';
  conditions?: ConditionLogic[];
  field?: string;
  operator?: '=' | '!=' | '>' | '<' | 'IN' | 'CONTAINS';
  value?: any;
}
```

##### Audit Logs Schema
```typescript
interface AuditLogSchema {
  log_id: UUID;
  claim_id: UUID | null;
  rule_id: UUID | null;
  action: AuditAction;
  execution_result: string;
  decision_rationale: string;
  user_id: UUID;
  ip_address: string;
  user_agent: string;
  phi_accessed: boolean;
  masked_fields: string[];
  timestamp: Timestamp;
}

type AuditAction = 
  | 'CLAIM_CREATED' 
  | 'CLAIM_SUBMITTED' 
  | 'CLAIM_ADJUDICATED'
  | 'PHI_ACCESSED'
  | 'RULE_EXECUTED'
  | 'DOCUMENT_UPLOADED'
  | 'USER_LOGIN'
  | 'USER_LOGOUT';
```

---

## 3. Integration Patterns

### 3.1 Communication Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      INTEGRATION ARCHITECTURE                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┐                          ┌─────────────────────┐
│   SYNCHRONOUS       │                          │   ASYNCHRONOUS      │
│   (REST APIs)       │                          │   (Event-Driven)    │
├─────────────────────┤                          ├─────────────────────┤
│ • Claims CRUD       │                          │ • Claim Submission  │
│ • Form retrieval    │                          │   Events            │
│ • AHCIP code lookup │                          │ • Adjudication      │
│ • User auth         │                          │   Workflows         │
│ • Document download │                          │ • Notification      │
└─────────────────────┘                          │   Triggers          │
         │                                       │ • Audit Log Events  │
         ▼                                       └─────────────────────┘
┌───────────────────────────────────────┐                 │
│           API GATEWAY                 │                 ▼
│  • Request routing                    │        ┌─────────────────────┐
│  • Rate limiting                      │        │   MESSAGE QUEUE     │
│  • Authentication                     │        │   (SQS/Service Bus) │
│  • SSL termination                    │        ├─────────────────────┤
└───────────────────────────────────────┘        │ • claim.submitted   │
         │                                       │ • claim.adjudicated │
         ▼                                       │ • claim.flagged     │
┌───────────────────────────────────────┐        │ • notification.send │
│       INTERNAL SERVICE MESH           │        └─────────────────────┘
│  • Service discovery                  │                 │
│  • Load balancing                     │                 ▼
│  • Circuit breaker                    │        ┌─────────────────────┐
│  • Retry policies                     │        │   EVENT HANDLERS    │
└───────────────────────────────────────┘        │  (Lambda/Functions) │
                                                 └─────────────────────┘
```

### 3.2 API Integration Contracts

#### 3.2.1 Claims API Contract (OpenAPI Summary)

```yaml
openapi: 3.0.3
info:
  title: Claims Processing API
  version: 1.0.0

paths:
  /api/v1/claims:
    post:
      summary: Create new claim
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ClaimCreateRequest'
      responses:
        '201':
          description: Claim created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Claim'
        '400':
          description: Validation error
        '401':
          description: Unauthorized
        '429':
          description: Rate limit exceeded

  /api/v1/claims/{claimId}/submit:
    post:
      summary: Submit claim for adjudication
      parameters:
        - name: claimId
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Claim submitted
        '400':
          description: Claim incomplete
        '404':
          description: Claim not found

components:
  schemas:
    ClaimCreateRequest:
      type: object
      required:
        - templateId
        - patientInfo
        - serviceLines
      properties:
        templateId:
          type: string
          format: uuid
        patientInfo:
          type: object
        serviceLines:
          type: array
          items:
            $ref: '#/components/schemas/ServiceLine'

    ServiceLine:
      type: object
      properties:
        procedureCode:
          type: string
          pattern: '^[A-Z0-9]{5,10}$'
        serviceDate:
          type: string
          format: date
        quantity:
          type: integer
          minimum: 1
```

#### 3.2.2 External Service Integrations

##### AHCIP Fee Schedule Service
```typescript
interface AHCIPServiceClient {
  // Search procedure codes
  searchCodes(query: string, options?: SearchOptions): Promise<AHCIPCode[]>;
  
  // Get specific code with fee
  getCodeDetails(code: string, effectiveDate: Date): Promise<AHCIPCodeDetails>;
  
  // Bulk fee lookup for claim processing
  getFeeSchedule(codes: string[], effectiveDate: Date): Promise<FeeScheduleResult>;
}

// Integration config
const ahcipConfig = {
  baseUrl: process.env.AHCIP_SERVICE_URL,
  timeout: 5000,
  retries: 3,
  circuitBreaker: {
    threshold: 5,
    timeout: 30000
  }
};
```

##### Notification Service
```typescript
interface NotificationServiceClient {
  // Send claim status notification
  sendClaimNotification(notification: ClaimNotification): Promise<void>;
  
  // Supported channels
  channels: ['email', 'sms', 'in-app'];
}

// Event-driven integration
eventBus.subscribe('claim.adjudicated', async (event) => {
  await notificationService.sendClaimNotification({
    providerId: event.providerId,
    claimId: event.claimId,
    status: event.status,
    channel: 'email',
    template: 'CLAIM_STATUS_UPDATE'
  });
});
```

##### Identity Provider Integration
```typescript
interface IdentityProviderClient {
  // OAuth 2.0 / OIDC
  authenticateUser(credentials: Credentials): Promise<TokenResponse>;
  validateToken(token: string): Promise<TokenValidation>;
  refreshToken(refreshToken: string): Promise<TokenResponse>;
  
  // SAML SSO (Enterprise)
  initiateSAMLLogin(idpEntityId: string): Promise<SAMLRequest>;
  processSAMLResponse(response: SAMLResponse): Promise<UserSession>;
}
```

### 3.3 Event-Driven Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EVENT FLOW DIAGRAM                                   │
└─────────────────────────────────────────────────────────────────────────────┘

    Claim Submission Flow:
    ═══════════════════════

    [Provider]                  [Claims API]              [Event Bus]
        │                           │                         │
        │  POST /claims/:id/submit  │                         │
        │ ─────────────────────────►│                         │
        │                           │                         │
        │                           │ publish: claim.submitted│
        │                           │────────────────────────►│
        │                           │                         │
        │   200 OK                  │                         │
        │◄───────────────────────── │                         │
        │                           │                         │
                                    │                         │
    [Adjudication Service]          │         [Event Bus]     │
        │                           │              │          │
        │ subscribe: claim.submitted│              │          │
        │◄─────────────────────────────────────────┤          │
        │                           │              │          │
        │ execute rules             │              │          │
        │                           │              │          │
        │ publish: claim.adjudicated│              │          │
        │──────────────────────────────────────────►          │
        │                           │              │          │
                                    │              │          │
    [Notification Service]          │              │          │
        │                           │              │          │
        │ subscribe: claim.adjudicated             │          │
        │◄─────────────────────────────────────────┤          │
        │                           │              │          │
        │ send email notification   │              │          │
        │                           │              │          │
```

### 3.4 Contract Testing Strategy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CONTRACT TESTING WORKFLOW                               │
└─────────────────────────────────────────────────────────────────────────────┘

    [Frontend Hooks]           [Pact Broker]           [Backend Services]
         │                          │                        │
         │  1. Generate consumer    │                        │
         │     contracts            │                        │
         │─────────────────────────►│                        │
         │                          │                        │
         │                          │  2. Provider verifies  │
         │                          │     contracts          │
         │                          │───────────────────────►│
         │                          │                        │
         │                          │  3. Verification       │
         │                          │     results            │
         │                          │◄───────────────────────│
         │                          │                        │
         │  4. Can-I-Deploy check   │                        │
         │◄─────────────────────────│                        │
         │                          │                        │

    Contract Testing Service (Pact):
    • Validates API producer-consumer agreements
    • Frontend hooks define expected responses
    • Backend services verify contracts in CI
    • Detects breaking changes before deployment
```

---

## 4. Data Architecture

### 4.1 Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DATA FLOW ARCHITECTURE                              │
└─────────────────────────────────────────────────────────────────────────────┘

                           CLAIM SUBMISSION DATA FLOW
    ══════════════════════════════════════════════════════════════════════

    [Provider Portal]
          │
          │ 1. Claim form data
          ▼
    ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
    │  Validation     │────►│   Encryption    │────►│  Claims API     │
    │  Middleware     │     │   (AES-256)     │     │  Service        │
    └─────────────────┘     └─────────────────┘     └─────────────────┘
                                                            │
                                                            ▼
    ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
    │   Audit Log     │◄────│  Claims         │────►│  PostgreSQL     │
    │   Service       │     │  Controller     │     │  (encrypted)    │
    └─────────────────┘     └─────────────────┘     └─────────────────┘
                                    │
                                    │ 2. Documents
                                    ▼
    ┌─────────────────┐     ┌─────────────────┐
    │  Virus Scan     │────►│  S3/Blob        │
    │  (ClamAV)       │     │  (SSE-S3)       │
    └─────────────────┘     └─────────────────┘


                           ADJUDICATION DATA FLOW
    ══════════════════════════════════════════════════════════════════════

    [Event: claim.submitted]
          │
          │ 1. Fetch claim data
          ▼
    ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
    │  Adjudication   │────►│  Rules Engine   │────►│  AHCIP Fee      │
    │  Workflow       │     │                 │     │  Service        │
    └─────────────────┘     └─────────────────┘     └─────────────────┘
          │                         │
          │ 2. Apply rules          │ 3. Calculate fees
          ▼                         ▼
    ┌─────────────────┐     ┌─────────────────┐
    │  Adjudication   │────►│  Audit Log      │
    │  Results        │     │  (HIPAA)        │
    └─────────────────┘     └─────────────────┘
          │
          │ 4. Update claim status
          ▼
    ┌─────────────────┐     ┌─────────────────┐
    │  Notification   │────►│  Email/SMS      │
    │  Service        │     │  Provider       │
    └─────────────────┘     └─────────────────┘
```

### 4.2 Data Storage Strategy

| Data Type | Storage | Encryption | Retention | Backup |
|-----------|---------|------------|-----------|--------|
| **Claims Data** | PostgreSQL RDS | AES-256 (at rest) + TLS 1.3 (transit) | 7 years (regulatory) | Daily automated, cross-region |
| **PHI Fields** | PostgreSQL (encrypted column) | AES-256 with KMS | 7 years | Daily + point-in-time recovery |
| **Documents** | S3/Azure Blob | SSE-S3 / Azure SSE | 7 years | Versioning + cross-region replication |
| **Session Data** | Redis | In-memory (encrypted cluster) | 15 minutes TTL | N/A (ephemeral) |
| **AHCIP Codes** | PostgreSQL + Redis cache | Standard | Per fee schedule version | With primary DB |
| **Audit Logs** | PostgreSQL + ELK | Encrypted | 6 years (HIPAA) | Daily + immutable archive |
| **Form Templates** | PostgreSQL | Standard | Indefinite | With primary DB |

### 4.3 Caching Strategy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CACHING ARCHITECTURE                               │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────┐
    │                    REDIS CACHE CLUSTER (3-node HA)                  │
    ├─────────────────────────────────────────────────────────────────────┤
    │                                                                     │
    │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
    │  │  Session Cache  │  │  AHCIP Code     │  │  Rule Def       │    │
    │  │                 │  │  Cache          │  │  Cache          │    │
    │  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤    │
    │  │ TTL: 15 min     │  │ TTL: 24 hours   │  │ TTL: 1 hour     │    │
    │  │ Key: session:id │  │ Key: ahcip:code │  │ Key: rule:id    │    │
    │  │ Size: ~1KB      │  │ Size: ~500B     │  │ Size: ~2KB      │    │
    │  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
    │                                                                     │
    │  ┌─────────────────┐  ┌─────────────────┐                         │
    │  │  Form Template  │  │  Rate Limit     │                         │
    │  │  Cache          │  │  Counters       │                         │
    │  ├─────────────────┤  ├─────────────────┤                         │
    │  │ TTL: 4 hours    │  │ TTL: 1 minute   │                         │
    │  │ Key: template:id│  │ Key: ratelimit  │                         │
    │  │ Size: ~5KB      │  │   :provider:id  │                         │
    │  └─────────────────┘  └─────────────────┘                         │
    │                                                                     │
    └─────────────────────────────────────────────────────────────────────┘

    Cache Invalidation Strategy:
    • AHCIP codes: Invalidate on fee schedule update
    • Rules: Invalidate on rule save, version bump
    • Templates: Invalidate on template modification
    • Sessions: Auto-expire with TTL
```

### 4.4 Data Partitioning & Indexing

```sql
-- Claims Table Partitioning (by submitted_at month)
CREATE TABLE claims (
    claim_id UUID PRIMARY KEY,
    provider_id UUID NOT NULL,
    patient_id_hash VARCHAR(64),
    service_date DATE,
    status claim_status NOT NULL,
    total_amount DECIMAL(10,2),
    submitted_at TIMESTAMP,
    adjudicated_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
) PARTITION BY RANGE (submitted_at);

-- Create monthly partitions
CREATE TABLE claims_2026_01 PARTITION OF claims
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

-- Indexes for common queries
CREATE INDEX idx_claims_provider_status ON claims(provider_id, status);
CREATE INDEX idx_claims_submitted_at ON claims(submitted_at DESC);
CREATE INDEX idx_claims_status_date ON claims(status, submitted_at);

-- Rules table indexes
CREATE INDEX idx_rules_type_active ON rules(rule_type, is_active) 
    WHERE is_active = true;
CREATE INDEX idx_rules_effective_dates ON rules(effective_from, effective_to);

-- AHCIP codes indexes
CREATE INDEX idx_ahcip_code ON ahcip_codes(procedure_code);
CREATE INDEX idx_ahcip_category ON ahcip_codes(category);
CREATE INDEX idx_ahcip_effective ON ahcip_codes(effective_date, expiration_date);
```

---

## 5. Scalability Design

### 5.1 Horizontal Scaling Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      HORIZONTAL SCALING ARCHITECTURE                         │
└─────────────────────────────────────────────────────────────────────────────┘

                              AUTO-SCALING GROUPS
    ══════════════════════════════════════════════════════════════════════

    ┌─────────────────────────────────────────────────────────────────────┐
    │                     APPLICATION LOAD BALANCER                        │
    │  • Health checks: 30s intervals                                     │
    │  • Cross-AZ distribution                                            │
    │  • Sticky sessions for stateful requests                            │
    └─────────────────────────────────────────────────────────────────────┘
                    │                              │
         ┌──────────┴──────────┐        ┌─────────┴──────────┐
         ▼                     ▼        ▼                    ▼
    ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
    │ API     │ │ API     │ │ API     │ │ API     │ │ API     │
    │Server 1 │ │Server 2 │ │Server 3 │ │Server N │ │Server N+│
    │ (AZ-A)  │ │ (AZ-A)  │ │ (AZ-B)  │ │ (AZ-B)  │ │  ...    │
    └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘

    Auto-Scaling Triggers:
    ┌─────────────────────────────────────────────────────────────────────┐
    │  Metric               │  Scale Out      │  Scale In      │ Cooldown │
    ├─────────────────────────────────────────────────────────────────────┤
    │  CPU Utilization      │  > 70%          │  < 30%         │ 300s     │
    │  Request Count        │  > 1000 req/min │  < 200 req/min │ 300s     │
    │  Queue Depth (SQS)    │  > 100 messages │  < 10 messages │ 120s     │
    └─────────────────────────────────────────────────────────────────────┘

    Instance Configuration:
    • Min instances: 2 (HA requirement)
    • Max instances: 20 (cost control)
    • Desired: Based on traffic patterns
```

### 5.2 Database Scaling Strategy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      DATABASE SCALING ARCHITECTURE                           │
└─────────────────────────────────────────────────────────────────────────────┘

                              WRITE PATH
    ══════════════════════════════════════════════════════════════════════

    [API Servers]
         │
         │ Write operations
         ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │                     PRIMARY DATABASE (RDS)                          │
    │  • Instance: db.r6g.2xlarge (8 vCPU, 64GB RAM)                      │
    │  • Multi-AZ: Synchronous replication to standby                    │
    │  • Storage: 500GB gp3 (auto-scaling to 1TB)                        │
    │  • IOPS: 12,000 provisioned                                        │
    └─────────────────────────────────────────────────────────────────────┘
         │
         │ Async replication (< 1 second lag)
         ▼

                              READ PATH
    ══════════════════════════════════════════════════════════════════════

    ┌─────────────────────┐     ┌─────────────────────┐
    │  READ REPLICA 1     │     │  READ REPLICA 2     │
    │  (API Read Traffic) │     │  (Reporting/BI)     │
    │                     │     │                     │
    │  • db.r6g.xlarge    │     │  • db.r6g.2xlarge   │
    │  • Same-region      │     │  • Same-region      │
    └─────────────────────┘     └─────────────────────┘

    Connection Pooling (PgBouncer):
    ┌─────────────────────────────────────────────────────────────────────┐
    │  Pool Mode: Transaction                                             │
    │  Max Client Connections: 10,000                                     │
    │  Default Pool Size: 20 per API server                               │
    │  Reserve Pool: 5                                                    │
    └─────────────────────────────────────────────────────────────────────┘
```

### 5.3 Caching Layer Scaling

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      REDIS CLUSTER CONFIGURATION                             │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────┐
    │                    REDIS CLUSTER (3 Primary + 3 Replica)            │
    │                                                                     │
    │   ┌─────────┐  ┌─────────┐  ┌─────────┐                           │
    │   │Primary 1│  │Primary 2│  │Primary 3│                           │
    │   │ (AZ-A)  │  │ (AZ-B)  │  │ (AZ-A)  │                           │
    │   │ Slots   │  │ Slots   │  │ Slots   │                           │
    │   │ 0-5460  │  │5461-10922│ │10923-   │                           │
    │   └────┬────┘  └────┬────┘  │ 16383   │                           │
    │        │            │       └────┬────┘                           │
    │        ▼            ▼            ▼                                │
    │   ┌─────────┐  ┌─────────┐  ┌─────────┐                           │
    │   │Replica 1│  │Replica 2│  │Replica 3│                           │
    │   │ (AZ-B)  │  │ (AZ-A)  │  │ (AZ-B)  │                           │
    │   └─────────┘  └─────────┘  └─────────┘                           │
    │                                                                     │
    │   Node Type: cache.r6g.large (13GB, 2 vCPU)                        │
    │   Total Capacity: ~39GB                                            │
    │   Failover: Redis Sentinel (automatic)                             │
    └─────────────────────────────────────────────────────────────────────┘
```

### 5.4 Load Testing Targets

| Metric | Target | Peak Load |
|--------|--------|-----------|
| **Concurrent Users** | 1,000 | 5,000 |
| **Claim Submissions/min** | 500 | 2,000 |
| **API Response Time (P95)** | < 200ms | < 500ms |
| **Document Uploads/min** | 100 | 500 |
| **Rule Evaluations/min** | 1,000 | 5,000 |
| **Database Connections** | 500 | 2,000 |

---

## 6. Performance Considerations

### 6.1 Latency Optimization Strategy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      LATENCY OPTIMIZATION LAYERS                             │
└─────────────────────────────────────────────────────────────────────────────┘

    Layer 1: Edge Caching (CDN)
    ══════════════════════════════════════════════════════════════════════
    ┌─────────────────────────────────────────────────────────────────────┐
    │  CloudFront / Azure CDN                                             │
    │  • Static assets: 30-day TTL                                        │
    │  • Form templates: 4-hour TTL (with cache invalidation)             │
    │  • API responses: No caching (dynamic data)                         │
    │  Expected latency reduction: ~50-100ms (geographic distance)        │
    └─────────────────────────────────────────────────────────────────────┘

    Layer 2: Application Caching (Redis)
    ══════════════════════════════════════════════════════════════════════
    ┌─────────────────────────────────────────────────────────────────────┐
    │  Cache-Aside Pattern                                                │
    │  • AHCIP code lookups: ~0.5ms (cached) vs ~50ms (database)         │
    │  • Session validation: ~0.3ms (cached) vs ~20ms (database)         │
    │  • Rule definitions: ~1ms (cached) vs ~30ms (database)             │
    │  Cache hit ratio target: > 85%                                      │
    └─────────────────────────────────────────────────────────────────────┘

    Layer 3: Database Optimization
    ══════════════════════════════════════════════════════════════════════
    ┌─────────────────────────────────────────────────────────────────────┐
    │  Query Optimization                                                 │
    │  • Prepared statements: Reduce parse time                           │
    │  • Connection pooling: Reduce connection overhead                   │
    │  • Read replicas: Offload read queries                              │
    │  • Table partitioning: Faster queries on recent data                │
    │  Target query time: < 50ms (P95)                                    │
    └─────────────────────────────────────────────────────────────────────┘
```

### 6.2 Throughput Optimization

```typescript
// Batch Processing for High-Volume Operations
class ClaimsBatchProcessor {
  // Batch size tuned for optimal throughput
  private readonly BATCH_SIZE = 100;
  private readonly CONCURRENT_BATCHES = 5;
  
  async processBatchAdjudication(claimIds: string[]): Promise<BatchResult> {
    const batches = this.chunk(claimIds, this.BATCH_SIZE);
    
    // Process batches with controlled concurrency
    const results = await pLimit(this.CONCURRENT_BATCHES)
      .map(batches, batch => this.processAdjudicationBatch(batch));
    
    return this.aggregateResults(results);
  }
  
  // Bulk insert for document metadata
  async bulkInsertDocuments(documents: DocumentMetadata[]): Promise<void> {
    await this.db.transaction(async (trx) => {
      await trx.batchInsert('documents', documents, this.BATCH_SIZE);
    });
  }
}

// Connection Pool Configuration
const poolConfig = {
  min: 10,
  max: 50,
  acquireTimeoutMillis: 30000,
  createTimeoutMillis: 30000,
  idleTimeoutMillis: 30000,
  reapIntervalMillis: 1000,
  createRetryIntervalMillis: 100,
};
```

### 6.3 SLA Thresholds & Monitoring

| API Endpoint | P50 Target | P95 Target | P99 Target | Error Rate |
|--------------|------------|------------|------------|------------|
| `GET /claims` | 50ms | 150ms | 300ms | < 0.1% |
| `POST /claims` | 100ms | 250ms | 500ms | < 0.5% |
| `POST /claims/:id/submit` | 150ms | 400ms | 800ms | < 0.5% |
| `GET /ahcip-codes/search` | 30ms | 100ms | 200ms | < 0.1% |
| `POST /documents/upload` | 500ms | 1500ms | 3000ms | < 1.0% |
| `POST /rules/execute` | 200ms | 500ms | 1000ms | < 0.5% |

```typescript
// APM Integration Configuration
const apmConfig = {
  serviceName: 'claims-processing-api',
  serverUrl: process.env.APM_SERVER_URL,
  environment: process.env.NODE_ENV,
  
  // Custom metrics
  customMetrics: {
    'claims.submission.duration': 'histogram',
    'rules.execution.duration': 'histogram',
    'cache.hit.ratio': 'gauge',
    'database.connection.pool': 'gauge'
  },
  
  // Alert thresholds
  alerts: [
    { metric: 'response_time_p95', threshold: 500, severity: 'warning' },
    { metric: 'response_time_p99', threshold: 1000, severity: 'critical' },
    { metric: 'error_rate', threshold: 1, severity: 'critical' }
  ]
};
```

### 6.4 Performance Optimization Checklist

| Category | Optimization | Impact | Status |
|----------|--------------|--------|--------|
| **Database** | Connection pooling | High | ✅ |
| **Database** | Read replicas for queries | High | ✅ |
| **Database** | Query index optimization | High | ✅ |
| **Database** | Table partitioning (claims) | Medium | ✅ |
| **Caching** | Redis session caching | High | ✅ |
| **Caching** | AHCIP code caching | Medium | ✅ |
| **Caching** | Rule definition caching | Medium | ✅ |
| **API** | Response compression (gzip) | Medium | ✅ |
| **API** | Pagination for list endpoints | High | ✅ |
| **API** | Rate limiting | Medium | ✅ |
| **Frontend** | CDN for static assets | High | ✅ |
| **Frontend** | Lazy loading components | Medium | ✅ |

---

## 7. Technology Decisions

### 7.1 Technology Stack Summary

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TECHNOLOGY STACK                                     │
└─────────────────────────────────────────────────────────────────────────────┘

    FRONTEND LAYER
    ══════════════════════════════════════════════════════════════════════
    ┌─────────────────────────────────────────────────────────────────────┐
    │  Framework: Vue.js 3 / React 18                                     │
    │  State Management: Pinia / Redux Toolkit                            │
    │  UI Components: Custom with Tailwind CSS                            │
    │  Form Handling: VeeValidate / React Hook Form                       │
    │  Testing: Jest, Cypress, Playwright                                 │
    │  Build: Vite / Webpack 5                                            │
    └─────────────────────────────────────────────────────────────────────┘

    BACKEND LAYER
    ══════════════════════════════════════════════════════════════════════
    ┌─────────────────────────────────────────────────────────────────────┐
    │  Runtime: Node.js 20 LTS                                            │
    │  Framework: Express.js / Fastify                                    │
    │  API Documentation: OpenAPI 3.0 / Swagger                           │
    │  Validation: Joi / Zod                                              │
    │  ORM: Knex.js / Prisma                                              │
    │  Testing: Jest, Supertest, Pact                                     │
    └─────────────────────────────────────────────────────────────────────┘

    DATA LAYER
    ══════════════════════════════════════════════════════════════════════
    ┌─────────────────────────────────────────────────────────────────────┐
    │  Primary Database: PostgreSQL 15 (AWS RDS)                          │
    │  Caching: Redis 7 (ElastiCache Cluster)                             │
    │  Document Storage: AWS S3 / Azure Blob                              │
    │  Search: PostgreSQL Full-Text (future: Elasticsearch)               │
    └─────────────────────────────────────────────────────────────────────┘

    INFRASTRUCTURE
    ══════════════════════════════════════════════════════════════════════
    ┌─────────────────────────────────────────────────────────────────────┐
    │  Cloud Provider: AWS (primary) / Azure (alternative)                │
    │  Container Orchestration: ECS Fargate / EKS                         │
    │  API Gateway: AWS API Gateway / Azure API Management                │
    │  Load Balancer: Application Load Balancer                           │
    │  CDN: CloudFront / Azure CDN                                        │
    │  Monitoring: CloudWatch, ELK Stack, Datadog                         │
    │  CI/CD: GitHub Actions, AWS CodePipeline                            │
    └─────────────────────────────────────────────────────────────────────┘

    SECURITY & COMPLIANCE
    ══════════════════════════════════════════════════════════════════════
    ┌─────────────────────────────────────────────────────────────────────┐
    │  Identity: Azure AD / Auth0 (OAuth 2.0, OIDC, SAML)                 │
    │  Secrets: AWS Secrets Manager / Azure Key Vault                     │
    │  Encryption: AWS KMS / Azure Key Vault                              │
    │  WAF: AWS WAF / Azure WAF                                           │
    │  Security Scanning: SonarQube, OWASP ZAP, Snyk                      │
    └─────────────────────────────────────────────────────────────────────┘
```

### 7.2 Technology Decisions & Rationale

| Component | Selected | Alternatives Considered | Rationale |
|-----------|----------|------------------------|-----------|
| **Frontend Framework** | Vue.js 3 | React, Angular | Gentler learning curve, excellent TypeScript support, composition API for complex forms |
| **Backend Runtime** | Node.js | Java/Spring, .NET, Go | Consistent JavaScript stack, excellent async I/O for API workloads, large ecosystem |
| **API Framework** | Fastify | Express, NestJS | Better performance than Express, built-in validation, OpenAPI support |
| **Database** | PostgreSQL | MySQL, MongoDB | JSONB for flexible claim data, excellent HIPAA compliance tooling, partitioning support |
| **Caching** | Redis | Memcached | Data structures (sorted sets for queues), Lua scripting, persistence options |
| **Document Storage** | AWS S3 | Azure Blob, GCS | SSE encryption, cross-region replication, lifecycle policies for compliance |
| **Identity Provider** | Azure AD | Auth0, Okta, Cognito | Enterprise SAML support, healthcare org familiarity, MFA enforcement |
| **Container Platform** | ECS Fargate | EKS, EC2 | Serverless containers reduce operational overhead, automatic scaling |

### 7.3 Cloud Architecture Decision

**Primary: AWS**

| Service | Component | Justification |
|---------|-----------|---------------|
| **ECS Fargate** | API Services | Serverless containers, automatic scaling, reduced ops |
| **RDS PostgreSQL** | Primary Database | Multi-AZ, automated backups, encryption |
| **ElastiCache Redis** | Caching Layer | Cluster mode, automatic failover |
| **S3** | Document Storage | Encryption, versioning, cross-region replication |
| **API Gateway** | API Management | Rate limiting, throttling, WAF integration |
| **CloudFront** | CDN | Global distribution, edge caching |
| **Secrets Manager** | Secret Storage | Automatic rotation, audit logging |
| **KMS** | Key Management | HIPAA-eligible, key rotation |
| **CloudWatch** | Monitoring | Metrics, logs, alarms, dashboards |
| **WAF** | Security | OWASP rules, DDoS protection |

### 7.4 Standards & Compliance

| Standard | Requirement | Implementation |
|----------|-------------|----------------|
| **HIPAA §164.312(a)(1)** | Access Controls | RBAC with Azure AD, session management |
| **HIPAA §164.312(a)(2)(iv)** | Encryption | AES-256 at rest, TLS 1.3 in transit |
| **HIPAA §164.312(b)** | Audit Controls | Comprehensive audit logging, ELK stack |
| **HIPAA §164.312(d)** | Authentication | MFA enforcement, password policies |
| **WCAG 2.1 AA** | Accessibility | axe-core scanning, keyboard navigation |
| **OWASP Top 10** | Security | SAST/DAST scanning, WAF rules |

---

## 8. Architecture Diagrams

### 8.1 C4 Model - Level 1: System Context

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SYSTEM CONTEXT DIAGRAM                              │
│                               (C4 Level 1)                                   │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌───────────────────────────────┐
                    │       Healthcare Provider     │
                    │                               │
                    │ [Person]                      │
                    │ Submits claims, uploads docs, │
                    │ tracks claim status           │
                    └───────────────┬───────────────┘
                                    │
                                    │ Uses [HTTPS]
                                    ▼
┌───────────────────┐     ┌─────────────────────────────────┐     ┌───────────────────┐
│                   │     │                                 │     │                   │
│  Administrator    │     │   CLAIMS PROCESSING PLATFORM   │     │  AHCIP Fee        │
│                   │────►│                                 │◄────│  Schedule Service │
│ [Person]          │     │ [Software System]               │     │                   │
│ Manages forms,    │     │                                 │     │ [External System] │
│ configures rules, │     │ Digital claims submission,      │     │ Provides procedure│
│ reviews claims    │     │ automated adjudication,         │     │ codes and fees    │
│                   │     │ compliance reporting            │     │                   │
└───────────────────┘     │                                 │     └───────────────────┘
                          └──────────────┬──────────────────┘
                                         │
              ┌──────────────────────────┼──────────────────────────┐
              │                          │                          │
              ▼                          ▼                          ▼
    ┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐
    │                   │     │                   │     │                   │
    │ Notification      │     │ Identity Provider │     │ Document Storage  │
    │ Service           │     │ (Azure AD)        │     │ (S3/Blob)         │
    │                   │     │                   │     │                   │
    │ [External System] │     │ [External System] │     │ [External System] │
    │ Sends email/SMS   │     │ Authenticates     │     │ Stores claim      │
    │ notifications     │     │ users, SSO        │     │ attachments       │
    │                   │     │                   │     │                   │
    └───────────────────┘     └───────────────────┘     └───────────────────┘
```

### 8.2 C4 Model - Level 2: Container Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CONTAINER DIAGRAM                                   │
│                            (C4 Level 2)                                      │
│                    Claims Processing Platform                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         PRESENTATION TIER                                    │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐ │
│  │ Provider Portal     │  │ Admin Dashboard     │  │ Form Builder        │ │
│  │ [SPA: Vue.js]       │  │ [SPA: Vue.js]       │  │ [SPA: Vue.js]       │ │
│  │                     │  │                     │  │                     │ │
│  │ Claim submission,   │  │ Metrics, reviews,   │  │ Form design,        │ │
│  │ status tracking     │  │ rule management     │  │ template versioning │ │
│  └──────────┬──────────┘  └──────────┬──────────┘  └──────────┬──────────┘ │
└─────────────┼────────────────────────┼────────────────────────┼─────────────┘
              │                        │                        │
              └────────────────────────┼────────────────────────┘
                                       │
                                       │ HTTPS / REST API
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            EDGE TIER                                         │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌──────────────┐ │
│  │ CDN           │  │ WAF           │  │ API Gateway   │  │ Load         │ │
│  │ [CloudFront]  │  │ [AWS WAF]     │  │ [AWS APIGW]   │  │ Balancer     │ │
│  └───────────────┘  └───────────────┘  └───────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          APPLICATION TIER                                    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     API Services [Node.js / Fastify]                 │   │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐       │   │
│  │  │ Claims API │ │ Forms API  │ │ Rules API  │ │ Docs API   │       │   │
│  │  │            │ │            │ │            │ │            │       │   │
│  │  │ Submit,    │ │ Templates, │ │ Define,    │ │ Upload,    │       │   │
│  │  │ track,     │ │ versioning │ │ test,      │ │ retrieve,  │       │   │
│  │  │ retrieve   │ │            │ │ execute    │ │ list       │       │   │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────────┘       │   │
│  │  ┌────────────┐ ┌────────────┐                                      │   │
│  │  │ AHCIP API  │ │ Audit API  │                                      │   │
│  │  │            │ │            │                                      │   │
│  │  │ Code       │ │ Compliance │                                      │   │
│  │  │ lookup,    │ │ reports,   │                                      │   │
│  │  │ fees       │ │ audit logs │                                      │   │
│  │  └────────────┘ └────────────┘                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │              Background Workers [Node.js / Lambda]                   │   │
│  │  ┌────────────────────┐  ┌────────────────────┐                     │   │
│  │  │ Adjudication       │  │ Notification       │                     │   │
│  │  │ Processor          │  │ Handler            │                     │   │
│  │  │                    │  │                    │                     │   │
│  │  │ Process submitted  │  │ Send status        │                     │   │
│  │  │ claims, execute    │  │ notifications      │                     │   │
│  │  │ rules              │  │ via email/SMS      │                     │   │
│  │  └────────────────────┘  └────────────────────┘                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DATA TIER                                         │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐ │
│  │ PostgreSQL RDS      │  │ Redis Cache         │  │ S3 Bucket           │ │
│  │ [Multi-AZ]          │  │ [ElastiCache]       │  │ [Documents]         │ │
│  │                     │  │                     │  │                     │ │
│  │ Claims, forms,      │  │ Sessions, AHCIP     │  │ Claim attachments,  │ │
│  │ rules, users,       │  │ codes, rate limits  │  │ supporting docs     │ │
│  │ audit logs          │  │                     │  │                     │ │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.3 C4 Model - Level 3: Component Diagram (Claims API)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         COMPONENT DIAGRAM                                    │
│                           (C4 Level 3)                                       │
│                        Claims API Service                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          CLAIMS API SERVICE                                  │
│                            [Node.js / Fastify]                               │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         MIDDLEWARE STACK                             │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│  │  │ Auth     │→│ Rate     │→│ CSRF     │→│ Validate │→│ Audit    │  │   │
│  │  │ MW       │ │ Limit MW │ │ MW       │ │ MW       │ │ Log MW   │  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         ROUTER LAYER                                 │   │
│  │  ┌────────────────────────────────────────────────────────────────┐ │   │
│  │  │                      Claims Router                              │ │   │
│  │  │  POST /claims              → createClaim()                     │ │   │
│  │  │  GET  /claims              → listClaims()                      │ │   │
│  │  │  GET  /claims/:id          → getClaim()                        │ │   │
│  │  │  PUT  /claims/:id/draft    → saveDraft()                       │ │   │
│  │  │  POST /claims/:id/submit   → submitClaim()                     │ │   │
│  │  │  GET  /claims/:id/status   → getClaimStatus()                  │ │   │
│  │  └────────────────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                       CONTROLLER LAYER                               │   │
│  │  ┌────────────────────────────┐  ┌────────────────────────────┐    │   │
│  │  │      Claims Controller     │  │   Adjudication Workflow    │    │   │
│  │  │                            │  │      Controller            │    │   │
│  │  │ • createClaim()            │  │                            │    │   │
│  │  │ • saveDraft()              │  │ • processSubmittedClaim()  │    │   │
│  │  │ • submitClaim()            │  │ • flagForManualReview()    │    │   │
│  │  │ • getClaim()               │  │ • finalizeAdjudication()   │    │   │
│  │  │ • listClaims()             │  │                            │    │   │
│  │  │ • getClaimStatus()         │  │                            │    │   │
│  │  └─────────────┬──────────────┘  └─────────────┬──────────────┘    │   │
│  └────────────────┼────────────────────────────────┼────────────────────┘   │
│                   │                                │                        │
│                   ▼                                ▼                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        SERVICE LAYER                                 │   │
│  │  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐          │   │
│  │  │ Claims Service │ │ Validation     │ │ Rules Engine   │          │   │
│  │  │                │ │ Service        │ │ Service        │          │   │
│  │  │ CRUD ops,      │ │                │ │                │          │   │
│  │  │ status mgmt    │ │ Schema,        │ │ Execute rules, │          │   │
│  │  │                │ │ business rules │ │ calculate fees │          │   │
│  │  └───────┬────────┘ └───────┬────────┘ └───────┬────────┘          │   │
│  │          │                  │                  │                    │   │
│  │  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐          │   │
│  │  │ Fee Calculator │ │ Audit Service  │ │ Notification   │          │   │
│  │  │                │ │                │ │ Service        │          │   │
│  │  │ AHCIP fees,    │ │ Log all ops,   │ │                │          │   │
│  │  │ totals         │ │ HIPAA audit    │ │ Trigger alerts │          │   │
│  │  └───────┬────────┘ └───────┬────────┘ └───────┬────────┘          │   │
│  └──────────┼──────────────────┼──────────────────┼─────────────────────┘   │
│             │                  │                  │                        │
│             ▼                  ▼                  ▼                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        UTILITY LAYER                                 │   │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐       │   │
│  │  │ Pagination │ │ Date/Time  │ │ Response   │ │ Validation │       │   │
│  │  │ Helpers    │ │ Formatters │ │ Helpers    │ │ Helpers    │       │   │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────────┘       │   │
│  │  ┌────────────┐ ┌────────────┐                                     │   │
│  │  │ Error      │ │ Fee        │                                     │   │
│  │  │ Handler    │ │ Calculator │                                     │   │
│  │  └────────────┘ └────────────┘                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
           ┌────────────────────────┼────────────────────────┐
           │                        │                        │
           ▼                        ▼                        ▼
    ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
    │ PostgreSQL  │          │ Redis       │          │ S3          │
    │ Database    │          │ Cache       │          │ Storage     │
    └─────────────┘          └─────────────┘          └─────────────┘
```

### 8.4 Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DEPLOYMENT ARCHITECTURE                               │
│                              AWS Cloud                                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              REGION: us-east-1                               │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                          PUBLIC SUBNETS                                │ │
│  │  ┌───────────────────────┐      ┌───────────────────────┐            │ │
│  │  │   AZ-A (us-east-1a)   │      │   AZ-B (us-east-1b)   │            │ │
│  │  │  ┌─────────────────┐  │      │  ┌─────────────────┐  │            │ │
│  │  │  │   NAT Gateway   │  │      │  │   NAT Gateway   │  │            │ │
│  │  │  └─────────────────┘  │      │  └─────────────────┘  │            │ │
│  │  │  ┌─────────────────┐  │      │  ┌─────────────────┐  │            │ │
│  │  │  │      ALB        │◄─┼──────┼──│      ALB        │  │            │ │
│  │  │  └─────────────────┘  │      │  └─────────────────┘  │            │ │
│  │  └───────────────────────┘      └───────────────────────┘            │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                        │
│                              ┌─────┴─────┐                                  │
│                              │    WAF    │                                  │
│                              └─────┬─────┘                                  │
│                                    │                                        │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                         PRIVATE SUBNETS                                │ │
│  │  ┌───────────────────────┐      ┌───────────────────────┐            │ │
│  │  │   AZ-A (us-east-1a)   │      │   AZ-B (us-east-1b)   │            │ │
│  │  │  ┌─────────────────┐  │      │  ┌─────────────────┐  │            │ │
│  │  │  │ ECS Fargate     │  │      │  │ ECS Fargate     │  │            │ │
│  │  │  │ ┌─────────────┐ │  │      │  │ ┌─────────────┐ │  │            │ │
│  │  │  │ │ Claims API  │ │  │      │  │ │ Claims API  │ │  │            │ │
│  │  │  │ │   (x2)      │ │  │      │  │ │   (x2)      │ │  │            │ │
│  │  │  │ └─────────────┘ │  │      │  │ └─────────────┘ │  │            │ │
│  │  │  │ ┌─────────────┐ │  │      │  │ ┌─────────────┐ │  │            │ │
│  │  │  │ │ Rules API   │ │  │      │  │ │ Rules API   │ │  │            │ │
│  │  │  │ │   (x2)      │ │  │      │  │ │   (x2)      │ │  │            │ │
│  │  │  │ └─────────────┘ │  │      │  │ └─────────────┘ │  │            │ │
│  │  │  └─────────────────┘  │      │  └─────────────────┘  │            │ │
│  │  └───────────────────────┘      └───────────────────────┘            │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                        │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                          DATA SUBNETS                                  │ │
│  │  ┌───────────────────────┐      ┌───────────────────────┐            │ │
│  │  │   AZ-A (us-east-1a)   │      │   AZ-B (us-east-1b)   │            │ │
│  │  │  ┌─────────────────┐  │      │  ┌─────────────────┐  │            │ │
│  │  │  │ RDS Primary     │  │◄────►│  │ RDS Standby     │  │            │ │
│  │  │  │ (PostgreSQL)    │  │ sync │  │ (PostgreSQL)    │  │            │ │
│  │  │  └─────────────────┘  │      │  └─────────────────┘  │            │ │
│  │  │  ┌─────────────────┐  │      │  ┌─────────────────┐  │            │ │
│  │  │  │ Redis Primary   │  │◄────►│  │ Redis Replica   │  │            │ │
│  │  │  │ (ElastiCache)   │  │      │  │ (ElastiCache)   │  │            │ │
│  │  │  └─────────────────┘  │      │  └─────────────────┘  │            │ │
│  │  └───────────────────────┘      └───────────────────────┘            │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                         GLOBAL SERVICES                                │ │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐         │ │
│  │  │ CloudFront │ │ Route 53   │ │ S3 Bucket  │ │ Secrets    │         │ │
│  │  │ (CDN)      │ │ (DNS)      │ │ (Docs)     │ │ Manager    │         │ │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────────┘         │ │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐                        │ │
│  │  │ KMS        │ │ CloudWatch │ │ X-Ray      │                        │ │
│  │  │ (Keys)     │ │ (Logs)     │ │ (Tracing)  │                        │ │
│  │  └────────────┘ └────────────┘ └────────────┘                        │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                       DISASTER RECOVERY REGION: us-west-2                    │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐          │ │
│  │  │ RDS Read       │  │ S3 Replica     │  │ Standby ECS    │          │ │
│  │  │ Replica        │  │ (Cross-Region) │  │ (Warm Standby) │          │ │
│  │  └────────────────┘  └────────────────┘  └────────────────┘          │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. Quality Assurance Architecture

### 9.1 Testing Strategy Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TESTING PYRAMID                                      │
└─────────────────────────────────────────────────────────────────────────────┘

                                 ▲
                                /│\
                               / │ \
                              /  │  \
                             /   │   \
                            / E2E│    \          10% (Cypress/Playwright)
                           /  Tests   \
                          /───────────\
                         /             \
                        / Integration   \        30% (API Tests, Pact)
                       /    Tests        \
                      /───────────────────\
                     /                     \
                    /     Unit Tests        \    60% (Jest)
                   /───────────────────────────\
                  ▼                             ▼

    Coverage Targets:
    • Unit Tests: 80% code coverage
    • Integration Tests: 60% API endpoint coverage
    • E2E Tests: Critical user journeys (submit claim, adjudicate)
```

### 9.2 QA Infrastructure Components

| Component | Purpose | Integration |
|-----------|---------|-------------|
| **Test Automation Service** | Centralized test execution | CI/CD pipeline |
| **API Test Harness** | API contract & load testing | Newman, k6, OWASP ZAP |
| **Contract Testing Service (Pact)** | Consumer-driven contracts | Frontend ↔ Backend |
| **Load Testing Service (k6)** | Performance validation | Pre-production |
| **Security Scanner (SAST/DAST)** | Vulnerability scanning | CI/CD gates |
| **Accessibility Scanner (axe-core)** | WCAG 2.1 AA compliance | E2E tests |
| **Performance Monitor** | APM, SLA tracking | CloudWatch/Datadog |
| **Test Data Factory** | Synthetic HIPAA-compliant data | All test types |
| **Quality Metrics Dashboard** | Coverage, defect tracking | Team visibility |
| **CI/CD Quality Gate** | Deployment approval | Pipeline |

### 9.3 Quality Gates

```yaml
# CI/CD Quality Gate Configuration
quality_gates:
  unit_tests:
    coverage_threshold: 80%
    pass_rate: 100%
    
  integration_tests:
    coverage_threshold: 60%
    pass_rate: 100%
    
  security_scanning:
    critical_findings: 0
    high_findings: 0
    
  performance:
    p95_response_time_ms: 500
    regression_threshold: 10%
    
  accessibility:
    wcag_aa_violations: 0
    
  contract_tests:
    consumer_contracts: verified
    
  e2e_smoke_tests:
    critical_journeys: passing
```

---

## 10. Appendices

### 10.1 Epic to Component Mapping

| Epic | Features | Key Components |
|------|----------|----------------|
| **E-002: Digital Claims Form Management** | F-001: Form Builder, F-002: AHCIP Lookup, F-003: Template Versioning | Form Designer Canvas, AHCIP Code Search Hook, Template Management Hook, Forms Controller |
| **E-003: Claims Submission Workflow** | F-001: Draft/Submit, F-003: Status Tracking | Claim Submission Form, Claim Status Tracker, Claims Controller |
| **E-004: Claims Rules Engine** | F-001: Document Upload, F-002: Document Retrieval | Document Uploader, Document Controller, Rules Controller |
| **E-005: Claims Adjudication Processing** | Automated adjudication, Manual review | Adjudication Workflow Controller, Flagged Claims Queue |
| **E-006: Rules Engine Administration** | F-001: Rule Versioning, F-002: Rule Testing, F-003: Audit Logs | Rule Editor Component, Rule Testing Controller, Audit & Compliance Controller |

### 10.2 Security Controls Matrix

| Control | HIPAA Section | Implementation |
|---------|---------------|----------------|
| Access Control | §164.312(a)(1) | Azure AD RBAC, Session management (15-min idle) |
| Encryption at Rest | §164.312(a)(2)(iv) | AES-256, AWS KMS |
| Encryption in Transit | §164.312(a)(2)(iv) | TLS 1.3 |
| Audit Controls | §164.312(b) | ELK Stack, PHI access logging |
| Integrity | §164.312(c)(1) | Input validation, checksums |
| Authentication | §164.312(d) | MFA, OAuth 2.0/SAML |

### 10.3 Glossary

| Term | Definition |
|------|------------|
| **AHCIP** | Alberta Health Care Insurance Plan |
| **PHI** | Protected Health Information |
| **HIPAA** | Health Insurance Portability and Accountability Act |
| **Adjudication** | Process of evaluating a claim against rules to determine payment |
| **Pact** | Consumer-driven contract testing framework |
| **TTL** | Time To Live (cache expiration) |
| **Multi-AZ** | Multi-Availability Zone deployment for high availability |
| **SSE** | Server-Side Encryption |
| **WAF** | Web Application Firewall |
| **CDN** | Content Delivery Network |

---

*Document prepared for: Claims Processing Platform Architecture Review*
*Last updated: January 2026*