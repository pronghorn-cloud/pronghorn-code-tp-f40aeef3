<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUIStore } from '@/stores'
import { Card, Button, Table, Badge, Pagination, Input } from '@/components/ui'
import { PlusIcon, MagnifyingGlassIcon } from '@heroicons/vue/24/outline'

const router = useRouter()
const uiStore = useUIStore()
const searchQuery = ref('')

const templates = ref([
  { id: 'TMP-001', name: 'Standard Approval Email', type: 'Email', subject: 'Claim Approved: {{claim_id}}', lastModified: '2024-01-10' },
  { id: 'TMP-002', name: 'Rejection Notification', type: 'Email', subject: 'Claim Status Update', lastModified: '2024-01-12' },
  { id: 'TMP-003', name: 'Monthly Statement PDF', type: 'PDF', subject: 'N/A', lastModified: '2023-12-05' },
])

const columns = [
  { key: 'name', label: 'Template Name', sortable: true },
  { key: 'type', label: 'Type', sortable: true },
  { key: 'subject', label: 'Subject/Description' },
  { key: 'lastModified', label: 'Last Modified', sortable: true },
]

onMounted(() => {
  uiStore.setBreadcrumbs([{ label: 'Admin', to: '/admin' }, { label: 'Templates' }])
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Templates</h1>
        <p class="mt-1 text-sm text-gray-500">Manage email and document templates</p>
      </div>
      <Button @click="router.push('/admin/templates/new')">
        <PlusIcon class="h-5 w-5 mr-2" />
        New Template
      </Button>
    </div>

    <Card>
      <div class="p-4 border-b border-gray-200 flex justify-between items-center">
        <div class="relative w-64">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MagnifyingGlassIcon class="h-5 w-5 text-gray-400" />
          </div>
          <Input v-model="searchQuery" placeholder="Search templates..." class="pl-10" />
        </div>
      </div>

      <Table :columns="columns" :data="templates" @row-click="(row) => router.push(`/admin/templates/${row.id}`)">
        <template #actions="{ item }">
          <Button size="sm" variant="outline" @click.stop="router.push(`/admin/templates/${item.id}`)">Edit</Button>
        </template>
      </Table>
      
      <div class="p-4 border-t border-gray-200">
        <Pagination :current-page="1" :total-pages="1" :total="3" :limit="10" />
      </div>
    </Card>
  </div>
</template>
