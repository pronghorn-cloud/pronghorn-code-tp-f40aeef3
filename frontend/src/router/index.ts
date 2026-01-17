import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Layout components
import ProviderLayout from '@/layouts/ProviderLayout.vue'
import AdminLayout from '@/layouts/AdminLayout.vue'
import AuthLayout from '@/layouts/AuthLayout.vue'

const routes: RouteRecordRaw[] = [
  // Auth routes
  {
    path: '/auth',
    component: AuthLayout,
    children: [
      {
        path: 'login',
        name: 'login',
        component: () => import('@/views/auth/LoginView.vue'),
        meta: { requiresGuest: true },
      },
      {
        path: 'forgot-password',
        name: 'forgot-password',
        component: () => import('@/views/auth/ForgotPasswordView.vue'),
        meta: { requiresGuest: true },
      },
    ],
  },

  // Provider routes
  {
    path: '/',
    component: ProviderLayout,
    meta: { requiresAuth: true, roles: ['provider'] },
    children: [
      {
        path: '',
        name: 'provider-dashboard',
        component: () => import('@/views/provider/DashboardView.vue'),
      },
      {
        path: 'claims',
        name: 'claims-list',
        component: () => import('@/views/provider/ClaimsListView.vue'),
      },
      {
        path: 'claims/new',
        name: 'claims-new',
        component: () => import('@/views/provider/ClaimFormView.vue'),
      },
      {
        path: 'claims/:id',
        name: 'claims-detail',
        component: () => import('@/views/provider/ClaimDetailView.vue'),
        props: true,
      },
      {
        path: 'claims/:id/edit',
        name: 'claims-edit',
        component: () => import('@/views/provider/ClaimFormView.vue'),
        props: true,
      },
      {
        path: 'documents',
        name: 'documents',
        component: () => import('@/views/provider/DocumentsView.vue'),
      },
      {
        path: 'profile',
        name: 'provider-profile',
        component: () => import('@/views/provider/ProfileView.vue'),
      },
    ],
  },

  // Admin routes
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true, roles: ['admin', 'adjudicator', 'auditor'] },
    children: [
      {
        path: '',
        name: 'admin-dashboard',
        component: () => import('@/views/admin/DashboardView.vue'),
      },
      // Claims management
      {
        path: 'claims',
        name: 'admin-claims',
        component: () => import('@/views/admin/claims/ClaimsManagementView.vue'),
      },
      {
        path: 'claims/:id',
        name: 'admin-claim-detail',
        component: () => import('@/views/admin/claims/ClaimReviewView.vue'),
        props: true,
      },
      {
        path: 'claims/flagged',
        name: 'flagged-claims',
        component: () => import('@/views/admin/claims/FlaggedClaimsView.vue'),
      },
      // Form management
      {
        path: 'forms',
        name: 'forms-list',
        component: () => import('@/views/admin/forms/FormsListView.vue'),
      },
      {
        path: 'forms/builder',
        name: 'form-builder',
        component: () => import('@/views/admin/forms/FormBuilderView.vue'),
      },
      {
        path: 'forms/builder/:id',
        name: 'form-builder-edit',
        component: () => import('@/views/admin/forms/FormBuilderView.vue'),
        props: true,
      },
      // Template management
      {
        path: 'templates',
        name: 'templates-list',
        component: () => import('@/views/admin/templates/TemplatesListView.vue'),
      },
      {
        path: 'templates/:id',
        name: 'template-detail',
        component: () => import('@/views/admin/templates/TemplateDetailView.vue'),
        props: true,
      },
      // Rules management
      {
        path: 'rules',
        name: 'rules-list',
        component: () => import('@/views/admin/rules/RulesListView.vue'),
      },
      {
        path: 'rules/new',
        name: 'rules-new',
        component: () => import('@/views/admin/rules/RuleEditorView.vue'),
      },
      {
        path: 'rules/:id',
        name: 'rules-edit',
        component: () => import('@/views/admin/rules/RuleEditorView.vue'),
        props: true,
      },
      {
        path: 'rules/testing',
        name: 'rules-testing',
        component: () => import('@/views/admin/rules/RuleTestingView.vue'),
      },
      // AHCIP Codes
      {
        path: 'ahcip-codes',
        name: 'ahcip-codes',
        component: () => import('@/views/admin/AHCIPCodesView.vue'),
      },
      // Audit & Reports
      {
        path: 'audit',
        name: 'audit-logs',
        component: () => import('@/views/admin/audit/AuditLogsView.vue'),
        meta: { roles: ['admin', 'auditor'] },
      },
      {
        path: 'reports',
        name: 'reports',
        component: () => import('@/views/admin/audit/ReportsView.vue'),
        meta: { roles: ['admin', 'auditor'] },
      },
      // User management
      {
        path: 'users',
        name: 'users-list',
        component: () => import('@/views/admin/users/UsersListView.vue'),
        meta: { roles: ['admin'] },
      },
      // Settings
      {
        path: 'settings',
        name: 'admin-settings',
        component: () => import('@/views/admin/SettingsView.vue'),
        meta: { roles: ['admin'] },
      },
    ],
  },

  // Error routes
  {
    path: '/403',
    name: 'forbidden',
    component: () => import('@/views/errors/ForbiddenView.vue'),
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/errors/NotFoundView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    return { top: 0 }
  },
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Check if route requires authentication
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      return next({ name: 'login', query: { redirect: to.fullPath } })
    }

    // Check role-based access
    const allowedRoles = to.meta.roles as string[] | undefined
    if (allowedRoles && !allowedRoles.includes(authStore.user?.role || '')) {
      return next({ name: 'forbidden' })
    }
  }

  // Redirect authenticated users away from guest-only pages
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    const redirectPath = authStore.user?.role === 'provider' ? '/' : '/admin'
    return next(redirectPath)
  }

  next()
})

export default router
