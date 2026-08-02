<script setup lang="ts">
import { Badge } from '@/components/ui/badge'

defineProps<{ status?: string; mode?: string }>()

const toneFor = (status?: string, mode?: string) => {
  if (mode === 'manual') return 'base'
  if (status === 'bear' || status?.includes('failed')) return 'bear'
  if (status === 'base') return 'base'
  if (status === 'bull' || status === 'strong_bull' || status?.includes('cached') || status?.includes('parsed')) return 'bull'
  return 'missing'
}
</script>

<template>
  <Badge :tone="toneFor(status, mode)">
    {{ mode || status || 'source' }}
  </Badge>
</template>
