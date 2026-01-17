import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import type { 
  Claim, 
  ClaimDraft, 
  PatientInfo, 
  ServiceLine, 
  FormTemplate,
  FormFieldDefinition 
} from '@/types'
import { useClaimsStore, useFormsStore } from '@/stores'

export interface UseClaimFormOptions {
  claimId?: string
  templateId?: string
  autoSaveInterval?: number
}

export function useClaimForm(options: UseClaimFormOptions = {}) {
  const router = useRouter()
  const toast = useToast()
  const claimsStore = useClaimsStore()
  const formsStore = useFormsStore()

  // State
  const isLoading = ref(false)
  const isSaving = ref(false)
  const isSubmitting = ref(false)
  const isDirty = ref(false)
  const lastSavedAt = ref<Date | null>(null)
  const errors = ref<Record<string, string>>({})
  const autoSaveTimer = ref<number | null>(null)

  // Form data
  const claimId = ref<string | null>(options.claimId || null)
  const templateId = ref<string>(options.templateId || '')
  const template = ref<FormTemplate | null>(null)
  
  const patientInfo = ref<Partial<PatientInfo>>({
    firstName: '',
    lastName: '',
    dateOfBirth: '',
    healthCardNumber: '',
    gender: undefined,
  })

  const serviceLines = ref<Partial<ServiceLine>[]>([{
    id: crypto.randomUUID(),
    procedureCode: '',
    description: '',
    serviceDate: '',
    quantity: 1,
    unitPrice: 0,
    total: 0,
  }])

  const documents = ref<string[]>([])

  // Computed
  const totalAmount = computed(() => {
    return serviceLines.value.reduce((sum, line) => sum + (line.total || 0), 0)
  })

  const isValid = computed(() => {
    return Object.keys(errors.value).length === 0 && validateForm()
  })

  const canSubmit = computed(() => {
    return isValid.value && !isSubmitting.value && !isSaving.value
  })

  const formData = computed<ClaimDraft>(() => ({
    templateId: templateId.value,
    patientInfo: patientInfo.value,
    serviceLines: serviceLines.value,
    documents: documents.value,
  }))

  // Validation
  function validateForm(): boolean {
    const newErrors: Record<string, string> = {}

    // Patient info validation
    if (!patientInfo.value.firstName?.trim()) {
      newErrors['patientInfo.firstName'] = 'First name is required'
    }
    if (!patientInfo.value.lastName?.trim()) {
      newErrors['patientInfo.lastName'] = 'Last name is required'
    }
    if (!patientInfo.value.dateOfBirth) {
      newErrors['patientInfo.dateOfBirth'] = 'Date of birth is required'
    }
    if (!patientInfo.value.healthCardNumber?.trim()) {
      newErrors['patientInfo.healthCardNumber'] = 'Health card number is required'
    }
    if (!patientInfo.value.gender) {
      newErrors['patientInfo.gender'] = 'Gender is required'
    }

    // Service lines validation
    serviceLines.value.forEach((line, index) => {
      if (!line.procedureCode?.trim()) {
        newErrors[`serviceLines.${index}.procedureCode`] = 'Procedure code is required'
      }
      if (!line.serviceDate) {
        newErrors[`serviceLines.${index}.serviceDate`] = 'Service date is required'
      }
      if (!line.quantity || line.quantity < 1) {
        newErrors[`serviceLines.${index}.quantity`] = 'Quantity must be at least 1'
      }
    })

    errors.value = newErrors
    return Object.keys(newErrors).length === 0
  }

  function validateField(fieldPath: string): string | null {
    const parts = fieldPath.split('.')
    
    if (parts[0] === 'patientInfo') {
      const field = parts[1] as keyof PatientInfo
      const value = patientInfo.value[field]
      
      switch (field) {
        case 'firstName':
        case 'lastName':
          return !value?.toString().trim() ? 'This field is required' : null
        case 'dateOfBirth':
          return !value ? 'Date of birth is required' : null
        case 'healthCardNumber':
          return !value?.toString().trim() ? 'Health card number is required' : null
        case 'gender':
          return !value ? 'Gender is required' : null
      }
    }
    
    return null
  }

  // Service line management
  function addServiceLine(): void {
    serviceLines.value.push({
      id: crypto.randomUUID(),
      procedureCode: '',
      description: '',
      serviceDate: '',
      quantity: 1,
      unitPrice: 0,
      total: 0,
    })
    isDirty.value = true
  }

  function removeServiceLine(index: number): void {
    if (serviceLines.value.length > 1) {
      serviceLines.value.splice(index, 1)
      isDirty.value = true
    }
  }

  function updateServiceLineTotal(index: number): void {
    const line = serviceLines.value[index]
    if (line) {
      line.total = (line.quantity || 0) * (line.unitPrice || 0)
      isDirty.value = true
    }
  }

  function setServiceLineFromAHCIP(
    index: number, 
    code: string, 
    description: string, 
    feeAmount: number
  ): void {
    const line = serviceLines.value[index]
    if (line) {
      line.procedureCode = code
      line.description = description
      line.unitPrice = feeAmount
      line.total = (line.quantity || 1) * feeAmount
      isDirty.value = true
    }
  }

  // Save operations
  async function saveDraft(): Promise<boolean> {
    if (!validateForm()) {
      return false
    }

    isSaving.value = true

    try {
      if (claimId.value) {
        await claimsStore.saveDraft(claimId.value, formData.value)
      } else {
        const claim = await claimsStore.createClaim(formData.value)
        claimId.value = claim.id
      }

      lastSavedAt.value = new Date()
      isDirty.value = false
      return true
    } catch (error: any) {
      toast.error(error.message || 'Failed to save draft')
      return false
    } finally {
      isSaving.value = false
    }
  }

  async function submitClaim(): Promise<boolean> {
    if (!validateForm()) {
      toast.error('Please fix validation errors before submitting')
      return false
    }

    isSubmitting.value = true

    try {
      // Save draft first if needed
      if (isDirty.value || !claimId.value) {
        const saved = await saveDraft()
        if (!saved) return false
      }

      // Submit the claim
      await claimsStore.submitClaim(claimId.value!)
      
      toast.success('Claim submitted successfully!')
      router.push({ name: 'claims-detail', params: { id: claimId.value } })
      return true
    } catch (error: any) {
      toast.error(error.message || 'Failed to submit claim')
      return false
    } finally {
      isSubmitting.value = false
    }
  }

  // Auto-save
  function startAutoSave(): void {
    const interval = options.autoSaveInterval || 30000 // 30 seconds
    autoSaveTimer.value = window.setInterval(async () => {
      if (isDirty.value && claimId.value) {
        await saveDraft()
      }
    }, interval)
  }

  function stopAutoSave(): void {
    if (autoSaveTimer.value) {
      clearInterval(autoSaveTimer.value)
      autoSaveTimer.value = null
    }
  }

  // Load existing claim
  async function loadClaim(id: string): Promise<void> {
    isLoading.value = true

    try {
      const claim = await claimsStore.fetchClaim(id)
      
      claimId.value = claim.id
      templateId.value = claim.templateId
      patientInfo.value = { ...claim.patientInfo }
      serviceLines.value = claim.serviceLines.map(line => ({ ...line }))
      documents.value = claim.documents?.map(d => d.id) || []
      
      isDirty.value = false
    } catch (error: any) {
      toast.error('Failed to load claim')
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // Load template
  async function loadTemplate(id: string): Promise<void> {
    isLoading.value = true

    try {
      template.value = await formsStore.fetchTemplate(id)
      templateId.value = id
    } catch (error: any) {
      toast.error('Failed to load template')
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // Reset form
  function resetForm(): void {
    claimId.value = null
    patientInfo.value = {
      firstName: '',
      lastName: '',
      dateOfBirth: '',
      healthCardNumber: '',
      gender: undefined,
    }
    serviceLines.value = [{
      id: crypto.randomUUID(),
      procedureCode: '',
      description: '',
      serviceDate: '',
      quantity: 1,
      unitPrice: 0,
      total: 0,
    }]
    documents.value = []
    errors.value = {}
    isDirty.value = false
    lastSavedAt.value = null
  }

  // Watch for changes
  watch(
    [patientInfo, serviceLines, documents],
    () => {
      isDirty.value = true
    },
    { deep: true }
  )

  // Lifecycle
  onMounted(() => {
    if (options.claimId) {
      loadClaim(options.claimId)
    }
    startAutoSave()
  })

  onUnmounted(() => {
    stopAutoSave()
  })

  return {
    // State
    isLoading,
    isSaving,
    isSubmitting,
    isDirty,
    lastSavedAt,
    errors,
    claimId,
    templateId,
    template,
    patientInfo,
    serviceLines,
    documents,
    // Computed
    totalAmount,
    isValid,
    canSubmit,
    formData,
    // Methods
    validateForm,
    validateField,
    addServiceLine,
    removeServiceLine,
    updateServiceLineTotal,
    setServiceLineFromAHCIP,
    saveDraft,
    submitClaim,
    loadClaim,
    loadTemplate,
    resetForm,
  }
}
