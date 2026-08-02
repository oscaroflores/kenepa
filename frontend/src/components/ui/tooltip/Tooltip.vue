<script setup lang="ts">
defineProps<{ text: string }>()
</script>

<template>
  <span class="group relative inline-flex cursor-help items-center">
    <slot />
    <span class="pointer-events-none absolute bottom-full left-1/2 z-20 mb-2 hidden w-64 -translate-x-1/2 rounded-md border border-[#111111] bg-white p-2 text-xs text-[#111111] group-hover:block">
      {{ text }}
    </span>
  </span>
</template>
