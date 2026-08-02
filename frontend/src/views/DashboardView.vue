<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { api, type Company, type Diagnosis } from '@/api/client'
import RunRefreshButton from '@/components/RunRefreshButton.vue'
import SignalCard from '@/components/SignalCard.vue'
import ValuationBandChart from '@/components/ValuationBandChart.vue'
import { Alert } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

const company = ref<Company | null>(null)
const diagnosis = ref<Diagnosis | null>(null)
const loading = ref(true)
const error = ref('')

const tone = computed(() => {
  const status = diagnosis.value?.overall_signal
  if (status === 'bear') return 'bear'
  if (status === 'bull') return 'bull'
  if (status === 'base') return 'base'
  return 'missing'
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    const companies = await api.companies()
    company.value = companies.find((item) => item.ticker === 'NOW') ?? companies[0] ?? null
    if (company.value) diagnosis.value = await api.latestDiagnosis(company.value.ticker)
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not load dashboard'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="space-y-5">
    <Alert v-if="error" tone="danger">{{ error }}</Alert>
    <Skeleton v-if="loading" class="h-64" />

    <template v-else>
      <section class="grid gap-5 lg:grid-cols-[1.2fr_0.8fr]">
        <Card class="overflow-hidden p-6">
          <div class="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p class="font-mono text-xs uppercase tracking-[0.24em] text-[#FF5D00]">{{ company?.ticker }} / {{ company?.cik }}</p>
              <h2 class="mt-3 max-w-2xl font-display text-4xl font-semibold tracking-[-0.035em] text-[#111111]">{{ diagnosis?.conclusion }}</h2>
            </div>
            <div class="flex items-center gap-3">
              <Badge :tone="tone">{{ diagnosis?.overall_signal ?? 'missing' }}</Badge>
              <RunRefreshButton v-if="company" :ticker="company.ticker" @refreshed="load" @error="error = $event" />
            </div>
          </div>
          <div class="mt-8 grid gap-4 sm:grid-cols-3">
            <div class="rounded-lg border border-[#E5E7EB] bg-white p-4 !shadow-[0_8px_24px_rgba(17,17,17,0.04)]">
              <p class="font-mono text-[0.65rem] uppercase tracking-[0.18em] text-[#FF5D00]">Quarter</p>
              <p class="mt-2 text-2xl font-semibold">{{ diagnosis?.quarter ?? 'missing' }}</p>
            </div>
            <div class="rounded-lg border border-[#E5E7EB] bg-white p-4 !shadow-[0_8px_24px_rgba(17,17,17,0.04)]">
              <p class="font-mono text-[0.65rem] uppercase tracking-[0.18em] text-[#FF5D00]">Exit signals</p>
              <p class="mt-2 text-2xl font-semibold text-[#FF5D00]">{{ diagnosis?.exit_signals?.length ?? 0 }}</p>
            </div>
            <div class="rounded-lg border border-[#E5E7EB] bg-white p-4 !shadow-[0_8px_24px_rgba(17,17,17,0.04)]">
              <p class="font-mono text-[0.65rem] uppercase tracking-[0.18em] text-[#FF5D00]">Missing KPIs</p>
              <p class="mt-2 text-2xl font-semibold text-[#111111]">{{ diagnosis?.missing_metrics?.length ?? 0 }}</p>
            </div>
          </div>
        </Card>
        <ValuationBandChart />
      </section>

      <section class="grid gap-4 md:grid-cols-2">
        <SignalCard v-for="signal in diagnosis?.signals ?? []" :key="signal.signal_key" :signal="signal" />
      </section>

      <section class="grid gap-4 md:grid-cols-2">
        <Card class="p-4">
          <h3 class="mb-3 font-display text-xl font-semibold">Exit Checklist</h3>
          <ul class="space-y-2 text-sm text-[#111111]">
            <li v-for="item in diagnosis?.exit_signals ?? []" :key="item" class="rounded border border-[#E5E7EB] bg-white px-3 py-2 !shadow-[0_8px_24px_rgba(17,17,17,0.04)]">{{ item }}</li>
            <li v-if="!diagnosis?.exit_signals?.length" class="text-[#111111]">No exit cluster active.</li>
          </ul>
        </Card>
        <Card class="p-4">
          <h3 class="mb-3 font-display text-xl font-semibold">Scale-In Checklist</h3>
          <ul class="space-y-2 text-sm text-[#111111]">
            <li v-for="item in diagnosis?.scale_in_signals ?? []" :key="item" class="rounded border border-[#E5E7EB] bg-white px-3 py-2 !shadow-[0_8px_24px_rgba(17,17,17,0.04)]">{{ item }}</li>
            <li v-if="!diagnosis?.scale_in_signals?.length" class="text-[#111111]">No scale-in cluster active.</li>
          </ul>
        </Card>
      </section>
    </template>
  </div>
</template>
