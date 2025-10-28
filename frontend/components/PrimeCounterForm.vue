<script lang="ts" setup>
const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit'])

const formData = ref({
  n: 200000,
  chunks: 16
})
</script>


<template>
  <div class="bg-white border border-gray-300 rounded p-6 mb-6">
    <form @submit.prevent="$emit('submit', formData)" class="space-y-4">
      <div>
        <label for="n" class="block text-sm font-medium text-gray-700 mb-1">
          Upper Limit (n)
        </label>
        <input
          id="n"
          v-model.number="formData.n"
          type="number"
          min="10000"
          required
          :disabled="loading"
          class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-gray-500 disabled:bg-gray-100"
        />
        <p class="text-xs text-gray-500 mt-1">Must be ≥ 10,000</p>
      </div>

      <div>
        <label for="chunks" class="block text-sm font-medium text-gray-700 mb-1">
          Number of Chunks
        </label>
        <input
          id="chunks"
          v-model.number="formData.chunks"
          type="number"
          min="1"
          max="128"
          required
          :disabled="loading"
          class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-gray-500 disabled:bg-gray-100"
        />
        <p class="text-xs text-gray-500 mt-1">Between 1 and 128</p>
      </div>

      <button
        type="submit"
        :disabled="loading"
        class="w-full text-black border border-gray-300 rounded-md py-2 px-4 hover:bg-gray-700 hover:text-white disabled:bg-gray-400 disabled:cursor-not-allowed disabled:text-gray-700 transition-colors"
      >
        {{ loading ? 'Processing...' : 'Count Primes' }}
      </button>
    </form>
  </div>
</template>
