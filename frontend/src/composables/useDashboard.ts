import { ref, computed, onMounted } from 'vue'
import type { DashboardStats, RecentActivity } from '@/types'
import { dashboardService } from '@/services/api'

export function useDashboard() {
  // State
  const stats = ref<DashboardStats | null>(null)
  const recentActivity = ref<RecentActivity[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const hasStats = computed(() => stats.value !== null)
  const hasActivity = computed(() => recentActivity.value.length > 0)

  // Format helpers
  const formattedTotalAmount = computed(() => {
    if (!stats.value) return '$0.00'
    return new Intl.NumberFormat('en-CA', {
      style: 'currency',
      currency: 'CAD',
    }).format(stats.value.totalAmount)
  })

  const averageProcessingTimeFormatted = computed(() => {
    if (!stats.value) return '0 hours'
    const hours = stats.value.averageProcessingTime
    if (hours < 1) return `${Math.round(hours * 60)} minutes`
    if (hours < 24) return `${hours.toFixed(1)} hours`
    return `${(hours / 24).toFixed(1)} days`
  })

  // Actions
  async function fetchStats(): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      const response = await dashboardService.getStats()
      stats.value = response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch dashboard stats'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchRecentActivity(limit = 10): Promise<void> {
    try {
      const response = await dashboardService.getRecentActivity(limit)
      recentActivity.value = response.data.data || response.data
    } catch (err: any) {
      console.error('Failed to fetch recent activity:', err)
    }
  }

  async function refresh(): Promise<void> {
    await Promise.all([
      fetchStats(),
      fetchRecentActivity(),
    ])
  }

  // Activity helpers
  function getActivityIcon(type: RecentActivity['type']): string {
    switch (type) {
      case 'claim_submitted':
        return 'DocumentPlusIcon'
      case 'claim_adjudicated':
        return 'CheckCircleIcon'
      case 'rule_updated':
        return 'CogIcon'
      case 'user_login':
        return 'UserIcon'
      default:
        return 'InformationCircleIcon'
    }
  }

  function getActivityColor(type: RecentActivity['type']): string {
    switch (type) {
      case 'claim_submitted':
        return 'text-blue-600 bg-blue-100'
      case 'claim_adjudicated':
        return 'text-green-600 bg-green-100'
      case 'rule_updated':
        return 'text-purple-600 bg-purple-100'
      case 'user_login':
        return 'text-gray-600 bg-gray-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  function formatTimestamp(timestamp: string): string {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.round(diffMs / 60000)
    const diffHours = Math.round(diffMs / 3600000)
    const diffDays = Math.round(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    
    return date.toLocaleDateString('en-CA', {
      month: 'short',
      day: 'numeric',
    })
  }

  onMounted(() => {
    refresh()
  })

  return {
    // State
    stats,
    recentActivity,
    isLoading,
    error,
    // Computed
    hasStats,
    hasActivity,
    formattedTotalAmount,
    averageProcessingTimeFormatted,
    // Actions
    fetchStats,
    fetchRecentActivity,
    refresh,
    // Helpers
    getActivityIcon,
    getActivityColor,
    formatTimestamp,
  }
}
