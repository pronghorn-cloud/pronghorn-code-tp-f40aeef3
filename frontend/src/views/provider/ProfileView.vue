<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Card, Button, Input, Badge } from '@/components/ui'
import { useUIStore, useAuthStore } from '@/stores'
import {
  UserCircleIcon,
  BuildingOfficeIcon,
  EnvelopeIcon,
  PhoneIcon,
  MapPinIcon,
  IdentificationIcon,
  ShieldCheckIcon,
  PencilIcon,
  CheckIcon,
  XMarkIcon,
  KeyIcon,
  BellIcon,
  DocumentTextIcon,
} from '@heroicons/vue/24/outline'

const uiStore = useUIStore()
const authStore = useAuthStore()

// State
const isEditing = ref(false)
const isSaving = ref(false)
const showPasswordModal = ref(false)
const activeTab = ref('profile')

// Profile data
const profile = reactive({
  firstName: 'John',
  lastName: 'Smith',
  email: 'dr.smith@metrohealth.ca',
  phone: '(403) 555-0123',
  practiceName: 'Metro Health Medical Clinic',
  practiceType: 'Medical Clinic',
  ahcipNumber: 'AH-123456',
  registrationDate: '2024-03-15',
  address: {
    street: '123 Medical Center Drive',
    suite: 'Suite 400',
    city: 'Calgary',
    province: 'Alberta',
    postalCode: 'T2P 1J9',
  },
  billingAddress: {
    sameAsMain: true,
    street: '',
    suite: '',
    city: '',
    province: '',
    postalCode: '',
  },
})

// Edit copy
const editProfile = reactive({ ...profile })

// Notification preferences
const notifications = reactive({
  emailClaimUpdates: true,
  emailPayments: true,
  emailFlagged: true,
  emailNewsletter: false,
  smsAlerts: false,
})

// Password change form
const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
})

// Tabs
const tabs = [
  { id: 'profile', label: 'Profile Information', icon: UserCircleIcon },
  { id: 'practice', label: 'Practice Details', icon: BuildingOfficeIcon },
  { id: 'security', label: 'Security', icon: ShieldCheckIcon },
  { id: 'notifications', label: 'Notifications', icon: BellIcon },
]

// Methods
const startEditing = () => {
  Object.assign(editProfile, JSON.parse(JSON.stringify(profile)))
  isEditing.value = true
}

const cancelEditing = () => {
  isEditing.value = false
}

const saveProfile = async () => {
  isSaving.value = true
  try {
    // TODO: API call to save profile
    await new Promise((resolve) => setTimeout(resolve, 1000))
    Object.assign(profile, JSON.parse(JSON.stringify(editProfile)))
    isEditing.value = false
  } catch (error) {
    console.error('Failed to save profile:', error)
  } finally {
    isSaving.value = false
  }
}

const changePassword = async () => {
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    alert('Passwords do not match')
    return
  }

  try {
    // TODO: API call to change password
    await new Promise((resolve) => setTimeout(resolve, 1000))
    showPasswordModal.value = false
    passwordForm.currentPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
  } catch (error) {
    console.error('Failed to change password:', error)
  }
}

const saveNotifications = async () => {
  try {
    // TODO: API call to save notification preferences
    await new Promise((resolve) => setTimeout(resolve, 500))
  } catch (error) {
    console.error('Failed to save notifications:', error)
  }
}

