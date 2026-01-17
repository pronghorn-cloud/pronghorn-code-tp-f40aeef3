<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useClaimsStore, useUIStore } from '@/stores'
import { Card, Badge, Button } from '@/components/ui'
import {
  DocumentTextIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  PlusIcon,
  ArrowRightIcon,
} from '@heroicons/vue/24/outline'

const claimsStore = useClaimsStore()
const uiStore = useUIStore()

onMounted(() => {
  uiStore.setBreadcrumbs([{ label: 'Dashboard' }])
  claimsStore.fetchClaims({ limit: 5 })
})

const stats = [
  {
    name: 'Total Claims',
    value: '24',
    icon: DocumentTextIcon,
    color: 'bg-blue-500',
  },
  {
    name: 'Pending Review',
    value: '3',
    icon: ClockIcon,
    color: 'bg-yellow-500',
  },
  {
    name: 'Approved',
    value: '18',
    icon: CheckCircleIcon,
    color: 'bg-green-500',
  },
  {
    name: 'Denied',
    value: '3',
    icon: XCircleIcon,
    color: 'bg-red-500',
  },
]

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-CA', {
    style: 'currency',
    currency: 'CAD',
  }).format(amount)
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('en-CA', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}
</script>

<template>
  <div>
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p class="mt-1 text-sm text-gray-600">Welcome back! Here's an overview of your claims.</p>
      </div>
      <RouterLink to="/claims/new">
        <Button variant="primary">
          <PlusIcon class="h-5 w-5 mr-2" />
          New Claim
        </Button>
      </RouterLink>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
      <Card v-for="stat in stats" :key="stat.name" padding="md">
        <div class="flex items-center">
          <div :class="[stat.color, 'p-3 rounded-lg']">
            <component :is="stat.icon" class="h-6 w-6 text-white" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">{{ stat.name }}</p>
            <p class="text-2xl font-semibold text-gray-900">{{ stat.value }}</p>
          </div>
        </div>
      </Card>
    </div>

    <!-- Recent Claims -->
    <Card padding="none">
      <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <h2 class="text-lg font-semibold text-gray-900">Recent Claims</h2>
        <RouterLink
          to="/claims"
          class="text-sm font-medium text-primary-600 hover:text-primary-500 flex items-center"
        >
          View all
          <ArrowRightIcon class="h-4 w-4 ml-1" />
        </RouterLink>
      </div>

      <div v-if="claimsStore.isLoading" class="p-12 text-center">
        <div class="animate-spin h-8 w-8 border-4 border-primary-600 border-t-transparent rounded-full mx-auto"></div>
        <p class="mt-2 text-sm text-gray-500">Loading claims...</p>
      </div>

      <div v-else-if="claimsStore.claims.length === 0" class="p-12 text-center">
        <DocumentTextIcon class="h-12 w-12 text-gray-400 mx-auto" />
        <h3 class="mt-2 text-sm font-medium text-gray-900">No claims yet</h3>
        <p class="mt-1 text-sm text-gray-500">Get started by creating a new claim.</p>
        <div class="mt-6">
          <RouterLink to="/claims/new">
            <Button variant="primary">
              <PlusIcon class="h-5 w-5 mr-2" />
              New Claim
            </Button>
          </RouterLink>
        </div>
      </div>

      <ul v-else class="divide-y divide-gray-200">
        <li
          v-for="claim in claimsStore.claims.slice(0, 5)"
          :key="claim.id"
          class="px-6 py-4 hover:bg-gray-50 transition-colors"
        >
          <RouterLink :to="`/claims/${claim.id}`" class="flex items-center justify-between">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-3">
                <p class="text-sm font-medium text-gray-900 truncate">
                  {{ claim.patientInfo.firstName }} {{ claim.patientInfo.lastName }}
                </p>
                <Badge :variant="claim.status" size="sm" />
              </div>
              <p class="mt-1 text-sm text-gray-500">
                {{ claim.serviceLines.length }} service(s) • Submitted {{ formatDate(claim.createdAt) }}
              </p>
            </div>
            <div class="text-right">
              <p class="text-sm font-medium text-gray-900">
                {{ formatCurrency(claim.totalAmount) }}
              </p>
              <p class="text-xs text-gray-500">
                #{{ claim.id.slice(0, 8) }}
              </p>
            </div>
          </RouterLink>
        </li>
      </ul>
    </Card>
  </div>
</template>
