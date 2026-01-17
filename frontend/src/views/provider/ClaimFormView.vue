<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useClaimForm, useAHCIPSearch } from '@/composables'
import { useUIStore, useFormsStore } from '@/stores'
import { Card, Button, Input, Select, Badge } from '@/components/ui'
import {
  PlusIcon,
  TrashIcon,
  CloudArrowUpIcon,
  MagnifyingGlassIcon,
  CheckIcon,
  ExclamationTriangleIcon,
} from '@heroicons/vue/24/outline'

const route = useRoute()
const router = useRouter()
const uiStore = useUIStore()
const formsStore = useFormsStore()

const claimId = route.params.id as string | undefined

const {
  isLoading,
  isSaving,
  isSubmitting,
  isDirty,
  lastSavedAt,
  errors,
  patientInfo,
  serviceLines,
  totalAmount,
  canSubmit,
  addServiceLine,
  removeServiceLine,
  updateServiceLineTotal,
  setServiceLineFromAHCIP,
  saveDraft,
  submitClaim,
  loadClaim,
} = useClaimForm({ claimId })

const ahcipSearch = useAHCIPSearch()

const genderOptions = [
  { value: 'male', label: 'Male' },
  { value: 'female', label: 'Female' },
  { value: 'other', label: 'Other' },
]

onMounted(async () => {
  if (claimId) {
    uiStore.setBreadcrumbs([
      { label: 'Dashboard', path: '/' },
      { label: 'Claims', path: '/claims' },
      { label: 'Edit Claim' },
    ])
    await loadClaim(claimId)
  } else {
    uiStore.setBreadcrumbs([
      { label: 'Dashboard', path: '/' },
      { label: 'Claims', path: '/claims' },
      { label: 'New Claim' },
    ])
  }
  
  // Load templates
  await formsStore.fetchTemplates()
})

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-CA', {
    style: 'currency',
    currency: 'CAD',
  }).format(amount)
}

