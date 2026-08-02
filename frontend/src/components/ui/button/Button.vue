<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{ variant?: 'default' | 'ghost' | 'danger' | 'outline'; size?: 'sm' | 'md'; disabled?: boolean }>(), {
  variant: 'default',
  size: 'md',
  disabled: false,
})

const classes = computed(() => [
  'inline-flex items-center justify-center rounded-md border font-mono uppercase tracking-[0.18em] transition-all duration-200 ease-out hover:!shadow-[0_10px_28px_rgba(17,17,17,0.12)] disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:!shadow-none',
  props.size === 'sm' ? 'px-3 py-1.5 text-[0.65rem]' : 'px-4 py-2 text-xs',
  props.variant === 'default' && 'border-[#111111] bg-[#FF5D00] text-white hover:border-[#E65300] hover:bg-[#E65300]',
  props.variant === 'ghost' && 'border-[#111111] bg-white text-[#111111] hover:border-[#FF5D00] hover:bg-white hover:text-[#FF5D00]',
  props.variant === 'danger' && 'border-[#111111] bg-white text-[#FF5D00] hover:border-[#FF5D00] hover:bg-white hover:text-[#E65300]',
  props.variant === 'outline' && 'border-[#111111] bg-white text-[#111111] hover:border-[#FF5D00] hover:bg-white hover:text-[#FF5D00]',
])
</script>

<template>
  <button :disabled="disabled" :class="classes">
    <slot />
  </button>
</template>
