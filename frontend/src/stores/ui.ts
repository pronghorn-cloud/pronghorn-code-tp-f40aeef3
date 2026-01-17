import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface ModalConfig {
  id: string
  component?: string
  props?: Record<string, any>
  onClose?: () => void
  onConfirm?: () => void
}

export interface ToastConfig {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  message: string
  duration?: number
}

export const useUIStore = defineStore('ui', () => {
  // State
  const isSidebarOpen = ref(true)
  const isSidebarCollapsed = ref(false)
  const isMobileMenuOpen = ref(false)
  const activeModal = ref<ModalConfig | null>(null)
  const modalStack = ref<ModalConfig[]>([])
  const toasts = ref<ToastConfig[]>([])
  const isGlobalLoading = ref(false)
  const globalLoadingMessage = ref('')
  const theme = ref<'light' | 'dark'>('light')
  const breadcrumbs = ref<{ label: string; path?: string }[]>([])

  // Getters
  const hasActiveModal = computed(() => !!activeModal.value)
  const hasToasts = computed(() => toasts.value.length > 0)

  // Sidebar Actions
  function toggleSidebar(): void {
    isSidebarOpen.value = !isSidebarOpen.value
  }

  function collapseSidebar(): void {
    isSidebarCollapsed.value = true
  }

  function expandSidebar(): void {
    isSidebarCollapsed.value = false
  }

  function toggleSidebarCollapse(): void {
    isSidebarCollapsed.value = !isSidebarCollapsed.value
  }

  function openMobileMenu(): void {
    isMobileMenuOpen.value = true
  }

  function closeMobileMenu(): void {
    isMobileMenuOpen.value = false
  }

  // Modal Actions
  function openModal(config: ModalConfig): void {
    if (activeModal.value) {
      modalStack.value.push(activeModal.value)
    }
    activeModal.value = config
  }

  function closeModal(): void {
    if (activeModal.value?.onClose) {
      activeModal.value.onClose()
    }
    
    if (modalStack.value.length > 0) {
      activeModal.value = modalStack.value.pop() || null
    } else {
      activeModal.value = null
    }
  }

  function confirmModal(): void {
    if (activeModal.value?.onConfirm) {
      activeModal.value.onConfirm()
    }
    closeModal()
  }

  function closeAllModals(): void {
    modalStack.value = []
    activeModal.value = null
  }

  // Toast Actions
  function showToast(config: Omit<ToastConfig, 'id'>): void {
    const id = `toast-${Date.now()}`
    const toast: ToastConfig = {
      ...config,
      id,
      duration: config.duration || 5000,
    }
    toasts.value.push(toast)

    // Auto-remove after duration
    setTimeout(() => {
      removeToast(id)
    }, toast.duration)
  }

  function showSuccess(message: string): void {
    showToast({ type: 'success', message })
  }

  function showError(message: string): void {
    showToast({ type: 'error', message, duration: 7000 })
  }

  function showWarning(message: string): void {
    showToast({ type: 'warning', message })
  }

  function showInfo(message: string): void {
    showToast({ type: 'info', message })
  }

  function removeToast(id: string): void {
    const index = toasts.value.findIndex(t => t.id === id)
    if (index !== -1) {
      toasts.value.splice(index, 1)
    }
  }

  function clearAllToasts(): void {
    toasts.value = []
  }

  // Loading Actions
  function startLoading(message?: string): void {
    isGlobalLoading.value = true
    globalLoadingMessage.value = message || 'Loading...'
  }

  function stopLoading(): void {
    isGlobalLoading.value = false
    globalLoadingMessage.value = ''
  }

  // Theme Actions
  function setTheme(newTheme: 'light' | 'dark'): void {
    theme.value = newTheme
    localStorage.setItem('theme', newTheme)
    document.documentElement.classList.toggle('dark', newTheme === 'dark')
  }

  function toggleTheme(): void {
    setTheme(theme.value === 'light' ? 'dark' : 'light')
  }

  function initTheme(): void {
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | null
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    setTheme(savedTheme || (prefersDark ? 'dark' : 'light'))
  }

  // Breadcrumbs Actions
  function setBreadcrumbs(items: { label: string; path?: string }[]): void {
    breadcrumbs.value = items
  }

  function clearBreadcrumbs(): void {
    breadcrumbs.value = []
  }

  return {
    // State
    isSidebarOpen,
    isSidebarCollapsed,
    isMobileMenuOpen,
    activeModal,
    modalStack,
    toasts,
    isGlobalLoading,
    globalLoadingMessage,
    theme,
    breadcrumbs,
    // Getters
    hasActiveModal,
    hasToasts,
    // Sidebar Actions
    toggleSidebar,
    collapseSidebar,
    expandSidebar,
    toggleSidebarCollapse,
    openMobileMenu,
    closeMobileMenu,
    // Modal Actions
    openModal,
    closeModal,
    confirmModal,
    closeAllModals,
    // Toast Actions
    showToast,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    removeToast,
    clearAllToasts,
    // Loading Actions
    startLoading,
    stopLoading,
    // Theme Actions
    setTheme,
    toggleTheme,
    initTheme,
    // Breadcrumbs Actions
    setBreadcrumbs,
    clearBreadcrumbs,
  }
})
