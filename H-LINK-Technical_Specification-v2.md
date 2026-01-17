# Technical Specification Document
## Claims Processing Platform

---

## Document Information

| Field | Value |
|-------|-------|
| **Project Name** | Claims Processing Platform |
| **Document Type** | Technical Specification |
| **Generated Date** | January 2026 |
| **Version** | 1.0 |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Project Overview](#2-project-overview)
3. [Requirements](#3-requirements)
4. [Architecture](#4-architecture)
5. [Technology Stack](#5-technology-stack)
6. [Standards & Compliance](#6-standards--compliance)
7. [Integration Points](#7-integration-points)
8. [Recommendations](#8-recommendations)

---

## 1. Executive Summary

The Claims Processing Platform is a comprehensive enterprise solution designed to digitize and automate the end-to-end healthcare claims management lifecycle. The platform enables healthcare providers to submit claims digitally, supports administrative configuration of claim forms and validation rules, and automates the adjudication process based on AHCIP (Alberta Health Care Insurance Plan) governing rules and fee schedules.

### Key Capabilities

- **Digital Claims Intake**: Provider portal for claim submission with dynamic forms and AHCIP code lookups
- **Automated Adjudication**: Rules-based engine for validating and processing claims per AHCIP requirements
- **Administrative Control**: Form builder, template management, and rule configuration interfaces
- **Compliance & Audit**: HIPAA-compliant data handling with comprehensive audit trails
- **Quality Assurance**: Integrated testing infrastructure with contract testing, load testing, and security scanning

### Business Value

- Eliminates paper-based claims processing inefficiencies
- Reduces adjudication cycle times through automation
- Ensures regulatory compliance with built-in HIPAA controls
- Provides transparency through real-time claim status tracking
- Enables flexible rule management to adapt to evolving AHCIP requirements

---

## 2. Project Overview

### 2.1 Project Description

The Claims Processing Platform serves as a centralized system for managing healthcare claims from initial submission through final adjudication and payment determination. The platform targets two primary user groups:

1. **Healthcare Providers**: Submit claims, upload supporting documents, and track claim status
2. **Administrators**: Configure claim forms, define validation/adjudication rules, review flagged claims, and generate compliance reports

### 2.2 Scope

#### In Scope

| Area | Description |
|------|-------------|
| Digital Form Management | Creation, versioning, and management of claim form templates |
| Claims Submission | End-to-end workflow from draft creation to submission |
| Document Management | Secure upload, storage, and retrieval of supporting documents |
| Rules Engine | Configurable validation and adjudication rules with testing capabilities |
| Automated Adjudication | Rule-based claim processing and payment calculation |
| Audit & Compliance | Comprehensive logging and compliance reporting |
| Provider Portal | User interface for claim submission and status tracking |
| Admin Dashboard | Administrative interface for system configuration and monitoring |

#### Out of Scope

- Payment processing and fund disbursement
- Provider credentialing and enrollment
- Patient eligibility verification (external service dependency)
- Legacy system data migration (separate initiative)

### 2.3 Objectives

1. **Digitize Claims Process**: Replace manual/paper-based claims with digital submission workflow
2. **Automate Validation**: Implement rules-based validation per AHCIP requirements
3. **Accelerate Adjudication**: Automate claim adjudication with manual review for exceptions
4. **Ensure Compliance**: Maintain HIPAA compliance throughout the data lifecycle
5. **Enable Flexibility**: Provide administrative tools for adapting to regulatory changes
6. **Improve Visibility**: Deliver real-time claim status tracking and reporting

---

## 3. Requirements

### 3.1 Requirements Hierarchy

```
Claims Processing Platform
├── E-002: Digital Claims Form Management
├── E-003: Claims Submission Workflow
├── E-004: Supporting Document Management / Claims Rules Engine
├── E-005: Claims Adjudication Processing
└── E-006: Rules Engine Administration
```

### 3.2 Epic: Digital Claims Form Management (E-002)

**Description**: Enable creation and management of digital forms to digitize the entire healthcare claims submission process.

#### Features

| Feature ID | Feature Name | Description |
|------------|--------------|-------------|
| E-002-F-001 | Form Design & Configuration | Allow administrators to design digital claim forms with drag-and-drop interface |
| E-002-F-002 | AHCIP Code Integration | Provide search and auto-population of AHCIP procedure codes and pricing |
| E-002-F-003 | Template Management | Create, duplicate, and version claim form templates |

#### User Stories & Acceptance Criteria

**E-002-F-001: Form Design & Configuration**

| Story ID | User Story | Acceptance Criteria |
|----------|------------|---------------------|
| E-002-F-001-S-001 | As an admin, I want to drag form fields onto a canvas to design claim forms | - Canvas accepts text, dropdown, date, and AHCIP code fields<br>- Fields can be reordered via drag-and-drop<br>- Form preview updates in real-time |
| E-002-F-001-S-002 | As an admin, I want to configure validation rules for each field | - Required/optional toggle available<br>- Format validation configurable (regex support)<br>- Cross-field validation rules definable |

**E-002-F-002: AHCIP Code Integration**

| Story ID | User Story | Acceptance Criteria |
|----------|------------|---------------------|
| E-002-F-002-S-001 | As a provider, I want to search AHCIP codes while completing a claim | - Search by code or description<br>- Results display within 500ms<br>- Selected code auto-populates fee amount |
| E-002-F-002-S-002 | As a provider, I want current fee schedules displayed | - Fee amounts reflect current effective date<br>- Expired codes clearly indicated<br>- Category filtering available |

**E-002-F-003: Template Management**

| Story ID | User Story | Acceptance Criteria |
|----------|------------|---------------------|
| E-002-F-003-S-001 | As an admin, I want to duplicate existing templates | - One-click duplication<br>- New template editable independently<br>- Version number incremented |
| E-002-F-003-S-002 | As an admin, I want to view template version history | - All versions listed with timestamps<br>- Author attribution shown<br>- Rollback capability available |

---

### 3.3 Epic: Claims Submission Workflow (E-003)

**Description**: Digitize the end-to-end claims submission process from form completion to submission tracking.

#### Features

| Feature ID | Feature Name | Description |
|------------|--------------|-------------|
| E-003-F-001 | Claim Form Completion | Dynamic form rendering with validation and draft saving |
| E-003-F-002 | Claim Submission | Submit completed claims with confirmation workflow |
| E-003-F-003 | Status Tracking | Real-time claim status visibility with notifications |

#### User Stories & Acceptance Criteria

**E-003-F-001: Claim Form Completion**

| Story ID | User Story | Acceptance Criteria |
|----------|------------|---------------------|
| E-003-F-001-S-001 | As a provider, I want to save claim drafts | - Auto-save triggers every 30 seconds<br>- Manual save available<br>- Draft indicator displayed<br>- Drafts retrievable from claims list |
| E-003-F-001-S-002 | As a provider, I want real-time validation feedback | - Field validation on blur<br>- Error messages displayed inline<br>- Submit button disabled until valid |

**E-003-F-002: Claim Submission**

| Story ID | User Story | Acceptance Criteria |
|----------|------------|---------------------|
| E-003-F-002-S-001 | As a provider, I want confirmation before submitting | - Review summary displayed<br>- Confirmation dialog requires explicit action<br>- Submission not reversible after confirmation |
| E-003-F-002-S-002 | As a provider, I want submission confirmation | - Success message with claim reference number<br>- Email/SMS notification sent (per E-003-F-003-S-001-AC-002)<br>- Claim appears in status tracker |

**E-003-F-003: Status Tracking**

| Story ID | User Story | Acceptance Criteria |
|----------|------------|---------------------|
| E-003-F-003-S-001 | As a provider, I want to view all my claims and their status | - List view with sortable columns<br>- Filter by status, date range<br>- Status: Draft, Submitted, In Review, Adjudicated, Paid, Denied |
| E-003-F-003-S-001-AC-002 | Notification on status change | - Email notification on status transitions<br>- Configurable notification preferences |

---

### 3.4 Epic: Claims Rules Engine (E-004)

**Description**: Automated engine to validate and adjudicate healthcare claims based on AHCIP governing rules and fee schedules.

#### Features

| Feature ID | Feature Name | Description |
|------------|--------------|-------------|
| E-004-F-001 | Rule Definition | Define validation rules with conditions and parameters |
| E-004-F-002 | Document Requirements | Configure required supporting documents per claim type |

#### User Stories & Acceptance Criteria

**E-004-F-001: Rule Definition**

| Story ID | User Story | Acceptance Criteria |
|----------|------------|---------------------|
| E-004-F-001-S-001 | As an admin, I want to define validation rules | - Rule editor with condition builder<br>- Logical operators (AND, OR, NOT)<br>- Field comparison operators<br>- Rule priority configurable |
| E-004-F-001-S-002 | As an admin, I want to specify rule actions | - Actions: Approve, Deny, Flag for Review, Calculate<br>- Denial reason configurable<br>- Flag reason for manual review |

**E-004-F-002: Document Requirements**

| Story ID | User Story | Acceptance Criteria |
|----------|------------|---------------------|
| E-004-F-002-S-001 | As an admin, I want to configure document requirements | - Document types definable<br>- Required vs optional designation<br>- Claim type associations |
| E-004-F-002-S-002 | As a provider, I want clear document requirements | - Required documents listed on form<br>- Upload status indicator<br>- Validation prevents submission without required docs |

---

### 3.5 Epic: Supporting Document Management (E-004)

**Description**: Handle attachments and supporting documents required for claims processing.

#### Features

| Feature ID | Feature Name | Description |
|------------|--------------|-------------|
| E-004-F-001 | Document Upload | Secure file upload with validation |
| E-004-F-002 | Document Retrieval | View and download claim attachments |

#### User Stories & Acceptance Criteria

| Story ID | User Story | Acceptance Criteria |
|----------|------------|---------------------|
| E-004-F-001-S-001 | As a provider, I want to upload supporting documents | - Drag-and-drop upload<br>- File type validation (PDF, images)<br>- Size limit: 10MB per file<br>- Progress indicator |
| E-004-F-002-S-001 | As an adjudicator, I want to view claim documents | - Thumbnail previews<br>- Full document viewer<br>- Download capability<br>- Document metadata visible |

---

### 3.6 Epic: Claims Adjudication Processing (E-005)

**Description**: Automated processing to adjudicate claims and determine payment amounts based on rules engine output.

#### Features

| Feature ID | Feature Name | Description |
|------------|--------------|-------------|
| E-005-F-001 | Automated Adjudication | Execute rules against submitted claims |
| E-005-F-002 | Manual Review Queue | Handle flagged claims requiring human review |
| E-005-F-003 | Payment Calculation | Calculate payment amounts based on fee schedules |

#### User Stories & Acceptance Criteria

**E-005-F-001: Automated Adjudication**

| Story ID | User Story | Acceptance Criteria |
|----------|------------|---------------------|
| E-005-F-001-S-001 | As the system, I want to automatically process claims | - Rules executed in priority order<br>- First matching rule determines outcome<br>- Audit log records all rule evaluations |
| E-005-F-001-S-002 | As the system, I want to handle rule conflicts | - Priority-based resolution<br>- Tie-breaker: most restrictive rule<br>- Conflict logged for review |

**E-005-F-002: Manual Review Queue**

| Story ID | User Story | Acceptance Criteria |
|----------|------------|---------------------|
| E-005-F-002-S-001 | As an adjudicator, I want to see flagged claims | - Queue sorted by priority/date<br>- Flag reason displayed<br>- Full claim details accessible |
| E-005-F-002-S-002 | As an adjudicator, I want to make decisions | - Approve/Deny buttons<br>- Decision reason required<br>- Decision logged with user attribution |

---

### 3.7 Epic: Rules Engine Administration (E-006)

**Description**: Manage, version, and audit rules engine configurations to maintain compliance with evolving AHCIP requirements.

#### Features

| Feature ID | Feature Name | Description |
|------------|--------------|-------------|
| E-006-F-001 | Rule Version Management | Version control for rule configurations |
| E-006-F-002 | Rule Testing | Test rules against sample data without affecting production |
| E-006-F-003 | Audit & Compliance Reporting | Generate audit trails and compliance reports |

#### User Stories & Acceptance Criteria

**E-006-F-001: Rule Version Management**

| Story ID | User Story | Acceptance Criteria |
|----------|------------|---------------------|
| E-006-F-001-S-001 | As an admin, I want to version rules | - Version created on each save<br>- Previous versions retrievable<br>- Effective date ranges configurable |
| E-006-F-001-S-002 | As an admin, I want to rollback rules | - One-click rollback to previous version<br>- Confirmation required<br>- Rollback logged |

**E-006-F-002: Rule Testing**

| Story ID | User Story | Acceptance Criteria |
|----------|------------|---------------------|
| E-006-F-002-S-001 | As an admin, I want to test rules | - Test mode flag isolates execution<br>- Sample claim data templates available<br>- Expected outcome configurable |
| E-006-F-002-S-002 | As an admin, I want to see test results | - Pass/fail status per rule<br>- Execution trace displayed<br>- Mismatches highlighted |

**E-006-F-003: Audit & Compliance Reporting**

| Story ID | User Story | Acceptance Criteria |
|----------|------------|---------------------|
| E-006-F-003-S-001 | As an auditor, I want rule execution history | - All rule evaluations logged<br>- Searchable by claim, rule, date<br>- Export capability (CSV, PDF) |
| E-006-F-003-S-002 | As an auditor, I want compliance reports | - Pre-built report templates<br>- Date range filtering<br>- Scheduled report generation |

---

## 4. Architecture

### 4.1 Architecture Overview

The Claims Processing Platform follows a modern multi-tier architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                          │
│  ┌─────────────────────┐  ┌─────────────────────────────────────┐  │
│  │  Provider Portal    │  │      Admin Dashboard                │  │
│  │  - Claims List      │  │  - Form Builder                     │  │
│  │  - Submission Form  │  │  - Template Management              │  │
│  │  - Status Tracker   │  │  - Rule Configuration               │  │
│  │  - Document Upload  │  │  - Flagged Claims Queue             │  │
│  └─────────────────────┘  └─────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          API GATEWAY LAYER                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐ │
│  │ API Gateway  │ │ Load Balancer│ │     WAF      │ │    CDN     │ │
│  │ (Rate Limit) │ │ (HA/Scaling) │ │ (Security)   │ │  (Static)  │ │
│  └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         MIDDLEWARE LAYER                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐ │
│  │    Auth      │ │  Validation  │ │ Rate Limit   │ │   Audit    │ │
│  │ (JWT/OAuth)  │ │  (Schema)    │ │  (Per-user)  │ │  Logging   │ │
│  └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘ │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐ │
│  │    CSRF      │ │ Sanitization │ │ Correlation  │ │ Test Mode  │ │
│  │ Protection   │ │   (XSS/SQL)  │ │    (Trace)   │ │  (QA)      │ │
│  └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         API SERVICE LAYER                           │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐ │
│  │ Claims API   │ │Forms/Template│ │ Rules Engine │ │ Document   │ │
│  │   Service    │ │  API Service │ │  API Service │ │ Mgmt API   │ │
│  └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘ │
│  ┌──────────────┐ ┌──────────────────────────────────────────────┐ │
│  │AHCIP Lookup  │ │             Audit API Service                │ │
│  │  API Service │ │                                              │ │
│  └──────────────┘ └──────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        CONTROLLER LAYER                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐ │
│  │   Claims     │ │    Forms     │ │    Rules     │ │  Document  │ │
│  │ Controller   │ │  Controller  │ │  Controller  │ │ Controller │ │
│  └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘ │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐ │
│  │ AHCIP Codes  │ │Rule Testing  │ │ Adjudication │ │Audit/Compl.│ │
│  │ Controller   │ │  Controller  │ │  Controller  │ │ Controller │ │
│  └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          DATA LAYER                                 │
│  ┌───────────────────────────────┐  ┌────────────────────────────┐ │
│  │      PostgreSQL RDS           │  │      Redis Cache           │ │
│  │  - claims_table               │  │  - Session data (15m TTL)  │ │
│  │  - claim_fields_table         │  │  - AHCIP codes (24h TTL)   │ │
│  │  - rules_table                │  │  - Rule defs (1h TTL)      │ │
│  │  - rule_versions_table        │  │  - Form templates          │ │
│  │  - form_definitions_table     │  │                            │ │
│  │  - form_templates_table       │  │                            │ │
│  │  - documents_table            │  │                            │ │
│  │  - audit_logs_table           │  │                            │ │
│  │  - users_table                │  │                            │ │
│  │  - providers_table            │  │                            │ │
│  │  - sessions_table             │  │                            │ │
│  │  - adjudication_results_table │  │                            │ │
│  │  - ahcip_codes_table          │  │                            │ │
│  └───────────────────────────────┘  └────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      EXTERNAL SERVICES                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐ │
│  │ AHCIP Fee    │ │ Notification │ │ Document     │ │  Identity  │ │
│  │  Schedule    │ │   Service    │ │Storage (S3)  │ │ Provider   │ │
│  └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘ │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐ │
│  │   Secrets    │ │   KMS/Key    │ │  Monitoring  │ │  Logging   │ │
│  │   Manager    │ │    Vault     │ │ (CloudWatch) │ │(ELK/Splunk)│ │
│  └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 Component Catalog

#### 4.2.1 Pages (User Interfaces)

| Page | Description | Target Users | Key Features |
|------|-------------|--------------|--------------|
| **Provider Claims Portal** | Main interface for providers | Providers | Claims list, form completion, status tracking, document upload |
| **Admin Dashboard** | Centralized administration | Admins | Metrics, recent activity, quick actions, navigation to subsystems |
| **Claim Form Builder** | Form design interface | Admins | Drag-and-drop canvas, field palette, preview panel |
| **Claim Template Management** | Template version control | Admins | Template list, version history, duplication |
| **Rule Configuration Interface** | Rule definition UI | Admins | Rule editor, parameter configuration, test execution |

#### 4.2.2 Web Components

| Component | Description | Parent Page(s) |
|-----------|-------------|----------------|
| Claims List Table | Sortable/filterable claims table | Provider Claims Portal |
| Claim Detail Modal | Full claim view with history | Provider Claims Portal |
| Claim Submission Form | Dynamic form renderer | Provider Claims Portal |
| Claim Status Tracker | Status history visualization | Provider Claims Portal |
| Document Uploader | File upload with validation | Provider Claims Portal |
| New Claim Button | Initiates new claim workflow | Provider Claims Portal |
| Provider Navigation Header | Top navigation bar | Provider Claims Portal |
| Claim Draft Indicator | Draft status visual cue | Provider Claims Portal |
| Admin Stats Cards | Key metrics display | Admin Dashboard |
| Recent Activity Feed | Real-time activity stream | Admin Dashboard |
| Quick Actions Panel | Shortcut buttons | Admin Dashboard |
| Admin Navigation Sidebar | Section navigation | Admin Dashboard |
| Form Designer Canvas | Drag-and-drop layout editor | Claim Form Builder |
| Form Field Palette | Available field types | Claim Form Builder |
| Form Preview Panel | Live form preview | Claim Form Builder |
| Template List View | Template selection grid | Claim Template Management |
| Template Version History | Version comparison view | Claim Template Management |
| Rule Editor Component | Condition builder UI | Rule Configuration Interface |
| Rule Test Case Selector | Test data selection | Rule Configuration Interface |
| Rule Test Results Panel | Test execution results | Rule Configuration Interface |
| Flagged Claims Queue | Manual review queue | Admin Dashboard |
| Document List View | Claim attachments grid | Provider Claims Portal |
| Success/Error Toast | Feedback notifications | All Pages |
| Confirmation Dialog | Destructive action confirmation | All Pages |

#### 4.2.3 Hooks & Composables (Frontend Logic)

| Hook | Purpose | Associated Feature |
|------|---------|-------------------|
| Claim Form State Management | Form field state, validation, draft status | E-003-F-001 |
| AHCIP Code Search Hook | Procedure code lookup | E-002-F-002 |
| Document Upload Logic | File validation and preparation | E-004-F-001 |
| Rule Versioning Hook | Rule history management | E-006-F-001 |
| Admin Dashboard Hook | Dashboard data aggregation | Admin Dashboard |
| Template Management Hook | Template CRUD operations | E-002-F-003 |
| Rule Configuration Hook | Rule editing state | E-004-F-001 |
| Claims Status Hook | Status polling and updates | E-003-F-003 |
| Flagged Claims Hook | Manual review queue state | E-005-F-002 |
| Form Designer State Hook | Form builder state | E-002-F-001 |
| Admin Stats Hook | Metrics aggregation | Admin Dashboard |
| Recent Activity Hook | Activity feed with WebSocket | Admin Dashboard |
| Rule Test Execution Hook | Test workflow management | E-006-F-002 |
| Template Version Hook | Version history state | E-002-F-003 |
| Document List Hook | Document metadata management | E-004-F-002 |
| Claims Test Utilities Hook | QA: Mock data and test helpers | Testing |
| E2E Test Selectors Hook | QA: Consistent data-testid attributes | Testing |

#### 4.2.4 API Services

| Service | Endpoint Base | Description |
|---------|---------------|-------------|
| Claims API Service | `/api/v1/claims` | Claims CRUD, submission, status |
| Forms & Templates API Service | `/api/v1/forms` | Form definitions, template management |
| Rules Engine API Service | `/api/v1/rules` | Rule definition, execution, testing |
| Document Management API Service | `/api/v1/documents` | Document upload, retrieval |
| AHCIP Code Lookup API Service | `/api/v1/ahcip-codes` | Procedure code search, fee schedules |
| Audit API Service | `/api/v1/audit` | Audit logs, compliance reports |

#### 4.2.5 API Controllers

| Controller | Responsibility | Key Methods |
|------------|---------------|-------------|
| Claims Controller | Claims lifecycle management | `create`, `update`, `submit`, `getStatus` |
| Forms Controller | Form and template CRUD | `create`, `update`, `duplicate`, `getVersions` |
| Rules Controller | Rule configuration | `create`, `update`, `activate`, `deactivate` |
| Document Controller | Document storage operations | `upload`, `download`, `delete`, `getByClaimId` |
| AHCIP Codes Controller | Code lookup with caching | `search`, `getByCode`, `getFeeSchedule` |
| Rule Testing Controller | Rule simulation | `executeTest`, `createTestCase`, `getResults` |
| Adjudication Workflow Controller | Automated processing | `processCliam`, `flagForReview`, `calculatePayment` |
| Audit & Compliance Controller | Reporting | `getAuditLog`, `generateReport`, `exportData` |

#### 4.2.6 Middleware Stack

| Middleware | Purpose | Order |
|------------|---------|-------|
| Auth Middleware | JWT validation, OAuth/SAML support | 1 |
| Rate Limiting Middleware | 100 req/min per provider, DDoS protection | 2 |
| CSRF Protection Middleware | Anti-CSRF tokens, SameSite cookies | 3 |
| Validation Middleware | Request body schema validation | 4 |
| Input Sanitization Middleware | XSS, SQL injection prevention | 5 |
| Request Correlation Middleware | Distributed tracing correlation IDs | 6 |
| Audit Logging Middleware | PHI access logging with PII masking | 7 |
| Test Mode Middleware | QA: Synthetic data injection | Conditional |

### 4.3 Database Schema

#### 4.3.1 Schema Overview

```
┌─────────────────────┐     ┌─────────────────────┐
│    users_table      │     │   providers_table   │
│─────────────────────│     │─────────────────────│
│ user_id (PK)        │◄────│ provider_id (PK)    │
│ email               │     │ npi_number          │
│ password_hash       │     │ provider_name       │
│ role                │     │ organization        │
│ provider_id (FK)    │     │ address             │
│ mfa_enabled         │     │ contact_email       │
│ last_login          │     │ phone               │
│ status              │     │ status              │
└─────────────────────┘     └─────────────────────┘
           │
           │
           ▼
┌─────────────────────┐     ┌─────────────────────┐
│   sessions_table    │     │   claims_table      │
│─────────────────────│     │─────────────────────│
│ session_id (PK)     │     │ claim_id (PK)       │
│ user_id (FK)        │     │ provider_id (FK)    │
│ token_hash          │     │ patient_id_hash     │
│ created_at          │     │ service_date        │
│ expires_at          │     │ status              │
│ ip_address          │     │ total_amount        │
│ user_agent          │     │ submitted_at        │
└─────────────────────┘     │ adjudicated_at      │
                            └─────────────────────┘
                                      │
           ┌──────────────────────────┼──────────────────────────┐
           │                          │                          │
           ▼                          ▼                          ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│ claim_fields_table  │  │  documents_table    │  │adjudication_results │
│─────────────────────│  │─────────────────────│  │─────────────────────│
│ field_id (PK)       │  │ document_id (PK)    │  │ result_id (PK)      │
│ claim_id (FK)       │  │ claim_id (FK)       │  │ claim_id (FK)       │
│ field_definition_id │  │ file_reference      │  │ status              │
│ field_value         │  │ document_type       │  │ payment_amount      │
│ created_at          │  │ upload_timestamp    │  │ denial_reason       │
└─────────────────────┘  │ file_size           │  │ processed_by (FK)   │
                         └─────────────────────┘  │ rules_applied       │
                                                  └─────────────────────┘

┌─────────────────────┐     ┌─────────────────────┐
│form_definitions_tbl │     │form_templates_table │
│─────────────────────│     │─────────────────────│
│ form_id (PK)        │◄────│ template_id (PK)    │
│ field_definitions   │     │ form_id (FK)        │
│ validation_rules    │     │ version             │
│ is_active           │     │ metadata            │
│ created_at          │     │ created_by          │
└─────────────────────┘     └─────────────────────┘

┌─────────────────────┐     ┌─────────────────────┐
│    rules_table      │     │rule_versions_table  │
│─────────────────────│     │─────────────────────│
│ rule_id (PK)        │◄────│ version_id (PK)     │
│ rule_name           │     │ rule_id (FK)        │
│ rule_type           │     │ version_number      │
│ condition_logic     │     │ condition_logic     │
│ action_type         │     │ effective_from      │
│ priority            │     │ created_by          │
│ is_active           │     │ created_at          │
│ effective_from      │     └─────────────────────┘
│ effective_to        │
│ created_by (FK)     │
└─────────────────────┘
           │
           ▼
┌─────────────────────┐     ┌─────────────────────┐
│  audit_logs_table   │     │  ahcip_codes_table  │
│─────────────────────│     │─────────────────────│
│ log_id (PK)         │     │ id (PK)             │
│ claim_id (FK)       │     │ procedure_code      │
│ rule_id (FK)        │     │ description         │
│ execution_result    │     │ category            │
│ decision_rationale  │     │ fee_amount          │
│ user_id (FK)        │     │ effective_date      │
│ timestamp           │     │ expiration_date     │
└─────────────────────┘     └─────────────────────┘
```

#### 4.3.2 Table Specifications

| Table | Primary Key | Key Columns | Indexes |
|-------|-------------|-------------|---------|
| `users_table` | `user_id` (UUID) | email, role, provider_id, status | email (unique), role |
| `providers_table` | `provider_id` (UUID) | npi_number, provider_name, status | npi_number (unique) |
| `sessions_table` | `session_id` (UUID) | user_id, expires_at | user_id, expires_at |
| `claims_table` | `claim_id` (UUID) | provider_id, status, submitted_at | provider_id, status, submitted_at |
| `claim_fields_table` | `field_id` (UUID) | claim_id, field_definition_id | claim_id |
| `documents_table` | `document_id` (UUID) | claim_id, document_type | claim_id, document_type |
| `adjudication_results_table` | `result_id` (UUID) | claim_id, status | claim_id, status |
| `form_definitions_table` | `form_id` (UUID) | field_definitions (JSONB), is_active | is_active |
| `form_templates_table` | `template_id` (UUID) | form_id, version | form_id, version |
| `rules_table` | `rule_id` (UUID) | rule_type, is_active, priority | rule_type, is_active |
| `rule_versions_table` | `version_id` (UUID) | rule_id, version_number | rule_id |
| `audit_logs_table` | `log_id` (UUID) | claim_id, rule_id, timestamp | claim_id, timestamp |
| `ahcip_codes_table` | `id` (UUID) | procedure_code, category, effective_date | procedure_code (unique), category |

### 4.4 Infrastructure Architecture

#### 4.4.1 Cloud Infrastructure Components

| Component | Technology | Purpose | Configuration |
|-----------|------------|---------|---------------|
| API Gateway | AWS API Gateway / Azure API Management | Rate limiting, SSL termination | 10K req/min per provider |
| Load Balancer | Application Load Balancer (ALB) | Traffic distribution, HA | Cross-AZ, health checks (30s), auto-scaling (CPU >70%) |
| WAF | AWS WAF / Azure WAF | OWASP protection, DDoS mitigation | SQL injection, XSS, CSRF rules |
| CDN | CloudFront / Azure CDN | Static asset caching | Global edge distribution |
| Cache | Redis Cluster (3-node) | Session, AHCIP codes, rule caching | Session: 15m TTL, Codes: 24h TTL, Rules: 1h TTL |
| Database | PostgreSQL RDS Multi-AZ | Primary data store | Automated backups, read replicas, encryption at rest |
| Object Storage | S3 / Azure Blob | Document storage | Server-side encryption, versioning, cross-region replication |
| Secrets Management | AWS Secrets Manager / Azure Key Vault | Credentials, API keys | Auto-rotation |
| Key Management | AWS KMS / Azure Key Vault | Encryption keys | PHI encryption |
| Monitoring | CloudWatch / Azure Monitor | Metrics, alerts | Latency, error rates, resource utilization |
| Logging | ELK / Splunk | Log aggregation | HIPAA-compliant retention |
| Identity Provider | Azure AD / Auth0 | OAuth 2.0, OIDC, SAML SSO | MFA enforcement |
| Disaster Recovery | Secondary Region | Hot standby | DNS failover |

### 4.5 Security Architecture

#### 4.5.1 Security Layers

```
┌─────────────────────────────────────────────────────────────────────┐
│                      PERIMETER SECURITY                             │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  WAF → API Gateway → Load Balancer → Application            │   │
│  │  (OWASP)  (Rate Limit)  (SSL Term)    (Auth/Authz)          │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    APPLICATION SECURITY                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐ │
│  │   Auth       │ │    RBAC      │ │   CSRF       │ │   Input    │ │
│  │(JWT/OAuth)   │ │ (Roles)      │ │ Protection   │ │Sanitization│ │
│  └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      DATA SECURITY                                  │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐ │
│  │ Encryption   │ │    PHI       │ │   Session    │ │  Database  │ │
│  │(TLS 1.3/AES) │ │ Protection   │ │ Management   │ │  Firewall  │ │
│  └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

#### 4.5.2 Security Policies

| Policy | Description | HIPAA Reference |
|--------|-------------|-----------------|
| PHI Data Protection Policy | AES-256 encryption at rest, TLS 1.3 in transit, data masking for logs | §164.312(a)(2)(iv) |
| Role-Based Access Control Policy | Provider, admin, adjudicator, auditor roles with least privilege | §164.312(a)(1) |
| Session Management Policy | 15-minute idle timeout, secure cookies, concurrent session limits | §164.312(d) |
| API Secret Management Policy | Secure storage, rotation, secrets never in code/logs | §164.312(d) |
| HIPAA Security Policy | PHI encryption, access controls, audit logging, breach notification | Multiple |

---

## 5. Technology Stack

### 5.1 Technology Summary

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Vue.js / React | Provider portal and admin interfaces |
| **Backend** | Node.js (Express/Fastify) | API services |
| **Database** | PostgreSQL | Relational data storage |
| **Cache** | Redis | Session management, caching |
| **Object Storage** | AWS S3 / Azure Blob | Document storage |
| **Authentication** | OAuth 2.0 / OIDC / SAML | Identity management |
| **API Gateway** | AWS API Gateway / Azure APIM | Traffic management |
| **Monitoring** | CloudWatch / Azure Monitor | Metrics and alerting |
| **Logging** | ELK Stack / Splunk | Log aggregation |

### 5.2 Frontend Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Framework | Vue.js 3 or React 18 | Reactive state management, component architecture |
| State Management | Pinia (Vue) / Redux Toolkit (React) | Predictable state handling |
| Styling | Tailwind CSS / Styled Components | Utility-first CSS, component styling |
| Form Handling | VeeValidate / React Hook Form | Declarative validation |
| Data Fetching | TanStack Query | Caching, background refetch |
| Testing | Jest, Cypress, Playwright | Unit, E2E testing |
| Accessibility | axe-core | WCAG 2.1 AA compliance |

### 5.3 Backend Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Runtime | Node.js 20 LTS | JavaScript ecosystem, async I/O |
| Framework | Express.js / Fastify | Mature middleware ecosystem |
| ORM | Prisma / TypeORM | Type-safe database access |
| Validation | Zod / Joi | Schema validation |
| Authentication | Passport.js | OAuth/OIDC/SAML strategies |
| Testing | Jest, Supertest | Unit and integration testing |
| API Documentation | OpenAPI / Swagger | Contract documentation |

### 5.4 Infrastructure Stack

| Component | Technology | Configuration |
|-----------|------------|---------------|
| Cloud Provider | AWS / Azure | Multi-AZ deployment |
| Container Orchestration | ECS / AKS | Auto-scaling, rolling deployments |
| Database | PostgreSQL 15 (RDS/Azure DB) | Multi-AZ, read replicas |
| Cache | Redis 7 (ElastiCache/Azure Cache) | 3-node cluster, Sentinel HA |
| Message Queue | SQS / Service Bus | Async claim processing |
| CDN | CloudFront / Azure CDN | Static asset distribution |
| DNS | Route 53 / Azure DNS | Failover routing |

### 5.5 Utility Libraries

| Utility | Purpose | Used By |
|---------|---------|---------|
| Pagination Helpers | Cursor/offset pagination | All list endpoints |
| Error Handler | Consistent error response formatting | All controllers |
| Date/Time Helpers | Timezone conversions, formatting | Claims, audit logs |
| Validation Helpers | Field validation, AHCIP code format | Claims, forms |
| Fee Calculation | Payment amount calculation | Adjudication |
| Response Helpers | Standardized API responses | All services |

---

## 6. Standards & Compliance

### 6.1 HIPAA Compliance

The Claims Processing Platform implements comprehensive HIPAA compliance measures:

#### 6.1.1 Technical Safeguards (§164.312)

| Requirement | Implementation |
|-------------|----------------|
| Access Control §164.312(a)(1) | RBAC with provider, admin, adjudicator, auditor roles |
| Audit Controls §164.312(b) | Comprehensive audit logging of all PHI access |
| Integrity §164.312(c)(1) | Input validation, checksums for documents |
| Person/Entity Authentication §164.312(d) | MFA, session management policies |
| Transmission Security §164.312(e)(1) | TLS 1.3 for all data in transit |

#### 6.1.2 Data Encryption

| Data State | Encryption | Key Management |
|------------|------------|----------------|
| At Rest (Database) | AES-256 | AWS KMS / Azure Key Vault |
| At Rest (Documents) | S3/Blob SSE | Managed keys with rotation |
| In Transit | TLS 1.3 | Certificate management |
| Backups | AES-256 | Separate backup keys |

#### 6.1.3 Audit Trail Requirements

| Event Type | Logged Data | Retention |
|------------|-------------|-----------|
| Authentication | User, timestamp, IP, success/failure | 6 years |
| PHI Access | User, claim_id, fields accessed | 6 years |
| Rule Execution | Claim_id, rule_id, outcome, rationale | 6 years |
| Configuration Changes | User, change details, timestamp | 6 years |

### 6.2 Accessibility Standards

| Standard | Implementation |
|----------|----------------|
| WCAG 2.1 AA | Automated axe-core scanning in CI/CD |
| Keyboard Navigation | All interactive elements keyboard accessible |
| Screen Reader Support | ARIA labels, semantic HTML |
| Color Contrast | Minimum 4.5:1 ratio |

### 6.3 Security Standards

| Standard | Implementation |
|----------|----------------|
| OWASP Top 10 | WAF rules, input sanitization, parameterized queries |
| NIST Cybersecurity Framework | Risk assessment, security monitoring |
| SOC 2 Type II | Access controls, encryption, audit trails |

---

## 7. Integration Points

### 7.1 External Service Integrations

#### 7.1.1 AHCIP Fee Schedule Service

| Aspect | Details |
|--------|---------|
| Purpose | Retrieve current procedure codes and fee schedules |
| Protocol | REST API with OAuth 2.0 client credentials |
| Caching | Redis cache with 24-hour TTL |
| Fallback | Cached data serves stale if service unavailable |
| Data Sync | Daily batch refresh + real-time lookups |

#### 7.1.2 Notification Service

| Aspect | Details |
|--------|---------|
| Purpose | Email/SMS notifications for claim status changes |
| Protocol | REST API / SQS message queue |
| Events | Claim submitted, status changed, payment processed |
| Templates | Provider-facing email templates |
| Preferences | User-configurable notification settings |

#### 7.1.3 Document Storage (S3/Blob)

| Aspect | Details |
|--------|---------|
| Purpose | Secure storage for claim attachments |
| Upload | Pre-signed URLs for direct browser upload |
| Download | Pre-signed URLs with expiration |
| Security | Server-side encryption, versioning enabled |
| Replication | Cross-region for disaster recovery |

#### 7.1.4 Identity Provider (Azure AD/Auth0)

| Aspect | Details |
|--------|---------|
| Purpose | Enterprise authentication and SSO |
| Protocols | OAuth 2.0, OIDC, SAML 2.0 |
| MFA | Required for all users per HIPAA |
| User Provisioning | SCIM for automated user management |

### 7.2 Data Flow Diagrams

#### 7.2.1 Claim Submission Flow

```
Provider → Portal → Claims API → Validation → Rules Engine → Database
                         ↓                          ↓
                    Documents API              Notification
                         ↓                      Service
                    S3 Storage                     ↓
                                             Email/SMS
```

#### 7.2.2 Adjudication Flow

```
Submitted Claim → Rules Engine → Automatic Decision?
                                        ↓
                            Yes ────────┴──────── No
                             ↓                     ↓
                    Calculate Payment      Flag for Review
                             ↓                     ↓
                    Update Status          Manual Queue
                             ↓                     ↓
                    Notification          Adjudicator Review
                                                   ↓
                                          Decision + Reason
                                                   ↓
                                          Update Status
                                                   ↓
                                          Notification
```

### 7.3 API Contract Summary

| API | Methods | Authentication | Rate Limit |
|-----|---------|----------------|------------|
| Claims API | GET, POST, PUT, DELETE | JWT Bearer | 100/min |
| Forms API | GET, POST, PUT, DELETE | JWT Bearer (Admin) | 50/min |
| Rules API | GET, POST, PUT, DELETE | JWT Bearer (Admin) | 50/min |
| Documents API | GET, POST, DELETE | JWT Bearer | 100/min |
| AHCIP Codes API | GET | JWT Bearer | 200/min |
| Audit API | GET | JWT Bearer (Auditor) | 50/min |

---

## 8. Recommendations

### 8.1 Architecture Recommendations

| Area | Recommendation | Priority |
|------|----------------|----------|
| **Microservices Evolution** | Consider decomposing the monolithic API into microservices (Claims, Rules, Documents) as scale demands | Medium |
| **Event-Driven Architecture** | Implement event sourcing for claims to maintain complete state history and enable replay | Medium |
| **CQRS Pattern** | Separate read and write models for reporting optimization | Low |
| **API Versioning** | Implement URL-based versioning (v1, v2) from day one | High |

### 8.2 Security Recommendations

| Area | Recommendation | Priority |
|------|----------------|----------|
| **Zero Trust** | Implement service mesh (Istio/Linkerd) for inter-service authentication | High |
| **Secret Rotation** | Automate database credential rotation every 90 days | High |
| **Penetration Testing** | Schedule quarterly third-party penetration tests | High |
| **Bug Bounty** | Consider establishing a responsible disclosure program | Medium |

### 8.3 Performance Recommendations

| Area | Recommendation | Target |
|------|----------------|--------|
| **API Response Time** | Maintain p95 latency under 500ms | High |
| **Database Query Optimization** | Index all foreign keys and frequently queried columns | High |
| **Cache Hit Ratio** | Target 90%+ cache hit ratio for AHCIP codes | Medium |
| **Document Upload** | Use resumable uploads for files >5MB | Medium |

### 8.4 Testing Recommendations

| Area | Recommendation | Target |
|------|----------------|--------|
| **Unit Test Coverage** | Minimum 80% coverage for all services | High |
| **Integration Test Coverage** | Minimum 60% coverage for API endpoints | High |
| **Contract Testing** | Pact tests for all frontend-backend contracts | High |
| **Load Testing** | Weekly k6 runs simulating peak load (1000 concurrent users) | Medium |
| **Security Scanning** | SAST/DAST in CI/CD pipeline, block on critical findings | High |

### 8.5 Quality Gates

| Gate | Criteria | Action on Failure |
|------|----------|-------------------|
| Code Coverage | ≥80% unit, ≥60% integration | Block merge |
| Security Scan | 0 critical, 0 high vulnerabilities | Block deployment |
| E2E Smoke Tests | 100% pass rate | Block deployment |
| Performance Regression | ≤10% increase in p95 latency | Alert + review |
| Accessibility | 0 WCAG 2.1 AA violations | Block merge |

### 8.6 Operational Recommendations

| Area | Recommendation | Priority |
|------|----------------|----------|
| **Runbook Documentation** | Create operational runbooks for incident response | High |
| **Chaos Engineering** | Implement controlled failure injection to test resilience | Medium |
| **Blue-Green Deployments** | Zero-downtime deployments with instant rollback capability | High |
| **Database Migrations** | Use forward-only, backwards-compatible migrations | High |
| **Feature Flags** | Implement feature flag system for gradual rollouts | Medium |

### 8.7 Documentation Recommendations

| Area | Recommendation | Priority |
|------|----------------|----------|
| **API Documentation** | Maintain OpenAPI specs with examples | High |
| **ADRs** | Document architectural decisions with context | High |
| **User Guides** | Create provider and admin user documentation | High |
| **Training Materials** | Develop onboarding materials for new team members | Medium |

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| AHCIP | Alberta Health Care Insurance Plan |
| Adjudication | Process of determining claim validity and payment amount |
| Claim | A request for payment for healthcare services rendered |
| PHI | Protected Health Information (HIPAA-regulated data) |
| Provider | Healthcare professional or organization submitting claims |
| Rule | Configurable logic for validating or adjudicating claims |
| Template | Reusable form configuration for claim types |

## Appendix B: Reference Documents

- HIPAA Security Rule (45 CFR Part 164)
- AHCIP Fee Schedule Documentation
- WCAG 2.1 Guidelines
- OWASP Top 10 2021

---

*This document was generated based on canvas architecture data and should be reviewed and validated by project stakeholders.*