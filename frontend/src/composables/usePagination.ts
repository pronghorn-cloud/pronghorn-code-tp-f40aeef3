import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

export interface UsePaginationOptions {
  initialPage?: number
  initialLimit?: number
  syncWithUrl?: boolean
}

export function usePagination(options: UsePaginationOptions = {}) {
  const route = useRoute()
  const router = useRouter()

  const {
    initialPage = 1,
    initialLimit = 20,
    syncWithUrl = true,
  } = options

  // State
  const page = ref(initialPage)
  const limit = ref(initialLimit)
  const total = ref(0)

  // Initialize from URL if syncing
  if (syncWithUrl && route.query.page) {
    page.value = parseInt(route.query.page as string) || initialPage
  }
  if (syncWithUrl && route.query.limit) {
    limit.value = parseInt(route.query.limit as string) || initialLimit
  }

  // Computed
  const totalPages = computed(() => Math.ceil(total.value / limit.value) || 1)
  const hasNext = computed(() => page.value < totalPages.value)
  const hasPrevious = computed(() => page.value > 1)
  const offset = computed(() => (page.value - 1) * limit.value)

  const startItem = computed(() => {
    if (total.value === 0) return 0
    return offset.value + 1
  })

  const endItem = computed(() => {
    const end = offset.value + limit.value
    return Math.min(end, total.value)
  })

  const displayRange = computed(() => {
    if (total.value === 0) return 'No items'
    return `${startItem.value}-${endItem.value} of ${total.value}`
  })

  // Page numbers for pagination UI
  const pageNumbers = computed(() => {
    const pages: (number | 'ellipsis')[] = []
    const maxVisible = 7

    if (totalPages.value <= maxVisible) {
      // Show all pages
      for (let i = 1; i <= totalPages.value; i++) {
        pages.push(i)
      }
    } else {
      // Show first, last, current, and surrounding pages with ellipsis
      const current = page.value
      const showFirst = current > 3
      const showLast = current < totalPages.value - 2

      if (showFirst) {
        pages.push(1)
        if (current > 4) pages.push('ellipsis')
      }

      // Pages around current
      const start = Math.max(showFirst ? current - 1 : 1, 1)
      const end = Math.min(showLast ? current + 1 : totalPages.value, totalPages.value)

      for (let i = start; i <= end; i++) {
        if (!pages.includes(i)) pages.push(i)
      }

      if (showLast) {
        if (current < totalPages.value - 3) pages.push('ellipsis')
        pages.push(totalPages.value)
      }
    }

    return pages
  })

  // Actions
  function setPage(newPage: number): void {
    if (newPage >= 1 && newPage <= totalPages.value) {
      page.value = newPage
      updateUrl()
    }
  }

  function nextPage(): void {
    if (hasNext.value) {
      setPage(page.value + 1)
    }
  }

  function previousPage(): void {
    if (hasPrevious.value) {
      setPage(page.value - 1)
    }
  }

  function firstPage(): void {
    setPage(1)
  }

  function lastPage(): void {
    setPage(totalPages.value)
  }

  function setLimit(newLimit: number): void {
    limit.value = newLimit
    page.value = 1 // Reset to first page when changing limit
    updateUrl()
  }

  function setTotal(newTotal: number): void {
    total.value = newTotal
    // Adjust page if current page is now out of bounds
    if (page.value > totalPages.value && totalPages.value > 0) {
      page.value = totalPages.value
    }
  }

  function reset(): void {
    page.value = initialPage
    limit.value = initialLimit
    total.value = 0
    updateUrl()
  }

  function updateUrl(): void {
    if (!syncWithUrl) return

    const query: Record<string, string> = { ...route.query } as Record<string, string>
    
    if (page.value !== 1) {
      query.page = page.value.toString()
    } else {
      delete query.page
    }

    if (limit.value !== initialLimit) {
      query.limit = limit.value.toString()
    } else {
      delete query.limit
    }

    router.replace({ query })
  }

  // Watch URL changes (for back/forward navigation)
  if (syncWithUrl) {
    watch(
      () => route.query,
      (query) => {
        const urlPage = parseInt(query.page as string) || initialPage
        const urlLimit = parseInt(query.limit as string) || initialLimit

        if (urlPage !== page.value) page.value = urlPage
        if (urlLimit !== limit.value) limit.value = urlLimit
      }
    )
  }

  return {
    // State
    page,
    limit,
    total,
    // Computed
    totalPages,
    hasNext,
    hasPrevious,
    offset,
    startItem,
    endItem,
    displayRange,
    pageNumbers,
    // Actions
    setPage,
    nextPage,
    previousPage,
    firstPage,
    lastPage,
    setLimit,
    setTotal,
    reset,
  }
}
