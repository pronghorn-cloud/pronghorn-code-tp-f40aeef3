import { ref, computed, watch } from 'vue'
import { useDebounceFn } from '@vueuse/core'
import type { AHCIPCode, AHCIPSearchParams } from '@/types'
import { ahcipService } from '@/services/api'

export interface UseAHCIPSearchOptions {
  debounceMs?: number
  minQueryLength?: number
  defaultLimit?: number
}

export function useAHCIPSearch(options: UseAHCIPSearchOptions = {}) {
  const {
    debounceMs = 300,
    minQueryLength = 2,
    defaultLimit = 20,
  } = options

  // State
  const query = ref('')
  const category = ref<string | null>(null)
  const results = ref<AHCIPCode[]>([])
  const categories = ref<string[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const selectedCode = ref<AHCIPCode | null>(null)

  // Cache for frequently accessed codes
  const codeCache = ref<Map<string, AHCIPCode>>(new Map())

  // Computed
  const hasResults = computed(() => results.value.length > 0)
  const canSearch = computed(() => query.value.length >= minQueryLength)

  // Search function
  async function search(params?: Partial<AHCIPSearchParams>): Promise<void> {
    const searchQuery = params?.query ?? query.value
    const searchCategory = params?.category ?? category.value

    if (searchQuery.length < minQueryLength && !searchCategory) {
      results.value = []
      return
    }

    isLoading.value = true
    error.value = null

    try {
      const response = await ahcipService.search({
        query: searchQuery,
        category: searchCategory || undefined,
        limit: params?.limit || defaultLimit,
      })

      results.value = response.data.data || response.data

      // Cache the results
      results.value.forEach(code => {
        codeCache.value.set(code.procedureCode, code)
      })
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to search AHCIP codes'
      results.value = []
    } finally {
      isLoading.value = false
    }
  }

  // Debounced search for live typing
  const debouncedSearch = useDebounceFn(search, debounceMs)

  // Get single code details
  async function getCode(code: string): Promise<AHCIPCode | null> {
    // Check cache first
    if (codeCache.value.has(code)) {
      return codeCache.value.get(code)!
    }

    isLoading.value = true
    error.value = null

    try {
      const response = await ahcipService.get(code)
      const ahcipCode: AHCIPCode = response.data
      
      // Cache the result
      codeCache.value.set(code, ahcipCode)
      
      return ahcipCode
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to get AHCIP code'
      return null
    } finally {
      isLoading.value = false
    }
  }

  // Get fee schedule for multiple codes
  async function getFeeSchedule(
    codes: string[], 
    effectiveDate?: string
  ): Promise<Map<string, number>> {
    const feeMap = new Map<string, number>()

    try {
      const response = await ahcipService.getFeeSchedule(codes, effectiveDate)
      const schedule = response.data

      // Populate fee map from response
      if (Array.isArray(schedule)) {
        schedule.forEach((item: { code: string; feeAmount: number }) => {
          feeMap.set(item.code, item.feeAmount)
        })
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to get fee schedule'
    }

    return feeMap
  }

  // Load categories
  async function loadCategories(): Promise<void> {
    try {
      const response = await ahcipService.getCategories()
      categories.value = response.data
    } catch (err: any) {
      console.error('Failed to load AHCIP categories:', err)
    }
  }

  // Select a code
  function selectCode(code: AHCIPCode): void {
    selectedCode.value = code
  }

  // Clear selection
  function clearSelection(): void {
    selectedCode.value = null
  }

  // Clear search
  function clearSearch(): void {
    query.value = ''
    results.value = []
    error.value = null
  }

  // Set category filter
  function setCategory(cat: string | null): void {
    category.value = cat
    if (canSearch.value) {
      search()
    }
  }

  // Watch query changes for live search
  watch(query, () => {
    if (canSearch.value) {
      debouncedSearch()
    } else {
      results.value = []
    }
  })

  return {
    // State
    query,
    category,
    results,
    categories,
    isLoading,
    error,
    selectedCode,
    // Computed
    hasResults,
    canSearch,
    // Methods
    search,
    debouncedSearch,
    getCode,
    getFeeSchedule,
    loadCategories,
    selectCode,
    clearSelection,
    clearSearch,
    setCategory,
  }
}
