<script setup lang="ts">
import { ref } from 'vue'

import kenepaLogo from '@/assets/kenepa-logo.png'
import DashboardView from '@/views/DashboardView.vue'
import MetricsView from '@/views/MetricsView.vue'
import ReportsView from '@/views/ReportsView.vue'
import SourcesView from '@/views/SourcesView.vue'
import { Tabs } from '@/components/ui/tabs'

const view = ref('dashboard')
const tabs = [
  { key: 'dashboard', label: 'Dashboard' },
  { key: 'metrics', label: 'Metrics' },
  { key: 'sources', label: 'Sources' },
  { key: 'reports', label: 'Reports' },
]
</script>

<template>
  <main class="relative mx-auto min-h-screen max-w-7xl px-4 py-6 md:px-8">
    <header class="mb-6 grid gap-4 border-b border-[#111111] bg-white pb-5 md:grid-cols-[1fr_auto] md:items-end">
      <div>
        <div class="mt-2 flex items-center gap-3">
          <img :src="kenepaLogo" alt="" class="h-20 w-20 object-contain md:h-20 md:w-20" />
          <h1 class="font-brand text-4xl font-bold tracking-[-0.04em] text-[#111111] md:text-6xl">Kenepa</h1>
        </div>
        <p class="mt-2 max-w-2xl text-sm leading-6 text-[#111111]">A dense diagnostic cockpit for stock thesis checks. Missing KPIs stay missing until sourced or entered manually.</p>
      </div>
      <Tabs v-model="view" :items="tabs" />
    </header>

    <DashboardView v-if="view === 'dashboard'" />
    <MetricsView v-else-if="view === 'metrics'" />
    <SourcesView v-else-if="view === 'sources'" />
    <ReportsView v-else />
  </main>
</template>
