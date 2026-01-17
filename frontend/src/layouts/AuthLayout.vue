<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <div class="min-h-screen flex">
    <!-- Left side - Branding -->
    <div class="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-primary-600 to-primary-800 p-12 flex-col justify-between">
      <div>
        <h1 class="text-3xl font-bold text-white">Claims Processing Platform</h1>
        <p class="mt-2 text-primary-100">Healthcare Claims Management System</p>
      </div>

      <div class="space-y-8">
        <div class="flex items-start space-x-4">
          <div class="flex-shrink-0 h-12 w-12 rounded-lg bg-primary-500 bg-opacity-50 flex items-center justify-center">
            <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-semibold text-white">Streamlined Claims Submission</h3>
            <p class="mt-1 text-primary-100">Submit and track claims with our intuitive digital forms</p>
          </div>
        </div>

        <div class="flex items-start space-x-4">
          <div class="flex-shrink-0 h-12 w-12 rounded-lg bg-primary-500 bg-opacity-50 flex items-center justify-center">
            <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-semibold text-white">Automated Adjudication</h3>
            <p class="mt-1 text-primary-100">Fast processing with AHCIP-compliant rules engine</p>
          </div>
        </div>

        <div class="flex items-start space-x-4">
          <div class="flex-shrink-0 h-12 w-12 rounded-lg bg-primary-500 bg-opacity-50 flex items-center justify-center">
            <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-semibold text-white">HIPAA Compliant</h3>
            <p class="mt-1 text-primary-100">Enterprise-grade security for protected health information</p>
          </div>
        </div>
      </div>

      <div class="text-primary-200 text-sm">
        © {{ new Date().getFullYear() }} Claims Processing Platform. All rights reserved.
      </div>
    </div>

    <!-- Right side - Auth form -->
    <div class="flex-1 flex items-center justify-center p-8 bg-gray-50">
      <div class="w-full max-w-md">
        <!-- Mobile logo -->
        <div class="lg:hidden text-center mb-8">
          <h1 class="text-2xl font-bold text-primary-600">Claims Processing Platform</h1>
          <p class="mt-1 text-gray-600">Healthcare Claims Management System</p>
        </div>

        <RouterView />
      </div>
    </div>
  </div>
</template>