onMounted(() => {
  uiStore.setBreadcrumbs([
    { label: 'Dashboard', to: '/provider' },
    { label: 'Profile' },
  ])
})
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Profile Settings</h1>
        <p class="mt-1 text-sm text-gray-500">
          Manage your account information and preferences
        </p>
      </div>
    </div>

    <!-- Profile Header Card -->
    <Card class="p-6">
      <div class="flex items-center">
        <div class="flex-shrink-0">
          <div class="h-20 w-20 rounded-full bg-blue-100 flex items-center justify-center">
            <UserCircleIcon class="h-12 w-12 text-blue-600" />
          </div>
        </div>
        <div class="ml-6">
          <h2 class="text-xl font-semibold text-gray-900">
            Dr. {{ profile.firstName }} {{ profile.lastName }}
          </h2>
          <p class="text-sm text-gray-500">{{ profile.practiceName }}</p>
          <div class="mt-2 flex items-center gap-4">
            <Badge variant="success">
              <ShieldCheckIcon class="w-3 h-3 mr-1" />
              Verified Provider
            </Badge>
            <span class="text-sm text-gray-500">
              AHCIP #: {{ profile.ahcipNumber }}
            </span>
          </div>
        </div>
      </div>
    </Card>

    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex space-x-8">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            activeTab === tab.id
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            'group inline-flex items-center py-4 px-1 border-b-2 font-medium text-sm',
          ]"
        >
          <component
            :is="tab.icon"
            :class="[
              activeTab === tab.id ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500',
              '-ml-0.5 mr-2 h-5 w-5',
            ]"
          />
          {{ tab.label }}
        </button>
      </nav>
    </div>

    <!-- Profile Information Tab -->
    <Card v-if="activeTab === 'profile'" class="p-6">
      <div class="flex items-center justify-between mb-6">
        <h3 class="text-lg font-medium text-gray-900">Personal Information</h3>
        <div v-if="!isEditing">
          <Button variant="outline" @click="startEditing">
            <PencilIcon class="w-4 h-4 mr-2" />
            Edit
          </Button>
        </div>
        <div v-else class="flex gap-2">
          <Button variant="outline" @click="cancelEditing">
            <XMarkIcon class="w-4 h-4 mr-2" />
            Cancel
          </Button>
          <Button @click="saveProfile" :loading="isSaving">
            <CheckIcon class="w-4 h-4 mr-2" />
            Save
          </Button>
        </div>
      </div>

      <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <div>
          <label class="block text-sm font-medium text-gray-700">First Name</label>
          <Input
            v-if="isEditing"
            v-model="editProfile.firstName"
            class="mt-1"
          />
          <p v-else class="mt-1 text-sm text-gray-900">{{ profile.firstName }}</p>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Last Name</label>
          <Input
            v-if="isEditing"
            v-model="editProfile.lastName"
            class="mt-1"
          />
          <p v-else class="mt-1 text-sm text-gray-900">{{ profile.lastName }}</p>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Email Address</label>
          <div class="mt-1 flex items-center">
            <EnvelopeIcon class="w-5 h-5 text-gray-400 mr-2" />
            <Input
              v-if="isEditing"
              v-model="editProfile.email"
              type="email"
            />
            <span v-else class="text-sm text-gray-900">{{ profile.email }}</span>
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Phone Number</label>
          <div class="mt-1 flex items-center">
            <PhoneIcon class="w-5 h-5 text-gray-400 mr-2" />
            <Input
              v-if="isEditing"
              v-model="editProfile.phone"
              type="tel"
            />
            <span v-else class="text-sm text-gray-900">{{ profile.phone }}</span>
          </div>
        </div>
      </div>

      <div class="mt-6 pt-6 border-t border-gray-200">
        <h4 class="text-sm font-medium text-gray-900 mb-4">Address</h4>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div class="sm:col-span-2">
            <label class="block text-sm font-medium text-gray-700">Street Address</label>
            <Input
              v-if="isEditing"
              v-model="editProfile.address.street"
              class="mt-1"
            />
            <p v-else class="mt-1 text-sm text-gray-900">{{ profile.address.street }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Suite/Unit</label>
            <Input
              v-if="isEditing"
              v-model="editProfile.address.suite"
              class="mt-1"
            />
            <p v-else class="mt-1 text-sm text-gray-900">{{ profile.address.suite }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">City</label>
            <Input
              v-if="isEditing"
              v-model="editProfile.address.city"
              class="mt-1"
            />
            <p v-else class="mt-1 text-sm text-gray-900">{{ profile.address.city }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Province</label>
            <Input
              v-if="isEditing"
              v-model="editProfile.address.province"
              class="mt-1"
            />
            <p v-else class="mt-1 text-sm text-gray-900">{{ profile.address.province }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Postal Code</label>
            <Input
              v-if="isEditing"
              v-model="editProfile.address.postalCode"
              class="mt-1"
            />
            <p v-else class="mt-1 text-sm text-gray-900">{{ profile.address.postalCode }}</p>
          </div>
        </div>
      </div>
    </Card>

    <!-- Practice Details Tab -->
    <Card v-if="activeTab === 'practice'" class="p-6">
      <h3 class="text-lg font-medium text-gray-900 mb-6">Practice Information</h3>
      <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <div>
          <label class="block text-sm font-medium text-gray-700">Practice Name</label>
          <div class="mt-1 flex items-center">
            <BuildingOfficeIcon class="w-5 h-5 text-gray-400 mr-2" />
            <span class="text-sm text-gray-900">{{ profile.practiceName }}</span>
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Practice Type</label>
          <p class="mt-1 text-sm text-gray-900">{{ profile.practiceType }}</p>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">AHCIP Number</label>
          <div class="mt-1 flex items-center">
            <IdentificationIcon class="w-5 h-5 text-gray-400 mr-2" />
            <span class="text-sm text-gray-900">{{ profile.ahcipNumber }}</span>
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Registration Date</label>
          <p class="mt-1 text-sm text-gray-900">{{ profile.registrationDate }}</p>
        </div>
      </div>

      <div class="mt-6 p-4 bg-blue-50 rounded-lg">
        <div class="flex">
          <DocumentTextIcon class="w-5 h-5 text-blue-400" />
          <div class="ml-3">
            <h4 class="text-sm font-medium text-blue-800">Need to update practice details?</h4>
            <p class="mt-1 text-sm text-blue-700">
              Contact AHCIP administration to update your practice registration information.
            </p>
          </div>
        </div>
      </div>
    </Card>

    <!-- Security Tab -->
    <Card v-if="activeTab === 'security'" class="p-6">
      <h3 class="text-lg font-medium text-gray-900 mb-6">Security Settings</h3>

      <div class="space-y-6">
        <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div class="flex items-center">
            <KeyIcon class="w-8 h-8 text-gray-400" />
            <div class="ml-4">
              <h4 class="text-sm font-medium text-gray-900">Password</h4>
              <p class="text-sm text-gray-500">Last changed 30 days ago</p>
            </div>
          </div>
          <Button variant="outline" @click="showPasswordModal = true">
            Change Password
          </Button>
        </div>

        <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div class="flex items-center">
            <ShieldCheckIcon class="w-8 h-8 text-gray-400" />
            <div class="ml-4">
              <h4 class="text-sm font-medium text-gray-900">Two-Factor Authentication</h4>
              <p class="text-sm text-gray-500">Add an extra layer of security</p>
            </div>
          </div>
          <Badge variant="warning">Not Enabled</Badge>
        </div>

        <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div class="flex items-center">
            <DocumentTextIcon class="w-8 h-8 text-gray-400" />
            <div class="ml-4">
              <h4 class="text-sm font-medium text-gray-900">Active Sessions</h4>
              <p class="text-sm text-gray-500">Manage your active login sessions</p>
            </div>
          </div>
          <Button variant="outline">View Sessions</Button>
        </div>
      </div>
    </Card>

    <!-- Notifications Tab -->
    <Card v-if="activeTab === 'notifications'" class="p-6">
      <h3 class="text-lg font-medium text-gray-900 mb-6">Notification Preferences</h3>

      <div class="space-y-4">
        <div class="flex items-center justify-between py-3 border-b border-gray-200">
          <div>
            <h4 class="text-sm font-medium text-gray-900">Claim Status Updates</h4>
            <p class="text-sm text-gray-500">Receive email notifications when claim status changes</p>
          </div>
          <input
            type="checkbox"
            v-model="notifications.emailClaimUpdates"
            @change="saveNotifications"
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
        </div>

        <div class="flex items-center justify-between py-3 border-b border-gray-200">
          <div>
            <h4 class="text-sm font-medium text-gray-900">Payment Notifications</h4>
            <p class="text-sm text-gray-500">Get notified when payments are processed</p>
          </div>
          <input
            type="checkbox"
            v-model="notifications.emailPayments"
            @change="saveNotifications"
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
        </div>

        <div class="flex items-center justify-between py-3 border-b border-gray-200">
          <div>
            <h4 class="text-sm font-medium text-gray-900">Flagged Claims Alerts</h4>
            <p class="text-sm text-gray-500">Immediate notification when a claim is flagged</p>
          </div>
          <input
            type="checkbox"
            v-model="notifications.emailFlagged"
            @change="saveNotifications"
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
        </div>

        <div class="flex items-center justify-between py-3 border-b border-gray-200">
          <div>
            <h4 class="text-sm font-medium text-gray-900">Newsletter & Updates</h4>
            <p class="text-sm text-gray-500">Receive system updates and announcements</p>
          </div>
          <input
            type="checkbox"
            v-model="notifications.emailNewsletter"
            @change="saveNotifications"
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
        </div>

        <div class="flex items-center justify-between py-3">
          <div>
            <h4 class="text-sm font-medium text-gray-900">SMS Alerts</h4>
            <p class="text-sm text-gray-500">Receive critical alerts via SMS</p>
          </div>
          <input
            type="checkbox"
            v-model="notifications.smsAlerts"
            @change="saveNotifications"
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
        </div>
      </div>
    </Card>
  </div>
</template>
