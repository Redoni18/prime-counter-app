<template>
  <div v-if="error" class="bg-red-50 border border-red-300 text-red-800 rounded p-4 mb-6">
    <strong>Error:</strong> {{ error }}
  </div>
</template>

<script lang="ts" setup>
defineProps({
  error: {
    type: String,
    default: ''
  }
})
</script>

