<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'

import { api, type MetricsResponse } from '@/api/client'
import ManualMetricDialog from '@/components/ManualMetricDialog.vue'
import MetricTable from '@/components/MetricTable.vue'
import QuarterSelector from '@/components/QuarterSelector.vue'
import { Alert } from '@/components/ui/alert'
import { Card } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

const ticker = 'NOW'
const quarters = ref<string[]>([])
const selectedQuarter = ref('')
const metrics = ref<MetricsResponse | null>(null)
const loading = ref(true)
const error = ref('')

async function loadQuarters() {
  quarters.value = await api.quarters(ticker)
  selectedQuarter.value = selectedQuarter.value || quarters.value[0] || 'FY2026-Q1'
}

async function loadMetrics() {
  if (!selectedQuarter.value) return
  loading.value = true
  error.value = ''
  try {
    metrics.value = await api.metrics(ticker, selectedQuarter.value)
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not load metrics'
  } finally {
    loading.value = false
  }
}

async function reloadAfterSave(quarter: string) {
  selectedQuarter.value = quarter
  await loadQuarters()
  if (!quarters.value.includes(quarter)) quarters.value = [quarter, ...quarters.value]
  await loadMetrics()
}

watch(selectedQuarter, loadMetrics)
onMounted(async () => {
  try {
    await loadQuarters()
    await loadMetrics()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not load metrics'
    loading.value = false
  }
})
</script>

<template>
  <div class="space-y-5">
    <Alert v-if="error" tone="danger">{{ error }}</Alert>
    <Card class="p-4">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p class="font-mono text-xs uppercase tracking-[0.2em] text-[#FF5D00]">Editable KPI ledger</p>
          <h2 class="font-display text-2xl font-semibold">Metrics</h2>
        </div>
        <div class="flex flex-wrap items-center gap-3">
          <QuarterSelector v-if="quarters.length" v-model="selectedQuarter" :quarters="quarters" />
          <ManualMetricDialog :ticker="ticker" :quarter="selectedQuarter" @saved="reloadAfterSave" @error="error = $event" />
        </div>
      </div>
    </Card>
    <Skeleton v-if="loading" class="h-72" />
    <MetricTable v-else-if="metrics?.values" :values="metrics.values" />
    <Alert v-else>No metrics found. Add manual KPIs with source tracing.</Alert>
  </div>
</template>
