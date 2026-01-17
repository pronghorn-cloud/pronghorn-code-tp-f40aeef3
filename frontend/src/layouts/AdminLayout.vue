<script setup lang="ts">
import { ref, computed } from 'vue'
import { RouterView, RouterLink, useRoute } from 'vue-router'
import { useAuthStore, useUIStore } from '@/stores'
import {
  HomeIcon,
  DocumentTextIcon,
  DocumentDuplicateIcon,
  CogIcon,
  ShieldCheckIcon,
  ClipboardDocumentListIcon,
  UsersIcon,
  ChartBarIcon,
  Bars3Icon,
  XMarkIcon,
  BellIcon,
  ArrowRightOnRectangleIcon,
  ChevronDownIcon,
  ExclamationTriangleIcon,
  BeakerIcon,
  TableCellsIcon,
} from '@heroicons/vue/24/outline'

const route = useRoute()
const authStore = useAuthStore()
const uiStore = useUIStore()

const isProfileMenuOpen = ref(false)
const expandedSections = ref<string[]>(['claims', 'forms', 'rules'])

const navigation = [
  { name: 'Dashboard', href: '/admin', icon: HomeIcon, exact: true },
  {
    name: 'Claims',
    icon: DocumentTextIcon,
    key: 'claims',
    children: [
      { name: 'All Claims', href: '/admin/claims' },
      { name: 'Flagged Claims', href: '/admin/claims/flagged', badge: 'flagged' },
    ],
  },
  {
    name: 'Forms & Templates',
    icon: DocumentDuplicateIcon,
    key: 'forms',
    children: [
      { name: 'Form Builder', href: '/admin/forms/builder' },
      { name: 'Forms List', href: '/admin/forms' },
      { name: 'Templates', href: '/admin/templates' },
    ],
  },
  {
    name: 'Rules Engine',
    icon: ShieldCheckIcon,
    key: 'rules',
    children: [
      { name: 'All Rules', href: '/admin/rules' },
      { name: 'Rule Testing', href: '/admin/rules/testing' },
    ],
  },
  { name: 'AHCIP Codes', href: '/admin/ahcip-codes', icon: TableCellsIcon },
  {
    name: 'Audit & Reports',
    icon: ClipboardDocumentListIcon,
    key: 'audit',
    roles: ['admin', 'auditor'],
    children: [
      { name: 'Audit Logs', href: '/admin/audit' },
      { name: 'Reports', href: '/admin/reports' },
    ],
  },
  { name: 'Users', href: '/admin/users', icon: UsersIcon, roles: ['admin'] },
  { name: 'Settings', href: '/admin/settings', icon: CogIcon, roles: ['admin'] },
]

const filteredNavigation = computed(() => {
  return navigation.filter(item => {
    if (!item.roles) return true
    return item.roles.includes(authStore.user?.role || '')
  })
})

const isActive = (href: string, exact = false) => {
  if (exact) {
    return route.path === href
  }
  return route.path.startsWith(href)
}

const toggleSection = (key: string) => {
  const index = expandedSections.value.indexOf(key)
  if (index === -1) {
    expandedSections.value.push(key)
  } else {
    expandedSections.value.splice(index, 1)
  }
}

const isSectionExpanded = (key: string) => expandedSections.value.includes(key)

const handleLogout = async () => {
  await authStore.logout()
  window.location.href = '/auth/login'
}
</script>

