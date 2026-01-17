<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUIStore } from '@/stores'
import { Card, Button, Input } from '@/components/ui'

const route = useRoute()
const router = useRouter()
const uiStore = useUIStore()

const isNew = computed(() => !route.params.id || route.params.id === 'new')
const templateId = route.params.id as string

const template = ref({
  name: '',
  type: 'email',
  subject: '',
  content: ''
})

const saveTemplate = () => {
  console.log('Saving template', template.value)
  router.push('/admin/templates')
}

onMounted(() => {
  uiStore.setBreadcrumbs([
    { label: 'Admin', to: '/admin' },
    { label: 'Templates', to: '/admin/templates' },
    { label: isNew.value ? 'New Template' : templateId }
  ])

  if (!isNew.value) {
    // Mock load
    template.value = {
      name: 'Standard Approval Email',
      type: 'email',
      subject: 'Claim Approved: {{claim_id}}',
      content: 'Dear {{provider_name}},\n\nYour claim {{claim_id}} has been approved for the amount of ${{amount}}.\n\nRegards,\nH-Link Admin'
    }
  }
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">{{ isNew ? 'Create Template' : 'Edit Template' }}</h1>
      </div>
      <div class="flex gap-3">
        <Button variant="secondary" @click="router.back()">Cancel</Button>
        <Button @click="saveTemplate">Save Template</Button>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 space-y-6">
        <Card title="Content">
          <div class="space-y-4">
            <div v-if="template.type === 'email'">
              <label class="block text-sm font-medium text-gray-700">Subject Line</label>
              <Input v-model="template.subject" class="mt-1" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Body Content</label>
              <textarea 
                v-model="template.content" 
                rows="15" 
                class="mt-1 font-mono text-sm block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              ></textarea>
            </div>
          </div>
        </Card>
      </div>

      <div class="space-y-6">
        <Card title="Properties">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Template Name</label>
              <Input v-model="template.name" class="mt-1" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Type</label>
              <select v-model="template.type" class="mt-1 block w-full rounded-md border-gray-300 py-2 pl-3 pr-10 text-base focus:border-primary-500 focus:outline-none focus:ring-primary-500 sm:text-sm">
                <option value="email">Email Notification</option>
                <option value="pdf">PDF Document</option>
                <option value="sms">SMS Message</option>
              </select>
            </div>
            <div>
              <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Available Variables</h4>
              <div class="flex flex-wrap gap-2">
                <span class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-800">{{claim_id}}</span>
                <span class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-800">{{provider_name}}</span>
                <span class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-800">{{amount}}</span>
                <span class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-800">{{service_date}}</span>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  </div>
</template>
