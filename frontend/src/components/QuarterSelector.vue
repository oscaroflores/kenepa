<script setup lang="ts">
import { Select } from '@/components/ui/select'

defineProps<{ modelValue: string; quarters: string[] }>()
const emit = defineEmits<{ 'update:modelValue': [value: string] }>()
</script>

<template>
  <label class="flex items-center gap-2 text-sm text-[#111111]">
    <span class="font-mono text-xs uppercase tracking-[0.18em] text-[#FF5D00]">Quarter</span>
    <Select :model-value="modelValue" :options="quarters" @update:model-value="emit('update:modelValue', $event)" />
  </label>
</template>
