<script setup lang="ts">
import { onMounted } from 'vue'
import { useUIStore } from '@/stores'
import { Card, Button } from '@/components/ui'
import { ChartBarIcon, DocumentTextIcon, BanknotesIcon } from '@heroicons/vue/24/outline'

const uiStore = useUIStore()

const reports = [
  { 
    title: 'Claims Summary', 
    description: 'Daily breakdown of submitted, approved, and denied claims.', 
    icon: DocumentTextIcon,
    lastRun: 'Today, 08:00 AM'
  },
  { 
    title: 'Financial Reconciliation', 
    description: 'Total payments processed and outstanding balances.', 
    icon: BanknotesIcon,
    lastRun: 'Yesterday, 11:59 PM'
  },
  { 
    title: 'Provider Performance', 
    description: 'Analysis of submission volume and rejection rates by provider.', 
    icon: ChartBarIcon,
    lastRun: '2024-01-15'
  },
]

onMounted(() => {
  uiStore.setBreadcrumbs([{ label: 'Admin', to: '/admin' }, { label: 'Reports' }])
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">System Reports</h1>
        <p class="mt-1 text-sm text-gray-500">Generate and view analytical reports</p>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <Card v-for="report in reports" :key="report.title" class="hover:shadow-md transition-shadow">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <div class="p-2 bg-primary-50 rounded-lg">
              <component :is="report.icon" class="h-6 w-6 text-primary-600" />
            </div>
            <span class="text-xs text-gray-500">Last run: {{ report.lastRun }}</span>
          </div>
          <h3 class="text-lg font-medium text-gray-900 mb-2">{{ report.title }}</h3>
          <p class="text-sm text-gray-500 mb-6">{{ report.description }}</p>
          <Button class="w-full" variant="outline">Generate Report</Button>
        </div>
      </Card>
    </div>
  </div>
</template>
