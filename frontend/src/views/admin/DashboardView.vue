<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { Card, Badge, Button } from '@/components/ui'
import { useUIStore } from '@/stores'
import {
  DocumentTextIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  FlagIcon,
  UserGroupIcon,
  ChartBarIcon,
  CogIcon,
  DocumentPlusIcon,
  ClipboardDocumentListIcon,
  ShieldCheckIcon,
  ArrowRightIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
} from '@heroicons/vue/24/outline'

const uiStore = useUIStore()

// Dashboard statistics
const stats = ref({
  totalClaims: 1247,
  pendingClaims: 89,
  flaggedClaims: 23,
  approvedToday: 45,
  deniedToday: 8,
  processingRate: 94.2,
  avgProcessingTime: '2.4 hours',
  totalProviders: 156,
})

// Trends (positive = good)
const trends = ref({
  pendingClaims: -12, // 12% decrease is good
  flaggedClaims: -5,
  processingRate: 3.2,
  avgProcessingTime: -8, // faster is better
})

// Recent activity feed
const recentActivity = ref([
  {
    id: 1,
    type: 'claim_submitted',
    message: 'New claim submitted by Dr. Smith Clinic',
    claimId: 'CLM-2026-001247',
    timestamp: '2 minutes ago',
    icon: DocumentPlusIcon,
    iconClass: 'text-blue-500 bg-blue-100',
  },
  {
    id: 2,
    type: 'claim_approved',
    message: 'Claim approved automatically',
    claimId: 'CLM-2026-001243',
    timestamp: '5 minutes ago',
    icon: CheckCircleIcon,
    iconClass: 'text-green-500 bg-green-100',
  },
  {
    id: 3,
    type: 'claim_flagged',
    message: 'Claim flagged for manual review',
    claimId: 'CLM-2026-001241',
    timestamp: '12 minutes ago',
    icon: FlagIcon,
    iconClass: 'text-yellow-500 bg-yellow-100',
  },
  {
    id: 4,
    type: 'rule_updated',
    message: 'Adjudication rule "Max Daily Visits" updated',
    timestamp: '25 minutes ago',
    icon: CogIcon,
    iconClass: 'text-purple-500 bg-purple-100',
  },
  {
    id: 5,
    type: 'claim_denied',
    message: 'Claim denied - Invalid procedure code',
    claimId: 'CLM-2026-001238',
    timestamp: '32 minutes ago',
    icon: XCircleIcon,
    iconClass: 'text-red-500 bg-red-100',
  },
])

// Flagged claims queue (preview)
const flaggedClaimsQueue = ref([
  {
    id: 'CLM-2026-001241',
    provider: 'Metro Health Services',
    amount: 2450.00,
    reason: 'Amount exceeds daily limit',
    flaggedAt: '12 minutes ago',
    priority: 'high',
  },
  {
    id: 'CLM-2026-001235',
    provider: 'City Medical Center',
    amount: 890.00,
    reason: 'Duplicate service code detected',
    flaggedAt: '45 minutes ago',
    priority: 'medium',
  },
  {
    id: 'CLM-2026-001229',
    provider: 'Family Care Clinic',
    amount: 1200.00,
    reason: 'Patient eligibility verification required',
    flaggedAt: '1 hour ago',
    priority: 'medium',
  },
  {
    id: 'CLM-2026-001221',
    provider: 'Wellness Medical Group',
    amount: 3100.00,
    reason: 'Procedure requires prior authorization',
    flaggedAt: '2 hours ago',
    priority: 'low',
  },
])

// Quick actions
const quickActions = [
  {
    label: 'Review Flagged Claims',
    description: 'Process claims requiring manual review',
    icon: FlagIcon,
    to: '/admin/claims/flagged',
    color: 'bg-yellow-500',
    count: 23,
  },
  {
    label: 'Manage Rules',
    description: 'Configure adjudication rules',
    icon: CogIcon,
    to: '/admin/rules',
    color: 'bg-purple-500',
  },
  {
    label: 'View Audit Logs',
    description: 'Review compliance and audit trail',
    icon: ShieldCheckIcon,
    to: '/admin/audit',
    color: 'bg-blue-500',
  },
  {
    label: 'Generate Reports',
    description: 'Create analytics and compliance reports',
    icon: ChartBarIcon,
    to: '/admin/reports',
    color: 'bg-green-500',
  },
]

const isLoading = ref(false)

// Format currency
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-CA', {
    style: 'currency',
    currency: 'CAD',
  }).format(amount)
}

// Get priority badge variant
const getPriorityVariant = (priority: string) => {
  switch (priority) {
    case 'high':
      return 'danger'
    case 'medium':
      return 'warning'
    case 'low':
      return 'info'
    default:
      return 'secondary'
  }
}

