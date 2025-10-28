<script lang="ts" setup>
defineProps({
  jobId: {
    type: String,
    default: ''
  },
  status: {
    type: Object,
    default: null
  }
})
</script>

<template>
  <div v-if="jobId" class="bg-white border border-gray-300 rounded p-6">
    <div class="mb-4 pb-4 border-b border-gray-200">
      <div class="text-sm text-gray-600 mb-1">Job ID</div>
      <code class="text-xs bg-gray-100 px-2 py-1 rounded">{{ jobId }}</code>
    </div>

    <div v-if="status" class="space-y-4">
      <div class="flex items-center space-x-3">
        <span class="text-sm font-medium text-gray-700">Status:</span>
        <span
          class="px-3 py-1 text-xs font-semibold rounded"
          :style="{
            backgroundColor: status.state === 'SUCCESS' ? '#dcfce7' : 
                           status.state === 'PENDING' ? '#fef3c7' :
                           status.state === 'FAILURE' ? '#fee2e2' :
                           status.state === 'STARTED' || status.state === 'PROGRESS' ? '#dbeafe' : '#f3f4f6',
            color: status.state === 'SUCCESS' ? '#166534' :
                   status.state === 'PENDING' ? '#92400e' :
                   status.state === 'FAILURE' ? '#991b1b' :
                   status.state === 'STARTED' || status.state === 'PROGRESS' ? '#1e40af' : '#374151'
          }"
        >
          {{ status.state }}
        </span>
      </div>

      <div v-if="status.progress" class="space-y-2">
        <div class="flex justify-between text-sm">
          <span class="font-medium text-gray-700">Progress</span>
          <span class="text-gray-600">
            {{ status.progress.completed }} / {{ status.progress.total }} chunks
            ({{ Math.round((status.progress.completed / status.progress.total) * 100) }}%)
          </span>
        </div>
        <div class="w-full bg-gray-200 rounded h-4">
          <div
            class="h-4 rounded transition-all duration-300"
            :style="{ 
              width: Math.round((status.progress.completed / status.progress.total) * 100) + '%',
              backgroundColor: '#29d646'
            }"
          ></div>
        </div>
      </div>

      <div v-if="status.result" class="mt-6 pt-6 border-t border-gray-200">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Results</h3>
        <div class="grid grid-cols-2 gap-4">
          <div class="bg-gray-50 p-4 rounded border border-gray-200">
            <div class="text-sm text-gray-600 mb-1">Prime Count</div>
            <div class="text-2xl font-bold text-gray-900">
              {{ status.result.prime_count.toLocaleString() }}
            </div>
          </div>
          <div class="bg-gray-50 p-4 rounded border border-gray-200">
            <div class="text-sm text-gray-600 mb-1">Duration</div>
            <div class="text-2xl font-bold text-gray-900">
              {{ status.result.duration_sec }}s
            </div>
          </div>
        </div>
      </div>

      <!-- Error -->
      <div v-if="status.error" class="bg-red-50 border border-red-300 text-red-800 rounded p-4">
        <strong>Job Failed:</strong> {{ status.error }}
      </div>
    </div>
  </div>
</template>
