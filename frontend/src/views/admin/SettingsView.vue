<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Card, Button, Input } from '@/components/ui'
import { useUIStore } from '@/stores'

const uiStore = useUIStore()

const settings = ref({
  systemName: 'H-LINK Claims Platform',
  maintenanceMode: false,
  autoAdjudicationEnabled: true,
  maxDailyClaimsPerProvider: 50,
  emailNotifications: true,
})

const saveSettings = () => {
  // Mock save
  console.log('Settings saved', settings.value)
}

onMounted(() => {
  uiStore.setBreadcrumbs([{ label: 'Admin', to: '/admin' }, { label: 'Settings' }])
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-900">System Settings</h1>
      <Button @click="saveSettings">Save Changes</Button>
    </div>

    <Card>
      <div class="p-6 space-y-6">
        <h2 class="text-lg font-medium text-gray-900">General Configuration</h2>
        <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
          <div>
            <label class="block text-sm font-medium text-gray-700">System Name</label>
            <Input v-model="settings.systemName" class="mt-1" />
          </div>
          <div>
             <label class="block text-sm font-medium text-gray-700">Max Daily Claims (Per Provider)</label>
             <Input v-model="settings.maxDailyClaimsPerProvider" type="number" class="mt-1" />
          </div>
        </div>
        
        <div class="flex items-center space-x-4">
          <div class="flex items-center">
            <input id="maintenance" type="checkbox" v-model="settings.maintenanceMode" class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded" />
            <label for="maintenance" class="ml-2 block text-sm text-gray-900">Maintenance Mode</label>
          </div>
          <div class="flex items-center">
            <input id="auto-adj" type="checkbox" v-model="settings.autoAdjudicationEnabled" class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded" />
            <label for="auto-adj" class="ml-2 block text-sm text-gray-900">Enable Auto-Adjudication</label>
          </div>
        </div>
      </div>
    </Card>
  </div>
</template>