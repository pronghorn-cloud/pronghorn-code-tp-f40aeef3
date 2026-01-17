import axios, { type AxiosInstance, type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import type { ApiResponse, ApiError } from '@/types'

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Add auth token
    const token = localStorage.getItem('accessToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // Add correlation ID for tracing
    config.headers['X-Correlation-ID'] = generateCorrelationId()

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiError>) => {
    const originalRequest = error.config

    // Handle 401 - Token expired
    if (error.response?.status === 401 && originalRequest) {
      try {
        const refreshToken = localStorage.getItem('refreshToken')
        if (refreshToken) {
          const response = await axios.post('/api/v1/auth/refresh', {
            refreshToken,
          })
          
          const { accessToken } = response.data
          localStorage.setItem('accessToken', accessToken)
          
          // Retry original request
          originalRequest.headers.Authorization = `Bearer ${accessToken}`
          return api(originalRequest)
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('accessToken')
        localStorage.removeItem('refreshToken')
        window.location.href = '/auth/login'
      }
    }

    return Promise.reject(error)
  }
)

// Helper to generate correlation ID
function generateCorrelationId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

export default api

// ==================== Auth Service ====================
export const authService = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),

  logout: () =>
    api.post('/auth/logout'),

  refreshToken: (refreshToken: string) =>
    api.post('/auth/refresh', { refreshToken }),

  getCurrentUser: () =>
    api.get('/auth/me'),

  forgotPassword: (email: string) =>
    api.post('/auth/forgot-password', { email }),

  resetPassword: (token: string, password: string) =>
    api.post('/auth/reset-password', { token, password }),
}

// ==================== Claims Service ====================
export const claimsService = {
  list: (params?: Record<string, any>) =>
    api.get('/claims', { params }),

  get: (id: string) =>
    api.get(`/claims/${id}`),

  create: (data: Record<string, any>) =>
    api.post('/claims', data),

  update: (id: string, data: Record<string, any>) =>
    api.put(`/claims/${id}`, data),

  saveDraft: (id: string, data: Record<string, any>) =>
    api.put(`/claims/${id}/draft`, data),

  submit: (id: string) =>
    api.post(`/claims/${id}/submit`),

  getStatus: (id: string) =>
    api.get(`/claims/${id}/status`),

  getStatusHistory: (id: string) =>
    api.get(`/claims/${id}/status-history`),

  delete: (id: string) =>
    api.delete(`/claims/${id}`),

  // Admin endpoints
  getFlagged: (params?: Record<string, any>) =>
    api.get('/claims/flagged', { params }),

  adjudicate: (id: string, data: { action: 'approve' | 'deny'; reason?: string }) =>
    api.post(`/claims/${id}/adjudicate`, data),
}

// ==================== Forms Service ====================
export const formsService = {
  list: (params?: Record<string, any>) =>
    api.get('/forms', { params }),

  get: (id: string) =>
    api.get(`/forms/${id}`),

  create: (data: Record<string, any>) =>
    api.post('/forms', data),

  update: (id: string, data: Record<string, any>) =>
    api.put(`/forms/${id}`, data),

  delete: (id: string) =>
    api.delete(`/forms/${id}`),

  duplicate: (id: string) =>
    api.post(`/forms/${id}/duplicate`),
}

// ==================== Templates Service ====================
export const templatesService = {
  list: (params?: Record<string, any>) =>
    api.get('/templates', { params }),

  get: (id: string) =>
    api.get(`/templates/${id}`),

  create: (data: Record<string, any>) =>
    api.post('/templates', data),

  update: (id: string, data: Record<string, any>) =>
    api.put(`/templates/${id}`, data),

  delete: (id: string) =>
    api.delete(`/templates/${id}`),

  duplicate: (id: string) =>
    api.post(`/templates/${id}/duplicate`),

  getVersions: (id: string) =>
    api.get(`/templates/${id}/versions`),

  rollback: (id: string, versionId: string) =>
    api.post(`/templates/${id}/rollback`, { versionId }),
}

// ==================== Rules Service ====================
export const rulesService = {
  list: (params?: Record<string, any>) =>
    api.get('/rules', { params }),

  get: (id: string) =>
    api.get(`/rules/${id}`),

  create: (data: Record<string, any>) =>
    api.post('/rules', data),

  update: (id: string, data: Record<string, any>) =>
    api.put(`/rules/${id}`, data),

  delete: (id: string) =>
    api.delete(`/rules/${id}`),

  activate: (id: string) =>
    api.post(`/rules/${id}/activate`),

  deactivate: (id: string) =>
    api.post(`/rules/${id}/deactivate`),

  getVersions: (id: string) =>
    api.get(`/rules/${id}/versions`),

  rollback: (id: string, versionId: string) =>
    api.post(`/rules/${id}/rollback`, { versionId }),

  test: (data: Record<string, any>) =>
    api.post('/rules/test', data),

  execute: (claimId: string) =>
    api.post('/rules/execute', { claimId }),
}

// ==================== Documents Service ====================
export const documentsService = {
  list: (claimId: string) =>
    api.get(`/claims/${claimId}/documents`),

  get: (id: string) =>
    api.get(`/documents/${id}`),

  getUploadUrl: (data: { claimId: string; fileName: string; fileType: string }) =>
    api.post('/documents/upload-url', data),

  confirmUpload: (id: string, data: { documentType: string }) =>
    api.post(`/documents/${id}/confirm`, data),

  delete: (id: string) =>
    api.delete(`/documents/${id}`),

  download: (id: string) =>
    api.get(`/documents/${id}/download`),
}

// ==================== AHCIP Codes Service ====================
export const ahcipService = {
  search: (params: { query?: string; category?: string; limit?: number }) =>
    api.get('/ahcip-codes/search', { params }),

  get: (code: string) =>
    api.get(`/ahcip-codes/${code}`),

  getFeeSchedule: (codes: string[], effectiveDate?: string) =>
    api.post('/ahcip-codes/fee-schedule', { codes, effectiveDate }),

  getCategories: () =>
    api.get('/ahcip-codes/categories'),
}

// ==================== Audit Service ====================
export const auditService = {
  getLogs: (params?: Record<string, any>) =>
    api.get('/audit/logs', { params }),

  getLog: (id: string) =>
    api.get(`/audit/logs/${id}`),

  exportLogs: (params: Record<string, any>) =>
    api.get('/audit/logs/export', { params, responseType: 'blob' }),

  getReports: () =>
    api.get('/audit/reports'),

  generateReport: (data: { type: string; dateFrom: string; dateTo: string }) =>
    api.post('/audit/reports', data),

  downloadReport: (id: string) =>
    api.get(`/audit/reports/${id}/download`, { responseType: 'blob' }),
}

// ==================== Users Service ====================
export const usersService = {
  list: (params?: Record<string, any>) =>
    api.get('/users', { params }),

  get: (id: string) =>
    api.get(`/users/${id}`),

  create: (data: Record<string, any>) =>
    api.post('/users', data),

  update: (id: string, data: Record<string, any>) =>
    api.put(`/users/${id}`, data),

  delete: (id: string) =>
    api.delete(`/users/${id}`),

  updatePassword: (id: string, data: { currentPassword: string; newPassword: string }) =>
    api.put(`/users/${id}/password`, data),
}

// ==================== Dashboard Service ====================
export const dashboardService = {
  getStats: () =>
    api.get('/dashboard/stats'),

  getRecentActivity: (limit?: number) =>
    api.get('/dashboard/activity', { params: { limit } }),

  getChartData: (type: string, params?: Record<string, any>) =>
    api.get(`/dashboard/charts/${type}`, { params }),
}
