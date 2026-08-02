<script setup lang="ts">
import { ref } from 'vue'

import { api } from '@/api/client'
import { Button } from '@/components/ui/button'

const props = defineProps<{ ticker: string }>()
const emit = defineEmits<{ refreshed: []; error: [message: string] }>()
const loading = ref(false)

async function refresh() {
  loading.value = true
  try {
    await api.refresh(props.ticker)
    emit('refreshed')
  } catch (error) {
    emit('error', error instanceof Error ? error.message : 'Refresh failed')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <Button :disabled="loading" @click="refresh">
    {{ loading ? 'Refreshing SEC' : 'Refresh SEC' }}
  </Button>
</template>
