<script setup lang="ts">
const props = withDefaults(defineProps<{ tone?: 'neutral' | 'bear' | 'base' | 'bull' | 'missing' }>(), { tone: 'neutral' })

const toneClass: Record<string, string> = {
  neutral: 'border-[#111111] bg-white text-[#111111]',
  bear: 'border-[#111111] bg-white text-[#FF5D00]',
  base: 'border-[#111111] bg-white text-[#FF5D00]',
  bull: 'border-[#111111] bg-white text-[#FF5D00]',
  missing: 'border-[#111111] bg-white text-[#111111]',
}
</script>

<template>
  <span :class="['inline-flex items-center rounded-full border px-2 py-0.5 font-mono text-[0.65rem] uppercase tracking-[0.16em]', toneClass[props.tone]]">
    <slot />
  </span>
</template>
