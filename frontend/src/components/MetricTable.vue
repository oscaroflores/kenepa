<script setup lang="ts">
import SourceBadge from '@/components/SourceBadge.vue'
import { Table } from '@/components/ui/table'

const props = defineProps<{ values: Record<string, unknown> }>()

const fields = [
  ['Demand', 'current_rpo_growth_constant_currency', 'cRPO constant currency growth'],
  ['Demand', 'current_rpo_growth', 'Current RPO growth'],
  ['Moat', 'renewal_rate', 'Renewal rate'],
  ['AI', 'creator_other_share', 'Creator/other share'],
  ['AI', 'ai_acv_run_rate', 'AI ACV run-rate'],
  ['AI', 'ai_acv_target', 'AI ACV target'],
  ['Profit', 'non_gaap_operating_margin', 'Non-GAAP operating margin'],
  ['Profit', 'gaap_net_income', 'GAAP net income'],
  ['Profit', 'free_cash_flow', 'Free cash flow'],
  ['Profit', 'stock_based_compensation', 'Stock-based compensation'],
  ['Dilution', 'diluted_share_count', 'Diluted share count'],
  ['Market', 'share_price_used', 'Share price used'],
  ['Market', 'market_cap', 'Market cap'],
  ['Market', 'enterprise_value', 'Enterprise value'],
  ['Balance', 'cash_and_equivalents', 'Cash and equivalents'],
  ['Moat', 'customers_over_5m_acv', 'Customers > $5M ACV'],
  ['Moat', 'named_competitive_wins', 'Named competitive wins'],
  ['Moat', 'named_displacements', 'Named displacements'],
  ['Guidance', 'fy_growth_guidance', 'FY growth guidance'],
  ['Guidance', 'fy_operating_margin_guidance', 'FY operating margin guidance'],
  ['Guidance', 'fy27_growth_guidance', 'FY27 growth guidance'],
] as const

function display(value: unknown) {
  if (value === null || value === undefined || value === '') return 'missing'
  if (typeof value === 'boolean') return value ? 'yes' : 'no'
  if (typeof value === 'number') return Math.abs(value) >= 1_000_000 ? value.toLocaleString() : value.toString()
  return String(value)
}

function sourceFor(field: string) {
  const sources = props.values.metric_sources as Record<string, { mode?: string; source_type?: string }> | undefined
  return sources?.[field]
}
</script>

<template>
  <Table>
    <thead class="bg-white font-mono text-[0.65rem] uppercase tracking-[0.18em] text-[#FF5D00]">
      <tr>
        <th>Group</th>
        <th>Metric</th>
        <th>Value</th>
        <th>Trace</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="[group, field, label] in fields" :key="field" class="text-[#111111]">
        <td class="font-mono text-xs uppercase tracking-[0.14em] text-[#FF5D00]">{{ group }}</td>
        <td>{{ label }}</td>
        <td :class="display(values[field]) === 'missing' ? 'text-[#111111]' : 'font-mono text-[#111111]'">{{ display(values[field]) }}</td>
        <td>
          <SourceBadge v-if="sourceFor(field)" :mode="sourceFor(field)?.mode" :status="sourceFor(field)?.source_type" />
          <SourceBadge v-else status="missing" />
        </td>
      </tr>
    </tbody>
  </Table>
</template>
