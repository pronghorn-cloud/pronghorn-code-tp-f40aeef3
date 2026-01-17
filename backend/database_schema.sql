-- Database Schema DDL based on SQLAlchemy Models

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ENUM Types
CREATE TYPE user_role AS ENUM ('provider', 'admin', 'adjudicator', 'auditor');
CREATE TYPE user_status AS ENUM ('active', 'inactive', 'suspended', 'pending');
CREATE TYPE provider_status AS ENUM ('active', 'inactive', 'suspended', 'pending_verification');
CREATE TYPE claim_status AS ENUM ('draft', 'submitted', 'in_review', 'adjudicated', 'approved', 'denied', 'paid', 'appealed', 'cancelled');
CREATE TYPE adjudication_status AS ENUM ('pending', 'processing', 'approved', 'denied', 'partial_approval', 'flagged', 'manual_review', 'error');
CREATE TYPE document_type AS ENUM ('medical_record', 'lab_result', 'prescription', 'referral', 'authorization', 'invoice', 'other');
CREATE TYPE document_status AS ENUM ('pending', 'uploaded', 'verified', 'rejected', 'deleted');
CREATE TYPE audit_action AS ENUM (
    'user_login', 'user_logout', 'user_login_failed', 'password_changed', 'mfa_enabled', 'mfa_disabled',
    'claim_created', 'claim_updated', 'claim_submitted', 'claim_adjudicated', 'claim_approved', 'claim_denied', 'claim_deleted',
    'phi_accessed', 'phi_exported',
    'document_uploaded', 'document_downloaded', 'document_deleted',
    'rule_created', 'rule_updated', 'rule_deleted', 'rule_executed',
    'form_created', 'form_updated', 'template_created', 'template_updated',
    'user_created', 'user_updated', 'user_deleted', 'settings_changed'
);
CREATE TYPE rule_type AS ENUM ('validation', 'adjudication', 'calculation', 'notification');
CREATE TYPE action_type AS ENUM ('approve', 'deny', 'flag', 'calculate', 'notify', 'transform');

-- TABLE: providers
CREATE TABLE providers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    npi_number VARCHAR(20) NOT NULL UNIQUE,
    provider_name VARCHAR(255) NOT NULL,
    organization VARCHAR(255),
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    province VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'Canada',
    contact_email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    fax VARCHAR(50),
    status provider_status NOT NULL DEFAULT 'pending_verification',
    specialty VARCHAR(100),
    license_number VARCHAR(100),
    notes TEXT
);
CREATE INDEX ix_providers_npi_number ON providers(npi_number);

-- TABLE: users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role user_role NOT NULL DEFAULT 'provider',
    status user_status NOT NULL DEFAULT 'pending',
    provider_id UUID REFERENCES providers(id),
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(255),
    last_login TIMESTAMP WITH TIME ZONE,
    failed_login_attempts VARCHAR(10) DEFAULT '0',
    locked_until TIMESTAMP WITH TIME ZONE,
    password_changed_at TIMESTAMP WITH TIME ZONE,
    must_change_password BOOLEAN DEFAULT FALSE
);
CREATE INDEX ix_users_email ON users(email);

-- TABLE: form_definitions
CREATE TABLE form_definitions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    form_name VARCHAR(255) NOT NULL,
    form_code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    field_definitions JSONB NOT NULL DEFAULT '[]',
    validation_rules JSONB DEFAULT '[]',
    layout_config JSONB DEFAULT '{}',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    category VARCHAR(100),
    claim_type VARCHAR(100),
    created_by UUID REFERENCES users(id)
);
CREATE INDEX ix_form_definitions_form_code ON form_definitions(form_code);
CREATE INDEX ix_form_definitions_is_active ON form_definitions(is_active);

-- TABLE: form_templates
CREATE TABLE form_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    form_id UUID NOT NULL REFERENCES form_definitions(id),
    template_name VARCHAR(255) NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    field_overrides JSONB DEFAULT '{}',
    additional_fields JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    notes TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    created_by UUID REFERENCES users(id)
);
CREATE INDEX ix_form_templates_form_id ON form_templates(form_id);

-- TABLE: claims
CREATE TABLE claims (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    provider_id UUID NOT NULL REFERENCES providers(id),
    claim_number VARCHAR(50) NOT NULL UNIQUE,
    patient_id_hash VARCHAR(64),
    patient_info_encrypted TEXT,
    service_date TIMESTAMP WITH TIME ZONE,
    service_end_date TIMESTAMP WITH TIME ZONE,
    template_id UUID REFERENCES form_templates(id),
    status claim_status NOT NULL DEFAULT 'draft',
    total_amount NUMERIC(10, 2),
    approved_amount NUMERIC(10, 2),
    service_lines JSONB DEFAULT '[]',
    submitted_at TIMESTAMP WITH TIME ZONE,
    adjudicated_at TIMESTAMP WITH TIME ZONE,
    paid_at TIMESTAMP WITH TIME ZONE,
    denial_reason TEXT,
    internal_notes TEXT
);
CREATE INDEX ix_claims_provider_id ON claims(provider_id);
CREATE INDEX ix_claims_claim_number ON claims(claim_number);
CREATE INDEX ix_claims_patient_id_hash ON claims(patient_id_hash);
CREATE INDEX ix_claims_status ON claims(status);
CREATE INDEX ix_claims_submitted_at ON claims(submitted_at);

