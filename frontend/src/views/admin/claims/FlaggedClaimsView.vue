<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Card, Button, Table, Badge, Pagination } from '@/components/ui'
import { useUIStore } from '@/stores'
import { RouterLink } from 'vue-router'

const uiStore = useUIStore()

const flaggedClaims = ref([
  { id: 'CLM-2026-001241', provider: 'Metro Health Services', amount: 2450.00, reason: 'Amount exceeds daily limit', priority: 'high', date: '2026-01-15' },
  { id: 'CLM-2026-001235', provider: 'City Medical Center', amount: 890.00, reason: 'Duplicate service code', priority: 'medium', date: '2026-01-15' },
  { id: 'CLM-2026-001229', provider: 'Family Care Clinic', amount: 1200.00, reason: 'Eligibility verification', priority: 'medium', date: '2026-01-14' },
])

const columns = [
  { key: 'id', label: 'Claim ID', sortable: true },
  { key: 'provider', label: 'Provider', sortable: true },
  { key: 'amount', label: 'Amount', sortable: true, align: 'right', render: (row: any) => `$${row.amount.toFixed(2)}` },
  { key: 'reason', label: 'Flag Reason' },
  { key: 'priority', label: 'Priority', sortable: true },
  { key: 'date', label: 'Date', sortable: true },
]

const getPriorityVariant = (priority: string) => {
  switch (priority) {
    case 'high': return 'danger'
    case 'medium': return 'warning'
    default: return 'info'
  }
}

onMounted(() => {
  uiStore.setBreadcrumbs([{ label: 'Admin', to: '/admin' }, { label: 'Claims', to: '/admin/claims' }, { label: 'Flagged Claims' }])
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Flagged Claims</h1>
        <p class="mt-1 text-sm text-gray-500">Claims requiring manual review and adjudication</p>
      </div>
    </div>

    <Card>
      <Table :columns="columns" :data="flaggedClaims" @row-click="(row) => $router.push(`/admin/claims/${row.id}`)">
        <template #cell-id="{ value }">
          <span class="text-primary-600 font-medium">{{ value }}</span>
        </template>
        <template #cell-priority="{ value }">
          <Badge :variant="getPriorityVariant(value)">{{ value }}</Badge>
        </template>
        <template #actions="{ item }">
          <Button size="sm" variant="outline" @click.stop="$router.push(`/admin/claims/${item.id}`)">Review</Button>
        </template>
      </Table>
      <div class="p-4 border-t border-gray-200">
        <Pagination :current-page="1" :total-pages="1" />
      </div>
    </Card>
  </div>
</template>