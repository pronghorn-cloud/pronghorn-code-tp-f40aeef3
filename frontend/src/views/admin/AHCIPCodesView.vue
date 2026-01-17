<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Card, Button, Input, Table, Badge, Pagination } from '@/components/ui'
import { useUIStore } from '@/stores'
import { MagnifyingGlassIcon } from '@heroicons/vue/24/outline'

const uiStore = useUIStore()
const searchQuery = ref('')

const codes = ref([
  { code: '03.03A', description: 'Limited Assessment', category: 'Visit', fee: 45.00, active: true },
  { code: '03.04A', description: 'Comprehensive Assessment', category: 'Visit', fee: 95.00, active: true },
  { code: '13.59A', description: 'Intramuscular Injection', category: 'Procedure', fee: 15.50, active: true },
])

const columns = [
  { key: 'code', label: 'Code', sortable: true },
  { key: 'description', label: 'Description', sortable: true },
  { key: 'category', label: 'Category', sortable: true },
  { key: 'fee', label: 'Fee', sortable: true, align: 'right', render: (row: any) => `$${row.fee.toFixed(2)}` },
  { key: 'active', label: 'Status', sortable: true },
]

onMounted(() => {
  uiStore.setBreadcrumbs([{ label: 'Admin', to: '/admin' }, { label: 'AHCIP Codes' }])
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-900">AHCIP Codes</h1>
      <Button>Import Codes</Button>
    </div>

    <Card>
      <div class="p-4 border-b border-gray-200 flex justify-between items-center">
        <div class="relative w-64">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MagnifyingGlassIcon class="h-5 w-5 text-gray-400" />
          </div>
          <Input v-model="searchQuery" placeholder="Search codes..." class="pl-10" />
        </div>
      </div>
      
      <Table :columns="columns" :data="codes">
        <template #cell-active="{ value }">
          <Badge :variant="value ? 'success' : 'secondary'">{{ value ? 'Active' : 'Inactive' }}</Badge>
        </template>
        <template #actions>
          <button class="text-blue-600 hover:text-blue-900 text-sm font-medium">Edit</button>
        </template>
      </Table>
      <div class="p-4 border-t border-gray-200">
        <Pagination :current-page="1" :total-pages="5" />
      </div>
    </Card>
  </div>
</template>