<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useClaimsStore, useUIStore } from '@/stores'
import { usePagination } from '@/composables'
import { Card, Badge, Button, Table, Pagination } from '@/components/ui'
import type { Claim, ClaimStatus } from '@/types'
import {
  PlusIcon,
  FunnelIcon,
  MagnifyingGlassIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
} from '@heroicons/vue/24/outline'

const claimsStore = useClaimsStore()
const uiStore = useUIStore()

const searchQuery = ref('')
const statusFilter = ref<ClaimStatus | ''>()
const showFilters = ref(false)

const { page, limit, total, totalPages, setPage, setLimit, setTotal } = usePagination({
  initialLimit: 20,
})

const columns = [
  { key: 'id', label: 'Claim ID', width: '120px' },
  { key: 'patient', label: 'Patient', sortable: true },
  { key: 'serviceDate', label: 'Service Date', sortable: true },
  { key: 'status', label: 'Status' },
  { key: 'totalAmount', label: 'Amount', align: 'right' as const, sortable: true },
  { key: 'createdAt', label: 'Created', sortable: true },
]

const statusOptions = [
  { value: '', label: 'All Statuses' },
  { value: 'draft', label: 'Draft' },
  { value: 'submitted', label: 'Submitted' },
  { value: 'in_review', label: 'In Review' },
  { value: 'approved', label: 'Approved' },
  { value: 'denied', label: 'Denied' },
  { value: 'paid', label: 'Paid' },
]

onMounted(async () => {
  uiStore.setBreadcrumbs([
    { label: 'Dashboard', path: '/' },
    { label: 'Claims' },
  ])
  await fetchClaims()
})

async function fetchClaims() {
  await claimsStore.fetchClaims({
    page: page.value,
    limit: limit.value,
    status: statusFilter.value || undefined,
    search: searchQuery.value || undefined,
  })
  setTotal(claimsStore.pagination.total)
}

function handleSearch() {
  setPage(1)
  fetchClaims()
}

function handleStatusChange() {
  setPage(1)
  fetchClaims()
}

function handlePageChange(newPage: number) {
  setPage(newPage)
  fetchClaims()
}

function handleLimitChange(newLimit: number) {
  setLimit(newLimit)
  fetchClaims()
}

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

const getPatientName = (claim: Claim) => {
  return `${claim.patientInfo.firstName} ${claim.patientInfo.lastName}`
}

const canEdit = (claim: Claim) => claim.status === 'draft'
const canDelete = (claim: Claim) => claim.status === 'draft'

async function handleDelete(claim: Claim) {
  if (confirm('Are you sure you want to delete this claim?')) {
    await claimsStore.deleteClaim(claim.id)
    uiStore.showSuccess('Claim deleted successfully')
  }
}
</script>

<template>
  <div>
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Claims</h1>
        <p class="mt-1 text-sm text-gray-600">Manage and track your healthcare claims</p>
      </div>
      <RouterLink to="/claims/new">
        <Button variant="primary">
          <PlusIcon class="h-5 w-5 mr-2" />
          New Claim
        </Button>
      </RouterLink>
    </div>

    <!-- Filters -->
    <Card padding="md" class="mb-6">
      <div class="flex flex-col sm:flex-row gap-4">
        <!-- Search -->
        <div class="flex-1">
          <div class="relative">
            <MagnifyingGlassIcon class="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search by patient name or claim ID..."
              class="form-input pl-10 w-full"
              @keyup.enter="handleSearch"
            />
          </div>
        </div>

        <!-- Status filter -->
        <div class="w-full sm:w-48">
          <select
            v-model="statusFilter"
            class="form-select w-full"
            @change="handleStatusChange"
          >
            <option v-for="opt in statusOptions" :key="opt.value" :value="opt.value">
              {{ opt.label }}
            </option>
          </select>
        </div>

        <!-- Search button -->
        <Button variant="secondary" @click="handleSearch">
          <FunnelIcon class="h-5 w-5 mr-2" />
          Filter
        </Button>
      </div>
    </Card>

    <!-- Claims Table -->
    <Card padding="none">
      <Table
        :columns="columns"
        :data="claimsStore.claims"
        :loading="claimsStore.isLoading"
        :sort-by="claimsStore.filters.sortBy"
        :sort-order="claimsStore.filters.sortOrder"
        empty-message="No claims found"
        @sort="(key, order) => claimsStore.setFilters({ sortBy: key as any, sortOrder: order })"
      >
        <!-- Claim ID -->
        <template #cell-id="{ item }">
          <RouterLink
            :to="`/claims/${item.id}`"
            class="text-primary-600 hover:text-primary-700 font-medium"
          >
            #{{ item.id.slice(0, 8) }}
          </RouterLink>
        </template>

        <!-- Patient -->
        <template #cell-patient="{ item }">
          <div>
            <p class="font-medium text-gray-900">{{ getPatientName(item) }}</p>
            <p class="text-xs text-gray-500">{{ item.patientInfo.healthCardNumber }}</p>
          </div>
        </template>

        <!-- Service Date -->
        <template #cell-serviceDate="{ item }">
          {{ item.serviceLines[0]?.serviceDate ? formatDate(item.serviceLines[0].serviceDate) : '-' }}
        </template>

        <!-- Status -->
        <template #cell-status="{ item }">
          <Badge :variant="item.status" dot />
        </template>

        <!-- Amount -->
        <template #cell-totalAmount="{ item }">
          <span class="font-medium">{{ formatCurrency(item.totalAmount) }}</span>
        </template>

        <!-- Created -->
        <template #cell-createdAt="{ item }">
          {{ formatDate(item.createdAt) }}
        </template>

        <!-- Actions -->
        <template #actions="{ item }">
          <div class="flex items-center justify-end gap-2">
            <RouterLink :to="`/claims/${item.id}`">
              <Button variant="ghost" size="sm">
                <EyeIcon class="h-4 w-4" />
              </Button>
            </RouterLink>
            <RouterLink v-if="canEdit(item)" :to="`/claims/${item.id}/edit`">
              <Button variant="ghost" size="sm">
                <PencilIcon class="h-4 w-4" />
              </Button>
            </RouterLink>
            <Button
              v-if="canDelete(item)"
              variant="ghost"
              size="sm"
              @click="handleDelete(item)"
            >
              <TrashIcon class="h-4 w-4 text-danger-500" />
            </Button>
          </div>
        </template>

        <!-- Empty state -->
        <template #empty>
          <div class="text-center py-12">
            <DocumentTextIcon class="h-12 w-12 text-gray-400 mx-auto" />
            <h3 class="mt-2 text-sm font-medium text-gray-900">No claims found</h3>
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
        </template>
      </Table>

      <!-- Pagination -->
      <Pagination
        v-if="claimsStore.claims.length > 0"
        :page="page"
        :total-pages="totalPages"
        :total="total"
        :limit="limit"
        @update:page="handlePageChange"
        @update:limit="handleLimitChange"
      />
    </Card>
  </div>
</template>

<script lang="ts">
import { DocumentTextIcon } from '@heroicons/vue/24/outline'
export default {
  components: { DocumentTextIcon }
}
</script>
