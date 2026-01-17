<script setup lang="ts">
import { ref, computed } from 'vue'
import { RouterView, RouterLink, useRoute } from 'vue-router'
import { useAuthStore, useUIStore } from '@/stores'
import {
  HomeIcon,
  DocumentTextIcon,
  FolderIcon,
  UserCircleIcon,
  Bars3Icon,
  XMarkIcon,
  BellIcon,
  ArrowRightOnRectangleIcon,
  PlusIcon,
} from '@heroicons/vue/24/outline'

const route = useRoute()
const authStore = useAuthStore()
const uiStore = useUIStore()

const isProfileMenuOpen = ref(false)

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Claims', href: '/claims', icon: DocumentTextIcon },
  { name: 'Documents', href: '/documents', icon: FolderIcon },
]

const isActive = (href: string) => {
  if (href === '/') {
    return route.path === '/'
  }
  return route.path.startsWith(href)
}

const handleLogout = async () => {
  await authStore.logout()
  window.location.href = '/auth/login'
}
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Mobile menu -->
    <div
      v-if="uiStore.isMobileMenuOpen"
      class="fixed inset-0 z-40 lg:hidden"
    >
      <!-- Overlay -->
      <div
        class="fixed inset-0 bg-gray-600 bg-opacity-75"
        @click="uiStore.closeMobileMenu()"
      />

      <!-- Menu panel -->
      <div class="fixed inset-y-0 left-0 flex w-full max-w-xs flex-col bg-white">
        <div class="flex h-16 items-center justify-between px-4">
          <span class="text-xl font-bold text-primary-600">Claims Portal</span>
          <button
            type="button"
            class="text-gray-400 hover:text-gray-500"
            @click="uiStore.closeMobileMenu()"
          >
            <XMarkIcon class="h-6 w-6" />
          </button>
        </div>

        <nav class="flex-1 space-y-1 px-2 py-4">
          <RouterLink
            v-for="item in navigation"
            :key="item.name"
            :to="item.href"
            :class="[
              isActive(item.href)
                ? 'bg-primary-50 text-primary-700'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900',
              'group flex items-center rounded-md px-3 py-2 text-base font-medium',
            ]"
            @click="uiStore.closeMobileMenu()"
          >
            <component
              :is="item.icon"
              :class="[
                isActive(item.href) ? 'text-primary-600' : 'text-gray-400 group-hover:text-gray-500',
                'mr-4 h-6 w-6 flex-shrink-0',
              ]"
            />
            {{ item.name }}
          </RouterLink>
        </nav>
      </div>
    </div>

    <!-- Desktop sidebar -->
    <div class="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
      <div class="flex min-h-0 flex-1 flex-col border-r border-gray-200 bg-white">
        <!-- Logo -->
        <div class="flex h-16 flex-shrink-0 items-center px-4 border-b border-gray-200">
          <span class="text-xl font-bold text-primary-600">Claims Portal</span>
        </div>

        <!-- Navigation -->
        <nav class="flex-1 space-y-1 px-3 py-4">
          <RouterLink
            v-for="item in navigation"
            :key="item.name"
            :to="item.href"
            :class="[
              isActive(item.href)
                ? 'bg-primary-50 text-primary-700'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900',
              'group flex items-center rounded-md px-3 py-2 text-sm font-medium transition-colors',
            ]"
          >
            <component
              :is="item.icon"
              :class="[
                isActive(item.href) ? 'text-primary-600' : 'text-gray-400 group-hover:text-gray-500',
                'mr-3 h-5 w-5 flex-shrink-0',
              ]"
            />
            {{ item.name }}
          </RouterLink>
        </nav>

        <!-- New Claim Button -->
        <div class="p-4 border-t border-gray-200">
          <RouterLink
            to="/claims/new"
            class="btn-primary w-full flex items-center justify-center"
          >
            <PlusIcon class="h-5 w-5 mr-2" />
            New Claim
          </RouterLink>
        </div>

        <!-- User info -->
        <div class="flex-shrink-0 border-t border-gray-200 p-4">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center">
                <span class="text-sm font-medium text-primary-700">
                  {{ authStore.userInitials }}
                </span>
              </div>
            </div>
            <div class="ml-3 min-w-0 flex-1">
              <p class="truncate text-sm font-medium text-gray-900">
                {{ authStore.fullName }}
              </p>
              <p class="truncate text-xs text-gray-500">
                {{ authStore.provider?.providerName }}
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

          <!-- Page title / Breadcrumbs -->
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
                <div class="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center">
                  <span class="text-sm font-medium text-primary-700">
                    {{ authStore.userInitials }}
                  </span>
                </div>
              </button>

              <!-- Dropdown menu -->
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
                    <RouterLink to="/profile" class="dropdown-item flex items-center">
                      <UserCircleIcon class="h-5 w-5 mr-3 text-gray-400" />
                      Profile
                    </RouterLink>
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
