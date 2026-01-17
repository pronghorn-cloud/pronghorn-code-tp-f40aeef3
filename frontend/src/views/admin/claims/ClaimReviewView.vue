<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUIStore } from '@/stores'
import { Card, Button, Badge } from '@/components/ui'

const route = useRoute()
const router = useRouter()
const uiStore = useUIStore()

const claimId = route.params.id as string

// Mock claim data
const claim = ref({
  id: claimId,
  status: 'in_review',
  provider: {
    name: 'Metro Health Services',
    id: 'PRV-88321',
    specialty: 'General Practice'
  },
  patient: {
    name: 'John Doe',
    phn: '123456789',
    dob: '1980-05-15'
  },
  serviceDate: '2024-01-15',
  submissionDate: '2024-01-16',
  diagnosis: ['A09', 'R50.9'],
  services: [
    { code: '03.03A', description: 'Limited Visit', fee: 45.00, requested: 45.00, approved: 45.00 },
    { code: '13.59A', description: 'Intramuscular injection', fee: 15.00, requested: 15.00, approved: 15.00 }
  ],
  totalAmount: 60.00,
  flags: [
    { type: 'warning', message: 'Potential duplicate service for date' }
  ],
  history: [
    { date: '2024-01-16 10:30', action: 'Submitted', user: 'System' },
    { date: '2024-01-16 10:31', action: 'Flagged for Review', user: 'Rule Engine' }
  ]
})

const approveClaim = () => {
  // Logic to approve claim
  console.log('Approving claim', claimId)
  router.push('/admin/claims')
}

const rejectClaim = () => {
  // Logic to reject claim
  console.log('Rejecting claim', claimId)
  router.push('/admin/claims')
}

onMounted(() => {
  uiStore.setBreadcrumbs([
    { label: 'Admin', to: '/admin' },
    { label: 'Claims', to: '/admin/claims' },
    { label: claimId }
  ])
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-start">
      <div>
        <div class="flex items-center gap-3">
          <h1 class="text-2xl font-bold text-gray-900">Claim {{ claim.id }}</h1>
          <Badge :variant="claim.status as any">{{ claim.status }}</Badge>
        </div>
        <p class="mt-1 text-sm text-gray-500">Submitted on {{ claim.submissionDate }}</p>
      </div>
      <div class="flex gap-3">
        <Button variant="danger" @click="rejectClaim">Deny Claim</Button>
        <Button variant="primary" @click="approveClaim">Approve Claim</Button>
      </div>
    </div>

    <!-- Alerts/Flags -->
    <div v-if="claim.flags.length" class="bg-yellow-50 border-l-4 border-yellow-400 p-4">
      <div class="flex">
        <div class="ml-3">
          <p class="text-sm text-yellow-700">
            <span class="font-medium">Attention needed:</span>
            This claim has been flagged for manual review.
          </p>
          <ul class="mt-1 list-disc list-inside text-sm text-yellow-700">
            <li v-for="(flag, idx) in claim.flags" :key="idx">{{ flag.message }}</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Main Content -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Services -->
        <Card title="Services Rendered">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                  <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Fee</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="service in claim.services" :key="service.code">
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ service.code }}</td>
                  <td class="px-6 py-4 text-sm text-gray-500">{{ service.description }}</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">${{ service.fee.toFixed(2) }}</td>
                </tr>
              </tbody>
              <tfoot class="bg-gray-50">
                <tr>
                  <td colspan="2" class="px-6 py-4 text-right text-sm font-medium text-gray-900">Total</td>
                  <td class="px-6 py-4 text-right text-sm font-bold text-gray-900">${{ claim.totalAmount.toFixed(2) }}</td>
                </tr>
              </tfoot>
            </table>
          </div>
        </Card>

        <!-- Diagnosis -->
        <Card title="Diagnosis Codes">
          <div class="flex gap-2">
            <span 
              v-for="code in claim.diagnosis" 
              :key="code" 
              class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
            >
              {{ code }}
            </span>
          </div>
        </Card>
      </div>

      <!-- Sidebar -->
      <div class="space-y-6">
        <!-- Provider Info -->
        <Card title="Provider Details">
          <dl class="space-y-3">
            <div>
              <dt class="text-sm font-medium text-gray-500">Name</dt>
              <dd class="text-sm text-gray-900">{{ claim.provider.name }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">ID</dt>
              <dd class="text-sm text-gray-900">{{ claim.provider.id }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">Specialty</dt>
              <dd class="text-sm text-gray-900">{{ claim.provider.specialty }}</dd>
            </div>
          </dl>
        </Card>

        <!-- Patient Info -->
        <Card title="Patient Details">
          <dl class="space-y-3">
            <div>
              <dt class="text-sm font-medium text-gray-500">Name</dt>
              <dd class="text-sm text-gray-900">{{ claim.patient.name }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">PHN</dt>
              <dd class="text-sm text-gray-900">{{ claim.patient.phn }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">DOB</dt>
              <dd class="text-sm text-gray-900">{{ claim.patient.dob }}</dd>
            </div>
          </dl>
        </Card>
      </div>
    </div>
  </div>
</template>
