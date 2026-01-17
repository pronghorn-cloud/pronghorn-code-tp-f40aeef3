<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUIStore } from '@/stores'
import { Card, Button, Input, Select, Badge } from '@/components/ui'

const route = useRoute()
const router = useRouter()
const uiStore = useUIStore()

const isNew = computed(() => !route.params.id)
const ruleId = route.params.id as string

const rule = ref({
  name: '',
  description: '',
  type: 'validation',
  priority: 10,
  status: 'draft',
  conditions: [
    { field: 'claim.serviceCode', operator: 'equals', value: '' }
  ],
  actions: [
    { type: 'flag', message: '' }
  ]
})

const ruleTypes = [
  { value: 'validation', label: 'Validation' },
  { value: 'eligibility', label: 'Eligibility' },
  { value: 'pricing', label: 'Pricing' },
  { value: 'payment', label: 'Payment' }
]

const operators = [
  { value: 'equals', label: 'Equals' },
  { value: 'not_equals', label: 'Not Equals' },
  { value: 'contains', label: 'Contains' },
  { value: 'greater_than', label: 'Greater Than' },
  { value: 'less_than', label: 'Less Than' },
  { value: 'in', label: 'In List' }
]

const actionTypes = [
  { value: 'flag', label: 'Flag for Review' },
  { value: 'deny', label: 'Auto Deny' },
  { value: 'approve', label: 'Auto Approve' },
  { value: 'modify_fee', label: 'Modify Fee' }
]

const addCondition = () => {
  rule.value.conditions.push({ field: '', operator: 'equals', value: '' })
}

const removeCondition = (index: number) => {
  rule.value.conditions.splice(index, 1)
}

const addAction = () => {
  rule.value.actions.push({ type: 'flag', message: '' })
}

const removeAction = (index: number) => {
  rule.value.actions.splice(index, 1)
}

const saveRule = () => {
  console.log('Saving rule', rule.value)
  router.push('/admin/rules')
}

onMounted(() => {
  uiStore.setBreadcrumbs([
    { label: 'Admin', to: '/admin' },
    { label: 'Rules', to: '/admin/rules' },
    { label: isNew.value ? 'New Rule' : ruleId }
  ])

  if (!isNew.value) {
    // Mock data load
    rule.value = {
      name: 'Check Duplicate Service',
      description: 'Flag claims with same service code on same day',
      type: 'validation',
      priority: 10,
      status: 'active',
      conditions: [
        { field: 'claim.serviceCode', operator: 'equals', value: '03.03A' },
        { field: 'history.hasServiceToday', operator: 'equals', value: 'true' }
      ],
      actions: [
        { type: 'flag', message: 'Potential duplicate service detected' }
      ]
    }
  }
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">{{ isNew ? 'Create New Rule' : 'Edit Rule' }}</h1>
        <p class="mt-1 text-sm text-gray-500">Define logic for automated claim processing</p>
      </div>
      <div class="flex gap-3">
        <Button variant="secondary" @click="router.back()">Cancel</Button>
        <Button @click="saveRule">Save Rule</Button>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 space-y-6">
        <Card title="Rule Logic">
          <div class="space-y-6">
            <!-- Conditions -->
            <div>
              <div class="flex justify-between items-center mb-4">
                <h3 class="text-sm font-medium text-gray-900">Conditions (IF)</h3>
                <Button size="sm" variant="secondary" @click="addCondition">Add Condition</Button>
              </div>
              <div class="space-y-3">
                <div v-for="(condition, idx) in rule.conditions" :key="idx" class="flex gap-3 items-start bg-gray-50 p-3 rounded-md">
                  <div class="flex-1">
                     <Input v-model="condition.field" placeholder="Field (e.g. claim.amount)" />
                  </div>
                  <div class="w-40">
                    <select v-model="condition.operator" class="block w-full rounded-md border-gray-300 py-2 pl-3 pr-10 text-base focus:border-primary-500 focus:outline-none focus:ring-primary-500 sm:text-sm">
                      <option v-for="op in operators" :key="op.value" :value="op.value">{{ op.label }}</option>
                    </select>
                  </div>
                  <div class="flex-1">
                    <Input v-model="condition.value" placeholder="Value" />
                  </div>
                  <button @click="removeCondition(idx)" class="text-red-600 hover:text-red-800 p-2">
                    <span class="sr-only">Remove</span>
                    &times;
                  </button>
                </div>
              </div>
            </div>

            <div class="border-t border-gray-200"></div>

            <!-- Actions -->
            <div>
              <div class="flex justify-between items-center mb-4">
                <h3 class="text-sm font-medium text-gray-900">Actions (THEN)</h3>
                <Button size="sm" variant="secondary" @click="addAction">Add Action</Button>
              </div>
              <div class="space-y-3">
                <div v-for="(action, idx) in rule.actions" :key="idx" class="flex gap-3 items-start bg-blue-50 p-3 rounded-md">
                  <div class="w-48">
                    <select v-model="action.type" class="block w-full rounded-md border-gray-300 py-2 pl-3 pr-10 text-base focus:border-primary-500 focus:outline-none focus:ring-primary-500 sm:text-sm">
                      <option v-for="t in actionTypes" :key="t.value" :value="t.value">{{ t.label }}</option>
                    </select>
                  </div>
                  <div class="flex-1">
                    <Input v-model="action.message" placeholder="Message or Value" />
                  </div>
                  <button @click="removeAction(idx)" class="text-red-600 hover:text-red-800 p-2">
                    <span class="sr-only">Remove</span>
                    &times;
                  </button>
                </div>
              </div>
            </div>
          </div>
        </Card>
      </div>

      <div class="space-y-6">
        <Card title="Properties">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Rule Name</label>
              <Input v-model="rule.name" class="mt-1" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Description</label>
              <textarea v-model="rule.description" rows="3" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"></textarea>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Type</label>
              <select v-model="rule.type" class="mt-1 block w-full rounded-md border-gray-300 py-2 pl-3 pr-10 text-base focus:border-primary-500 focus:outline-none focus:ring-primary-500 sm:text-sm">
                <option v-for="t in ruleTypes" :key="t.value" :value="t.value">{{ t.label }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Status</label>
              <select v-model="rule.status" class="mt-1 block w-full rounded-md border-gray-300 py-2 pl-3 pr-10 text-base focus:border-primary-500 focus:outline-none focus:ring-primary-500 sm:text-sm">
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="draft">Draft</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Priority</label>
              <Input v-model="rule.priority" type="number" class="mt-1" />
              <p class="mt-1 text-xs text-gray-500">Higher numbers run later</p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  </div>
</template>
