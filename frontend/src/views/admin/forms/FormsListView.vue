<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUIStore } from '@/stores'
import { Card, Button, Table, Badge, Pagination, Input } from '@/components/ui'
import { PlusIcon, MagnifyingGlassIcon } from '@heroicons/vue/24/outline'

const router = useRouter()
const uiStore = useUIStore()
const searchQuery = ref('')

const forms = ref([
  { id: 'FRM-001', name: 'General Service Claim', version: '2.1', status: 'published', lastModified: '2024-01-15' },
  { id: 'FRM-002', name: 'Extended Health Benefit', version: '1.0', status: 'draft', lastModified: '2024-01-18' },
  { id: 'FRM-003', name: 'Dental Claim Form', version: '3.0', status: 'published', lastModified: '2023-11-20' },
])

const columns = [
  { key: 'name', label: 'Form Name', sortable: true },
  { key: 'version', label: 'Version' },
  { key: 'status', label: 'Status', sortable: true },
  { key: 'lastModified', label: 'Last Modified', sortable: true },
]

onMounted(() => {
  uiStore.setBreadcrumbs([{ label: 'Admin', to: '/admin' }, { label: 'Forms' }])
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Forms Management</h1>
        <p class="mt-1 text-sm text-gray-500">Manage claim submission forms and layouts</p>
      </div>
      <Button @click="router.push('/admin/forms/builder')">
        <PlusIcon class="h-5 w-5 mr-2" />
        New Form
      </Button>
    </div>

    <Card>
      <div class="p-4 border-b border-gray-200 flex justify-between items-center">
        <div class="relative w-64">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MagnifyingGlassIcon class="h-5 w-5 text-gray-400" />
          </div>
          <Input v-model="searchQuery" placeholder="Search forms..." class="pl-10" />
        </div>
      </div>

      <Table :columns="columns" :data="forms" @row-click="(row) => router.push(`/admin/forms/builder/${row.id}`)">
        <template #cell-status="{ value }">
          <Badge :variant="value === 'published' ? 'success' : 'secondary'">{{ value }}</Badge>
        </template>
        <template #actions="{ item }">
          <Button size="sm" variant="outline" @click.stop="router.push(`/admin/forms/builder/${item.id}`)">Edit</Button>
        </template>
      </Table>
      
      <div class="p-4 border-t border-gray-200">
        <Pagination :current-page="1" :total-pages="1" :total="3" :limit="10" />
      </div>
    </Card>
  </div>
</template>
