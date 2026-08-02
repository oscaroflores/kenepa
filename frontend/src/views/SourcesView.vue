<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { api, type SourceDocument } from '@/api/client'
import SourceBadge from '@/components/SourceBadge.vue'
import { Alert } from '@/components/ui/alert'
import { Card } from '@/components/ui/card'
import { Table } from '@/components/ui/table'

const sources = ref<SourceDocument[]>([])
const error = ref('')

async function load() {
  try {
    sources.value = await api.sources('NOW')
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not load sources'
  }
}

onMounted(load)
</script>

<template>
  <div class="space-y-5">
    <Alert v-if="error" tone="danger">{{ error }}</Alert>
    <Card class="p-4">
      <p class="font-mono text-xs uppercase tracking-[0.2em] text-[#FF5D00]">Audit trail</p>
      <h2 class="font-display text-2xl font-semibold">Cached Sources</h2>
    </Card>
    <Table>
      <thead class="bg-white font-mono text-[0.65rem] uppercase tracking-[0.18em] text-[#FF5D00]">
        <tr><th>Type</th><th>Title</th><th>Status</th><th>Filed</th><th>Path</th></tr>
      </thead>
      <tbody>
        <tr v-for="source in sources" :key="source.id">
          <td class="font-mono text-xs text-[#111111]">{{ source.source_type }}</td>
          <td><a v-if="source.document_url" class="text-[#111111] underline decoration-[#111111] underline-offset-4" :href="source.document_url" target="_blank">{{ source.title }}</a><span v-else>{{ source.title }}</span></td>
          <td><SourceBadge :status="source.parse_status" /></td>
          <td class="font-mono text-xs text-[#111111]">{{ source.filed_at || 'n/a' }}</td>
          <td class="max-w-[18rem] truncate font-mono text-xs text-[#111111]">{{ source.local_path || 'remote only' }}</td>
        </tr>
        <tr v-if="!sources.length"><td colspan="5" class="text-[#111111]">No cached source documents yet. Run SEC refresh.</td></tr>
      </tbody>
    </Table>
  </div>
</template>