<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Mobile menu -->
    <div
      v-if="uiStore.isMobileMenuOpen"
      class="fixed inset-0 z-40 lg:hidden"
    >
      <div
        class="fixed inset-0 bg-gray-600 bg-opacity-75"
        @click="uiStore.closeMobileMenu()"
      />

      <div class="fixed inset-y-0 left-0 flex w-full max-w-xs flex-col bg-secondary-900">
        <div class="flex h-16 items-center justify-between px-4">
          <span class="text-xl font-bold text-white">Admin Portal</span>
          <button
            type="button"
            class="text-gray-300 hover:text-white"
            @click="uiStore.closeMobileMenu()"
          >
            <XMarkIcon class="h-6 w-6" />
          </button>
        </div>

        <nav class="flex-1 space-y-1 px-2 py-4 overflow-y-auto">
          <!-- Mobile nav items -->
          <template v-for="item in filteredNavigation" :key="item.name">
            <RouterLink
              v-if="!item.children"
              :to="item.href!"
              :class="[
                isActive(item.href!, item.exact)
                  ? 'bg-secondary-800 text-white'
                  : 'text-gray-300 hover:bg-secondary-700 hover:text-white',
                'group flex items-center rounded-md px-3 py-2 text-base font-medium',
              ]"
              @click="uiStore.closeMobileMenu()"
            >
              <component :is="item.icon" class="mr-4 h-6 w-6 flex-shrink-0" />
              {{ item.name }}
            </RouterLink>
          </template>
        </nav>
      </div>
    </div>

    <!-- Desktop sidebar -->
    <div class="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
      <div class="flex min-h-0 flex-1 flex-col bg-secondary-900">
        <!-- Logo -->
        <div class="flex h-16 flex-shrink-0 items-center px-4 bg-secondary-950">
          <span class="text-xl font-bold text-white">Admin Portal</span>
        </div>

        <!-- Navigation -->
        <nav class="flex-1 space-y-1 px-3 py-4 overflow-y-auto scrollbar-thin">
          <template v-for="item in filteredNavigation" :key="item.name">
            <!-- Simple link -->
            <RouterLink
              v-if="!item.children"
              :to="item.href!"
              :class="[
                isActive(item.href!, item.exact)
                  ? 'bg-secondary-800 text-white'
                  : 'text-gray-300 hover:bg-secondary-700 hover:text-white',
                'group flex items-center rounded-md px-3 py-2 text-sm font-medium transition-colors',
              ]"
            >
              <component
                :is="item.icon"
                :class="[
                  isActive(item.href!, item.exact) ? 'text-white' : 'text-gray-400 group-hover:text-gray-300',
                  'mr-3 h-5 w-5 flex-shrink-0',
                ]"
              />
              {{ item.name }}
            </RouterLink>

            <!-- Expandable section -->
            <div v-else>
              <button
                type="button"
                :class="[
                  item.children.some(c => isActive(c.href))
                    ? 'bg-secondary-800 text-white'
                    : 'text-gray-300 hover:bg-secondary-700 hover:text-white',
                  'w-full group flex items-center justify-between rounded-md px-3 py-2 text-sm font-medium transition-colors',
                ]"
                @click="toggleSection(item.key!)"
              >
                <span class="flex items-center">
                  <component
                    :is="item.icon"
                    :class="[
                      item.children.some(c => isActive(c.href)) ? 'text-white' : 'text-gray-400 group-hover:text-gray-300',
                      'mr-3 h-5 w-5 flex-shrink-0',
                    ]"
                  />
                  {{ item.name }}
                </span>
                <ChevronDownIcon
                  :class="[
                    isSectionExpanded(item.key!) ? 'rotate-180' : '',
                    'h-4 w-4 transition-transform',
                  ]"
                />
              </button>

              <Transition
                enter-active-class="transition duration-100 ease-out"
                enter-from-class="transform scale-95 opacity-0"
                enter-to-class="transform scale-100 opacity-100"
                leave-active-class="transition duration-75 ease-in"
                leave-from-class="transform scale-100 opacity-100"
                leave-to-class="transform scale-95 opacity-0"
              >
                <div v-if="isSectionExpanded(item.key!)" class="mt-1 space-y-1 pl-10">
                  <RouterLink
                    v-for="child in item.children"
                    :key="child.name"
                    :to="child.href"
                    :class="[
                      isActive(child.href)
                        ? 'bg-secondary-800 text-white'
                        : 'text-gray-400 hover:bg-secondary-700 hover:text-white',
                      'group flex items-center justify-between rounded-md px-3 py-2 text-sm font-medium transition-colors',
                    ]"
                  >
                    {{ child.name }}
                    <span
                      v-if="child.badge === 'flagged'"
                      class="bg-red-500 text-white text-xs px-2 py-0.5 rounded-full"
                    >
                      5
                    </span>
                  </RouterLink>
                </div>
              </Transition>
            </div>
          </template>
        </nav>

        <!-- User info -->
        <div class="flex-shrink-0 border-t border-secondary-700 p-4">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="h-10 w-10 rounded-full bg-secondary-700 flex items-center justify-center">
                <span class="text-sm font-medium text-white">
                  {{ authStore.userInitials }}
                </span>
              </div>
            </div>
            <div class="ml-3 min-w-0 flex-1">
              <p class="truncate text-sm font-medium text-white">
                {{ authStore.fullName }}
              </p>
              <p class="truncate text-xs text-gray-400 capitalize">
                {{ authStore.user?.role }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main content -->
    <div class="lg:pl-64">
      <!-- Top header -->
      <header class="sticky top-0 z-10 flex h-16 flex-shrink-0 bg-white shadow-sm">
        <div class="flex flex-1 items-center justify-between px-4">
          <!-- Mobile menu button -->
          <button
            type="button"
            class="lg:hidden text-gray-500 hover:text-gray-600"
            @click="uiStore.openMobileMenu()"
          >
            <Bars3Icon class="h-6 w-6" />
          </button>

          <!-- Breadcrumbs -->
          <div class="hidden lg:flex items-center">
            <nav v-if="uiStore.breadcrumbs.length" class="flex" aria-label="Breadcrumb">
              <ol class="flex items-center space-x-2">
                <li v-for="(crumb, index) in uiStore.breadcrumbs" :key="index" class="flex items-center">
                  <span v-if="index > 0" class="mx-2 text-gray-400">/</span>
                  <RouterLink
                    v-if="crumb.path && index < uiStore.breadcrumbs.length - 1"
                    :to="crumb.path"
                    class="text-sm text-gray-500 hover:text-gray-700"
                  >
                    {{ crumb.label }}
                  </RouterLink>
                  <span v-else class="text-sm text-gray-900 font-medium">
                    {{ crumb.label }}
                  </span>
                </li>
              </ol>
            </nav>
          </div>

          <!-- Right side actions -->
          <div class="flex items-center space-x-4">
            <!-- Notifications -->
            <button
              type="button"
              class="relative p-2 text-gray-400 hover:text-gray-500 rounded-full hover:bg-gray-100"
            >
              <BellIcon class="h-6 w-6" />
              <span class="absolute top-1 right-1 h-2 w-2 rounded-full bg-red-500" />
            </button>

            <!-- Profile dropdown -->
            <div class="relative">
              <button
                type="button"
                class="flex items-center space-x-3 rounded-full p-1 hover:bg-gray-100"
                @click="isProfileMenuOpen = !isProfileMenuOpen"
              >
                <div class="h-8 w-8 rounded-full bg-secondary-700 flex items-center justify-center">
                  <span class="text-sm font-medium text-white">
                    {{ authStore.userInitials }}
                  </span>
                </div>
              </button>

              <Transition
                enter-active-class="transition ease-out duration-100"
                enter-from-class="transform opacity-0 scale-95"
                enter-to-class="transform opacity-100 scale-100"
                leave-active-class="transition ease-in duration-75"
                leave-from-class="transform opacity-100 scale-100"
                leave-to-class="transform opacity-0 scale-95"
              >
                <div
                  v-if="isProfileMenuOpen"
                  class="dropdown-menu"
                  @click="isProfileMenuOpen = false"
                >
                  <div class="py-1">
                    <button
                      type="button"
                      class="dropdown-item flex items-center w-full text-left"
                      @click="handleLogout"
                    >
                      <ArrowRightOnRectangleIcon class="h-5 w-5 mr-3 text-gray-400" />
                      Sign out
                    </button>
                  </div>
                </div>
              </Transition>
            </div>
          </div>
        </div>
      </header>

      <!-- Page content -->
      <main class="py-6">
        <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <RouterView />
        </div>
      </main>
    </div>
  </div>
</template>
