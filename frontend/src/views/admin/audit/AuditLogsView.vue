<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUIStore } from '@/stores'
import { Card, Table, Badge, Pagination, Input, Button } from '@/components/ui'
import { MagnifyingGlassIcon, ArrowDownTrayIcon } from '@heroicons/vue/24/outline'

const uiStore = useUIStore()
const searchQuery = ref('')

const logs = ref([
  { id: 'LOG-001', user: 'admin@h-link.com', action: 'LOGIN', resource: 'System', details: 'Successful login from 192.168.1.1', timestamp: '2024-01-20 08:30:15' },
  { id: 'LOG-002', user: 'system', action: 'AUTO_ADJUDICATE', resource: 'Claim #CLM-2024-001', details: 'Rule validation passed', timestamp: '2024-01-20 08:32:00' },
  { id: 'LOG-003', user: 'provider@clinic.com', action: 'SUBMIT_CLAIM', resource: 'Claim #CLM-2024-005', details: 'New claim submission', timestamp: '2024-01-20 09:15:22' },
  { id: 'LOG-004', user: 'admin@h-link.com', action: 'UPDATE_RULE', resource: 'Rule #RULE-002', details: 'Modified fee threshold', timestamp: '2024-01-20 10:05:45' },
])

const columns = [
  { key: 'timestamp', label: 'Timestamp', sortable: true },
  { key: 'user', label: 'User', sortable: true },
  { key: 'action', label: 'Action', sortable: true },
  { key: 'resource', label: 'Resource' },
  { key: 'details', label: 'Details' },
]

onMounted(() => {
  uiStore.setBreadcrumbs([{ label: 'Admin', to: '/admin' }, { label: 'Audit Logs' }])
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Audit Logs</h1>
        <p class="mt-1 text-sm text-gray-500">Track system activity and user actions</p>
      </div>
      <Button variant="outline">
        <ArrowDownTrayIcon class="h-5 w-5 mr-2" />
        Export CSV
      </Button>
    </div>

    <Card>
      <div class="p-4 border-b border-gray-200 flex justify-between items-center">
        <div class="relative w-64">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MagnifyingGlassIcon class="h-5 w-5 text-gray-400" />
          </div>
          <Input v-model="searchQuery" placeholder="Search logs..." class="pl-10" />
        </div>
      </div>

      <Table :columns="columns" :data="logs">
        <template #cell-action="{ value }">
          <Badge variant="secondary">{{ value }}</Badge>
        </template>
      </Table>
      
      <div class="p-4 border-t border-gray-200">
        <Pagination :current-page="1" :total-pages="1" :total="4" :limit="20" />
      </div>
    </Card>
  </div>
</template>
