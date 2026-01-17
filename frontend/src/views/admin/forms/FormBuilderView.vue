<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUIStore } from '@/stores'
import { Card, Button, Input } from '@/components/ui'

const route = useRoute()
const router = useRouter()
const uiStore = useUIStore()

const isNew = computed(() => !route.params.id)
const formId = route.params.id as string

const form = ref({
  name: 'New Form',
  description: '',
  fields: [
    { id: '1', type: 'text', label: 'Patient Name', required: true, width: 'full' },
    { id: '2', type: 'date', label: 'Date of Service', required: true, width: 'half' },
    { id: '3', type: 'select', label: 'Service Type', required: true, width: 'half', options: ['Consultation', 'Procedure'] }
  ]
})

const fieldTypes = [
  { type: 'text', label: 'Text Input', icon: '📝' },
  { type: 'number', label: 'Number', icon: '🔢' },
  { type: 'date', label: 'Date Picker', icon: '📅' },
  { type: 'select', label: 'Dropdown', icon: '▼' },
  { type: 'checkbox', label: 'Checkbox', icon: '☑️' }
]

const addField = (type: string) => {
  form.value.fields.push({
    id: Date.now().toString(),
    type,
    label: 'New Field',
    required: false,
    width: 'full'
  })
}

const removeField = (index: number) => {
  form.value.fields.splice(index, 1)
}

const saveForm = () => {
  console.log('Saving form', form.value)
  router.push('/admin/forms')
}

onMounted(() => {
  uiStore.setBreadcrumbs([
    { label: 'Admin', to: '/admin' },
    { label: 'Forms', to: '/admin/forms' },
    { label: isNew.value ? 'Form Builder' : formId }
  ])
})
</script>

<template>
  <div class="h-[calc(100vh-8rem)] flex flex-col">
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-4">
        <Input v-model="form.name" class="text-xl font-bold w-64" />
        <span class="text-sm text-gray-500" v-if="!isNew">{{ formId }}</span>
      </div>
      <div class="flex gap-3">
        <Button variant="secondary" @click="router.back()">Cancel</Button>
        <Button @click="saveForm">Save Form</Button>
      </div>
    </div>

    <div class="flex-1 flex gap-6 overflow-hidden">
      <!-- Toolbox -->
      <div class="w-64 flex-shrink-0">
        <Card title="Toolbox" class="h-full">
          <div class="space-y-2">
            <div 
              v-for="ft in fieldTypes" 
              :key="ft.type" 
              class="p-3 bg-white border border-gray-200 rounded cursor-move hover:border-primary-500 hover:shadow-sm transition-all flex items-center gap-3"
              draggable="true"
              @click="addField(ft.type)"
            >
              <span class="text-xl">{{ ft.icon }}</span>
              <span class="text-sm font-medium text-gray-700">{{ ft.label }}</span>
            </div>
          </div>
        </Card>
      </div>

      <!-- Canvas -->
      <div class="flex-1 overflow-y-auto bg-gray-50 rounded-lg border-2 border-dashed border-gray-300 p-8">
        <div class="max-w-3xl mx-auto space-y-4">
          <div 
            v-for="(field, idx) in form.fields" 
            :key="field.id" 
            class="bg-white p-4 rounded shadow-sm border border-gray-200 relative group"
          >
            <div class="absolute right-2 top-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <button @click="removeField(idx)" class="text-red-500 hover:text-red-700 p-1">
                &times;
              </button>
            </div>
            
            <div class="flex gap-4 items-start">
              <div class="flex-1 space-y-3">
                <div>
                  <label class="text-xs text-gray-500 uppercase font-bold">Label</label>
                  <Input v-model="field.label" class="mt-1" />
                </div>
                <div class="flex items-center gap-4">
                   <label class="flex items-center text-sm text-gray-700">
                     <input type="checkbox" v-model="field.required" class="mr-2 rounded text-primary-600" />
                     Required
                   </label>
                   <select v-model="field.width" class="text-sm border-gray-300 rounded">
                     <option value="full">Full Width</option>
                     <option value="half">Half Width</option>
                     <option value="third">1/3 Width</option>
                   </select>
                </div>
              </div>
              <div class="w-1/3 p-4 bg-gray-50 rounded flex items-center justify-center text-gray-400 text-sm">
                Preview: {{ field.type }}
              </div>
            </div>
          </div>

          <div v-if="form.fields.length === 0" class="text-center py-12 text-gray-400">
            Click items from toolbox to add fields
          </div>
        </div>
      </div>

      <!-- Properties -->
      <div class="w-72 flex-shrink-0">
        <Card title="Form Properties" class="h-full">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Description</label>
              <textarea v-model="form.description" rows="3" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"></textarea>
            </div>
          </div>
        </Card>
      </div>
    </div>
  </div>
</template>
