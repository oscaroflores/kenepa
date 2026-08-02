<script setup lang="ts">
import type { SignalResult } from '@/api/client'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'

defineProps<{ signal: SignalResult }>()

const tone = (status: string) => {
  if (status === 'bear') return 'bear'
  if (status === 'base') return 'base'
  if (status === 'bull' || status === 'strong_bull') return 'bull'
  return 'missing'
}
</script>

<template>
  <Card class="p-4">
    <div class="mb-3 flex items-start justify-between gap-3">
      <div>
        <p class="font-mono text-[0.65rem] uppercase tracking-[0.18em] text-[#FF5D00]">{{ signal.signal_key }}</p>
        <h3 class="mt-1 font-display text-lg font-semibold text-[#111111]">{{ signal.signal_name }}</h3>
      </div>
      <Badge :tone="tone(signal.status)">{{ signal.status }}</Badge>
    </div>
    <p class="text-sm leading-6 text-[#111111]">{{ signal.summary }}</p>
  </Card>
</template>
