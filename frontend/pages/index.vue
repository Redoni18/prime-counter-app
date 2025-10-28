<script lang="ts" setup>
import axios from 'axios'

const config = useRuntimeConfig()
const apiBaseUrl = config.public.apiBaseUrl

const jobId = ref('')
const status = ref(null)
const loading = ref(false)
const error = ref<string>('')
const polling = ref<boolean>(false)
let pollInterval: ReturnType<typeof setInterval> | null = null

const submitJob = async (formData: { n: number; chunks: number }) => {
  error.value = ''
  status.value = null
  jobId.value = ''
  loading.value = true

  try {
    const response = await axios.post(
      `${apiBaseUrl}/api/count-primes`,
      {
        n: formData.n,
        chunks: formData.chunks
      }
    )
    jobId.value = response.data.job_id
    status.value = { job_id: response.data.job_id, state: 'PENDING' } as any
    startPolling()
  } catch (err: any) {
    error.value = (err?.response?.data?.detail) ?? (err?.message) ?? 'Failed to submit job'
    loading.value = false
  }
}

const startPolling = () => {
  polling.value = true
  pollInterval = setInterval(async () => {
    await checkJobStatus()
  }, 1000)
}

const stopPolling = () => {
  polling.value = false
  if (pollInterval) {
    clearInterval(pollInterval)
    pollInterval = null
  }
}

const checkJobStatus = async () => {
  if (!jobId.value) return

  try {
    const response = await axios.get(`${apiBaseUrl}/api/jobs/${jobId.value}`)
    status.value = response.data

    // Stop polling if job is complete or failed
    if (response.data.state === 'SUCCESS' || response.data.state === 'FAILURE') {
      stopPolling()
      loading.value = false
    }
  } catch (err) {
    console.error('Error polling job status:', err)
    error.value = 'Failed to fetch job status'
    stopPolling()
    loading.value = false
  }
}

// Cleanup on unmount
onUnmounted(() => {
  stopPolling()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto p-8">
      <Header />

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div class="space-y-6">
          <PrimeCounterForm 
            :loading="loading" 
            @submit="submitJob" 
          />
          <ErrorMessage :error="error" />
        </div>

        <div class="space-y-6">
          <JobStatus :job-id="jobId" :status="status" />
        </div>
      </div>
    </div>
  </div>
</template>