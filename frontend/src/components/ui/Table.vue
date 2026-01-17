<script setup lang="ts" generic="T">
import { computed } from 'vue'
import { ChevronUpIcon, ChevronDownIcon } from '@heroicons/vue/20/solid'

export interface Column<T> {
  key: string
  label: string
  sortable?: boolean
  width?: string
  align?: 'left' | 'center' | 'right'
  render?: (item: T) => string
}

interface Props {
  columns: Column<T>[]
  data: T[]
  rowKey?: string
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
  loading?: boolean
  hoverable?: boolean
  striped?: boolean
  emptyMessage?: string
}

const props = withDefaults(defineProps<Props>(), {
  rowKey: 'id',
  sortOrder: 'asc',
  loading: false,
  hoverable: true,
  striped: false,
  emptyMessage: 'No data available',
})

const emit = defineEmits<{
  sort: [key: string, order: 'asc' | 'desc']
  rowClick: [item: T]
}>()

const handleSort = (column: Column<T>) => {
  if (!column.sortable) return

  const newOrder =
    props.sortBy === column.key && props.sortOrder === 'asc' ? 'desc' : 'asc'
  emit('sort', column.key, newOrder)
}

const getAlignClass = (align?: string) => {
  switch (align) {
    case 'center':
      return 'text-center'
    case 'right':
      return 'text-right'
    default:
      return 'text-left'
  }
}

const getCellValue = (item: T, column: Column<T>): any => {
  if (column.render) {
    return column.render(item)
  }
  // Support nested keys like 'user.name'
  return column.key.split('.').reduce((obj: any, key) => obj?.[key], item)
}
</script>

<template>
  <div class="overflow-x-auto">
    <table class="min-w-full divide-y divide-gray-200">
      <!-- Header -->
      <thead class="bg-gray-50">
        <tr>
          <th
            v-for="column in columns"
            :key="column.key"
            :class="[
              'px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider',
              getAlignClass(column.align),
              column.sortable && 'cursor-pointer hover:bg-gray-100 select-none',
            ]"
            :style="column.width ? { width: column.width } : {}"
            @click="handleSort(column)"
          >
            <div class="flex items-center gap-1" :class="column.align === 'right' && 'justify-end'">
              {{ column.label }}
              <span v-if="column.sortable" class="flex flex-col">
                <ChevronUpIcon
                  :class="[
                    'h-3 w-3 -mb-1',
                    sortBy === column.key && sortOrder === 'asc'
                      ? 'text-primary-600'
                      : 'text-gray-400',
                  ]"
                />
                <ChevronDownIcon
                  :class="[
                    'h-3 w-3 -mt-1',
                    sortBy === column.key && sortOrder === 'desc'
                      ? 'text-primary-600'
                      : 'text-gray-400',
                  ]"
                />
              </span>
            </div>
          </th>
          <!-- Actions column -->
          <th v-if="$slots.actions" class="px-6 py-3 text-right">
            <span class="sr-only">Actions</span>
          </th>
        </tr>
      </thead>

      <!-- Body -->
      <tbody class="bg-white divide-y divide-gray-200">
        <!-- Loading state -->
        <tr v-if="loading">
          <td
            :colspan="columns.length + ($slots.actions ? 1 : 0)"
            class="px-6 py-12 text-center"
          >
            <div class="flex items-center justify-center">
              <svg
                class="animate-spin h-8 w-8 text-primary-600"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  class="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  stroke-width="4"
                />
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
            </div>
          </td>
        </tr>

        <!-- Empty state -->
        <tr v-else-if="data.length === 0">
          <td
            :colspan="columns.length + ($slots.actions ? 1 : 0)"
            class="px-6 py-12 text-center text-gray-500"
          >
            <slot name="empty">
              {{ emptyMessage }}
            </slot>
          </td>
        </tr>

        <!-- Data rows -->
        <tr
          v-else
          v-for="(item, index) in data"
          :key="(item as any)[rowKey]"
          :class="[
            hoverable && 'hover:bg-gray-50',
            striped && index % 2 === 1 && 'bg-gray-50',
            'transition-colors',
          ]"
          @click="emit('rowClick', item)"
        >
          <td
            v-for="column in columns"
            :key="column.key"
            :class="[
              'px-6 py-4 whitespace-nowrap text-sm',
              getAlignClass(column.align),
            ]"
          >
            <slot :name="`cell-${column.key}`" :item="item" :value="getCellValue(item, column)">
              {{ getCellValue(item, column) }}
            </slot>
          </td>

          <!-- Actions column -->
          <td v-if="$slots.actions" class="px-6 py-4 whitespace-nowrap text-right text-sm">
            <slot name="actions" :item="item" />
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
