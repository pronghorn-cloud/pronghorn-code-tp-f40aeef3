<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { useClaimsStore, useUIStore } from '@/stores'
import { Card, Badge, Button } from '@/components/ui'
import {
  ArrowLeftIcon,
  PencilIcon,
  DocumentDuplicateIcon,
  PrinterIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  DocumentIcon,
  ArrowDownTrayIcon,
} from '@heroicons/vue/24/outline'

const route = useRoute()
const router = useRouter()
const claimsStore = useClaimsStore()
const uiStore = useUIStore()

const claimId = route.params.id as string

onMounted(async () => {
  await claimsStore.fetchClaim(claimId)
  
  uiStore.setBreadcrumbs([
    { label: 'Dashboard', path: '/' },
    { label: 'Claims', path: '/claims' },
    { label: `Claim #${claimId.slice(0, 8)}` },
  ])
})

const claim = computed(() => claimsStore.currentClaim)

const canEdit = computed(() => claim.value?.status === 'draft')

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-CA', {
    style: 'currency',
    currency: 'CAD',
  }).format(amount)
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('en-CA', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

const formatDateTime = (date: string) => {
  return new Date(date).toLocaleString('en-CA', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'approved':
    case 'paid':
      return CheckCircleIcon
    case 'denied':
      return XCircleIcon
    case 'in_review':
      return ExclamationTriangleIcon
    default:
      return ClockIcon
  }
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'approved':
    case 'paid':
      return 'text-green-600 bg-green-100'
    case 'denied':
      return 'text-red-600 bg-red-100'
    case 'in_review':
      return 'text-yellow-600 bg-yellow-100'
    case 'submitted':
      return 'text-blue-600 bg-blue-100'
    default:
      return 'text-gray-600 bg-gray-100'
  }
}
</script>

