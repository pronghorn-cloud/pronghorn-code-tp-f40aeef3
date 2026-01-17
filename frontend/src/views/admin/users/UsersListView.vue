<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUIStore } from '@/stores'
import { Card, Button, Table, Badge, Pagination, Input } from '@/components/ui'
import { PlusIcon, MagnifyingGlassIcon } from '@heroicons/vue/24/outline'

const uiStore = useUIStore()
const searchQuery = ref('')

const users = ref([
  { id: 'USR-001', name: 'Admin User', email: 'admin@h-link.com', role: 'admin', status: 'active', lastLogin: '2024-01-20' },
  { id: 'USR-002', name: 'Dr. John Smith', email: 'jsmith@clinic.com', role: 'provider', status: 'active', lastLogin: '2024-01-19' },
  { id: 'USR-003', name: 'Sarah Auditor', email: 'sauditor@h-link.com', role: 'auditor', status: 'active', lastLogin: '2024-01-18' },
  { id: 'USR-004', name: 'Bob Adjudicator', email: 'badjudicator@h-link.com', role: 'adjudicator', status: 'inactive', lastLogin: '2023-12-15' },
])

const columns = [
  { key: 'name', label: 'Name', sortable: true },
  { key: 'email', label: 'Email', sortable: true },
  { key: 'role', label: 'Role', sortable: true },
  { key: 'status', label: 'Status', sortable: true },
  { key: 'lastLogin', label: 'Last Login', sortable: true },
]

onMounted(() => {
  uiStore.setBreadcrumbs([{ label: 'Admin', to: '/admin' }, { label: 'User Management' }])
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">User Management</h1>
        <p class="mt-1 text-sm text-gray-500">Manage system access and roles</p>
      </div>
      <Button>
        <PlusIcon class="h-5 w-5 mr-2" />
        Invite User
      </Button>
    </div>

    <Card>
      <div class="p-4 border-b border-gray-200 flex justify-between items-center">
        <div class="relative w-64">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MagnifyingGlassIcon class="h-5 w-5 text-gray-400" />
          </div>
          <Input v-model="searchQuery" placeholder="Search users..." class="pl-10" />
        </div>
      </div>

      <Table :columns="columns" :data="users">
        <template #cell-name="{ item }">
          <div class="flex items-center">
            <div class="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 font-bold mr-3">
              {{ item.name.charAt(0) }}
            </div>
            <div>
              <div class="font-medium text-gray-900">{{ item.name }}</div>
              <div class="text-xs text-gray-500">{{ item.id }}</div>
            </div>
          </div>
        </template>
        <template #cell-role="{ value }">
          <Badge variant="info">{{ value }}</Badge>
        </template>
        <template #cell-status="{ value }">
          <Badge :variant="value === 'active' ? 'success' : 'secondary'">{{ value }}</Badge>
        </template>
        <template #actions>
          <button class="text-blue-600 hover:text-blue-900 text-sm font-medium">Edit</button>
        </template>
      </Table>
      
      <div class="p-4 border-t border-gray-200">
        <Pagination :current-page="1" :total-pages="1" :total="4" :limit="10" />
      </div>
    </Card>
  </div>
</template>
