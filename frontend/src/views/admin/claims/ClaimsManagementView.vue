<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUIStore } from '@/stores'
import Table from '@/components/ui/Table.vue'
import Badge from '@/components/ui/Badge.vue'
import Pagination from '@/components/ui/Pagination.vue'
import type { Column } from '@/components/ui/Table.vue'

const router = useRouter()
const uiStore = useUIStore()

interface Claim {
  id: string
  provider: string
  patient: string
  serviceDate: string
  amount: number
  status: string
}

const claims = ref<Claim[]>([
  { id: 'CLM-2024-001', provider: 'Dr. Smith', patient: 'John Doe', serviceDate: '2024-01-15', amount: 150.00, status: 'submitted' },
  { id: 'CLM-2024-002', provider: 'City Hospital', patient: 'Jane Roe', serviceDate: '2024-01-16', amount: 1200.50, status: 'in_review' },
  { id: 'CLM-2024-003', provider: 'Wellness Clinic', patient: 'Bob Smith', serviceDate: '2024-01-14', amount: 75.00, status: 'approved' },
  { id: 'CLM-2024-004', provider: 'Dr. Jones', patient: 'Alice Johnson', serviceDate: '2024-01-18', amount: 200.00, status: 'denied' },
])

const columns: Column<Claim>[] = [
  { key: 'id', label: 'Claim ID', sortable: true },
  { key: 'provider', label: 'Provider', sortable: true },
  { key: 'patient', label: 'Patient', sortable: true },
  { key: 'serviceDate', label: 'Service Date', sortable: true },
  { key: 'amount', label: 'Amount', sortable: true, align: 'right', render: (item) => `$${item.amount.toFixed(2)}` },
  { key: 'status', label: 'Status', sortable: true },
]

const page = ref(1)
const limit = ref(10)
const total = ref(100)

const handleRowClick = (claim: Claim) => {
  router.push({ name: 'admin-claim-detail', params: { id: claim.id } })
}

onMounted(() => {
  uiStore.setBreadcrumbs([
    { label: 'Admin', to: '/admin' },
    { label: 'Claims Management' }
  ])
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Claims Management</h1>
        <p class="mt-1 text-sm text-gray-500">View and manage all claims submitted to the system.</p>
      </div>
      <div class="flex gap-3">
        <!-- Filter controls could go here -->
      </div>
    </div>

    <div class="bg-white shadow rounded-lg overflow-hidden">
      <Table
        :columns="columns"
        :data="claims"
        :loading="false"
        @row-click="handleRowClick"
      >
        <template #cell-status="{ item }">
          <Badge :variant="item.status as any">{{ item.status }}</Badge>
        </template>
      </Table>
      
      <Pagination
        v-model:page="page"
        v-model:limit="limit"
        :total="total"
        :total-pages="Math.ceil(total / limit)"
      />
    </div>
  </div>
</template>
