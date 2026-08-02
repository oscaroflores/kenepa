<script setup lang="ts">
import { reactive, ref, watch } from 'vue'

import { api } from '@/api/client'
import { Button } from '@/components/ui/button'
import { Dialog } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'

const props = defineProps<{ ticker: string; quarter?: string }>()
const emit = defineEmits<{ saved: [quarter: string]; error: [message: string] }>()

const open = ref(false)
const saving = ref(false)
const form = reactive({ quarter: props.quarter || 'FY2026-Q1', fiscal_year: '', source_label: 'Manual entry', source_url: '', notes: '' })
const values = reactive<Record<string, string>>({})

const fields = [
  ['current_rpo_growth_constant_currency', 'cRPO CC growth %'],
  ['current_rpo_growth', 'Current RPO growth %'],
  ['renewal_rate', 'Renewal rate %'],
  ['creator_other_share', 'Creator/other share %'],
  ['ai_acv_run_rate', 'AI ACV run-rate'],
  ['ai_acv_target', 'AI ACV target'],
  ['non_gaap_operating_margin', 'Non-GAAP op margin %'],
  ['free_cash_flow', 'Free cash flow'],
  ['free_cash_flow_margin', 'FCF margin %'],
  ['named_competitive_wins', 'Named competitive wins true/false'],
  ['named_displacements', 'Named displacements true/false'],
  ['fy27_growth_guidance', 'FY27 growth guide %'],
  ['share_price_used', 'Share price used'],
] as const

for (const [field] of fields) values[field] = ''

watch(() => props.quarter, (quarter) => {
  if (quarter) form.quarter = quarter
})

function coerce(field: string, raw: string) {
  const trimmed = raw.trim()
  if (field.startsWith('named_') || field === 'discretionary_insider_selling_depressed') {
    return ['true', 'yes', '1', 'si', 'sí'].includes(trimmed.toLowerCase())
  }
  const numeric = Number(trimmed.replaceAll(',', ''))
  return Number.isFinite(numeric) ? numeric : trimmed
}

async function save() {
  saving.value = true
  const payloadValues: Record<string, unknown> = {}
  for (const [field] of fields) {
    if (values[field]?.trim()) payloadValues[field] = coerce(field, values[field])
  }
  try {
    await api.manualMetrics(props.ticker, {
      quarter: form.quarter,
      fiscal_year: form.fiscal_year ? Number(form.fiscal_year) : null,
      source_label: form.source_label,
      source_url: form.source_url || null,
      notes: form.notes || null,
      values: payloadValues,
    })
    open.value = false
    emit('saved', form.quarter)
  } catch (error) {
    emit('error', error instanceof Error ? error.message : 'Save failed')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <Button variant="outline" @click="open = true">Manual KPI</Button>
  <Dialog :open="open" title="Manual metric entry" @close="open = false">
    <div class="grid gap-4 md:grid-cols-2">
      <label class="space-y-1 text-sm text-[#111111]">Quarter<Input v-model="form.quarter" placeholder="FY2026-Q1" /></label>
      <label class="space-y-1 text-sm text-[#111111]">Fiscal year<Input v-model="form.fiscal_year" placeholder="2026" /></label>
      <label class="space-y-1 text-sm text-[#111111]">Source label<Input v-model="form.source_label" placeholder="Q1 FY26 earnings release" /></label>
      <label class="space-y-1 text-sm text-[#111111]">Source URL<Input v-model="form.source_url" placeholder="https://..." /></label>
      <label class="space-y-1 text-sm text-[#111111] md:col-span-2">Notes<Input v-model="form.notes" placeholder="Page, paragraph, or manual context" /></label>
    </div>
    <div class="mt-5 grid gap-3 md:grid-cols-2">
      <label v-for="[field, label] in fields" :key="field" class="space-y-1 text-sm text-[#111111]">
        {{ label }}
        <Input v-model="values[field]" placeholder="leave blank if missing" />
      </label>
    </div>
    <div class="mt-5 flex justify-end gap-3">
      <Button variant="ghost" @click="open = false">Cancel</Button>
      <Button :disabled="saving" @click="save">{{ saving ? 'Saving' : 'Save metrics' }}</Button>
    </div>
  </Dialog>
</template>
