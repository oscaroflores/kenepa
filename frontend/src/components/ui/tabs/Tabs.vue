<script setup lang="ts">
defineProps<{ items: { key: string; label: string }[]; modelValue: string }>()
const emit = defineEmits<{ 'update:modelValue': [value: string] }>()
</script>

<template>
  <div class="flex flex-wrap gap-2 rounded-lg border border-[#E5E7EB] bg-white p-1 !shadow-[0_8px_24px_rgba(17,17,17,0.04)]">
    <button v-for="item in items" :key="item.key" :class="['rounded-md border px-3 py-2 font-mono text-xs uppercase tracking-[0.18em] transition-all duration-200 ease-out hover:!shadow-[0_10px_28px_rgba(17,17,17,0.12)]', modelValue === item.key ? 'border-[#111111] bg-[#FF5D00] text-white hover:border-[#E65300] hover:bg-[#E65300]' : 'border-[#111111] bg-white text-[#111111] hover:border-[#FF5D00] hover:bg-white hover:text-[#FF5D00]']" @click="emit('update:modelValue', item.key)">
      {{ item.label }}
    </button>
  </div>
</template>
