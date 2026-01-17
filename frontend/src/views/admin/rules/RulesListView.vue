<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUIStore } from '@/stores'
import { Card, Button, Table, Badge, Pagination, Input } from '@/components/ui'
import { PlusIcon, MagnifyingGlassIcon, PlayIcon } from '@heroicons/vue/24/outline'

const router = useRouter()
const uiStore = useUIStore()
const searchQuery = ref('')

const rules = ref([
  { id: 'RULE-001', name: 'Check Duplicate Service', description: 'Flag claims with same service code on same day', type: 'Validation', status: 'active', lastModified: '2024-01-15' },
  { id: 'RULE-002', name: 'Verify Age Limit', description: 'Ensure patient age is appropriate for service code', type: 'Eligibility', status: 'active', lastModified: '2024-01-10' },
  { id: 'RULE-003', name: 'Gender Specific Services', description: 'Validate service codes against patient gender', type: 'Validation', status: 'inactive', lastModified: '2023-12-20' },
])

const columns = [
  { key: 'name', label: 'Rule Name', sortable: true },
  { key: 'description', label: 'Description' },
  { key: 'type', label: 'Type', sortable: true },
  { key: 'status', label: 'Status', sortable: true },
  { key: 'lastModified', label: 'Last Modified', sortable: true },
]

onMounted(() => {
  uiStore.setBreadcrumbs([{ label: 'Admin', to: '/admin' }, { label: 'Rules Engine' }])
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Rules Management</h1>
        <p class="mt-1 text-sm text-gray-500">Configure and manage adjudication rules</p>
      </div>
      <div class="flex gap-3">
        <Button variant="secondary" @click="router.push('/admin/rules/testing')">
          <PlayIcon class="h-5 w-5 mr-2" />
          Test Rules
        </Button>
        <Button @click="router.push('/admin/rules/new')">
          <PlusIcon class="h-5 w-5 mr-2" />
          New Rule
        </Button>
      </div>
    </div>

    <Card>
      <div class="p-4 border-b border-gray-200 flex justify-between items-center">
        <div class="relative w-64">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MagnifyingGlassIcon class="h-5 w-5 text-gray-400" />
          </div>
          <Input v-model="searchQuery" placeholder="Search rules..." class="pl-10" />
        </div>
      </div>

      <Table :columns="columns" :data="rules" @row-click="(row) => router.push(`/admin/rules/${row.id}`)">
        <template #cell-name="{ item }">
          <div>
            <div class="font-medium text-gray-900">{{ item.name }}</div>
            <div class="text-xs text-gray-500">{{ item.id }}</div>
          </div>
        </template>
        <template #cell-status="{ value }">
          <Badge :variant="value === 'active' ? 'success' : 'secondary'">{{ value }}</Badge>
        </template>
        <template #actions="{ item }">
          <Button size="sm" variant="outline" @click.stop="router.push(`/admin/rules/${item.id}`)">Edit</Button>
        </template>
      </Table>
      
      <div class="p-4 border-t border-gray-200">
        <Pagination :current-page="1" :total-pages="1" :total="3" :limit="10" />
      </div>
    </Card>
  </div>
</template>
