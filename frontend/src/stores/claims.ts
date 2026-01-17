import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { 
  Claim, 
  ClaimDraft, 
  ClaimFilters, 
  ClaimStatus,
  PaginatedResponse,
  AdjudicationResult 
} from '@/types'
import { claimsService } from '@/services/api'

export const useClaimsStore = defineStore('claims', () => {
  // State
  const claims = ref<Claim[]>([])
  const currentClaim = ref<Claim | null>(null)
  const flaggedClaims = ref<Claim[]>([])
  const isLoading = ref(false)
  const isSaving = ref(false)
  const error = ref<string | null>(null)
  const pagination = ref({
    page: 1,
    limit: 20,
    total: 0,
    totalPages: 0,
    hasNext: false,
    hasPrevious: false,
  })
  const filters = ref<ClaimFilters>({
    sortBy: 'createdAt',
    sortOrder: 'desc',
  })

  // Getters
  const draftClaims = computed(() => 
    claims.value.filter(c => c.status === 'draft')
  )
  const submittedClaims = computed(() => 
    claims.value.filter(c => c.status === 'submitted')
  )
  const pendingReviewClaims = computed(() => 
    claims.value.filter(c => c.status === 'in_review')
  )
  const totalClaimsAmount = computed(() => 
    claims.value.reduce((sum, c) => sum + c.totalAmount, 0)
  )
  const claimsByStatus = computed(() => {
    const grouped: Record<ClaimStatus, Claim[]> = {
      draft: [],
      submitted: [],
      in_review: [],
      adjudicated: [],
      approved: [],
      denied: [],
      paid: [],
    }
    claims.value.forEach(claim => {
      grouped[claim.status].push(claim)
    })
    return grouped
  })

  // Actions
  async function fetchClaims(newFilters?: Partial<ClaimFilters>): Promise<void> {
    isLoading.value = true
    error.value = null

    if (newFilters) {
      filters.value = { ...filters.value, ...newFilters }
    }

    try {
      const response = await claimsService.list({
        ...filters.value,
        page: pagination.value.page,
        limit: pagination.value.limit,
      })
      
      const data: PaginatedResponse<Claim> = response.data
      claims.value = data.data
      pagination.value = data.pagination
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch claims'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchClaim(id: string): Promise<Claim> {
    isLoading.value = true
    error.value = null

    try {
      const response = await claimsService.get(id)
      currentClaim.value = response.data
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch claim'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function createClaim(data: ClaimDraft): Promise<Claim> {
    isSaving.value = true
    error.value = null

    try {
      const response = await claimsService.create(data)
      const newClaim: Claim = response.data
      claims.value.unshift(newClaim)
      currentClaim.value = newClaim
      return newClaim
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to create claim'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  async function updateClaim(id: string, data: Partial<ClaimDraft>): Promise<Claim> {
    isSaving.value = true
    error.value = null

    try {
      const response = await claimsService.update(id, data)
      const updatedClaim: Claim = response.data
      
      // Update in list
      const index = claims.value.findIndex(c => c.id === id)
      if (index !== -1) {
        claims.value[index] = updatedClaim
      }
      
      // Update current if viewing
      if (currentClaim.value?.id === id) {
        currentClaim.value = updatedClaim
      }
      
      return updatedClaim
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to update claim'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  async function saveDraft(id: string, data: Partial<ClaimDraft>): Promise<Claim> {
    isSaving.value = true
    error.value = null

    try {
      const response = await claimsService.saveDraft(id, data)
      const updatedClaim: Claim = response.data
      
      // Update in list
      const index = claims.value.findIndex(c => c.id === id)
      if (index !== -1) {
        claims.value[index] = updatedClaim
      }
      
      if (currentClaim.value?.id === id) {
        currentClaim.value = updatedClaim
      }
      
      return updatedClaim
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to save draft'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  async function submitClaim(id: string): Promise<Claim> {
    isSaving.value = true
    error.value = null

    try {
      const response = await claimsService.submit(id)
      const submittedClaim: Claim = response.data
      
      // Update in list
      const index = claims.value.findIndex(c => c.id === id)
      if (index !== -1) {
        claims.value[index] = submittedClaim
      }
      
      if (currentClaim.value?.id === id) {
        currentClaim.value = submittedClaim
      }
      
      return submittedClaim
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to submit claim'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  async function deleteClaim(id: string): Promise<void> {
    isSaving.value = true
    error.value = null

    try {
      await claimsService.delete(id)
      claims.value = claims.value.filter(c => c.id !== id)
      
      if (currentClaim.value?.id === id) {
        currentClaim.value = null
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to delete claim'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  // Admin actions
  async function fetchFlaggedClaims(): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      const response = await claimsService.getFlagged()
      flaggedClaims.value = response.data.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch flagged claims'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function adjudicateClaim(
    id: string, 
    action: 'approve' | 'deny', 
    reason?: string
  ): Promise<AdjudicationResult> {
    isSaving.value = true
    error.value = null

    try {
      const response = await claimsService.adjudicate(id, { action, reason })
      
      // Update claim in lists
      const updateClaimInList = (list: Claim[]) => {
        const index = list.findIndex(c => c.id === id)
        if (index !== -1) {
          list[index] = { ...list[index], ...response.data.claim }
        }
      }
      
      updateClaimInList(claims.value)
      updateClaimInList(flaggedClaims.value)
      
      if (currentClaim.value?.id === id) {
        currentClaim.value = { ...currentClaim.value, ...response.data.claim }
      }
      
      return response.data.result
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to adjudicate claim'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  function setPage(page: number): void {
    pagination.value.page = page
    fetchClaims()
  }

  function setFilters(newFilters: Partial<ClaimFilters>): void {
    pagination.value.page = 1
    fetchClaims(newFilters)
  }

  function clearCurrentClaim(): void {
    currentClaim.value = null
  }

  function clearError(): void {
    error.value = null
  }

  return {
    // State
    claims,
    currentClaim,
    flaggedClaims,
    isLoading,
    isSaving,
    error,
    pagination,
    filters,
    // Getters
    draftClaims,
    submittedClaims,
    pendingReviewClaims,
    totalClaimsAmount,
    claimsByStatus,
    // Actions
    fetchClaims,
    fetchClaim,
    createClaim,
    updateClaim,
    saveDraft,
    submitClaim,
    deleteClaim,
    fetchFlaggedClaims,
    adjudicateClaim,
    setPage,
    setFilters,
    clearCurrentClaim,
    clearError,
  }
})
