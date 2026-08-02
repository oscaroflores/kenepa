<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { api, type ReportSummary } from '@/api/client'
import SourceBadge from '@/components/SourceBadge.vue'
import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'

const reports = ref<ReportSummary[]>([])
const selected = ref<number | null>(null)
const content = ref('')
const error = ref('')

async function load() {
  try {
    reports.value = await api.reports()
    if (reports.value[0]) await openReport(reports.value[0].run_id)
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not load reports'
  }
}

async function openReport(runId: number) {
  selected.value = runId
  const report = await api.report(runId)
  content.value = report.content ?? 'Report file not found on disk.'
}

onMounted(load)
</script>

<template>
  <div class="grid gap-5 lg:grid-cols-[20rem_1fr]">
    <Alert v-if="error" tone="danger" class="lg:col-span-2">{{ error }}</Alert>
    <Card class="p-4">
      <p class="font-mono text-xs uppercase tracking-[0.2em] text-[#FF5D00]">Generated markdown</p>
      <h2 class="mb-4 font-display text-2xl font-semibold">Reports</h2>
      <div class="space-y-2">
        <button v-for="report in reports" :key="report.run_id" :class="['w-full rounded-lg border bg-white p-3 text-left transition-all duration-200 ease-out !shadow-[0_8px_24px_rgba(17,17,17,0.04)] hover:!shadow-[0_10px_28px_rgba(17,17,17,0.12)]', selected === report.run_id ? 'border-[#FF5D00] text-[#FF5D00] hover:border-[#E65300] hover:text-[#E65300]' : 'border-[#E5E7EB] text-[#111111] hover:border-[#FF5D00] hover:bg-white hover:text-[#FF5D00]']" @click="openReport(report.run_id)">
          <div class="flex items-center justify-between gap-2">
            <span class="font-mono text-xs transition-colors duration-200">Run {{ report.run_id }}</span>
            <SourceBadge :status="report.overall_signal" />
          </div>
          <p class="mt-2 text-sm transition-colors duration-200">{{ report.quarter || 'No quarter' }}</p>
        </button>
        <p v-if="!reports.length" class="text-sm text-[#111111]">No reports yet.</p>
      </div>
    </Card>
    <Card class="p-4">
      <div class="mb-3 flex items-center justify-between">
        <h3 class="font-display text-xl font-semibold">Report preview</h3>
        <Button variant="ghost" size="sm" @click="load">Reload</Button>
      </div>
      <pre class="max-h-[68vh] overflow-auto whitespace-pre-wrap rounded-lg border border-[#E5E7EB] bg-white p-4 font-mono text-xs leading-6 text-[#111111] !shadow-[0_8px_24px_rgba(17,17,17,0.04)]">{{ content || 'Select a report.' }}</pre>
    </Card>
  </div>
</template>