const formatDate = (date: Date | null) => {
  if (!date) return 'Never'
  return new Date(date).toLocaleTimeString('en-CA', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

const handleCodeSelect = (index: number, code: any) => {
  setServiceLineFromAHCIP(index, code.procedureCode, code.description, code.feeAmount)
  ahcipSearch.clearSearch()
}

const handleSave = async () => {
  const success = await saveDraft()
  if (success) {
    uiStore.showSuccess('Claim saved as draft')
  }
}

const handleSubmit = async () => {
  const success = await submitClaim()
  if (success) {
    router.push('/claims')
  }
}
</script>

<template>
  <div class="max-w-4xl mx-auto">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">
          {{ claimId ? 'Edit Claim' : 'New Claim' }}
        </h1>
        <p class="mt-1 text-sm text-gray-600">
          Fill out the claim details below
        </p>
      </div>
      
      <!-- Save status -->
      <div class="flex items-center gap-4">
        <div v-if="isDirty" class="flex items-center text-sm text-yellow-600">
          <ExclamationTriangleIcon class="h-4 w-4 mr-1" />
          Unsaved changes
        </div>
        <div v-else-if="lastSavedAt" class="flex items-center text-sm text-green-600">
          <CheckIcon class="h-4 w-4 mr-1" />
          Last saved {{ formatDate(lastSavedAt) }}
        </div>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="isLoading" class="flex items-center justify-center py-12">
      <div class="animate-spin h-8 w-8 border-4 border-primary-600 border-t-transparent rounded-full"></div>
    </div>

    <form v-else @submit.prevent="handleSubmit">
      <!-- Patient Information -->
      <Card class="mb-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Patient Information</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            v-model="patientInfo.firstName"
            label="First Name"
            required
            :error="errors['patientInfo.firstName']"
            placeholder="Enter first name"
          />
          
          <Input
            v-model="patientInfo.lastName"
            label="Last Name"
            required
            :error="errors['patientInfo.lastName']"
            placeholder="Enter last name"
          />
          
          <Input
            v-model="patientInfo.dateOfBirth"
            label="Date of Birth"
            type="date"
            required
            :error="errors['patientInfo.dateOfBirth']"
          />
          
          <Select
            v-model="patientInfo.gender"
            label="Gender"
            :options="genderOptions"
            required
            :error="errors['patientInfo.gender']"
          />
          
          <Input
            v-model="patientInfo.healthCardNumber"
            label="Health Card Number"
            required
            :error="errors['patientInfo.healthCardNumber']"
            placeholder="Enter health card number"
            class="md:col-span-2"
          />
        </div>
      </Card>

      <!-- Service Lines -->
      <Card class="mb-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-gray-900">Service Lines</h2>
          <Button type="button" variant="secondary" size="sm" @click="addServiceLine">
            <PlusIcon class="h-4 w-4 mr-1" />
            Add Service
          </Button>
        </div>

        <div class="space-y-4">
          <div
            v-for="(line, index) in serviceLines"
            :key="line.id"
            class="p-4 bg-gray-50 rounded-lg border border-gray-200"
          >
            <div class="flex items-start justify-between mb-3">
              <span class="text-sm font-medium text-gray-700">Service #{{ index + 1 }}</span>
              <Button
                v-if="serviceLines.length > 1"
                type="button"
                variant="ghost"
                size="sm"
                @click="removeServiceLine(index)"
              >
                <TrashIcon class="h-4 w-4 text-danger-500" />
              </Button>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <!-- AHCIP Code Search -->
              <div class="lg:col-span-2">
                <label class="form-label">Procedure Code</label>
                <div class="relative">
                  <div class="flex gap-2">
                    <input
                      v-model="line.procedureCode"
                      type="text"
                      class="form-input flex-1"
                      placeholder="Search AHCIP code..."
                      @input="ahcipSearch.query = ($event.target as HTMLInputElement).value"
                    />
                  </div>
                  
                  <!-- AHCIP Search Results -->
                  <div
                    v-if="ahcipSearch.hasResults && ahcipSearch.query"
                    class="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-md shadow-lg max-h-60 overflow-auto"
                  >
                    <button
                      v-for="code in ahcipSearch.results"
                      :key="code.procedureCode"
                      type="button"
                      class="w-full px-4 py-2 text-left hover:bg-gray-50 border-b border-gray-100 last:border-0"
                      @click="handleCodeSelect(index, code)"
                    >
                      <div class="flex justify-between">
                        <span class="font-medium text-gray-900">{{ code.procedureCode }}</span>
                        <span class="text-primary-600">{{ formatCurrency(code.feeAmount) }}</span>
                      </div>
                      <p class="text-sm text-gray-500 truncate">{{ code.description }}</p>
                    </button>
                  </div>
                </div>
                <p v-if="line.description" class="mt-1 text-xs text-gray-500">{{ line.description }}</p>
              </div>

              <Input
                v-model="line.serviceDate"
                label="Service Date"
                type="date"
                required
                :error="errors[`serviceLines.${index}.serviceDate`]"
              />

              <div>
                <label class="form-label">Quantity</label>
                <input
                  v-model.number="line.quantity"
                  type="number"
                  min="1"
                  class="form-input"
                  @change="updateServiceLineTotal(index)"
                />
              </div>

              <div>
                <label class="form-label">Unit Price</label>
                <input
                  v-model.number="line.unitPrice"
                  type="number"
                  step="0.01"
                  min="0"
                  class="form-input"
                  @change="updateServiceLineTotal(index)"
                />
              </div>

              <div>
                <label class="form-label">Total</label>
                <p class="form-input bg-gray-100 text-gray-700">
                  {{ formatCurrency(line.total || 0) }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Total -->
        <div class="mt-4 pt-4 border-t border-gray-200 flex justify-end">
          <div class="text-right">
            <p class="text-sm text-gray-500">Total Amount</p>
            <p class="text-2xl font-bold text-gray-900">{{ formatCurrency(totalAmount) }}</p>
          </div>
        </div>
      </Card>

      <!-- Documents -->
      <Card class="mb-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Supporting Documents</h2>
        
        <div class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary-400 transition-colors">
          <CloudArrowUpIcon class="h-12 w-12 text-gray-400 mx-auto" />
          <p class="mt-2 text-sm text-gray-600">
            Drag and drop files here, or
            <button type="button" class="text-primary-600 font-medium hover:text-primary-500">
              browse
            </button>
          </p>
          <p class="mt-1 text-xs text-gray-500">PDF, JPEG, PNG up to 10MB</p>
        </div>
      </Card>

      <!-- Actions -->
      <div class="flex items-center justify-between">
        <Button
          type="button"
          variant="secondary"
          @click="router.push('/claims')"
        >
          Cancel
        </Button>

        <div class="flex items-center gap-3">
          <Button
            type="button"
            variant="secondary"
            :loading="isSaving"
            @click="handleSave"
          >
            Save Draft
          </Button>
          
          <Button
            type="submit"
            variant="primary"
            :loading="isSubmitting"
            :disabled="!canSubmit"
          >
            Submit Claim
          </Button>
        </div>
      </div>
    </form>
  </div>
</template>