-- TABLE: claim_fields
CREATE TABLE claim_fields (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    claim_id UUID NOT NULL REFERENCES claims(id),
    field_definition_id VARCHAR(100) NOT NULL,
    field_name VARCHAR(255) NOT NULL,
    field_value TEXT,
    field_value_encrypted TEXT,
    is_phi VARCHAR(5) DEFAULT 'false'
);
CREATE INDEX ix_claim_fields_claim_id ON claim_fields(claim_id);

-- TABLE: adjudication_results
CREATE TABLE adjudication_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    claim_id UUID NOT NULL UNIQUE REFERENCES claims(id),
    status adjudication_status NOT NULL DEFAULT 'pending',
    submitted_amount NUMERIC(10, 2),
    approved_amount NUMERIC(10, 2),
    adjustment_amount NUMERIC(10, 2),
    payment_amount NUMERIC(10, 2),
    payment_date TIMESTAMP WITH TIME ZONE,
    denial_reason TEXT,
    denial_code VARCHAR(50),
    flag_reason TEXT,
    rules_applied JSONB DEFAULT '[]',
    processed_by UUID REFERENCES users(id),
    processed_at TIMESTAMP WITH TIME ZONE,
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    review_notes TEXT,
    line_item_results JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}'
);
CREATE INDEX ix_adjudication_results_claim_id ON adjudication_results(claim_id);
CREATE INDEX ix_adjudication_results_status ON adjudication_results(status);

-- TABLE: documents
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    claim_id UUID NOT NULL REFERENCES claims(id),
    original_filename VARCHAR(255) NOT NULL,
    file_reference VARCHAR(500) NOT NULL,
    file_type VARCHAR(100) NOT NULL,
    file_size INTEGER NOT NULL,
    document_type document_type NOT NULL DEFAULT 'other',
    description VARCHAR(500),
    status document_status NOT NULL DEFAULT 'pending',
    uploaded_at TIMESTAMP WITH TIME ZONE,
    uploaded_by UUID REFERENCES users(id),
    verified_at TIMESTAMP WITH TIME ZONE,
    verified_by UUID REFERENCES users(id),
    checksum VARCHAR(64),
    virus_scan_result VARCHAR(50),
    virus_scan_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX ix_documents_claim_id ON documents(claim_id);

-- TABLE: rules
CREATE TABLE rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    rule_name VARCHAR(255) NOT NULL,
    rule_code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    rule_type rule_type NOT NULL DEFAULT 'validation',
    action_type action_type NOT NULL DEFAULT 'flag',
    condition_logic JSONB NOT NULL DEFAULT '{}',
    priority INTEGER NOT NULL DEFAULT 100,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    effective_from TIMESTAMP WITH TIME ZONE,
    effective_to TIMESTAMP WITH TIME ZONE,
    denial_reason_template TEXT,
    flag_reason_template TEXT,
    category VARCHAR(100),
    tags JSONB DEFAULT '[]',
    created_by UUID REFERENCES users(id),
    last_modified_by UUID REFERENCES users(id)
);
CREATE INDEX ix_rules_rule_code ON rules(rule_code);
CREATE INDEX ix_rules_rule_type ON rules(rule_type);
CREATE INDEX ix_rules_is_active ON rules(is_active);

-- TABLE: rule_versions
CREATE TABLE rule_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    rule_id UUID NOT NULL REFERENCES rules(id),
    version_number INTEGER NOT NULL,
    rule_name VARCHAR(255) NOT NULL,
    rule_type rule_type NOT NULL,
    action_type action_type NOT NULL,
    condition_logic JSONB NOT NULL,
    priority INTEGER NOT NULL,
    change_description TEXT,
    effective_from TIMESTAMP WITH TIME ZONE,
    created_by UUID REFERENCES users(id)
);
CREATE INDEX ix_rule_versions_rule_id ON rule_versions(rule_id);

-- TABLE: audit_logs
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    action audit_action NOT NULL,
    action_description TEXT,
    claim_id UUID REFERENCES claims(id),
    rule_id UUID REFERENCES rules(id),
    document_id UUID REFERENCES documents(id),
    user_id UUID REFERENCES users(id),
    execution_result VARCHAR(50),
    decision_rationale TEXT,
    ip_address INET,
    user_agent VARCHAR(500),
    correlation_id VARCHAR(100),
    phi_accessed BOOLEAN DEFAULT FALSE,
    masked_fields JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    before_state JSONB,
    after_state JSONB
);
CREATE INDEX ix_audit_logs_action ON audit_logs(action);
CREATE INDEX ix_audit_logs_claim_id ON audit_logs(claim_id);
CREATE INDEX ix_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX ix_audit_logs_correlation_id ON audit_logs(correlation_id);

-- TABLE: sessions
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id),
    token_hash VARCHAR(255) NOT NULL,
    refresh_token_hash VARCHAR(255),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_activity TIMESTAMP WITH TIME ZONE,
    ip_address INET,
    user_agent VARCHAR(500),
    device_info VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    revoked_at TIMESTAMP WITH TIME ZONE,
    revoke_reason VARCHAR(255)
);
CREATE INDEX ix_sessions_user_id ON sessions(user_id);
CREATE INDEX ix_sessions_token_hash ON sessions(token_hash);
CREATE INDEX ix_sessions_expires_at ON sessions(expires_at);
