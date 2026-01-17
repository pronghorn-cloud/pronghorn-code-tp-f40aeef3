<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUIStore } from '@/stores'
import { Card, Button, Input } from '@/components/ui'

const uiStore = useUIStore()

const testClaim = ref('{
  "provider": "PRV-123",
  "patient": "PHN-456",
  "services": [
    { "code": "03.03A", "fee": 45.00 }
  ]
}')

const testResult = ref<any>(null)

const runTest = () => {
  // Mock test execution
  testResult.value = {
    success: true,
    triggeredRules: [
      { id: 'RULE-001', name: 'Check Duplicate Service', result: 'pass' },
      { id: 'RULE-002', name: 'Verify Age Limit', result: 'pass' }
    ],
    finalStatus: 'approved',
    executionTime: '45ms'
  }
}

onMounted(() => {
  uiStore.setBreadcrumbs([
    { label: 'Admin', to: '/admin' },
    { label: 'Rules', to: '/admin/rules' },
    { label: 'Test Console' }
  ])
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Rule Testing Console</h1>
        <p class="mt-1 text-sm text-gray-500">Test adjudication rules against sample claim data</p>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Card title="Test Input (JSON)">
        <div class="space-y-4">
          <textarea 
            v-model="testClaim" 
            rows="15" 
            class="font-mono text-sm block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
          ></textarea>
          <div class="flex justify-end">
            <Button @click="runTest">Run Test</Button>
          </div>
        </div>
      </Card>

      <Card title="Test Results">
        <div v-if="testResult" class="space-y-4">
          <div class="flex items-center gap-4 p-4 bg-green-50 rounded-lg">
            <div class="flex-1">
              <div class="text-sm font-medium text-green-800">Execution Successful</div>
              <div class="text-xs text-green-600">Time: {{ testResult.executionTime }}</div>
            </div>
            <div class="text-lg font-bold text-green-700 uppercase">
              {{ testResult.finalStatus }}
            </div>
          </div>

          <div class="space-y-2">
            <h3 class="text-sm font-medium text-gray-900">Rule Execution Trace</h3>
            <div v-for="rule in testResult.triggeredRules" :key="rule.id" class="flex justify-between items-center p-3 bg-gray-50 rounded border border-gray-200">
              <div>
                <div class="text-sm font-medium text-gray-900">{{ rule.name }}</div>
                <div class="text-xs text-gray-500">{{ rule.id }}</div>
              </div>
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                {{ rule.result }}
              </span>
            </div>
          </div>
        </div>
        <div v-else class="flex flex-col items-center justify-center h-64 text-gray-500">
          <p>Run a test to view results</p>
        </div>
      </Card>
    </div>
  </div>
</template>
