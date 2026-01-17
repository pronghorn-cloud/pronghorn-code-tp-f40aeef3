// ============================================
// Core Types for Claims Processing Platform
// ============================================

// ==================== User & Auth Types ====================
export type UserRole = 'provider' | 'admin' | 'adjudicator' | 'auditor'

export interface User {
  id: string
  email: string
  firstName: string
  lastName: string
  role: UserRole
  providerId?: string
  mfaEnabled: boolean
  lastLogin?: string
  status: 'active' | 'inactive' | 'suspended'
  createdAt: string
  updatedAt: string
}

export interface Provider {
  id: string
  npiNumber: string
  providerName: string
  organization: string
  address: Address
  contactEmail: string
  phone: string
  status: 'active' | 'inactive'
  createdAt: string
  updatedAt: string
}

export interface Address {
  street: string
  city: string
  province: string
  postalCode: string
  country: string
}

export interface AuthState {
  user: User | null
  provider: Provider | null
  isAuthenticated: boolean
  isLoading: boolean
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface AuthResponse {
  user: User
  provider?: Provider
  accessToken: string
  refreshToken: string
  expiresAt: string
}

// ==================== Claim Types ====================
export type ClaimStatus = 'draft' | 'submitted' | 'in_review' | 'adjudicated' | 'approved' | 'denied' | 'paid'

export interface Claim {
  id: string
  providerId: string
  templateId: string
  patientInfo: PatientInfo
  serviceLines: ServiceLine[]
  status: ClaimStatus
  totalAmount: number
  submittedAt?: string
  adjudicatedAt?: string
  createdAt: string
  updatedAt: string
  documents?: Document[]
  adjudicationResult?: AdjudicationResult
  statusHistory: ClaimStatusHistory[]
}

export interface PatientInfo {
  firstName: string
  lastName: string
  dateOfBirth: string
  healthCardNumber: string
  gender: 'male' | 'female' | 'other'
  address?: Address
  phone?: string
  email?: string
}

export interface ServiceLine {
  id: string
  procedureCode: string
  description: string
  serviceDate: string
  quantity: number
  unitPrice: number
  total: number
  diagnosisCode?: string
  modifier?: string
}

export interface ClaimStatusHistory {
  id: string
  status: ClaimStatus
  changedAt: string
  changedBy: string
  reason?: string
}

export interface ClaimDraft {
  templateId: string
  patientInfo: Partial<PatientInfo>
  serviceLines: Partial<ServiceLine>[]
  documents?: string[]
}

export interface ClaimFilters {
  status?: ClaimStatus | ClaimStatus[]
  dateFrom?: string
  dateTo?: string
  search?: string
  sortBy?: 'createdAt' | 'submittedAt' | 'totalAmount' | 'status'
  sortOrder?: 'asc' | 'desc'
  page?: number
  limit?: number
}

// ==================== Adjudication Types ====================
export interface AdjudicationResult {
  id: string
  claimId: string
  status: 'approved' | 'denied' | 'partial'
  paymentAmount: number
  denialReason?: string
  processedBy?: string
  processedAt: string
  rulesApplied: RuleExecutionResult[]
  flaggedForReview: boolean
  flagReason?: string
}

export interface RuleExecutionResult {
  ruleId: string
  ruleName: string
  passed: boolean
  action: 'approve' | 'deny' | 'flag' | 'calculate'
  message?: string
  calculatedAmount?: number
}

// ==================== Document Types ====================
export type DocumentType = 'referral' | 'lab_result' | 'prescription' | 'medical_record' | 'imaging' | 'other'

export interface Document {
  id: string
  claimId: string
  fileName: string
  fileType: string
  fileSize: number
  documentType: DocumentType
  uploadedAt: string
  uploadedBy: string
  url?: string
}

export interface DocumentUploadRequest {
  claimId: string
  file: File
  documentType: DocumentType
}

// ==================== Form & Template Types ====================
export type FieldType = 'text' | 'number' | 'date' | 'select' | 'checkbox' | 'textarea' | 'ahcip_code' | 'file'

export interface FormFieldDefinition {
  id: string
  name: string
  label: string
  type: FieldType
  required: boolean
  placeholder?: string
  helpText?: string
  defaultValue?: any
  options?: SelectOption[]
  validation?: FieldValidation
  order: number
  section?: string
  width?: 'full' | 'half' | 'third'
}

export interface SelectOption {
  value: string
  label: string
}

export interface FieldValidation {
  pattern?: string
  minLength?: number
  maxLength?: number
  min?: number
  max?: number
  customMessage?: string
}

export interface FormDefinition {
  id: string
  name: string
  description?: string
  fields: FormFieldDefinition[]
  sections: FormSection[]
  validationRules: FormValidationRule[]
  isActive: boolean
  createdAt: string
  updatedAt: string
}

export interface FormSection {
  id: string
  name: string
  description?: string
  order: number
}

export interface FormValidationRule {
  id: string
  type: 'required' | 'pattern' | 'custom' | 'cross_field'
  fieldId?: string
  condition?: string
  message: string
}

export interface FormTemplate {
  id: string
  formId: string
  name: string
  description?: string
  version: number
  metadata?: Record<string, any>
  isActive: boolean
  createdBy: string
  createdAt: string
  updatedAt: string
}

export interface TemplateVersion {
  id: string
  templateId: string
  version: number
  changes: string
  createdBy: string
  createdAt: string
}

// ==================== Rule Types ====================
export type RuleType = 'validation' | 'adjudication'
export type RuleAction = 'approve' | 'deny' | 'flag' | 'calculate'
export type ConditionOperator = '=' | '!=' | '>' | '<' | '>=' | '<=' | 'in' | 'not_in' | 'contains' | 'starts_with'

export interface Rule {
  id: string
  name: string
  description?: string
  type: RuleType
  conditionLogic: ConditionGroup
  action: RuleAction
  actionParams?: Record<string, any>
  priority: number
  isActive: boolean
  effectiveFrom: string
  effectiveTo?: string
  createdBy: string
  createdAt: string
  updatedAt: string
}

export interface ConditionGroup {
  type: 'AND' | 'OR' | 'NOT'
  conditions: (Condition | ConditionGroup)[]
}

export interface Condition {
  field: string
  operator: ConditionOperator
  value: any
}

export interface RuleVersion {
  id: string
  ruleId: string
  version: number
  conditionLogic: ConditionGroup
  changes?: string
  createdBy: string
  createdAt: string
}

export interface RuleTestRequest {
  ruleIds: string[]
  claimData?: Partial<Claim>
  scenario?: string
}

export interface RuleTestResult {
  passed: boolean
  executionTrace: RuleExecutionTrace[]
  assertions: TestAssertion[]
  coverageReport?: CoverageReport
}

export interface RuleExecutionTrace {
  ruleId: string
  ruleName: string
  conditionEvaluations: ConditionEvaluation[]
  finalResult: boolean
  action?: RuleAction
  executionTime: number
}

export interface ConditionEvaluation {
  condition: string
  result: boolean
  actualValue: any
  expectedValue: any
}

export interface TestAssertion {
  name: string
  passed: boolean
  expected: any
  actual: any
  message?: string
}

export interface CoverageReport {
  totalRules: number
  rulesCovered: number
  coveragePercentage: number
  uncoveredRules: string[]
}

// ==================== AHCIP Code Types ====================
export interface AHCIPCode {
  id: string
  procedureCode: string
  description: string
  category: string
  feeAmount: number
  effectiveDate: string
  expirationDate?: string
  isActive: boolean
}

export interface AHCIPSearchParams {
  query?: string
  category?: string
  effectiveDate?: string
  limit?: number
}

// ==================== Audit Types ====================
export type AuditAction = 
  | 'CLAIM_CREATED'
  | 'CLAIM_UPDATED'
  | 'CLAIM_SUBMITTED'
  | 'CLAIM_ADJUDICATED'
  | 'PHI_ACCESSED'
  | 'RULE_EXECUTED'
  | 'RULE_CREATED'
  | 'RULE_UPDATED'
  | 'DOCUMENT_UPLOADED'
  | 'DOCUMENT_DELETED'
  | 'USER_LOGIN'
  | 'USER_LOGOUT'
  | 'TEMPLATE_CREATED'
  | 'TEMPLATE_UPDATED'

export interface AuditLog {
  id: string
  action: AuditAction
  userId: string
  userName: string
  claimId?: string
  ruleId?: string
  documentId?: string
  details?: Record<string, any>
  ipAddress: string
  userAgent: string
  timestamp: string
}

export interface AuditLogFilters {
  action?: AuditAction | AuditAction[]
  userId?: string
  claimId?: string
  dateFrom?: string
  dateTo?: string
  page?: number
  limit?: number
}

// ==================== Dashboard Types ====================
export interface DashboardStats {
  totalClaims: number
  pendingClaims: number
  flaggedClaims: number
  approvedToday: number
  deniedToday: number
  totalAmount: number
  averageProcessingTime: number
}

export interface RecentActivity {
  id: string
  type: 'claim_submitted' | 'claim_adjudicated' | 'rule_updated' | 'user_login'
  description: string
  userId: string
  userName: string
  timestamp: string
  metadata?: Record<string, any>
}

// ==================== API Response Types ====================
export interface PaginatedResponse<T> {
  data: T[]
  pagination: Pagination
}

export interface Pagination {
  page: number
  limit: number
  total: number
  totalPages: number
  hasNext: boolean
  hasPrevious: boolean
}

export interface ApiError {
  code: string
  message: string
  details?: Record<string, any>
  validationErrors?: ValidationError[]
}

export interface ValidationError {
  field: string
  message: string
  code: string
}

export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: ApiError
  correlationId?: string
}
