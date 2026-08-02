<script setup lang="ts">
defineProps<{ open: boolean; title?: string }>()
const emit = defineEmits<{ close: [] }>()
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="fixed inset-0 z-50 grid place-items-center bg-white p-4" @click.self="emit('close')">
      <section class="max-h-[88vh] w-full max-w-3xl overflow-auto rounded-lg border border-[#E5E7EB] bg-white p-5 !shadow-[0_8px_24px_rgba(17,17,17,0.04)]">
        <div class="mb-4 flex items-center justify-between gap-4 border-b border-[#E5E7EB] pb-3">
          <h2 class="font-display text-xl font-semibold tracking-tight">{{ title }}</h2>
          <button class="rounded-md border border-[#111111] bg-white px-2 py-1 text-xs text-[#111111] transition-all duration-200 ease-out hover:border-[#FF5D00] hover:bg-white hover:text-[#FF5D00] hover:!shadow-[0_10px_28px_rgba(17,17,17,0.12)]" @click="emit('close')">Close</button>
        </div>
        <slot />
      </section>
    </div>
  </Teleport>
</template>