<template>
  <div class="max-w-4xl mx-auto">
    <!-- Loading -->
    <div v-if="claimsStore.isLoading" class="flex items-center justify-center py-12">
      <div class="animate-spin h-8 w-8 border-4 border-primary-600 border-t-transparent rounded-full"></div>
    </div>

    <template v-else-if="claim">
      <!-- Header -->
      <div class="mb-6">
        <RouterLink
          to="/claims"
          class="inline-flex items-center text-sm text-gray-500 hover:text-gray-700 mb-4"
        >
          <ArrowLeftIcon class="h-4 w-4 mr-1" />
          Back to Claims
        </RouterLink>

        <div class="flex items-start justify-between">
          <div>
            <div class="flex items-center gap-3">
              <h1 class="text-2xl font-bold text-gray-900">
                Claim #{{ claim.id.slice(0, 8) }}
              </h1>
              <Badge :variant="claim.status" size="lg" dot />
            </div>
            <p class="mt-1 text-sm text-gray-600">
              Created on {{ formatDate(claim.createdAt) }}
            </p>
          </div>

          <div class="flex items-center gap-2">
            <Button v-if="canEdit" variant="secondary" @click="router.push(`/claims/${claim.id}/edit`)">
              <PencilIcon class="h-4 w-4 mr-2" />
              Edit
            </Button>
            <Button variant="secondary">
              <PrinterIcon class="h-4 w-4 mr-2" />
              Print
            </Button>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Main content -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Patient Information -->
          <Card>
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Patient Information</h2>
            <dl class="grid grid-cols-2 gap-4">
              <div>
                <dt class="text-sm text-gray-500">Name</dt>
                <dd class="text-sm font-medium text-gray-900">
                  {{ claim.patientInfo.firstName }} {{ claim.patientInfo.lastName }}
                </dd>
              </div>
              <div>
                <dt class="text-sm text-gray-500">Date of Birth</dt>
                <dd class="text-sm font-medium text-gray-900">
                  {{ formatDate(claim.patientInfo.dateOfBirth) }}
                </dd>
              </div>
              <div>
                <dt class="text-sm text-gray-500">Health Card Number</dt>
                <dd class="text-sm font-medium text-gray-900">
                  {{ claim.patientInfo.healthCardNumber }}
                </dd>
              </div>
              <div>
                <dt class="text-sm text-gray-500">Gender</dt>
                <dd class="text-sm font-medium text-gray-900 capitalize">
                  {{ claim.patientInfo.gender }}
                </dd>
              </div>
            </dl>
          </Card>

          <!-- Service Lines -->
          <Card>
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Services</h2>
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead>
                  <tr>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    <th class="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Qty</th>
                    <th class="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Price</th>
                    <th class="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Total</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200">
                  <tr v-for="line in claim.serviceLines" :key="line.id">
                    <td class="px-4 py-3 text-sm font-medium text-gray-900">{{ line.procedureCode }}</td>
                    <td class="px-4 py-3 text-sm text-gray-600">{{ line.description }}</td>
                    <td class="px-4 py-3 text-sm text-gray-600">{{ formatDate(line.serviceDate) }}</td>
                    <td class="px-4 py-3 text-sm text-gray-600 text-right">{{ line.quantity }}</td>
                    <td class="px-4 py-3 text-sm text-gray-600 text-right">{{ formatCurrency(line.unitPrice) }}</td>
                    <td class="px-4 py-3 text-sm font-medium text-gray-900 text-right">{{ formatCurrency(line.total) }}</td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr class="bg-gray-50">
                    <td colspan="5" class="px-4 py-3 text-sm font-medium text-gray-900 text-right">Total</td>
                    <td class="px-4 py-3 text-lg font-bold text-gray-900 text-right">{{ formatCurrency(claim.totalAmount) }}</td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </Card>

          <!-- Documents -->
          <Card v-if="claim.documents && claim.documents.length > 0">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Supporting Documents</h2>
            <ul class="divide-y divide-gray-200">
              <li v-for="doc in claim.documents" :key="doc.id" class="py-3 flex items-center justify-between">
                <div class="flex items-center">
                  <DocumentIcon class="h-8 w-8 text-gray-400" />
                  <div class="ml-3">
                    <p class="text-sm font-medium text-gray-900">{{ doc.fileName }}</p>
                    <p class="text-xs text-gray-500">{{ doc.documentType }} • {{ formatDate(doc.uploadedAt) }}</p>
                  </div>
                </div>
                <Button variant="ghost" size="sm">
                  <ArrowDownTrayIcon class="h-4 w-4" />
                </Button>
              </li>
            </ul>
          </Card>
        </div>

        <!-- Sidebar -->
        <div class="space-y-6">
          <!-- Status Timeline -->
          <Card>
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Status History</h2>
            <ol class="relative border-l border-gray-200 ml-3">
              <li
                v-for="(history, index) in claim.statusHistory"
                :key="history.id"
                class="mb-6 ml-6 last:mb-0"
              >
                <span
                  :class="[
                    'absolute flex items-center justify-center w-6 h-6 rounded-full -left-3',
                    getStatusColor(history.status),
                  ]"
                >
                  <component :is="getStatusIcon(history.status)" class="w-3 h-3" />
                </span>
                <div>
                  <Badge :variant="history.status" size="sm" />
                  <time class="block text-xs text-gray-500 mt-1">
                    {{ formatDateTime(history.changedAt) }}
                  </time>
                  <p v-if="history.reason" class="text-sm text-gray-600 mt-1">
                    {{ history.reason }}
                  </p>
                </div>
              </li>
            </ol>
          </Card>

          <!-- Adjudication Result -->
          <Card v-if="claim.adjudicationResult">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Adjudication Result</h2>
            <dl class="space-y-3">
              <div>
                <dt class="text-sm text-gray-500">Status</dt>
                <dd>
                  <Badge :variant="claim.adjudicationResult.status" />
                </dd>
              </div>
              <div>
                <dt class="text-sm text-gray-500">Payment Amount</dt>
                <dd class="text-lg font-semibold text-gray-900">
                  {{ formatCurrency(claim.adjudicationResult.paymentAmount) }}
                </dd>
              </div>
              <div v-if="claim.adjudicationResult.denialReason">
                <dt class="text-sm text-gray-500">Denial Reason</dt>
                <dd class="text-sm text-gray-900">
                  {{ claim.adjudicationResult.denialReason }}
                </dd>
              </div>
              <div>
                <dt class="text-sm text-gray-500">Processed</dt>
                <dd class="text-sm text-gray-900">
                  {{ formatDateTime(claim.adjudicationResult.processedAt) }}
                </dd>
              </div>
            </dl>
          </Card>
        </div>
      </div>
    </template>

    <!-- Not found -->
    <div v-else class="text-center py-12">
      <h2 class="text-lg font-medium text-gray-900">Claim not found</h2>
      <p class="mt-1 text-sm text-gray-500">The claim you're looking for doesn't exist.</p>
      <RouterLink to="/claims" class="mt-4 inline-block">
        <Button variant="primary">Back to Claims</Button>
      </RouterLink>
    </div>
  </div>
</template>
