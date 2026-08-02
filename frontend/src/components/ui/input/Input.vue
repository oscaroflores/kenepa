<script setup lang="ts">
defineProps<{ modelValue: string; placeholder?: string; type?: string }>()
const emit = defineEmits<{ 'update:modelValue': [value: string] }>()
</script>

<template>
  <input :type="type ?? 'text'" class="w-full rounded-md border border-[#111111] bg-white px-3 py-2 text-sm text-[#111111] outline-none placeholder:text-[#111111] focus:border-[#FF5D00]" :placeholder="placeholder" :value="modelValue" @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)" />
</template>
