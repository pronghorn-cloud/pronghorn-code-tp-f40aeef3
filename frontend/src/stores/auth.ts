import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, Provider, AuthState, LoginCredentials, AuthResponse } from '@/types'
import { authService } from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const provider = ref<Provider | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!user.value)
  const isProvider = computed(() => user.value?.role === 'provider')
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isAdjudicator = computed(() => user.value?.role === 'adjudicator')
  const isAuditor = computed(() => user.value?.role === 'auditor')
  const fullName = computed(() => 
    user.value ? `${user.value.firstName} ${user.value.lastName}` : ''
  )
  const userInitials = computed(() => {
    if (!user.value) return ''
    return `${user.value.firstName[0]}${user.value.lastName[0]}`.toUpperCase()
  })

  // Actions
  async function login(credentials: LoginCredentials): Promise<boolean> {
    isLoading.value = true
    error.value = null

    try {
      const response = await authService.login(credentials.email, credentials.password)
      const data: AuthResponse = response.data

      // Store tokens
      localStorage.setItem('accessToken', data.accessToken)
      localStorage.setItem('refreshToken', data.refreshToken)

      // Update state
      user.value = data.user
      provider.value = data.provider || null

      return true
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Login failed. Please try again.'
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function logout(): Promise<void> {
    try {
      await authService.logout()
    } catch (err) {
      // Continue with logout even if API call fails
      console.error('Logout API call failed:', err)
    } finally {
      // Clear state and storage
      user.value = null
      provider.value = null
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
    }
  }

  async function checkAuth(): Promise<boolean> {
    const token = localStorage.getItem('accessToken')
    if (!token) {
      return false
    }

    isLoading.value = true

    try {
      const response = await authService.getCurrentUser()
      user.value = response.data.user
      provider.value = response.data.provider || null
      return true
    } catch (err) {
      // Token invalid or expired
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
      user.value = null
      provider.value = null
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function refreshToken(): Promise<boolean> {
    const refreshTokenValue = localStorage.getItem('refreshToken')
    if (!refreshTokenValue) {
      return false
    }

    try {
      const response = await authService.refreshToken(refreshTokenValue)
      localStorage.setItem('accessToken', response.data.accessToken)
      return true
    } catch (err) {
      await logout()
      return false
    }
  }

  function clearError(): void {
    error.value = null
  }

  function hasRole(role: string | string[]): boolean {
    if (!user.value) return false
    const roles = Array.isArray(role) ? role : [role]
    return roles.includes(user.value.role)
  }

  return {
    // State
    user,
    provider,
    isLoading,
    error,
    // Getters
    isAuthenticated,
    isProvider,
    isAdmin,
    isAdjudicator,
    isAuditor,
    fullName,
    userInitials,
    // Actions
    login,
    logout,
    checkAuth,
    refreshToken,
    clearError,
    hasRole,
  }
})