// Fetch dashboard data
const fetchDashboardData = async () => {
  isLoading.value = true
  try {
    // TODO: Replace with actual API calls
    // const response = await adminService.getDashboardStats()
    // stats.value = response.data
    await new Promise(resolve => setTimeout(resolve, 500)) // Simulate API call
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  uiStore.setBreadcrumbs([{ label: 'Admin Dashboard' }])
  fetchDashboardData()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
        <p class="mt-1 text-sm text-gray-500">
          Overview of claims processing and system status
        </p>
      </div>
      <div class="flex items-center space-x-3">
        <span class="text-sm text-gray-500">Last updated: Just now</span>
        <Button
          variant="outline"
          size="sm"
          :loading="isLoading"
          @click="fetchDashboardData"
        >
          Refresh
        </Button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
      <!-- Total Claims -->
      <Card class="overflow-hidden">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="p-3 bg-blue-100 rounded-lg">
                <DocumentTextIcon class="w-6 h-6 text-blue-600" />
              </div>
            </div>
            <div class="flex-1 w-0 ml-5">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">
                  Total Claims
                </dt>
                <dd class="flex items-baseline">
                  <span class="text-2xl font-semibold text-gray-900">
                    {{ stats.totalClaims.toLocaleString() }}
                  </span>
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </Card>

      <!-- Pending Claims -->
      <Card class="overflow-hidden">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="p-3 bg-yellow-100 rounded-lg">
                <ClockIcon class="w-6 h-6 text-yellow-600" />
              </div>
            </div>
            <div class="flex-1 w-0 ml-5">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">
                  Pending Review
                </dt>
                <dd class="flex items-baseline">
                  <span class="text-2xl font-semibold text-gray-900">
                    {{ stats.pendingClaims }}
                  </span>
                  <span
                    v-if="trends.pendingClaims"
                    :class="[
                      'ml-2 flex items-baseline text-sm font-semibold',
                      trends.pendingClaims < 0 ? 'text-green-600' : 'text-red-600'
                    ]"
                  >
                    <component
                      :is="trends.pendingClaims < 0 ? ArrowTrendingDownIcon : ArrowTrendingUpIcon"
                      class="w-4 h-4 mr-0.5"
                    />
                    {{ Math.abs(trends.pendingClaims) }}%
                  </span>
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </Card>

      <!-- Flagged Claims -->
      <Card class="overflow-hidden">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="p-3 bg-red-100 rounded-lg">
                <FlagIcon class="w-6 h-6 text-red-600" />
              </div>
            </div>
            <div class="flex-1 w-0 ml-5">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">
                  Flagged Claims
                </dt>
                <dd class="flex items-baseline">
                  <span class="text-2xl font-semibold text-gray-900">
                    {{ stats.flaggedClaims }}
                  </span>
                  <span
                    v-if="trends.flaggedClaims"
                    :class="[
                      'ml-2 flex items-baseline text-sm font-semibold',
                      trends.flaggedClaims < 0 ? 'text-green-600' : 'text-red-600'
                    ]"
                  >
                    <component
                      :is="trends.flaggedClaims < 0 ? ArrowTrendingDownIcon : ArrowTrendingUpIcon"
                      class="w-4 h-4 mr-0.5"
                    />
                    {{ Math.abs(trends.flaggedClaims) }}%
                  </span>
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </Card>

      <!-- Processing Rate -->
      <Card class="overflow-hidden">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="p-3 bg-green-100 rounded-lg">
                <ChartBarIcon class="w-6 h-6 text-green-600" />
              </div>
            </div>
            <div class="flex-1 w-0 ml-5">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">
                  Auto-Approval Rate
                </dt>
                <dd class="flex items-baseline">
                  <span class="text-2xl font-semibold text-gray-900">
                    {{ stats.processingRate }}%
                  </span>
                  <span
                    v-if="trends.processingRate"
                    :class="[
                      'ml-2 flex items-baseline text-sm font-semibold',
                      trends.processingRate > 0 ? 'text-green-600' : 'text-red-600'
                    ]"
                  >
                    <component
                      :is="trends.processingRate > 0 ? ArrowTrendingUpIcon : ArrowTrendingDownIcon"
                      class="w-4 h-4 mr-0.5"
                    />
                    {{ Math.abs(trends.processingRate) }}%
                  </span>
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </Card>
    </div>

    <!-- Secondary Stats Row -->
    <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
      <Card class="p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-500">Approved Today</p>
            <p class="text-xl font-semibold text-green-600">{{ stats.approvedToday }}</p>
          </div>
          <CheckCircleIcon class="w-8 h-8 text-green-500" />
        </div>
      </Card>
      <Card class="p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-500">Denied Today</p>
            <p class="text-xl font-semibold text-red-600">{{ stats.deniedToday }}</p>
          </div>
          <XCircleIcon class="w-8 h-8 text-red-500" />
        </div>
      </Card>
      <Card class="p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-500">Avg Processing Time</p>
            <p class="text-xl font-semibold text-gray-900">{{ stats.avgProcessingTime }}</p>
          </div>
          <ClockIcon class="w-8 h-8 text-blue-500" />
        </div>
      </Card>
      <Card class="p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-500">Active Providers</p>
            <p class="text-xl font-semibold text-gray-900">{{ stats.totalProviders }}</p>
          </div>
          <UserGroupIcon class="w-8 h-8 text-purple-500" />
        </div>
      </Card>
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
      <!-- Quick Actions -->
      <Card class="lg:col-span-1">
        <div class="p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div class="space-y-3">
            <RouterLink
              v-for="action in quickActions"
              :key="action.label"
              :to="action.to"
              class="flex items-center p-3 rounded-lg hover:bg-gray-50 transition-colors group"
            >
              <div :class="[action.color, 'p-2 rounded-lg']">
                <component :is="action.icon" class="w-5 h-5 text-white" />
              </div>
              <div class="ml-3 flex-1">
                <div class="flex items-center justify-between">
                  <p class="text-sm font-medium text-gray-900 group-hover:text-blue-600">
                    {{ action.label }}
                  </p>
                  <Badge v-if="action.count" variant="danger" size="sm">
                    {{ action.count }}
                  </Badge>
                </div>
                <p class="text-xs text-gray-500">{{ action.description }}</p>
              </div>
              <ArrowRightIcon class="w-4 h-4 text-gray-400 group-hover:text-blue-600 ml-2" />
            </RouterLink>
          </div>
        </div>
      </Card>

      <!-- Flagged Claims Queue -->
      <Card class="lg:col-span-2">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold text-gray-900">Flagged Claims Queue</h2>
            <RouterLink
              to="/admin/claims/flagged"
              class="text-sm font-medium text-blue-600 hover:text-blue-500"
            >
              View All →
            </RouterLink>
          </div>
          <div class="overflow-hidden">
            <table class="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Claim ID
                  </th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Provider
                  </th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Amount
                  </th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Reason
                  </th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Priority
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr
                  v-for="claim in flaggedClaimsQueue"
                  :key="claim.id"
                  class="hover:bg-gray-50 cursor-pointer"
                >
                  <td class="px-3 py-3 whitespace-nowrap">
                    <RouterLink
                      :to="`/admin/claims/${claim.id}`"
                      class="text-sm font-medium text-blue-600 hover:text-blue-500"
                    >
                      {{ claim.id }}
                    </RouterLink>
                  </td>
                  <td class="px-3 py-3 whitespace-nowrap text-sm text-gray-900">
                    {{ claim.provider }}
                  </td>
                  <td class="px-3 py-3 whitespace-nowrap text-sm text-gray-900">
                    {{ formatCurrency(claim.amount) }}
                  </td>
                  <td class="px-3 py-3 text-sm text-gray-500 max-w-xs truncate">
                    {{ claim.reason }}
                  </td>
                  <td class="px-3 py-3 whitespace-nowrap">
                    <Badge :variant="getPriorityVariant(claim.priority)" size="sm">
                      {{ claim.priority }}
                    </Badge>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </Card>
    </div>

    <!-- Recent Activity Feed -->
    <Card>
      <div class="p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-gray-900">Recent Activity</h2>
          <RouterLink
            to="/admin/audit"
            class="text-sm font-medium text-blue-600 hover:text-blue-500"
          >
            View All Activity →
          </RouterLink>
        </div>
        <div class="flow-root">
          <ul class="-mb-8">
            <li v-for="(activity, index) in recentActivity" :key="activity.id">
              <div class="relative pb-8">
                <!-- Connecting line -->
                <span
                  v-if="index !== recentActivity.length - 1"
                  class="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"
                  aria-hidden="true"
                />
                <div class="relative flex space-x-3">
                  <div>
                    <span
                      :class="[
                        activity.iconClass,
                        'h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white'
                      ]"
                    >
                      <component :is="activity.icon" class="w-4 h-4" />
                    </span>
                  </div>
                  <div class="flex-1 min-w-0 pt-1.5 flex justify-between space-x-4">
                    <div>
                      <p class="text-sm text-gray-900">
                        {{ activity.message }}
                        <RouterLink
                          v-if="activity.claimId"
                          :to="`/admin/claims/${activity.claimId}`"
                          class="font-medium text-blue-600 hover:text-blue-500 ml-1"
                        >
                          {{ activity.claimId }}
                        </RouterLink>
                      </p>
                    </div>
                    <div class="text-right text-sm whitespace-nowrap text-gray-500">
                      {{ activity.timestamp }}
                    </div>
                  </div>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </Card>
  </div>
</template>
