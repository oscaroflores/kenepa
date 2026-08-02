<script setup lang="ts">
defineProps<{ modelValue: string; options: string[] }>()
const emit = defineEmits<{ 'update:modelValue': [value: string] }>()
</script>

<template>
  <select class="rounded-md border border-[#111111] bg-white px-3 py-2 font-mono text-sm text-[#111111] outline-none focus:border-[#FF5D00]" :value="modelValue" @change="emit('update:modelValue', ($event.target as HTMLSelectElement).value)">
    <option v-for="option in options" :key="option" :value="option">{{ option }}</option>
  </select>
</template>
