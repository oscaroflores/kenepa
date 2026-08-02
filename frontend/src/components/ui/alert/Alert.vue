<script setup lang="ts">
withDefaults(defineProps<{ tone?: 'neutral' | 'danger' }>(), { tone: 'neutral' })
</script>

<template>
  <div :class="['rounded-lg border border-[#E5E7EB] bg-white px-4 py-3 text-sm !shadow-[0_8px_24px_rgba(17,17,17,0.04)]', tone === 'danger' ? 'text-[#FF5D00]' : 'text-[#111111]']">
    <slot />
  </div>
</template>
